#!/usr/bin/env bash
# no-customer-data-in-message — Lintel warn-only hook
# Scans operator prompt for customer-data tells.
# Reads prompt content from $1 (Claude Code passes prompt as first arg).

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
PROMPT="$(hook_input prompt "${1:-}")"
[ -z "$PROMPT" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

patterns_hit=()

# Email
if echo "$PROMPT" | grep -qE '\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'; then
  patterns_hit+=("email")
fi

# Phone (intl + Swedish formats)
if echo "$PROMPT" | grep -qE '\+?[0-9]{1,3}[ -]?\(?[0-9]{2,4}\)?[ -]?[0-9]{3,4}[ -]?[0-9]{3,4}'; then
  patterns_hit+=("phone")
fi

# Swedish personnummer
if echo "$PROMPT" | grep -qE '\b[0-9]{6}[-+][0-9]{4}\b'; then
  patterns_hit+=("personnummer")
fi

# Case identifier with name pattern (heuristic)
if echo "$PROMPT" | grep -qE '\b[A-ZÅÄÖ][a-zåäö]+ [A-ZÅÄÖ][a-zåäö]+,?\s+(case|kase|case-id|ärende)\s*#?[0-9]+'; then
  patterns_hit+=("name-with-case-id")
fi

if [ ${#patterns_hit[@]} -gt 0 ]; then
  joined=$(IFS=,; echo "${patterns_hit[*]}")
  audit_log "hooks" "no_customer_data_in_message" "hook=no-customer-data-in-message" "tier=warn" "patterns_matched=$joined"
  echo "WARN [Lintel hook]: customer-data tell detected in prompt — patterns: $joined"
  echo "WARN: Sanitize before continuing if this is sensitive. (warn-only; not blocking.)"
fi

exit 0
