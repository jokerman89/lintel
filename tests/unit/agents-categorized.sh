#!/usr/bin/env bash
# tests/unit/agents-categorized.sh
#
# Verifies all v3 agents have category frontmatter + proper directory placement.
# tag: v3 critical

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

FAILED=0

echo "tests/unit/agents-categorized.sh"
echo "================================="

if [ ! -d "$REPO_ROOT/agents" ]; then
  fail "agents/ directory missing at repo root"
  exit 1
fi

# Each agent file must have category: frontmatter
total=0
no_category=0
for f in $(find "$REPO_ROOT/agents" -name '*.md' 2>/dev/null | grep -v README); do
  total=$((total + 1))
  if ! grep -q '^category:' "$f"; then
    fail "missing category: $(realpath --relative-to="$REPO_ROOT" "$f")"
    no_category=$((no_category + 1))
  fi
done

if [ "$no_category" = "0" ]; then
  pass "all $total agents have category frontmatter"
fi

# Category matches directory
mismatch=0
for f in $(find "$REPO_ROOT/agents" -name '*.md' 2>/dev/null | grep -v README); do
  dir_cat=$(basename "$(dirname "$f")")
  file_cat=$(grep '^category:' "$f" | head -1 | awk '{print $2}')
  if [ "$dir_cat" != "$file_cat" ]; then
    fail "category mismatch: $(basename "$f") in dir '$dir_cat' but declares 'category: $file_cat'"
    mismatch=$((mismatch + 1))
  fi
done

if [ "$mismatch" = "0" ]; then
  pass "all agents' category matches their directory"
fi

# Expected categories present
EXPECTED_CATEGORIES=(ms-specific engineering security compliance devops customer communication doc-gen voice)
for cat in "${EXPECTED_CATEGORIES[@]}"; do
  if [ -d "$REPO_ROOT/agents/$cat" ]; then
    count=$(find "$REPO_ROOT/agents/$cat" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -gt 0 ]; then
      pass "category dir '$cat' has $count agent(s)"
    else
      fail "category dir '$cat' exists but is empty"
    fi
  else
    fail "expected category dir missing: $cat"
  fi
done

# Total agent count must be reasonable (>= 60 for v3)
if [ "$total" -ge 60 ]; then
  pass "total agent count $total >= 60 (v3 expectation)"
else
  fail "total agent count $total < 60 (v3 expects >= 60)"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All agent categorization tests PASSED"
  exit 0
else
  echo "Some agent categorization tests FAILED"
  exit 1
fi
