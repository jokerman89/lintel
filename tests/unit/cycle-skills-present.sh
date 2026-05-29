#!/usr/bin/env bash
# tests/unit/cycle-skills-present.sh
#
# Verifies v3.5 Lintel cycle skills are present + valid frontmatter.
# Post-Väg-A: skill names are bare (no li- prefix), invocation /li:<name>.
# tag: v3.5 cycle

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/cycle-skills-present.sh"
echo "=================================="

# 8 phase-skills (bare names, no li- prefix)
PHASES=(sense define discover plan build review ship capture)
for phase in "${PHASES[@]}"; do
  f="$REPO_ROOT/skills/$phase/SKILL.md"
  if [ -f "$f" ]; then
    name=$(grep '^name:' "$f" | head -1 | awk '{print $2}')
    if [ "$name" = "$phase" ]; then
      pass "phase skill: $phase (folder + frontmatter match)"
    else
      fail "phase skill name mismatch: folder=$phase, frontmatter=$name"
    fi
  else
    fail "phase skill missing: $f"
  fi
done

# 2 orchestrator skills
for orch in cycle resume; do
  f="$REPO_ROOT/skills/$orch/SKILL.md"
  [ -f "$f" ] && pass "orchestrator: $orch" || fail "orchestrator missing: $orch"
done

# 4 composite shortcuts
for comp in fix research plan-and-build review-and-ship; do
  f="$REPO_ROOT/skills/$comp/SKILL.md"
  [ -f "$f" ] && pass "composite: $comp" || fail "composite missing: $comp"
done

# Frontmatter has cli_support
for skill_dir in sense define discover plan build review ship capture cycle resume; do
  f="$REPO_ROOT/skills/$skill_dir/SKILL.md"
  [ -f "$f" ] || continue
  if ! grep -q '^cli_support:' "$f"; then
    fail "missing cli_support: $skill_dir"
  fi
done
pass "all cycle skills have cli_support frontmatter"

# Frontmatter has layer: foundation
for skill_dir in sense define discover plan build review ship capture cycle resume; do
  f="$REPO_ROOT/skills/$skill_dir/SKILL.md"
  [ -f "$f" ] || continue
  layer=$(grep '^layer:' "$f" | head -1 | awk '{print $2}')
  if [ "$layer" != "foundation" ]; then
    fail "wrong layer for $skill_dir: got '$layer', expected 'foundation'"
  fi
done
pass "all cycle skills have layer: foundation"

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All cycle-skills-present tests PASSED"
  exit 0
else
  echo "Some cycle-skills-present tests FAILED"
  exit 1
fi
