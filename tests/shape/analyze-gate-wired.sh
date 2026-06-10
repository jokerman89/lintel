#!/usr/bin/env bash
# tests/shape/analyze-gate-wired.sh
# Asserts the /li:analyze consistency gate (ADR-0004) exists and is wired:
# the skill is present with its contract pieces, PLAN Step 8 delegates to it
# (no re-implemented inline checks), BUILD's final pass calls it, and the
# ADR + report path are declared. Convergent #6 regression guard.
# tag: shape v4.12

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/analyze-gate-wired.sh"
echo "==================================="

SKILL="$REPO_ROOT/skills/analyze/SKILL.md"
PLAN="$REPO_ROOT/skills/plan/SKILL.md"
BUILD="$REPO_ROOT/skills/build/SKILL.md"
ADR="$REPO_ROOT/docs/adr/0004-analyze-consistency-gate.md"

# 1. Skill exists with the contract pieces
if [ -f "$SKILL" ]; then
  pass "skills/analyze/SKILL.md exists"
  grep -q "^name: analyze$" "$SKILL" && pass "frontmatter name: analyze" || fail "frontmatter name drift"
  grep -q "analyze-report.md" "$SKILL" && pass "persisted report path declared" || fail "report path missing"
  for leg in "DEFINE↔PLAN" "PLAN↔BUILD" "Authority alignment"; do
    grep -q "$leg" "$SKILL" && pass "leg documented: $leg" || fail "leg missing: $leg"
  done
  grep -q "GREEN | YELLOW | RED" "$SKILL" && pass "verdict scale declared" || fail "verdict scale missing"
  grep -q "Cycle-position footer" "$SKILL" && pass "footer convention present (ADR-0003)" || fail "footer section missing"
else
  fail "skills/analyze/SKILL.md missing"
fi

# 2. PLAN Step 8 delegates (and does not keep the old inline checklist)
if grep -q "delegates to /li:analyze" "$PLAN"; then
  pass "PLAN Step 8 delegates to /li:analyze"
else
  fail "PLAN Step 8 does not delegate to /li:analyze"
fi
if grep -q "Does plan.md cover all requirements in design doc?" "$PLAN"; then
  fail "PLAN Step 8 still carries the inline checklist (duplication — shared-schema violation)"
else
  pass "PLAN Step 8 inline checklist removed (single implementation)"
fi

# 3. BUILD final pass calls the build-final leg
if grep -q "build-final" "$BUILD" && grep -q "/li:analyze" "$BUILD"; then
  pass "BUILD final pass invokes /li:analyze (build-final trigger)"
else
  fail "BUILD final pass missing the /li:analyze call"
fi

# 4. ADR exists and is Accepted
if [ -f "$ADR" ] && grep -q "Accepted" "$ADR"; then
  pass "ADR-0004 exists and Accepted"
else
  fail "ADR-0004 missing or not Accepted"
fi

echo ""
if [ "$FAILED" -eq 1 ]; then echo "RESULT: FAIL"; exit 1; fi
echo "RESULT: PASS"
exit 0
