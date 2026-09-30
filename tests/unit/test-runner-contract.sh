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
cp "$ROOT/CODEOWNERS" "$TMP/CODEOWNERS"
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
      .github/plugin/marketplace.json CLAUDE.md AGENTS.md; do
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

# Weighted shards (ADR-0041): "# SHARD-WEIGHT: <seconds>" in the leading comment block selects a
# deterministic longest-first partition in which unweighted files count 60 s. A scope with no
# header keeps (i mod N) + 1, and a malformed header refuses before any test runs.
W_TMP="$(mktemp -d)"
trap 'rm -rf "$TMP" "$SHARD_TMP" "$NA_TMP" "$W_TMP"' EXIT
mkdir -p "$W_TMP/tests/runner" "$W_TMP/tests/unit"
cp "$ROOT/tests/runner/run-all.sh" "$W_TMP/tests/runner/run-all.sh"
weighted_fixture() {
  # $1: file name; $2: header line or empty; $3: body (default: one passing assertion).
  {
    printf '#!/usr/bin/env bash\n# TAGS: unit\n'
    [ -z "$2" ] || printf '%s\n' "$2"
    printf '%s\n' "${3:-echo \"  PASS: $1\"}"
  } > "$W_TMP/tests/unit/$1.sh"
}
weighted_set() {
  # $1..$7: the header for a.sh .. g.sh, in discovery order; "-" means none.
  local name header
  rm -f "$W_TMP"/tests/unit/*.sh
  for name in a b c d e f g; do
    header="$1"; shift
    if [ "$header" = "-" ]; then weighted_fixture "$name" ""
    else weighted_fixture "$name" "# SHARD-WEIGHT: $header"
    fi
  done
}
w_run() {
  W_RC=0
  W_OUT=$(bash "$W_TMP/tests/runner/run-all.sh" --scope unit "$@" 2>&1) || W_RC=$?
  # Keep the actual run order: a shard runs its files in discovery order.
  W_RAN=$(printf '%s\n' "$W_OUT" | sed -n 's/^RUN unit\///p' | tr '\n' ' ')
}
expect_weighted() {
  local expected_rc="$1" expected_ran="$2"; shift 2
  w_run "$@"
  if [ "$W_RC" -ne "$expected_rc" ] || [ "$W_RAN" != "$expected_ran" ]; then
    printf 'FAIL: weighted %s: expected rc %s running [%s], got rc %s running [%s]\n%s\n' \
      "$*" "$expected_rc" "$expected_ran" "$W_RC" "$W_RAN" "$W_OUT"
    exit 1
  fi
}
w_all="a.sh b.sh c.sh d.sh e.sh f.sh g.sh "
# Hand-computed LPT for three shards. Order by weight, ties in discovery order:
# c 300, e 120, b 60 (default), f 60 (default), a 10, d 10, g 5. Loads after each step:
# c->1 [300,0,0]; e->2 [300,120,0]; b->3 [300,120,60]; f->3 [300,120,120]; a->2 [300,130,120];
# d->3 [300,130,130]; g->2 [300,135,130]. Each shard runs its files in discovery order.
weighted_set 10 - 300 10 120 - 5
expect_weighted 0 "c.sh " --shard 1/3 --require-all
expect_weighted 0 "a.sh e.sh g.sh " --shard 2/3 --require-all
[[ "$W_OUT" == *"Shard:   2/3 (3 of 7 discovered test files)"* \
    && "$W_OUT" == *"Weights: 5 of 7 discovered test files declare SHARD-WEIGHT; the others count 60 s"* ]] || {
  printf 'FAIL: weighted shard summary missing\n%s\n' "$W_OUT"; exit 1; }
expect_weighted 0 "b.sh d.sh f.sh " --shard 3/3 --require-all
first_run="$W_OUT"
expect_weighted 0 "b.sh d.sh f.sh " --shard 3/3 --require-all
[ "$first_run" = "$W_OUT" ] || { printf 'FAIL: weighted shard output is not deterministic\n'; exit 1; }
expect_weighted 0 "$w_all" --require-all
for count in 1 2 3 4 5; do
  union=""
  for index in $(seq 1 "$count"); do
    w_run --shard "$index/$count" --require-all
    [ "$W_RC" -eq 0 ] && [ -n "$W_RAN" ] || {
      printf 'FAIL: weighted shard %s/%s failed or is empty\n%s\n' "$index" "$count" "$W_OUT"; exit 1; }
    union="$union$W_RAN"
  done
  [ "$(printf '%s' "$union" | tr ' ' '\n' | sed '/^$/d' | sort | tr '\n' ' ')" = "$w_all" ] || {
    printf 'FAIL: weighted shards 1-%s are not a disjoint cover: [%s]\n' "$count" "$union"; exit 1; }
done
expect_weighted 1 "" --shard 8/8
[[ "$W_OUT" == *"selected zero of 7 discovered tests"* ]] || {
  printf 'FAIL: an empty weighted shard was not refused\n%s\n' "$W_OUT"; exit 1; }
weighted_fixture e "# SHARD-WEIGHT: 120" 'echo "  SKIP: unavailable dependency"'
expect_weighted 1 "a.sh e.sh g.sh " --shard 2/3 --require-all
expect_weighted 0 "b.sh d.sh f.sh " --shard 3/3 --require-all
# A header's trailing carriage return is ignored.
weighted_set 10 - - 10 120 - 5
printf '#!/usr/bin/env bash\r\n# SHARD-WEIGHT: 300\r\necho "  PASS: c"\r\n' > "$W_TMP/tests/unit/c.sh"
expect_weighted 0 "c.sh " --shard 1/3
# Equal weights give exactly (i mod N) + 1.
weighted_set 7 7 7 7 7 7 7
expect_weighted 0 "a.sh d.sh g.sh " --shard 1/3
expect_weighted 0 "b.sh e.sh " --shard 2/3
expect_weighted 0 "c.sh f.sh " --shard 3/3
# No header in the scope: modulo, and the summary is unchanged. A SHARD-WEIGHT line after the
# leading comment block is not a header.
weighted_set - - - - - - -
weighted_fixture c "" $'echo "  PASS: c"\n# SHARD-WEIGHT: 999'
expect_weighted 0 "a.sh d.sh g.sh " --shard 1/3
[[ "$W_OUT" != *"Weights:"* ]] || { printf 'FAIL: an unweighted scope reported weights\n%s\n' "$W_OUT"; exit 1; }
expect_weighted 0 "c.sh f.sh " --shard 3/3
# Malformed, near-miss and repeated headers are runner errors, with or without --shard.
for bad in "# SHARD-WEIGHT: 0" "# SHARD-WEIGHT: 1.5" "# SHARD-WEIGHT: abc" "# SHARD-WEIGHT:" \
    "# SHARD-WEIGHT: 012" "# SHARD-WEIGHT: -5" "# SHARD-WEIGHT: 1234567890" "# SHARD-WEIGHT: 5 s" \
    "# shard-weight: 5" "#SHARD-WEIGHT: 5" "# SHARD_WEIGHT: 5" $'# SHARD-WEIGHT: 5\n# SHARD-WEIGHT: 6'; do
  weighted_set 10 - 300 10 120 - 5
  weighted_fixture d "$bad"
  for args in "--shard 2/3" ""; do
    # shellcheck disable=SC2086
    expect_weighted 2 "" $args
    [[ "$W_OUT" == *"unit/d.sh"* ]] || {
      printf 'FAIL: a malformed header did not name its file: [%s]\n%s\n' "$bad" "$W_OUT"; exit 1; }
  done
done

echo 'PASS: runner rejects invalid input, empty suites, exact tag misses, shell/framework skips, and failed tests'
echo 'PASS: runner shards are deterministic, disjoint, complete, strict and fail closed when malformed or empty'
echo 'PASS: weighted shards are longest-first, deterministic, disjoint and complete; no weights keeps modulo; malformed headers refuse'
echo 'PASS: windows-only unittest skips are N/A only off Windows and only when every skip is so marked'
echo 'PASS: runner preserves literal Windows paths and backslash diagnostics'
echo 'PASS: actual manifest and hook guards report unavailable tools and block strict acceptance'
