#!/usr/bin/env bash
# component: brief-forge-evaluators
# implements: ADR-0008, ADR-0027
# intent: .claude/plans/universal-implementation/packages/P04.md
# constraints: explicit invocation; unknown or unavailable evaluators fail, never score as success
# last_intent_review: 2026-09-20

_BFE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
declare -F _brief_forge_python >/dev/null 2>&1 || source "$_BFE_DIR/brief-forge.sh"

evaluators_for_handoff() {
  local value
  value=$(resolve_brief_forge_handoff_field "${1:?}" evaluators) || return 1
  [ -n "$value" ] || { echo "BRIEF FORGE: evaluator policy is missing" >&2; return 1; }
  printf '%s' "$value" | tr -d '[]' | tr ',' ' '
}

run_evaluator() {
  local name="${1:?}" envelope="${2:?}" fn
  [[ "$name" =~ ^[a-z][a-z0-9_-]*$ ]] || { echo "BRIEF FORGE: invalid evaluator identifier" >&2; return 1; }
  fn="evaluator_${name//-/_}"
  declare -F "$fn" >/dev/null 2>&1 || { echo "BRIEF FORGE: unknown evaluator" >&2; return 1; }
  "$fn" "$envelope"
}

evaluator_security() { _brief_forge_python evaluate security "${1:?}"; }
evaluator_completeness() { _brief_forge_python evaluate completeness "${1:?}"; }
evaluator_stale() { _brief_forge_python evaluate stale "${1:?}"; }
