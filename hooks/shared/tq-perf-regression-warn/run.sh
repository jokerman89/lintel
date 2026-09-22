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

# Read one record for the complete path, not a text occurrence near other budgets.
tq_state_dir=".claude/runtime/state/tq"
[ -d "$tq_state_dir" ] || tq_state_dir=".lintel/state/tq" # legacy-fallback-ok
budget_spec=$(find "$tq_state_dir" -name "perf-budget-*.md" -mtime -30 2>/dev/null | sort | tail -1) || true
journey=""; budget_p95=""
if [ -n "$budget_spec" ]; then
  budget_text="$(cat -- "$budget_spec")" || {
    echo "WARN [Lintel hook tq-perf-regression-warn]: cannot read budget metadata: $budget_spec" >&2
    exit 1
  }
  metadata="$(printf '%s\n' "$budget_text" | LINTEL_PERF_EDITED_PATH="$file_edited" LC_ALL=C awk '
    function trim(s) { gsub(/^[[:space:]]+|[[:space:]]+$/, "", s); return s }
    function invalid(key) {
      print "WARN [Lintel hook tq-perf-regression-warn]: invalid " key " budget metadata" > "/dev/stderr"
      failed=1
    }
    function scalar(s, q,i,c,out,rest,closed) {
      scalar_bad=0; quoted=0; s=trim(s); q=substr(s,1,1)
      if (q=="\"" || q==sprintf("%c",39)) {
        quoted=1; out=""; closed=0
        for (i=2; i<=length(s); i++) {
          c=substr(s,i,1)
          if (c==q) {
            if (q==sprintf("%c",39) && substr(s,i+1,1)==q) { out=out q; i++; continue }
            closed=1; break
          }
          if (q=="\"" && c=="\\") {
            c=substr(s,++i,1)
            if (c=="t") c="\t"
            else if (c!="\\" && c!="\"" && c!="/") scalar_bad=1
          }
          out=out c
        }
        rest=substr(s,i+1)
        if (!closed || (rest!="" && rest !~ /^[[:space:]]+(#.*)?$/)) scalar_bad=1
        s=out
      } else {
        sub(/[[:space:]]+#.*$/, "", s)
        s=trim(s)
        if (s ~ /^#/) s=""
        if (s ~ /^[&*!|>]/ || substr(s,1,1)=="[" || substr(s,1,1)=="{") scalar_bad=1
      }
      if (s=="" || s ~ /[\r\n]/) scalar_bad=1
      return s
    }
    # Validate numeric spelling without conversion, rounding or machine-range loss.
    function finite_number(s) {
      return s ~ /^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?$/ \
          || s ~ /^[+-]?0x[0-9a-fA-F]+$/ || s ~ /^[+-]?0o[0-7]+$/
    }
    function finish_record( path,value,key) {
      if (!chosen && seen["path"]) {
        path=scalar(values["path"])
        if (scalar_bad) invalid("path")
        else if (("x" path)==("x" ENVIRON["LINTEL_PERF_EDITED_PATH"])) {
          chosen=1
          if (seen["journey"]) {
            selected_journey=scalar(values["journey"])
            if (scalar_bad || seen["journey"]>1) invalid("journey")
          }
          key=(seen["budget.p95_ms"] ? "budget.p95_ms" : "p95_ms")
          if (seen[key]) {
            value=scalar(values[key])
            if (scalar_bad || quoted || !finite_number(value) || seen[key]>1) invalid("p95_ms")
            selected_p95=value
          }
        }
      }
      for (key in seen) delete seen[key]
      for (key in values) delete values[key]
      list_record=0
    }
    {
      sub(/\r$/, "")
      line=trim($0)
      if (line ~ /^(```|~~~)/ || line=="---" || line=="...") {
        finish_record(); depth=0; next
      }
      if (line=="" || line ~ /^#/) next
      indent=match($0,/[^[:space:]]/)-1
      item=(line ~ /^-[[:space:]]+/)
      if (item) {
        match(line,/^-[[:space:]]+/)
        indent+=RLENGTH; line=substr(line,RLENGTH+1)
      }
      while (depth>0 && indent<=indents[depth]) depth--
      if (line !~ /^[A-Za-z_][A-Za-z_0-9-]*[[:space:]]*:/) next
      colon=index(line,":"); key=trim(substr(line,1,colon-1))
      value=trim(substr(line,colon+1))
      if (item && depth==0) {
        finish_record(); list_record=1; record_indent=indent
      } else if (list_record && depth==0 && indent<record_indent && key!="path") {
        finish_record()
      }
      if (depth==0) {
        if (key=="journey" && (seen["journey"] || (seen["path"] && !list_record))) finish_record()
        if (key=="path" && seen["path"]) finish_record()
        if (key=="journey" || key=="path" || (key=="p95_ms" && (seen["journey"] || seen["path"]))) {
          seen[key]++; values[key]=value
        }
      } else if (depth==1 && sections[depth]=="budget" && key=="p95_ms" && (seen["journey"] || seen["path"])) {
        seen["budget.p95_ms"]++; values["budget.p95_ms"]=value
      }
      if ((value=="" || value ~ /^#/) && key!="journey" && key!="path" && key!="p95_ms") {
        depth++; indents[depth]=indent; sections[depth]=key
      }
    }
    END {
      finish_record()
      if (failed) exit 1
      if (chosen) printf "matched\njourney=%s\np95_ms=%s\n", selected_journey, selected_p95
    }
  ')" || {
    echo "WARN [Lintel hook tq-perf-regression-warn]: cannot parse budget metadata: $budget_spec" >&2
    exit 1
  }
  while IFS= read -r field; do
    case "$field" in
      matched) matches_perf=1 ;;
      journey=*) journey="${field#journey=}" ;;
      p95_ms=*) budget_p95="${field#p95_ms=}" ;;
    esac
  done <<< "$metadata"
fi

[ "$matches_perf" -eq 0 ] && exit 0

audit_log "hooks" "tq_perf_regression_warn" "hook=tq-perf-regression-warn" "tier=warn" "file_edited=$file_edited" "journey=${journey:-unknown}" "budget_p95_ms=${budget_p95:-unknown}"

echo "WARN [Lintel hook tq-perf-regression-warn]: $file_edited"
echo "WARN: perf-budget-bound path${journey:+ (journey: $journey)}${budget_p95:+, p95 budget ${budget_p95}ms}"
echo "WARN: CI will enforce the budget; consider local perf check, or pass --ignore-perf-regression to acknowledge."

exit 0
