#!/usr/bin/env bash
# tests/shape/build-workflow-contract.sh
#
# Structural checks on BUILD instructions. Executable helper/snippet coverage lives
# in tests/integration/enterprise-workflow-snippets.sh; this test never invokes an agent.
#
# tag: shape build-workflow-contract

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/build-workflow-contract.sh"
echo "=============================================================="

# 1. skills/build/SKILL.md exists + has expected workflow structure
BUILD_FILE="$REPO_ROOT/skills/build/SKILL.md"
if [ -f "$BUILD_FILE" ]; then
  pass "skills/build/SKILL.md present"

  # Instruction contract expectations:
  # - Workflow section present
  # - Workflow declares artifact-shape (what gets produced)
  # - Status protocol documented (DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT)
  # - Anti-patterns section present (negative-space spec)

  if grep -q "## Workflow" "$BUILD_FILE"; then
    pass "build/SKILL.md has a Workflow section"
  else
    fail "build/SKILL.md missing Workflow section"
  fi

  if grep -qE "DONE|DONE_WITH_CONCERNS|BLOCKED|NEEDS_CONTEXT" "$BUILD_FILE"; then
    pass "build/SKILL.md has status protocol"
  else
    fail "build/SKILL.md missing status protocol"
  fi

  if grep -q "## Anti-patterns" "$BUILD_FILE"; then
    pass "build/SKILL.md has an Anti-patterns section"
  else
    fail "build/SKILL.md missing Anti-patterns section"
  fi

  # v4.11: review is fail-closed on a no-op tree (superpowers #1701)
  if grep -q "3b-guard" "$BUILD_FILE" && grep -qiE "empty.*diff|diff is empty" "$BUILD_FILE"; then
    pass "build/SKILL.md has empty-diff fail-closed guard before review dispatch"
  else
    fail "build/SKILL.md missing empty-diff guard — a reviewer fed a no-op tree rubber-stamps it"
  fi
else
  fail "skills/build/SKILL.md missing — pilot cannot run"
fi

# 2. Build refers to artifact shape (not just "ships code")
if [ -f "$BUILD_FILE" ]; then
  if grep -qE "artifact|commit|test.*pass|PR" "$BUILD_FILE"; then
    pass "build/SKILL.md names the artifact-shape it produces"
  else
    fail "build/SKILL.md missing artifact-shape spec (what gets produced?)"
  fi
fi

# 3. Build references upstream phase (PLAN) for context
if [ -f "$BUILD_FILE" ]; then
  if grep -qiE "plan|design.doc|spec" "$BUILD_FILE"; then
    pass "build/SKILL.md takes upstream context (PLAN/design-doc) as input"
  else
    fail "build/SKILL.md missing upstream-context input — orphan phase risk"
  fi
fi

# 4. Evidence boundary
echo ""
echo "Evidence boundary:"
echo "  - This test validates the build-phase SHAPE spec, not runtime behavior"
echo "  - Executable workflow snippets have separate integration tests"
echo "  - Model-driven execution is not exercised by this shape check"

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All build workflow contract checks PASSED"
  exit 0
else
  echo "Some build workflow contract checks FAILED"
  exit 1
fi
