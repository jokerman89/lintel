#!/usr/bin/env bash
# tests/unit/closeout-additions-present.sh
#
# Verifies v3.6 closeout additions: handoff-size-check (3.2) +
# agent-dispatch-rules doc (2.4) + the layer-model L-trio reflection (M-3) +
# memory.md M-1 reviewer-concerns tracking.
# tag: v3.6 closeout

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/closeout-additions-present.sh"
echo "========================================"

# 3.2: handoff-size-check skill
HSC="$REPO_ROOT/skills/handoff-size-check/SKILL.md"
if [ -f "$HSC" ]; then
  name=$(grep '^name:' "$HSC" | head -1 | awk '{print $2}')
  if [ "$name" = "handoff-size-check" ]; then
    pass "handoff-size-check skill present"
  else
    fail "handoff-size-check frontmatter mismatch"
  fi
  if grep -qE "500k|mode-aware|soft.*hard" "$HSC"; then
    pass "handoff-size-check references 500k cap + mode-aware envelopes"
  else
    fail "handoff-size-check missing cap-logic reference"
  fi
else
  fail "handoff-size-check SKILL.md missing"
fi

# 2.4: agent-dispatch-rules concept doc
ADR="$REPO_ROOT/docs/concepts/agent-dispatch-rules.md"
if [ -f "$ADR" ]; then
  pass "agent-dispatch-rules concept doc present (2.4)"
  for keyword in "dedicated" "inline" "SENSE" "BUILD" "REVIEW"; do
    if grep -q "$keyword" "$ADR"; then
      pass "agent-dispatch-rules references $keyword"
    else
      fail "agent-dispatch-rules missing $keyword reference"
    fi
  done
else
  fail "agent-dispatch-rules concept doc missing"
fi

# M-3: the layer-model L-trio reflection. LAYERS.md was retired to the design archive when
# docs/architecture.md replaced it as the public reference; the historical record lives on there.
LAYERS="$REPO_ROOT/.claude/engineering/design-archive/LAYERS.md"
if [ -f "$LAYERS" ]; then
  for lesson in "L-001" "L-002" "L-003"; do
    if grep -q "$lesson" "$LAYERS"; then
      pass "archived LAYERS.md reflects $lesson"
    else
      fail "archived LAYERS.md missing $lesson reflection"
    fi
  done
fi

# M-1: working-state reviewer-concerns tracking (v5 home: .claude/memory/working-state.md)
MEM="$REPO_ROOT/.claude/memory/working-state.md"
if [ -f "$MEM" ]; then
  if grep -q "reviewer-concerns" "$MEM"; then
    pass "working-state.md has reviewer-concerns tracking entry (M-1)"
  else
    fail "working-state.md missing reviewer-concerns tracking"
  fi

  if grep -q "PR #7\|PR #9" "$MEM"; then
    pass "working-state.md tracks PR #7 + #9 reviewer concerns"
  else
    fail "working-state.md missing PR #7 or PR #9 tracking"
  fi
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All closeout-additions tests PASSED"
  exit 0
else
  echo "Some closeout-additions tests FAILED"
  exit 1
fi
