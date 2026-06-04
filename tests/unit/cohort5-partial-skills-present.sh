#!/usr/bin/env bash
# tests/unit/cohort5-partial-skills-present.sh
#
# Verifies v3.6 cohort 5-partial skills present + frontmatter.
# Cohort 5-partial ships: safe-install (5.1) + az-discover-presale (5.4-slot) +
# security-genomlysning (5.5-slot) + compliance-gate (6.10).
# tag: v3.6 cohort-5-partial

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/cohort5-partial-skills-present.sh"
echo "==========================================="

# Generic cohort-5 skills that stay (az-discover-presale + security-genomlysning
# moved to lintel-caip-pack in the v4.7 CAIP extraction)
COHORT5_SKILLS=(safe-install compliance-gate)
for skill in "${COHORT5_SKILLS[@]}"; do
  f="$REPO_ROOT/skills/$skill/SKILL.md"
  if [ -f "$f" ]; then
    name=$(grep '^name:' "$f" | head -1 | awk '{print $2}')
    if [ "$name" = "$skill" ]; then
      pass "cohort 5-partial skill: $skill"
    else
      fail "cohort 5-partial skill frontmatter mismatch: $skill"
    fi

    # Required frontmatter (per Cohort 1 frontmatter-lint)
    for field in name layer description color tools voice cli_support; do
      if ! grep -q "^${field}:" "$f"; then
        fail "$skill SKILL.md missing frontmatter field: $field"
      fi
    done
  else
    fail "cohort 5-partial SKILL.md missing: $f"
  fi
done

# compliance-gate is now pack-driven (resolves compliance.hooks from the active
# pack); it no longer hardcodes MS gate names — verify it delegates to the pack.
CG="$REPO_ROOT/skills/compliance-gate/SKILL.md"
if [ -f "$CG" ]; then
  if grep -q "resolve_pack_field compliance.hooks\|compliance.hooks" "$CG"; then
    pass "compliance-gate is pack-driven (resolves compliance.hooks)"
  else
    fail "compliance-gate not pack-driven (expected compliance.hooks resolution)"
  fi
fi

# safe-install backups directory pattern
SI="$REPO_ROOT/skills/safe-install/SKILL.md"
if [ -f "$SI" ]; then
  if grep -q "snapshot\|backup" "$SI"; then
    pass "safe-install har backup-pattern (operator-request 5.1)"
  else
    fail "safe-install saknar backup-pattern"
  fi
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All cohort 5-partial tests PASSED"
  exit 0
else
  echo "Some cohort 5-partial tests FAILED"
  exit 1
fi
