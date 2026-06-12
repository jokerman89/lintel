#!/usr/bin/env bash
# tests/unit/jobs-steps.sh
#
# Slice 3 (scope-scaled-planning §3.4): per-step contracts in job.yaml.
# Asserts the three new mechanical contracts bin/_jobs.sh now enforces:
#   T1 — steps[] gets populated with real contracts (name/consumes/produces/
#        status/blocked_until), not a literal `steps: []`
#   T2 — job_can_start blocks a step until its blocked_until predicate holds,
#        across single- and &&-conjunction predicates
#   T3 — job_resume_point returns the deepest incomplete WBS node-path for a
#        tree-schema fixture job (and falls through to empty when complete)
#   T4 — job_update on a populated step is step-scoped (job stays ACTIVE);
#        on an un-stepped job it preserves the legacy top-level-status behaviour
# tag: slice-3 scope-scaled-planning jobs

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HELPER="$REPO_ROOT/bin/_jobs.sh"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/jobs-steps.sh"
echo "========================"

[ -f "$HELPER" ] || { fail "bin/_jobs.sh MISSING"; exit 1; }

# Isolated LINTEL_HOME so we never touch the operator's real jobs dir.
# This test pins the explicit-env seam (LINTEL_JOBS_DIR always wins — the
# documented test escape from v5 repo-scope resolution) and points
# LINTEL_REPO_ROOT at the markerless sandbox so audit writes stay sandboxed
# too; scope ROUTING itself is covered by jobs-system-present.sh.
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
export LINTEL_HOME="$TMP/.lintel"
export LINTEL_JOBS_DIR="$LINTEL_HOME/jobs"
export LINTEL_REPO_ROOT="$TMP"
mkdir -p "$LINTEL_HOME/audit"

# shellcheck disable=SC1090
source "$HELPER"

# New functions must exist (signature-presence guard).
for fn in job_set_steps job_step_status job_can_start job_resume_point; do
  if declare -F "$fn" >/dev/null; then
    pass "_jobs.sh exposes $fn"
  else
    fail "_jobs.sh missing $fn"
  fi
done

JY() { cat "$LINTEL_HOME/jobs/$1/job.yaml"; }   # job.yaml dumper

# ─── T1: steps[] gets populated with full contracts ──────────────────────────
echo ""
echo "[T1] steps[] populated with per-step contracts"
ID=$(job_create cycle internal-tool \
  "PLAN|consumes=design.md|produces=plan.md,spec.md,prompt.md|status=IN_PROGRESS" \
  "BUILD|consumes=plan.md|produces=|status=PENDING|blocked_until=PLAN.status == DONE" \
  "REVIEW|consumes=|produces=|status=PENDING|blocked_until=PLAN.status == DONE && BUILD.status == DONE")

if [ -n "$ID" ] && [ -f "$LINTEL_HOME/jobs/$ID/job.yaml" ]; then
  pass "job_create with step-specs produced a job"
else
  fail "job_create with step-specs produced no job"
fi

# steps[] is no longer the empty literal
if JY "$ID" | grep -qE '^steps: \[\]$'; then
  fail "steps[] is still the empty literal 'steps: []'"
else
  pass "steps[] is not the empty literal"
fi

# Every contract field is present for at least one step
for needle in '  - name: PLAN' '    consumes: \[design.md\]' \
              '    produces: \[plan.md, spec.md, prompt.md\]' \
              '    status: IN_PROGRESS' \
              '    blocked_until: PLAN.status == DONE'; do
  if JY "$ID" | grep -qE "^$needle$"; then
    pass "contract line present: ${needle#  }"
  else
    fail "contract line MISSING: ${needle#  }"
  fi
done

# Empty produces renders as []
if JY "$ID" | awk '/^  - name: BUILD/{f=1} f&&/^    produces: \[\]/{print "ok"; exit}' | grep -q ok; then
  pass "empty produces renders as []"
else
  fail "empty produces did not render as []"
fi

# job_step_status reads back a named step's status
if [ "$(job_step_status "$ID" PLAN)" = "IN_PROGRESS" ]; then
  pass "job_step_status reads PLAN=IN_PROGRESS"
else
  fail "job_step_status PLAN got '$(job_step_status "$ID" PLAN)'"
fi

# ─── T2: job_can_start enforces blocked_until ────────────────────────────────
echo ""
echo "[T2] job_can_start enforces blocked_until"

# BUILD blocked while PLAN is IN_PROGRESS
[ "$(job_can_start "$ID" BUILD)" = "no" ] \
  && pass "BUILD blocked while PLAN != DONE" \
  || fail "BUILD should be blocked while PLAN != DONE"

# A step with no blocked_until is always startable
[ "$(job_can_start "$ID" PLAN)" = "yes" ] \
  && pass "PLAN (no predicate) startable" \
  || fail "PLAN (no predicate) should be startable"

