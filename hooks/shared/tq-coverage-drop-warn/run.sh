#!/usr/bin/env bash
# tq-coverage-drop-warn — Lintel warn-only hook
# Surfaces commits dropping coverage below profile threshold.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
PROFILE="$LINTEL_HOME/profile.yaml"
mkdir -p "$LINTEL_HOME/audit"

command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

# Read thresholds
coverage_target=80
critical_path=100

if [ -f "$PROFILE" ]; then
  v=$(awk '/^engineering:/{in_eng=1; next} /^[a-z]/{in_eng=0}
           in_eng && /testing_qa:/{in_tq=1; next} in_eng && /^[[:space:]]+[a-z]/ && !/testing_qa/{in_tq=0}
           in_tq && /coverage_target:/{print $NF; exit}' "$PROFILE" 2>/dev/null || true)
  [ -n "$v" ] && coverage_target="$v"
  v=$(awk '/^engineering:/{in_eng=1; next} /^[a-z]/{in_eng=0}
           in_eng && /testing_qa:/{in_tq=1; next} in_eng && /^[[:space:]]+[a-z]/ && !/testing_qa/{in_tq=0}
           in_tq && /critical_path_coverage:/{print $NF; exit}' "$PROFILE" 2>/dev/null || true)
  [ -n "$v" ] && critical_path="$v"
fi

# Look for a recent coverage report
tq_state_dir=".claude/runtime/state/tq"
[ -d "$tq_state_dir" ] || tq_state_dir=".lintel/state/tq" # legacy-fallback-ok
coverage_report=$(find "$tq_state_dir" -name "coverage-audit-*.md" -mtime -1 2>/dev/null | sort | tail -1)
[ -z "$coverage_report" ] && exit 0   # No report available; can't compare; silent

# Heuristic: extract overall coverage %
overall_pct=$(grep -oE 'overall[^[:digit:]]*([0-9]+)' "$coverage_report" 2>/dev/null | head -1 | grep -oE '[0-9]+' | head -1)
critical_below=$(grep -oE 'critical.path[^[:digit:]]*([0-9]+)[[:space:]]*below' "$coverage_report" 2>/dev/null | grep -oE '[0-9]+' | head -1)
critical_below="${critical_below:-0}"

should_warn=false
[ -n "$overall_pct" ] && [ "$overall_pct" -lt "$coverage_target" ] && should_warn=true
[ "$critical_below" -gt 0 ] && should_warn=true

if $should_warn; then
  audit_log "hooks" "tq_coverage_drop_warn" "hook=tq-coverage-drop-warn" "tier=warn" "coverage_pct=${overall_pct:-unknown}" "target_pct=$coverage_target" "critical_below=$critical_below"

  echo "WARN [Lintel hook tq-coverage-drop-warn]: coverage drop detected"
  [ -n "$overall_pct" ] && echo "WARN: overall coverage $overall_pct% (target $coverage_target%)"
  [ "$critical_below" -gt 0 ] && echo "WARN: $critical_below critical path(s) below $critical_path% threshold"
  echo "WARN: consider /li:tq single --action coverage-audit for backfill plan, or pass --ignore-coverage-drop."
fi

exit 0
