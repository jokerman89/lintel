#!/usr/bin/env bash
# tests/shape/frontmatter-lint-all.sh
# Asserts: every SKILL.md and agent .md has required frontmatter fields.
# Delegates to existing tests/unit/frontmatter-lint.sh if present.
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/frontmatter-lint-all.sh"
echo "====================================="

REQUIRED_SKILL_FIELDS=(name layer description color tools voice cli_support)
REQUIRED_AGENT_FIELDS=(name category description color tools voice cli_support)

# Check all SKILL.md files
SKILL_FILES=()
while IFS= read -r f; do SKILL_FILES+=("$f"); done < <(find "$REPO_ROOT/skills" -name "SKILL.md" 2>/dev/null)
pass "Found ${#SKILL_FILES[@]} SKILL.md files"

BAD_SKILLS=()
for f in "${SKILL_FILES[@]}"; do
  miss=""
  for field in "${REQUIRED_SKILL_FIELDS[@]}"; do
    if ! grep -qE "^${field}:" "$f"; then
      miss="$miss $field"
    fi
  done
  if [ -n "$miss" ]; then
    BAD_SKILLS+=("$f:$miss")
  fi
done

if [ "${#BAD_SKILLS[@]}" -eq 0 ]; then
  pass "All SKILL.md files have required frontmatter fields"
else
  fail "${#BAD_SKILLS[@]} SKILL.md files missing required fields:"
  for e in "${BAD_SKILLS[@]}"; do echo "    - $e"; done
fi

# Check all agent .md files (under agents/<category>/)
AGENT_FILES=()
while IFS= read -r f; do AGENT_FILES+=("$f"); done < <(find "$REPO_ROOT/agents" -name "*.md" 2>/dev/null | grep -v README | grep -v "_TEMPLATE")
pass "Found ${#AGENT_FILES[@]} agent files"

BAD_AGENTS=()
for f in "${AGENT_FILES[@]}"; do
  miss=""
  for field in "${REQUIRED_AGENT_FIELDS[@]}"; do
    if ! grep -qE "^${field}:" "$f"; then
      miss="$miss $field"
    fi
  done
  if [ -n "$miss" ]; then
    BAD_AGENTS+=("$f:$miss")
  fi
done

if [ "${#BAD_AGENTS[@]}" -eq 0 ]; then
  pass "All agent files have required frontmatter fields"
else
  fail "${#BAD_AGENTS[@]} agent files missing required fields:"
  for e in "${BAD_AGENTS[@]:0:10}"; do echo "    - $e"; done
  [ "${#BAD_AGENTS[@]}" -gt 10 ] && echo "    ... and $((${#BAD_AGENTS[@]} - 10)) more"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All frontmatter-lint-all assertions PASSED"; exit 0
else echo "Some frontmatter-lint-all assertions FAILED"; exit 1; fi
