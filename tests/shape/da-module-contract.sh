#!/usr/bin/env bash
# tests/shape/da-module-contract.sh
# Asserts (v4.2): DA module declares the engineering-module contract:
# workflow_root + necessity + navigation + domain block + sub-skills + new agents + hooks.
# tag: shape v4.2

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/da-module-contract.sh"
echo "==================================="

# Module skill exists
if [ -f "$REPO_ROOT/skills/da/SKILL.md" ]; then
  pass "skills/da/SKILL.md present"
else
  fail "skills/da/SKILL.md MISSING"
  exit 1
fi

# workflow_root + necessity (v4.1+ convention)
if grep -qE "^workflow_root:[[:space:]]*true" "$REPO_ROOT/skills/da/SKILL.md"; then
  pass "DA declares workflow_root: true"
else
  fail "DA missing workflow_root: true"
fi
if grep -qE "^necessity:" "$REPO_ROOT/skills/da/SKILL.md"; then
  pass "DA declares necessity"
else
  fail "DA missing necessity"
fi
if grep -qE "^gap_if_skipped:" "$REPO_ROOT/skills/da/SKILL.md"; then
  pass "DA declares gap_if_skipped"
else
  fail "DA missing gap_if_skipped"
fi

# Required navigation fields
for f in primary_intent triggers risk_level auto_mode_eligible estimated_tokens; do
  if grep -qE "^[[:space:]]+${f}:" "$REPO_ROOT/skills/da/SKILL.md"; then
    pass "DA navigation declares $f"
  else
    fail "DA navigation MISSING $f"
  fi
done

# Domain block
for f in preferences_root granularities checkpoints recovery continuation raise_help; do
  if grep -qE "^[[:space:]]+${f}:" "$REPO_ROOT/skills/da/SKILL.md"; then
    pass "DA domain block declares $f"
  else
    fail "DA domain block MISSING $f"
  fi
done

# 3 granularities (accepts block-list OR inline-flow form)
for g in full loop single; do
  if grep -qE "(^[[:space:]]+-[[:space:]]+${g}|granularities:[[:space:]]*\[[^]]*${g})" "$REPO_ROOT/skills/da/SKILL.md"; then
    pass "DA declares granularity '$g'"
  else
    fail "DA MISSING granularity '$g'"
  fi
done

# 7 sub-skills
for sub in da-schema-design da-migration-plan da-retention-policy da-query-pattern-audit da-sharding-plan da-data-contract-collision da-analytics-readiness; do
  if [ -f "$REPO_ROOT/skills/$sub/SKILL.md" ]; then
    pass "sub-skill $sub present"
  else
    fail "sub-skill $sub MISSING"
  fi
done

# 2 new agents
for agent in SchemaArchitect MigrationPlanner; do
  if [ -f "$REPO_ROOT/agents/engineering/$agent.md" ]; then
    pass "agent $agent present"
  else
    fail "agent $agent MISSING"
  fi
done

# 3 hooks
for hook in da-schema-drift-warn da-migration-irreversible-warn da-retention-violation-warn; do
  if [ -f "$REPO_ROOT/hooks/shared/$hook/HOOK.md" ] && [ -f "$REPO_ROOT/hooks/shared/$hook/run.sh" ]; then
    pass "hook $hook present (HOOK.md + run.sh)"
  else
    fail "hook $hook MISSING"
  fi
done

# Concept doc
if [ -f "$REPO_ROOT/docs/concepts/da-module.md" ]; then
  pass "concept doc da-module.md present"
else
  fail "concept doc da-module.md MISSING"
fi

# 5 checkpoints documented
for cp in data_model_complete schema_locked migration_safe retention_specified query_patterns_documented; do
  if grep -q "$cp" "$REPO_ROOT/skills/da/SKILL.md"; then
    pass "DA documents checkpoint $cp"
  else
    fail "DA MISSING checkpoint $cp"
  fi
done

# Hooks use audit_log via bin/_audit.sh
for hook in da-schema-drift-warn da-migration-irreversible-warn da-retention-violation-warn; do
  if grep -q "audit_log" "$REPO_ROOT/hooks/shared/$hook/run.sh" 2>/dev/null && grep -q "_audit.sh" "$REPO_ROOT/hooks/shared/$hook/run.sh" 2>/dev/null; then
    pass "hook $hook uses unified audit_log"
  else
    fail "hook $hook MISSING unified audit_log integration"
  fi
done

# Agents use structured cli_support
for agent in SchemaArchitect MigrationPlanner; do
  if grep -qE "^[[:space:]]+-[[:space:]]+cli:" "$REPO_ROOT/agents/engineering/$agent.md" 2>/dev/null; then
    pass "agent $agent uses structured cli_support"
  else
    fail "agent $agent uses old flat cli_support (should be list of {cli, level})"
  fi
done

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All da-module-contract assertions PASSED"; exit 0
else echo "Some da-module-contract assertions FAILED"; exit 1; fi
