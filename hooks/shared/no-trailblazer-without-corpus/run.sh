#!/usr/bin/env bash
# no-trailblazer-without-corpus — Lintel warn-only hook
set -euo pipefail

PAYLOAD="${1:-}"
[ -z "$PAYLOAD" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

# Trailblazer-tagged content?
if ! echo "$PAYLOAD" | grep -qE '^voice:\s*trailblazer(-draft)?'; then
  exit 0
fi

# Check calibration state
CALIB=""
for candidate in \
  "./scaffolding/03-personal-advanced/voice/TRAILBLAZER-CALIBRATION.md" \
  "./TRAILBLAZER-CALIBRATION.md"
do
  [ -f "$candidate" ] && CALIB="$candidate" && break
done

calibrated=0
if [ -n "$CALIB" ]; then
  if grep -qE 'status:\s*CALIBRATED' "$CALIB" 2>/dev/null; then
    calibrated=1
  fi
fi

if [ "$calibrated" = "0" ]; then
  # Unified writer → ~/.lintel/audit/hooks.jsonl
  audit_log "hooks" "no_trailblazer_without_corpus" "tier=warn"
  echo "WARN [Lintel hook]: writing trailblazer-voice content while T0 calibration incomplete"
  echo "WARN: Output will carry UNCALIBRATED stamp; downstream /customer-voice-check will refuse."
fi

exit 0
