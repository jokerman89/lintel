#!/usr/bin/env bash
# tests/shape/sc-module-contract.sh
# Asserts (v4.3): SC module declares the engineering-module contract.
# tag: shape v4.3

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/sc-module-contract.sh"
echo "==================================="

# Module skill
if [ -f "$REPO_ROOT/skills/sc/SKILL.md" ]; then
  pass "skills/sc/SKILL.md present"
else
  fail "skills/sc/SKILL.md MISSING"; exit 1
fi

# workflow_root + necessity + gap_if_skipped
for f in "workflow_root:[[:space:]]*true" "^necessity:" "^gap_if_skipped:"; do
  if grep -qE "$f" "$REPO_ROOT/skills/sc/SKILL.md"; then
    pass "SC declares $f"
  else
    fail "SC missing $f"
  fi
done

# Navigation required fields
for f in primary_intent triggers risk_level auto_mode_eligible estimated_tokens; do
  if grep -qE "^[[:space:]]+${f}:" "$REPO_ROOT/skills/sc/SKILL.md"; then
    pass "SC navigation declares $f"
  else
    fail "SC navigation MISSING $f"
  fi
done

# Domain block
for f in preferences_root granularities checkpoints recovery continuation raise_help; do
  if grep -qE "^[[:space:]]+${f}:" "$REPO_ROOT/skills/sc/SKILL.md"; then
    pass "SC domain declares $f"
  else
    fail "SC domain MISSING $f"
  fi
done

# 3 granularities
for g in full loop single; do
  if grep -qE "(^[[:space:]]+-[[:space:]]+${g}|granularities:[[:space:]]*\[[^]]*${g})" "$REPO_ROOT/skills/sc/SKILL.md"; then
    pass "SC granularity '$g'"
  else
    fail "SC MISSING granularity '$g'"
  fi
done

# Sub-capability dispatch table (ADR-0009 — sub-skill files collapsed into the module)
if grep -q "^## Sub-capability dispatch" "$REPO_ROOT/skills/sc/SKILL.md"; then
  pass "SC declares Sub-capability dispatch section"
else
  fail "SC MISSING Sub-capability dispatch section"
fi
for cap in threat-model secret-management auth-flow compliance-evidence audit-path dependency-security incident-runbook; do
  if grep -qE "^\|[[:space:]]*\`${cap}\`[[:space:]]*\|" "$REPO_ROOT/skills/sc/SKILL.md"; then
    pass "dispatch row '$cap' present"
  else
    fail "dispatch row '$cap' MISSING"
  fi
done

# 1 new agent
for agent in ComplianceOfficer; do
  if [ -f "$REPO_ROOT/agents/security/$agent.md" ]; then
    pass "agent $agent present"
  else
    fail "agent $agent MISSING"
  fi
done

# 3 new hooks
for hook in sc-threat-coverage-warn sc-auth-bypass-warn sc-compliance-gap-warn; do
  if [ -f "$REPO_ROOT/hooks/shared/$hook/HOOK.md" ] && [ -f "$REPO_ROOT/hooks/shared/$hook/run.sh" ]; then
    pass "hook $hook present"
  else
    fail "hook $hook MISSING"
  fi
done

# Concept doc
if [ -f "$REPO_ROOT/docs/concepts/sc-module.md" ]; then
  pass "concept doc sc-module.md present"
else
  fail "concept doc sc-module.md MISSING"
fi

# 5 checkpoints
for cp in threat_model_complete secrets_inventoried auth_flow_locked compliance_evidence_present audit_path_verified; do
  if grep -q "$cp" "$REPO_ROOT/skills/sc/SKILL.md"; then
    pass "SC checkpoint $cp"
  else
    fail "SC MISSING checkpoint $cp"
  fi
done

# Hooks use unified audit_log
for hook in sc-threat-coverage-warn sc-auth-bypass-warn sc-compliance-gap-warn; do
  if grep -q "audit_log" "$REPO_ROOT/hooks/shared/$hook/run.sh" 2>/dev/null && grep -q "_audit.sh" "$REPO_ROOT/hooks/shared/$hook/run.sh" 2>/dev/null; then
    pass "hook $hook uses unified audit_log"
  else
    fail "hook $hook MISSING unified audit_log"
  fi
done

# ComplianceOfficer uses structured cli_support
if grep -qE "^[[:space:]]+-[[:space:]]+cli:" "$REPO_ROOT/agents/security/ComplianceOfficer.md" 2>/dev/null; then
  pass "ComplianceOfficer uses structured cli_support"
else
  fail "ComplianceOfficer uses old flat cli_support"
fi

# SC color = red
if grep -qE "^color:[[:space:]]+red" "$REPO_ROOT/skills/sc/SKILL.md"; then
  pass "SC uses red module color"
else
  fail "SC does not use red"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All sc-module-contract assertions PASSED"; exit 0
else echo "Some sc-module-contract assertions FAILED"; exit 1; fi
