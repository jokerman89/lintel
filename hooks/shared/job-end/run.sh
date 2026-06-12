#!/usr/bin/env bash
# job-end — Lintel lifecycle hook (v3.8 Feature 1)
# Fires when a workflow_root skill reaches DONE/ABORTED/FAILED.
# Applies cleanup policy + moves to _archive/.

set -uo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../bin" 2>/dev/null && pwd)" || \
BIN_DIR="${LINTEL_HOME}/scaffolding/bin"

# Args: <job_id> <result>
job_id="${1:-}"
result="${2:-DONE}"
[ -z "$job_id" ] && exit 0
[ -n "${NO_CLEANUP:-}" ] && exit 0

helper="$BIN_DIR/_jobs.sh"
[ -f "$helper" ] || {
  for candidate in \
    "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../bin" 2>/dev/null && pwd)/_jobs.sh" \
    "$LINTEL_HOME/scaffolding/bin/_jobs.sh"; do
    [ -f "$candidate" ] && { helper="$candidate"; break; }
  done
}
[ -f "$helper" ] || exit 0

# Source the helper FIRST — it scope-resolves LINTEL_JOBS_DIR (v5: repo-local
# .claude/runtime/jobs/ on migrated repos, ~/.lintel/jobs otherwise).
# shellcheck disable=SC1090
source "$helper"

dir="$LINTEL_JOBS_DIR/$job_id"
[ -d "$dir" ] || exit 0

# Promote durable artifacts BEFORE moving to archive (v5: .claude/plans/;
# legacy docs/plans/ on un-migrated repos)
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || printf '%s' "$PWD")"
_layout_v=$(grep -E '^layout_version:' "$repo_root/.claude/lintel-layout.yaml" 2>/dev/null \
            | head -1 | awk '{print $2}' | tr -d '\r')
if [ "${_layout_v:-0}" -ge 5 ] 2>/dev/null; then
  docs_plans="$repo_root/.claude/plans"
else
  docs_plans="$repo_root/docs/plans"   # legacy-fallback-ok
fi

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
      echo "[lintel] Promoted $artifact → ${target_dir#"$repo_root"/}/"
  fi
done

# Promote lessons via existing /li:lessons-promote pattern (skill body handles details)
lessons_file="$repo_root/.claude/memory/lessons.md"
[ -f "$lessons_file" ] || lessons_file="$repo_root/tasks/lessons.md"   # legacy-fallback-ok
if [ -f "$dir/outputs/lessons.md" ] && [ -f "$lessons_file" ]; then
  echo "[lintel] Lesson candidates in job — invoke /li:lessons-promote for review"
fi

# Promote ADRs
adr_target="$repo_root/.claude/decisions"
[ -d "$adr_target" ] || adr_target="$repo_root/docs/adr"   # legacy-fallback-ok
if [ -d "$dir/outputs/adr" ] && [ -d "$adr_target" ]; then
  for adr in "$dir/outputs/adr"/*; do
    [ -f "$adr" ] || continue
    cp "$adr" "$adr_target/" 2>/dev/null && \
      echo "[lintel] Promoted ADR: $(basename "$adr") → ${adr_target#"$repo_root"/}/"
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
