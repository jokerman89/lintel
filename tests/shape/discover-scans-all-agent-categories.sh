#!/usr/bin/env bash
# tests/shape/discover-scans-all-agent-categories.sh
# Asserts: DISCOVER's Step 6 agent scan is directory-derived (iterates agents/*/)
#          and does NOT hardcode a category list, so it can never drift from the
#          actual agent categories (e.g. silently omitting `frontend`).
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL="$REPO_ROOT/skills/discover/SKILL.md"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/discover-scans-all-agent-categories.sh"
echo "===================================================="

if [ ! -f "$SKILL" ]; then
  fail "skills/discover/SKILL.md not found"
  echo ""
  echo "Some discover-scans-all-agent-categories assertions FAILED"
  exit 1
fi

# 1. The scan must be directory-derived.
if grep -q 'for cat_dir in agents/\*/' "$SKILL"; then
  pass "Agent scan iterates agents/*/ (directory-derived)"
else
  fail "Agent scan is not directory-derived (expected 'for cat_dir in agents/*/')"
fi

# 2. The scan must NOT hardcode a space-separated category list.
#    Catches the regressed form: 'for cat in ms-specific engineering security ...'
if grep -Eq 'for cat in [a-z]+(-[a-z]+)? [a-z]' "$SKILL"; then
  fail "Agent scan hardcodes a category list (will drift from agents/)"
  grep -nE 'for cat in [a-z]+(-[a-z]+)? [a-z]' "$SKILL" | head -1 | sed 's/^/    offending: /'
else
  pass "No hardcoded category list present"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All discover-scans-all-agent-categories assertions PASSED"
  exit 0
else
  echo "Some discover-scans-all-agent-categories assertions FAILED"
  exit 1
fi
