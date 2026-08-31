#!/usr/bin/env bash
# tests/unit/aliases-resolve.sh
#
# Verifies the v3.6 Cohort 4 alias mechanism:
# - config/aliases.yaml well-formed + populated with WS-4a/b decisions
# - bin/_aliases.sh sources cleanly + resolve_env_var works
# - All 4 renamed skills exist at new path + frontmatter name matches
# - deprecated_aliases field present on renamed skills
# tag: v3.6 cohort-4 aliases

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/aliases-resolve.sh"
echo "============================="

# Step 1 — config/aliases.yaml present + well-formed
ALIASES="$REPO_ROOT/config/aliases.yaml"
if [ -f "$ALIASES" ]; then
  pass "config/aliases.yaml present"

  for section in "skill_aliases:" "env_var_aliases:" "plugin_slug_aliases:"; do
    if grep -q "^$section" "$ALIASES"; then
      pass "aliases.yaml has section: $section"
    else
      fail "aliases.yaml missing section: $section"
    fi
  done

  # version + as_of metadata
  if grep -qE "^version:[[:space:]]*1" "$ALIASES"; then
    pass "aliases.yaml has version: 1"
  else
    fail "aliases.yaml missing or wrong version"
  fi
else
  fail "config/aliases.yaml missing"
  exit 1
fi

# Step 2 — bin/_aliases.sh sources cleanly
HELPER="$REPO_ROOT/bin/_aliases.sh"
if [ -f "$HELPER" ]; then
  pass "bin/_aliases.sh present"

  if head -1 "$HELPER" | grep -qE "^#!/usr/bin/env bash"; then
    pass "bin/_aliases.sh has bash shebang"
  fi

  # Source in subshell to avoid polluting test environment
  if ( source "$HELPER" 2>/dev/null && declare -F resolve_env_var >/dev/null ); then
    pass "bin/_aliases.sh sources cleanly + exposes resolve_env_var"
  else
    fail "bin/_aliases.sh source or resolve_env_var missing"
  fi

  if ( source "$HELPER" 2>/dev/null && declare -F list_skill_aliases >/dev/null ); then
    pass "bin/_aliases.sh exposes list_skill_aliases"
  else
    fail "bin/_aliases.sh list_skill_aliases missing"
  fi
fi

# Step 3 — resolve_env_var behavior (use isolated HOME)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

(
  # Markerless sandbox repo root: without a v5 layout marker the audit write
  # falls back to LINTEL_AUDIT_DIR (a migrated repo root would route it to
  # <repo>/.claude/runtime/audit/). The alias map is pinned explicitly since
  # its default derives from LINTEL_REPO_ROOT.
  export LINTEL_REPO_ROOT="$TMP"
  export LINTEL_ALIASES_FILE="$REPO_ROOT/config/aliases.yaml"
  export HOME="$TMP"
  export LINTEL_AUDIT_DIR="$TMP/.lintel/audit"
  source "$HELPER"

  # Case A: NEW_VAR set → returns its value
  export LINTEL_HOME="/test/value"
  result=$(resolve_env_var LINTEL_HOME)
  if [ "$result" = "/test/value" ]; then
    echo "  PASS: resolve_env_var returns NEW value when set"
  else
    echo "  FAIL: resolve_env_var got '$result' expected '/test/value'"
    exit 1
  fi

  # Case B: NEW unset, OLD set → falls back to OLD with warning
  unset LINTEL_HOME
  export JSTACK_HOME="/old/value"
  result=$(resolve_env_var LINTEL_HOME 2>/dev/null)
  if [ "$result" = "/old/value" ]; then
    echo "  PASS: resolve_env_var falls back to deprecated alias"
  else
    echo "  FAIL: alias-fallback returned '$result' expected '/old/value'"
    exit 1
  fi

  # Verify audit-log was written
  if [ -f "$LINTEL_AUDIT_DIR/alias-resolution.jsonl" ]; then
    if grep -q '"kind":"env_var"' "$LINTEL_AUDIT_DIR/alias-resolution.jsonl"; then
      echo "  PASS: alias-resolution audit-log written"
    else
      echo "  FAIL: audit-log present but missing env_var entry"
      exit 1
    fi
  else
    echo "  FAIL: audit-log not created at $LINTEL_AUDIT_DIR/alias-resolution.jsonl"
    exit 1
  fi

  # Case C: both unset → returns empty
  unset JSTACK_HOME LINTEL_HOME
  result=$(resolve_env_var LINTEL_HOME)
  if [ -z "$result" ]; then
    echo "  PASS: resolve_env_var returns empty when both unset"
  else
    echo "  FAIL: expected empty, got '$result'"
    exit 1
  fi
) || FAILED=1

# Step 4 — list_skill_aliases reports the 4 renames
(
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  source "$HELPER"
  output=$(list_skill_aliases)
  for pair in "match -> skill-router"; do
    if echo "$output" | grep -qF "$pair"; then
      echo "  PASS: list_skill_aliases reports: $pair"
    else
      echo "  FAIL: list_skill_aliases missing: $pair"
      exit 1
    fi
  done
) || FAILED=1

# Step 5 — Renamed skills exist at NEW paths with NEW frontmatter
declare -A RENAMES=(
  [match]=skill-router
)
for old in "${!RENAMES[@]}"; do
  new="${RENAMES[$old]}"
  new_path="$REPO_ROOT/skills/$new/SKILL.md"
  old_path="$REPO_ROOT/skills/$old/SKILL.md"

  if [ -f "$new_path" ]; then
    pass "renamed skill exists at new path: $new"
  else
    fail "renamed skill missing: $new (was $old)"
    continue
  fi

  if [ ! -d "$REPO_ROOT/skills/$old" ]; then
    pass "old skill folder removed: $old"
  else
    fail "old skill folder still exists: $old (should be deleted)"
  fi

  # Frontmatter name matches
  name=$(grep '^name:' "$new_path" | head -1 | awk '{print $2}')
  if [ "$name" = "$new" ]; then
    pass "$new frontmatter name field matches"
  else
    fail "$new frontmatter name='$name' expected '$new'"
  fi

  # deprecated_aliases field present + lists old name
  if grep -q "deprecated_aliases:" "$new_path" && grep -q "$old" "$new_path"; then
    pass "$new declares deprecated_aliases including '$old'"
  else
    fail "$new missing deprecated_aliases or doesn't list '$old'"
  fi
done

# Step 6 — Each rename has matching entry in aliases.yaml
for old in match; do
  if grep -qE "^[[:space:]]*-[[:space:]]*old:[[:space:]]*$old\$" "$ALIASES"; then
    pass "aliases.yaml has skill_alias entry: old=$old"
  else
    fail "aliases.yaml missing skill_alias entry for old=$old"
  fi
done

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All aliases-resolve tests PASSED"
  exit 0
else
  echo "Some aliases-resolve tests FAILED"
  exit 1
fi
