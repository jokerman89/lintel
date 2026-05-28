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
#   1 = at least one fail
#   2 = runner-level error (missing tests/ dir, etc.)

set -euo pipefail

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TAG_FILTER=""
SCOPE="all"

while [ $# -gt 0 ]; do
  case "$1" in
    --tag) TAG_FILTER="$2"; shift 2 ;;
    --scope) SCOPE="$2"; shift 2 ;;
    -h|--help)
      head -10 "${BASH_SOURCE[0]}"; exit 0 ;;
    *) shift ;;
  esac
done

[ -d "$TESTS_DIR" ] || { echo "ERROR: tests/ dir missing" >&2; exit 2; }

c_green='\033[32m'; c_red='\033[31m'; c_yellow='\033[33m'; c_reset='\033[0m'; c_bold='\033[1m'

case "$SCOPE" in
  unit) SEARCH_DIRS="unit" ;;
  integration) SEARCH_DIRS="integration" ;;
  e2e) SEARCH_DIRS="e2e" ;;
  all) SEARCH_DIRS="unit integration e2e" ;;
  *) echo "ERROR: unknown scope $SCOPE" >&2; exit 2 ;;
esac

passed=0
failed=0
skipped=0
total=0

declare -a FAIL_LOG

# Discover test files
for dir in $SEARCH_DIRS; do
  [ -d "$TESTS_DIR/$dir" ] || continue
  while IFS= read -r test_file; do
    [ -f "$test_file" ] || continue
    [ -x "$test_file" ] || chmod +x "$test_file"
    total=$((total + 1))

    # Set tag filter env var if provided
    if [ -n "$TAG_FILTER" ]; then
      export LINTEL_TEST_FILTER_TAGS="$TAG_FILTER"
    else
      unset LINTEL_TEST_FILTER_TAGS 2>/dev/null || true
    fi

    output=$(bash "$test_file" 2>&1) || rc=$?
    rc=${rc:-0}

    if [ "$rc" -eq 0 ]; then
      if echo "$output" | grep -q '^SKIP'; then
        skipped=$((skipped + 1))
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

if [ "$failed" -gt 0 ]; then
  printf "\n${c_red}== Failure details ==${c_reset}\n"
  for entry in "${FAIL_LOG[@]}"; do printf "%b\n" "$entry"; done
  exit 1
fi

exit 0
