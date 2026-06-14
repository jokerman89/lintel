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
validate_json() {
  local file="$1"
  if command -v python3 >/dev/null 2>&1; then
    python3 -c "import json,sys;json.load(open(sys.argv[1]))" "$file" 2>/dev/null
  elif command -v jq >/dev/null 2>&1; then
    jq empty "$file" 2>/dev/null
  else
    echo "  WARN: no python3/jq available — skipping JSON validation"
    return 0
  fi
}

# Required manifests
MANIFESTS=(
  "$REPO_ROOT/.claude-plugin/plugin.json"
  "$REPO_ROOT/.claude-plugin/marketplace.json"
  "$REPO_ROOT/.codex-plugin/plugin.json"
  "$REPO_ROOT/.cursor-plugin/plugin.json"
  "$REPO_ROOT/gemini-extension.json"
)

for m in "${MANIFESTS[@]}"; do
  if [ ! -f "$m" ]; then
    fail "missing: $m"
  fi
  if validate_json "$m"; then
    pass "valid JSON: $(basename "$(dirname "$m")")/$(basename "$m")"
  else
    fail "INVALID JSON: $m"
  fi
done

# OpenCode INSTALL.md (markdown, not JSON)
if [ -f "$REPO_ROOT/.opencode/INSTALL.md" ]; then
  pass "exists: .opencode/INSTALL.md"
else
  fail "missing: .opencode/INSTALL.md"
fi

# Root entrypoint context files
for f in CLAUDE.md AGENTS.md GEMINI.md; do
  if [ -f "$REPO_ROOT/$f" ]; then
    pass "root entrypoint: $f"
  else
    fail "missing root entrypoint: $f"
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

  # Gemini contextFileName
  if python3 -c "
import json,sys
m = json.load(open(sys.argv[1]))
sys.exit(0 if m.get('contextFileName') == 'GEMINI.md' else 1)
" "$REPO_ROOT/gemini-extension.json"; then
    pass "gemini-extension contextFileName -> GEMINI.md"
  else
    fail "gemini-extension contextFileName missing or wrong"
  fi
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All plugin manifest tests PASSED"
  exit 0
else
  echo "Some plugin manifest tests FAILED"
  exit 1
fi
