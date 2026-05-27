#!/usr/bin/env bash
# jokerman-session-setup install verifier.
#
# Reads upstream-sources.yaml and checks that each non-reference-only source has
# a clone present at the expected install_path with a .git directory inside.
# Also checks the scaffolding is in place at ~/.claude-scaffolding/.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCES_FILE="$SCRIPT_DIR/upstream-sources.yaml"

c_reset='\033[0m'
c_green='\033[32m'
c_yellow='\033[33m'
c_red='\033[31m'
c_dim='\033[2m'

ok()   { printf "${c_green}✓${c_reset} %s\n" "$1"; }
warn() { printf "${c_yellow}⚠${c_reset} %s\n" "$1"; }
fail() { printf "${c_red}✗${c_reset} %s\n" "$1"; }
info() { printf "${c_dim}·${c_reset} %s\n" "$1"; }

expand_path() {
  local p="$1"
  if [[ "$p" == "~"* ]]; then echo "${HOME}${p:1}"; else echo "$p"; fi
}

EXIT_CODE=0

# Pre-flight
command -v git >/dev/null || { fail "git not on PATH"; EXIT_CODE=1; }
command -v yq  >/dev/null || { fail "yq not on PATH";  EXIT_CODE=1; }
[[ "$EXIT_CODE" -eq 0 ]] || exit "$EXIT_CODE"

# Scaffolding
echo "Scaffolding:"
if [[ -d "$HOME/.claude-scaffolding" ]]; then
  count=$(find "$HOME/.claude-scaffolding" -type f -name '*.md' | wc -l | tr -d ' ')
  ok "~/.claude-scaffolding/ exists ($count markdown files)"
else
  fail "~/.claude-scaffolding/ missing — re-run install.sh"
  EXIT_CODE=1
fi

# Canonical AGENT-INSTRUCTIONS.md
if [[ -f "$HOME/.claude-scaffolding/AGENT-INSTRUCTIONS.md" ]]; then
  ok "~/.claude-scaffolding/AGENT-INSTRUCTIONS.md present"
else
  warn "~/.claude-scaffolding/AGENT-INSTRUCTIONS.md missing"
  EXIT_CODE=1
fi

echo ""
echo "Upstream sources:"

mapfile -t SOURCE_NAMES < <(yq '.sources | keys | .[]' "$SOURCES_FILE")

for name in "${SOURCE_NAMES[@]}"; do
  name="${name//\"/}"
  install_type=$(yq ".sources.${name}.install_type" "$SOURCES_FILE" | tr -d '"')
  install_path_raw=$(yq ".sources.${name}.install_path" "$SOURCES_FILE" | tr -d '"')
  install_path=$(expand_path "$install_path_raw")

  if [[ "$install_type" == "reference-only" ]]; then
    info "$name (reference-only — not installed by design)"
    continue
  fi

  if [[ -d "$install_path/.git" ]]; then
    rev=$(cd "$install_path" && git rev-parse --short HEAD 2>/dev/null || echo "?")
    ok "$name @ $rev"
  else
    fail "$name missing at $install_path"
    EXIT_CODE=1
  fi
done

echo ""
if [[ "$EXIT_CODE" -eq 0 ]]; then
  ok "Verify: all expected sources are present."
else
  fail "Verify: some checks failed (exit $EXIT_CODE). Re-run install.sh to repair."
fi

exit "$EXIT_CODE"
