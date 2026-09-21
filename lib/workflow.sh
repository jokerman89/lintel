#!/usr/bin/env bash
# component: selected-work-lifecycle
# implements: ADR-0026, ADR-0028, ADR-0029
# intent: skills/spec-kit/references/work-map.md
# constraints: references in the existing ledger only; no execution, approval or new backlog
# last_intent_review: 2026-09-21

_WORKFLOW_SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$_WORKFLOW_SOURCE/lib/state.sh"

_workflow_init() {
  : "${LINTEL_SOURCE_ROOT:?select the trusted source}"
  : "${LINTEL_REPO_ROOT:?select the working target}"
  LINTEL_HOME="${LINTEL_HOME:-$LINTEL_REPO_ROOT/.claude/runtime/lintel-home}"
  source "$_WORKFLOW_SOURCE/lib/pack-resolver.sh" || return $?
  _profile_python
}

_workflow_map() {
  local argument
  for argument in "${@:2}"; do
    case "$argument" in
      --repo|--repo=*|--rep|--rep=*|--map|--map=*)
        echo "ERROR [lintel/workflow]: extra arguments cannot replace the selected target or map" >&2
        return 2 ;;
    esac
  done
  PYTHONDONTWRITEBYTECODE=1 "$_LINTEL_PROFILE_PYTHON" "$_WORKFLOW_SOURCE/bin/li-work-artifacts.py" \
    --repo "$LINTEL_REPO_ROOT" --map "$1" "${@:2}"
}

_workflow_value() {
  "$_LINTEL_PROFILE_PYTHON" -c '
import json, sys
value = json.load(sys.stdin)[sys.argv[1]]
print(value if isinstance(value, str) else json.dumps(value, sort_keys=True, separators=(",", ":")))
' "$1"
}

_workflow_same_json() {
  "$_LINTEL_PROFILE_PYTHON" -c 'import json,sys; sys.exit(json.loads(sys.argv[1]) != json.loads(sys.argv[2]))' "$1" "$2"
}

_workflow_guard_analyze_report_path() {
  PYTHONDONTWRITEBYTECODE=1 "${_LINTEL_PROFILE_PYTHON:?verify workflow context first}" - \
    "$_WORKFLOW_SOURCE/lib" "${LINTEL_REPO_ROOT:?select the working target}" "${2:-}" "${1:-}" <<'PY'
from pathlib import Path
import stat
import sys

sys.path.insert(0, sys.argv[1])
from context_safety import checked_root, safe_path


def anchored(value, root):
    if not value:
        raise ValueError("An explicit report/state path is required")
    path = Path(value)
    if (path.drive or path.root) and not path.is_absolute():
        raise ValueError("Drive-relative or incompletely rooted paths are unsupported")
    return path if path.is_absolute() else root / path


def leaf_stat(path):
    try:
        result = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(result.st_mode):
        raise ValueError("Analysis report is not a regular file")
    return result


try:
    target = checked_root(Path(sys.argv[2]))
    state = checked_root(anchored(sys.argv[3], target))
    candidate = anchored(sys.argv[4], target)
    for root in (target, state):
        try:
            relative = candidate.relative_to(root)
        except ValueError:
            continue
        checked = safe_path(root, relative.as_posix())
        if not checked.parent.samefile(candidate.parent):
            raise ValueError("Report parent identity disagrees with the declared root")
        break
    else:
        raise ValueError("Analysis report is outside the declared target/state roots")
    history = safe_path(state, "analyze-report.md")
    if not stat.S_ISDIR(candidate.parent.stat().st_mode):
        raise ValueError("Analysis report parent is not an existing directory")
    current, previous = leaf_stat(candidate), leaf_stat(history)
    if current is not None and previous is not None:
        is_history = candidate.samefile(history)
    else:
        same_parent = candidate.parent.samefile(history.parent)
        is_history = same_parent and candidate.name == history.name
        # A case-only absent leaf is uncertainty, not proof of equivalence.
        # Never fold whole paths or override existing-file identity above.
        if (same_parent and current is None and previous is None and not is_history
                and candidate.name.casefold() == history.name.casefold()):
            raise ValueError("Absent report names may alias the global history location")
    if is_history:
        print("INCOMPLETE [lintel/plan]: legacy global analysis is history; reconcile its cycle link",
              file=sys.stderr)
        raise SystemExit(2)
except (OSError, ValueError) as exc:
    print(f"INCOMPLETE [lintel/plan]: analysis report identity unresolved: {exc}", file=sys.stderr)
    raise SystemExit(2)
PY
}

_workflow_profile() {
  local previous="${LINTEL_PROFILE_REFERENCE:-}" rc
  _workflow_init || return $?
  # Verification, not bootstrap: missing durable state on resume must not rebind.
  # The shell API's positional argument is a reference FILE. Ledger JSON uses
  # its existing LINTEL_PROFILE_REFERENCE input instead.
  if [ "$#" -gt 0 ]; then export LINTEL_PROFILE_REFERENCE="$1"; fi
  if verify_profile_context >/dev/null; then :
  else
    rc=$?; export LINTEL_PROFILE_REFERENCE="$previous"; return "$rc"
  fi
  LINTEL_REQUIRED_POLICY=$(profile_required_policy) || return $?
  export LINTEL_REQUIRED_POLICY
}

workflow_inspect() {
  _workflow_profile || return $?
  _workflow_map "${1:?select work.json}" --view context "${@:2}"
}

