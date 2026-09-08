#!/usr/bin/env bash
# component: no-secrets-in-edit
# implements: ADR-0013
# intent: docs/compliance.md
# constraints: pattern coverage and host activation limits in docs/compliance.md
# last_intent_review: 2026-09-08
# no-secrets-in-edit — Lintel warn-only hook
# Scans Edit/Write tool payload for secret patterns.

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
PAYLOAD="$(hook_input payload "${1:-}")"
[ -z "$PAYLOAD" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"
# Shared detection patterns (defined once). Warn hook → broad `all` tier (includes heuristics).
source "$(dirname "${BASH_SOURCE[0]}")/../_patterns.sh"

if ! joined="$(scan_secrets all "$PAYLOAD")"; then
  audit_log "hooks" "no_secrets_in_edit" "hook=no-secrets-in-edit" "tier=warn" "reason=scan-unavailable" || true
  echo "WARN [Lintel hook]: no-secrets-in-edit pattern scan unavailable; payload was not verified." >&2
  exit 0
fi

if [ -n "$joined" ]; then
  audit_log "hooks" "no_secrets_in_edit" "hook=no-secrets-in-edit" "tier=warn" "patterns_matched=$joined"
  echo "WARN [Lintel hook]: secret pattern detected in payload — $joined"
  echo "WARN: If this is a real secret, abort + use env var or secret manager. (warn-only; secret-scan-block fires at commit.)"
fi

exit 0
