#!/usr/bin/env bash
# tests/shape/brief-forge-handoffs-canonical.sh
# Asserts (NEW v4.0): only canonical `brief_forge_handoffs:` field name used.
# No legacy short-form `brief_forge:` permitted in skills/agents/hooks/packs.
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/brief-forge-handoffs-canonical.sh"
echo "==============================================="

# Search for legacy `brief_forge:` field name (without _handoffs suffix)
# Exclude design docs (which mention both forms historically)
LEGACY=()
while IFS= read -r f; do
  LEGACY+=("$f")
done < <(grep -rln "^brief_forge:" "$REPO_ROOT/skills" "$REPO_ROOT/agents" "$REPO_ROOT/hooks" "$REPO_ROOT/packs" 2>/dev/null | grep -v "docs/" || true)

if [ "${#LEGACY[@]}" -eq 0 ]; then
  pass "No legacy `brief_forge:` field name in skills/agents/hooks/packs"
else
  fail "Legacy `brief_forge:` field found in ${#LEGACY[@]} files:"
  for f in "${LEGACY[@]}"; do echo "    - $f"; done
  echo "  Rename to canonical `brief_forge_handoffs:` per v4.0 §2.5 finding 2-P2.2"
fi

# Forward-positive: any v4.0-ready file using canonical name is OK
CANONICAL=()
while IFS= read -r f; do
  CANONICAL+=("$f")
done < <(grep -rln "brief_forge_handoffs:" "$REPO_ROOT/skills" "$REPO_ROOT/agents" "$REPO_ROOT/hooks" "$REPO_ROOT/packs" 2>/dev/null || true)

pass "Canonical `brief_forge_handoffs:` found in ${#CANONICAL[@]} file(s)"

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All brief-forge-handoffs-canonical assertions PASSED"; exit 0
else echo "Some brief-forge-handoffs-canonical assertions FAILED"; exit 1; fi
