#!/usr/bin/env bash
# cycle-position-inject — Lintel UserPromptSubmit turn-start continuity driver.
# component: cycle-position-inject hook
# implements: ADR-0023 (extends ADR-0022); intent: docs/v4.x/structure-changes; constraints: L-016, L-018
#
# Re-asserts cycle position BEFORE the model responds, on EVERY turn a cycle is active — the
# turn-START surface the continuity trifecta was missing (SessionStart digest = session edge,
# the Stop hook = turn end *after* the footer-less turn, SKILL.md prose = decays after 2-3 phases).
# This keeps the model in the workflow, reminds it to render the footer + give the per-phase report,
# and to advance when a phase completes.
#
# Hard contract:
#   • Fail-open. ALWAYS exit 0. NEVER exit 2 / {"decision":"block"} — on UserPromptSubmit that would
#     DROP the operator's prompt. Every path is guarded.
#   • Silent + near-zero cost when no cycle is active (the common case): a state-file + marker check
#     before any lib is sourced. Reuses render_cycle_footer (the single source of truth) — no 2nd parser.
#   • Read-only. The model owns writing the ledger (gap-A is a nudge, not an auto-write).

set -uo pipefail

_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_root="$(cd "$_dir/../../.." && pwd)"                 # plugin root — for sourcing libs
_repo="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"   # the USER's repo — for state + footer

# State ledger lives in the user's repo (v5 path, legacy fallback).
_sf="$_repo/.claude/runtime/state/00-state.md"
[ -f "$_sf" ] || _sf="$_repo/.lintel/state/00-state.md"

# Read the submitted prompt via the shared adapter (cheap, bounded stdin read).
# shellcheck disable=SC1091
. "$_root/hooks/shared/_input.sh" 2>/dev/null || exit 0
PROMPT="$(hook_input prompt "${1:-}" 2>/dev/null || true)"

# Emit text in the UserPromptSubmit additionalContext envelope, then exit 0.
_emit() {
  local c="$1" esc
  if command -v jq >/dev/null 2>&1; then
    jq -nc --arg c "$c" '{hookSpecificOutput:{hookEventName:"UserPromptSubmit",additionalContext:$c}}'
  else
    # Portable JSON escape (\, ", newline) — mirrors session-digest's no-jq branch.
    esc="$(printf '%s' "$c" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | awk 'BEGIN{ORS="\\n"} {print}' | sed 's/\\n$//')"
    printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"%s"}}\n' "$esc"
  fi
  exit 0
}

# ── 1. Active Lintel cycle? Cheap marker pre-check, then render_cycle_footer decides active-vs-done ──
if [ -f "$_sf" ] && grep -qiE '^[[:space:]]*phase:[[:space:]]*CYCLE' "$_sf" 2>/dev/null; then
  # shellcheck disable=SC1091
  . "$_root/lib/cycle-footer.sh" 2>/dev/null || exit 0
  command -v render_cycle_footer >/dev/null 2>&1 || exit 0
  foot="$(render_cycle_footer --compact 2>/dev/null)" || exit 0
  case "$foot" in
    *"no active cycle"*|*"cycle position unresolved"*) : ;;   # completed/none → fall through
    *)
      command -v audit_log >/dev/null 2>&1 || . "$_root/bin/_audit.sh" 2>/dev/null || true
      command -v audit_log >/dev/null 2>&1 && \
        audit_log "hooks" "cycle_position_inject" "hook=cycle-position-inject" "tier=active" 2>/dev/null || true
      _emit "LINTEL CYCLE ACTIVE — you are mid-cycle; stay in the workflow.
${foot}
This turn: end your reply with the position footer (render_cycle_footer), give the structured per-phase report, and advance to the next phase when this one is done (state_append <PHASE> DONE next=<next>)."
      ;;
  esac
fi

# ── 2. Gap A: a cycle is being invoked but no ledger exists yet → nudge to start it ──
# (the model owns the write so cycle_id/mode/branch/commit are correct — no auto-write).
case "$PROMPT" in
  */li:cycle*|*/li:fix*|*/li:autoplan*|*/li:plan-and-build*)
    if ! { [ -f "$_sf" ] && grep -qiE '^[[:space:]]*phase:[[:space:]]*CYCLE' "$_sf" 2>/dev/null; }; then
      _emit "LINTEL CYCLE ENTRY — and the ledger has no cycle marker yet. Your FIRST mechanical action, before any phase work: state_append CYCLE STARTING cycle_id=<id> cycle_mode=<mode> branch=<branch> commit=<sha> (source lib/state.sh per the cycle skill's mode-persistence step). The position footer, the turn-end Stop hook, and the session digest ALL key off this marker — skip it and the cycle loses the thread."
    fi
    ;;
esac

# ── 3. pack-ready seam (deferred): if no Lintel cycle, probe the ACTIVE pack's continuity provider ──
#   e.g. resolve_pack_field continuity.probe → source the INSTALLED pack's lib (~/.lintel/packs/...,
#   never repo-supplied code) → call its probe → _emit the pack's compact reminder. Left as a seam so
#   wiring /s4l:forge later needs no rework (ADR-0023 §pack-ready).

# ── 4. nothing matched → SILENT, zero-overhead ──
exit 0
