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

DOM="$ARTIFACT_DIR/dom.html"
[ ! -f "$DOM" ] && exit 0

patterns_hit=()

# Reuse customer-data patterns
grep -qE '\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b' "$DOM" 2>/dev/null && patterns_hit+=("email")
grep -qE '\+?[0-9]{1,3}[ -]?\(?[0-9]{2,4}\)?[ -]?[0-9]{3,4}[ -]?[0-9]{3,4}' "$DOM" 2>/dev/null && patterns_hit+=("phone")
grep -qE '\b[0-9]{6}[-+][0-9]{4}\b' "$DOM" 2>/dev/null && patterns_hit+=("personnummer")

if [ ${#patterns_hit[@]} -gt 0 ]; then
  joined=$(IFS=,; echo "${patterns_hit[*]}")
  audit_log "hooks" "no_customer_data_in_screenshot" "hook=no-customer-data-in-screenshot" "tier=warn" "artifact_dir=$ARTIFACT_DIR" "patterns_matched=$joined"
  echo "WARN [Lintel hook]: screenshot DOM at $ARTIFACT_DIR contains customer-data tells ($joined)"
  echo "WARN: Quarantine the artifact before sharing. Consider mv to ~/.lintel/quarantine/"
fi

exit 0
