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
export LINTEL_HOME="$TMP/home" LINTEL_REPO_ROOT="$ROOT"
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

# Run BUILD's actual ledger snippet and real state helper with a temporary path.
# An incomplete package must send a cold session back to BUILD, not REVIEW.
extract_step "$ROOT/skills/build/SKILL.md" '### Step 7 ' "$TMP/build-state.sh"
lintel_state_dir() { printf '%s/state' "$TMP"; }
plan_path="$TMP/plan.md" tasks_completed=1 tasks_blocked=1
build_status=BLOCKED build_next_action='Repair P2/T2 handler acceptance, then rerun impacted integration checks'
source "$TMP/build-state.sh"
test "$(state_last status)" = BLOCKED
test "$(state_last next_recommended)" = BUILD
test "$(state_last note)" = "$build_next_action"
build_status=DONE tasks_completed=5 tasks_blocked=0
build_next_action='Review completed implementation'
source "$TMP/build-state.sh"
test "$(state_last next_recommended)" = REVIEW
echo 'PASS: enterprise workflow snippets (scope, inheritance, blocked/completed BUILD resume)'
