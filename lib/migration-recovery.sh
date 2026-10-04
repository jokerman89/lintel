#!/usr/bin/env bash
# component: migration-recovery-eligibility
# implements: ADR-0034
# intent: .claude/plans/v2-findings/plan.md
# constraints: predicate over reviewed evidence only; never performs recovery
# last_intent_review: 2026-10-03
# lintel-migration-recovery-gate
migration_recovery_allowed() {
  local approved_state="${1:-}" observed_state="${2:-}"
  local verification="${3:-}" authorization="${4:-}" side_effects="${5:-}"
  [ -n "$approved_state" ] && [ "$approved_state" = "$observed_state" ] &&
    [ "$verification" = verified ] && [ "$authorization" = exact-scope ] &&
    [ "$side_effects" = none ]
}

# Source for the predicate, or invoke with Bash for its exit status. Neither path
# changes shell options, cwd, files or Git state, and success never means "restored".
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  migration_recovery_allowed "$@"
fi
