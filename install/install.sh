#!/usr/bin/env bash
# jokerman-lintel (Lintel) installer — bash/Linux/macOS/WSL/Git Bash
#
# Honors Lintel architecture decisions:
# - A1/ADR-0008: this bare installer copies hooks to ~/.lintel/hooks/ INERT (bare install only —
#   operator manually symlinks + merges the snippet to opt in). A PLUGIN install instead
#   auto-registers them with zero setup via the plugin's hooks/hooks.json. Canonical matrix:
#   docs/getting-started.md#how-hook-activation-works
# - A2: scaffolding lives at ~/.lintel/scaffolding/ (separate from ~/.claude/)
# - A3: layer config at ~/.lintel/config.yaml — per-layer enable
# - A6: cli_support frontmatter validated at install time
# - C1: skill/agent frontmatter validated at install time
#
# Does NOT bundle upstream code. The upstream-sources.yaml step below is a STUB: it lists the
# declared sources, it does NOT clone them. SHA-pinned cloning is not implemented in this
# installer — Lintel currently ships only operator-authored content (see README "What you don't get").

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
source "$REPO_ROOT/lib/frontmatter.sh"
SOURCES_FILE="$SCRIPT_DIR/upstream-sources.yaml"
LAYER_CONFIG_EXAMPLE="$SCRIPT_DIR/layer-config.yaml.example"

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
LINTEL_SCAFFOLDING="$LINTEL_HOME/scaffolding"
LINTEL_HOOKS="$LINTEL_HOME/hooks"
LINTEL_CONFIG="$LINTEL_HOME/config.yaml"

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

