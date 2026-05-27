#!/usr/bin/env bash
# jokerman-session-setup installer (bash / Linux / macOS / WSL / Git Bash)
#
# Reads upstream-sources.yaml and installs each source from its upstream repo.
# Does NOT bundle any external code — every source is cloned from its public origin
# at install time.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCES_FILE="$SCRIPT_DIR/upstream-sources.yaml"

# ----- helpers ----------------------------------------------------------------

c_reset='\033[0m'
c_bold='\033[1m'
c_dim='\033[2m'
c_green='\033[32m'
c_yellow='\033[33m'
c_red='\033[31m'
c_blue='\033[34m'

say()   { printf "%b\n" "$1"; }
ok()    { printf "${c_green}✓${c_reset} %s\n" "$1"; }
warn()  { printf "${c_yellow}⚠${c_reset} %s\n" "$1"; }
fail()  { printf "${c_red}✗${c_reset} %s\n" "$1" >&2; }
info()  { printf "${c_blue}·${c_reset} %s\n" "$1"; }
hdr()   { printf "\n${c_bold}== %s ==${c_reset}\n" "$1"; }

expand_path() {
  # Expand leading ~ to $HOME. Does not expand other env vars.
  local p="$1"
  if [[ "$p" == "~"* ]]; then
    echo "${HOME}${p:1}"
  else
    echo "$p"
  fi
}

# ----- pre-flight -------------------------------------------------------------

hdr "jokerman-session-setup installer"
say "${c_dim}Sources file: $SOURCES_FILE${c_reset}"

if ! command -v git >/dev/null 2>&1; then
  fail "git not found — install git and re-run"
  exit 1
fi
ok "git found ($(git --version))"

if ! command -v yq >/dev/null 2>&1; then
  fail "yq not found — install yq and re-run"
  say "  macOS:    brew install yq"
  say "  Linux:    https://github.com/mikefarah/yq/#install"
  say "  Windows:  scoop install yq  (or download release binary)"
  exit 1
fi
ok "yq found ($(yq --version))"

if [[ ! -f "$SOURCES_FILE" ]]; then
  fail "Sources file missing: $SOURCES_FILE"
  exit 1
fi
ok "Sources file found"

# ----- backup ~/.claude/ ------------------------------------------------------

hdr "Backing up existing ~/.claude/ (if any)"

if [[ -d "$HOME/.claude" ]]; then
  BACKUP="$HOME/.claude-backup-$(date +%Y%m%d-%H%M%S)"
  cp -r "$HOME/.claude" "$BACKUP"
  ok "Backed up to $BACKUP"
else
  info "No existing ~/.claude/ — nothing to back up"
fi

# ----- copy scaffolding -------------------------------------------------------

hdr "Installing scaffolding"

SCAFFOLDING_DEST="$HOME/.claude-scaffolding"
mkdir -p "$SCAFFOLDING_DEST"
cp -r "$REPO_ROOT/scaffolding/." "$SCAFFOLDING_DEST/"
ok "Scaffolding copied to $SCAFFOLDING_DEST"

# Link the canonical AGENT-INSTRUCTIONS.md so each new repo can reference one source.
ln -sf "$REPO_ROOT/AGENT-INSTRUCTIONS.md" "$SCAFFOLDING_DEST/AGENT-INSTRUCTIONS.md" 2>/dev/null || \
  cp "$REPO_ROOT/AGENT-INSTRUCTIONS.md" "$SCAFFOLDING_DEST/AGENT-INSTRUCTIONS.md"
ok "AGENT-INSTRUCTIONS.md available at $SCAFFOLDING_DEST/"

# ----- install upstream sources ----------------------------------------------

hdr "Installing upstream sources"

# yq query: read source names
mapfile -t SOURCE_NAMES < <(yq '.sources | keys | .[]' "$SOURCES_FILE")

INSTALLED=0
SKIPPED=0
WARNED=0

