#!/usr/bin/env bash
# component: brief-forge
# implements: ADR-0008, ADR-0027
# intent: .claude/plans/universal-implementation/packages/P04.md
# constraints: explicit opt-in; source implementation from this bundle; validate before audit/output
# last_intent_review: 2026-09-20
# Public helpers retain their historical signatures. forge_handoff is the release gate;
# constructing a head/body/tail fragment alone is not an evaluated or dispatched handoff.

_BF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$_BF_DIR/pack-resolver.sh" || return 1
command -v audit_log >/dev/null 2>&1 || source "$_BF_DIR/../bin/_audit.sh" || return 1

_brief_forge_python() {
  local python
  if command -v python3 >/dev/null 2>&1; then python=python3
  elif command -v python >/dev/null 2>&1; then python=python
  else echo "BRIEF FORGE: Python 3.9+ is required" >&2; return 1
  fi
  "$python" "$_BF_DIR/envelope_contract.py" "$@"
}

generate_envelope_id() { _brief_forge_python id; }
forge_envelope_head() { _brief_forge_python head "$@"; }
forge_envelope_body() { _brief_forge_python body "$@"; }
forge_envelope_tail() { _brief_forge_python tail "$@"; }
forge_envelope() { _brief_forge_python construct "$@"; }
yaml_to_json() { _brief_forge_python json "$@"; }
aggregate_evaluator_scores() { _brief_forge_python aggregate "$@"; }

build_escape_hatches() { _brief_forge_python escape-hatches "$@"; }

resolve_brief_forge_handoff_field() {
  local handoff="${1:-}" field="${2:-}" value
  case "$handoff" in
    on_subagent_spawn|on_phase_transition|on_workflow_handoff|on_cold_executor|on_operator_input|cold_path_bypass) ;;
    *) return 2 ;;
  esac
  case "$handoff:$field" in
    on_*:enabled|on_*:evaluators|cold_path_bypass:eligible_skills) ;;
    *) return 2 ;;
  esac
  if declare -F resolve_pack_field_json >/dev/null 2>&1; then
    value=$(resolve_pack_field_json "brief_forge_handoffs.$handoff.$field") || return 1
    _brief_forge_python policy-value "$field" "$value"
  else
    value=$(resolve_pack_field "brief_forge_handoffs.$handoff.$field") || return 1
    _brief_forge_python policy-value "$field" "$value" --legacy-accessor
  fi
}

_brief_forge_audit() {
  local directory receipt_id decision="${1:?}" reason="${2:?}" evaluator="${4:-}"
  case "$decision:$reason" in
    blocked:invalid_policy|blocked:unknown_evaluator|blocked:invalid_content|blocked:evaluation_failed|blocked:release_failed|bypassed:disabled|bypassed:eligible) ;;
    *) echo "BRIEF FORGE: invalid audit outcome" >&2; return 1 ;;
  esac
  directory="$(_audit_out_dir brief-forge)" || return 1
  receipt_id=$(generate_envelope_id) || return 1
  local -a fields=("reason=$reason" "audit_receipt=$receipt_id")
  if [ -n "$evaluator" ]; then
    _brief_forge_python policy-value evaluators "[$evaluator]" --legacy-accessor >/dev/null || return 1
    fields+=("evaluator=$evaluator")
  fi
  audit_log brief-forge "brief_forge_$decision" "${fields[@]}" || return 1
  _brief_forge_python receipt "$directory" "$receipt_id" "brief_forge_$decision"
}

write_bypass_audit() { _brief_forge_audit bypassed "${4:-eligible}"; }

validate_brief_forge_evaluators() {
  local names="${1:-}" name evaluator_fn
  local -a configured=()
  IFS=',' read -ra configured <<< "$names"
  for name in "${configured[@]}"; do
    [ -z "$name" ] && continue
    if [[ ! "$name" =~ ^[a-z][a-z0-9_-]*$ ]]; then
      echo "BRIEF FORGE: invalid evaluator identifier" >&2
      return 1
    fi
    evaluator_fn="evaluator_${name//-/_}"
    if ! declare -F "$evaluator_fn" >/dev/null 2>&1; then
      _brief_forge_audit blocked unknown_evaluator --evaluator "$name" || return 1
      echo "BRIEF FORGE: BLOCKED - unknown evaluator '$name' is not loaded" >&2
      return 1
    fi
  done
}

