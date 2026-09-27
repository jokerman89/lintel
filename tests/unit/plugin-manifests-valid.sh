#!/usr/bin/env bash
# tests/unit/plugin-manifests-valid.sh
#
# Verifies that v3 plugin manifests are present and valid JSON.
# tag: v3 critical
#
# Pre-req: bash, python3 or jq

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Inline test helpers (avoid template that auto-passes)
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }
assert_file_exists() { [ -f "$1" ] && pass "exists: $1" || fail "missing: $1"; }

echo "tests/unit/plugin-manifests-valid.sh"
echo "===================================="

# JSON validator (python3 or jq)
JSON_VALIDATOR=""
if command -v python3 >/dev/null 2>&1; then
  JSON_VALIDATOR=python3
elif command -v jq >/dev/null 2>&1; then
  JSON_VALIDATOR=jq
fi

validate_json() {
  local file="$1"
  case "$JSON_VALIDATOR" in
    python3) python3 -c "import json,sys;json.load(open(sys.argv[1]))" "$file" 2>/dev/null ;;
    jq) jq empty "$file" 2>/dev/null ;;
    *) echo "ERROR: JSON validation requested without a parser" >&2; return 1 ;;
  esac
}

# Required manifests
MANIFESTS=(
  "$REPO_ROOT/.claude-plugin/plugin.json"
  "$REPO_ROOT/.claude-plugin/marketplace.json"
  "$REPO_ROOT/.codex-plugin/plugin.json"
  "$REPO_ROOT/.cursor-plugin/plugin.json"
  "$REPO_ROOT/.github/plugin/plugin.json"
  "$REPO_ROOT/.github/plugin/marketplace.json"
)

for m in "${MANIFESTS[@]}"; do
  if [ ! -f "$m" ]; then
    fail "missing: $m"
    continue
  fi
  if [ -z "$JSON_VALIDATOR" ]; then
    echo "  SKIP: no python3/jq available — JSON validation not run: $m"
  elif validate_json "$m"; then
    pass "valid JSON: $(basename "$(dirname "$m")")/$(basename "$m")"
  else
    fail "INVALID JSON: $m"
  fi
done

# Root entrypoint context files
for f in CLAUDE.md AGENTS.md; do
  if [ -f "$REPO_ROOT/$f" ]; then
    pass "root entrypoint: $f"
  else
    fail "missing root entrypoint: $f"
  fi
done

# Only Copilot, Claude, Codex and Cursor are supported (ADR-0035); removed client routes stay out
# of the shipped tree. In a checkout only tracked files count, so a contributor's local tool
# configuration (an untracked .opencode/ or GEMINI.md) is not a failure.
removed_route_shipped() {
  local tracked
  if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    # A Git error must not read as absence.
    tracked=$(git -C "$REPO_ROOT" ls-files -- "$1") || return 0
    [ -n "$tracked" ]
  else
    [ -e "$REPO_ROOT/$1" ]
  fi
}
for f in GEMINI.md gemini-extension.json .opencode; do
  if removed_route_shipped "$f"; then
    fail "removed client route present: $f"
  else
    pass "removed client route absent: $f"
  fi
done

# Verify Claude plugin manifest has required fields (passing path as argv)
if command -v python3 >/dev/null 2>&1; then
  if python3 -c "
import json,sys
m = json.load(open(sys.argv[1]))
required = ['name', 'description', 'version']
missing = [r for r in required if r not in m]
sys.exit(1 if missing else 0)
" "$REPO_ROOT/.claude-plugin/plugin.json"; then
    pass "claude-plugin manifest has required fields (name/description/version)"
  else
    fail "claude-plugin manifest missing required field(s)"
  fi

  # Codex interface{} block
  if python3 -c "
import json,sys
m = json.load(open(sys.argv[1]))
sys.exit(0 if 'interface' in m else 1)
" "$REPO_ROOT/.codex-plugin/plugin.json"; then
    pass "codex-plugin manifest has interface{} block"
  else
    fail "codex-plugin manifest missing interface{} block"
  fi

  # Cursor skills + agents paths
  if python3 -c "
import json,sys
m = json.load(open(sys.argv[1]))
sys.exit(0 if m.get('skills') == './skills/' and m.get('agents') == './agents/' else 1)
" "$REPO_ROOT/.cursor-plugin/plugin.json"; then
    pass "cursor-plugin manifest points at ./skills/ + ./agents/"
  else
    fail "cursor-plugin manifest path issue"
  fi
else
  echo "  SKIP: python3 absent — manifest field assertions not run"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "Executed plugin manifest checks PASSED"
  exit 0
else
  echo "Some plugin manifest tests FAILED"
  exit 1
fi
