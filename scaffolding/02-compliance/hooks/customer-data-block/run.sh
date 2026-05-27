#!/usr/bin/env bash
# customer-data-block — JStack JUSTIFIED-BLOCK hook
# Blocks git commit/push if Tier 1 customer-data pattern in staged content.

set -euo pipefail

CMD="${1:-}"
[ -z "$CMD" ] && exit 0

JSTACK_HOME="${JSTACK_HOME:-$HOME/.jstack}"
mkdir -p "$JSTACK_HOME/audit"
AUDIT="$JSTACK_HOME/audit/hooks.jsonl"

if ! echo "$CMD" | grep -qE '^git\s+(commit|push)\b'; then
  exit 0
fi

# Override path
if [ "${JSTACK_OVERRIDE_CUSTOMER_DATA:-}" = "1" ]; then
  reason="${JSTACK_OVERRIDE_REASON:-no-reason-given}"
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  printf '{"hook":"customer-data-block","tier":"OVERRIDDEN","ts":"%s","reason":"%s","blocked":false}\n' \
    "$ts" "$reason" >> "$AUDIT"
  echo "INFO [JStack hook]: customer-data-block OVERRIDDEN (reason: $reason). Audit-logged."
  exit 0
fi

STAGED="$(git diff --cached 2>/dev/null || true)"
[ -z "$STAGED" ] && exit 0

patterns_hit=()
echo "$STAGED" | grep -qE '\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b' && patterns_hit+=("email")
echo "$STAGED" | grep -qE '\+?[0-9]{1,3}[ -]?\(?[0-9]{2,4}\)?[ -]?[0-9]{3,4}[ -]?[0-9]{3,4}' && patterns_hit+=("phone")
echo "$STAGED" | grep -qE '\b[0-9]{6}[-+][0-9]{4}\b' && patterns_hit+=("personnummer")
echo "$STAGED" | grep -qE '\b[A-ZÅÄÖ][a-zåäö]+ [A-ZÅÄÖ][a-zåäö]+,?\s+(case|kase|ärende)\s*#?[0-9]+' && patterns_hit+=("name-with-case-id")

if [ ${#patterns_hit[@]} -gt 0 ]; then
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  joined=$(IFS=,; echo "${patterns_hit[*]}")
  printf '{"hook":"customer-data-block","tier":"BLOCK","ts":"%s","patterns_matched":"%s","blocked":true}\n' \
    "$ts" "$joined" >> "$AUDIT"
  echo "ERROR [JStack hook]: customer-data pattern in staged content — $joined" >&2
  echo "ERROR: COMMIT BLOCKED. Sanitize the staged content (placeholders) + re-stage." >&2
  echo "ERROR: To override (e.g. confirmed placeholder, public-domain example):" >&2
  echo '  JSTACK_OVERRIDE_CUSTOMER_DATA=1 JSTACK_OVERRIDE_REASON="<reason>" git commit ...' >&2
  exit 1
fi

exit 0
