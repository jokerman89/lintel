#!/usr/bin/env bash
# tests/unit/frontend-skills-present.sh
#
# Verifies v3.7 Fas A1 frontend-* family foundation: 3 skills + 3 agents
# + new agents/frontend/ category.
# Pattern följer tests/unit/observation-spine-skills-present.sh + closeout-additions-present.sh.
# tag: v3.7 fas-a1 frontend-foundation

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/frontend-skills-present.sh"
echo "====================================="

# 6 frontend-* skills (Fas A1: design orchestrator + typography + motion;
#                       Fas A2: shader + style-extract + design-review)
FRONTEND_SKILLS=(frontend-design frontend-typography frontend-motion frontend-shader frontend-style-extract frontend-design-review)
for skill in "${FRONTEND_SKILLS[@]}"; do
  f="$REPO_ROOT/skills/$skill/SKILL.md"
  if [ -f "$f" ]; then
    name=$(grep '^name:' "$f" | head -1 | awk '{print $2}')
    layer=$(grep '^layer:' "$f" | head -1 | awk '{print $2}')
    color=$(grep '^color:' "$f" | head -1 | awk '{print $2}')
    voice=$(grep '^voice:' "$f" | head -1 | awk '{print $2}')

    if [ "$name" = "$skill" ] && [ "$layer" = "ms-team" ]; then
      pass "frontend-* skill: $skill (name + layer match)"
    else
      fail "frontend-* skill frontmatter: $skill (name=$name, layer=$layer)"
    fi

    # Color: frontend-* family follows generate-* convention (orange = ms-team format/content)
    if [ "$color" = "orange" ]; then
      pass "frontend-* skill: $skill has color: orange (family-convention)"
    else
      fail "frontend-* skill: $skill color=$color, expected 'orange'"
    fi

    # Voice tier present (internal default; orchestrator is 'mixed')
    if [ -n "$voice" ]; then
      pass "frontend-* skill: $skill has voice tier ($voice)"
    else
      fail "frontend-* skill: $skill missing voice tier"
    fi

    # cli_support present (required per v3.6 frontmatter-lint contract)
    if grep -q '^cli_support:' "$f"; then
      pass "frontend-* skill: $skill has cli_support frontmatter"
    else
      fail "frontend-* skill: $skill missing cli_support frontmatter"
    fi

    # schema_version: 1 must appear in body (M-5 resolution contract)
    if grep -q 'schema_version' "$f"; then
      pass "frontend-* skill: $skill body references schema_version (M-5)"
    else
      fail "frontend-* skill: $skill body missing schema_version (M-5 contract)"
    fi
  else
    fail "frontend-* SKILL.md missing: $f"
  fi
done

# frontend-design orchestrator specific checks (parallel-dispatch + M-1 + boundary)
ORCHESTRATOR="$REPO_ROOT/skills/frontend-design/SKILL.md"
if [ -f "$ORCHESTRATOR" ]; then
  if grep -qE "PARALLEL|parallel" "$ORCHESTRATOR"; then
    pass "frontend-design orchestrator references PARALLEL dispatch (M-4)"
  else
    fail "frontend-design orchestrator missing parallel-dispatch reference (M-4 contract)"
  fi

  if grep -q "frontend-design-spec.json" "$ORCHESTRATOR"; then
    pass "frontend-design orchestrator uses frontend-design-spec.json filename (M-1)"
  else
    fail "frontend-design orchestrator missing frontend-design-spec.json reference (M-1 contract)"
  fi

  if grep -qE "design-director|rendering-engine" "$ORCHESTRATOR"; then
    pass "frontend-design orchestrator documents design-director vs rendering-engine boundary (L-002)"
  else
    fail "frontend-design orchestrator missing family-boundary documentation"
  fi
fi

# 5 frontend agents (Fas A1: FrontendArchitect + MotionDirector + TypographyCurator;
#                     Fas A2: ShaderEngineer + DesignSystemAuditor)
FRONTEND_AGENTS=(FrontendArchitect MotionDirector TypographyCurator ShaderEngineer DesignSystemAuditor)
for agent in "${FRONTEND_AGENTS[@]}"; do
  f="$REPO_ROOT/agents/frontend/$agent.md"
  if [ -f "$f" ]; then
    name=$(grep '^name:' "$f" | head -1 | awk '{print $2}')
    category=$(grep '^category:' "$f" | head -1 | awk '{print $2}')
    color=$(grep '^color:' "$f" | head -1 | awk '{print $2}')

    if [ "$name" = "$agent" ] && [ "$category" = "frontend" ]; then
      pass "frontend agent: $agent (name + category match)"
    else
      fail "frontend agent frontmatter: $agent (name=$name, category=$category)"
    fi

    if [ "$color" = "purple" ]; then
      pass "frontend agent: $agent has color: purple (agent-family-convention)"
    else
      fail "frontend agent: $agent color=$color, expected 'purple'"
    fi

    if grep -q '^tier:' "$f"; then
      pass "frontend agent: $agent has tier frontmatter"
    else
      fail "frontend agent: $agent missing tier frontmatter"
    fi
  else
    fail "frontend agent .md missing: $f"
  fi
