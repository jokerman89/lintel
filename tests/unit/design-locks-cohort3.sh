#!/usr/bin/env bash
# tests/unit/design-locks-cohort3.sh
#
# Verifies v3.6 cohort 3 design-locks + guardrails additions to existing skills.
# Cohort 3 modifies: context-budget (2.1+2.2+2.3), sense (3.1), cycle (2.5+1.5).
# tag: v3.6 cohort-3 design-locks

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/design-locks-cohort3.sh"
echo "================================="

# 2.1+2.2+2.3+3.3: context-budget 500k cap + mode-aware envelopes
CB="$REPO_ROOT/skills/context-budget/SKILL.md"
if [ -f "$CB" ]; then
  if grep -q "soft + 750k hard cap\|500k soft" "$CB"; then
    pass "context-budget has 500k soft + 750k hard cap logic (2.1)"
  else
    fail "context-budget missing 500k cap logic"
  fi

  if grep -q "mode_envelopes\|hotfix:.*soft.*hard\|mode-aware" "$CB"; then
    pass "context-budget has mode-aware envelopes (3.3)"
  else
    fail "context-budget missing mode-aware envelopes"
  fi

  if grep -q "[Ss]ynthetic.*[Rr]eal warming\|synthetic vs real" "$CB"; then
    pass "context-budget has synthetic-vs-real warming distinction (2.3)"
  else
    fail "context-budget missing synthetic-vs-real distinction"
  fi
fi

# 3.1: sense elephant-hint detection
SENSE="$REPO_ROOT/skills/sense/SKILL.md"
if [ -f "$SENSE" ]; then
  if grep -q "[Ee]lephant.*hint\|elephant_score" "$SENSE"; then
    pass "sense has elephant-hint detection (3.1)"
  else
    fail "sense missing elephant-hint detection"
  fi

  if grep -q "three paths\|Three paths\|3 paths" "$SENSE"; then
    pass "sense surfaces 3-paths (A/B/C) per design"
  else
    fail "sense missing 3-paths surface"
  fi
fi

# 2.5: cycle --dry-run flag
CYCLE="$REPO_ROOT/skills/cycle/SKILL.md"
if [ -f "$CYCLE" ]; then
  if grep -q "dry-run\|--dry-run\|DRY-RUN" "$CYCLE"; then
    pass "cycle has --dry-run flag support (2.5)"
  else
    fail "cycle missing --dry-run flag"
  fi
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All cohort-3 design-locks tests PASSED"
  exit 0
else
  echo "Some cohort-3 design-locks tests FAILED"
  exit 1
fi
