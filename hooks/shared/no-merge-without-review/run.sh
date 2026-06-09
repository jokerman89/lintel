#!/usr/bin/env bash
# no-merge-without-review — Lintel warn-only hook
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
CMD="$(hook_input command "${1:-}")"
[ -z "$CMD" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

# Detect merge-to-main patterns
if echo "$CMD" | grep -qE '(gh\s+pr\s+merge|git\s+merge.*main|git\s+merge.*master)'; then
  # The review log is written by bin/li-review-log via the unified audit helper to
  # ~/.lintel/audit/reviews.jsonl (NOT the legacy ~/.lintel/review-log/entries.jsonl path,
  # which nothing writes). And li-review-log resolves commits to the SHORT HEAD, so we
  # match on the short commit (a prefix that substring-matches whether the record stored
  # the short or full sha). Both were silent mismatches that left this gate effectively dead.
  REVIEW_LOG="$LINTEL_HOME/audit/reviews.jsonl"
  recent_review=0
  if [ -f "$REVIEW_LOG" ]; then
    head_commit=$(git rev-parse --short HEAD 2>/dev/null || echo "")
    seven_days_ago=$(date -u -d '7 days ago' +"%Y-%m-%d" 2>/dev/null || date -u -v-7d +"%Y-%m-%d" 2>/dev/null || echo "")
    if [ -n "$head_commit" ] && [ -n "$seven_days_ago" ]; then
      if grep "$head_commit" "$REVIEW_LOG" 2>/dev/null | grep -qE "\"status\":\"CLEARED\""; then
        recent_review=1
      fi
    fi
  fi

  if [ "$recent_review" = "0" ]; then
    audit_log "hooks" "no_merge_without_review" "hook=no-merge-without-review" "tier=warn" "cmd_preview=$(echo "$CMD" | head -c 120)"
    echo "WARN [Lintel hook]: merge to main detected without recent /review or /plan-eng-review CLEARED for HEAD"
    echo "WARN: Run /review or /plan-eng-review first, or confirm intentional bypass."
  fi
fi

exit 0
