#!/usr/bin/env bash
# tests/shape/workflow-root-has-navigation.sh
# Asserts (NEW v4.0): every workflow_root: true skill declares a navigation: block.
# tag: shape v4.0

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

# Each must declare navigation: block
# Phase 1 enforcement is documentation-only (v4.0 Chapter 1 §2.5 mandates the block
# at spine-load time; spine extraction ships in Phase 2 where the actual rejection
# fires). For Phase 1 we surface MISSING navigation as WARNING, not FAIL.
MISSING=()
for f in "${WR_SKILLS[@]}"; do
  if grep -qE "^navigation:" "$f"; then
    pass "navigation: block present in $(basename "$(dirname "$f")")/SKILL.md"
  else
    echo "  WARN: navigation: block MISSING in $(basename "$(dirname "$f")")/SKILL.md (will block in Phase 2)"
    MISSING+=("$f")
  fi
done

if [ "${#MISSING[@]}" -gt 0 ]; then
  echo ""
  echo "  Phase 1 grace: ${#MISSING[@]} workflow_root skill(s) missing navigation: block."
  echo "  Phase 2 spine-load enforcement will reject these. Schedule migration."
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All workflow-root-has-navigation assertions PASSED (warnings ok in Phase 1)"; exit 0
else echo "Some workflow-root-has-navigation assertions FAILED"; exit 1; fi
