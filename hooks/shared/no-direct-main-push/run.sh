#!/usr/bin/env bash
# no-direct-main-push — Lintel warn-only hook
# Warns when a Bash command pushes directly to main/master.

set -euo pipefail

CMD="${1:-}"
[ -z "$CMD" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

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
  audit_log "hooks" "no_direct_main_push" "hook=no-direct-main-push" "tier=warn" "pattern=$matched" "cmd_preview=$(echo "$CMD" | head -c 120)"
  echo "WARN [Lintel hook]: $matched to main/master detected"
  echo "WARN: CLAUDE.md requires explicit per-batch authorization for direct main push."
  echo "WARN: Confirm in conversation: 'yes, push this batch to main, I authorize'."
fi

exit 0
