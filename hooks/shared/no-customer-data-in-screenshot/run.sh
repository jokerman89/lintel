#!/usr/bin/env bash
# no-customer-data-in-screenshot — Lintel warn-only hook
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
ARTIFACT_DIR="$(hook_input file_path "${1:-}")"
[ -z "$ARTIFACT_DIR" ] && exit 0
[ ! -d "$ARTIFACT_DIR" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"
# Shared customer-PII patterns (defined once). Using the shared set also gives the
# DOM scan the name-with-case-id pattern the other two customer hooks already had.
source "$(dirname "${BASH_SOURCE[0]}")/../_patterns.sh"

DOM="$ARTIFACT_DIR/dom.html"
[ ! -f "$DOM" ] && exit 0

joined="$(scan_customer "$(cat "$DOM" 2>/dev/null || true)")"

if [ -n "$joined" ]; then
  audit_log "hooks" "no_customer_data_in_screenshot" "hook=no-customer-data-in-screenshot" "tier=warn" "artifact_dir=$ARTIFACT_DIR" "patterns_matched=$joined"
  echo "WARN [Lintel hook]: screenshot DOM at $ARTIFACT_DIR contains customer-data tells ($joined)"
  echo "WARN: Quarantine the artifact before sharing. Consider mv to ~/.lintel/quarantine/"
fi

exit 0
