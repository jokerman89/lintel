#!/usr/bin/env bash
# tests/unit/v37-closeout-additions-present.sh
#
# Verifies v3.7 closeout — all 9 skills + 5 agents + 1 hook + canonical pattern
# + install-bootstrap from Fas A1+A2+B+C on plats.
# Pattern följer tests/unit/closeout-additions-present.sh (v3.6 closeout).
# tag: v3.7 closeout

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/v37-closeout-additions-present.sh"
echo "============================================"

# --- 9 skills (Fas A1 + A2 + B) ---
# Fas A1: frontend-design + frontend-typography + frontend-motion
# Fas A2: frontend-shader + frontend-style-extract + frontend-design-review
# Fas B:  generate-app (NEW skill, M-2 resolution) + generate-web (extended)
V37_SKILLS=(frontend-design frontend-typography frontend-motion frontend-shader frontend-style-extract frontend-design-review generate-app)
for s in "${V37_SKILLS[@]}"; do
  f="$REPO_ROOT/skills/$s/SKILL.md"
  if [ -f "$f" ] && grep -qE "^name: $s\$" "$f"; then
    pass "v3.7 skill present: $s"
  else
    fail "v3.7 skill missing or frontmatter wrong: $s"
  fi
done

# generate-web extended med --from-frontend-design (Fas B)
GW="$REPO_ROOT/skills/generate-web/SKILL.md"
if [ -f "$GW" ] && grep -q "from-frontend-design" "$GW"; then
  pass "generate-web extended with --from-frontend-design mode (Fas B)"
else
  fail "generate-web missing --from-frontend-design mode (Fas B contract)"
fi

# --- 5 agents i agents/frontend/ category (Fas A1 + A2) ---
V37_AGENTS=(FrontendArchitect MotionDirector TypographyCurator ShaderEngineer DesignSystemAuditor)
for a in "${V37_AGENTS[@]}"; do
  f="$REPO_ROOT/agents/frontend/$a.md"
  if [ -f "$f" ] && grep -qE "^name: $a\$" "$f"; then
    pass "v3.7 agent present: $a"
  else
    fail "v3.7 agent missing or frontmatter wrong: $a"
  fi
done

# --- 1 hook (Fas C) ---
HOOK_DIR="$REPO_ROOT/hooks/shared/frontend-design-surface"
if [ -d "$HOOK_DIR" ] && [ -f "$HOOK_DIR/HOOK.md" ] && [ -f "$HOOK_DIR/run.sh" ]; then
  pass "v3.7 hook present: frontend-design-surface (HOOK.md + run.sh)"
else
  fail "v3.7 hook missing: frontend-design-surface"
fi

# --- Canonical pattern seed (Fas A2) ---
SEED="$REPO_ROOT/seeds/brand/design-patterns/ultra-modern-lovable-style"
if [ -d "$SEED" ]; then
  pass "canonical pattern seed present: ultra-modern-lovable-style"

  # 4 required JSON contracts
  for jf in pattern.json typography.json motion.json component-imports.json; do
    if [ -f "$SEED/$jf" ] && grep -q '"schema_version": 1' "$SEED/$jf"; then
      pass "canonical $jf present + schema_version: 1"
    else
      fail "canonical $jf missing or schema_version mismatch"
    fi
  done

  # Shader snippets subfolder
  if [ -d "$SEED/shader-snippets" ] && [ -f "$SEED/shader-snippets/README.md" ]; then
    pass "canonical shader-snippets/ subfolder + README"
  else
    fail "canonical shader-snippets/ structure incomplete"
  fi
fi

# --- Install scripts bootstrap brand-asset slots (Fas A2) ---
for installer in install/install.sh install/install.ps1; do
  f="$REPO_ROOT/$installer"
  if [ -f "$f" ] && grep -qE "design-patterns|motion-libraries|shader-snippets" "$f"; then
    pass "$installer bootstraps brand-asset slots"
  else
    fail "$installer missing brand-asset bootstrap"
  fi
done

# --- M-1 through M-6 contracts validated by other tests already ---
# Cross-reference: frontend-skills-present.sh + frontend-design-roundtrip.sh +
# frontend-design-surface-hook.sh cover individual contracts. This closeout
# test only verifies presence.

# --- Frontend agents — exactly 5 in agents/frontend/ (the v3.7 contract) ---
# Note: total-agent count varies between local + CI because agents/customer/* is
# gitignored (untracked locally inflates local count). Use frontend-only count
# as the contract instead — it's exact and matches reality on both surfaces.
frontend_count=$(find "$REPO_ROOT/agents/frontend" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
if [ "$frontend_count" -eq 5 ]; then
  pass "agents/frontend/ has exactly 5 agents (v3.7 contract: 3 from A1 + 2 from A2)"
else
  fail "agents/frontend/ has $frontend_count agents, expected 5 (v3.7 contract)"
fi

# --- Reviewer-concern tracking — working-state captures v3.7 PRs (v5 home) ---
MEM="$REPO_ROOT/.claude/memory/working-state.md"
if [ -f "$MEM" ] && grep -q "PR #21" "$MEM"; then
  pass "working-state.md tracks PR #21 (v3.7 design doc reviewer-concerns)"
else
  fail "working-state.md missing PR #21 reviewer-concern tracking"
fi

# --- LAYERS.md reflects v3.7 separation-of-concerns lesson ---
LAYERS="$REPO_ROOT/LAYERS.md"
if [ -f "$LAYERS" ] && grep -qiE "v3.7|design-director|rendering-engine" "$LAYERS"; then
  pass "LAYERS.md reflects v3.7 architectural learning"
else
  fail "LAYERS.md missing v3.7 reflection"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All v3.7-closeout-additions tests PASSED"
  exit 0
else
  echo "Some v3.7-closeout-additions tests FAILED"
  exit 1
fi
