#!/usr/bin/env bash
# tests/unit/sc-routing.sh
# Asserts: SC module's granularity dispatch, sub-skill enumeration, hook integration, scoring rubric.
# tag: v4.3 sc-module

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SC="$REPO_ROOT/skills/sc/SKILL.md"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/sc-routing.sh"
echo "=========================="

[ -f "$SC" ] || { fail "skills/sc/SKILL.md MISSING"; exit 1; }

# ─── Scenario 1: 3 granularities ────────────────────────────────────────
echo ""
echo "[1] Granularities documented"
for g in "li:sc full" "li:sc loop" "li:sc single"; do
  if grep -qE "/${g}" "$SC"; then
    pass "SC documents entry: /${g}"
  else
    fail "SC missing entry: /${g}"
  fi
done

# ─── Scenario 2: 7 sub-skill actions ────────────────────────────────────
echo ""
echo "[2] Sub-skill actions enumerated"
for action in threat-model secret-management auth-flow compliance-evidence audit-path dependency-security incident-runbook; do
  if grep -q "$action" "$SC"; then
    pass "SC enumerates --action $action"
  else
    fail "SC missing --action $action"
  fi
done

# ─── Scenario 3: Dispatch table declares agent per capability (ADR-0009) ─
echo ""
echo "[3] Dispatch rows declare agent dispatch (L-001)"
declare -A CAP_AGENT=(
  ["threat-model"]="ThreatModelDrafter"
  ["secret-management"]="SecurityAuditor"
  ["auth-flow"]="SecurityAuditor"
  ["compliance-evidence"]="ComplianceOfficer"
  ["audit-path"]="SecurityAuditor"
  ["dependency-security"]="DependencyAuditor"
  ["incident-runbook"]="SecurityAuditor"
)
for cap in "${!CAP_AGENT[@]}"; do
  expected="${CAP_AGENT[$cap]}"
  if grep -E "^\|[[:space:]]*\`${cap}\`[[:space:]]*\|" "$SC" | grep -q "$expected"; then
    pass "dispatch row $cap → $expected"
  else
    fail "dispatch row $cap MISSING agent $expected"
  fi
done

# ─── Scenario 4: 5 checkpoint pass-criteria ─────────────────────────────
echo ""
echo "[4] Checkpoints have pass-criteria"
for cp in threat_model_complete secrets_inventoried auth_flow_locked compliance_evidence_present audit_path_verified; do
  if grep -qE "${cp}:[[:space:]]+[A-Za-z]" "$SC"; then
    pass "checkpoint $cp has pass-criterion"
  else
    fail "checkpoint $cp MISSING pass-criterion"
  fi
done

# ─── Scenario 5: 3 raise-help triggers ──────────────────────────────────
echo ""
echo "[5] Raise-help triggers"
for trigger in high_severity_threat_without_mitigation compliance_evidence_gap_in_required_framework secret_with_no_rotation_path; do
  if grep -q "$trigger" "$SC"; then
    pass "raise-help: $trigger"
  else
    fail "raise-help MISSING: $trigger"
  fi
done

# ─── Scenario 6: Each hook references SC module ─────────────────────────
echo ""
echo "[6] Hooks reference SC module"
for hook in sc-threat-coverage-warn sc-auth-bypass-warn sc-compliance-gap-warn; do
  if [ -f "$REPO_ROOT/hooks/shared/$hook/HOOK.md" ] && grep -qE "sc|security|/li:sc" "$REPO_ROOT/hooks/shared/$hook/HOOK.md"; then
    pass "hook $hook references SC"
  else
    fail "hook $hook MISSING SC reference"
  fi
done

# ─── Scenario 7: 6-dim scoring rubric ──────────────────────────────────
echo ""
echo "[7] 6-dim scoring rubric"
for dim in "Threat model coverage" "Mitigations declared" "Secrets inventoried" "Auth flow review verdict" "Compliance evidence" "Audit path verified"; do
  if grep -qF "$dim" "$SC"; then
    pass "rubric dimension: $dim"
  else
    fail "rubric dimension MISSING: $dim"
  fi
done

# ─── Scenario 8: Profile prefs root ─────────────────────────────────────
echo ""
echo "[8] Profile preferences root"
if grep -qE "preferences_root:[[:space:]]+engineering\.security_compliance" "$SC"; then
  pass "preferences root: engineering.security_compliance.*"
else
  fail "preferences root MISSING or incorrect"
fi

# ─── Scenario 9: L-002 reuse — 6 of 7 capabilities use existing agents ──
echo ""
echo "[9] L-002: 6 of 7 capabilities reuse existing agents"
existing_agent_count=0
for cap in threat-model secret-management auth-flow audit-path dependency-security incident-runbook; do
  row=$(grep -E "^\|[[:space:]]*\`${cap}\`[[:space:]]*\|" "$SC" 2>/dev/null)
  if [ -n "$row" ] && ! echo "$row" | grep -q "ComplianceOfficer"; then
    existing_agent_count=$((existing_agent_count + 1))
  fi
done
if [ "$existing_agent_count" -ge 6 ]; then
  pass "L-002 win: $existing_agent_count of 7 capabilities dispatch to existing security agents"
else
  fail "L-002 gap: only $existing_agent_count capabilities reuse existing agents"
fi

# ─── Scenario 10: Engineering-modules pattern consistency ───────────────
echo ""
echo "[10] Engineering-modules pattern consistency"
if grep -q "engineering-modules.md" "$REPO_ROOT/docs/concepts/sc-module.md" 2>/dev/null; then
  pass "SC concept doc references shared pattern"
else
  fail "SC concept doc MISSING engineering-modules.md reference"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All sc-routing scenarios PASSED"; exit 0
else echo "Some sc-routing scenarios FAILED"; exit 1; fi
