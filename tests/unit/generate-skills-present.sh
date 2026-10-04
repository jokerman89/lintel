#!/usr/bin/env bash
# tests/unit/generate-skills-present.sh
#
# Verifies generation skill presence/frontmatter: 1 orchestrator, 4 shared
# sub-skills, concrete PDF/XLSX methods and the Visio unavailable-writer preflight.
# Existing PPT/web/Word builders are checked separately. Source presence does
# not establish native/runtime verification.
#
# tag: v3.5 doc-generation-pipeline

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/generate-skills-present.sh"
echo "====================================="

# 1. Orchestrator
ORCHESTRATOR="generate"
f="$REPO_ROOT/skills/$ORCHESTRATOR/SKILL.md"
if [ -f "$f" ]; then
  name=$(grep '^name:' "$f" | head -1 | awk '{print $2}')
  layer=$(grep '^layer:' "$f" | head -1 | awk '{print $2}')
  if [ "$name" = "$ORCHESTRATOR" ] && [ "$layer" = "foundation" ]; then
    pass "orchestrator: $ORCHESTRATOR (name + layer match)"
  else
    fail "orchestrator frontmatter: name=$name, layer=$layer (expected $ORCHESTRATOR + foundation)"
  fi
else
  fail "orchestrator SKILL.md missing: $f"
fi

# 2. Shared sub-skills (4)
SHARED_SUBSKILLS=(generate-outline generate-write generate-design generate-qa)
for skill in "${SHARED_SUBSKILLS[@]}"; do
  f="$REPO_ROOT/skills/$skill/SKILL.md"
  if [ -f "$f" ]; then
    name=$(grep '^name:' "$f" | head -1 | awk '{print $2}')
    layer=$(grep '^layer:' "$f" | head -1 | awk '{print $2}')
    if [ "$name" = "$skill" ] && [ "$layer" = "foundation" ]; then
      pass "shared sub-skill: $skill (name + layer match)"
    else
      fail "shared sub-skill frontmatter: $skill (name=$name, layer=$layer)"
    fi
  else
    fail "shared sub-skill SKILL.md missing: $f"
  fi
done

# 3. Format source state: concrete PDF/XLSX methods; Visio has no bundled writer
SLOT_SKILLS=(generate-pdf generate-xlsx generate-visio)
for skill in "${SLOT_SKILLS[@]}"; do
  f="$REPO_ROOT/skills/$skill/SKILL.md"
  if [ -f "$f" ]; then
    name=$(grep '^name:' "$f" | head -1 | awk '{print $2}')
    layer=$(grep '^layer:' "$f" | head -1 | awk '{print $2}')

    # Frontmatter check
    if [ "$name" = "$skill" ] && [ "$layer" = "foundation" ]; then
      pass "slot: $skill (name + layer match)"
    else
      fail "slot frontmatter: $skill (name=$name, layer=$layer)"
    fi

    if [ "$skill" = "generate-visio" ]; then
      # Require truthful refusal/format proof, not an empty workflow or magic marker.
      for condition in 'no bundled writer' 'actual requested format' \
        'available authorized writer' 'editable reopen' 'connectors' 'labels' \
        'required inspection' 'No image-as-VSDX' 'QA handoff is not' \
        'blocks only that output'; do
        if grep -qF "$condition" "$f"; then
          pass "Visio preflight: $condition"
        else
          fail "Visio preflight missing: $condition"
        fi
      done
      if grep -qE 'python-vsdx|libvsx|qa-handoff successful|AI generates fresh per invocation|~/\.lintel/brand/visio-templates' "$f"; then
        fail "Visio promises an unapproved writer, personal template or false completion"
      else
        pass "Visio has no invented writer, personal template or handoff-only success"
      fi
    elif grep -qi "TEMPLATE ONLY" "$f"; then
      fail "concrete method: $skill must not declare TEMPLATE ONLY"
    else
      pass "concrete method: $skill does not declare TEMPLATE ONLY"
    fi
  else
    fail "slot SKILL.md missing: $f"
  fi
done

# Concrete methods must retain their helpers and existing integration entry points.
CONCRETE_SUPPORT=(
  skills/generate-pdf/scripts/prepare_html.py
  skills/generate-pdf/scripts/print_pdf.mjs
  skills/generate-xlsx/scripts/check_xlsx.py
  tests/integration/document-pdf.py
  tests/integration/document-pdf.sh
  tests/integration/document-pdf.test.mjs
  tests/integration/document-workbook.py
  tests/integration/document-workbook.sh
)
for support in "${CONCRETE_SUPPORT[@]}"; do
  if [ -f "$REPO_ROOT/$support" ]; then
    pass "concrete method support: $support"
  else
    fail "concrete method support missing: $support"
  fi
done

# 4. Frontmatter consistency across the generate-family
ALL_GENERATE=(generate generate-outline generate-write generate-design generate-qa generate-pdf generate-xlsx generate-visio)
for skill in "${ALL_GENERATE[@]}"; do
  f="$REPO_ROOT/skills/$skill/SKILL.md"
  [ -f "$f" ] || continue
  for field in name layer description color tools voice cli_support; do
    if ! grep -q "^${field}:" "$f"; then
      fail "$skill SKILL.md missing frontmatter field: $field"
    fi
  done
done
pass "all generate-family skills have required frontmatter fields"

# 5. Color consistency (orange across family)
for skill in "${ALL_GENERATE[@]}"; do
  f="$REPO_ROOT/skills/$skill/SKILL.md"
  [ -f "$f" ] || continue
  color=$(grep '^color:' "$f" | head -1 | awk '{print $2}')
  if [ "$color" != "orange" ]; then
    fail "$skill color=$color, expected 'orange' (generate-family convention)"
  fi
done
pass "all generate-family skills have color: orange"

# 6. agent-mapping.yaml exists + has entries for all sub-skills
MAPPING_FILE="$REPO_ROOT/skills/generate/agent-mapping.yaml"
if [ -f "$MAPPING_FILE" ]; then
  pass "agent-mapping.yaml exists"
  for skill in generate-outline generate-write generate-design generate-qa generate-pdf generate-xlsx generate-visio; do
    if grep -q "^  ${skill}:" "$MAPPING_FILE"; then
      pass "agent-mapping has entry: $skill"
    else
      fail "agent-mapping missing entry: $skill"
    fi
  done

  # role_overlays section
  if grep -q "^role_overlays:" "$MAPPING_FILE"; then
    pass "agent-mapping has role_overlays section"
  else
    fail "agent-mapping missing role_overlays section"
  fi

  # voice_gate_owner policy (per design doc Reviewer Concern #2 + #8)
  if grep -q "voice_gate_owner:" "$MAPPING_FILE"; then
    pass "agent-mapping declares voice_gate_owner (gate-execution-order)"
  else
    fail "agent-mapping missing voice_gate_owner policy"
  fi
else
  fail "agent-mapping.yaml missing"
fi

# 7. Existing legacy format-builders still present (refactor target, not yet refactored)
LEGACY_BUILDERS=(generate-ppt generate-web generate-word)
for builder in "${LEGACY_BUILDERS[@]}"; do
  f="$REPO_ROOT/skills/$builder/SKILL.md"
  if [ -f "$f" ]; then
    pass "legacy format-builder still present: $builder (refactor target for phase 2)"
  else
    fail "legacy format-builder unexpectedly removed: $builder"
  fi
done

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All generate-skills-present tests PASSED"
  exit 0
else
  echo "Some generate-skills-present tests FAILED"
  exit 1
fi
