#!/usr/bin/env bash
# tests/shape/bin-scripts-executable.sh
# Asserts every invokable bin/li-* CLI script is committed with the executable
# bit (git mode 100755). A non-exec commit (100644) passes on Windows — where
# the filesystem has no unix exec bit — but FAILS on Linux CI the moment a test
# does `[ -x bin/li-foo ]`. This guard catches that class at shape time instead
# of in a red CI run (root cause of the 2026-06 CI breakage: li-envelope-validate
# + li-wiki-gen committed 100644).
# tag: ci-hygiene exec-bit

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/bin-scripts-executable.sh"
echo "====================================="

# Invokable CLI scripts = bin/li-* (the _*.sh helpers + lib/*.sh are sourced,
# so their exec bit is irrelevant and intentionally left 100644).
mapfile -t LI < <(git ls-files -s bin/ | awk '$4 ~ /^bin\/li-/ {print $1"\t"$4}')

if [ "${#LI[@]}" -eq 0 ]; then
  fail "no bin/li-* scripts found via git ls-files (run from a git checkout)"
else
  for row in "${LI[@]}"; do
    mode="${row%%	*}"; path="${row#*	}"
    if [ "$mode" = "100755" ]; then
      pass "$path is executable (100755)"
    else
      fail "$path is committed $mode — must be 100755 (will break Linux CI [ -x ]). Fix: git update-index --chmod=+x $path"
    fi
  done
fi

echo ""
[ "$FAILED" -eq 0 ] && { echo "bin-scripts-executable: ALL PASS"; exit 0; } || { echo "bin-scripts-executable: FAILURES"; exit 1; }
