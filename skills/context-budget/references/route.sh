#!/usr/bin/env bash
# component: context-budget-routing
# implements: ADR-0006, ADR-0028, ADR-0034
# intent: skills/context-budget/SKILL.md
# constraints: read-only selector glue; existing providers own parsing and results
# last_intent_review: 2026-09-29

set -u
source_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)" || exit 1
export LINTEL_SOURCE_ROOT="$source_root"

route=observation
case "${1:-}" in
  --advice) route=advice; shift ;;
  --handoff) route=handoff; shift ;;
  --watch) route=watch; shift ;;
esac

for argument in "$@"; do
  case "$argument" in
    --advice|--handoff|--watch)
      printf 'context-budget route: choose only one leading selector.\n' >&2
      exit 2 ;;
  esac
done

case "$route" in
  watch)
    printf 'context-budget route: watch is an instruction-driven workflow; resolve its selected configuration and telemetry before calling the observation reader.\n' >&2
    exit 2 ;;
  observation|advice)
    source "$source_root/bin/_context.sh" || exit $?
    if [ "$route" = advice ]; then context_perf "$@"; else context_budget "$@"; fi
    exit $? ;;
esac

case "${1:-}" in
  --plan|--plan=*|[!-]*)
    printf 'context-budget route: legacy plan inspection retains the explicit selected-file/manual join; follow the owner workflow instead of inventing a work map.\n' >&2
    exit 2 ;;
esac

has_map=false
for argument in "$@"; do
  case "$argument" in
    --plan|--plan=*)
      printf 'context-budget route: legacy --plan needs the explicit selected-file/manual join, not the mapped reader.\n' >&2
      exit 2 ;;
    --rep|--rep=*|--repo|--repo=*|--v|--v=*|--vi|--vi=*|--vie|--vie=*|--view|--view=*)
      printf 'context-budget route: repository and budget view come from the selected workflow, not overriding arguments.\n' >&2
      exit 2 ;;
    --map|--map=*) has_map=true ;;
  esac
done

arguments=("$@")
if [ "$has_map" = false ] && [ -n "${LINTEL_WORK_MAP:-}" ]; then
  arguments=(--map "$LINTEL_WORK_MAP" ${arguments[@]+"${arguments[@]}"})
fi
python="${LINTEL_PYTHON:-python3}"
"$python" "$source_root/bin/li-work-artifacts.py" \
  --repo "${LINTEL_REPO_ROOT:?select the working repository}" --view budget ${arguments[@]+"${arguments[@]}"}
