#!/usr/bin/env bash
# Runner failures and skips must never produce a vacuous green release.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/tests/runner" "$TMP/tests/unit"
cp "$ROOT/tests/runner/run-all.sh" "$TMP/tests/runner/run-all.sh"
RUNNER="$TMP/tests/runner/run-all.sh"

expect_rc() {
  local expected="$1"; shift
  local rc=0 output
  output=$(bash "$RUNNER" "$@" 2>&1) || rc=$?
  [ "$rc" -eq "$expected" ] || { printf 'FAIL: expected %s, got %s\n%s\n' "$expected" "$rc" "$output"; exit 1; }
}
expect_rc 2 --typo
expect_rc 2 --scope
expect_rc 1
printf 'echo "  SKIP: unavailable dependency"\n' > "$TMP/tests/unit/fixture.sh"
expect_rc 1
printf 'echo "  PASS: useful assertion"\necho "  SKIP: optional assertion"\n' > "$TMP/tests/unit/fixture.sh"
expect_rc 0
expect_rc 1 --require-all
printf 'echo "  PASS: useful assertion"\n' > "$TMP/tests/unit/fixture.sh"
expect_rc 0 --require-all
expect_rc 1 --tag missing
printf '# TAGS: unit\necho "  PASS: tagged assertion"\n' > "$TMP/tests/unit/fixture.sh"
expect_rc 0 --tag unit
expect_rc 1 --tag uni
printf 'echo "Ran 3 tests in 0.001s"\necho "OK (skipped=1)"\n' > "$TMP/tests/unit/fixture.sh"
expect_rc 0
expect_rc 1 --require-all
printf 'echo "Ran 1 test in 0.001s"\necho "OK (skipped=1)"\n' > "$TMP/tests/unit/fixture.sh"
expect_rc 1
printf 'exit 7\n' > "$TMP/tests/unit/fixture.sh"
expect_rc 1
cat > "$TMP/tests/unit/fixture.sh" <<'EOF'
printf '%s\n' 'C:\new\target\profile.json' 'literal \c must not truncate' 'last failure line'
exit 7
EOF
expected_output=$(bash "$TMP/tests/unit/fixture.sh" 2>&1) || test "$?" -eq 7
rc=0
actual_output=$(bash "$RUNNER" 2>&1) || rc=$?
[ "$rc" -eq 1 ] || { printf 'FAIL: diagnostic fixture returned %s\n' "$rc"; exit 1; }
[[ "$actual_output" == *"$expected_output"* ]] || {
  printf 'FAIL: runner changed literal failure output\n%s\n' "$actual_output"
  exit 1
}

mkdir -p "$TMP/tests/shape"
cp "$ROOT/tests/shape/manifest-identity.sh" "$TMP/tests/shape/manifest-identity.sh"
(
  HIDDEN_COMMANDS=jq
  export HIDDEN_COMMANDS
  command() {
    if [ "$#" -eq 2 ] && [ "$1" = "-v" ]; then
      case ":$HIDDEN_COMMANDS:" in *":$2:"*) return 1 ;; esac
    fi
    builtin command "$@"
  }
  export -f command
  unavailable_failures=0
  expect_partial() {
    local scope="$1" message="$2" forbidden="${3:-}" entry="${4:-}" detail="${5:-}" rc=0 output
    output=$(bash "$RUNNER" --scope "$scope" --require-all 2>&1) || rc=$?
    if [ "$rc" -ne 1 ] || [[ "$output" != *"$message"* || "$output" != *"Partial: 1 "* ]]; then
      printf 'FAIL: unavailable assertions were not reported as partial coverage\n%s\n' "$output"
      unavailable_failures=$((unavailable_failures + 1))
    fi
    output=$(bash "$RUNNER" --scope "$scope" 2>&1) || {
      printf 'FAIL: non-strict partial checks failed\n%s\n' "$output"
      unavailable_failures=$((unavailable_failures + 1))
    }
    if [ -n "$forbidden" ]; then
      output=$(bash "$entry" </dev/null 2>&1) || {
        printf 'FAIL: standalone partial guard failed\n%s\n' "$output"
        unavailable_failures=$((unavailable_failures + 1))
      }
      if [[ "$output" == *"$forbidden"* ]]; then
        printf 'FAIL: unavailable assertions claimed success\n%s\n' "$output"
        unavailable_failures=$((unavailable_failures + 1))
      fi
      if [ -n "$detail" ] && [[ "$output" != *"$detail"* ]]; then
        printf 'FAIL: an additional unavailable check was silently omitted\n%s\n' "$output"
        unavailable_failures=$((unavailable_failures + 1))
      fi
    fi
  }
  expect_partial shape "SKIP: jq absent"

  mkdir -p "$TMP/hooks/shared"
  cp "$ROOT/hooks/shared/_input.sh" "$TMP/hooks/shared/_input.sh"
  cp "$ROOT/tests/unit/hook-input-adapter.sh" "$TMP/tests/unit/fixture.sh"
  expect_partial unit "SKIP: jq absent"

  for path in .claude-plugin/plugin.json .claude-plugin/marketplace.json \
      .codex-plugin/plugin.json .cursor-plugin/plugin.json .github/plugin/plugin.json \
      .github/plugin/marketplace.json gemini-extension.json .opencode/INSTALL.md \
      CLAUDE.md AGENTS.md GEMINI.md; do
    mkdir -p "$(dirname "$TMP/$path")"
    cp "$ROOT/$path" "$TMP/$path"
  done
  cp "$ROOT/tests/unit/plugin-manifests-valid.sh" "$TMP/tests/unit/fixture.sh"
  HIDDEN_COMMANDS=jq:python3
  expect_partial unit "SKIP: no python3/jq available" "PASS: valid JSON:" \
    "$TMP/tests/unit/fixture.sh" "SKIP: python3 absent"
  (
    HIDDEN_COMMANDS=jq
    if builtin command -v python3 >/dev/null 2>&1; then
      expect_rc 0 --scope unit
      printf '{\n' > "$TMP/.claude-plugin/plugin.json"
      expect_rc 1 --scope unit
    else
      echo 'SKIP: python3 absent; real valid/malformed manifest regression not run'
    fi
  )
  (
    HIDDEN_COMMANDS=jq
    python3() { return 7; }
    export -f python3
    expect_rc 1 --scope unit
  )
  [ "$unavailable_failures" -eq 0 ] || exit 1
)
echo 'PASS: runner rejects invalid input, empty suites, exact tag misses, shell/framework skips, and failed tests'
echo 'PASS: runner preserves literal Windows paths and backslash diagnostics'
echo 'PASS: actual manifest and hook guards report unavailable tools and block strict acceptance'
