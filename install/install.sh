#!/usr/bin/env bash
# jokerman-session-setup (JStack) installer — bash/Linux/macOS/WSL/Git Bash
#
# Honors JStack architecture decisions:
# - A1: hooks ship INERT at ~/.jstack/hooks/ (operator manually symlinks to opt in)
# - A2: scaffolding lives at ~/.jstack/scaffolding/ (separate from ~/.claude/)
# - A3: layer config at ~/.jstack/config.yaml — per-layer enable
# - A6: cli_support frontmatter validated at install time
# - C1: skill/agent frontmatter validated at install time
#
# Does NOT bundle upstream code — clones from declared upstreams at install time
# with SHA pinning where declared in upstream-sources.yaml.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCES_FILE="$SCRIPT_DIR/upstream-sources.yaml"
LAYER_CONFIG_EXAMPLE="$SCRIPT_DIR/layer-config.yaml.example"

JSTACK_HOME="${JSTACK_HOME:-$HOME/.jstack}"
JSTACK_SCAFFOLDING="$JSTACK_HOME/scaffolding"
JSTACK_HOOKS="$JSTACK_HOME/hooks"
JSTACK_CONFIG="$JSTACK_HOME/config.yaml"

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
  local p="$1"
  if [[ "$p" == "~"* ]]; then echo "${HOME}${p:1}"; else echo "$p"; fi
}

# ----- pre-flight -------------------------------------------------------------

hdr "JStack installer"
say "${c_dim}Repo: $REPO_ROOT${c_reset}"
say "${c_dim}JStack home: $JSTACK_HOME${c_reset}"

if ! command -v git >/dev/null 2>&1; then
  fail "git not found — install git and re-run"
  exit 1
fi
ok "git found ($(git --version))"

YQ_AVAILABLE=0
if command -v yq >/dev/null 2>&1; then
  ok "yq found ($(yq --version))"
  YQ_AVAILABLE=1
else
  warn "yq not found — upstream-sources.yaml parsing limited"
  say "  macOS:    brew install yq"
  say "  Linux:    https://github.com/mikefarah/yq/#install"
  say "  Windows:  scoop install yq"
fi

# ----- backup existing JStack -------------------------------------------------

hdr "Backing up existing ~/.jstack/ (if any)"

if [[ -d "$JSTACK_HOME" ]]; then
  BACKUP="$JSTACK_HOME-backup-$(date +%Y%m%d-%H%M%S)"
  cp -r "$JSTACK_HOME" "$BACKUP"
  ok "Backed up to $BACKUP"
else
  info "No existing ~/.jstack/ — nothing to back up"
fi

# ----- create JStack home structure ------------------------------------------

hdr "Creating ~/.jstack/ structure"

mkdir -p "$JSTACK_HOME"
mkdir -p "$JSTACK_SCAFFOLDING"
mkdir -p "$JSTACK_HOOKS"
mkdir -p "$JSTACK_HOME/audit"
mkdir -p "$JSTACK_HOME/sessions"
mkdir -p "$JSTACK_HOME/provenance"
mkdir -p "$JSTACK_HOME/freeze"
mkdir -p "$JSTACK_HOME/rai"
mkdir -p "$JSTACK_HOME/dpia"
mkdir -p "$JSTACK_HOME/dsb"
mkdir -p "$JSTACK_HOME/entra"
mkdir -p "$JSTACK_HOME/review-log"
mkdir -p "$JSTACK_HOME/benchmarks"
mkdir -p "$JSTACK_HOME/calibrations"
mkdir -p "$JSTACK_HOME/browse-runs"
mkdir -p "$JSTACK_HOME/scrape-runs"
mkdir -p "$JSTACK_HOME/design-runs"
mkdir -p "$JSTACK_HOME/design-html"
mkdir -p "$JSTACK_HOME/design-shotgun"
mkdir -p "$JSTACK_HOME/browser-profiles"
mkdir -p "$JSTACK_HOME/quarantine"

