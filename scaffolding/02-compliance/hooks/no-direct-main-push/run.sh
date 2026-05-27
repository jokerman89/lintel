#!/usr/bin/env bash
# no-direct-main-push — JStack warn-only hook
# Warns when a Bash command pushes directly to main/master.

set -euo pipefail

CMD="${1:-}"
[ -z "$CMD" ] && exit 0

JSTACK_HOME="${JSTACK_HOME:-$HOME/.jstack}"
mkdir -p "$JSTACK_HOME/audit"
AUDIT="$JSTACK_HOME/audit/hooks.jsonl"

# Detect direct-push patterns
matched=""
if echo "$CMD" | grep -qE 'git\s+push\s+(\S+\s+)?(main|master)(\s|$)'; then
  matched="direct push"
fi
if echo "$CMD" | grep -qE 'git\s+push\s+--force\s+.*\b(main|master)\b'; then
  matched="force push"
fi
if echo "$CMD" | grep -qE 'git\s+push\s+\S+\s+HEAD:(main|master)'; then
  matched="HEAD: alias push"
fi

if [ -n "$matched" ]; then
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  printf '{"hook":"no-direct-main-push","tier":"warn","ts":"%s","pattern":"%s","cmd_preview":"%s"}\n' \
    "$ts" "$matched" "$(echo "$CMD" | head -c 120)" >> "$AUDIT"
  echo "WARN [JStack hook]: $matched to main/master detected"
  echo "WARN: CLAUDE.md requires explicit per-batch authorization for direct main push."
  echo "WARN: Confirm in conversation: 'yes, push this batch to main, I authorize'."
fi

exit 0