for name in "${SOURCE_NAMES[@]}"; do
  # Strip yq quote artifacts
  name="${name//\"/}"

  repo=$(yq ".sources.${name}.repo" "$SOURCES_FILE" | tr -d '"')
  install_path_raw=$(yq ".sources.${name}.install_path" "$SOURCES_FILE" | tr -d '"')
  install_path=$(expand_path "$install_path_raw")
  install_type=$(yq ".sources.${name}.install_type" "$SOURCES_FILE" | tr -d '"')
  license=$(yq ".sources.${name}.license" "$SOURCES_FILE" | tr -d '"')
  tier=$(yq ".sources.${name}.tier" "$SOURCES_FILE" | tr -d '"')
  description=$(yq ".sources.${name}.description" "$SOURCES_FILE" | tr -d '"')

  say ""
  say "${c_bold}${name}${c_reset} ${c_dim}(${license}, ${tier})${c_reset}"
  say "  ${c_dim}${description}${c_reset}"
  say "  ${c_dim}→ ${install_path}${c_reset}"

  # Reference-only sources are skipped by install.
  if [[ "$install_type" == "reference-only" ]]; then
    info "Reference-only (see docs/promoted-agents.md). Not cloning."
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Already installed? Pull instead of re-clone.
  if [[ -d "$install_path/.git" ]]; then
    info "Already cloned — pulling latest"
    if (cd "$install_path" && git pull --ff-only --quiet 2>&1); then
      ok "Updated $name"
      INSTALLED=$((INSTALLED + 1))
    else
      warn "git pull failed for $name — leaving as is, check $install_path manually"
      WARNED=$((WARNED + 1))
    fi
    continue
  fi

  # Fresh clone.
  mkdir -p "$(dirname "$install_path")"
  if git clone --depth 1 "$repo" "$install_path" 2>&1 | grep -E "(Cloning|fatal)"; then
    :
  fi

  if [[ ! -d "$install_path/.git" ]]; then
    fail "Clone failed for $name (from $repo)"
    WARNED=$((WARNED + 1))
    continue
  fi

  # Post-install for git-clone-and-setup type.
  if [[ "$install_type" == "git-clone-and-setup" ]]; then
    post_install=$(yq ".sources.${name}.post_install" "$SOURCES_FILE" | tr -d '"')
    if [[ -n "$post_install" && "$post_install" != "null" ]]; then
      info "Running post-install: $post_install"
      if (cd "$install_path" && eval "$post_install"); then
        ok "Post-install complete"
      else
        warn "Post-install command failed for $name — install_path is cloned but setup incomplete"
        WARNED=$((WARNED + 1))
      fi
    fi
  fi

  # Print license note for restricted-tier sources.
  if [[ "$tier" == "restricted" ]]; then
    license_note=$(yq ".sources.${name}.license_note" "$SOURCES_FILE" | tr -d '"' | tr '\n' ' ')
    if [[ -n "$license_note" && "$license_note" != "null" ]]; then
      warn "License note: $license_note"
    fi
  fi

  ok "Installed $name"
  INSTALLED=$((INSTALLED + 1))
done

# ----- summary ----------------------------------------------------------------

hdr "Summary"

say "  Installed/updated: ${c_green}${INSTALLED}${c_reset}"
say "  Skipped (reference-only): ${c_dim}${SKIPPED}${c_reset}"
say "  Warnings: ${c_yellow}${WARNED}${c_reset}"
say ""
say "Next steps:"
say "  1. ${c_bold}Run verify.sh${c_reset} to check the install"
say "       ${c_dim}bash $SCRIPT_DIR/verify.sh${c_reset}"
say "  2. ${c_bold}Per-CLI shim setup${c_reset} — see docs/getting-started.md"
say "       Claude Code: symlinks are in $SCAFFOLDING_DEST/"
say "       Copilot:     copy shims/copilot-instructions.md to .github/copilot-instructions.md in each repo"
say "       Codex:       copy shims/AGENTS.md to AGENTS.md in each repo"
say ""
ok "Install complete."
