#!/usr/bin/env bash
# tests/unit/context-warm-skills-present.sh
#
# Verifies v3.5 context-warming infrastructure: 10 skills present + valid.
# Post-Väg-A: skill folder/name bare (no li- prefix), invocation /li:<name>.
# tag: v3.5 context-warming

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/context-warm-skills-present.sh"
echo "========================================="

# 10 context-warming skills (bare folder names)
WARM_SKILLS=(
  context-warm
  context-warm-related
  context-warm-sessions
  context-warm-adrs
  context-warm-customer
  context-warm-from-url
  context-save
  context-restore
  context-budget
  context-cool
)

for skill in "${WARM_SKILLS[@]}"; do
  f="$REPO_ROOT/skills/$skill/SKILL.md"
  if [ -f "$f" ]; then
    name=$(grep '^name:' "$f" | head -1 | awk '{print $2}')
    if [ "$name" = "$skill" ]; then
      pass "context skill: $skill"
    else
      fail "context skill name mismatch: folder=$skill, frontmatter=$name"
    fi
  else
    fail "context skill missing: $f"
  fi
done

# All have cli_support
for skill in "${WARM_SKILLS[@]}"; do
  f="$REPO_ROOT/skills/$skill/SKILL.md"
  [ -f "$f" ] || continue
  if ! grep -q '^cli_support:' "$f"; then
    fail "missing cli_support: $skill"
  fi
done
pass "all context-warming skills have cli_support frontmatter"

# All have layer: foundation
for skill in "${WARM_SKILLS[@]}"; do
  f="$REPO_ROOT/skills/$skill/SKILL.md"
  [ -f "$f" ] || continue
  layer=$(grep '^layer:' "$f" | head -1 | awk '{print $2}')
  if [ "$layer" != "foundation" ]; then
    fail "wrong layer for $skill: '$layer'"
  fi
done
pass "all context-warming skills have layer: foundation"

# context-warm is the base, most variants reference /li:context-warm.
# from-url uses WebFetch directly (not delegating); excluded from delegation check.
DELEGATING_VARIANTS=(context-warm-related context-warm-sessions context-warm-adrs context-warm-customer)
for variant in "${DELEGATING_VARIANTS[@]}"; do
  f="$REPO_ROOT/skills/$variant/SKILL.md"
  [ -f "$f" ] || continue
  if grep -q '/li:context-warm' "$f"; then
    : # ok, references base
  else
    fail "$variant doesn't reference /li:context-warm (delegation expected)"
  fi
done
pass "all delegating context-warm variants reference /li:context-warm"

# Budget tracking referenced in base skill
if grep -q 'context-budget.md' "$REPO_ROOT/skills/context-warm/SKILL.md"; then
  pass "context-warm references context-budget.md tracking"
else
  fail "context-warm doesn't track budget"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All context-warm-skills-present tests PASSED"
  exit 0
else
  echo "Some context-warm-skills-present tests FAILED"
  exit 1
fi
