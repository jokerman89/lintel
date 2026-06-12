#!/usr/bin/env bash
# tests/shape/ta-module-contract.sh
# Asserts (v4.1, dispatch-table form per ADR-0009): TA module declares the engineering-module
# contract: workflow_root + navigation + domain block + sub-capability dispatch table + new
# agents + hooks.
# tag: shape v4.1

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/ta-module-contract.sh"
echo "==================================="

# Module skill exists
if [ -f "$REPO_ROOT/skills/ta/SKILL.md" ]; then
  pass "skills/ta/SKILL.md present"
else
  fail "skills/ta/SKILL.md MISSING"
  exit 1
fi

# workflow_root: true
if grep -qE "^workflow_root:[[:space:]]*true" "$REPO_ROOT/skills/ta/SKILL.md"; then
  pass "TA declares workflow_root: true"
else
  fail "TA missing workflow_root: true"
fi

# Required navigation fields
for f in primary_intent triggers risk_level auto_mode_eligible estimated_tokens; do
  if grep -qE "^[[:space:]]+${f}:" "$REPO_ROOT/skills/ta/SKILL.md"; then
    pass "TA navigation declares $f"
  else
    fail "TA navigation MISSING $f"
  fi
done

# Domain block (engineering-module contract)
for f in preferences_root granularities checkpoints recovery continuation raise_help; do
  if grep -qE "^[[:space:]]+${f}:" "$REPO_ROOT/skills/ta/SKILL.md"; then
    pass "TA domain block declares $f"
  else
    fail "TA domain block MISSING $f"
  fi
done

# 3 granularities documented (accepts block-list OR inline-flow form)
for g in full loop single; do
  if grep -qE "(^[[:space:]]+-[[:space:]]+${g}|granularities:[[:space:]]*\[[^]]*${g})" "$REPO_ROOT/skills/ta/SKILL.md"; then
    pass "TA declares granularity '$g'"
  else
    fail "TA MISSING granularity '$g'"
  fi
done

# Sub-capability dispatch table (ADR-0009 — sub-skill files collapsed into the module)
if grep -q "^## Sub-capability dispatch" "$REPO_ROOT/skills/ta/SKILL.md"; then
  pass "TA declares Sub-capability dispatch section"
else
  fail "TA MISSING Sub-capability dispatch section"
fi
for cap in api-design dependency-graph complexity-audit boundary-review scaling-plan contract-collision quality-attributes; do
  if grep -qE "^\|[[:space:]]*\`${cap}\`[[:space:]]*\|" "$REPO_ROOT/skills/ta/SKILL.md"; then
    pass "dispatch row '$cap' present"
  else
    fail "dispatch row '$cap' MISSING"
  fi
done

# 2 new agents present
for agent in SystemArchitect CapacityPlanner; do
  if [ -f "$REPO_ROOT/agents/engineering/$agent.md" ]; then
    pass "agent $agent present"
  else
    fail "agent $agent MISSING"
  fi
done

# 3 hooks present
for hook in ta-arch-drift-warn ta-contract-collision-warn ta-complexity-budget-warn; do
  if [ -f "$REPO_ROOT/hooks/shared/$hook/HOOK.md" ] && [ -f "$REPO_ROOT/hooks/shared/$hook/run.sh" ]; then
    pass "hook $hook present (HOOK.md + run.sh)"
  else
    fail "hook $hook MISSING"
  fi
done

# Concept docs present
for doc in docs/concepts/engineering-modules.md docs/concepts/ta-module.md; do
  if [ -f "$REPO_ROOT/$doc" ]; then
    pass "concept doc $doc present"
  else
    fail "concept doc $doc MISSING"
  fi
done

# 5 checkpoints documented
for cp in discovery_complete decision_documented contract_locked complexity_within_budget non_functionals_specified; do
  if grep -q "$cp" "$REPO_ROOT/skills/ta/SKILL.md"; then
    pass "TA documents checkpoint $cp"
  else
    fail "TA MISSING checkpoint $cp"
  fi
done

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All ta-module-contract assertions PASSED"; exit 0
else echo "Some ta-module-contract assertions FAILED"; exit 1; fi
