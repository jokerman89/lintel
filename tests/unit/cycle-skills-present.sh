#!/usr/bin/env bash
# tests/unit/cycle-skills-present.sh
#
# Verifies v3.5 Lintel cycle skills are present + valid frontmatter.
# tag: v3.5 cycle

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/cycle-skills-present.sh"
echo "=================================="

# 8 phase-skills
PHASES=(sense define discover plan build review ship capture)
for phase in "${PHASES[@]}"; do
  f="$REPO_ROOT/skills/li-$phase/SKILL.md"
  if [ -f "$f" ]; then
    name=$(grep '^name:' "$f" | head -1 | awk '{print $2}')
    expected="li-$phase"
    if [ "$name" = "$expected" ]; then
      pass "phase skill: $expected"
    else
      fail "phase skill: $expected (frontmatter name mismatch: got '$name')"
    fi
  else
    fail "phase skill missing: $f"
  fi
done

# 2 orchestrator skills
for orch in cycle resume; do
  f="$REPO_ROOT/skills/li-$orch/SKILL.md"
  [ -f "$f" ] && pass "orchestrator: li-$orch" || fail "orchestrator missing: li-$orch"
done

# 4 composite shortcuts
for comp in fix research plan-and-build review-and-ship; do
  f="$REPO_ROOT/skills/li-$comp/SKILL.md"
  [ -f "$f" ] && pass "composite: li-$comp" || fail "composite missing: li-$comp"
done

# Frontmatter has cli_support
for skill_dir in li-sense li-define li-discover li-plan li-build li-review li-ship li-capture li-cycle li-resume; do
  f="$REPO_ROOT/skills/$skill_dir/SKILL.md"
  [ -f "$f" ] || continue
  if grep -q '^cli_support:' "$f"; then
    : # ok
  else
    fail "missing cli_support: $skill_dir"
  fi
done
pass "all cycle skills have cli_support frontmatter"

# Frontmatter has layer: foundation
for skill_dir in li-sense li-define li-discover li-plan li-build li-review li-ship li-capture li-cycle li-resume; do
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
