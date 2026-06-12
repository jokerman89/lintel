#!/usr/bin/env bash
# tests/unit/da-routing.sh
# Asserts: DA module's granularity dispatch, sub-skill enumeration, hook integration, scoring rubric.
# tag: v4.2 da-module

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DA="$REPO_ROOT/skills/da/SKILL.md"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/da-routing.sh"
echo "=========================="

[ -f "$DA" ] || { fail "skills/da/SKILL.md MISSING"; exit 1; }

# ─── Scenario 1: 3 granularity entries documented ────────────────────────
echo ""
echo "[1] Granularities documented with entries"
for g in "li:da full" "li:da loop" "li:da single"; do
  if grep -qE "/${g}" "$DA"; then
    pass "DA documents entry: /${g}"
  else
    fail "DA missing entry: /${g}"
  fi
done

# ─── Scenario 2: 7 sub-skill actions enumerated ──────────────────────────
echo ""
echo "[2] Single-action sub-skills enumerated"
for action in schema-design migration-plan retention-policy query-pattern-audit sharding-plan data-contract-collision analytics-readiness; do
  if grep -q "$action" "$DA"; then
    pass "DA enumerates --action $action"
  else
    fail "DA missing --action $action"
  fi
done

# ─── Scenario 3: Dispatch table declares agent per capability (ADR-0009) ─
echo ""
echo "[3] Dispatch rows declare agent dispatch (L-001 contract)"
declare -A CAP_AGENT=(
  ["schema-design"]="DatabaseDesigner"
  ["migration-plan"]="MigrationPlanner"
  ["retention-policy"]="DatabaseDesigner"
  ["query-pattern-audit"]="Explorer"
  ["sharding-plan"]="SchemaArchitect"
  ["data-contract-collision"]="DatabaseDesigner"
  ["analytics-readiness"]="DataPipelineDesigner"
)
for cap in "${!CAP_AGENT[@]}"; do
  expected_agent="${CAP_AGENT[$cap]}"
  if grep -E "^\|[[:space:]]*\`${cap}\`[[:space:]]*\|" "$DA" | grep -q "$expected_agent"; then
    pass "dispatch row $cap → $expected_agent"
  else
    fail "dispatch row $cap MISSING agent $expected_agent"
  fi
done

# ─── Scenario 4: 5 checkpoints have pass-criteria ───────────────────────
echo ""
echo "[4] Checkpoints have pass-criteria"
for cp in data_model_complete schema_locked migration_safe retention_specified query_patterns_documented; do
  if grep -qE "${cp}:[[:space:]]+[A-Za-z]" "$DA"; then
    pass "checkpoint $cp has pass-criterion"
  else
    fail "checkpoint $cp MISSING pass-criterion"
  fi
done

# ─── Scenario 5: 3 raise-help triggers ──────────────────────────────────
echo ""
echo "[5] Raise-help triggers documented"
for trigger in migration_against_table_above_100k_rows retention_conflicts_with_compliance_policy schema_change_breaks_3_plus_consumers; do
  if grep -q "$trigger" "$DA"; then
    pass "raise-help trigger: $trigger"
  else
    fail "raise-help trigger MISSING: $trigger"
  fi
done

# ─── Scenario 6: Each hook references DA module ─────────────────────────
echo ""
echo "[6] Hooks reference DA module"
for hook in da-schema-drift-warn da-migration-irreversible-warn da-retention-violation-warn; do
  hook_dir="$REPO_ROOT/hooks/shared/$hook"
  if [ -f "$hook_dir/HOOK.md" ] && grep -qE "da|data.architecture|/li:da" "$hook_dir/HOOK.md"; then
    pass "hook $hook references DA"
  else
    fail "hook $hook MISSING DA reference"
  fi
done

# ─── Scenario 7: 6-dim scoring rubric ──────────────────────────────────
echo ""
echo "[7] 6-dim scoring rubric"
for dim in "Data model completeness" "Schema locked" "Migration safety" "Retention specified" "Query patterns documented" "Consumer impact analyzed"; do
  if grep -qF "$dim" "$DA"; then
    pass "rubric dimension: $dim"
  else
    fail "rubric dimension MISSING: $dim"
  fi
done

# ─── Scenario 8: Profile preferences root ──────────────────────────────
echo ""
echo "[8] Profile preferences root"
if grep -qE "preferences_root:[[:space:]]+engineering\.data_architecture" "$DA"; then
  pass "preferences root: engineering.data_architecture.*"
else
  fail "preferences root MISSING or incorrect"
fi

# ─── Scenario 9: TA pattern + DA pattern consistency (engineering-modules) ─
echo ""
echo "[9] Engineering-modules pattern consistency"
if grep -q "engineering-modules.md" "$REPO_ROOT/docs/concepts/da-module.md" 2>/dev/null; then
  pass "DA concept doc references the shared engineering-modules pattern"
else
  fail "DA concept doc missing engineering-modules.md reference"
fi

# Module color convention
if grep -qE "^color:[[:space:]]+blue" "$DA"; then
  pass "DA uses blue module color (per engineering-modules convention)"
else
  fail "DA does not use blue (engineering-modules convention violated)"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All da-routing scenarios PASSED"; exit 0
else echo "Some da-routing scenarios FAILED"; exit 1; fi
