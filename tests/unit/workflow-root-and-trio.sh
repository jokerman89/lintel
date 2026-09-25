#!/usr/bin/env bash
# tests/unit/workflow-root-and-trio.sh
#
# Verifies v3.8 Feature 1 (workflow_root flag) + Feature 2 (planner-as-module).
# tag: v3.8 feature-1 feature-2

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/workflow-root-and-trio.sh"
echo "===================================="

# Feature 1: cycle + plan declare workflow_root: true
WORKFLOW_ROOT_SKILLS=(cycle plan)
for s in "${WORKFLOW_ROOT_SKILLS[@]}"; do
  f="$REPO_ROOT/skills/$s/SKILL.md"
  if [ -f "$f" ]; then
    if grep -qE "^workflow_root:[[:space:]]*true" "$f"; then
      pass "skill $s declares workflow_root: true"
    else
      fail "skill $s missing workflow_root: true flag"
    fi
  else
    fail "skill $s missing"
  fi
done

# Feature 2.2: PLAN documents the trio born together
PLAN="$REPO_ROOT/skills/plan/SKILL.md"
if [ -f "$PLAN" ]; then
  if grep -q "BORN TOGETHER\|born together" "$PLAN"; then
    pass "plan/SKILL.md documents 'born together' trio (Feature 2.2)"
  else
    fail "plan/SKILL.md missing 'born together' language"
  fi

  if grep -qE "prompt\.md" "$PLAN" && grep -qE "v3\.8 Feature 2\.2" "$PLAN"; then
    pass "plan/SKILL.md references prompt.md + Feature 2.2 explicit"
  else
    fail "plan/SKILL.md missing prompt.md or Feature 2.2 reference"
  fi

  if grep -q "Module-callable" "$PLAN"; then
    pass "plan/SKILL.md has Module-callable section (Feature 2.4)"
  else
    fail "plan/SKILL.md missing Module-callable section"
  fi

  if grep -q "no-job\|NO_JOB" "$PLAN"; then
    pass "plan/SKILL.md documents --no-job nested-call escape (Feature 2.4)"
  else
    fail "plan/SKILL.md missing --no-job documentation"
  fi
else
  fail "plan/SKILL.md missing"
fi

# Feature 2.2: CAPTURE no longer generates prompt.md (reaffirm only)
CAPTURE="$REPO_ROOT/skills/capture/SKILL.md"
if [ -f "$CAPTURE" ]; then
  # Capture should mention "reaffirm" or "v3.8" or note move
  if grep -qE "reaffirm|v3\.8 Feature 2\.2|BORN in PLAN|born in PLAN" "$CAPTURE"; then
    pass "capture/SKILL.md acknowledges trio born in PLAN (Feature 2.2)"
  else
    fail "capture/SKILL.md missing v3.8 trio-move acknowledgment"
  fi

  # Step 6 heading should now indicate REAFFIRM not NEW
  if grep -qE "Step 6 — Cold-executor handoff trio \(REAFFIRM" "$CAPTURE"; then
    pass "capture/SKILL.md Step 6 heading says REAFFIRM (not NEW v3.5)"
  else
    fail "capture/SKILL.md Step 6 heading not updated"
  fi
else
  fail "capture/SKILL.md missing"
fi

# Short leaves remain a substantive inspection obligation, not a naming check.
INSPECT="$REPO_ROOT/skills/inspect/SKILL.md"
if [ -f "$INSPECT" ]; then
  if grep -q "Granularity hard check" "$INSPECT" &&
     grep -q "every leaf" "$INSPECT" &&
     grep -q "2-5 minutes" "$INSPECT"; then
    pass "inspect checks granularity and acceptance for every leaf"
  else
    fail "inspect missing the per-leaf granularity contract"
  fi

  if grep -q "Decompose now" "$INSPECT" &&
     grep -q "Accept with concern" "$INSPECT" &&
     grep -q "operator authority" "$INSPECT"; then
    pass "inspect retains authorized decompose-or-concern decisions"
  else
    fail "inspect missing the decomposition decision path"
  fi
  for lens in engineering design devex; do
    grep -q "/li:inspect --target plan --lens $lens" "$PLAN" \
      && pass "PLAN routes the $lens lens to inspect" \
      || fail "PLAN does not route the $lens lens to inspect"
  done
  grep -q -- "--skill inspect" "$PLAN" &&
    grep -q -- "--expected" "$PLAN" &&
    grep -q -- "--corroboration" "$PLAN" \
    && pass "PLAN consumes explicitly selected bound inspection evidence" \
    || fail "PLAN lost the shared latest-reader selection"
else
  fail "skills/inspect/SKILL.md missing"
fi

# Concept docs present
CONCEPT_JOBS="$REPO_ROOT/docs/concepts/jobs-system.md"
CONCEPT_PLAN="$REPO_ROOT/docs/concepts/planner-as-module.md"
[ -f "$CONCEPT_JOBS" ] && pass "docs/concepts/jobs-system.md present" || fail "docs/concepts/jobs-system.md missing"
[ -f "$CONCEPT_PLAN" ] && pass "docs/concepts/planner-as-module.md present" || fail "docs/concepts/planner-as-module.md missing"

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All workflow-root-and-trio tests PASSED"
  exit 0
else
  echo "Some workflow-root-and-trio tests FAILED"
  exit 1
fi
