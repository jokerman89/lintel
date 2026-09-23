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
  command() {
    if [ "$#" -eq 2 ] && [ "$1" = "-v" ] && [ "$2" = "jq" ]; then
      return 1
    fi
    builtin command "$@"
  }
  export -f command
  manifest_rc=0
  manifest_output=$(bash "$RUNNER" --scope shape --require-all 2>&1) || manifest_rc=$?
  [ "$manifest_rc" -eq 1 ] || {
    printf 'FAIL: strict runner accepted unavailable manifest parity checks\n%s\n' "$manifest_output"
    exit 1
  }
  [[ "$manifest_output" == *"SKIP: jq absent"* && "$manifest_output" == *"Partial: 1 "* ]] || {
    printf 'FAIL: manifest parity was not reported as skipped coverage\n%s\n' "$manifest_output"
    exit 1
  }
  expect_rc 0 --scope shape
)
echo 'PASS: runner rejects invalid input, empty suites, exact tag misses, shell/framework skips, and failed tests'
echo 'PASS: runner preserves literal Windows paths and backslash diagnostics'
echo 'PASS: actual manifest parity reports unavailable jq and blocks strict acceptance'
