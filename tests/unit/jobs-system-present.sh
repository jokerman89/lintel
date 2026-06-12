#!/usr/bin/env bash
# tests/unit/jobs-system-present.sh
#
# Verifies v3.8 Feature 1 (jobs system) artifacts: 3 hooks + 2 skills + helper.
# tag: v3.8 feature-1 jobs

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/jobs-system-present.sh"
echo "================================="

# Helper present + sources cleanly
HELPER="$REPO_ROOT/bin/_jobs.sh"
if [ -f "$HELPER" ]; then
  pass "bin/_jobs.sh present"
  if ( source "$HELPER" 2>/dev/null && declare -F job_create >/dev/null ); then
    pass "_jobs.sh exposes job_create"
  else
    fail "_jobs.sh missing job_create"
  fi
  for fn in job_update job_archive regenerate_active list_jobs stale_jobs job_path job_id; do
    if ( source "$HELPER" 2>/dev/null && declare -F "$fn" >/dev/null ); then
      pass "_jobs.sh exposes $fn"
    else
      fail "_jobs.sh missing $fn"
    fi
  done
else
  fail "bin/_jobs.sh missing"
fi

# Three hooks
HOOKS=(job-begin job-end job-stale-warn)
for h in "${HOOKS[@]}"; do
  dir="$REPO_ROOT/hooks/shared/$h"
  if [ -d "$dir" ] && [ -f "$dir/HOOK.md" ] && [ -f "$dir/run.sh" ]; then
    pass "hook present: $h (HOOK.md + run.sh)"

    # HOOK.md frontmatter required fields
    for field in name tier event fires_on; do
      if grep -qE "^${field}:" "$dir/HOOK.md"; then
        pass "$h HOOK.md has $field"
      else
        fail "$h HOOK.md missing $field"
      fi
    done
  else
    fail "hook missing or incomplete: $h"
  fi
done

# Two skills (jobs + status)
SKILLS=(jobs status)
for s in "${SKILLS[@]}"; do
  f="$REPO_ROOT/skills/$s/SKILL.md"
  if [ -f "$f" ]; then
    name=$(grep '^name:' "$f" | head -1 | awk '{print $2}')
    layer=$(grep '^layer:' "$f" | head -1 | awk '{print $2}')
    if [ "$name" = "$s" ] && [ "$layer" = "foundation" ]; then
      pass "skill $s: frontmatter ok (name + layer)"
    else
      fail "skill $s: frontmatter mismatch (name=$name, layer=$layer)"
    fi
  else
    fail "skill missing: $s"
  fi
done

# jobs skill documents 5 subcommands
JOBS_SKILL="$REPO_ROOT/skills/jobs/SKILL.md"
if [ -f "$JOBS_SKILL" ]; then
  for sub in list continue replan abort branch; do
    if grep -qE "\`$sub\`" "$JOBS_SKILL" || grep -q "^- \`$sub" "$JOBS_SKILL" || grep -qE "^\*\*\`$sub\`\*\*:" "$JOBS_SKILL"; then
      pass "jobs/SKILL.md documents subcommand: $sub"
    else
      fail "jobs/SKILL.md missing subcommand documentation: $sub"
    fi
  done
fi

# Behavior smoke: create + update + archive — against the v5 layout (ADR-0005):
# job data is repo-scoped, so the sandbox simulates a MIGRATED repo (layout
# marker present) and asserts data lands in <repo>/.claude/runtime/jobs/ with
# the cross-repo registry at $LINTEL_HOME/jobs/_active.md.
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
export LINTEL_HOME="$TMP/.lintel"
mkdir -p "$LINTEL_HOME/audit"
SBREPO="$TMP/repo"
mkdir -p "$SBREPO/.claude"
printf 'layout_version: 5\n' > "$SBREPO/.claude/lintel-layout.yaml"
export LINTEL_REPO_ROOT="$SBREPO"
JOBS_DIR="$SBREPO/.claude/runtime/jobs"

(
  source "$HELPER"
  id=$(job_create cycle customer-engagement)
  if [ -n "$id" ] && [ -d "$JOBS_DIR/$id" ]; then
    echo "  PASS: job_create produces job-id ($id) + directory in .claude/runtime/jobs/"
  else
    echo "  FAIL: job_create did not yield directory under .claude/runtime/jobs/"
    exit 1
  fi

  if [ -f "$JOBS_DIR/$id/job.yaml" ]; then
    echo "  PASS: job.yaml created"
  else
    echo "  FAIL: job.yaml missing"
    exit 1
  fi

  if [ -f "$JOBS_DIR/_active.md" ]; then
    echo "  PASS: per-repo _active.md regenerated"
  else
    echo "  FAIL: per-repo _active.md not regenerated"
    exit 1
  fi

  if [ -f "$LINTEL_HOME/jobs/_active.md" ] && grep -q "$id" "$LINTEL_HOME/jobs/_active.md"; then
    echo "  PASS: cross-repo registry at ~/.lintel/jobs/_active.md lists the job"
  else
    echo "  FAIL: cross-repo registry missing or does not list the job"
    exit 1
  fi

  job_update "$id" "PLAN" "IN_PROGRESS"
  if grep -q "current_step: PLAN" "$JOBS_DIR/$id/job.yaml"; then
    echo "  PASS: job_update modifies current_step"
  else
    echo "  FAIL: job_update did not update current_step"
    exit 1
  fi

  job_archive "$id" "DONE"
  if [ -d "$JOBS_DIR/$id" ]; then
    echo "  FAIL: archive did not move job folder"
    exit 1
  fi
  if find "$JOBS_DIR/_archive" -name "job.yaml" -path "*$id*" 2>/dev/null | grep -q .; then
    echo "  PASS: job_archive moves to _archive/"
  else
    echo "  FAIL: job not found in _archive after archive"
    exit 1
  fi

  if [ -f "$SBREPO/.claude/runtime/audit/jobs.jsonl" ]; then
    n=$(wc -l < "$SBREPO/.claude/runtime/audit/jobs.jsonl" | tr -d ' ')
    if [ "$n" -ge 3 ]; then
      echo "  PASS: jobs.jsonl audit log written repo-scoped ($n entries)"
    else
      echo "  FAIL: audit log under-populated ($n entries, expected ≥3)"
      exit 1
    fi
  else
    echo "  FAIL: jobs.jsonl audit log not written to .claude/runtime/audit/"
    exit 1
  fi
) || FAILED=1

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All jobs-system-present tests PASSED"
  exit 0
else
  echo "Some jobs-system-present tests FAILED"
  exit 1
fi
