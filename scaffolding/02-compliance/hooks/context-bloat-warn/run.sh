#!/usr/bin/env bash
# context-bloat-warn — JStack warn-only hook
# Surfaces token/tool-call threshold warnings.

set -euo pipefail

JSTACK_HOME="${JSTACK_HOME:-$HOME/.jstack}"
SESSION_ID="${JSTACK_SESSION_ID:-default}"
TOKEN_FILE="$JSTACK_HOME/sessions/${SESSION_ID}/tokens.txt"
CALL_FILE="$JSTACK_HOME/sessions/${SESSION_ID}/tool-calls.count"
RATE_FILE="$JSTACK_HOME/sessions/${SESSION_ID}/.last-bloat-warn"

CONFIG="$JSTACK_HOME/config.yaml"

# Defaults
SOFT_TOKEN=50000
HARD_TOKEN=80000
SOFT_CALLS=80
HARD_CALLS=130

# Optional config override (simple grep, no YAML parser needed)
if [ -f "$CONFIG" ]; then
  v=$(grep -E '^[[:space:]]*soft_token:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}')
  [ -n "$v" ] && SOFT_TOKEN="$v"
  v=$(grep -E '^[[:space:]]*hard_token:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}')
  [ -n "$v" ] && HARD_TOKEN="$v"
  v=$(grep -E '^[[:space:]]*soft_tool_calls:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}')
  [ -n "$v" ] && SOFT_CALLS="$v"
  v=$(grep -E '^[[:space:]]*hard_tool_calls:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}')
  [ -n "$v" ] && HARD_CALLS="$v"
fi

tokens=0
calls=0
[ -f "$TOKEN_FILE" ] && tokens=$(cat "$TOKEN_FILE" 2>/dev/null || echo 0)
[ -f "$CALL_FILE" ] && calls=$(cat "$CALL_FILE" 2>/dev/null || echo 0)

# Rate-limit: only fire once per 5 calls to avoid spam
now_call="$calls"
last_warn=0
[ -f "$RATE_FILE" ] && last_warn=$(cat "$RATE_FILE" 2>/dev/null || echo 0)
diff=$(( now_call - last_warn ))
[ "$diff" -lt 5 ] && exit 0

# Decide tier
if [ "$tokens" -ge "$HARD_TOKEN" ] || [ "$calls" -ge "$HARD_CALLS" ]; then
  echo "WARN [JStack context-bloat]: HARD threshold crossed (tokens=$tokens/$HARD_TOKEN, calls=$calls/$HARD_CALLS)"
  echo "WARN: Run /context-save now; resume in fresh session. Quality degrades past this point."
  mkdir -p "$(dirname "$RATE_FILE")"
  echo "$now_call" > "$RATE_FILE"
elif [ "$tokens" -ge "$SOFT_TOKEN" ] || [ "$calls" -ge "$SOFT_CALLS" ]; then
  echo "WARN [JStack context-bloat]: soft threshold crossed (tokens=$tokens/$SOFT_TOKEN, calls=$calls/$SOFT_CALLS)"
  echo "WARN: Consider /context-save at next natural pause."
  mkdir -p "$(dirname "$RATE_FILE")"
  echo "$now_call" > "$RATE_FILE"
fi

exit 0
