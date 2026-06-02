#!/usr/bin/env bash
# tests/shape/tq-module-contract.sh
# Asserts (v4.5): TQ module declares the engineering-module contract.
# tag: shape v4.5

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/tq-module-contract.sh"
echo "==================================="

[ -f "$REPO_ROOT/skills/tq/SKILL.md" ] || { fail "skills/tq/SKILL.md MISSING"; exit 1; }
pass "skills/tq/SKILL.md present"

for f in "workflow_root:[[:space:]]*true" "^necessity:" "^gap_if_skipped:"; do
  if grep -qE "$f" "$REPO_ROOT/skills/tq/SKILL.md"; then pass "TQ declares $f"
  else fail "TQ missing $f"; fi
done

for f in primary_intent triggers risk_level auto_mode_eligible estimated_tokens; do
  if grep -qE "^[[:space:]]+${f}:" "$REPO_ROOT/skills/tq/SKILL.md"; then pass "TQ navigation $f"
  else fail "TQ navigation MISSING $f"; fi
done

for f in preferences_root granularities checkpoints recovery continuation raise_help; do
  if grep -qE "^[[:space:]]+${f}:" "$REPO_ROOT/skills/tq/SKILL.md"; then pass "TQ domain $f"
  else fail "TQ domain MISSING $f"; fi
done

for g in full loop single; do
  if grep -qE "(^[[:space:]]+-[[:space:]]+${g}|granularities:[[:space:]]*\[[^]]*${g})" "$REPO_ROOT/skills/tq/SKILL.md"; then
    pass "TQ granularity '$g'"
  else fail "TQ MISSING granularity '$g'"; fi
done

for sub in tq-coverage-audit tq-perf-budget-spec tq-contract-test-design tq-regression-suite tq-chaos-plan tq-flaky-quarantine tq-test-pyramid-review; do
  if [ -f "$REPO_ROOT/skills/$sub/SKILL.md" ]; then pass "sub-skill $sub present"
  else fail "sub-skill $sub MISSING"; fi
done

for agent in PerfBudgetEnforcer ContractTestArchitect; do
  if [ -f "$REPO_ROOT/agents/engineering/$agent.md" ]; then pass "agent $agent present"
  else fail "agent $agent MISSING"; fi
done

for hook in tq-coverage-drop-warn tq-perf-regression-warn tq-contract-break-warn; do
  if [ -f "$REPO_ROOT/hooks/shared/$hook/HOOK.md" ] && [ -f "$REPO_ROOT/hooks/shared/$hook/run.sh" ]; then
    pass "hook $hook present"
  else fail "hook $hook MISSING"; fi
done

if [ -f "$REPO_ROOT/docs/concepts/tq-module.md" ]; then pass "concept doc tq-module.md present"
else fail "concept doc tq-module.md MISSING"; fi

for cp in coverage_targets_met perf_budgets_locked contract_tests_complete regression_suite_curated chaos_scenarios_documented; do
  if grep -q "$cp" "$REPO_ROOT/skills/tq/SKILL.md"; then pass "TQ checkpoint $cp"
  else fail "TQ MISSING checkpoint $cp"; fi
done

# Hooks use unified audit_log
for hook in tq-coverage-drop-warn tq-perf-regression-warn tq-contract-break-warn; do
  if grep -q "audit_log" "$REPO_ROOT/hooks/shared/$hook/run.sh" 2>/dev/null && grep -q "_audit.sh" "$REPO_ROOT/hooks/shared/$hook/run.sh" 2>/dev/null; then
    pass "hook $hook uses unified audit_log"
  else fail "hook $hook MISSING unified audit_log"; fi
done

# Agents use structured cli_support
for agent in PerfBudgetEnforcer ContractTestArchitect; do
  if grep -qE "^[[:space:]]+-[[:space:]]+cli:" "$REPO_ROOT/agents/engineering/$agent.md" 2>/dev/null; then
    pass "agent $agent uses structured cli_support"
  else fail "agent $agent uses old flat cli_support"; fi
done

# TQ color = green
if grep -qE "^color:[[:space:]]+green" "$REPO_ROOT/skills/tq/SKILL.md"; then
  pass "TQ uses green module color"
else fail "TQ does not use green"; fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All tq-module-contract assertions PASSED"; exit 0
else echo "Some tq-module-contract assertions FAILED"; exit 1; fi
