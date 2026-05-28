#!/usr/bin/env bash
# tests/unit/observation-spine-skills-present.sh
#
# Verifies v3.6 cohort 2 observation-spine skills are present + valid frontmatter.
# Cohort 2 ships: usage-log + hooks-status + lessons-surface + catalog (foundation layer).
# tag: v3.6 cohort-2 observation-spine

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/observation-spine-skills-present.sh"
echo "=============================================="

# 4 observation-spine skills
OBSERVATION_SKILLS=(usage-log hooks-status lessons-surface catalog)
for skill in "${OBSERVATION_SKILLS[@]}"; do
  f="$REPO_ROOT/skills/$skill/SKILL.md"
  if [ -f "$f" ]; then
    name=$(grep '^name:' "$f" | head -1 | awk '{print $2}')
    layer=$(grep '^layer:' "$f" | head -1 | awk '{print $2}')
    color=$(grep '^color:' "$f" | head -1 | awk '{print $2}')

    if [ "$name" = "$skill" ] && [ "$layer" = "foundation" ]; then
      pass "observation-spine skill: $skill (name + layer match)"
    else
      fail "observation-spine skill frontmatter: $skill (name=$name, layer=$layer)"
    fi

    # Color consistency (yellow = observation family per v3.6 convention)
    if [ "$color" = "yellow" ]; then
      pass "observation-spine: $skill has color: yellow (family-convention)"
    else
      fail "observation-spine: $skill color=$color, expected 'yellow'"
    fi
  else
    fail "observation-spine SKILL.md missing: $f"
  fi
done

# Verify SENSE auto-invokes lessons-surface
SENSE_FILE="$REPO_ROOT/skills/sense/SKILL.md"
if [ -f "$SENSE_FILE" ]; then
  if grep -q "lessons-surface" "$SENSE_FILE"; then
    pass "sense/SKILL.md references lessons-surface (Step 0 integration)"
  else
    fail "sense/SKILL.md does NOT reference lessons-surface — L-001/L-002 loop NOT closed"
  fi
fi

# Verify CYCLE has phase-progress output
CYCLE_FILE="$REPO_ROOT/skills/cycle/SKILL.md"
if [ -f "$CYCLE_FILE" ]; then
  if grep -q "phase-progress\|Phase N/M\|Phase-progress" "$CYCLE_FILE"; then
    pass "cycle/SKILL.md has phase-progress output (1.5)"
  else
    fail "cycle/SKILL.md missing phase-progress output (1.5)"
  fi
fi

# Catalog CI workflow present
CATALOG_WORKFLOW="$REPO_ROOT/.github/workflows/catalog.yml"
if [ -f "$CATALOG_WORKFLOW" ]; then
  pass "catalog auto-regenerate CI workflow present"
else
  fail "catalog auto-regenerate CI workflow missing"
fi

# All required frontmatter fields (per Cohort 1 frontmatter-lint)
for skill in "${OBSERVATION_SKILLS[@]}"; do
  f="$REPO_ROOT/skills/$skill/SKILL.md"
  [ -f "$f" ] || continue
  for field in name layer description color tools voice cli_support; do
    if ! grep -q "^${field}:" "$f"; then
      fail "$skill SKILL.md missing frontmatter field: $field"
    fi
  done
done
pass "all observation-spine skills have required frontmatter fields"

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All observation-spine tests PASSED"
  exit 0
else
  echo "Some observation-spine tests FAILED"
  exit 1
fi
