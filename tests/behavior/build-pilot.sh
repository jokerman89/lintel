#!/usr/bin/env bash
# tests/behavior/build-pilot.sh
#
# v3.6 cohort 2 item 1.4 REPLACED: pilot behavior test på `build`-fasen.
# Skill mandates 100% test-coverage; current 11 unit tests check presence + frontmatter
# not behavior. Behavior tests måste validera shape of artifacts producerade, ej bara
# file-existence. Pilot på build eftersom generate-pipeline dogfoodas där.
#
# Pilot scope: given minimal fixture, build-fasen should produce documented artifact-shape.
# If pilot succeeds, expand behavior-tests till other phases iteratively.
#
# tag: v3.6 cohort-2 behavior-test-pilot

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/behavior/build-pilot.sh — v3.6 cohort 2 item 1.4 pilot"
echo "=============================================================="

# 1. skills/build/SKILL.md exists + has expected workflow structure
BUILD_FILE="$REPO_ROOT/skills/build/SKILL.md"
if [ -f "$BUILD_FILE" ]; then
  pass "skills/build/SKILL.md present"

  # Behavior expectations från spec:
  # - Workflow section present
  # - Workflow declarerar artifact-shape (what gets produced)
  # - Status protocol documented (DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT)
  # - Anti-patterns section present (negative-space spec)

  if grep -q "## Workflow" "$BUILD_FILE"; then
    pass "build/SKILL.md har Workflow-sektion"
  else
    fail "build/SKILL.md saknar Workflow-sektion"
  fi

  if grep -qE "DONE|DONE_WITH_CONCERNS|BLOCKED|NEEDS_CONTEXT" "$BUILD_FILE"; then
    pass "build/SKILL.md har status protocol"
  else
    fail "build/SKILL.md saknar status protocol"
  fi

  if grep -q "## Anti-patterns" "$BUILD_FILE"; then
    pass "build/SKILL.md har Anti-patterns-sektion"
  else
    fail "build/SKILL.md saknar Anti-patterns-sektion"
  fi

  # v4.11: review is fail-closed on a no-op tree (superpowers #1701)
  if grep -q "3b-guard" "$BUILD_FILE" && grep -qi "empty.*diff\|diff is empty" "$BUILD_FILE"; then
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
    pass "build/SKILL.md namnger producerad artifact-shape"
  else
    fail "build/SKILL.md saknar artifact-shape-spec (vad produceras?)"
  fi
fi

# 3. Build references upstream phase (PLAN) for context
if [ -f "$BUILD_FILE" ]; then
  if grep -qiE "plan|design.doc|spec" "$BUILD_FILE"; then
    pass "build/SKILL.md tar upstream context (PLAN/design-doc) som input"
  else
    fail "build/SKILL.md saknar upstream-context-input — orphan phase risk"
  fi
fi

# 4. Pilot scope validation — denna är ETT phase. Future expansion till other phases:
echo ""
echo "Pilot-scope notes:"
echo "  - Detta test validates build-phase SHAPE-spec, ej runtime behavior"
echo "  - Runtime behavior-tests kräver fixture + skill-execution sandbox (separat infrastructure)"
echo "  - Om pilot passes → expand pattern till andra phases (sense, define, discover, etc) i v3.6+"

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All behavior-pilot tests PASSED"
  exit 0
else
  echo "Some behavior-pilot tests FAILED"
  exit 1
fi
