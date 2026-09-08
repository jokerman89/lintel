#!/usr/bin/env bash
# component: no-customer-data-in-message
# implements: ADR-0013
# intent: docs/compliance.md
# constraints: pattern coverage and host activation limits in docs/compliance.md
# last_intent_review: 2026-09-08
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
# Shared customer-PII patterns (defined once in _patterns.sh).
source "$(dirname "${BASH_SOURCE[0]}")/../_patterns.sh"

if ! joined="$(scan_customer "$PROMPT")"; then
  audit_log "hooks" "no_customer_data_in_message" "hook=no-customer-data-in-message" "tier=warn" "reason=scan-unavailable" || true
  echo "WARN [Lintel hook]: no-customer-data-in-message pattern scan unavailable; prompt was not verified." >&2
  exit 0
fi

if [ -n "$joined" ]; then
  audit_log "hooks" "no_customer_data_in_message" "hook=no-customer-data-in-message" "tier=warn" "patterns_matched=$joined"
  echo "WARN [Lintel hook]: customer-data tell detected in prompt — patterns: $joined"
  echo "WARN: Sanitize before continuing if this is sensitive. (warn-only; not blocking.)"
fi

exit 0
