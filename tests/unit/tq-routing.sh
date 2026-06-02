#!/usr/bin/env bash
# tests/unit/tq-routing.sh
# Asserts: TQ module's granularity dispatch, sub-skill enumeration, hook integration, scoring rubric.
# tag: v4.5 tq-module

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TQ="$REPO_ROOT/skills/tq/SKILL.md"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/tq-routing.sh"
echo "=========================="

[ -f "$TQ" ] || { fail "skills/tq/SKILL.md MISSING"; exit 1; }

# Scenario 1: 3 granularities
echo ""; echo "[1] Granularities"
for g in "li:tq full" "li:tq loop" "li:tq single"; do
  if grep -qE "/${g}" "$TQ"; then pass "TQ /${g}"
  else fail "TQ missing /${g}"; fi
done

# Scenario 2: 7 sub-skill actions
echo ""; echo "[2] Sub-skill actions"
for action in coverage-audit perf-budget-spec contract-test-design regression-suite chaos-plan flaky-quarantine test-pyramid-review; do
  if grep -q "$action" "$TQ"; then pass "TQ --action $action"
  else fail "TQ missing --action $action"; fi
done

# Scenario 3: Sub-skill agent dispatch (L-001)
echo ""; echo "[3] Sub-skills declare agent dispatch"
declare -A SUB_AGENT=(
  ["tq-coverage-audit"]="TestRunner"
  ["tq-perf-budget-spec"]="LatencyAnalyzer"
  ["tq-contract-test-design"]="APIDesigner"
  ["tq-regression-suite"]="RegressionDetective"
  ["tq-chaos-plan"]="SecurityAuditor"
  ["tq-flaky-quarantine"]="TestRunner"
  ["tq-test-pyramid-review"]="Architect"
)
for sub in "${!SUB_AGENT[@]}"; do
  expected="${SUB_AGENT[$sub]}"
  if grep -q "$expected" "$REPO_ROOT/skills/$sub/SKILL.md" 2>/dev/null; then
    pass "$sub dispatches to $expected"
  else fail "$sub MISSING dispatch to $expected"; fi
done

# Scenario 4: 5 checkpoint pass-criteria
echo ""; echo "[4] Checkpoints pass-criteria"
for cp in coverage_targets_met perf_budgets_locked contract_tests_complete regression_suite_curated chaos_scenarios_documented; do
  if grep -qE "${cp}:[[:space:]]+[A-Za-z]" "$TQ"; then pass "$cp"
  else fail "$cp MISSING"; fi
done

# Scenario 5: 3 raise-help triggers
echo ""; echo "[5] Raise-help triggers"
for trigger in critical_path_coverage_below_threshold perf_regression_above_budget contract_break_against_active_consumer; do
  if grep -q "$trigger" "$TQ"; then pass "raise-help: $trigger"
  else fail "raise-help MISSING: $trigger"; fi
done

# Scenario 6: Hooks reference TQ
echo ""; echo "[6] Hooks reference TQ"
for hook in tq-coverage-drop-warn tq-perf-regression-warn tq-contract-break-warn; do
  if [ -f "$REPO_ROOT/hooks/shared/$hook/HOOK.md" ] && grep -qE "tq|testing|/li:tq" "$REPO_ROOT/hooks/shared/$hook/HOOK.md"; then
    pass "hook $hook references TQ"
  else fail "hook $hook MISSING TQ reference"; fi
done

# Scenario 7: 6-dim rubric
echo ""; echo "[7] 6-dim scoring rubric"
for dim in "Critical-path coverage" "Perf budgets" "Contract tests" "Regression suite" "Chaos scenarios" "Test pyramid"; do
  if grep -qF "$dim" "$TQ"; then pass "rubric: $dim"
  else fail "rubric MISSING: $dim"; fi
done

# Scenario 8: Profile prefs root
echo ""; echo "[8] Profile preferences root"
if grep -qE "preferences_root:[[:space:]]+engineering\.testing_qa" "$TQ"; then
  pass "preferences root: engineering.testing_qa.*"
else fail "preferences root MISSING"; fi

# Scenario 9: TQ color = green
echo ""; echo "[9] Module color convention"
if grep -qE "^color:[[:space:]]+green" "$TQ"; then
  pass "TQ uses green (engineering-modules convention)"
else fail "TQ color != green"; fi

# Scenario 10: Pattern consistency + final-module marker
echo ""; echo "[10] Pattern consistency + final-module status"
if grep -q "engineering-modules.md" "$REPO_ROOT/docs/concepts/tq-module.md" 2>/dev/null; then
  pass "TQ concept doc references shared pattern"
else fail "TQ concept doc MISSING engineering-modules.md reference"; fi

if grep -qi "final.*engineering-domain module\|Final engineering-domain module" "$REPO_ROOT/skills/tq/SKILL.md" 2>/dev/null; then
  pass "TQ marked as final engineering-domain module"
else fail "TQ missing final-module marker"; fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All tq-routing scenarios PASSED"; exit 0
else echo "Some tq-routing scenarios FAILED"; exit 1; fi
