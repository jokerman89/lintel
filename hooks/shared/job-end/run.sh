#!/usr/bin/env bash
# job-end — Lintel lifecycle hook (v3.8 Feature 1)
# Fires when a workflow_root skill reaches DONE/ABORTED/FAILED.
# Applies cleanup policy + moves to _archive/.

set -uo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
LINTEL_JOBS_DIR="${LINTEL_JOBS_DIR:-$LINTEL_HOME/jobs}"
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../bin" 2>/dev/null && pwd)" || \
BIN_DIR="${LINTEL_HOME}/scaffolding/bin"

# Args: <job_id> <result>
job_id="${1:-}"
result="${2:-DONE}"
[ -z "$job_id" ] && exit 0
[ -n "${NO_CLEANUP:-}" ] && exit 0

dir="$LINTEL_JOBS_DIR/$job_id"
[ -d "$dir" ] || exit 0

helper="$BIN_DIR/_jobs.sh"
[ -f "$helper" ] || {
  for candidate in \
    "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../bin" 2>/dev/null && pwd)/_jobs.sh" \
    "$LINTEL_HOME/scaffolding/bin/_jobs.sh"; do
    [ -f "$candidate" ] && { helper="$candidate"; break; }
  done
}
[ -f "$helper" ] || exit 0

# Promote durable artifacts BEFORE moving to archive
repo_root="${PWD}"
docs_plans="$repo_root/docs/plans"

# Determine slug from job_id (strip the date+hash suffix → workflow part)
slug=$(printf '%s' "$job_id" | sed -E 's/-[0-9]{8}-[0-9]{4}-[a-f0-9]{6}$//')
[ -z "$slug" ] && slug="$job_id"

# Promote the cold-executor trio (plan.md + spec.md + prompt.md)
for artifact in plan.md spec.md prompt.md; do
  src="$dir/outputs/$artifact"
  if [ -f "$src" ]; then
    target_dir="$docs_plans/$slug"
    mkdir -p "$target_dir" 2>/dev/null || true
    cp "$src" "$target_dir/" 2>/dev/null && \
      echo "[lintel] Promoted $artifact → docs/plans/$slug/"
  fi
done

# Promote lessons via existing /li:lessons-promote pattern (skill body handles details)
if [ -f "$dir/outputs/lessons.md" ] && [ -f "$repo_root/tasks/lessons.md" ]; then
  echo "[lintel] Lesson candidates in job — invoke /li:lessons-promote for review"
fi

# Promote ADRs
adr_target="$repo_root/docs/adr"
if [ -d "$dir/outputs/adr" ] && [ -d "$adr_target" ]; then
  for adr in "$dir/outputs/adr"/*; do
    [ -f "$adr" ] || continue
    cp "$adr" "$adr_target/" 2>/dev/null && \
      echo "[lintel] Promoted ADR: $(basename "$adr") → docs/adr/"
  done
fi

# Discard scratch
if [ -d "$dir/scratch" ]; then
  rm -rf "$dir/scratch" 2>/dev/null || true
fi

# Archive the job (uses helper)
# shellcheck disable=SC1090
source "$helper"
job_archive "$job_id" "$result"

echo "[lintel] Job ended: $job_id (result=$result) → archived"

exit 0
