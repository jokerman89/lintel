#!/usr/bin/env bash
# tests/unit/full-engineering-pass-dag.sh
# Asserts: composition DAG is correctly specified (ordering, parallel-stage marker,
# dependencies, graceful degradation).
# tag: v4.6 full-engineering-pass

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FEP="$REPO_ROOT/skills/full-engineering-pass/SKILL.md"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/full-engineering-pass-dag.sh"
echo "========================================="

[ -f "$FEP" ] || { fail "FEP SKILL.md MISSING"; exit 1; }

# Scenario 1: DAG stage ordering — TA before DA + SC before DH before TQ
echo ""; echo "[1] DAG ordering"
ta_line=$(grep -n '^[[:space:]]*-[[:space:]]*stage:[[:space:]]*1' "$FEP" | head -1 | cut -d: -f1)
ta_modules_line=$(awk -v sl="$ta_line" 'NR > sl && /modules:/ {print NR; exit}' "$FEP")
if grep -A2 'stage: 1' "$FEP" | grep -q "modules:.*ta"; then
  pass "Stage 1 modules include ta"
else
  fail "Stage 1 missing ta"
fi

if grep -A2 'stage: 2' "$FEP" | grep -qE "modules:.*da.*sc|modules:.*sc.*da"; then
  pass "Stage 2 modules include da + sc"
else
  fail "Stage 2 MISSING da + sc"
fi

if grep -A2 'stage: 3' "$FEP" | grep -q "modules:.*dh"; then
  pass "Stage 3 modules include dh"
else
  fail "Stage 3 MISSING dh"
fi

if grep -A2 'stage: 4' "$FEP" | grep -q "modules:.*tq"; then
  pass "Stage 4 modules include tq"
else
  fail "Stage 4 MISSING tq"
fi

# Scenario 2: parallel-stage marker on Stage 2
echo ""; echo "[2] Parallel-stage marker"
if awk '/stage: 2/{found=1} found && /parallel: true/{print "yes"; exit}' "$FEP" | grep -q yes; then
  pass "Stage 2 marked parallel: true"
else
  fail "Stage 2 MISSING parallel: true"
fi

# Stage 1 should NOT be parallel
if awk '/stage: 1/{found=1} found && /parallel: false/{print "yes"; exit}' "$FEP" | grep -q yes; then
  pass "Stage 1 correctly marked parallel: false"
else
  fail "Stage 1 missing parallel: false marker"
fi

# Scenario 3: Dependency tracking
echo ""; echo "[3] Dependency tracking"
if grep -q "depends_on:" "$FEP"; then
  pass "DAG declares depends_on relationships"
else
  fail "DAG missing depends_on declarations"
fi

# Scenario 4: Graceful degradation logic
echo ""; echo "[4] Graceful degradation"
if grep -qiE "missing[_-]modules|available[_-]modules|partial.rollout" "$FEP"; then
  pass "Composition handles missing modules"
else
  fail "Composition MISSING graceful-degradation logic"
fi

# Scenario 5: Skip-module operator override
echo ""; echo "[5] Operator override"
if grep -qE "\-\-skip-module|skip_modules" "$FEP"; then
  pass "Composition supports --skip-module override"
else
  fail "Composition MISSING --skip-module support"
fi

# Scenario 6: Brief Forge handoff between stages
echo ""; echo "[6] Brief Forge handoffs"
if grep -qiE "(brief.forge|brief_forge|forge_envelope|phase_transition)" "$FEP"; then
  pass "Composition uses Brief Forge for stage transitions"
else
  fail "Composition MISSING Brief Forge integration"
fi

# Scenario 7: SHIP verdict semantics
echo ""; echo "[7] SHIP verdict"
for verdict in GREEN YELLOW RED; do
  if grep -q "$verdict" "$FEP"; then
    pass "SHIP verdict '$verdict' documented"
  else
    fail "SHIP verdict '$verdict' MISSING"
  fi
done

# Scenario 8: Cap from pack policy
echo ""; echo "[8] Token cap"
if grep -qE "cap_soft:.*500" "$FEP" && grep -qE "cap_hard:.*(750|1000)" "$FEP"; then
  pass "Cap documented (500k soft / 750k+ hard)"
else
  fail "Cap MISSING or incorrect"
fi

# Scenario 9: All 5 modules referenced in sibling_workflows
echo ""; echo "[9] Sibling workflows complete"
sibling_count=0
for module in ta da sc dh tq; do
  if grep -E "^[[:space:]]+-[[:space:]]+/li:${module}\b" "$FEP" >/dev/null 2>&1; then
    sibling_count=$((sibling_count + 1))
  fi
done
if [ "$sibling_count" -eq 5 ]; then
  pass "All 5 module siblings declared"
else
  fail "Only $sibling_count of 5 module siblings declared"
fi

# Scenario 10: Aggregate scoring across 30 dims
echo ""; echo "[10] 30-dim aggregate scoring"
if grep -qE "30.dim|aggregate.score|aggregate_score" "$FEP"; then
  pass "30-dim aggregate scoring documented"
else
  fail "30-dim aggregate scoring MISSING"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All full-engineering-pass-dag scenarios PASSED"; exit 0
else echo "Some full-engineering-pass-dag scenarios FAILED"; exit 1; fi