canonical_destination() {
  local path="$1" parent suffix="" part
  local -a components=()
  case "$path" in [A-Za-z]:*)
    command -v cygpath >/dev/null 2>&1 && path="$(cygpath -u "$path")" ;;
  esac
  case "$path" in /*) ;; *) path="$PWD/$path" ;; esac
  # Normalize lexical traversal before resolving the nearest existing parent.
  local -a raw=()
  IFS=/ read -r -a raw <<< "$path"
  for part in "${raw[@]}"; do
    case "$part" in
      ''|.) ;;
      ..) [ ${#components[@]} -eq 0 ] || unset "components[$((${#components[@]} - 1))]" ;;
      *) components+=("$part") ;;
    esac
  done
  path="$(IFS=/; printf '/%s' "${components[*]}")"
  while [ ! -d "$path" ]; do
    suffix="/$(basename "$path")$suffix"
    parent="$(dirname "$path")"
    [ "$parent" != "$path" ] || return 1
    path="$parent"
  done
  printf '%s%s' "$(cd "$path" && pwd -P)" "$suffix"
}

# ----- pre-flight -------------------------------------------------------------

hdr "Lintel installer"
say "${c_dim}Repo: $REPO_ROOT${c_reset}"
say "${c_dim}Lintel home: $LINTEL_HOME${c_reset}"

if ! command -v git >/dev/null 2>&1; then
  fail "git not found — install git and re-run"
  exit 1
fi
ok "git found ($(git --version))"

# Validate every destination before backup or writes. A self-install may copy
# onto its own source, and cp follows pre-existing destination symlinks.
LINTEL_HOME="$(canonical_destination "$LINTEL_HOME")"
LINTEL_SCAFFOLDING="$LINTEL_HOME/scaffolding"
LINTEL_HOOKS="$LINTEL_HOME/hooks"
LINTEL_CONFIG="$LINTEL_HOME/config.yaml"
source_compare="${REPO_ROOT%/}/"
destination_compare="${LINTEL_HOME%/}/"
case "${OSTYPE:-}" in msys*|cygwin*)
  source_compare="$(printf '%s' "$source_compare" | tr '[:upper:]' '[:lower:]')"
  destination_compare="$(printf '%s' "$destination_compare" | tr '[:upper:]' '[:lower:]')" ;;
esac
case "$destination_compare" in "$source_compare"*)
  fail "LINTEL_HOME must be separate from the source checkout"; exit 1 ;; esac
case "$source_compare" in "$destination_compare"*)
  fail "LINTEL_HOME must not be an ancestor of the source checkout"; exit 1 ;; esac
if [ -d "$LINTEL_HOME" ]; then
  linked_entry="$(find "$LINTEL_HOME" -type l -print -quit)"
  if [ -n "$linked_entry" ]; then
    fail "Linked install entry refused before writes: $linked_entry"
    fail "Use a dedicated install home without symlinks; existing links were preserved."
    exit 1
  fi
fi

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

# ----- backup existing Lintel -------------------------------------------------

hdr "Backing up existing ~/.lintel/ (if any)"

if [[ -d "$LINTEL_HOME" ]]; then
  BACKUP="$LINTEL_HOME-backup-$(date +%Y%m%d-%H%M%S)"
  cp -r "$LINTEL_HOME" "$BACKUP"
  ok "Backed up to $BACKUP"
else
  info "No existing ~/.lintel/ — nothing to back up"
fi

# ----- create Lintel home structure ------------------------------------------

hdr "Creating ~/.lintel/ structure"

mkdir -p "$LINTEL_HOME"
mkdir -p "$LINTEL_SCAFFOLDING"
mkdir -p "$LINTEL_HOOKS"
mkdir -p "$LINTEL_HOME/audit"
mkdir -p "$LINTEL_HOME/sessions"
mkdir -p "$LINTEL_HOME/provenance"
mkdir -p "$LINTEL_HOME/freeze"
# Compliance-artifact directories are pack concerns, NOT spine — a company pack
# that needs them creates them on activation. The neutral installer stays company-neutral.
mkdir -p "$LINTEL_HOME/review-log"
mkdir -p "$LINTEL_HOME/benchmarks"
mkdir -p "$LINTEL_HOME/calibrations"
mkdir -p "$LINTEL_HOME/browse-runs"
mkdir -p "$LINTEL_HOME/scrape-runs"
mkdir -p "$LINTEL_HOME/design-runs"
mkdir -p "$LINTEL_HOME/design-html"
mkdir -p "$LINTEL_HOME/design-shotgun"
mkdir -p "$LINTEL_HOME/browser-profiles"
mkdir -p "$LINTEL_HOME/quarantine"
mkdir -p "$LINTEL_HOME/frontend-runs"      # v3.7 — frontend-design orchestrator run-output

# v3.7 Phase A2 — brand-asset slots for the frontend-* family
mkdir -p "$LINTEL_HOME/brand"
mkdir -p "$LINTEL_HOME/brand/design-patterns"
mkdir -p "$LINTEL_HOME/brand/motion-libraries"
mkdir -p "$LINTEL_HOME/brand/shader-snippets"
mkdir -p "$LINTEL_HOME/brand/palettes"
mkdir -p "$LINTEL_HOME/brand/fonts"

chmod 700 "$LINTEL_HOME/browser-profiles"   # secrets-adjacent
chmod 700 "$LINTEL_HOME/audit"               # operator-private on POSIX

ok "Lintel home structure created"

# ----- seed identity (ADR-0008: no silently-unconfigured identity layer) ------
# Every session before v5.0 ran the _default fallback because profile.yaml and
# packs/active-pack never existed. Seed them explicitly so identity is a stated
# fact, not a fallback. Never overwrite operator files.
if [ ! -f "$LINTEL_HOME/profile.yaml" ]; then
  cat > "$LINTEL_HOME/profile.yaml" <<'PROFEOF'
# Lintel operator profile (seeded by install.sh — edit freely)
active_pack: _default
default_mode: internal-tool
role_active: none
PROFEOF
  ok "profile.yaml seeded (_default / internal-tool)"
fi
mkdir -p "$LINTEL_HOME/packs"
if [ ! -f "$LINTEL_HOME/packs/active-pack" ]; then
  printf '_default' > "$LINTEL_HOME/packs/active-pack"
  ok "active-pack seeded (_default)"
fi

# ----- copy scaffolding -------------------------------------------------------

hdr "Copying scaffolding to ~/.lintel/scaffolding/"

cp -r "$REPO_ROOT/scaffolding/"* "$LINTEL_SCAFFOLDING/"
ok "Foundation scaffolding copied"

# Shared runtime helpers (lib/ + bin/) — the hooks installed under
# ~/.lintel/hooks resolve lib/memory.sh + bin/_jobs.sh here when no repo
# checkout is present (ADR-0006).
mkdir -p "$LINTEL_HOME/lib" "$LINTEL_HOME/bin" "$LINTEL_HOME/templates"
cp -R "$REPO_ROOT/lib/." "$LINTEL_HOME/lib/"
cp -R "$REPO_ROOT/bin/." "$LINTEL_HOME/bin/"
cp -R "$REPO_ROOT/templates/." "$LINTEL_HOME/templates/"
ok "Runtime helpers copied (lib/ + bin/ + templates/)"
for asset in skills agents shims docs; do
  mkdir -p "$LINTEL_HOME/$asset"
  cp -R "$REPO_ROOT/$asset/." "$LINTEL_HOME/$asset/"
done
cp "$REPO_ROOT/LICENSE" "$REPO_ROOT/AGENT-INSTRUCTIONS.md" "$LINTEL_HOME/"
ok "Copilot source assets copied (skills/ + agents/ + shims/ + docs/)"

# The installed resolver must work without this checkout. Seed only missing
# neutral identity; a local _default pack can contain operator customizations.
if [ ! -d "$LINTEL_HOME/packs/_default" ]; then
  cp -R "$REPO_ROOT/packs/_default" "$LINTEL_HOME/packs/_default"
  ok "Neutral pack installed"
fi

# ----- v3.7 brand-seeds (idempotent) -----------------------------------------

if [[ -d "$REPO_ROOT/seeds/brand" ]]; then
  hdr "Copying brand seeds to ~/.lintel/brand/ (idempotent — operator-extracted patterns preserved)"
  for seed_pattern in "$REPO_ROOT/seeds/brand/design-patterns/"*/; do
    [ -d "$seed_pattern" ] || continue
    pattern_name=$(basename "$seed_pattern")
    target="$LINTEL_HOME/brand/design-patterns/$pattern_name"
    if [[ -d "$target" ]]; then
      info "Pattern '$pattern_name' exists at $target — preserving operator state (idempotent)"
    else
      cp -r "$seed_pattern" "$target"
      ok "Seeded canonical pattern: $pattern_name → $target"
    fi
  done
