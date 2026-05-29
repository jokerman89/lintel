#!/usr/bin/env bash
# tests/shape/deprecated-aliases-resolve.sh
# Asserts: every deprecated_aliases entry in a SKILL.md maps to a real new-name skill.
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/deprecated-aliases-resolve.sh"
echo "==========================================="

# Find all skills declaring deprecated_aliases
declared=0
while IFS= read -r f; do
  declared=$((declared + 1))
  # Resolve: the file's own `name:` field is the new-name
  new_name=$(grep -E "^name:" "$f" | head -1 | awk '{print $2}')
  if [ -d "$REPO_ROOT/skills/$new_name" ]; then
    pass "deprecated_aliases in $(basename "$(dirname "$f")")/SKILL.md → new name '$new_name' (resolved)"
  else
    fail "deprecated_aliases in $(basename "$(dirname "$f")")/SKILL.md → new name '$new_name' DOES NOT RESOLVE"
  fi
done < <(grep -rl "^deprecated_aliases:" "$REPO_ROOT/skills" 2>/dev/null)

if [ "$declared" -eq 0 ]; then
  pass "No deprecated_aliases entries to verify (clean state)"
else
  pass "Checked $declared skill(s) declaring deprecated_aliases"
fi

# Also check config/aliases.yaml — only the skill_aliases: section.
# env_var_aliases: and plugin_slug_aliases: have their own resolution semantics
# (env vars and plugin slugs are not directories under skills/).
ALIASES="$REPO_ROOT/config/aliases.yaml"
if [ -f "$ALIASES" ]; then
  while IFS= read -r new_name; do
    if [ -d "$REPO_ROOT/skills/$new_name" ]; then
      pass "config/aliases.yaml skill_aliases entry → '$new_name' (resolved)"
    else
      fail "config/aliases.yaml skill_aliases entry → '$new_name' DOES NOT RESOLVE"
    fi
  done < <(awk '
    /^skill_aliases:/ { in_skill=1; next }
    /^[a-z_]+_aliases:/ { in_skill=0 }
    in_skill && /^[[:space:]]+new:/ { sub("^[[:space:]]+new:[[:space:]]*", ""); print }
  ' "$ALIASES" | sort -u)
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All deprecated-aliases-resolve assertions PASSED"; exit 0
else echo "Some deprecated-aliases-resolve assertions FAILED"; exit 1; fi