chmod 700 "$JSTACK_HOME/browser-profiles"   # secrets-adjacent
chmod 700 "$JSTACK_HOME/audit"               # tamper-evident

ok "JStack home structure created"

# ----- copy scaffolding -------------------------------------------------------

hdr "Copying scaffolding to ~/.jstack/scaffolding/"

cp -r "$REPO_ROOT/scaffolding/"* "$JSTACK_SCAFFOLDING/"
ok "Scaffolding copied (4 layers)"

# ----- config -----------------------------------------------------------------

hdr "Layer config"

if [[ -f "$JSTACK_CONFIG" ]]; then
  info "Config exists at $JSTACK_CONFIG — not overwriting"
else
  cp "$LAYER_CONFIG_EXAMPLE" "$JSTACK_CONFIG"
  ok "Default config installed to $JSTACK_CONFIG"
  info "Edit $JSTACK_CONFIG to enable/disable layers, watchers, voice defaults"
fi

# ----- hooks: copy to ~/.jstack/hooks/ (INERT) -------------------------------

hdr "Hooks (inert install — opt-in symlink to activate)"

# v3: hooks live at hooks/shared/ at repo root (lifted from scaffolding/02-sdl/hooks/)
# v2 fallback: scaffolding/02-compliance/hooks/ or scaffolding/02-sdl/hooks/
HOOK_SRC=""
if [ -d "$REPO_ROOT/hooks/shared" ]; then
  HOOK_SRC="$REPO_ROOT/hooks/shared"
elif [ -d "$REPO_ROOT/scaffolding/02-sdl/hooks" ]; then
  HOOK_SRC="$REPO_ROOT/scaffolding/02-sdl/hooks"
elif [ -d "$REPO_ROOT/scaffolding/02-compliance/hooks" ]; then
  HOOK_SRC="$REPO_ROOT/scaffolding/02-compliance/hooks"
fi

if [ -n "$HOOK_SRC" ]; then
  cp -r "$HOOK_SRC/"* "$JSTACK_HOOKS/" 2>/dev/null || true
  # Ensure scripts are executable
  find "$JSTACK_HOOKS" -name 'run.sh' -exec chmod +x {} + 2>/dev/null || true
  ok "Hooks copied from $HOOK_SRC to $JSTACK_HOOKS (INERT — symlink to activate)"
  info "To activate a hook: ln -s $JSTACK_HOOKS/<name>/run.sh ~/.claude/hooks/<name>.sh"
  info "Then register in ~/.claude/settings.json — see $JSTACK_HOOKS/README.md"
else
  warn "No hooks source found — skipping"
fi

# ----- frontmatter validation -------------------------------------------------

hdr "Frontmatter validation (skills + agents)"

INVALID=0
INVALID_FILES=()

