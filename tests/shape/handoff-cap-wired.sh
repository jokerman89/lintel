#!/usr/bin/env bash
# tests/shape/handoff-cap-wired.sh
# Asserts (v4.9 cost-gap fix): the 500k handoff cap is WIRED at the two
# trio handoffs. The cap logic is prose-embedded shell in
# skills/handoff-size-check/SKILL.md (no sourceable function), so the
# regression risk is that PLAN/CAPTURE silently stop invoking it. This test
# pins the wiring so it can't regress un-noticed:
#   W1 — PLAN (trio-emit) invokes /li:handoff-size-check, non-blocking,
#        with an off-switch
#   W2 — CAPTURE (trio-reaffirm) invokes /li:handoff-size-check, non-blocking,
#        with an off-switch
#   W3 — the cap mechanism itself still exists (handoff-size-check skill +
#        the 500k cap in context-budget) so the calls resolve to something
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
  grep -qE "500k|500 ?k" "$PLAN" \
    && pass "plan references the 500k cap" \
    || fail "plan does not reference the 500k cap"
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
  grep -qE "500k|500 ?k" "$CAPTURE" \
    && pass "capture references the 500k cap" \
    || fail "capture does not reference the 500k cap"
else
  fail "skills/capture/SKILL.md MISSING"
fi

# ─── W3: the cap mechanism the calls resolve to still exists ─────────────────
echo ""
echo "[W3] the cap mechanism exists (calls resolve to something real)"
if [ -f "$HSC" ]; then
  pass "skills/handoff-size-check/SKILL.md exists"
  grep -qE "500k" "$HSC" && pass "handoff-size-check carries the 500k cap" \
                         || fail "handoff-size-check lost the 500k cap"
else
  fail "skills/handoff-size-check/SKILL.md MISSING (calls would dangle)"
fi
if [ -f "$CTXBUDGET" ]; then
  grep -qE "mode_envelopes" "$CTXBUDGET" \
    && pass "context-budget defines mode_envelopes (the cap source)" \
    || fail "context-budget missing mode_envelopes"
  grep -qE "customer-engagement:[[:space:]]*\{[[:space:]]*soft:[[:space:]]*500k" "$CTXBUDGET" \
    && pass "context-budget default cap is 500k soft" \
    || fail "context-budget default 500k soft cap not found"
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
