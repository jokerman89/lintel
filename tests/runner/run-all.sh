#!/usr/bin/env bash
# Lintel test runner — runs all tests under tests/, aggregates pass/fail/skip.
#
# Usage:
#   bash tests/runner/run-all.sh                  # everything
#   bash tests/runner/run-all.sh --tag <tag>      # filter by tag
#   bash tests/runner/run-all.sh --scope unit     # unit only (subset)
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

while [ $# -gt 0 ]; do
  case "$1" in
    --tag) [ $# -ge 2 ] && [ -n "$2" ] || { echo "ERROR: --tag needs a value" >&2; exit 2; }; TAG_FILTER="$2"; shift 2 ;;
    --scope) [ $# -ge 2 ] && [ -n "$2" ] || { echo "ERROR: --scope needs a value" >&2; exit 2; }; SCOPE="$2"; shift 2 ;;
    --require-all) REQUIRE_ALL=1; shift ;;
    --shape-only) SCOPE="shape"; shift ;;
    -h|--help)
      head -10 "${BASH_SOURCE[0]}"; exit 0 ;;
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

declare -a FAIL_LOG

# Discover test files
for dir in $SEARCH_DIRS; do
  [ -d "$TESTS_DIR/$dir" ] || continue
  while IFS= read -r test_file; do
    [ -f "$test_file" ] || continue
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
        if [ "$framework_total" = "$framework_skips" ]; then
          skipped=$((skipped + 1))
        else
          passed=$((passed + 1))
          partial=$((partial + 1))
        fi
        printf 'SKIP: %s unittest assertions in %s\n' "$framework_skips" "$test_file"
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
      FAIL_LOG+=("$test_file:\n$output\n")
    fi
  done < <(find "$TESTS_DIR/$dir" -name '*.sh' -type f 2>/dev/null | sort)
done

# Report
echo ""
printf "${c_bold}== Lintel test summary ==${c_reset}\n"
printf "Total:   %d\n" "$total"
printf "${c_green}Pass:   %d${c_reset}\n" "$passed"
printf "${c_yellow}Skip:   %d${c_reset}\n" "$skipped"
printf "${c_red}Fail:   %d${c_reset}\n" "$failed"
printf "Partial: %d (passed tests with skipped assertions)\n" "$partial"

if [ "$failed" -gt 0 ]; then
  printf "\n${c_red}== Failure details ==${c_reset}\n"
  for entry in "${FAIL_LOG[@]}"; do printf "%b\n" "$entry"; done
  exit 1
fi

if [ "$total" -eq 0 ]; then
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
