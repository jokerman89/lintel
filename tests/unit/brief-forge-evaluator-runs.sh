#!/usr/bin/env bash
# tests/unit/brief-forge-evaluator-runs.sh
# Asserts: all three built-in evaluators execute, return well-formed JSON,
# identify documented failure patterns, and the skill's three-level hand-off
# policy resolver reaches both default-enabled and fail-closed paths.
# tag: v4.0 phase-3 brief-forge

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EVALS="$REPO_ROOT/lib/brief-forge-evaluators.sh"
FORGE="$REPO_ROOT/lib/brief-forge.sh"
SKILL="$REPO_ROOT/skills/brief-forge/SKILL.md"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/brief-forge-evaluator-runs.sh"
echo "=========================================="

for f in "$EVALS" "$FORGE" "$SKILL"; do
  [ -f "$f" ] || { fail "$f MISSING"; exit 1; }
done

# Sandbox the audit seams BEFORE sourcing: lib/brief-forge.sh sources bin/_audit.sh,
# which mkdirs $LINTEL_AUDIT_DIR at source time — without these seams the test
# touches the real ~/.lintel/audit.
SANDBOX=$(mktemp -d)
export LINTEL_HOME="$SANDBOX/lintel-home"
export LINTEL_AUDIT_DIR="$SANDBOX/audit"
export LINTEL_PACKS_DIR="$SANDBOX/packs"
export LINTEL_ACTIVE_PACK_FILE="$LINTEL_PACKS_DIR/active-pack"
export LINTEL_SOURCE_ROOT="$REPO_ROOT"
export LINTEL_REPO_ROOT="$REPO_ROOT"
mkdir -p "$LINTEL_PACKS_DIR"

# shellcheck disable=SC1090
source "$EVALS"
# shellcheck disable=SC1090
source "$FORGE"

TMP=$(mktemp)
trap 'rm -rf "$SANDBOX"; rm -f "$TMP" "$TMP.evil" "$TMP.bad-brief" "$TMP.tb"' EXIT

# ─── Scenario 1: clean brief envelope passes all evaluators ─────────────
echo ""
echo "[1] Clean brief envelope → all evaluators return high scores"
cat > "$TMP" <<'EOF'
head:
  envelope_id: "01J-test"
  envelope_schema_version: "1"
  kind: subagent_spawn
  from: plan
  to: PlanReviewer
  issued_at: "2026-05-29T15:00:00Z"
  voice_tier: internal
body:
  content_type: brief
  content:
    task: Review the plan
    constraints: [no scope creep]
    acceptance: [reviewer surfaces concerns or APPROVES]
tail:
  completeness_score: 0
  evaluators_run: []
  escape_hatches: []
  audit_pointer: /tmp/x.jsonl
EOF

for e in security completeness stale; do
  result=$(run_evaluator "$e" "$TMP")
  score=$(printf '%s' "$result" | grep -oE '"score"[[:space:]]*:[[:space:]]*[0-9]+' | head -1 | grep -oE '[0-9]+')
  if [ -n "$score" ] && [ "$score" -ge 90 ]; then
    pass "$e clean envelope → score=$score"
  else
    fail "$e clean envelope → score=$score (expected ≥90)"
  fi
done

# ─── Scenario 2: secret in body → security low ──────────────────────────
echo ""
echo "[2] Envelope with API key → security low"
cat > "$TMP.evil" <<'EOF'
head:
  envelope_id: "01J-bad"
  envelope_schema_version: "1"
  kind: subagent_spawn
  from: plan
  to: PlanReviewer
  issued_at: "2026-05-29T15:00:00Z"
body:
  content_type: brief
  content:
    task: Use this key sk-abcdefghijklmnopqrstuvwxyz1234567890ABCDEFG to call API
    constraints: [test]
    acceptance: [done]
tail:
  completeness_score: 0
  evaluators_run: []
  escape_hatches: []
  audit_pointer: /tmp/x.jsonl
EOF

result=$(run_evaluator security "$TMP.evil")
score=$(printf '%s' "$result" | grep -oE '"score"[[:space:]]*:[[:space:]]*[0-9]+' | head -1 | grep -oE '[0-9]+')
if [ -n "$score" ] && [ "$score" -le 60 ]; then
  pass "security caught API-key pattern → score=$score"
else
  fail "security missed API-key pattern → score=$score (expected ≤60)"
fi

# ─── Scenario 3: missing required brief field → completeness low ────────
echo ""
echo "[3] Brief missing acceptance field → completeness low"
cat > "$TMP.bad-brief" <<'EOF'
head:
  envelope_id: "01J-incomplete"
  envelope_schema_version: "1"
  kind: subagent_spawn
  from: plan
  to: PlanReviewer
  issued_at: "2026-05-29T15:00:00Z"
body:
  content_type: brief
  content:
    task: Do something
    constraints: [vague]
tail:
  completeness_score: 0
  evaluators_run: []
  escape_hatches: []
  audit_pointer: /tmp/x.jsonl
EOF

result=$(run_evaluator completeness "$TMP.bad-brief")
score=$(printf '%s' "$result" | grep -oE '"score"[[:space:]]*:[[:space:]]*[0-9]+' | head -1 | grep -oE '[0-9]+')
if [ -n "$score" ] && [ "$score" -le 80 ]; then
  pass "completeness caught missing acceptance → score=$score"
else
  fail "completeness missed gap → score=$score (expected ≤80)"
