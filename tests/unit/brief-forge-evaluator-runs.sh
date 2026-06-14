#!/usr/bin/env bash
# tests/unit/brief-forge-evaluator-runs.sh
# Asserts: all 5 default evaluators execute, return well-formed JSON,
# and identify documented failure patterns.
# tag: v4.0 phase-3 brief-forge

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EVALS="$REPO_ROOT/lib/brief-forge-evaluators.sh"
FORGE="$REPO_ROOT/lib/brief-forge.sh"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/brief-forge-evaluator-runs.sh"
echo "=========================================="

for f in "$EVALS" "$FORGE"; do
  [ -f "$f" ] || { fail "$f MISSING"; exit 1; }
done

# Sandbox the audit seams BEFORE sourcing: lib/brief-forge.sh sources bin/_audit.sh,
# which mkdirs $LINTEL_AUDIT_DIR at source time — without these seams the test
# touches the real ~/.lintel/audit.
SANDBOX=$(mktemp -d)
export LINTEL_HOME="$SANDBOX/lintel-home"
export LINTEL_AUDIT_DIR="$SANDBOX/audit"

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

# ─── Scenario 4 removed: trailblazer_alignment evaluator moved to an external
#     pack (lintel-caip-pack) in the v4.7 CAIP extraction. The pack repo tests it. ───

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
   printf '%s' "$head_out" | grep -qE 'kind: subagent_spawn'; then
  pass "forge_envelope_head produces valid HEAD"
else
  fail "forge_envelope_head output invalid"
fi

body_out=$(forge_envelope_body brief "$content_file")
if printf '%s' "$body_out" | grep -qE '^body:' && \
   printf '%s' "$body_out" | grep -qE 'content_type: brief'; then
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
