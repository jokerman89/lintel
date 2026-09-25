#!/usr/bin/env bash
# tests/shape/deprecated-aliases-resolve.sh
# Asserts: declared alias targets exist and published expiry dates have not elapsed.
# Frontmatter and central aliases remain independently supported declaration sources.
# tag: shape aliases

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
ALIASES="$REPO_ROOT/config/aliases.yaml"
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/deprecated-aliases-resolve.sh"
echo "==========================================="

# Find all skills declaring deprecated_aliases
declared=0
while IFS= read -r f; do
  declared=$((declared + 1))
  # Resolve: the file's own `name:` field is the new-name
  new_name=$(awk 'NR == 1 {next} /^---$/ {exit} /^name:/ {print $2; exit}' "$f" | tr -d '\r')
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
if [ -f "$ALIASES" ]; then
  if ! awk -v today="$(date -u +%Y-%m-%d)" '
    /^[[:space:]]*-[[:space:]]*old:/ { name=$NF }
    /^[[:space:]]*removal_at:/ {
      removal=$0; sub(/^[[:space:]]*removal_at:[[:space:]]*/, "", removal)
      sub(/[[:space:]]+#.*/, "", removal)
      gsub(/["\047\r]/, "", removal); sub(/[[:space:]]+$/, "", removal)
      if (removal !~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/) {
        printf "  FAIL: alias %s has an invalid removal date\n", name
        failed=1; next
      }
      if (removal <= today) {
        printf "  FAIL: expired alias %s (removal_at %s)\n", name, removal
        failed=1
      }
    }
    END { exit failed }
  ' "$ALIASES"; then FAILED=1; fi
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
else
  fail "config/aliases.yaml is missing"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All deprecated-aliases-resolve assertions PASSED"; exit 0
else echo "Some deprecated-aliases-resolve assertions FAILED"; exit 1; fi
