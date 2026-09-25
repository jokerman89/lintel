#!/usr/bin/env bash
# Lintel test runner — runs all tests under tests/, aggregates pass/fail/skip.
#
# Usage:
#   bash tests/runner/run-all.sh                  # everything
#   bash tests/runner/run-all.sh --tag <tag>      # filter by tag
#   bash tests/runner/run-all.sh --scope unit     # unit only (subset)
#   bash tests/runner/run-all.sh --shard 2/4      # every 4th discovered file, from the 2nd
#
# Exit codes:
#   0 = all pass (or skips only)
#   1 = at least one fail, OR zero tests discovered, OR a tag filter that
#       matched nothing (fail-closed: a green run must assert something —
#       an empty scope or all-skip filter is a broken promise, not a pass)
#   2 = runner-level error (missing tests/ dir, etc.)

set -euo pipefail

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TAG_FILTER=""
SCOPE="all"
REQUIRE_ALL=0
SHARD_INDEX=1
SHARD_COUNT=1

while [ $# -gt 0 ]; do
  case "$1" in
    --tag) [ $# -ge 2 ] && [ -n "$2" ] || { echo "ERROR: --tag needs a value" >&2; exit 2; }; TAG_FILTER="$2"; shift 2 ;;
    --scope) [ $# -ge 2 ] && [ -n "$2" ] || { echo "ERROR: --scope needs a value" >&2; exit 2; }; SCOPE="$2"; shift 2 ;;
    --shard)
      # A shard is K/N with 1 <= K <= N; any other spelling is a runner error, never a subset.
      if [ $# -lt 2 ] || ! [[ "$2" =~ ^([1-9][0-9]*)/([1-9][0-9]*)$ ]] \
          || [ "${BASH_REMATCH[1]}" -gt "${BASH_REMATCH[2]}" ]; then
        echo "ERROR: --shard needs K/N with 1 <= K <= N" >&2; exit 2
      fi
      SHARD_INDEX="${BASH_REMATCH[1]}"; SHARD_COUNT="${BASH_REMATCH[2]}"; shift 2 ;;
    --require-all) REQUIRE_ALL=1; shift ;;
    --shape-only) SCOPE="shape"; shift ;;
    -h|--help)
      head -11 "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "ERROR: unknown argument $1" >&2; exit 2 ;;
  esac
done

[ -d "$TESTS_DIR" ] || { echo "ERROR: tests/ dir missing" >&2; exit 2; }

c_green='\033[32m'; c_red='\033[31m'; c_yellow='\033[33m'; c_reset='\033[0m'; c_bold='\033[1m'
ESC=$(printf '\033')

case "$SCOPE" in
  unit) SEARCH_DIRS="unit" ;;
  integration) SEARCH_DIRS="integration" ;;
  e2e) SEARCH_DIRS="e2e" ;;
  behavior) SEARCH_DIRS="behavior" ;;
  shape) SEARCH_DIRS="shape" ;;
  all) SEARCH_DIRS="unit behavior integration e2e shape" ;;
  *) echo "ERROR: unknown scope $SCOPE" >&2; exit 2 ;;
esac

passed=0
failed=0
skipped=0
total=0
partial=0
discovered=0
not_applicable=0
# Git Bash, MSYS and Cygwin report their Windows host through uname; everything else is not Windows.
case "$(uname -s 2>/dev/null || true)" in
  MINGW*|MSYS*|CYGWIN*) ON_WINDOWS=1 ;;
  *) ON_WINDOWS=0 ;;
esac

declare -a FAIL_LOG