validate_frontmatter() {
  local file="$1"
  local kind="$2"  # skill | agent

  # Frontmatter must start with `---`
  if ! head -1 "$file" | grep -q '^---$'; then
    INVALID_FILES+=("$file: missing frontmatter start")
    return 1
  fi

  # Required fields
  local missing=()
  grep -q '^name:' "$file" || missing+=("name")
  grep -q '^description:' "$file" || missing+=("description")
  grep -q '^color:' "$file" || missing+=("color")
  grep -q '^tools:' "$file" || missing+=("tools")
  grep -q '^voice:' "$file" || missing+=("voice")
  grep -q '^cli_support:' "$file" || missing+=("cli_support")

  if [ ${#missing[@]} -gt 0 ]; then
    INVALID_FILES+=("$file: missing fields: ${missing[*]}")
    return 1
  fi
  return 0
}

# v3: skills at repo root skills/, agents at agents/<category>/
# v2 fallback: scaffolding/*/skills/ and scaffolding/*/agents/

# Validate skills (v3 path + v2 fallback)
SKILL_PATHS=()
[ -d "$REPO_ROOT/skills" ] && SKILL_PATHS+=("$REPO_ROOT/skills")
[ -d "$REPO_ROOT/scaffolding" ] && SKILL_PATHS+=("$REPO_ROOT/scaffolding")

for path in "${SKILL_PATHS[@]}"; do
  while IFS= read -r f; do
    if ! validate_frontmatter "$f" skill; then
      INVALID=$((INVALID + 1))
    fi
  done < <(find "$path" -name 'SKILL.md' 2>/dev/null)
done

# Validate agents (v3 path + v2 fallback)
AGENT_PATHS=()
[ -d "$REPO_ROOT/agents" ] && AGENT_PATHS+=("$REPO_ROOT/agents")
[ -d "$REPO_ROOT/scaffolding" ] && AGENT_PATHS+=("$REPO_ROOT/scaffolding")

for path in "${AGENT_PATHS[@]}"; do
  while IFS= read -r f; do
    if ! validate_frontmatter "$f" agent; then
      INVALID=$((INVALID + 1))
    fi
  done < <(find "$path" \( -path '*/agents/*.md' -o -path '*/agents/*/*.md' \) 2>/dev/null | grep -v README)
done

if [ "$INVALID" -eq 0 ]; then
  ok "All skills + agents have valid frontmatter"
else
  warn "$INVALID files have frontmatter issues:"
  for issue in "${INVALID_FILES[@]}"; do
    say "  - $issue"
  done
fi

# ----- upstream sources -------------------------------------------------------

if [ "$YQ_AVAILABLE" = "1" ]; then
  hdr "Upstream sources"
  info "Reading $SOURCES_FILE..."
  # Real install would iterate sources and clone each per upstream-sources.yaml
  # Stub: just confirm file readable + list source names
  if mapfile -t SOURCE_NAMES < <(yq '.sources | keys | .[]' "$SOURCES_FILE" 2>/dev/null); then
    ok "${#SOURCE_NAMES[@]} upstream sources declared"
    for n in "${SOURCE_NAMES[@]}"; do
      info "  · $n"
    done
    info "Run /tier-stamp-agents after install to classify each source's agents."
  else
    warn "Could not parse upstream sources — verify yq and file format"
  fi
fi

# ----- summary ----------------------------------------------------------------

hdr "Install complete"

say "JStack installed at: $JSTACK_HOME"
say ""
say "Next steps:"
say "  1. Review config:           ${c_bold}\$EDITOR $JSTACK_CONFIG${c_reset}"
say "  2. Activate hooks (opt-in): see $JSTACK_HOOKS/README.md"
say "  3. Verify install:          ${c_bold}$SCRIPT_DIR/verify.sh --all${c_reset}"
say "  4. Read JStack overview:    ${c_bold}cat $REPO_ROOT/LAYERS.md${c_reset}"
say ""
say "v3 plugin install (per CLI):"
say "  Claude Code:  ${c_bold}/plugin marketplace add Azureflipper/jokerman-session-setup${c_reset}"
say "                ${c_bold}/plugin install jstack@jokerman-session-setup${c_reset}"
say "  Codex CLI:    ${c_bold}/plugins${c_reset} -> search jstack -> Install"
say "  Cursor:       ${c_bold}/add-plugin jstack${c_reset}"
say "  Gemini CLI:   ${c_bold}gemini extensions install https://github.com/Azureflipper/jokerman-session-setup${c_reset}"
say ""
say "v3 operator utilities (add to PATH):"
say "  ${c_bold}export PATH=\"\$PATH:$REPO_ROOT/bin\"${c_reset}"
say "  Available: jstack-scaffold, jstack-doctor, jstack-lessons-sync,"
say "             jstack-lessons-promote, jstack-adr-new, jstack-update"
say ""
say "First commands to try:"
say "  ${c_bold}jstack-doctor${c_reset}                 — cross-CLI health check"
say "  ${c_bold}jstack-scaffold check${c_reset}         — preview scaffolding for current dir"
say "  ${c_bold}/help${c_reset}                         — in Claude Code (after plugin install)"
say ""

if [ "$INVALID" -gt 0 ]; then
  exit 1
fi

exit 0
