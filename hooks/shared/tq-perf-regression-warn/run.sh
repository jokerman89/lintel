#!/usr/bin/env bash
# tq-perf-regression-warn — Lintel warn-only hook
# Surfaces edits to perf-budget-bound paths.

set -euo pipefail
LINTEL_REPO_ROOT="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"  # guard: unset under set -u aborts the hook (fail-closed)

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
file_edited="$(hook_input file_path "${1:-}")"
[ -z "$file_edited" ] && exit 0

# Match against perf_path_glob from pack
perf_glob=""
if [ -f "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" ]; then
  source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" 2>/dev/null
  perf_glob=$(resolve_pack_field testing_qa.perf_path_glob 2>/dev/null || true)
fi

matches_perf=0
if [ -n "$perf_glob" ]; then
  IFS=',' read -ra patterns <<< "$perf_glob"
  for p in "${patterns[@]}"; do
    p=$(printf '%s' "$p" | tr -d '[:space:]')
    case "$file_edited" in $p) matches_perf=1; break ;; esac
  done
fi

# Check perf-budget spec for explicit path mentions
tq_state_dir=".claude/runtime/state/tq"
[ -d "$tq_state_dir" ] || tq_state_dir=".lintel/state/tq" # legacy-fallback-ok
budget_spec=$(find "$tq_state_dir" -name "perf-budget-*.md" -mtime -30 2>/dev/null | sort | tail -1)
if [ "$matches_perf" -eq 0 ] && [ -n "$budget_spec" ] && [ -f "$budget_spec" ]; then
  if grep -qF "$file_edited" "$budget_spec" 2>/dev/null; then
    matches_perf=1
  fi
fi

[ "$matches_perf" -eq 0 ] && exit 0

# Extract journey + budget if known
journey=$(grep -B1 "$file_edited" "$budget_spec" 2>/dev/null | grep -oE 'journey:[[:space:]]*[a-z_]+' | head -1 | awk -F': *' '{print $2}')
budget_p95=$(grep -A5 "$file_edited" "$budget_spec" 2>/dev/null | grep -oE 'p95_ms:[[:space:]]*[0-9]+' | head -1 | grep -oE '[0-9]+')

audit_log "hooks" "tq_perf_regression_warn" "hook=tq-perf-regression-warn" "tier=warn" "file_edited=$file_edited" "journey=${journey:-unknown}" "budget_p95_ms=${budget_p95:-unknown}"

echo "WARN [Lintel hook tq-perf-regression-warn]: $file_edited"
echo "WARN: perf-budget-bound path${journey:+ (journey: $journey)}${budget_p95:+, p95 budget ${budget_p95}ms}"
echo "WARN: CI will enforce the budget; consider local perf check, or pass --ignore-perf-regression to acknowledge."

exit 0
