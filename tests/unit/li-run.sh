#!/usr/bin/env bash
# component: li-run-tests
# implements: ADR-0039
# intent: .claude/plans/native-client-parity/spec.md
# constraints: synthetic repositories and temp directories only; no network or host session
# last_intent_review: 2026-09-28
# DESCRIPTION: bin/li-run prepares the Lintel environment, runs one step in the working
#              repository with its own status, and fails actionably on bad input.
# tag: unit copilot li-run

set -euo pipefail

TEST_NAME="$(basename "${BASH_SOURCE[0]}" .sh)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_TMP="$(mktemp -d "${TMPDIR:-/tmp}/li-test-${TEST_NAME}-XXXXXX")"
FAILED=0

pass() { printf 'PASS %s :: %s\n' "$TEST_NAME" "$1"; }
fail() { printf 'FAIL %s :: %s\n' "$TEST_NAME" "$1"; FAILED=$((FAILED + 1)); }
check() { if [ "$2" = "$3" ]; then pass "$1: $3"; else fail "$1: expected '$2', got '$3'"; fi; }
contains() { case "$2" in *"$3"*) pass "$1" ;; *) fail "$1: '$3' not in: $2" ;; esac; }
cleanup() { rm -rf "$TEST_TMP" 2>/dev/null || true; }
trap cleanup EXIT

if ! { command -v python3 || command -v python; } >/dev/null 2>&1; then
  echo "SKIP $TEST_NAME :: Python 3.9+ is required for the profile bootstrap"
  exit 0
fi

# Nothing inherited may select a different source, repository or profile.
for name in $(compgen -e); do
  case "$name" in LINTEL_*|CLAUDE_*|PACK_CACHE_FILE) unset "$name" ;; esac
done
export HOME="$TEST_TMP/home" USERPROFILE="$TEST_TMP/home"
mkdir -p "$HOME" "$TEST_TMP/repo one" "$TEST_TMP/elsewhere" "$TEST_TMP/bare" "$TEST_TMP/buffer" \
  "$TEST_TMP/hostile/lib" "$TEST_TMP/hostile/bin"
printf '# Fixture repository\n' > "$TEST_TMP/repo one/AGENTS.md"
FIXTURE="$(cd "$TEST_TMP/repo one" && pwd)"
RUN="$REPO_ROOT/bin/li-run"
for helper in lib/pack-resolver.sh lib/copilot-env.sh bin/_audit.sh; do
  printf 'printf ran > "%s/hostile-ran"\n' "$TEST_TMP" > "$TEST_TMP/hostile/$helper"
done
cat > "$TEST_TMP/step.sh" <<'STEP'
printf 'SOURCE=%s\nREPO=%s\nCWD=%s\n' "$LINTEL_SOURCE_ROOT" "$LINTEL_REPO_ROOT" "$PWD"
printf 'SKILLS=%s\nCHILD_SKILLS=%s\n' "${LINTEL_SKILLS_DIR:-}" "$(bash -c 'printf %s "${LINTEL_SKILLS_DIR:-}"')"
[ -n "${LINTEL_PROFILE_REFERENCE:-}" ] && echo "PROFILE=ready"
false
echo "after-false"
exit 3
STEP

# 1. A relative step runs in the selected repository with this runner's own source.
rc=0
out=$(cd "$TEST_TMP/elsewhere" && LINTEL_SOURCE_ROOT="$TEST_TMP/hostile" \
  bash "$RUN" --repo "$FIXTURE" ../step.sh 2>&1) || rc=$?
check "step exit status is returned" 3 "$rc"
contains "LINTEL_SOURCE_ROOT is the runner's source" "$out" "SOURCE=$REPO_ROOT"
contains "LINTEL_REPO_ROOT is the working repository" "$out" "REPO=$FIXTURE"
contains "the step runs in the working repository" "$out" "CWD=$FIXTURE"
contains "the profile context is prepared" "$out" "PROFILE=ready"
contains "the step keeps default shell options (no errexit)" "$out" "after-false"
if [ -e "$TEST_TMP/hostile-ran" ]; then fail "an inherited source root executed"; else pass "inherited source root ignored"; fi
contains "LINTEL_SKILLS_DIR is the runner's skills folder" "$out" $'\n'"SKILLS=$REPO_ROOT/skills"$'\n'
contains "LINTEL_SKILLS_DIR is exported to child processes" "$out" $'\n'"CHILD_SKILLS=$REPO_ROOT/skills"$'\n'

# 1b. LINTEL_SKILLS_DIR is pinned like LINTEL_SOURCE_ROOT: an inherited absolute or relative value
#     is ignored, and the pinned value is exported to child processes.
for inherited in "$TEST_TMP/operator skills" skills; do
  rc=0
  out=$(cd "$FIXTURE" && LINTEL_SKILLS_DIR="$inherited" bash "$RUN" "$TEST_TMP/step.sh" 2>&1) || rc=$?
  check "inherited LINTEL_SKILLS_DIR '$inherited' step exit status" 3 "$rc"
  contains "an inherited LINTEL_SKILLS_DIR '$inherited' is ignored" "$out" $'\n'"SKILLS=$REPO_ROOT/skills"$'\n'
  contains "the pinned LINTEL_SKILLS_DIR reaches a child over '$inherited'" "$out" \
    $'\n'"CHILD_SKILLS=$REPO_ROOT/skills"$'\n'
done

# 2. stdin (-) defaults to the current repository and removes its buffer.
rc=0
out=$(cd "$FIXTURE" && printf 'echo "stdin:$LINTEL_REPO_ROOT"\nexit 7\n' |
  TMPDIR="$TEST_TMP/buffer" bash "$RUN" - 2>&1) || rc=$?
check "stdin step exit status" 7 "$rc"
contains "stdin step runs with the current repository" "$out" "stdin:$FIXTURE"
check "stdin buffer removed" "" "$(ls -A "$TEST_TMP/buffer")"

# 3. Actionable failures.
rc=0
out=$(bash "$RUN" --repo "$FIXTURE" "$TEST_TMP/absent.sh" 2>&1) || rc=$?
check "missing script exit" 2 "$rc"
check "missing script message" "li-run: script not found: $TEST_TMP/absent.sh" "$out"
rc=0
out=$(bash "$RUN" --repo "$TEST_TMP/bare" "$TEST_TMP/step.sh" 2>&1) || rc=$?
check "repository without AGENTS.md exit" 1 "$rc"
contains "copilot-env error passes through" "$out" "ERROR: expected a scaffolded working repository at"
for arguments in "" "--repo" "--bogus $TEST_TMP/step.sh" "$TEST_TMP/step.sh $TEST_TMP/step.sh"; do
  rc=0
  # shellcheck disable=SC2086 # deliberate word splitting of the usage-error cases
  out=$(bash "$RUN" $arguments 2>&1) || rc=$?
  check "usage error exit for '${arguments:-<none>}'" 2 "$rc"
  contains "usage shown for '${arguments:-<none>}'" "$out" "Usage: bash li-run"
done
rc=0
out=$(bash "$RUN" --help 2>&1) || rc=$?
check "help exit" 0 "$rc"
contains "help text" "$out" "Usage: bash li-run [--repo <dir>] <script>|-"

if [ "$FAILED" -gt 0 ]; then
  echo "FAILED $TEST_NAME with $FAILED assertion failure(s)"
  exit 1
fi
echo "li-run: ALL PASS"
