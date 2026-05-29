#!/usr/bin/env bash
# job-stale-warn — Lintel surface-only hook (v3.8 Feature 1)
# Surfaces jobs untouched > N hours at session-start.

set -uo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../bin" 2>/dev/null && pwd)" || \
BIN_DIR="${LINTEL_HOME}/scaffolding/bin"
AUDIT="$LINTEL_HOME/audit/jobs.jsonl"

mkdir -p "$LINTEL_HOME/audit" 2>/dev/null || true

# Operator override
[ -f "$HOME/.lintel/.jobs-stale-warn-disabled" ] && exit 0
[ -n "${NO_STALE_WARN:-}" ] && exit 0

# Threshold
hours="${LINTEL_JOBS_STALE_HOURS:-24}"
PROFILE="$HOME/.lintel/profile.yaml"
if [ -f "$PROFILE" ]; then
  pv=$(grep '^jobs_stale_threshold_hours:' "$PROFILE" 2>/dev/null | awk '{print $2}')
  [ -n "$pv" ] && hours="$pv"
fi

helper="$BIN_DIR/_jobs.sh"
[ -f "$helper" ] || {
  for candidate in \
    "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../bin" 2>/dev/null && pwd)/_jobs.sh" \
    "$LINTEL_HOME/scaffolding/bin/_jobs.sh"; do
    [ -f "$candidate" ] && { helper="$candidate"; break; }
  done
}
[ -f "$helper" ] || exit 0

# shellcheck disable=SC1090
source "$helper"

# Get stale jobs
mapfile -t stale_lines < <(stale_jobs "$hours" 2>/dev/null || true)

if [ "${#stale_lines[@]}" -gt 0 ]; then
  echo "[lintel] ${#stale_lines[@]} job(s) untouched >${hours}h:"
  for line in "${stale_lines[@]}"; do
    job_id=$(printf '%s' "$line" | awk '{print $1}')
    age=$(printf '%s' "$line" | awk '{print $2}')
    echo "  ⚠ $job_id ($age) — /li:jobs continue $job_id  ·  /li:jobs abort $job_id  ·  /li:jobs branch $job_id"

    ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    printf '{"ts":"%s","kind":"job_stale_warn","job_id":"%s","age_hours_str":"%s","threshold_hours":%d}\n' \
      "$ts" "$job_id" "$age" "$hours" >> "$AUDIT" 2>/dev/null || true
  done
fi

exit 0