fi

# ─── Scenario 4: nested hand-off policy and unknown evaluator gate ──────
echo ""
echo "[4] Nested hand-off policy → default enabled; unknown evaluator blocks"

# The skill now invokes the same library functions instead of duplicating a recipe.
grep -q 'forge_handoff "$@"' "$SKILL" || { fail "skill does not invoke the shared release gate"; exit 1; }

kind=subagent_spawn
from=plan
to=PlanReviewer
policy_mismatch=0
for expectation in \
  'on_subagent_spawn|true|security,stale' \
  'on_phase_transition|true|completeness' \
  'on_workflow_handoff|true|completeness' \
  'on_cold_executor|true|security,completeness' \
  'on_operator_input|false|'; do
  IFS='|' read -r policy_event expected_enabled expected_evaluators <<< "$expectation"
  actual_enabled=$(resolve_brief_forge_handoff_field "$policy_event" enabled)
  actual_evaluators=$(resolve_brief_forge_handoff_field "$policy_event" evaluators | tr -d '[][:space:]')
  if [ "$actual_enabled" != "$expected_enabled" ] || \
     [ "$actual_evaluators" != "$expected_evaluators" ]; then
    fail "$policy_event mismatch → enabled=$actual_enabled evaluators=$actual_evaluators"
    policy_mismatch=1
  fi
done

default_evaluators=$(resolve_brief_forge_handoff_field on_subagent_spawn evaluators | tr -d '[][:space:]')
default_bypass=$(resolve_brief_forge_handoff_field cold_path_bypass eligible_skills | tr -d '[][:space:]')
if [ "$policy_mismatch" -eq 0 ] && [ -z "$default_bypass" ] && \
   validate_brief_forge_evaluators "$default_evaluators"; then
  pass "all default event policies and cold-path bypass resolve from the nested block"
else
  fail "default nested policy or evaluator validation is unreachable"
fi

mkdir -p "$LINTEL_PACKS_DIR/unknown-evaluator"
cat > "$LINTEL_PACKS_DIR/unknown-evaluator/pack.yaml" <<'EOF'
schema_version: "1"
name: unknown-evaluator
version: 1.0.0
voice:
  default_tier: internal
compliance:
  mode: advisory
navigation:
  default_workflow: cycle
brief_forge_handoffs:
  on_subagent_spawn:
    enabled: true
    evaluators: [security, not_loaded]
  budget_tokens: 5000
EOF
printf '%s\n' unknown-evaluator > "$LINTEL_ACTIVE_PACK_FILE"
clear_pack_cache

custom_enabled=$(resolve_brief_forge_handoff_field on_subagent_spawn enabled)
custom_evaluators=$(resolve_brief_forge_handoff_field on_subagent_spawn evaluators | tr -d '[][:space:]')
unknown_output="$SANDBOX/unknown-evaluator.out"
if [ "$custom_enabled" != "true" ] || [ "$custom_evaluators" != "security,not_loaded" ]; then
  fail "custom nested policy unresolved → enabled=$custom_enabled evaluators=$custom_evaluators"
elif validate_brief_forge_evaluators "$custom_evaluators" >"$unknown_output" 2>&1; then
  fail "unknown evaluator did not block the hand-off"
elif grep -q "unknown evaluator 'not_loaded'" "$unknown_output" && \
     grep -q '"kind":"brief_forge_blocked"' "$LINTEL_AUDIT_DIR/brief-forge.jsonl" && \
     grep -q '"evaluator":"not_loaded"' "$LINTEL_AUDIT_DIR/brief-forge.jsonl"; then
  pass "unknown configured evaluator blocks before envelope construction and is audited"
else
  fail "unknown evaluator blocked without the required diagnostic or audit evidence"
fi

# ─── Scenario 5: envelope construction roundtrip ─────────────────────────
echo ""
echo "[5] Envelope construction roundtrip via forge helpers"
content_file=$(mktemp)
cat > "$content_file" <<'EOF'
task: Sample task
constraints: [c1]
acceptance: [a1]
EOF

head_out=$(forge_envelope_head subagent_spawn plan PlanReviewer)
if printf '%s' "$head_out" | grep -qE '^head:' && \
   printf '%s' "$head_out" | grep -qE 'envelope_id:' && \
   printf '%s' "$head_out" | grep -qE 'kind: "?subagent_spawn'; then
  pass "forge_envelope_head produces valid HEAD"
else
  fail "forge_envelope_head output invalid"
fi

body_out=$(forge_envelope_body brief "$content_file")
if printf '%s' "$body_out" | grep -qE '^body:' && \
   printf '%s' "$body_out" | grep -qE 'content_type: "?brief'; then
  pass "forge_envelope_body produces valid BODY"
else
  fail "forge_envelope_body output invalid"
fi

rm -f "$content_file"

# ─── Scenario 6: aggregate_evaluator_scores returns minimum ──────────────
echo ""
echo "[6] aggregate_evaluator_scores returns minimum"
agg=$(aggregate_evaluator_scores 'security:{"score":95}' 'completeness:{"score":50}' 'stale:{"score":90}')
if [ "$agg" = "50" ]; then
  pass "aggregate returned 50 (minimum of 95,50,90)"
else
  fail "aggregate returned $agg (expected 50)"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All brief-forge-evaluator-runs scenarios PASSED"; exit 0
else echo "Some brief-forge-evaluator-runs scenarios FAILED"; exit 1; fi
