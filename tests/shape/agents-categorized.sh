#!/usr/bin/env bash
# tests/shape/agents-categorized.sh
# Asserts: every agent under agents/<category>/ declares matching `category:`.
# Wraps existing tests/unit/agents-categorized.sh.
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXISTING="$REPO_ROOT/tests/unit/agents-categorized.sh"

if [ -f "$EXISTING" ]; then
  bash "$EXISTING"
  exit $?
fi

# Fallback inline check (if unit test missing for any reason)
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/agents-categorized.sh (fallback)"
echo "=============================================="

mismatch=0
for f in $(find "$REPO_ROOT/agents" -name '*.md' 2>/dev/null | grep -v README); do
  dir_cat=$(basename "$(dirname "$f")")
  file_cat=$(grep '^category:' "$f" 2>/dev/null | head -1 | awk '{print $2}')
  if [ "$dir_cat" != "$file_cat" ]; then
    mismatch=$((mismatch+1))
    [ "$mismatch" -le 5 ] && echo "    mismatch: $(basename "$f") in $dir_cat/ declares category: $file_cat"
  fi
done

if [ "$mismatch" -eq 0 ]; then
  pass "All agents' category matches directory"
else
  fail "$mismatch category mismatches"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All agents-categorized assertions PASSED"; exit 0
else echo "Some agents-categorized assertions FAILED"; exit 1; fi
