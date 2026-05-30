#!/usr/bin/env bash
# tests/shape/brief-forge-evaluators-present.sh
# Asserts (v4.0 Phase 3): brief-forge skill exists + lib exists + 5 evaluators
# declared + evaluators framework dispatches via run_evaluator.
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/brief-forge-evaluators-present.sh"
echo "==============================================="

# Skill
if [ -f "$REPO_ROOT/skills/brief-forge/SKILL.md" ]; then
  pass "skills/brief-forge/SKILL.md present"
else
  fail "skills/brief-forge/SKILL.md MISSING"
fi

# Libraries
for lib in lib/brief-forge.sh lib/brief-forge-evaluators.sh; do
  if [ -f "$REPO_ROOT/$lib" ]; then
    pass "$lib present"
  else
    fail "$lib MISSING"
  fi
done

# 5 default evaluators
for e in security completeness stale sdl_compliance trailblazer_alignment; do
  if grep -qE "^evaluator_${e}\(\)" "$REPO_ROOT/lib/brief-forge-evaluators.sh" 2>/dev/null; then
    pass "evaluator_${e} declared"
  else
    fail "evaluator_${e} MISSING"
  fi
done

# Dispatcher
if grep -qE "^run_evaluator\(\)" "$REPO_ROOT/lib/brief-forge-evaluators.sh" 2>/dev/null; then
  pass "run_evaluator dispatcher present"
else
  fail "run_evaluator dispatcher MISSING"
fi

# Envelope construction helpers
for fn in forge_envelope_head forge_envelope_body forge_envelope_tail generate_envelope_id write_bypass_audit aggregate_evaluator_scores; do
  if grep -qE "^${fn}\(\)" "$REPO_ROOT/lib/brief-forge.sh" 2>/dev/null; then
    pass "brief-forge.sh exports $fn()"
  else
    fail "brief-forge.sh MISSING $fn()"
  fi
done

# 5 hand-off events documented in skill
for event in subagent_spawn phase_transition workflow_handoff cold_executor operator_input; do
  if grep -q "$event" "$REPO_ROOT/skills/brief-forge/SKILL.md" 2>/dev/null; then
    pass "skill documents hand-off event '$event'"
  else
    fail "skill missing hand-off event '$event'"
  fi
done

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All brief-forge-evaluators-present assertions PASSED"; exit 0
else echo "Some brief-forge-evaluators-present assertions FAILED"; exit 1; fi
