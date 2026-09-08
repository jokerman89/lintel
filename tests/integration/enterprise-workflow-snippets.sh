#!/usr/bin/env bash
# component: enterprise-workflow-snippets
# implements: ADR-0008, ADR-0018
# intent: docs/enterprise-profile-value.md
# constraints: synthetic packs and temporary homes only; no host activation
# last_intent_review: 2026-09-08
# tag: integration enterprise planning packs

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
export LINTEL_HOME="$TMP/home" LINTEL_REPO_ROOT="$ROOT" LINTEL_SOURCE_ROOT="$ROOT"
export LINTEL_PACKS_DIR="$LINTEL_HOME/packs" LINTEL_AUDIT_DIR="$TMP/audit"
export LINTEL_SESSION_ID="enterprise-workflow-test"
mkdir -p "$LINTEL_PACKS_DIR/base" "$TMP/audit"

# Execute the actual skill's Bash block, so a copied test implementation cannot
# conceal a regression in the instructions that agents receive.
extract_step() {
  awk -v heading="$2" '
    index($0, heading) == 1 { section=1; next }
    section && /^```bash/ { code=1; next }
    code && /^```/ { exit }
    code { sub(/\r$/, ""); print }
  ' "$1" > "$3"
  test -s "$3"
}
extract_step "$ROOT/skills/scope/SKILL.md" '### Step 4 ' "$TMP/scope.sh"
extract_step "$ROOT/skills/pack-create/SKILL.md" '### Step 5 ' "$TMP/create.sh"

# A fresh feature branch is not evidence of an existing deliverable.
git() { printf 'codex/new-feature\n'; }
scale_size=XL intent=deploy
unset has_artifact
source "$TMP/scope.sh"
test "$override_route" = DEFINE
test "${resolved_intent:-unset}" = build
scale_size=XL intent=deploy has_artifact=yes
source "$TMP/scope.sh"
test -z "$override_route"
test "$resolved_intent" = deploy
scale_size=S intent=fix has_artifact=no
source "$TMP/scope.sh"
test -z "$override_route"
test "$resolved_intent" = fix
unset -f git

cat > "$LINTEL_PACKS_DIR/base/pack.yaml" <<'EOF'
name: base
version: 1.0.0
voice:
  default_tier: internal
compliance:
  mode: hard
  hooks: [secret-scan-block]
navigation:
  default_workflow: cycle
EOF
name=team extends=base target_dir="$LINTEL_PACKS_DIR"
source "$TMP/create.sh"
# No neutral override may silently replace inherited enterprise rules.
! grep -q '^compliance:' "$target_dir/team/pack.yaml"
source "$ROOT/lib/pack-resolver.sh"
validate_pack team
printf 'team\n' > "$LINTEL_PACKS_DIR/active-pack"
test "$(resolve_pack_field compliance.mode)" = hard
test "$(resolve_pack_field compliance.hooks)" = '[secret-scan-block]'

# Blank/clone mode still copies the selected template, replacing only identity.
name=copy extends='' template="$LINTEL_PACKS_DIR/base/pack.yaml"
source "$TMP/create.sh"
validate_pack copy
test "$(_pack_yaml_field "$target_dir/copy/pack.yaml" name)" = copy
test "$(_pack_yaml_field "$target_dir/copy/pack.yaml" compliance.mode)" = hard

# Execute PLAN's real gate against a separate target repository. A newer valid
# initiative cannot conceal a missing/empty/draft explicitly selected initiative.
export LINTEL_REPO_ROOT="$TMP/project"
mkdir -p "$LINTEL_REPO_ROOT/.claude"
printf 'layout_version: 5\n' > "$LINTEL_REPO_ROOT/.claude/lintel-layout.yaml"

# SCOPE reads SENSE from the target's state, including an explicit target-relative
# override and the legacy layout. A conflicting cwd ledger must never steer it.
extract_step "$ROOT/skills/scope/SKILL.md" '### Step 1 ' "$TMP/scope-read.sh"
mkdir -p "$TMP/other/.claude/runtime/state" "$LINTEL_REPO_ROOT/.claude/runtime/state"
printf 'intent_detected: ship\n' > "$TMP/other/.claude/runtime/state/00-state.md"
printf 'intent_detected: fix\n' > "$LINTEL_REPO_ROOT/.claude/runtime/state/00-state.md"
(cd "$TMP/other" && source "$TMP/scope-read.sh" && test "$intent" = fix)
mkdir -p "$LINTEL_REPO_ROOT/selected-state"
printf 'intent_detected: deploy\n' > "$LINTEL_REPO_ROOT/selected-state/00-state.md"
(cd "$TMP/other" && export LINTEL_STATE_DIR=selected-state
 source "$TMP/scope-read.sh" && test "$intent" = deploy)