done

# FrontendArchitect non-overlap (m-1 resolution) — must reference FrontendBuilder
ARCH="$REPO_ROOT/agents/frontend/FrontendArchitect.md"
if [ -f "$ARCH" ]; then
  if grep -q "FrontendBuilder" "$ARCH"; then
    pass "FrontendArchitect documents non-overlap with FrontendBuilder (m-1)"
  else
    fail "FrontendArchitect missing FrontendBuilder non-overlap note (m-1 contract)"
  fi
fi

# agents/frontend/ category present in directory structure
if [ -d "$REPO_ROOT/agents/frontend" ]; then
  count=$(find "$REPO_ROOT/agents/frontend" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
  if [ "$count" -ge 5 ]; then
    pass "agents/frontend/ category present with $count agents (≥5 expected för Fas A2)"
  else
    fail "agents/frontend/ category has $count agents, expected ≥5 (Fas A2: 5 total)"
  fi
else
  fail "agents/frontend/ directory missing"
fi

# Fas A2 — canonical pattern seed present in repo
SEED_DIR="$REPO_ROOT/seeds/brand/design-patterns/ultra-modern-lovable-style"
if [ -d "$SEED_DIR" ]; then
  pass "canonical pattern seed present: ultra-modern-lovable-style"

  # All 5 required files (pattern + typography + motion + component-imports + shader-snippets)
  REQUIRED_FILES=(pattern.json typography.json motion.json component-imports.json)
  for rf in "${REQUIRED_FILES[@]}"; do
    if [ -f "$SEED_DIR/$rf" ]; then
      pass "canonical pattern includes: $rf"
    else
      fail "canonical pattern missing: $rf"
    fi
  done

  # shader-snippets/ subfolder present
  if [ -d "$SEED_DIR/shader-snippets" ]; then
    pass "canonical pattern includes shader-snippets/ subfolder"
  else
    fail "canonical pattern missing shader-snippets/ subfolder"
  fi

  # schema_version: 1 grep-check on all JSON
  for jf in pattern.json typography.json motion.json component-imports.json; do
    if [ -f "$SEED_DIR/$jf" ] && grep -q '"schema_version": 1' "$SEED_DIR/$jf"; then
      pass "canonical pattern $jf has schema_version: 1 (M-5)"
    else
      fail "canonical pattern $jf missing schema_version: 1"
    fi
  done
else
  fail "canonical pattern seed missing: seeds/brand/design-patterns/ultra-modern-lovable-style/"
fi

# Fas A2 — frontend-design-review skill has explicit scoring rubric (resolves M-3 reviewer-concern)
REVIEW_SKILL="$REPO_ROOT/skills/frontend-design-review/SKILL.md"
if [ -f "$REVIEW_SKILL" ]; then
  if grep -qE "(≥|>=)?80.*green" "$REVIEW_SKILL" && grep -qE "60-79.*yellow" "$REVIEW_SKILL"; then
    pass "frontend-design-review has explicit scoring rubric (≥80=green, 60-79=yellow, <60=red)"
  else
    fail "frontend-design-review missing scoring rubric (resolves /plan-eng-review M-3 concern #3)"
  fi
fi

# Fas A2 — frontend-style-extract inherits --overwrite flag from generate-style-learn (m-3)
EXTRACT_SKILL="$REPO_ROOT/skills/frontend-style-extract/SKILL.md"
if [ -f "$EXTRACT_SKILL" ]; then
  if grep -q "overwrite" "$EXTRACT_SKILL"; then
    pass "frontend-style-extract documents --overwrite flag inheritance (m-3)"
  else
    fail "frontend-style-extract missing --overwrite flag documentation (m-3 concern)"
  fi
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All frontend-skills-present tests PASSED"
  exit 0
else
  echo "Some frontend-skills-present tests FAILED"
  exit 1
fi