_brief_forge_block() {
  _brief_forge_audit blocked "$1" || return 1
  echo "BRIEF FORGE: BLOCKED - $1; no envelope released" >&2
  return 1
}

forge_handoff() (
  [ "$#" -eq 5 ] || { echo "Usage: forge_handoff <kind> <from> <to> <content_type> <content_file>" >&2; return 2; }
  local kind="$1" from="$2" to="$3" content_type="$4" content_file="$5"
  local enabled raw_evaluators evaluators_csv bypass budget audit_dir temporary candidate ready results errors name result seen
  local fields identity digest ctype score ran
  local -a configured=()
  source "$_BF_DIR/brief-forge-evaluators.sh" || return 1
  enabled=$(resolve_brief_forge_handoff_field "on_$kind" enabled) || { _brief_forge_block invalid_policy; return 1; }
  raw_evaluators=$(resolve_brief_forge_handoff_field "on_$kind" evaluators) || { _brief_forge_block invalid_policy; return 1; }
  case "$enabled" in true|false) ;; *) _brief_forge_block invalid_policy; return 1 ;; esac
  [ -n "$raw_evaluators" ] || { _brief_forge_block invalid_policy; return 1; }
  evaluators_csv=$(printf '%s' "$raw_evaluators" | tr -d '[][:space:]')
  bypass=$(resolve_brief_forge_handoff_field cold_path_bypass eligible_skills) || { _brief_forge_block invalid_policy; return 1; }
  bypass=$(printf '%s' "$bypass" | tr -d '[][:space:]')
  if [ "$enabled" = false ]; then
    write_bypass_audit "$kind" "$from" "$to" disabled || return 1
    return 3
  fi
  case ",$bypass," in
    *",$from,"*) write_bypass_audit "$kind" "$from" "$to" eligible || return 1; return 3 ;;
  esac
  validate_brief_forge_evaluators "$evaluators_csv" || return 1
  budget=$(resolve_pack_field brief_forge_handoffs.budget_tokens) || { _brief_forge_block invalid_policy; return 1; }
  [[ "$budget" =~ ^[0-9]+$ ]] || { _brief_forge_block invalid_policy; return 1; }
  audit_dir="$(_audit_out_dir brief-forge)" || return 1
  umask 077
  temporary=$(mktemp -d) || return 1
  candidate="$temporary/candidate.json"
  ready="$temporary/ready.json"
  results="$temporary/evaluator-results.data"
  errors="$temporary/evaluator-error.txt"
  trap 'rm -f "$candidate" "$ready" "$results" "$errors"; rmdir "$temporary"' EXIT
  forge_envelope "$kind" "$from" "$to" "$content_type" "$content_file" > "$candidate" || {
    _brief_forge_block invalid_content; return 1;
  }
  : > "$results"
  IFS=',' read -ra configured <<< "security,$evaluators_csv"
  seen=","
  for name in "${configured[@]}"; do
    [ -n "$name" ] || continue
    case "$seen" in *",$name,"*) continue ;; esac
    seen="$seen$name,"
    result=$(run_evaluator "$name" "$candidate" 2>"$errors") || { _brief_forge_block evaluation_failed; return 1; }
    _brief_forge_python wrap-result "$name" "$result" >> "$results" || { _brief_forge_block evaluation_failed; return 1; }
  done
  _brief_forge_python finalize "$candidate" "$results" "$budget" "$audit_dir" > "$ready" || {
    _brief_forge_block release_failed; return 1;
  }
  fields=$(_brief_forge_python audit-fields "$ready") || { _brief_forge_block release_failed; return 1; }
  IFS='|' read -r identity digest ctype score ran <<< "$fields"
  audit_log brief-forge brief_forge_emitted "decision=validated-not-dispatched" \
    "envelope_id=$identity" "envelope_digest=$digest" "content_type=$ctype" \
    "score=$score" "evaluators_run=$ran" || return 1
  _brief_forge_python release "$ready" "$audit_dir" || {
    _brief_forge_block release_failed; return 1;
  }
)
