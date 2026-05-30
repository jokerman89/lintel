#!/usr/bin/env bash
# tests/shape/orientator-decisions-audited.sh
# Asserts (v4.0 Phase 3): orientator skill exists + routing lib exists + SENSE
# invokes orientator + audit path is documented.
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/orientator-decisions-audited.sh"
echo "============================================="

# Skill exists
if [ -f "$REPO_ROOT/skills/orientator/SKILL.md" ]; then
  pass "skills/orientator/SKILL.md present"
else
  fail "skills/orientator/SKILL.md MISSING"
fi

# Routing lib exists
if [ -f "$REPO_ROOT/lib/orientator-routing.sh" ]; then
  pass "lib/orientator-routing.sh present"
else
  fail "lib/orientator-routing.sh MISSING"
fi

# Required public functions in routing lib
for fn in classify_intent match_workflow assess_risk score_confidence check_escalation_threshold invoke_llm_orientation; do
  if grep -qE "^${fn}\(\)" "$REPO_ROOT/lib/orientator-routing.sh" 2>/dev/null; then
    pass "routing lib exports $fn()"
  else
    fail "routing lib MISSING function $fn()"
  fi
done

# SENSE invokes orientator (Step 0d)
if grep -qE "Step 0d.*[Oo]rientator|orientator-routing\.sh" "$REPO_ROOT/skills/sense/SKILL.md" 2>/dev/null; then
  pass "SENSE Step 0d invokes orientator"
else
  fail "SENSE does not document orientator invocation at Step 0d"
fi

# Skill documents audit path
if grep -qE "orientator-decisions\.jsonl" "$REPO_ROOT/skills/orientator/SKILL.md" 2>/dev/null; then
  pass "orientator audit path documented"
else
  fail "orientator skill does not document audit path"
fi

# Skill documents pack-overridable parameters
for f in orientator_budget_tokens escalation_threshold high_risk_workflows auto_mode_eligible; do
  if grep -q "$f" "$REPO_ROOT/skills/orientator/SKILL.md" 2>/dev/null; then
    pass "orientator skill references pack field $f"
  else
    fail "orientator skill does not document pack field $f"
  fi
done

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All orientator-decisions-audited assertions PASSED"; exit 0
else echo "Some orientator-decisions-audited assertions FAILED"; exit 1; fi
