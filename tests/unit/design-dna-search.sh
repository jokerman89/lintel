#!/usr/bin/env bash
# tests/unit/design-dna-search.sh
# Behavior: the BM25 search engine answers domain/stack/design-system queries
# (ADR-0015). Skips cleanly when python3 is absent (the documented degradation
# path is grep over the CSVs — covered by the shape test's file assertions).
# tag: design-dna search behavior
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/design-dna-search.sh"
echo "==============================="

if ! command -v python3 >/dev/null 2>&1; then
  echo "  SKIP: python3 not available — degradation path is direct CSV reads"
  echo ""
  echo "design-dna-search: ALL PASS (skipped)"
  exit 0
fi

S="skills/design-dna/scripts/search.py"

# 1. Domain search returns results
out=$(python3 "$S" "elegant serif editorial" --domain typography -n 2 2>&1); rc=$?
[ $rc -eq 0 ] && pass "typography domain search rc=0" || fail "typography search rc=$rc"
echo "$out" | grep -q "Font Pairing Name" && pass "typography results carry pairing rows" || fail "no pairing rows in output"

# 2. Auto-detect routes a bare font query to typography (google-fonts domain removed)
out=$(python3 "$S" "elegant serif font" 2>&1); rc=$?
[ $rc -eq 0 ] && echo "$out" | grep -q "Domain:.*typography" \
  && pass "auto-detect routes font query to typography post-subtraction" \
  || fail "auto-detect broken for font queries (rc=$rc)"

# 3. Stack search returns Do/Don't rules
out=$(python3 "$S" "layout shift images" --stack html-tailwind -n 1 2>&1); rc=$?
[ $rc -eq 0 ] && echo "$out" | grep -q "Do" && pass "stack search returns rules" || fail "stack search broken (rc=$rc)"

# 4. Design-system composition: pattern + style + colors + typography sections
out=$(python3 "$S" "fintech saas dashboard professional" --design-system -f markdown 2>&1); rc=$?
[ $rc -eq 0 ] && pass "--design-system compose rc=0" || fail "--design-system rc=$rc"
for section in "Pattern" "Style" "Colors" "Typography"; do
  echo "$out" | grep -q "### $section" && pass "compose has $section section" || fail "compose missing $section section"
done

# 5. Negative: unknown stack fails loudly, not silently
out=$(python3 "$S" "anything" --stack not-a-stack 2>&1); rc=$?
[ $rc -ne 0 ] && pass "unknown stack rejected (rc=$rc)" || fail "unknown stack accepted silently"

# 6. Slide decision engine (ADR-0017): emotion → color, goal → layout, strategy w/ sparkline-beats
out=$(python3 "$S" "confidence" --slide color-logic -n 1 2>&1); rc=$?
[ $rc -eq 0 ] && echo "$out" | grep -qi "background:" && pass "slide color-logic by emotion" || fail "slide color-logic broken (rc=$rc)"
out=$(python3 "$S" "proof" --slide layout-logic -n 1 2>&1)
echo "$out" | grep -qi "layout_pattern:" && pass "slide layout-logic by goal" || fail "slide layout-logic broken"
out=$(python3 "$S" "investor pitch" --slide strategy -n 1 2>&1)
echo "$out" | grep -qi "sparkline_beats:" && pass "slide strategy carries Duarte sparkline-beats" || fail "slide strategy missing sparkline-beats"
# negative: unknown slide domain rejected
out=$(python3 "$S" "x" --slide not-a-slide 2>&1); rc=$?
[ $rc -ne 0 ] && pass "unknown slide domain rejected" || fail "unknown slide domain accepted silently"

echo ""
[ "$FAILED" -eq 0 ] && { echo "design-dna-search: ALL PASS"; exit 0; } || { echo "design-dna-search: FAILURES"; exit 1; }
