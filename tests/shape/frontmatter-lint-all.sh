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

# Optional agent frontmatter (ADR-0012): memory: + model: are recognized OPTIONAL keys.
# Unknown keys are not rejected (no strict allowlist), but when present these two must be valid.
#   memory: one of {project, user, local}  (Claude Code agent-memory scope)
#   model:  a known model id               (cheap-tier routing for mechanical agents)
VALID_MEMORY_SCOPES="project user local"
VALID_MODEL_IDS="claude-haiku-4-5-20251001 claude-sonnet-4-5-20250929 claude-opus-4-1-20250805"

BAD_MEMORY=()
BAD_MODEL=()
for f in "${AGENT_FILES[@]}"; do
  # only inspect the frontmatter line (anchored ^key:)
  mval="$(grep -m1 -E '^memory:' "$f" | sed -E 's/^memory:[[:space:]]*//; s/[[:space:]]*$//')"
  if [ -n "$mval" ]; then
    case " $VALID_MEMORY_SCOPES " in
      *" $mval "*) : ;;
      *) BAD_MEMORY+=("$f: memory='$mval'") ;;
    esac
  fi
  mdl="$(grep -m1 -E '^model:' "$f" | sed -E 's/^model:[[:space:]]*//; s/[[:space:]]*$//')"
  if [ -n "$mdl" ]; then
    case " $VALID_MODEL_IDS " in
      *" $mdl "*) : ;;
      *) BAD_MODEL+=("$f: model='$mdl'") ;;
    esac
  fi
done

if [ "${#BAD_MEMORY[@]}" -eq 0 ]; then
  pass "All agent memory: values use a valid scope (project|user|local)"
else
  fail "${#BAD_MEMORY[@]} agent files have an invalid memory: scope:"
  for e in "${BAD_MEMORY[@]}"; do echo "    - $e"; done
fi

if [ "${#BAD_MODEL[@]}" -eq 0 ]; then
  pass "All agent model: values are a known model id"
else
  fail "${#BAD_MODEL[@]} agent files have an unknown model: id:"
  for e in "${BAD_MODEL[@]}"; do echo "    - $e"; done
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All frontmatter-lint-all assertions PASSED"; exit 0
else echo "Some frontmatter-lint-all assertions FAILED"; exit 1; fi
