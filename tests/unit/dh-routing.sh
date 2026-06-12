#!/usr/bin/env bash
# tests/unit/dh-routing.sh
# Asserts: DH module's granularity dispatch, sub-skill enumeration, hook integration, scoring rubric.
# tag: v4.4 dh-module

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DH="$REPO_ROOT/skills/dh/SKILL.md"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/dh-routing.sh"
echo "=========================="

[ -f "$DH" ] || { fail "skills/dh/SKILL.md MISSING"; exit 1; }

# Scenario 1: granularities
echo ""; echo "[1] Granularities"
for g in "li:dh full" "li:dh loop" "li:dh single"; do
  if grep -qE "/${g}" "$DH"; then pass "DH entry /${g}"
  else fail "DH missing /${g}"; fi
done

# Scenario 2: 7 sub-skill actions
echo ""; echo "[2] Sub-skill actions"
for action in deployment-plan observability-spec sli-slo-spec cost-projection rollback-strategy capacity-headroom on-call-playbook; do
  if grep -q "$action" "$DH"; then pass "DH --action $action"
  else fail "DH missing --action $action"; fi
done

# Scenario 3: agent dispatch (dispatch-table rows per ADR-0009)
echo ""; echo "[3] Dispatch rows declare agent dispatch (L-001)"
declare -A CAP_AGENT=(
  ["deployment-plan"]="ReleaseEngineer"
  ["observability-spec"]="ObservabilityArchitect"
  ["sli-slo-spec"]="ObservabilityArchitect"
  ["cost-projection"]="CostAnalyzer"
  ["rollback-strategy"]="ReleaseEngineer"
  ["capacity-headroom"]="CapacityPlanner"
  ["on-call-playbook"]="ReleaseEngineer"
)
for cap in "${!CAP_AGENT[@]}"; do
  expected="${CAP_AGENT[$cap]}"
  if grep -E "^\|[[:space:]]*\`${cap}\`[[:space:]]*\|" "$DH" | grep -q "$expected"; then
    pass "dispatch row $cap → $expected"
  else fail "dispatch row $cap MISSING agent $expected"; fi
done

# Scenario 4: 5 checkpoint pass-criteria
echo ""; echo "[4] Checkpoints have pass-criteria"
for cp in deployment_plan_locked observability_specified slos_defined cost_projected on_call_ready; do
  if grep -qE "${cp}:[[:space:]]+[A-Za-z]" "$DH"; then pass "$cp has pass-criterion"
  else fail "$cp MISSING pass-criterion"; fi
done

# Scenario 5: 3 raise-help triggers
echo ""; echo "[5] Raise-help triggers"
for trigger in cost_projection_exceeds_budget_threshold slo_budget_below_30_day_minimum rollback_path_irreversible; do
  if grep -q "$trigger" "$DH"; then pass "raise-help: $trigger"
  else fail "raise-help MISSING: $trigger"; fi
done

# Scenario 6: Hooks reference DH
echo ""; echo "[6] Hooks reference DH"
for hook in dh-deploy-without-rollback-warn dh-observability-gap-warn dh-cost-budget-warn; do
  if [ -f "$REPO_ROOT/hooks/shared/$hook/HOOK.md" ] && grep -qE "dh|devops|/li:dh" "$REPO_ROOT/hooks/shared/$hook/HOOK.md"; then
    pass "hook $hook references DH"
  else fail "hook $hook MISSING DH reference"; fi
done

# Scenario 7: 6-dim rubric
echo ""; echo "[7] 6-dim scoring rubric"
for dim in "Deployment pattern" "Observability instrumentation" "SLI/SLO definitions" "Cost projection" "Capacity headroom" "On-call playbook"; do
  if grep -qF "$dim" "$DH"; then pass "rubric: $dim"
  else fail "rubric MISSING: $dim"; fi
done

# Scenario 8: Profile prefs root
echo ""; echo "[8] Profile preferences root"
if grep -qE "preferences_root:[[:space:]]+engineering\.devops_hosting" "$DH"; then
  pass "preferences root: engineering.devops_hosting.*"
else fail "preferences root MISSING or incorrect"; fi

# Scenario 9: L-002 — 5 of 7 capabilities use existing agents
echo ""; echo "[9] L-002: 5 of 7 reuse existing agents"
# Existing agents at this point: ReleaseEngineer, CostAnalyzer, LatencyAnalyzer, CapacityPlanner (from TA), SystemArchitect (from TA), SecurityAuditor, Architect
# New: DeploymentEngineer, ObservabilityArchitect
existing_only_caps=0
for cap in cost-projection rollback-strategy capacity-headroom on-call-playbook; do
  # These dispatch rows should have NO references to the new agents (DeploymentEngineer, ObservabilityArchitect)
  row=$(grep -E "^\|[[:space:]]*\`${cap}\`[[:space:]]*\|" "$DH" 2>/dev/null)
  if [ -n "$row" ] && ! echo "$row" | grep -qE "DeploymentEngineer|ObservabilityArchitect"; then
    existing_only_caps=$((existing_only_caps + 1))
  fi
done
if [ "$existing_only_caps" -eq 4 ]; then
  pass "L-002 win: 4 capabilities dispatch ONLY to existing agents (cost-projection, rollback-strategy, capacity-headroom, on-call-playbook)"
else
  fail "L-002 unexpected: only $existing_only_caps of 4 expected-existing-only capabilities"
fi

# Scenario 10: Pattern consistency
echo ""; echo "[10] Pattern consistency"
if grep -q "engineering-modules.md" "$REPO_ROOT/docs/concepts/dh-module.md" 2>/dev/null; then
  pass "DH concept doc references shared pattern"
else fail "DH concept doc MISSING engineering-modules.md reference"; fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All dh-routing scenarios PASSED"; exit 0
else echo "Some dh-routing scenarios FAILED"; exit 1; fi
