#!/usr/bin/env bash
# no-merge-without-review — JStack warn-only hook
set -euo pipefail

CMD="${1:-}"
[ -z "$CMD" ] && exit 0

JSTACK_HOME="${JSTACK_HOME:-$HOME/.jstack}"
mkdir -p "$JSTACK_HOME/audit"
AUDIT="$JSTACK_HOME/audit/hooks.jsonl"

# Detect merge-to-main patterns
if echo "$CMD" | grep -qE '(gh\s+pr\s+merge|git\s+merge.*main|git\s+merge.*master)'; then
  REVIEW_LOG="$JSTACK_HOME/review-log/entries.jsonl"
  recent_review=0
  if [ -f "$REVIEW_LOG" ]; then
    head_commit=$(git rev-parse HEAD 2>/dev/null || echo "")
    seven_days_ago=$(date -u -d '7 days ago' +"%Y-%m-%d" 2>/dev/null || date -u -v-7d +"%Y-%m-%d" 2>/dev/null || echo "")
    if [ -n "$head_commit" ] && [ -n "$seven_days_ago" ]; then
      if grep "$head_commit" "$REVIEW_LOG" 2>/dev/null | grep -qE "\"status\":\"CLEARED\""; then
        recent_review=1
      fi
    fi
  fi

  if [ "$recent_review" = "0" ]; then
    ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    printf '{"hook":"no-merge-without-review","tier":"warn","ts":"%s","cmd_preview":"%s"}\n' \
      "$ts" "$(echo "$CMD" | head -c 120)" >> "$AUDIT"
    echo "WARN [JStack hook]: merge to main detected without recent /review or /plan-eng-review CLEARED for HEAD"
    echo "WARN: Run /review or /plan-eng-review first, or confirm intentional bypass."
  fi
fi

exit 0
