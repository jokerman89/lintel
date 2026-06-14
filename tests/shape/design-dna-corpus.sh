#!/usr/bin/env bash
# tests/shape/design-dna-corpus.sh
# Structural contract for the design-dna module (ADR-0015/0016): the consumed
# corpus is present + attributed, the anthropic-default profile carries the 7
# canonical tokens, scripts exist, and the skill conforms to frontmatter rules.
# tag: design-dna corpus profile attribution
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/shape/design-dna-corpus.sh"
echo "================================"

DNA="skills/design-dna"

# 1. Corpus files (11 domain CSVs + 16 stack CSVs)
for f in styles colors charts landing products ux-guidelines typography icons react-performance app-interface ui-reasoning; do
  [ -f "$DNA/data/$f.csv" ] && pass "data/$f.csv present" || fail "data/$f.csv MISSING"
done
stack_count=$(find "$DNA/data/stacks" -name "*.csv" 2>/dev/null | wc -l)
[ "$stack_count" -eq 16 ] && pass "16 stack CSVs present" || fail "expected 16 stack CSVs, found $stack_count"

# 2. Subtraction holds: the dropped ballast must NOT come back silently
for dropped in google-fonts.csv draft.csv design.csv; do
  [ ! -f "$DNA/data/$dropped" ] && pass "$dropped stays dropped (ADR-0015 subtraction)" || fail "$dropped reappeared — ADR-0015 dropped it deliberately"
done
grep -q '"google-fonts"' "$DNA/scripts/core.py" && fail "core.py still registers google-fonts domain" || pass "core.py registry matches the corpus"

# 3. Scripts present
for s in core.py search.py design_system.py validate_design.py emit_tokens.py; do
  [ -f "$DNA/scripts/$s" ] && pass "scripts/$s present" || fail "scripts/$s MISSING"
done

# 3b. Slide decision engine (ADR-0017): 8 slide CSVs + token-architecture references
slide_count=$(find "$DNA/data/slides" -name "slide-*.csv" 2>/dev/null | wc -l)
[ "$slide_count" -eq 8 ] && pass "8 slide-decision CSVs present" || fail "expected 8 slide CSVs, found $slide_count"
[ -f "$DNA/references/token-architecture.md" ] && pass "token-architecture reference present" || fail "token-architecture.md MISSING"
grep -q 'SLIDE_CONFIG' "$DNA/scripts/core.py" && pass "core.py registers slide domains" || fail "slide domains not registered in core.py"

# 4. anthropic-default profile: the 7 canonical tokens, exact values
PROFILE="$DNA/profiles/anthropic-default.yaml"
if [ -f "$PROFILE" ]; then
  pass "profiles/anthropic-default.yaml present"
  for hex in '#141413' '#faf9f5' '#b0aea5' '#e8e6dc' '#d97757' '#6a9bcc' '#788c5d'; do
    grep -qi "$hex" "$PROFILE" && pass "canonical token $hex" || fail "canonical token $hex MISSING from profile"
  done
  grep -q 'Poppins' "$PROFILE" && grep -q 'Lora' "$PROFILE" \
    && pass "canonical font roles (Poppins/Lora)" || fail "canonical font roles missing"
  grep -q 'source: derived' "$PROFILE" \
    && pass "derived blocks are source-marked" || fail "no source: derived markers — gap-fills must be marked"
else
  fail "profiles/anthropic-default.yaml MISSING"
fi

# 5. Attribution (license obligations)
if [ -f "$DNA/ATTRIBUTION.md" ]; then
  grep -q 'Next Level Builder' "$DNA/ATTRIBUTION.md" && pass "MIT attribution (Next Level Builder)" || fail "MIT attribution missing"
  grep -q 'Anthropic, PBC' "$DNA/ATTRIBUTION.md" && pass "Apache-2.0 attribution (Anthropic, PBC)" || fail "Apache-2.0 attribution missing"
else
  fail "ATTRIBUTION.md MISSING — license obligation"
fi

# 6. SKILL.md exists + declares the consumers' contract
if [ -f "$DNA/SKILL.md" ]; then
  pass "SKILL.md present"
  grep -q 'design.profile' "$DNA/SKILL.md" && pass "pack seam (design.profile) documented" || fail "pack seam undocumented"
  grep -qi 'python3 absent\|grep fallback\|Degradation' "$DNA/SKILL.md" && pass "python-absent degradation documented" || fail "degradation path undocumented"
else
  fail "SKILL.md MISSING"
fi

# 7. Consumers actually wired (the rewire is load-bearing, not decorative)
grep -q 'design-dna' skills/frontend-design/SKILL.md && pass "frontend-design wired to design-dna" || fail "frontend-design not wired"
grep -q 'validate_design.py' skills/generate-web/SKILL.md && pass "generate-web Gate 0 wired" || fail "generate-web Gate 0 missing"

echo ""
[ "$FAILED" -eq 0 ] && { echo "design-dna-corpus: ALL PASS"; exit 0; } || { echo "design-dna-corpus: FAILURES"; exit 1; }
