#!/usr/bin/env bash
# tests/unit/orientator-mechanical-routing.sh
# Asserts: lib/orientator-routing.sh produces correct mechanical routing
# for documented prompts.
# tag: v4.0 phase-3 orientator

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ROUTING="$REPO_ROOT/lib/orientator-routing.sh"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/orientator-mechanical-routing.sh"
echo "============================================="

if [ ! -f "$ROUTING" ]; then
  fail "lib/orientator-routing.sh MISSING"
  exit 1
fi

# shellcheck disable=SC1090
source "$ROUTING"

# ─── Scenario 1: 'fix the broken button' → fix → hotfix ─────────────────
echo ""
echo "[1] 'fix the broken button' → fix → hotfix"
intent=$(classify_intent "fix the broken button")
workflow=$(match_workflow "$intent" "cycle")
[ "$intent" = "fix" ] && pass "intent=fix" || fail "intent=$intent (expected fix)"
[ "$workflow" = "/li:cycle --mode hotfix" ] && pass "workflow=hotfix" || fail "workflow=$workflow"

# ─── Scenario 2: 'build a new feature' → build → cycle ──────────────────
echo ""
echo "[2] 'build a new feature' → build → cycle"
intent=$(classify_intent "build a new feature")
workflow=$(match_workflow "$intent" "cycle")
[ "$intent" = "build" ] && pass "intent=build" || fail "intent=$intent (expected build)"
[ "$workflow" = "/li:cycle" ] && pass "workflow=cycle" || fail "workflow=$workflow"

# ─── Scenario 3: 'what should I do?' → unclear → default ───────────────
echo ""
echo "[3] 'what should I do?' → unclear → pack default"
intent=$(classify_intent "what should I do?")
workflow=$(match_workflow "$intent" "cycle")
confidence=$(score_confidence "$intent" "$workflow")
[ "$intent" = "unclear" ] && pass "intent=unclear" || fail "intent=$intent (expected unclear)"
[ "$workflow" = "/li:cycle" ] && pass "workflow=cycle (pack default)" || fail "workflow=$workflow"
[ "$confidence" = "low" ] && pass "confidence=low" || fail "confidence=$confidence"

# ─── Scenario 4: Swedish 'fixa felet' → fix ─────────────────────────────
echo ""
echo "[4] Swedish 'fixa felet i knappen' → fix"
intent=$(classify_intent "fixa felet i knappen")
[ "$intent" = "fix" ] && pass "Swedish intent=fix" || fail "intent=$intent (expected fix)"

# ─── Scenario 5: 'review my PR' → review ────────────────────────────────
echo ""
echo "[5] 'review my PR' → review → /li:review"
intent=$(classify_intent "review my PR")
workflow=$(match_workflow "$intent" "cycle")
[ "$intent" = "review" ] && pass "intent=review" || fail "intent=$intent (expected review)"
[ "$workflow" = "/li:review" ] && pass "workflow=review" || fail "workflow=$workflow"

# ─── Scenario 6: risk assessment ────────────────────────────────────────
echo ""
echo "[6] risk assessment"
risk=$(assess_risk "/li:cycle --mode hotfix" "cycle,plan,ship")
[ "$risk" = "high" ] && pass "hotfix on cycle-in-high-risk → high (cycle base matches)" || fail "risk=$risk (expected high)"

risk=$(assess_risk "/li:cycle --mode research-dive" "ship,plan")
[ "$risk" = "low" ] && pass "research-dive → low (read-only)" || fail "risk=$risk (expected low)"

risk=$(assess_risk "/li:review" "cycle,plan,ship")
[ "$risk" = "medium" ] && pass "review not in high-risk csv → medium (default)" || fail "risk=$risk (expected medium)"

# ─── Scenario 7: escalation threshold ───────────────────────────────────
echo ""
echo "[7] escalation threshold"
should=$(check_escalation_threshold "low" "medium")
[ "$should" = "yes" ] && pass "low confidence vs medium threshold → escalate" || fail "got $should"

should=$(check_escalation_threshold "high" "medium")
[ "$should" = "no" ] && pass "high confidence vs medium threshold → no escalation" || fail "got $should"

should=$(check_escalation_threshold "low" "never")
[ "$should" = "no" ] && pass "threshold=never → never escalate" || fail "got $should"

# ─── Scenario 8: deploy is a distinct intent (D3), ship unchanged ────────
# Regression: classify_intent used to collapse deploy → ship, leaving the
# scope/SKILL.md route-override `deploy` arm dead. Deploy is now its own intent
# so the SCOPE greenfield override (deploy a website to azure → build) is live.
echo ""
echo "[8] deploy/ship intent split (D3 regression)"
intent=$(classify_intent "deploy a website to azure")
[ "$intent" = "deploy" ] && pass "'deploy a website to azure' → deploy" || fail "intent=$intent (expected deploy)"
intent=$(classify_intent "deploy to production")
[ "$intent" = "deploy" ] && pass "'deploy to production' → deploy" || fail "intent=$intent (expected deploy)"
intent=$(classify_intent "ship it")
[ "$intent" = "ship" ] && pass "'ship it' → ship (unchanged)" || fail "intent=$intent (expected ship)"
intent=$(classify_intent "release v2")
[ "$intent" = "ship" ] && pass "'release v2' → ship (release stays ship)" || fail "intent=$intent (expected ship)"
workflow=$(match_workflow "deploy" "cycle")
[ "$workflow" = "/li:cycle --from SHIP" ] && pass "deploy → /li:cycle --from SHIP" || fail "workflow=$workflow"
confidence=$(score_confidence "deploy" "/li:cycle --from SHIP")
[ "$confidence" = "high" ] && pass "deploy confidence=high" || fail "confidence=$confidence"
intent=$(classify_intent "driftsätt till produktion")
[ "$intent" = "deploy" ] && pass "Swedish 'driftsätt' → deploy (bilingual input preserved)" || fail "intent=$intent (expected deploy)"

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All orientator-mechanical-routing scenarios PASSED"; exit 0
else echo "Some orientator-mechanical-routing scenarios FAILED"; exit 1; fi
