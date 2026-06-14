#!/usr/bin/env bash
# cycle-incomplete-warn — Lintel warn-only Stop hook (ADR-0003 follow-up, setup-hardening 2026-06-14)
# Fires at turn end. If an active cycle is open mid-flight (a phase started but the
# cycle is not complete), it surfaces the position footer so the session can NEVER
# silently end mid-cycle "as if it forgot it was in something". This is the mechanical
# backstop for the footer convention, which until now was 100% model-discipline (the
# root cause behind L-008 / L-016 / the recurring "no footer, total silence" symptom).
#
# Warn-only by design: stdout + exit 0, NEVER decision:block / exit 2 — a blocking Stop
# hook forces continuation and can re-trigger itself (infinite loop). This surfaces the
# canary to the operator; it does not coerce the model.

set -uo pipefail

# Fail-open: any error here must never break turn-end. Resolve plugin root for lib/.
_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_root="$(cd "$_dir/../../.." && pwd)"

# Source the footer (pulls in state.sh + cycle-modes.sh). If unavailable, stay silent.
# shellcheck disable=SC1091
. "$_root/lib/cycle-footer.sh" 2>/dev/null || exit 0
command -v render_cycle_footer >/dev/null 2>&1 || exit 0

# render_cycle_footer is the SINGLE source of truth for "is a cycle active": its auto
# tier returns the thin "no active cycle" line when there is no open cycle (none, or
# cycle_complete:true), and the full position block when a cycle is genuinely mid-flight.
foot="$(render_cycle_footer 2>/dev/null)" || exit 0
case "$foot" in
  *"no active cycle"*|*"cycle position unresolved"*) exit 0 ;;  # not mid-cycle → silent
esac

# Active, incomplete cycle at turn end → surface it.
command -v audit_log >/dev/null 2>&1 || . "$_root/bin/_audit.sh" 2>/dev/null || true
phase="$(state_last phase 2>/dev/null || echo '?')"
command -v audit_log >/dev/null 2>&1 && \
  audit_log "hooks" "cycle_incomplete_warn" "hook=cycle-incomplete-warn" "tier=warn" "phase=$phase" 2>/dev/null || true

echo "WARN [Lintel]: this turn is ending with an open cycle — don't lose the thread."
printf '%s\n' "$foot"
echo "WARN: say 'go' to continue · 'pause' to checkpoint (/li:context-save) · or close it with /li:capture."

exit 0
