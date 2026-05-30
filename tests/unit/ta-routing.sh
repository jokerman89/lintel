#!/usr/bin/env bash
# tests/unit/ta-routing.sh
# Asserts: TA module's granularity dispatch documents all required entries,
# sub-skill enumeration covers all 7 actions, hooks integrate correctly.
# tag: v4.1 ta-module

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TA="$REPO_ROOT/skills/ta/SKILL.md"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/ta-routing.sh"
echo "=========================="

[ -f "$TA" ] || { fail "skills/ta/SKILL.md MISSING"; exit 1; }

# ─── Scenario 1: All 3 granularities have documented entries + outputs ──
echo ""
echo "[1] Granularities documented with entries + outputs"
for g in "li:ta full" "li:ta loop" "li:ta single"; do
  if grep -qE "\`?/${g}" "$TA"; then
    pass "TA documents entry: /${g}"
  else
    fail "TA missing entry: /${g}"
  fi
done

# ─── Scenario 2: All 7 sub-skill actions enumerated ─────────────────────
echo ""
echo "[2] Single-action sub-skills enumerated"
for action in api-design dependency-graph complexity-audit boundary-review scaling-plan contract-collision quality-attributes; do
  if grep -q "$action" "$TA"; then
    pass "TA enumerates --action $action"
  else
    fail "TA missing --action $action"
  fi
done

# ─── Scenario 3: Each sub-skill documents its agent dispatch ────────────
echo ""
echo "[3] Sub-skills declare agent dispatch (L-001 contract)"
declare -A SUB_AGENT=(
  ["ta-api-design"]="APIDesigner"
  ["ta-dependency-graph"]="Explorer"
  ["ta-complexity-audit"]="Architect"
  ["ta-boundary-review"]="BackendArchitect"
  ["ta-scaling-plan"]="CapacityPlanner"
  ["ta-contract-collision"]="APIDesigner"
  ["ta-quality-attributes"]="SystemArchitect"
)
for sub in "${!SUB_AGENT[@]}"; do
  expected_agent="${SUB_AGENT[$sub]}"
  if grep -q "$expected_agent" "$REPO_ROOT/skills/$sub/SKILL.md" 2>/dev/null; then
    pass "$sub dispatches to $expected_agent"
  else
    fail "$sub MISSING dispatch to $expected_agent"
  fi
done

# ─── Scenario 4: 5 checkpoints have pass-criteria documented ────────────
echo ""
echo "[4] Checkpoints have pass-criteria"
for cp in discovery_complete decision_documented contract_locked complexity_within_budget non_functionals_specified; do
  if grep -qE "${cp}:[[:space:]]+[A-Za-z]" "$TA"; then
    pass "checkpoint $cp has pass-criterion"
  else
    fail "checkpoint $cp MISSING pass-criterion"
  fi
done

# ─── Scenario 5: 3 raise-help triggers documented ───────────────────────
echo ""
echo "[5] Raise-help triggers documented"
for trigger in new_dependency_tree_shake_reveals_unknown_service adr_alternatives_within_5_percent contract_change_breaks_3_plus_consumers; do
  if grep -q "$trigger" "$TA"; then
    pass "raise-help trigger: $trigger"
  else
    fail "raise-help trigger MISSING: $trigger"
  fi
done

# ─── Scenario 6: Each hook references the TA module ─────────────────────
echo ""
echo "[6] Hooks reference TA module (integration documented)"
for hook in ta-arch-drift-warn ta-contract-collision-warn ta-complexity-budget-warn; do
  hook_dir="$REPO_ROOT/hooks/shared/$hook"
  if [ -f "$hook_dir/HOOK.md" ] && grep -qE "ta|tech.architecture" "$hook_dir/HOOK.md"; then
    pass "hook $hook references TA"
  else
    fail "hook $hook MISSING TA reference"
  fi
done

# ─── Scenario 7: 6-dim scoring rubric documented ────────────────────────
echo ""
echo "[7] 6-dim scoring rubric"
for dim in "Decisions documented" "Contracts locked" "Complexity within budget" "Non-functionals specified" "Consumer impact analyzed" "Alternatives considered"; do
  if grep -qF "$dim" "$TA"; then
    pass "rubric dimension: $dim"
  else
    fail "rubric dimension MISSING: $dim"
  fi
done

# ─── Scenario 8: Profile preferences root declared ──────────────────────
echo ""
echo "[8] Profile preferences root"
if grep -qE "preferences_root:[[:space:]]+engineering\.tech_architecture" "$TA"; then
  pass "preferences root: engineering.tech_architecture.*"
else
  fail "preferences root MISSING or incorrect"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All ta-routing scenarios PASSED"; exit 0
else echo "Some ta-routing scenarios FAILED"; exit 1; fi
