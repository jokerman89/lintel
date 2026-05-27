#!/usr/bin/env bash
# stale-calibration-warn — JStack warn-only hook
# Warns when trailblazer operation runs against stale calibration.

set -euo pipefail

JSTACK_HOME="${JSTACK_HOME:-$HOME/.jstack}"
mkdir -p "$JSTACK_HOME/audit"
AUDIT="$JSTACK_HOME/audit/hooks.jsonl"

# Find TRAILBLAZER-CALIBRATION.md — repo-local or under known scaffolding path
CALIB=""
for candidate in \
  "./scaffolding/03-personal-advanced/voice/TRAILBLAZER-CALIBRATION.md" \
  "./TRAILBLAZER-CALIBRATION.md" \
  "$HOME/.jstack/voice/TRAILBLAZER-CALIBRATION.md"
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
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  printf '{"hook":"stale-calibration-warn","tier":"warn","ts":"%s","calibration_age_days":%d}\n' \
    "$ts" "$age_days" >> "$AUDIT"
  echo "WARN [JStack hook]: TRAILBLAZER-CALIBRATION is $age_days days old (>30 day threshold)"
  echo "WARN: Voice-check verdicts will carry STALE stamp. Re-run /jstack-eval against corpus to refresh."
fi

exit 0
