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
echo 'PASS: runner rejects invalid input, empty suites, exact tag misses, shell/framework skips, and failed tests'
