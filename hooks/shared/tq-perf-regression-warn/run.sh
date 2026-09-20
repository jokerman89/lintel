#!/usr/bin/env bash
# tq-perf-regression-warn — Lintel warn-only hook
# Surfaces edits to perf-budget-bound paths.
# component: tq-perf-regression-warn
# implements: ADR-0008
# intent: .claude/plans/universal-implementation/packages/P01.md
# constraints: opt-in warning; target policy is data, not implementation code
# last_intent_review: 2026-09-20

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
_resolver="$(dirname "${BASH_SOURCE[0]}")/../../../lib/pack-resolver.sh"
[ -f "$_resolver" ] || _resolver="$LINTEL_HOME/lib/pack-resolver.sh"
if [ -f "$_resolver" ]; then
  LINTEL_SOURCE_ROOT="$(cd "$(dirname "$_resolver")/.." && pwd)"
  source "$_resolver" 2>/dev/null
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
budget_spec=$(find "$tq_state_dir" -name "perf-budget-*.md" -mtime -30 2>/dev/null | sort | tail -1) || true
if [ "$matches_perf" -eq 0 ] && [ -n "$budget_spec" ] && [ -f "$budget_spec" ]; then
  if grep -qF "$file_edited" "$budget_spec" 2>/dev/null; then
    matches_perf=1
  fi
fi

[ "$matches_perf" -eq 0 ] && exit 0

# Missing advisory metadata is not a failed read or malformed present value.
read_budget_field() {
  local context rc=0
  context="$(grep "$1" -- "$file_edited" "$budget_spec")" || rc=$?
  if [ "$rc" -gt 1 ]; then
    echo "WARN [Lintel hook tq-perf-regression-warn]: cannot read budget metadata: $budget_spec" >&2
    return 1
  fi
  printf '%s\n' "$context" | awk -v key="$2" -v value_pattern="$3" '
    !found && match($0, key ":[[:space:]]*" value_pattern) {
      value=substr($0, RSTART, RLENGTH)
      sub("^" key ":[[:space:]]*", "", value)
      print value; found=1; next
    }
    !found && $0 ~ key ":" {
      print "WARN [Lintel hook tq-perf-regression-warn]: invalid " key " budget metadata" > "/dev/stderr"
      exit 1
    }
  '
}
journey=""; budget_p95=""
if [ -n "$budget_spec" ]; then
  journey="$(read_budget_field -B1 journey '[a-z_]+')"
  budget_p95="$(read_budget_field -A5 p95_ms '[0-9]+')"
fi

audit_log "hooks" "tq_perf_regression_warn" "hook=tq-perf-regression-warn" "tier=warn" "file_edited=$file_edited" "journey=${journey:-unknown}" "budget_p95_ms=${budget_p95:-unknown}"

echo "WARN [Lintel hook tq-perf-regression-warn]: $file_edited"
echo "WARN: perf-budget-bound path${journey:+ (journey: $journey)}${budget_p95:+, p95 budget ${budget_p95}ms}"
echo "WARN: CI will enforce the budget; consider local perf check, or pass --ignore-perf-regression to acknowledge."

exit 0
