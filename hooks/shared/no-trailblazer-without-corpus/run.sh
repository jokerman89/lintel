#!/usr/bin/env bash
# no-trailblazer-without-corpus — Lintel warn-only hook
set -euo pipefail

PAYLOAD="${1:-}"
[ -z "$PAYLOAD" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"
AUDIT="$LINTEL_HOME/audit/hooks.jsonl"

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
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  printf '{"hook":"no-trailblazer-without-corpus","tier":"warn","ts":"%s"}\n' "$ts" >> "$AUDIT"
  echo "WARN [Lintel hook]: writing trailblazer-voice content while T0 calibration incomplete"
  echo "WARN: Output will carry UNCALIBRATED stamp; downstream /customer-voice-check will refuse."
fi

exit 0
