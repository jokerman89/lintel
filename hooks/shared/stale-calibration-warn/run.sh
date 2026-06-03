#!/usr/bin/env bash
# stale-calibration-warn — Lintel warn-only hook
# Warns when trailblazer operation runs against stale calibration.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

# Find TRAILBLAZER-CALIBRATION.md — repo-local or under known scaffolding path
CALIB=""
for candidate in \
  "./scaffolding/03-personal-advanced/voice/TRAILBLAZER-CALIBRATION.md" \
  "./TRAILBLAZER-CALIBRATION.md" \
  "$HOME/.lintel/voice/TRAILBLAZER-CALIBRATION.md"
do
  if [ -f "$candidate" ]; then
    CALIB="$candidate"
    break
  fi
done

[ -z "$CALIB" ] && exit 0   # No calibration file = different problem, not this hook's job

# Get mtime
if stat -c "%Y" "$CALIB" >/dev/null 2>&1; then
  mtime=$(stat -c "%Y" "$CALIB")
else
  # macOS / BSD stat
  mtime=$(stat -f "%m" "$CALIB" 2>/dev/null || echo 0)
fi
now=$(date +%s)
age_days=$(( (now - mtime) / 86400 ))

if [ "$age_days" -gt 30 ]; then
  audit_log "hooks" "stale_calibration_warn" "hook=stale-calibration-warn" "tier=warn" "calibration_age_days=$age_days"
  echo "WARN [Lintel hook]: TRAILBLAZER-CALIBRATION is $age_days days old (>30 day threshold)"
  echo "WARN: Voice-check verdicts will carry STALE stamp. Re-run /li:eval against corpus to refresh."
fi

exit 0
