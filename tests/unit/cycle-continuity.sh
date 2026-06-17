#!/usr/bin/env bash
# tests/unit/cycle-continuity.sh
# Behavior: the cycle never silently loses the thread. Three mechanical backstops
# (setup-hardening 2026-06-14): (1) the footer renders the stepper for a just-STARTED
# cycle instead of falling to thin; (2) the cycle-incomplete-warn Stop hook surfaces the
# footer at turn end ONLY when a cycle is open mid-flight; (3) session-digest re-injects
# the current-cycle position. Positive AND negative assertions per L-012.
# tag: cycle footer continuity stop-hook digest
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/cycle-continuity.sh"
echo "=============================="

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
STARTED="$TMP/started.md"; MID="$TMP/mid.md"; DONE="$TMP/done.md"
printf -- '---\nphase: CYCLE\nstatus: STARTING\ncycle_mode: meta-infra\n' > "$STARTED"
printf -- '---\nphase: CYCLE\nstatus: STARTING\ncycle_mode: meta-infra\n---\nphase: BUILD\nstatus: STARTING\nnext_recommended: REVIEW\n' > "$MID"
printf -- '---\nphase: CAPTURE\nstatus: DONE\ncycle_complete: true\n' > "$DONE"

# ── 1. Footer: a just-started cycle renders the stepper, NOT the thin line ──
# shellcheck disable=SC1091
source lib/cycle-footer.sh
out="$(render_cycle_footer --state "$STARTED")"
case "$out" in
  *"no active cycle"*) fail "started cycle still falls to thin 'no active cycle' (the bug)" ;;
  *"SENSE 📍"*|*"SENSE [>]"*) pass "started cycle renders the stepper with SENSE as here" ;;
  *) fail "started cycle rendered unexpected output: $out" ;;
esac
out="$(render_cycle_footer --state "$DONE")"
case "$out" in *"no active cycle"*) pass "completed cycle still falls to thin (no false stepper)" ;;
  *) fail "completed cycle should be thin, got: $out" ;; esac

# ── 2. Stop hook: warns on active mid-cycle, silent otherwise ──
HK="hooks/shared/cycle-incomplete-warn/run.sh"
[ -x "$HK" ] && pass "cycle-incomplete-warn hook is executable" || fail "$HK missing or not executable"
mkdir -p .claude/runtime/state
# preserve any real live state, restore after
LIVE=".claude/runtime/state/00-state.md"; BAK=""
[ -f "$LIVE" ] && { BAK="$TMP/live.bak"; cp "$LIVE" "$BAK"; }
cp "$MID" "$LIVE"
o="$(bash "$HK" 2>&1)"; rc=$?
[ $rc -eq 0 ] && pass "Stop hook exits 0 (warn-only, never blocks)" || fail "Stop hook exit $rc — must be 0"
case "$o" in *"open cycle"*|*"You are here"*) pass "Stop hook surfaces the footer on active mid-cycle" ;;
  *) fail "Stop hook silent on active cycle (should warn): $o" ;; esac
cp "$DONE" "$LIVE"
o="$(bash "$HK" 2>&1)"
[ -z "$o" ] && pass "Stop hook SILENT on completed cycle" || fail "Stop hook noisy on completed cycle: $o"
rm -f "$LIVE"
o="$(bash "$HK" 2>&1)"
[ -z "$o" ] && pass "Stop hook SILENT when no cycle state exists" || fail "Stop hook noisy with no state: $o"

# ── 3. session-digest re-injects the cycle position ──
cp "$MID" "$LIVE"
dg="$(bash hooks/shared/session-digest/run.sh 2>/dev/null)"
case "$dg" in *"Current cycle"*"BUILD"*) pass "digest re-injects Current cycle position" ;;
  *) fail "digest missing Current cycle line for active cycle" ;; esac
cp "$DONE" "$LIVE"
dg="$(bash hooks/shared/session-digest/run.sh 2>/dev/null)"
case "$dg" in *"Current cycle"*) fail "digest emits cycle line for a COMPLETED cycle" ;;
  *) pass "digest omits cycle line when cycle is complete" ;; esac

# ── 5. cycle-position-inject (UserPromptSubmit): injects compact position on an active cycle ──
UPS="hooks/shared/cycle-position-inject/run.sh"
[ -x "$UPS" ] && pass "cycle-position-inject hook is executable" || fail "$UPS missing or not executable"
cp "$MID" "$LIVE"
o="$(printf '{"prompt":"continue"}' | bash "$UPS" 2>&1)"; rc=$?
[ $rc -eq 0 ] && pass "UPS hook exits 0 (never blocks the prompt)" || fail "UPS hook exit $rc — must be 0"
case "$o" in *additionalContext*BUILD*) pass "UPS hook injects compact position on active cycle" ;;
  *) fail "UPS hook did not inject position on active cycle: $o" ;; esac
case "$o" in *'"decision":"block"'*|*'"decision": "block"'*) fail "UPS hook must NEVER block the prompt" ;;
  *) pass "UPS hook never emits decision:block" ;; esac

# ── 6. UPS hook: SILENT (empty stdout) when no cycle is active (zero-overhead path) ──
cp "$DONE" "$LIVE"
o="$(printf '{"prompt":"just chatting"}' | bash "$UPS" 2>/dev/null)"; rc=$?
{ [ -z "$o" ] && [ $rc -eq 0 ]; } && pass "UPS hook silent on completed cycle" || fail "UPS hook not silent on completed cycle: $o"
rm -f "$LIVE"
o="$(printf '{"prompt":"just chatting"}' | bash "$UPS" 2>/dev/null)"
[ -z "$o" ] && pass "UPS hook silent when no cycle state exists" || fail "UPS hook noisy with no state: $o"

# ── 7. gap-A: a cycle is invoked but no ledger exists → nudge to write CYCLE STARTING ──
o="$(printf '{"prompt":"/li:cycle build the thing"}' | bash "$UPS" 2>&1)"; rc=$?
[ $rc -eq 0 ] && pass "UPS nudge exits 0" || fail "UPS nudge exit $rc"
case "$o" in *"CYCLE STARTING"*) pass "UPS nudges to write CYCLE STARTING on cycle-invocation with no ledger" ;;
  *) fail "UPS did not nudge on cycle invocation: $o" ;; esac

# restore live state
rm -f "$LIVE"; [ -n "$BAK" ] && cp "$BAK" "$LIVE"

# ── 4. the continuity hooks are registered in hooks.json ──
grep -q "cycle-incomplete-warn" hooks/hooks.json && pass "Stop hook registered in hooks.json" || fail "Stop hook not registered in hooks.json"
grep -q "cycle-position-inject" hooks/hooks.json && pass "UserPromptSubmit hook registered in hooks.json" || fail "cycle-position-inject not registered in hooks.json"

echo ""
[ "$FAILED" -eq 0 ] && { echo "cycle-continuity: ALL PASS"; exit 0; } || { echo "cycle-continuity: FAILURES"; exit 1; }
