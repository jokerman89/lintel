#!/usr/bin/env bash
# tests/shape/workflow-root-has-navigation.sh
# Asserts (v4.0 Phase 2): every workflow_root: true skill declares a navigation: block.
# tag: shape v4.0
#
# Phase 1 (PR #36) shipped this in WARN mode as grace.
# Phase 2 (this branch) tightens to FAIL — workflow_root contract is mandatory.

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/workflow-root-has-navigation.sh"
echo "============================================="

# Find all workflow_root: true skills
WR_SKILLS=()
while IFS= read -r f; do
  WR_SKILLS+=("$f")
done < <(grep -rlE "^workflow_root:[[:space:]]*true" "$REPO_ROOT/skills" 2>/dev/null)

if [ "${#WR_SKILLS[@]}" -eq 0 ]; then
  fail "No workflow_root: true skills found (expected cycle + plan at minimum)"
else
  pass "Found ${#WR_SKILLS[@]} workflow_root: true skills"
fi

# Each MUST declare navigation: block (Phase 2 hard requirement)
for f in "${WR_SKILLS[@]}"; do
  skill_name=$(basename "$(dirname "$f")")
  if grep -qE "^navigation:" "$f"; then
    pass "navigation: block present in $skill_name/SKILL.md"

    # Phase 2 sub-checks: required nav fields
    for required in primary_intent triggers risk_level; do
      if grep -qE "^[[:space:]]+${required}:" "$f"; then
        pass "  required nav field '$required' present in $skill_name"
      else
        fail "  required nav field '$required' MISSING in $skill_name/SKILL.md"
      fi
    done
  else
    fail "navigation: block MISSING in $skill_name/SKILL.md (Phase 2 mandatory)"
  fi
done

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All workflow-root-has-navigation assertions PASSED"; exit 0
else echo "Some workflow-root-has-navigation assertions FAILED"; exit 1; fi