fi

# ----- config -----------------------------------------------------------------

hdr "Layer config"

if [[ -f "$LINTEL_CONFIG" ]]; then
  info "Config exists at $LINTEL_CONFIG — not overwriting"
else
  cp "$LAYER_CONFIG_EXAMPLE" "$LINTEL_CONFIG"
  ok "Default config installed to $LINTEL_CONFIG"
  info "Edit $LINTEL_CONFIG to enable/disable layers, watchers, voice defaults"
fi

# ----- hooks: copy to ~/.lintel/hooks/ (INERT — bare install only) -----------

hdr "Hooks (inert — bare install only; opt-in symlink to activate. Plugin installs auto-register.)"

# Hooks live at hooks/shared/ at repo root
HOOK_SRC=""
if [ -d "$REPO_ROOT/hooks/shared" ]; then
  HOOK_SRC="$REPO_ROOT/hooks/shared"
fi

if [ -n "$HOOK_SRC" ]; then
  # shared/ layout (ADR-0008): matches the repo tree, the settings snippet, li-doctor's
  # drift check, and the scripts' BASH_SOURCE-relative ../_input.sh + ../../../bin lookups.
  mkdir -p "$LINTEL_HOOKS/shared"
  cp -R "$HOOK_SRC/." "$LINTEL_HOOKS/shared/"
  # Preserve legacy inert copies: custom hook directories belong to the operator.
  # Ensure scripts are executable
  find "$LINTEL_HOOKS" -name '*.sh' -exec chmod +x {} + 2>/dev/null || true
  ok "Hooks copied to $LINTEL_HOOKS/shared (Claude Code: auto-registered via the plugin's hooks/hooks.json)"
  info "Claude Code bare installs: register manually — see $LINTEL_HOOKS/shared/README.md"
  # session-digest is REQUIRED (ADR-0002): auto-loads the memory snowball at SessionStart.
  if [ -f "$LINTEL_HOOKS/shared/session-digest/run.sh" ]; then
    info "Non-plugin installs: merge $REPO_ROOT/hooks/claude-code/session-digest.settings.json"
    info "into ~/.claude/settings.json. Verify with: li-doctor"
  fi
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

  local issue
  if ! issue=$(validate_lintel_frontmatter "$file" "$kind"); then
    INVALID_FILES+=("$file: $issue")
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
  if source_names=$(yq '.sources | keys | .[]' "$SOURCES_FILE" 2>/dev/null); then
    SOURCE_NAMES=()
    while IFS= read -r source_name; do
      [ -n "$source_name" ] && SOURCE_NAMES+=("$source_name")
    done <<< "$source_names"
    ok "${#SOURCE_NAMES[@]} upstream sources declared (listed only — this installer does not clone them)"
    for n in "${SOURCE_NAMES[@]}"; do
      info "  · $n"
    done
  else
    warn "Could not parse upstream sources — verify yq and file format"
  fi
fi

# ----- summary ----------------------------------------------------------------

hdr "Install complete"

say "Lintel installed at: $LINTEL_HOME"
say ""
say "Next steps:"
say "  1. Review config:           ${c_bold}\$EDITOR $LINTEL_CONFIG${c_reset}"
say "  2. Claude Code hooks (opt-in): see $LINTEL_HOOKS/shared/README.md"
say "  3. Verify install:          ${c_bold}$SCRIPT_DIR/verify.sh --all${c_reset}"
say "  4. Read Lintel overview:    ${c_bold}cat $REPO_ROOT/docs/architecture.md${c_reset}"
say ""
say "Plugin install (per CLI):"
say "  Copilot:      see $REPO_ROOT/docs/copilot.md"
say "  Claude Code:  ${c_bold}/plugin marketplace add jokerman89/lintel${c_reset}"
say "                ${c_bold}/plugin install li@jokerman-lintel${c_reset}"
say "  Codex CLI:    ${c_bold}/plugins${c_reset} -> search lintel -> Install"
say "  Cursor:       ${c_bold}/add-plugin lintel${c_reset}"
say "  Gemini CLI:   ${c_bold}gemini extensions install https://github.com/jokerman89/lintel${c_reset}"
say ""
say "Operator utilities (add to PATH):"
say "  ${c_bold}export PATH=\"\$PATH:$LINTEL_HOME/bin\"${c_reset}"
say "  Available: li-scaffold, li-doctor, li-lessons-sync,"
say "             li-lessons-promote, li-adr-new, li-update"
say ""
say "First commands to try:"
say "  ${c_bold}li-doctor${c_reset}                 — cross-CLI health check"
say "  ${c_bold}li-scaffold check${c_reset}         — preview scaffolding for current dir"
say "  ${c_bold}/help${c_reset}                         — in Claude Code (after plugin install)"
say ""

if [ "$INVALID" -gt 0 ]; then
  exit 1
fi

exit 0
