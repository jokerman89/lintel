#!/usr/bin/env bash
# component: no-merge-without-review
# implements: ADR-0028
# intent: skills/review/references/evidence.md
# constraints: advisory and opt-in; does not authorize or block a merge
# last_intent_review: 2026-09-20
set -uo pipefail
SOURCE_ROOT="${LINTEL_SOURCE_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
source "$SOURCE_ROOT/hooks/shared/_input.sh"
CMD="$(hook_input command "${1:-}")"
[ -z "$CMD" ] && exit 0
if ! printf '%s\n' "$CMD" | grep -qE '(gh[[:space:]]+pr[[:space:]]+merge|git[[:space:]]+merge.*(main|master))'; then
  exit 0
fi

options=(--skill "${LINTEL_REVIEW_SKILL:-review}" --gate-json)
if [ -n "${LINTEL_REVIEW_CONTEXT:-}" ]; then
  options+=(--expected "$LINTEL_REVIEW_CONTEXT")
fi
if [ -n "${LINTEL_REVIEW_CORROBORATION:-}" ]; then
  options+=(--corroboration "$LINTEL_REVIEW_CORROBORATION")
fi
if bash "$SOURCE_ROOT/bin/li-review-read" "${options[@]}" >/dev/null 2>&1; then
  exit 0
fi
source "$SOURCE_ROOT/bin/_audit.sh"
audit_log hooks no_merge_without_review "hook=no-merge-without-review" "tier=warn" \
  "reason=missing-or-invalid-content-bound-review"
echo 'WARN [Lintel hook]: merge detected without a current content-bound review decision.'
echo 'WARN: Supply the selected review context and actual corroboration; inspect li-review-read diagnostics.'
echo 'WARN: This opt-in hook is advisory, not merge authorization or enforcement.'
exit 0
