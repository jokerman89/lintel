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

# 3 frontend-* skills (Fas A1 scope: design orchestrator + typography + motion)
FRONTEND_SKILLS=(frontend-design frontend-typography frontend-motion)
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

# 3 frontend agents (Fas A1)
FRONTEND_AGENTS=(FrontendArchitect MotionDirector TypographyCurator)
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
  if [ "$count" -ge 3 ]; then
    pass "agents/frontend/ category present with $count agents (≥3 expected för Fas A1)"
  else
    fail "agents/frontend/ category has $count agents, expected ≥3"
  fi
else
  fail "agents/frontend/ directory missing"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All frontend-skills-present tests PASSED"
  exit 0
else
  echo "Some frontend-skills-present tests FAILED"
  exit 1
fi