# Satisfy PLAN → BUILD unblocks, REVIEW still blocked (needs BUILD too)
job_update "$ID" PLAN DONE >/dev/null
[ "$(job_step_status "$ID" PLAN)" = "DONE" ] \
  && pass "job_update set PLAN step status DONE" \
  || fail "job_update did not set PLAN step DONE"
[ "$(job_can_start "$ID" BUILD)" = "yes" ] \
  && pass "BUILD startable once PLAN DONE" \
  || fail "BUILD should be startable once PLAN DONE"
[ "$(job_can_start "$ID" REVIEW)" = "no" ] \
  && pass "REVIEW still blocked (&&: needs BUILD too)" \
  || fail "REVIEW should still be blocked (needs BUILD)"

# Satisfy BUILD → the && conjunction now holds
job_update "$ID" BUILD DONE >/dev/null
[ "$(job_can_start "$ID" REVIEW)" = "yes" ] \
  && pass "REVIEW startable once PLAN && BUILD DONE" \
  || fail "REVIEW should be startable once both DONE"

# Return code mirrors the echo (yes→0, no→1)
job_can_start "$ID" REVIEW >/dev/null && rc=0 || rc=1
[ "$rc" -eq 0 ] && pass "job_can_start returns 0 when startable" \
                || fail "job_can_start return-code mismatch (startable)"

# ─── T3: job_resume_point returns the deepest incomplete WBS node-path ────────
echo ""
echo "[T3] job_resume_point — tree-schema node-path"
TID=$(job_create cycle internal-tool \
  "1.1.a|produces=x|status=DONE" \
  "1.1.b|produces=y|status=DONE" \
  "1.2.a|produces=z|status=PENDING" \
  "2.1.a|produces=w|status=PENDING|blocked_until=1.2.a.status == DONE")

[ "$(job_resume_point "$TID")" = "1.2.a" ] \
  && pass "resume_point = 1.2.a (first incomplete leaf)" \
  || fail "resume_point got '$(job_resume_point "$TID")', want 1.2.a"

# Completing 1.2.a unblocks + advances the resume point to 2.1.a
job_update "$TID" "1.2.a" DONE >/dev/null
[ "$(job_resume_point "$TID")" = "2.1.a" ] \
  && pass "resume_point advances to 2.1.a after 1.2.a DONE" \
  || fail "resume_point got '$(job_resume_point "$TID")', want 2.1.a"

# All-done → empty resume point (job complete; caller may fall back)
job_update "$TID" "2.1.a" DONE >/dev/null
[ -z "$(job_resume_point "$TID")" ] \
  && pass "resume_point empty when every leaf DONE" \
  || fail "resume_point should be empty when complete, got '$(job_resume_point "$TID")'"

# A blocked (un-satisfiable) leaf is skipped, not returned as resumable
BID=$(job_create cycle internal-tool \
  "1.1.a|status=DONE" \
  "1.2.a|status=PENDING|blocked_until=9.9.a.status == DONE")
[ -z "$(job_resume_point "$BID")" ] \
  && pass "blocked leaf skipped (not a resume point)" \
  || fail "blocked leaf wrongly returned: '$(job_resume_point "$BID")'"

# Un-stepped job → empty (resume skill falls back to current_step)
FID=$(job_create plan internal-tool)
[ -z "$(job_resume_point "$FID")" ] \
  && pass "un-stepped job → empty resume_point (current_step fallback)" \
  || fail "un-stepped job should yield empty resume_point"

# ─── T4: step-scoped vs legacy job_update semantics ──────────────────────────
echo ""
echo "[T4] job_update: step-scoped vs legacy top-level"

# Stepped: job_update on a populated step must NOT flip the job to a terminal
# top-level status (job stays ACTIVE; job_archive owns terminal transitions).
top_status=$(JY "$ID" | awk '/^status:/{print $2; exit}')
[ "$top_status" = "ACTIVE" ] \
  && pass "stepped job stays ACTIVE after step transitions to DONE" \
  || fail "stepped job top-level status flipped to '$top_status' (want ACTIVE)"

# Legacy un-stepped job: job_update writes the third arg to top-level status
# (the pre-Slice-3 contract the existing test relies on).
LID=$(job_create plan internal-tool)
job_update "$LID" PLAN IN_PROGRESS >/dev/null
cs=$(JY "$LID" | awk '/^current_step:/{print $2; exit}')
ls=$(JY "$LID" | awk '/^status:/{print $2; exit}')
[ "$cs" = "PLAN" ] && pass "legacy job_update sets current_step=PLAN" \
                   || fail "legacy current_step got '$cs'"
[ "$ls" = "IN_PROGRESS" ] && pass "legacy job_update sets top-level status=IN_PROGRESS" \
                          || fail "legacy top-level status got '$ls' (want IN_PROGRESS)"

# ─── Done ────────────────────────────────────────────────────────────────────
echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "jobs-steps: ALL PASS"
  exit 0
else
  echo "jobs-steps: FAILURES"
  exit 1
fi
