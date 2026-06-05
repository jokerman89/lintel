#!/usr/bin/env bash
# customer-data-block — Lintel JUSTIFIED-BLOCK hook
# Blocks git commit/push if Tier 1 customer-data pattern in staged content.

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
CMD="$(hook_input command "${1:-}")"
[ -z "$CMD" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

if ! echo "$CMD" | grep -qE '^git\s+(commit|push)\b'; then
  exit 0
fi

# Override path
if [ "${LINTEL_OVERRIDE_CUSTOMER_DATA:-}" = "1" ]; then
  reason="${LINTEL_OVERRIDE_REASON:-no-reason-given}"
  audit_log "hooks" "customer_data_block" "hook=customer-data-block" "tier=OVERRIDDEN" "override=true" "reason=$reason" "blocked=false"
  echo "INFO [Lintel hook]: customer-data-block OVERRIDDEN (reason: $reason). Audit-logged."
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
  joined=$(IFS=,; echo "${patterns_hit[*]}")
  audit_log "hooks" "customer_data_block" "hook=customer-data-block" "tier=BLOCK" "patterns_matched=$joined" "blocked=true"
  echo "ERROR [Lintel hook]: customer-data pattern in staged content — $joined" >&2
  echo "ERROR: COMMIT BLOCKED. Sanitize the staged content (placeholders) + re-stage." >&2
  echo "ERROR: To override (e.g. confirmed placeholder, public-domain example):" >&2
  echo '  LINTEL_OVERRIDE_CUSTOMER_DATA=1 LINTEL_OVERRIDE_REASON="<reason>" git commit ...' >&2
  exit 1
fi

exit 0