# Discover test files
for dir in $SEARCH_DIRS; do
  [ -d "$TESTS_DIR/$dir" ] || continue
  while IFS= read -r test_file; do
    [ -f "$test_file" ] || continue
    position=$discovered
    discovered=$((discovered + 1))
    # Files outside this shard are neither run nor counted, so strict accounting stays exact.
    [ $((position % SHARD_COUNT + 1)) -eq "$SHARD_INDEX" ] || continue
    total=$((total + 1))

    # Enforce tags here; old tests do not all implement their own tag filter.
    # Match complete tokens, so e.g. "unit" cannot match "not-unit".
    if [ -n "$TAG_FILTER" ]; then
      declared_tags=$(sed -nE 's/^#[[:space:]]*([Tt][Aa][Gg][Ss]?):[[:space:]]*//p' "$test_file" | head -1)
      tag_match=0
      for filter in ${TAG_FILTER//,/ }; do
        for declared in ${declared_tags//,/ }; do
          [ "$filter" = "$declared" ] && tag_match=1
        done
      done
      if [ "$tag_match" -eq 0 ]; then
        skipped=$((skipped + 1))
        continue
      fi
      export LINTEL_TEST_FILTER_TAGS="$TAG_FILTER"
    else
      unset LINTEL_TEST_FILTER_TAGS 2>/dev/null || true
    fi

    rc=0
    printf 'RUN %s\n' "${test_file#"$TESTS_DIR"/}"
    # Isolate each test's stdin from the runner's control FD. The loop reads test
    # paths from `< <(find ...)`; a test that invokes a hook (hooks now read stdin
    # via hooks/shared/_input.sh) would otherwise consume that FD and eat the rest
    # of the test list. /dev/null gives hooks an immediate EOF → their $1 fallback.
    output=$(bash "$test_file" </dev/null 2>&1) || rc=$?

    if [ "$rc" -eq 0 ]; then
      # The test template's skip() prints a color code before "SKIP", so the
      # line starts with an ANSI escape — strip them or every skip counts as a pass.
      plain_output=$(printf '%s\n' "$output" | sed "s/${ESC}\[[0-9;]*m//g")
      framework_skips=$(printf '%s\n' "$plain_output" | sed -n 's/^OK (skipped=\([1-9][0-9]*\)).*/\1/p')
      if [ -n "$framework_skips" ]; then
        framework_total=$(printf '%s\n' "$plain_output" | sed -n 's/^Ran \([0-9][0-9]*\) test.*/\1/p')
        # Off Windows, a unittest skip whose reason starts "platform: windows-only" is not applicable,
        # not missing coverage: the Windows jobs run those methods strictly. It counts only when every
        # skip in the entry carries that reason and something else ran; on Windows it stays partial.
        platform_skips=0
        if [ "$ON_WINDOWS" -eq 0 ]; then
          platform_skips=$(printf '%s\n' "$plain_output" | grep -cE "\.\.\. skipped 'platform: windows-only" || true)
        fi
        if [ "$platform_skips" -gt 0 ] && [ "$platform_skips" = "$framework_skips" ] \
            && [ "$framework_total" != "$framework_skips" ]; then
          passed=$((passed + 1))
          not_applicable=$((not_applicable + platform_skips))
          printf 'N/A: %s windows-only unittest assertions in %s\n' "$platform_skips" "$test_file"
        elif [ "$framework_total" = "$framework_skips" ]; then
          skipped=$((skipped + 1))
          printf 'SKIP: %s unittest assertions in %s\n' "$framework_skips" "$test_file"
        else
          passed=$((passed + 1))
          partial=$((partial + 1))
          printf 'SKIP: %s unittest assertions in %s\n' "$framework_skips" "$test_file"
        fi
      elif printf '%s\n' "$plain_output" | grep -qE '^[[:space:]]*SKIP([ :]|$)'; then
        if printf '%s\n' "$plain_output" | grep -qE '^[[:space:]]*PASS([ :]|$)'; then
          passed=$((passed + 1))
          partial=$((partial + 1))
        else
          skipped=$((skipped + 1))
        fi
        printf '%s\n' "$plain_output" | grep -E '^[[:space:]]*SKIP([ :]|$)'
      else
        passed=$((passed + 1))
      fi
    else
      failed=$((failed + 1))
      FAIL_LOG+=("$test_file:"$'\n'"$output")
    fi
  done < <(find "$TESTS_DIR/$dir" -name '*.sh' -type f 2>/dev/null | sort)
done

# Report
echo ""
printf "${c_bold}== Lintel test summary ==${c_reset}\n"
printf "Total:   %d\n" "$total"
if [ "$SHARD_COUNT" -gt 1 ]; then
  printf "Shard:   %d/%d (%d of %d discovered test files)\n" "$SHARD_INDEX" "$SHARD_COUNT" "$total" "$discovered"
fi
printf "${c_green}Pass:   %d${c_reset}\n" "$passed"
printf "${c_yellow}Skip:   %d${c_reset}\n" "$skipped"
printf "${c_red}Fail:   %d${c_reset}\n" "$failed"
printf "Partial: %d (passed tests with skipped assertions)\n" "$partial"
if [ "$not_applicable" -gt 0 ]; then
  printf "N/A:     %d (windows-only unittest assertions, not applicable on this host)\n" "$not_applicable"
fi

if [ "$failed" -gt 0 ]; then
  printf "\n${c_red}== Failure details ==${c_reset}\n"
  for entry in "${FAIL_LOG[@]}"; do printf '%s\n\n' "$entry"; done
  exit 1
fi

if [ "$total" -eq 0 ]; then
  if [ "$SHARD_COUNT" -gt 1 ]; then
    printf "\n${c_red}FAIL-CLOSED: shard %d/%d of scope '%s' selected zero of %d discovered tests — a run that asserts nothing is not green.${c_reset}\n" "$SHARD_INDEX" "$SHARD_COUNT" "$SCOPE" "$discovered" >&2
    exit 1
  fi
  printf "\n${c_red}FAIL-CLOSED: scope '%s' discovered zero tests — a run that asserts nothing is not green.${c_reset}\n" "$SCOPE" >&2
  exit 1
fi

if [ "$passed" -eq 0 ]; then
  printf "\n${c_red}FAIL-CLOSED: no tests passed (scope '%s', filter '%s') — a run that asserts nothing is not green.${c_reset}\n" "$SCOPE" "$TAG_FILTER" >&2
  exit 1
fi

if [ "$REQUIRE_ALL" -eq 1 ] && [ $((skipped + partial)) -gt 0 ]; then
  printf '\nFAIL-CLOSED: --require-all forbids skipped tests or assertions.\n' >&2
  exit 1
fi

exit 0
