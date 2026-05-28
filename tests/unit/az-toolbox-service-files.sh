#!/usr/bin/env bash
# tests/unit/az-toolbox-service-files.sh
#
# Verifies az-tldr service files follow template structure.
# Active service files must have all 15 sections + valid frontmatter.
# tag: v3.5 azure-toolbox

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/az-toolbox-service-files.sh"
echo "======================================"

# 1. Toolbox structure
[ -d "$REPO_ROOT/skills/az-tldr" ] && pass "skills/az-tldr/ exists" || fail "missing skills/az-tldr/"
[ -f "$REPO_ROOT/skills/az-tldr/SKILL.md" ] && pass "az-tldr/SKILL.md exists" || fail "missing SKILL.md"
[ -d "$REPO_ROOT/skills/az-tldr/services" ] && pass "services/ dir exists" || fail "missing services/"
[ -d "$REPO_ROOT/skills/az-tldr/sections" ] && pass "sections/ dir exists" || fail "missing sections/"
[ -f "$REPO_ROOT/skills/az-tldr/agent-mapping.yaml" ] && pass "agent-mapping.yaml exists" || fail "missing agent-mapping.yaml"
[ -f "$REPO_ROOT/skills/az-tldr/services/_template.md" ] && pass "_template.md exists" || fail "missing _template.md"
[ -f "$REPO_ROOT/skills/az-tldr/services/README.md" ] && pass "services/README.md exists" || fail "missing services/README.md"
[ -f "$REPO_ROOT/skills/az-tldr/sections/README.md" ] && pass "sections/README.md exists" || fail "missing sections/README.md"

# 2. SKILL.md frontmatter
SKILL_FILE="$REPO_ROOT/skills/az-tldr/SKILL.md"
if [ -f "$SKILL_FILE" ]; then
  for field in name layer description color tools voice cli_support; do
    if grep -q "^${field}:" "$SKILL_FILE"; then
      :
    else
      fail "az-tldr/SKILL.md missing frontmatter: $field"
    fi
  done

  name=$(grep '^name:' "$SKILL_FILE" | head -1 | awk '{print $2}')
  if [ "$name" = "az-tldr" ]; then
    pass "SKILL.md name field correct"
  else
    fail "SKILL.md name='$name', expected 'az-tldr'"
  fi

  layer=$(grep '^layer:' "$SKILL_FILE" | head -1 | awk '{print $2}')
  if [ "$layer" = "ms-team" ]; then
    pass "SKILL.md layer=ms-team"
  else
    fail "SKILL.md layer='$layer', expected 'ms-team'"
  fi
fi

# 3. Active service files have all sections
ACTIVE_SERVICES=(expressroute)
for service in "${ACTIVE_SERVICES[@]}"; do
  f="$REPO_ROOT/skills/az-tldr/services/${service}.md"
  if [ ! -f "$f" ]; then
    fail "active service missing: $service"
    continue
  fi

  # Frontmatter checks
  for field in service service_id category caf_pillars waf_pillars as_of subagent_mapping; do
    if grep -q "^${field}:" "$f"; then
      :
    else
      fail "$service.md missing frontmatter: $field"
    fi
  done

  # Required 15 sections (§1 through §15)
  missing_sections=()
  for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
    if grep -qE "^## §${n} " "$f"; then
      :
    else
      missing_sections+=("$n")
    fi
  done

  if [ ${#missing_sections[@]} -eq 0 ]; then
    pass "$service.md has all 15 sections"
  else
    fail "$service.md missing sections: ${missing_sections[*]}"
  fi

  # Content age check (warn-only)
  as_of=$(grep '^as_of:' "$f" | head -1 | awk '{print $2}')
  if [ -n "$as_of" ]; then
    # Approximate age (skip on Windows bash if date parsing differs)
    pass "$service.md as_of: $as_of"
  fi
done

# 4. agent-mapping.yaml has entries for active services
MAPPING_FILE="$REPO_ROOT/skills/az-tldr/agent-mapping.yaml"
if [ -f "$MAPPING_FILE" ]; then
  for service in "${ACTIVE_SERVICES[@]}"; do
    if grep -q "^  ${service}:" "$MAPPING_FILE"; then
      pass "agent-mapping has entry: $service"
    else
      fail "agent-mapping missing entry: $service"
    fi
  done

  # Check role_overlays section
  if grep -q "^role_overlays:" "$MAPPING_FILE"; then
    pass "agent-mapping has role_overlays section"
  else
    fail "agent-mapping missing role_overlays"
  fi
fi

# 5. Sections README references all 15 sections in glossary table
SECTIONS_README="$REPO_ROOT/skills/az-tldr/sections/README.md"
if [ -f "$SECTIONS_README" ]; then
  missing_glossary=()
  for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
    if grep -qE "§${n}" "$SECTIONS_README"; then
      :
    else
      missing_glossary+=("§$n")
    fi
  done

  if [ ${#missing_glossary[@]} -eq 0 ]; then
    pass "sections/README.md has all 15 sections in glossary"
  else
    fail "sections/README.md missing glossary entries: ${missing_glossary[*]}"
  fi
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All az-toolbox tests PASSED"
  exit 0
else
  echo "Some az-toolbox tests FAILED"
  exit 1
fi
