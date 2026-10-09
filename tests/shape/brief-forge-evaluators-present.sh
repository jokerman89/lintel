#!/usr/bin/env bash
# tests/shape/brief-forge-evaluators-present.sh
# Asserts the internal Brief Forge method and its unchanged evaluator boundary.
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/brief-forge-evaluators-present.sh"
echo "==============================================="

# Public skill retired; internal method retained.
if [ ! -e "$REPO_ROOT/skills/brief-forge/SKILL.md" ]; then
  pass "public brief-forge skill retired"
else
  fail "public brief-forge skill still present"
fi
if [ -f "$REPO_ROOT/skills/brief-forge/references/handoff.md" ]; then
  pass "internal handoff method present"
else
  fail "internal handoff method MISSING"
fi

# Libraries
for lib in lib/brief-forge.sh lib/brief-forge-evaluators.sh; do
  if [ -f "$REPO_ROOT/$lib" ]; then
    pass "$lib present"
  else
    fail "$lib MISSING"
  fi
done

# The generic evaluators Lintel ships by default; a pack may contribute
# additional evaluators of its own.
for e in security completeness stale; do
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

# Five hand-off kinds documented in the internal method.
for event in subagent_spawn phase_transition workflow_handoff cold_executor operator_input; do
  if grep -q "\`$event\`" "$REPO_ROOT/skills/brief-forge/references/handoff.md" 2>/dev/null; then
    pass "internal method documents hand-off kind '$event'"
  else
    fail "internal method missing hand-off kind '$event'"
  fi
done

for claim in \
  "All built-in evaluators are pass/fail checks with fixed accounting values" \
  "score protocol remains for explicitly trusted" \
  "trusted custom evaluators yield a minimum advisory score of 40–59" \
  "The deny-list is not a prompt-injection" \
  "caller must read each original acceptance item" \
  "The caller still performs dispatch"; do
  if grep -qF "$claim" "$REPO_ROOT/skills/brief-forge/references/handoff.md"; then
    pass "internal method states: $claim"
  else
    fail "internal method missing: $claim"
  fi
done

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All brief-forge-evaluators-present assertions PASSED"; exit 0
else echo "Some brief-forge-evaluators-present assertions FAILED"; exit 1; fi