workflow_begin() {
  local id="${1:?cycle ID required}" mode="${2:?mode required}" selected="${3:-}"
  local context argument artifacts='{}'
  shift 2; [ "$#" -eq 0 ] || shift
  for argument in "$@"; do
    case "${argument%%=*}" in
      work_map_path|work_artifacts|profile_reference|profile_context_file|required_policy)
        echo "ERROR [lintel/workflow]: metadata cannot replace verified work/profile identity" >&2
        return 2 ;;
    esac
  done
  _workflow_profile || return $?
  if [ -n "$selected" ]; then
    context=$(_workflow_map "$selected" --view context) || return $?
    selected=$(printf '%s' "$context" | _workflow_value work_map) || return $?
    artifacts=$(printf '%s' "$context" | _workflow_value artifacts) || return $?
  fi
  state_cycle_begin "$id" "$mode" "work_map_path=$selected" "work_artifacts=$artifacts" \
    "profile_reference=$LINTEL_PROFILE_REFERENCE" "profile_context_file=$PACK_CACHE_FILE" \
    "required_policy=$LINTEL_REQUIRED_POLICY" "$@" || return $?
  export LINTEL_CYCLE_ID="$id" LINTEL_WORK_MAP="$selected"
}

workflow_bind_work() {
  local context selected artifacts previous reference
  _workflow_profile || return $?
  [ -n "$(state_cycle_field cycle_id)" ] || {
    echo "ERROR [lintel/workflow]: begin a cycle before attaching work" >&2; return 2;
  }
  reference=$(state_cycle_field profile_reference) || return $?
  _workflow_same_json "$reference" "$LINTEL_PROFILE_REFERENCE" || {
    echo "ERROR [lintel/workflow]: cycle profile differs; explicit reconciliation required" >&2; return 2;
  }
  context=$(_workflow_map "${1:?select work.json}" --view context) || return $?
  selected=$(printf '%s' "$context" | _workflow_value work_map) || return $?
  artifacts=$(printf '%s' "$context" | _workflow_value artifacts) || return $?
  previous=$(state_cycle_field work_map_path) || return $?
  [ -z "$previous" ] || [ "$previous" = "$selected" ] || {
    echo "ERROR [lintel/workflow]: cannot replace this cycle's selected initiative" >&2; return 2;
  }
  if [ -n "$previous" ]; then
    _workflow_same_json "$(state_cycle_field work_artifacts)" "$artifacts" || {
      echo "ERROR [lintel/workflow]: mapped artifact paths changed; reconcile explicitly" >&2; return 2;
    }
  else
    state_append WORK SELECTED "work_map_path=$selected" "work_artifacts=$artifacts" || return $?
  fi
  export LINTEL_WORK_MAP="$selected"
}

workflow_resume() {
  local id="${1:?select the original cycle ID}" selected="${2:-}" saved reference policy context artifacts phase profile_file operation
  _workflow_init || return $?
  saved=$(state_cycle_field work_map_path "$(state_file)" "$id") || {
    echo "ERROR [lintel/workflow]: selected cycle is absent" >&2; return 2;
  }
  reference=$(state_cycle_field profile_reference "$(state_file)" "$id") || return $?
  policy=$(state_cycle_field required_policy "$(state_file)" "$id") || return $?
  profile_file=$(state_cycle_field profile_context_file "$(state_file)" "$id") || return $?
  if [ -z "$reference" ] || [ -z "$policy" ]; then
    echo "ERROR [lintel/workflow]: legacy/unbound cycle requires explicit profile reconciliation" >&2
    return 2
  fi
  if [ -n "${LINTEL_PROFILE_REFERENCE:-}" ]; then
    _workflow_same_json "$LINTEL_PROFILE_REFERENCE" "$reference" || {
      echo "ERROR [lintel/workflow]: caller and cycle profile references differ" >&2; return 2;
    }
  fi
  if [ -z "${LINTEL_PROFILE_CONTEXT_FILE:-}" ] && [ -n "$profile_file" ]; then
    export LINTEL_PROFILE_CONTEXT_FILE="$profile_file"
  fi
  _workflow_profile "$reference" || return $?
  _workflow_same_json "$policy" "$LINTEL_REQUIRED_POLICY" || {
    echo "ERROR [lintel/workflow]: required policy differs from the saved cycle" >&2; return 2;
  }
  selected="${selected:-$saved}"
  context='{"work_map":null,"artifacts":{}}'
  if [ -n "$selected" ]; then
    context=$(_workflow_map "$selected" --view context) || return $?
    selected=$(printf '%s' "$context" | _workflow_value work_map) || return $?
  fi
  if [ "$selected" != "$saved" ]; then
    echo "ERROR [lintel/workflow]: selected map is a different initiative" >&2; return 2
  fi
  artifacts=$(printf '%s' "$context" | _workflow_value artifacts) || return $?
  _workflow_same_json "$(state_cycle_field work_artifacts "$(state_file)" "$id")" "$artifacts" || {
    echo "ERROR [lintel/workflow]: mapped artifact paths changed; reconcile explicitly" >&2; return 2;
  }
  phase=$(state_resume_phase "$(state_file)" "$id") || return $?
  operation=$(state_cycle_field operation "$(state_file)" "$id") || return $?
  export LINTEL_CYCLE_ID="$id" LINTEL_WORK_MAP="$selected"
  printf '%s' "$context" | "$_LINTEL_PROFILE_PYTHON" -c '
import json, sys
work = json.load(sys.stdin)
print(json.dumps(dict(cycle_id=sys.argv[1], phase=sys.argv[2], work_map=work["work_map"],
                     artifacts=work["artifacts"], profile=json.loads(sys.argv[3]),
                     required_policy=json.loads(sys.argv[4]), operation=sys.argv[5] or None,
                     release_clearance=False), sort_keys=True))
' "$id" "$phase" "$LINTEL_PROFILE_REFERENCE" "$LINTEL_REQUIRED_POLICY" "$operation"
}
