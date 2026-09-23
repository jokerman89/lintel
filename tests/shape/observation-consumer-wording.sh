#!/usr/bin/env bash
# component: observation-consumer-wording-test
# implements: ADR-0008
# intent: .claude/plans/universal-implementation/packages/P08.md
# constraints: text contract only; observation readers may report absence, never a verdict from it
# last_intent_review: 2026-09-23
# Asserts the observation readers issue no dead, never-invoked or "nothing ran"
# verdict, including the hooks-status frontmatter description.
# tag: shape observation wording
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/observation-consumer-wording.sh"
echo "==========================================="

VERDICT='\bdead\b|active-vs-dead|never[- ]invoked|nothing (ran|has been|was) (run|logged|audit-logged|recorded)|nothing ran'
for skill in hooks-status audit usage-log retro maintenance; do
  file="$REPO_ROOT/skills/$skill/SKILL.md"
  if [ ! -f "$file" ]; then
    fail "$skill: SKILL.md missing"
    continue
  fi
  # The contract's own negation ("absence is not evidence that nothing ran") is not a verdict.
  hits="$(sed -E 's/not evidence that nothing ran//g' "$file" | grep -niE "$VERDICT" || true)"
  if [ -n "$hits" ]; then
    fail "$skill issues an absence verdict:"
    printf '%s\n' "$hits" | sed 's/^/      /'
  else
    pass "$skill reports absence as unobserved, not as a verdict"
  fi
done

description="$(sed -n 's/^description:[[:space:]]*//p' "$REPO_ROOT/skills/hooks-status/SKILL.md" | head -1)"
if [ -n "$description" ] && ! printf '%s\n' "$description" | grep -qiE "$VERDICT|firing|healthy"; then
  pass "hooks-status description carries no activity verdict"
else
  fail "hooks-status description: ${description:-missing}"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All observation-consumer-wording assertions PASSED"; exit 0
else echo "Some observation-consumer-wording assertions FAILED"; exit 1; fi
