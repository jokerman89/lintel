#!/usr/bin/env bash
# tests/unit/role-files-valid.sh
#
# Verifies v3.5 role-lifting infrastructure: 8 role-skills + 3 default
# public roles + bin/li-roles-sync.
# Post-Väg-A: skill folder/name bare (no li- prefix). bin script keeps li- prefix.
# tag: v3.5 roles

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/role-files-valid.sh"
echo "=============================="

# 8 role-lifting skills (bare folder names)
ROLE_SKILLS=(role-activate role-deep-dive role-frame role-rotate role-deactivate roles-list role-new role-update)
for skill in "${ROLE_SKILLS[@]}"; do
  f="$REPO_ROOT/skills/$skill/SKILL.md"
  [ -f "$f" ] && pass "role-skill: $skill" || fail "role-skill missing: $skill"
done

# 3 default public roles
ROLES=(field-cto solution-architect engineering-manager)
for role in "${ROLES[@]}"; do
  f="$REPO_ROOT/roles/$role.md"
  if [ -f "$f" ]; then
    # Check frontmatter has required fields
    missing=()
    grep -q "^role_id: $role$" "$f" || missing+=("role_id")
    grep -q '^display_name:' "$f" || missing+=("display_name")
    grep -q '^scope:' "$f" || missing+=("scope")
    grep -q '^audience:' "$f" || missing+=("audience")
    grep -q '^voice_tier:' "$f" || missing+=("voice_tier")
    grep -q '^sensitivity:' "$f" || missing+=("sensitivity")
    grep -q '^last_updated:' "$f" || missing+=("last_updated")
    grep -q '^applies_to_phases:' "$f" || missing+=("applies_to_phases")
    grep -q '^companion_agents:' "$f" || missing+=("companion_agents")

    if [ ${#missing[@]} -gt 0 ]; then
      fail "$role.md missing frontmatter: ${missing[*]}"
    else
      pass "role file: $role.md (frontmatter complete)"
    fi

    # Check required sections
    for section in "# IDENTITY" "# COLD KNOWLEDGE" "# DECISION CRITERIA" "# VOICE + COMMUNICATION" "# OUTCOME LENS" "# ROLE-SPECIFIC INSIGHTS" "# COMPANION SKILLS"; do
      if ! grep -q "^$section" "$f"; then
        fail "$role.md missing section: $section"
      fi
    done

    # Default public roles must be sensitivity: public
    sens=$(grep '^sensitivity:' "$f" | head -1 | awk '{print $2}')
    if [ "$sens" != "public" ]; then
      fail "$role.md sensitivity should be 'public', got '$sens'"
    fi
  else
    fail "default role missing: roles/$role.md"
  fi
done

# bin/li-roles-sync executable (bin scripts keep li- prefix per shell convention)
if [ -x "$REPO_ROOT/bin/li-roles-sync" ]; then
  pass "bin/li-roles-sync executable"
else
  fail "bin/li-roles-sync not executable or missing"
fi

# bin/li-roles-sync has expected commands
if grep -q 'cmd_setup\|cmd_push\|cmd_pull\|cmd_status\|cmd_forget' "$REPO_ROOT/bin/li-roles-sync"; then
  pass "bin/li-roles-sync has core commands (setup/push/pull/status/forget)"
else
  fail "bin/li-roles-sync missing core command implementations"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All role-files-valid tests PASSED"
  exit 0
else
  echo "Some role-files-valid tests FAILED"
  exit 1
fi
