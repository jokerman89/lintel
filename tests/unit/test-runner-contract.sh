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

# Sharding: deterministic, disjoint shards whose union is the unsharded run, with strict
# accounting inside each shard and fail-closed malformed or empty shards.
SHARD_TMP="$(mktemp -d)"
trap 'rm -rf "$TMP" "$SHARD_TMP"' EXIT
mkdir -p "$SHARD_TMP/tests/runner" "$SHARD_TMP/tests/unit"
cp "$ROOT/tests/runner/run-all.sh" "$SHARD_TMP/tests/runner/run-all.sh"
SHARD_RUNNER="$SHARD_TMP/tests/runner/run-all.sh"
for name in a b c d e; do
  printf 'echo "  PASS: %s"\n' "$name" > "$SHARD_TMP/tests/unit/$name.sh"
done
shard_run() {
  SHARD_RC=0
  SHARD_OUT=$(bash "$SHARD_RUNNER" "$@" 2>&1) || SHARD_RC=$?
  SHARD_RAN=$(printf '%s\n' "$SHARD_OUT" | sed -n 's/^RUN //p' | sort | tr '\n' ' ')
}
expect_shard() {
  local expected_rc="$1" expected_ran="$2"; shift 2
  shard_run "$@"
  if [ "$SHARD_RC" -ne "$expected_rc" ] || [ "$SHARD_RAN" != "$expected_ran" ]; then
    printf 'FAIL: %s: expected rc %s running [%s], got rc %s running [%s]\n%s\n' \
      "$*" "$expected_rc" "$expected_ran" "$SHARD_RC" "$SHARD_RAN" "$SHARD_OUT"
    exit 1
  fi
}
for bad in "" 0/2 3/2 x/2 1/0 1/2/3 -1/2 01/2 "1 /2"; do
  expect_shard 2 "" --shard "$bad"
done
expect_shard 2 "" --shard
all="unit/a.sh unit/b.sh unit/c.sh unit/d.sh unit/e.sh "
expect_shard 0 "$all"
expect_shard 0 "$all" --shard 1/1
expect_shard 0 "unit/a.sh unit/c.sh unit/e.sh " --shard 1/2
[[ "$SHARD_OUT" == *"Shard:   1/2 (3 of 5 discovered test files)"* ]] || {
  printf 'FAIL: shard summary missing\n%s\n' "$SHARD_OUT"; exit 1; }
expect_shard 0 "unit/b.sh unit/d.sh " --shard 2/2
expect_shard 0 "unit/c.sh " --shard 3/5 --scope unit
expect_shard 1 "" --shard 6/6
[[ "$SHARD_OUT" == *"selected zero of 5 discovered tests"* ]] || {
  printf 'FAIL: empty shard was not refused visibly\n%s\n' "$SHARD_OUT"; exit 1; }
union=""
for index in 1 2 3; do shard_run --shard "$index/3" --require-all; union="$union$SHARD_RAN"; done
[ "$(printf '%s' "$union" | tr ' ' '\n' | sed '/^$/d' | sort | tr '\n' ' ')" = "$all" ] || {
  printf 'FAIL: shards 1-3 of 3 are not a disjoint cover: [%s]\n' "$union"; exit 1; }
printf 'echo "  SKIP: unavailable dependency"\n' > "$SHARD_TMP/tests/unit/b.sh"
expect_shard 0 "unit/a.sh unit/c.sh unit/e.sh " --shard 1/2 --require-all
expect_shard 1 "unit/b.sh unit/d.sh " --shard 2/2 --require-all

# Platform applicability: off Windows, windows-only unittest skips are N/A only when every skip
# carries the canonical reason and something ran; on Windows, and for any other reason, they refuse.
NA_TMP="$(mktemp -d)"
trap 'rm -rf "$TMP" "$SHARD_TMP" "$NA_TMP"' EXIT
mkdir -p "$NA_TMP/tests/runner" "$NA_TMP/tests/unit"
cp "$ROOT/tests/runner/run-all.sh" "$NA_TMP/tests/runner/run-all.sh"
na_fixture() {
  # $1: skip reasons, one per skipped test; one further test always passes unless $2 is "none".
  local reasons="$1" ran=0 skips=0 body=""
  if [ "${2:-}" != "none" ]; then body+="echo \"test_ok (m.C.test_ok) ... ok\""$'\n'; ran=1; fi
  while IFS= read -r reason; do
    [ -n "$reason" ] || continue
    body+="echo \"test_s$skips (m.C.test_s$skips) ... skipped '$reason'\""$'\n'
    skips=$((skips + 1)); ran=$((ran + 1))
  done <<< "$reasons"
  body+="echo \"Ran $ran tests in 0.001s\""$'\n'"echo \"OK (skipped=$skips)\""$'\n'
  printf '%s' "$body" > "$NA_TMP/tests/unit/fixture.sh"
}
expect_na() {
  local host="$1" expected="$2" needle="$3"; shift 3
  local rc=0 output
  output=$(eval "uname() { echo '$host'; }"; export -f uname; bash "$NA_TMP/tests/runner/run-all.sh" "$@" 2>&1) || rc=$?
  if [ "$rc" -ne "$expected" ] || [[ "$output" != *"$needle"* ]]; then
    printf 'FAIL: host %s %s: expected rc %s with [%s], got rc %s\n%s\n' "$host" "$*" "$expected" "$needle" "$rc" "$output"
    exit 1
  fi
}
[ "$(eval "uname() { echo 'Probe-OS'; }"; export -f uname; bash -c 'uname -s')" = "Probe-OS" ] || {
  echo 'FAIL: the uname host simulation does not reach a child bash'; exit 1; }
na_fixture $'platform: windows-only; native long path\nplatform: windows-only; native junction'
expect_na Linux 0 "N/A: 2 windows-only unittest assertions" --require-all
expect_na Darwin 0 "N/A:     2 (windows-only unittest assertions" --require-all
expect_na MINGW64_NT-10.0 1 "FAIL-CLOSED: --require-all forbids skipped tests" --require-all
expect_na MSYS_NT-10.0 1 "Partial: 1 " --require-all
na_fixture $'platform: windows-only; native long path\nsymlinks unavailable'
expect_na Linux 1 "Partial: 1 " --require-all
expect_na Linux 0 "SKIP: 2 unittest assertions"
na_fixture $'platform: windows-only; native long path' none
expect_na Linux 1 "Skip:   1" --require-all
na_fixture $'Platform: windows-only; wrong case\nplatform:windows-only; no space'
expect_na Linux 1 "Partial: 1 " --require-all

echo 'PASS: runner rejects invalid input, empty suites, exact tag misses, shell/framework skips, and failed tests'
echo 'PASS: runner shards are deterministic, disjoint, complete, strict and fail closed when malformed or empty'
echo 'PASS: windows-only unittest skips are N/A only off Windows and only when every skip is so marked'
echo 'PASS: runner preserves literal Windows paths and backslash diagnostics'
echo 'PASS: actual manifest and hook guards report unavailable tools and block strict acceptance'
