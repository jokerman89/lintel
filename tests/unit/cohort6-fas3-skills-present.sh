#!/usr/bin/env bash
# tests/unit/cohort6-fas3-skills-present.sh
#
# Verifies v3.6 cohort 6 + v3.5 phase 3 skills present + frontmatter.
# Cohort 6 ships: instruction-parity-check (6.2).
# v3.5 phase 3 ships: generate-style-learn (style extraction).
# tag: v3.6 cohort-6 fas3

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/cohort6-fas3-skills-present.sh"
echo "========================================="

# Cohort 6 + phase 3 skills
COHORT6_FAS3_SKILLS=(instruction-parity-check generate-style-learn)
for skill in "${COHORT6_FAS3_SKILLS[@]}"; do
  f="$REPO_ROOT/skills/$skill/SKILL.md"
  if [ -f "$f" ]; then
    name=$(grep '^name:' "$f" | head -1 | awk '{print $2}')
    if [ "$name" = "$skill" ]; then
      pass "skill present: $skill"
    else
      fail "skill frontmatter mismatch: $skill"
    fi

    # Required frontmatter (per Cohort 1 frontmatter-lint)
    for field in name layer description color tools voice cli_support; do
      if ! grep -q "^${field}:" "$f"; then
        fail "$skill SKILL.md missing frontmatter field: $field"
      fi
    done
  else
    fail "skill SKILL.md missing: $f"
  fi
done

# instruction-parity-check references all 6 instruction files
IPC="$REPO_ROOT/skills/instruction-parity-check/SKILL.md"
if [ -f "$IPC" ]; then
  for ref in "CLAUDE.md" "AGENTS.md" "GEMINI.md" "copilot-instructions.md"; do
    if grep -q "$ref" "$IPC"; then
      pass "instruction-parity-check references $ref"
    else
      fail "instruction-parity-check missing reference: $ref"
    fi
  done

  # 4 key sections mentioned
  for section in "compliance" "voice tier" "scaffolding" "auto"; do
    if grep -qi "$section" "$IPC"; then
      pass "instruction-parity-check checks $section section"
    else
      fail "instruction-parity-check missing $section check"
    fi
  done
fi

# generate-style-learn supports multiple formats
GSL="$REPO_ROOT/skills/generate-style-learn/SKILL.md"
if [ -f "$GSL" ]; then
  for fmt in pptx docx html; do
    if grep -qiE "$fmt|$(echo $fmt | tr 'a-z' 'A-Z')" "$GSL"; then
      pass "generate-style-learn supports $fmt format"
    else
      fail "generate-style-learn missing $fmt format support"
    fi
  done

  # Output schema documented
  if grep -q "palettes\|STYLE.md" "$GSL"; then
    pass "generate-style-learn documents output paths"
  else
    fail "generate-style-learn missing output spec"
  fi
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All cohort-6 + phase 3 tests PASSED"
  exit 0
else
  echo "Some cohort-6 + phase 3 tests FAILED"
  exit 1
fi
