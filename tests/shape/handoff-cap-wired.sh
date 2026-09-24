#!/usr/bin/env bash
# tests/shape/handoff-cap-wired.sh
# Asserts selected-work handoff budgeting is WIRED at both handoffs.
# Authority: accepted P03 500adb3, skills/context-budget/SKILL.md
# "Shared admission reader" and "Local thresholds and compatibility";
# lib/context_safety.py::context_budget. Unknown capacity stays unknown.
# Behavior/threshold evidence lives in integration/universal-work-lifecycle.py.
# This is a structural guard, not a model/runtime invocation. The
# regression risk is that PLAN/CAPTURE silently stop invoking it. This test
# pins the wiring so it can't regress un-noticed:
#   W1 — PLAN (trio-emit) invokes /li:handoff-size-check, non-blocking,
#        with an off-switch
#   W2 — CAPTURE (trio-reaffirm) invokes /li:handoff-size-check, non-blocking,
#        with an off-switch
#   W3 — shared selected-map/P03 reader exists, with unknown/provenance semantics
#   W4 — BUILD's per-task review is complexity-gated (mechanical → inline,
#        substantive → two-stage dedicated), keyed to agent-dispatch-rules
# tag: shape v4.9 handoff-cap-wiring

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/handoff-cap-wired.sh"
echo "================================="

PLAN="$REPO_ROOT/skills/plan/SKILL.md"
CAPTURE="$REPO_ROOT/skills/capture/SKILL.md"
BUILD="$REPO_ROOT/skills/build/SKILL.md"
HSC="$REPO_ROOT/skills/handoff-size-check/SKILL.md"
CTXBUDGET="$REPO_ROOT/skills/context-budget/SKILL.md"
DISPATCH="$REPO_ROOT/docs/concepts/agent-dispatch-rules.md"

# ─── W1: PLAN invokes the cap check at the trio-emit point ───────────────────
echo ""
echo "[W1] PLAN (trio-emit) wires the cap check"
if [ -f "$PLAN" ]; then
  grep -q "/li:handoff-size-check" "$PLAN" \
    && pass "plan references /li:handoff-size-check (portable skill call)" \
    || fail "plan does NOT invoke /li:handoff-size-check"
  grep -qiE "non-?blocking|surface, don'?t block|does NOT (halt|block)" "$PLAN" \
    && pass "plan cap check is non-blocking (surfaces, does not halt)" \
    || fail "plan cap check missing non-blocking semantics"
  grep -q -- "--skip-handoff-size-check" "$PLAN" \
    && pass "plan cap check has an off-switch (--skip-handoff-size-check)" \
    || fail "plan cap check missing off-switch"
  grep -q "/li:handoff-size-check --map" "$PLAN" \
    && pass "plan carries the selected map to budgeting" \
    || fail "plan budget call loses explicit work selection"
else
  fail "skills/plan/SKILL.md MISSING"
fi

# ─── W2: CAPTURE invokes the cap check at the trio-reaffirm point ────────────
echo ""
echo "[W2] CAPTURE (trio-reaffirm) wires the cap check"
if [ -f "$CAPTURE" ]; then
  grep -q "/li:handoff-size-check" "$CAPTURE" \
    && pass "capture references /li:handoff-size-check (portable skill call)" \
    || fail "capture does NOT invoke /li:handoff-size-check"
  grep -qiE "non-?blocking|surface, don'?t block|does NOT (halt|block)" "$CAPTURE" \
    && pass "capture cap check is non-blocking (surfaces, does not halt)" \
    || fail "capture cap check missing non-blocking semantics"
  grep -q -- "--skip-handoff-size-check" "$CAPTURE" \
    && pass "capture cap check has an off-switch (--skip-handoff-size-check)" \
    || fail "capture cap check missing off-switch"
  grep -q "/li:handoff-size-check --map" "$CAPTURE" \
    && pass "capture carries the same selected map to budgeting" \
    || fail "capture budget call loses explicit work selection"
else
  fail "skills/capture/SKILL.md MISSING"
fi

# ─── W3: the cap mechanism the calls resolve to still exists ─────────────────
echo ""
echo "[W3] the cap mechanism exists (calls resolve to something real)"
if [ -f "$HSC" ]; then
  pass "skills/handoff-size-check/SKILL.md exists"
  if grep -q 'li-work-artifacts.py' "$HSC" && grep -q -- '--view budget' "$HSC" &&
     grep -q 'context_budget' "$HSC" && grep -q 'unknown' "$HSC"; then
    pass "handoff reader uses selected artifacts and P03 budget with unknown capacity"
  else
    fail "handoff reader lost the actual shared budget mechanism or unknown boundary"
  fi
else
  fail "skills/handoff-size-check/SKILL.md MISSING (calls would dangle)"
fi
if [ -f "$CTXBUDGET" ]; then
  if grep -q 'context_budget' "$CTXBUDGET" && grep -q -- '--capacity-source' "$CTXBUDGET" &&
     grep -q 'unknown' "$CTXBUDGET"; then
    pass "context-budget carries actual helper, observation source and unknown capacity"
  else
    fail "context-budget lost the accepted P03 observation contract"
  fi
  if grep -q 'mode_envelopes' "$CTXBUDGET" &&
     grep -q 'not defaults for model capacity' "$CTXBUDGET"; then
    pass "historical local thresholds remain advice, not a fabricated host default"
  else
    fail "historical threshold compatibility or no-capacity-default boundary lost"
  fi
else
  fail "skills/context-budget/SKILL.md MISSING (cap source gone)"
fi

# ─── W4: BUILD per-task review is complexity-gated ───────────────────────────
echo ""
echo "[W4] BUILD review is complexity-gated (inline for mechanical, two-stage for substantive)"
if [ -f "$BUILD" ]; then
  grep -qiE "inline review" "$BUILD" \
    && pass "build documents inline review for mechanical/Haiku-tier tasks" \
    || fail "build missing inline-review gate for mechanical tasks"
  grep -qiE "two-stage (dedicated )?review" "$BUILD" \
    && pass "build keeps two-stage dedicated review for substantive tasks" \
    || fail "build dropped two-stage review for substantive tasks"
  # the gate must cite the dispatch-rules rule it follows
  grep -q "agent-dispatch-rules" "$BUILD" \
    && pass "build cites docs/concepts/agent-dispatch-rules.md for the gate" \
    || fail "build review gate does not cite agent-dispatch-rules"
  # off-switch-for-trivial, NOT removal-of-review
  grep -qiE "does NOT remove|not.*remove.*two-stage|off-switch for trivial" "$BUILD" \
    && pass "build gate is an off-switch for trivial tasks, NOT review removal" \
    || fail "build gate does not assert review is preserved for substantive work"
else
  fail "skills/build/SKILL.md MISSING"
fi

# the rule the gate leans on must exist
[ -f "$DISPATCH" ] && pass "docs/concepts/agent-dispatch-rules.md present" \
                    || fail "docs/concepts/agent-dispatch-rules.md MISSING"

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All handoff-cap-wired assertions PASSED"; exit 0
else echo "Some handoff-cap-wired assertions FAILED"; exit 1; fi
