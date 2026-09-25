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
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/cycle-continuity.sh"
echo "=============================="

TMP="$(mktemp -d)" && TMP="$(cd "${TMP:?}" && pwd -P)" || exit 1
trap 'rm -rf "$TMP"' EXIT
FIXTURE="$TMP/repo"
mkdir -p "$FIXTURE/.claude/runtime/state"
git -C "$FIXTURE" init -q || exit 1
printf 'layout_version: 5\n' > "$FIXTURE/.claude/lintel-layout.yaml"
export LINTEL_REPO_ROOT="$FIXTURE" LINTEL_SOURCE_ROOT="$REPO_ROOT"
export LINTEL_HOME="$TMP/lintel" LINTEL_PACKS_DIR="$TMP/lintel/packs"
export LINTEL_ACTIVE_PACK_FILE="$TMP/lintel/packs/active-pack"
export LINTEL_AUDIT_DIR="$TMP/audit" LINTEL_JOBS_DIR="$TMP/jobs"
export LINTEL_JOBS_REGISTRY="$TMP/lintel/jobs/_active.md"
unset LINTEL_PROFILE_CONTEXT LINTEL_PROFILE_CONTEXT_FILE LINTEL_PROFILE_REFERENCE LINTEL_PROFILE_PACK
unset LINTEL_STATE_DIR LINTEL_CYCLE_ID LINTEL_WORK_MAP LINTEL_SESSION_ID CLAUDE_SESSION_ID
cd "$FIXTURE" || exit 1
STARTED="$TMP/started.md"; MID="$TMP/mid.md"; DONE="$TMP/done.md"
printf -- '---\nphase: CYCLE\nstatus: STARTING\ncycle_mode: meta-infra\n' > "$STARTED"
printf -- '---\nphase: CYCLE\nstatus: STARTING\ncycle_mode: meta-infra\n---\nphase: BUILD\nstatus: STARTING\nnext_recommended: REVIEW\n' > "$MID"
printf -- '---\nphase: CAPTURE\nstatus: DONE\ncycle_complete: true\n' > "$DONE"

# ── 1. Footer: a just-started cycle renders the stepper, NOT the thin line ──
# shellcheck disable=SC1091
source "$REPO_ROOT/lib/cycle-footer.sh"
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
HK="$REPO_ROOT/hooks/shared/cycle-incomplete-warn/run.sh"
[ -f "$HK" ] && pass "cycle-incomplete-warn hook exists for explicit Bash invocation" || fail "$HK missing"
LIVE="$FIXTURE/.claude/runtime/state/00-state.md"
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
dg="$(bash "$REPO_ROOT/hooks/shared/session-digest/run.sh" 2>/dev/null)"
case "$dg" in *"Current cycle"*"BUILD"*) pass "digest re-injects Current cycle position" ;;
  *) fail "digest missing Current cycle line for active cycle" ;; esac
cp "$DONE" "$LIVE"
dg="$(bash "$REPO_ROOT/hooks/shared/session-digest/run.sh" 2>/dev/null)"
case "$dg" in *"Current cycle"*) fail "digest emits cycle line for a COMPLETED cycle" ;;
  *) pass "digest omits cycle line when cycle is complete" ;; esac

# ── 5. cycle-position-inject (UserPromptSubmit): injects compact position on an active cycle ──
UPS="$REPO_ROOT/hooks/shared/cycle-position-inject/run.sh"
[ -f "$UPS" ] && pass "cycle-position-inject hook exists for explicit Bash invocation" || fail "$UPS missing"
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

for invocation in '/li:cycle --from PLAN --to BUILD' '/li:cycle --from REVIEW --to CAPTURE' '/li-cycle --from SENSE --to DISCOVER'; do
  o="$(bash "$UPS" "$invocation" </dev/null 2>&1)"
  case "$o" in *"CYCLE STARTING"*) pass "range invocation nudges ledger creation: $invocation" ;;
    *) fail "range invocation did not nudge: $invocation: $o" ;; esac
done
for retired in autoplan plan-and-build review-and-ship research; do
  o="$(bash "$UPS" "/li:$retired" </dev/null 2>&1)"
  [ -z "$o" ] && pass "retired shortcut is not a cycle trigger: $retired" ||
    fail "retired shortcut still triggers: $retired"
done
cp "$MID" "$LIVE"
o="$(cd "$REPO_ROOT" && bash "$UPS" continue </dev/null 2>&1)"
case "$o" in *additionalContext*BUILD*) pass "target repository takes precedence over source cwd" ;;
  *) fail "source cwd hid selected target state: $o" ;; esac
o="$(bash "$HK" </dev/null 2>&1)"
case "$o" in *"/li:pause"*) pass "Stop hook emits the canonical pause command" ;;
  *) fail "Stop hook emitted an obsolete checkpoint command: $o" ;; esac

# ── 4. the continuity hooks are registered in hooks.json ──
grep -q "cycle-incomplete-warn" "$REPO_ROOT/hooks/hooks.json" && pass "Stop hook declared in hooks.json" || fail "Stop hook not declared in hooks.json"
grep -q "cycle-position-inject" "$REPO_ROOT/hooks/hooks.json" && pass "UserPromptSubmit hook declared in hooks.json" || fail "cycle-position-inject not declared in hooks.json"

echo ""
[ "$FAILED" -eq 0 ] && { echo "cycle-continuity: ALL PASS"; exit 0; } || { echo "cycle-continuity: FAILURES"; exit 1; }