mkdir -p "$TMP/legacy/.lintel/state"
printf 'intent_detected: research\n' > "$TMP/legacy/.lintel/state/00-state.md"
(cd "$TMP/other" && export LINTEL_REPO_ROOT="$TMP/legacy"
 source "$TMP/scope-read.sh" && test "$intent" = research)

extract_step "$ROOT/skills/plan/SKILL.md" '### Step 11a ' "$TMP/plan-gate.sh"
"${PYTHON:-python3}" - "$LINTEL_REPO_ROOT" <<'PY'
import json
from pathlib import Path
import sys
repo = Path(sys.argv[1])
for name in ("selected", "newer-decoy", "draft"):
    folder = repo / ".claude/plans" / name
    folder.mkdir(parents=True)
    for member in ("spec", "plan", "prompt"):
        (folder / f"{member}.md").write_text(f"# {name} {member}\nT1 has observable acceptance.\n")
    data = dict(schema_version=1, workflow="lintel", status="DRAFT" if name == "draft" else "APPROVED")
    data.update({key: f".claude/plans/{name}/{key}.md" for key in ("spec", "plan", "prompt")})
    data["tasks"] = data["plan"]
    (folder / "work.json").write_text(json.dumps(data))
feature = repo / "specs/001-feature"
feature.mkdir(parents=True)
for member, text in (("spec", "# Approved feature requirements"), ("plan", "# Technical design"),
                     ("tasks", "- [ ] T001 Verify access denial\n")):
    (feature / f"{member}.md").write_text(text)
mapped = dict(schema_version=1, workflow="spec-kit", status="APPROVED",
              spec="specs/001-feature/spec.md", plan="specs/001-feature/plan.md",
              tasks="specs/001-feature/tasks.md", prompt=".claude/plans/selected/prompt.md")
(repo / ".claude/plans/mapped.json").write_text(json.dumps(mapped))
PY
unset LINTEL_PLAN_DIR
export LINTEL_WORK_MAP=.claude/plans/selected/work.json
(cd "$TMP" && source "$TMP/plan-gate.sh")
saved_spec=$(cat "$LINTEL_REPO_ROOT/.claude/plans/selected/spec.md")
printf ' \n' > "$LINTEL_REPO_ROOT/.claude/plans/selected/spec.md"
touch "$LINTEL_REPO_ROOT/.claude/plans/newer-decoy"
if (cd "$TMP" && source "$TMP/plan-gate.sh") > "$TMP/empty.out" 2>&1; then
  echo 'FAIL: empty selected spec was hidden by the newer decoy' >&2; exit 1
fi
grep -q 'selected spec artifact is empty' "$TMP/empty.out"
printf '%s\n' "$saved_spec" > "$LINTEL_REPO_ROOT/.claude/plans/selected/spec.md"
unset LINTEL_WORK_MAP
if (cd "$TMP" && source "$TMP/plan-gate.sh") > "$TMP/unselected.out" 2>&1; then
  echo 'FAIL: PLAN silently selected an initiative' >&2; exit 1
fi
grep -q 'select the initiative' "$TMP/unselected.out"
export LINTEL_PLAN_DIR=.claude/plans/selected
(cd "$TMP" && source "$TMP/plan-gate.sh")
export LINTEL_WORK_MAP=.claude/plans/draft/work.json
if (cd "$TMP" && source "$TMP/plan-gate.sh") > "$TMP/draft.out" 2>&1; then
  echo 'FAIL: draft selected scope was accepted' >&2; exit 1
fi
grep -q 'must be APPROVED' "$TMP/draft.out"
export LINTEL_WORK_MAP=.claude/plans/mapped.json
cp "$LINTEL_REPO_ROOT/specs/001-feature/tasks.md" "$TMP/tasks-before.md"
(cd "$TMP" && source "$TMP/plan-gate.sh")
cmp "$TMP/tasks-before.md" "$LINTEL_REPO_ROOT/specs/001-feature/tasks.md"

