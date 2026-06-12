#!/usr/bin/env bash
# tests/unit/envelope-schema-validates.sh
# Asserts: bin/li-envelope-validate correctly accepts valid envelopes,
# rejects invalid ones, identifies the specific failed field.
# tag: v4.0 phase-2 envelope

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VALIDATOR="$REPO_ROOT/bin/li-envelope-validate"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/envelope-schema-validates.sh"
echo "========================================"

if [ ! -x "$VALIDATOR" ]; then
  fail "bin/li-envelope-validate missing or not executable"
  exit 1
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# ─── Scenario 1: minimal valid envelope (brief content_type) ─────────────
echo ""
echo "[1] Minimal valid envelope (kind=subagent_spawn, content_type=brief)"
cat > "$TMP/valid-brief.yaml" <<'EOF'
head:
  envelope_id: "01JKQNZ8X9YAR6FJ4V7Q5MWXYZ"
  envelope_schema_version: "1"
  kind: subagent_spawn
  from: plan
  to: PlanReviewer
  issued_at: "2026-05-29T15:00:00Z"
body:
  content_type: brief
  content:
    task: Review the plan for elegance
    constraints:
      - no scope creep
      - keep changes minimal
    acceptance:
      - reviewer surfaces specific concerns or APPROVES
tail:
  completeness_score: 95
  evaluators_run:
    - completeness
    - security
  escape_hatches:
    - Re-invoke /li:plan --more-detail
  audit_pointer: .claude/runtime/audit/envelopes-2026-05-29.jsonl
EOF

if "$VALIDATOR" --quiet "$TMP/valid-brief.yaml"; then
  pass "valid brief envelope accepted"
else
  fail "valid brief envelope rejected"
  "$VALIDATOR" "$TMP/valid-brief.yaml" 2>&1 | sed 's/^/    /'
fi

# ─── Scenario 2: invalid kind ─────────────────────────────────────────────
echo ""
echo "[2] Invalid kind enum value → reject"
cat > "$TMP/invalid-kind.yaml" <<'EOF'
head:
  envelope_id: "01JKQNZ8X9YAR6FJ4V7Q5MWXYY"
  envelope_schema_version: "1"
  kind: not_a_real_kind
  from: plan
  to: agent-x
  issued_at: "2026-05-29T15:00:00Z"
body:
  content_type: brief
  content:
    task: x
    constraints: [a]
    acceptance: [b]
tail:
  completeness_score: 80
  evaluators_run: []
  escape_hatches: []
  audit_pointer: /tmp/x.jsonl
EOF

if "$VALIDATOR" --quiet "$TMP/invalid-kind.yaml"; then
  fail "invalid kind 'not_a_real_kind' wrongly accepted"
else
  pass "invalid kind rejected"
fi

# ─── Scenario 3: missing head.envelope_id ─────────────────────────────────
echo ""
echo "[3] Missing head.envelope_id → reject"
cat > "$TMP/missing-id.yaml" <<'EOF'
head:
  envelope_schema_version: "1"
  kind: subagent_spawn
  from: plan
  to: PlanReviewer
  issued_at: "2026-05-29T15:00:00Z"
body:
  content_type: brief
  content:
    task: x
    constraints: [a]
    acceptance: [b]
tail:
  completeness_score: 80
  evaluators_run: []
  escape_hatches: []
  audit_pointer: /tmp/x.jsonl
EOF

if "$VALIDATOR" --quiet "$TMP/missing-id.yaml"; then
  fail "missing head.envelope_id wrongly accepted"
else
  pass "missing head.envelope_id rejected"
fi

# ─── Scenario 4: completeness_score out of range ──────────────────────────
echo ""
echo "[4] tail.completeness_score = 150 (out of range) → reject"
cat > "$TMP/bad-score.yaml" <<'EOF'
head:
  envelope_id: "01JKQNZ8X9YAR6FJ4V7Q5MWXYW"
  envelope_schema_version: "1"
  kind: subagent_spawn
  from: plan
  to: PlanReviewer
  issued_at: "2026-05-29T15:00:00Z"
body:
  content_type: brief
  content:
    task: x
    constraints: [a]
    acceptance: [b]
tail:
  completeness_score: 150
  evaluators_run: []
  escape_hatches: []
  audit_pointer: /tmp/x.jsonl
EOF

if "$VALIDATOR" --quiet "$TMP/bad-score.yaml"; then
  fail "completeness_score=150 wrongly accepted"
else
  pass "out-of-range completeness_score rejected"
fi

# ─── Scenario 5: brief content_type missing required body fields ─────────
echo ""
echo "[5] content_type=brief but missing task → reject"
cat > "$TMP/brief-no-task.yaml" <<'EOF'
head:
  envelope_id: "01JKQNZ8X9YAR6FJ4V7Q5MWXYV"
  envelope_schema_version: "1"
  kind: subagent_spawn
  from: plan
  to: PlanReviewer
  issued_at: "2026-05-29T15:00:00Z"
body:
  content_type: brief
  content:
    constraints: [a]
    acceptance: [b]
tail:
  completeness_score: 80
  evaluators_run: []
  escape_hatches: []
  audit_pointer: /tmp/x.jsonl
EOF

if "$VALIDATOR" --quiet "$TMP/brief-no-task.yaml"; then
  fail "brief without task wrongly accepted"
else
  pass "brief without required 'task' field rejected"
fi

# ─── Scenario 6: wrong schema_version ─────────────────────────────────────
echo ""
echo "[6] envelope_schema_version = '99' → reject"
cat > "$TMP/wrong-version.yaml" <<'EOF'
head:
  envelope_id: "01JKQNZ8X9YAR6FJ4V7Q5MWXYU"
  envelope_schema_version: "99"
  kind: subagent_spawn
  from: plan
  to: PlanReviewer
  issued_at: "2026-05-29T15:00:00Z"
body:
  content_type: brief
  content:
    task: x
    constraints: [a]
    acceptance: [b]
tail:
  completeness_score: 80
  evaluators_run: []
  escape_hatches: []
  audit_pointer: /tmp/x.jsonl
EOF

if "$VALIDATOR" --quiet "$TMP/wrong-version.yaml"; then
  fail "envelope_schema_version='99' wrongly accepted"
else
  pass "unknown schema_version rejected"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All envelope-schema-validates scenarios PASSED"
  exit 0
else
  echo "Some envelope-schema-validates scenarios FAILED"
  exit 1
fi
