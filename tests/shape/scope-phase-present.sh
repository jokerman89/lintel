#!/usr/bin/env bash
# tests/shape/scope-phase-present.sh
# Asserts (Slice 2 — scope-scaled-planning):
#   S1 — skills/scope/SKILL.md exists, folder+frontmatter name match, has the
#        required SKILL frontmatter fields + necessity + a real gap_if_skipped
#   S2 — the 3 canonical plan templates exist (plan/spec/prompt.template.md)
#        and plan.template.md carries all three depth_schema markers
#   S3 — plan/SKILL.md references depth_schema=tree (Slice 2 WBS rendering) and
#        the template family; cycle inserts SCOPE between SENSE and DEFINE
# tag: shape slice-2 scope-scaled-planning

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/scope-phase-present.sh"
echo "==================================="

# ─── S1: SCOPE skill exists with valid frontmatter ───────────────────────────
echo ""
echo "[S1] skills/scope/SKILL.md"
SCOPE="$REPO_ROOT/skills/scope/SKILL.md"
if [ -f "$SCOPE" ]; then
  pass "skills/scope/SKILL.md exists"
  name=$(grep -E '^name:' "$SCOPE" | head -1 | awk '{print $2}')
  [ "$name" = "scope" ] && pass "frontmatter name=scope (matches folder)" \
                        || fail "frontmatter name='$name' (expected 'scope')"
  # Mirror frontmatter-lint-all's REQUIRED_SKILL_FIELDS
  for field in name layer description color tools voice cli_support; do
    grep -qE "^${field}:" "$SCOPE" && pass "required field '$field' present" \
                                   || fail "required field '$field' MISSING"
  done
  layer=$(grep -E '^layer:' "$SCOPE" | head -1 | awk '{print $2}')
  [ "$layer" = "foundation" ] && pass "layer: foundation" \
                              || fail "layer='$layer' (expected foundation)"
  # Slice-2 contract: SCOPE declares necessity + a real (non-empty) gap_if_skipped
  grep -qE "^necessity:[[:space:]]*STRONGLY_RECOMMENDED" "$SCOPE" \
    && pass "necessity: STRONGLY_RECOMMENDED" \
    || fail "necessity not STRONGLY_RECOMMENDED"
  gap=$(grep -E '^gap_if_skipped:' "$SCOPE" | head -1 | sed 's/^gap_if_skipped:[[:space:]]*//')
  [ "${#gap}" -ge 40 ] && pass "gap_if_skipped is substantive (${#gap} chars)" \
                       || fail "gap_if_skipped too short/empty (${#gap} chars)"
else
  fail "skills/scope/SKILL.md MISSING"
fi

# ─── S2: canonical template family ───────────────────────────────────────────
echo ""
echo "[S2] template family"
TPL_DIR="$REPO_ROOT/scaffolding/01-foundation/templates/plan"
for t in plan spec prompt; do
  f="$TPL_DIR/$t.template.md"
  [ -f "$f" ] && pass "$t.template.md exists" || fail "$t.template.md MISSING"
done
PLAN_TPL="$TPL_DIR/plan.template.md"
if [ -f "$PLAN_TPL" ]; then
  for marker in "depth_schema: flat" "depth_schema: phased" "depth_schema: tree"; do
    grep -q "$marker" "$PLAN_TPL" && pass "plan.template.md has marker '$marker'" \
                                  || fail "plan.template.md missing marker '$marker'"
  done
fi

# ─── S3: plan references tree + templates; cycle inserts SCOPE ────────────────
echo ""
echo "[S3] plan references depth_schema=tree + template family; cycle wiring"
PLAN_SKILL="$REPO_ROOT/skills/plan/SKILL.md"
if [ -f "$PLAN_SKILL" ]; then
  grep -q "depth_schema: tree" "$PLAN_SKILL" && pass "plan references depth_schema=tree" \
                                             || fail "plan missing depth_schema=tree reference"
  grep -q "1.1.a" "$PLAN_SKILL" && pass "plan documents tree numbering (1.1.a leaf)" \
                                || fail "plan missing tree numbering scheme"
  grep -q "templates/plan/" "$PLAN_SKILL" && pass "plan references the template family path" \
                                          || fail "plan does not reference templates/plan/"
else
  fail "skills/plan/SKILL.md MISSING"
fi

CYCLE="$REPO_ROOT/skills/cycle/SKILL.md"
if [ -f "$CYCLE" ]; then
  grep -qE "SENSE +→ +SCOPE +→ +DEFINE" "$CYCLE" && pass "cycle full path inserts SCOPE between SENSE and DEFINE" \
    || fail "cycle full path does not show SENSE → SCOPE → DEFINE"
else
  fail "skills/cycle/SKILL.md MISSING"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All scope-phase-present assertions PASSED"; exit 0
else echo "Some scope-phase-present assertions FAILED"; exit 1; fi