# Exercise SCOPE -> RESUME with their actual snippets and the real jobs helper.
# Poison the shared parent and a sibling so the old ../scope.md read selects wrongly.
extract_step "$ROOT/skills/scope/SKILL.md" '### Step 5 ' "$TMP/scope-write.sh"
extract_step "$ROOT/skills/resume/SKILL.md" '### Step 2.5 ' "$TMP/resume-job.sh"
export LINTEL_JOBS_DIR="$LINTEL_REPO_ROOT/.claude/runtime/jobs"
mkdir -p "$LINTEL_JOBS_DIR/selected-job" "$LINTEL_JOBS_DIR/other-job"
printf 'depth_schema: phased\n' > "$LINTEL_JOBS_DIR/scope.md"
printf 'depth_schema: flat\n' > "$LINTEL_JOBS_DIR/other-job/scope.md"
cat > "$LINTEL_JOBS_DIR/selected-job/job.yaml" <<'EOF'
job_id: selected-job
current_step: BUILD
steps:
  - name: 1.1.a
    status: DONE
  - name: 1.1.b
    status: PENDING
    blocked_until: 1.1.a.status == DONE
EOF
export JOB_ID=selected-job
unset LINTEL_JOB_DIR LINTEL_SCOPE_PATH
prompt_text='Implement selected feature' scale_size=L scale_amb=no resolved_intent=build
depth_schema=tree chosen_reading='selected feature' operator_answer=''
source "$TMP/scope-write.sh"
test "$scope_out" = "$LINTEL_JOBS_DIR/selected-job/scope.md"
source "$TMP/resume-job.sh"
test "$schema" = tree
test "$resume_target" = 1.1.b
test "$resume_scope" = "$scope_out"
# Explicit repo-relative handoff link overrides the job's default file.
cp "$scope_out" "$LINTEL_REPO_ROOT/.claude/plans/selected/scope.md"
printf 'depth_schema: flat\n' > "$scope_out"
export LINTEL_SCOPE_PATH=.claude/plans/selected/scope.md
source "$TMP/resume-job.sh"
test "$resume_target" = 1.1.b
export LINTEL_SCOPE_PATH=.claude/plans/missing/scope.md
if (source "$TMP/resume-job.sh") > "$TMP/missing-scope.out" 2>&1; then
  echo 'FAIL: missing explicit scope silently selected another scope' >&2; exit 1
fi
grep -q 'selected scope is missing' "$TMP/missing-scope.out"
# Legacy job without its own scope retains current_step, never the parent's schema.
unset LINTEL_SCOPE_PATH
rm "$LINTEL_JOBS_DIR/selected-job/scope.md"
source "$TMP/resume-job.sh"
test "$resume_target" = BUILD
unset JOB_ID LINTEL_PLAN_DIR

# Source/runtime roots stay distinct even when RESUME is invoked outside the target.
extract_step "$ROOT/skills/resume/SKILL.md" '### Step 1 ' "$TMP/resume-locate.sh"
(cd "$TMP" && source "$TMP/resume-locate.sh"
 test "$STATE_FILE" = "$LINTEL_REPO_ROOT/.claude/runtime/state/00-state.md")

# Run BUILD's actual ledger snippet and real state helper with a temporary path.
# An incomplete package must send a cold session back to BUILD, not REVIEW.
extract_step "$ROOT/skills/build/SKILL.md" '### Step 7 ' "$TMP/build-state.sh"
lintel_state_dir() { printf '%s/state' "$TMP"; }
plan_path="$TMP/plan.md" tasks_completed=1 tasks_blocked=1
tasks_path=specs/001-feature/tasks.md
build_status=BLOCKED build_next_action='Repair P2/T2 handler acceptance, then rerun impacted integration checks'
source "$TMP/build-state.sh"
test "$(state_last status)" = BLOCKED
test "$(state_last next_recommended)" = BUILD
test "$(state_last note)" = "$build_next_action"
test "$(state_last work_map_path)" = "$LINTEL_WORK_MAP"
test "$(state_last tasks_path)" = "$tasks_path"
build_status=DONE tasks_completed=5 tasks_blocked=0
build_next_action='Review completed implementation'
source "$TMP/build-state.sh"
test "$(state_last next_recommended)" = REVIEW
echo 'PASS: enterprise workflow snippets (selected work, scope/resume chain, inheritance, BUILD continuity)'
