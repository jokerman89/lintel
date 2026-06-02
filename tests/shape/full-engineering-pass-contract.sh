#!/usr/bin/env bash
# tests/shape/full-engineering-pass-contract.sh
# Asserts (v4.6): full-engineering-pass composition skill is workflow_root,
# declares the DAG, references the 5 modules, supports graceful degradation.
# tag: shape v4.6

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/full-engineering-pass-contract.sh"
echo "==============================================="

FEP="$REPO_ROOT/skills/full-engineering-pass/SKILL.md"
[ -f "$FEP" ] || { fail "skills/full-engineering-pass/SKILL.md MISSING"; exit 1; }
pass "skills/full-engineering-pass/SKILL.md present"

# workflow_root + necessity + gap_if_skipped (v4.1+ convention)
for f in "workflow_root:[[:space:]]*true" "^necessity:" "^gap_if_skipped:"; do
  if grep -qE "$f" "$FEP"; then pass "FEP declares $f"
  else fail "FEP missing $f"; fi
done

# Required navigation fields
for f in primary_intent triggers risk_level auto_mode_eligible estimated_tokens; do
  if grep -qE "^[[:space:]]+${f}:" "$FEP"; then pass "FEP navigation $f"
  else fail "FEP navigation MISSING $f"; fi
done

# Composition DAG declared
for f in composition_dag cap_soft cap_hard partial_rollout; do
  if grep -qE "^[[:space:]]+${f}:" "$FEP"; then pass "FEP domain $f"
  else fail "FEP domain MISSING $f"; fi
done

# All 5 modules referenced as siblings + DAG stages
for module in ta da sc dh tq; do
  if grep -qE "/li:${module}\b" "$FEP"; then pass "FEP references /li:$module"
  else fail "FEP MISSING /li:$module reference"; fi
done

# 4 stages documented
for stage in "Stage 1" "Stage 2" "Stage 3" "Stage 4"; do
  if grep -qF "$stage" "$FEP"; then pass "FEP documents $stage"
  else fail "FEP MISSING $stage"; fi
done

# Graceful degradation documented
if grep -qiE "graceful|gracefully|missing module|partial.rollout" "$FEP"; then
  pass "FEP documents graceful-degradation behavior"
else
  fail "FEP MISSING graceful degradation documentation"
fi

# Resume support
if grep -qE "(\-\-resume|--resume)" "$FEP"; then
  pass "FEP supports --resume"
else
  fail "FEP MISSING --resume support"
fi

# Aggregate scoring (30 dims = 6 × 5)
if grep -qE "(30.dim|6.dim.*5|aggregate)" "$FEP"; then
  pass "FEP documents aggregate scoring (30-dim or 6×5)"
else
  fail "FEP MISSING aggregate scoring documentation"
fi

# Concept doc
if [ -f "$REPO_ROOT/docs/concepts/full-engineering-pass.md" ]; then
  pass "concept doc full-engineering-pass.md present"
else
  fail "concept doc full-engineering-pass.md MISSING"
fi

# Concept doc references engineering-modules pattern
if grep -q "engineering-modules" "$REPO_ROOT/docs/concepts/full-engineering-pass.md" 2>/dev/null; then
  pass "concept doc references engineering-modules pattern"
else
  fail "concept doc MISSING engineering-modules reference"
fi

# Concept doc marks v4.x feature-complete
if grep -qiE "v4\.x feature.complete|feature-complete" "$REPO_ROOT/docs/concepts/full-engineering-pass.md" 2>/dev/null; then
  pass "concept doc marks v4.x feature-complete"
else
  fail "concept doc MISSING v4.x feature-complete marker"
fi

# Color cyan (composition / orchestration color, distinct from module colors)
if grep -qE "^color:[[:space:]]+cyan" "$FEP"; then
  pass "FEP uses cyan (composition/orchestration color)"
else
  fail "FEP color != cyan"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All full-engineering-pass-contract assertions PASSED"; exit 0
else echo "Some full-engineering-pass-contract assertions FAILED"; exit 1; fi
