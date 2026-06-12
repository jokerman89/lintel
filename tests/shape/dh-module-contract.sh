#!/usr/bin/env bash
# tests/shape/dh-module-contract.sh
# Asserts (v4.4): DH module declares the engineering-module contract.
# tag: shape v4.4

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/dh-module-contract.sh"
echo "==================================="

[ -f "$REPO_ROOT/skills/dh/SKILL.md" ] || { fail "skills/dh/SKILL.md MISSING"; exit 1; }
pass "skills/dh/SKILL.md present"

# workflow_root + necessity + gap_if_skipped
for f in "workflow_root:[[:space:]]*true" "^necessity:" "^gap_if_skipped:"; do
  if grep -qE "$f" "$REPO_ROOT/skills/dh/SKILL.md"; then pass "DH declares $f"
  else fail "DH missing $f"; fi
done

# Required navigation fields
for f in primary_intent triggers risk_level auto_mode_eligible estimated_tokens; do
  if grep -qE "^[[:space:]]+${f}:" "$REPO_ROOT/skills/dh/SKILL.md"; then pass "DH navigation $f"
  else fail "DH navigation MISSING $f"; fi
done

# Domain block
for f in preferences_root granularities checkpoints recovery continuation raise_help; do
  if grep -qE "^[[:space:]]+${f}:" "$REPO_ROOT/skills/dh/SKILL.md"; then pass "DH domain $f"
  else fail "DH domain MISSING $f"; fi
done

# 3 granularities
for g in full loop single; do
  if grep -qE "(^[[:space:]]+-[[:space:]]+${g}|granularities:[[:space:]]*\[[^]]*${g})" "$REPO_ROOT/skills/dh/SKILL.md"; then
    pass "DH granularity '$g'"
  else fail "DH MISSING granularity '$g'"; fi
done

# Sub-capability dispatch table (ADR-0009 — sub-skill files collapsed into the module)
if grep -q "^## Sub-capability dispatch" "$REPO_ROOT/skills/dh/SKILL.md"; then
  pass "DH declares Sub-capability dispatch section"
else fail "DH MISSING Sub-capability dispatch section"; fi
for cap in deployment-plan observability-spec sli-slo-spec cost-projection rollback-strategy capacity-headroom on-call-playbook; do
  if grep -qE "^\|[[:space:]]*\`${cap}\`[[:space:]]*\|" "$REPO_ROOT/skills/dh/SKILL.md"; then pass "dispatch row '$cap' present"
  else fail "dispatch row '$cap' MISSING"; fi
done

# 2 new agents
for agent in DeploymentEngineer ObservabilityArchitect; do
  if [ -f "$REPO_ROOT/agents/engineering/$agent.md" ]; then pass "agent $agent present"
  else fail "agent $agent MISSING"; fi
done

# 3 new hooks
for hook in dh-deploy-without-rollback-warn dh-observability-gap-warn dh-cost-budget-warn; do
  if [ -f "$REPO_ROOT/hooks/shared/$hook/HOOK.md" ] && [ -f "$REPO_ROOT/hooks/shared/$hook/run.sh" ]; then
    pass "hook $hook present"
  else fail "hook $hook MISSING"; fi
done

# Concept doc
if [ -f "$REPO_ROOT/docs/concepts/dh-module.md" ]; then pass "concept doc dh-module.md present"
else fail "concept doc dh-module.md MISSING"; fi

# 5 checkpoints
for cp in deployment_plan_locked observability_specified slos_defined cost_projected on_call_ready; do
  if grep -q "$cp" "$REPO_ROOT/skills/dh/SKILL.md"; then pass "DH checkpoint $cp"
  else fail "DH MISSING checkpoint $cp"; fi
done

# Hooks use unified audit_log
for hook in dh-deploy-without-rollback-warn dh-observability-gap-warn dh-cost-budget-warn; do
  if grep -q "audit_log" "$REPO_ROOT/hooks/shared/$hook/run.sh" 2>/dev/null && grep -q "_audit.sh" "$REPO_ROOT/hooks/shared/$hook/run.sh" 2>/dev/null; then
    pass "hook $hook uses unified audit_log"
  else fail "hook $hook MISSING unified audit_log"; fi
done

# Agents use structured cli_support
for agent in DeploymentEngineer ObservabilityArchitect; do
  if grep -qE "^[[:space:]]+-[[:space:]]+cli:" "$REPO_ROOT/agents/engineering/$agent.md" 2>/dev/null; then
    pass "agent $agent uses structured cli_support"
  else fail "agent $agent uses old flat cli_support"; fi
done

# DH color = purple
if grep -qE "^color:[[:space:]]+purple" "$REPO_ROOT/skills/dh/SKILL.md"; then
  pass "DH uses purple module color"
else fail "DH does not use purple"; fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All dh-module-contract assertions PASSED"; exit 0
else echo "Some dh-module-contract assertions FAILED"; exit 1; fi
