#!/usr/bin/env bash
# tests/unit/aliases-resolve.sh
#
# Neutral fixtures verify alias precedence, warnings, audit and section boundaries.
# Production aliases have independent expiry and target checks in the shape suite.
# tag: unit aliases

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

# Source and resolve only inside the same owned fixture.
TMP="$(mktemp -d "${TMPDIR:-/tmp}/lintel-alias-test.XXXXXX")"
TMP="$(cd "$TMP" && pwd -P)"
trap 'rm -rf "$TMP"' EXIT
cat > "$TMP/aliases.yaml" <<'YAML'
version: 1
skill_aliases:
  - old: prior-workflow
    new: current-workflow
  - old: earlier-workflow
    new: another-workflow
env_var_aliases:
  - old: LINTEL_TEST_PREVIOUS
    new: LINTEL_TEST_CURRENT
  - old: LINTEL_TEST_SECOND
    new: LINTEL_TEST_CURRENT
plugin_slug_aliases:
  - old: LINTEL_TEST_PLUGIN
    new: LINTEL_TEST_OTHER
YAML
export HOME="$TMP/home" USERPROFILE="$TMP/home"
export LINTEL_HOME="$TMP/home/.lintel" LINTEL_REPO_ROOT="$TMP/repo"
export LINTEL_AUDIT_DIR="$TMP/audit" LINTEL_ALIASES_FILE="$TMP/aliases.yaml"
mkdir -p "$HOME" "$LINTEL_REPO_ROOT"

# Step 2 — bin/_aliases.sh sources cleanly
HELPER="$REPO_ROOT/bin/_aliases.sh"
if [ -f "$HELPER" ]; then
  pass "bin/_aliases.sh present"

  if head -1 "$HELPER" | grep -qE "^#!/usr/bin/env bash"; then
    pass "bin/_aliases.sh has bash shebang"
  fi

  # Source in subshell to avoid polluting test environment
  if ( source "$HELPER" && declare -F resolve_env_var >/dev/null ); then
    pass "bin/_aliases.sh sources cleanly + exposes resolve_env_var"
  else
    fail "bin/_aliases.sh source or resolve_env_var missing"
  fi

  if ( source "$HELPER" && declare -F list_skill_aliases >/dev/null ); then
    pass "bin/_aliases.sh exposes list_skill_aliases"
  else
    fail "bin/_aliases.sh list_skill_aliases missing"
  fi
fi

# Step 3 — resolve_env_var behavior
(
  source "$HELPER"

  # Current values take precedence even when an alias is populated.
  export LINTEL_TEST_CURRENT="current value" LINTEL_TEST_PREVIOUS="previous value"
  result=$(resolve_env_var LINTEL_TEST_CURRENT 2>"$TMP/warning")
  if [ "$result" = "current value" ] && [ ! -s "$TMP/warning" ] &&
      [ ! -e "$LINTEL_AUDIT_DIR/alias-resolution.jsonl" ]; then
    echo "  PASS: resolve_env_var returns NEW value when set"
  else
    echo "  FAIL: current value did not take precedence without a deprecation event"
    exit 1
  fi

  # Case B: NEW unset, OLD set → falls back to OLD with warning
  unset LINTEL_TEST_CURRENT
  result=$(resolve_env_var LINTEL_TEST_CURRENT 2>"$TMP/warning")
  if [ "$result" = "previous value" ] &&
      grep -qF 'LINTEL_TEST_PREVIOUS is deprecated' "$TMP/warning" &&
      grep -qF 'LINTEL_TEST_CURRENT' "$TMP/warning"; then
    echo "  PASS: resolve_env_var falls back to deprecated alias"
  else
    echo "  FAIL: alias fallback did not return its value and actionable warning"
    exit 1
  fi

  # Verify audit-log was written
  if [ -f "$LINTEL_AUDIT_DIR/alias-resolution.jsonl" ]; then
    if grep -q '"kind":"env_var"' "$LINTEL_AUDIT_DIR/alias-resolution.jsonl" &&
        grep -qF '"old":"LINTEL_TEST_PREVIOUS","new":"LINTEL_TEST_CURRENT"' "$LINTEL_AUDIT_DIR/alias-resolution.jsonl"; then
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
  unset LINTEL_TEST_PREVIOUS
  export LINTEL_TEST_SECOND="second value"
  result=$(resolve_env_var LINTEL_TEST_CURRENT 2>"$TMP/warning")
  [ "$result" = "second value" ] || { echo '  FAIL: later populated alias was masked'; exit 1; }
  echo '  PASS: an empty earlier alias does not mask a later mapping'
  unset LINTEL_TEST_SECOND
  result=$(resolve_env_var LINTEL_TEST_CURRENT)
  if [ -z "$result" ]; then
    echo "  PASS: resolve_env_var returns empty when both unset"
  else
    echo "  FAIL: expected empty, got '$result'"
    exit 1
  fi
) || FAILED=1

# Step 4 — fixture listing retains order and excludes other sections
(
  source "$HELPER"
  output=$(list_skill_aliases)
  expected=$'prior-workflow -> current-workflow\nearlier-workflow -> another-workflow'
  [ "$output" = "$expected" ] || { echo '  FAIL: skill alias order or section boundary changed'; exit 1; }
  for pair in "prior-workflow -> current-workflow" "earlier-workflow -> another-workflow"; do
    if echo "$output" | grep -qF "$pair"; then
      echo "  PASS: list_skill_aliases reports: $pair"
    else
      echo "  FAIL: list_skill_aliases missing: $pair"
      exit 1
    fi
  done
) || FAILED=1

# Step 5 — unrelated sections and absent registries do not create mappings
(
  source "$HELPER"
  export LINTEL_TEST_PLUGIN="not an environment alias"
  [ -z "$(resolve_env_var LINTEL_TEST_OTHER)" ] || { echo '  FAIL: plugin alias leaked into env lookup'; exit 1; }
  export LINTEL_ALIASES_FILE="$TMP/absent.yaml"
  [ -z "$(resolve_env_var LINTEL_TEST_CURRENT)" ] && [ -z "$(list_skill_aliases)" ] ||
    { echo '  FAIL: absent registry did not retain the empty-result contract'; exit 1; }
  echo '  PASS: unrelated sections and missing registry preserve resolver semantics'
  printf 'version: 1\nskill_aliases: []\nenv_var_aliases: []\nplugin_slug_aliases: []\n' > "$TMP/empty.yaml"
  export LINTEL_ALIASES_FILE="$TMP/empty.yaml" LINTEL_TEST_PREVIOUS="not selected"
  [ -z "$(resolve_env_var LINTEL_TEST_CURRENT)" ] && [ -z "$(list_skill_aliases)" ] ||
    { echo '  FAIL: empty registry resurrected a fixture alias'; exit 1; }
  echo '  PASS: retired registry entries cannot resolve through an empty registry'
) || FAILED=1

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All aliases-resolve tests PASSED"
  exit 0
else
  echo "Some aliases-resolve tests FAILED"
  exit 1
fi
