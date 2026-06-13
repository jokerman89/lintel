#!/usr/bin/env bash
# tests/unit/auto-decide.sh
# ADR-0014 (issue I3): is_one_way_door must flag irreversible/sovereignty decisions
# so --auto can't run past them. Conservative by design — a false positive just asks
# the operator (safe); a false negative is the failure we guard, so this pins the set.
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0; pass(){ echo "  PASS: $1"; }; fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/auto-decide.sh"; echo "========================="
source "$REPO_ROOT/lib/auto-decide.sh"

# MUST flag (irreversible / sovereignty)
for t in "drop the users table" "deploy to production" "force-push the branch" \
         "wipe the cache directory" "overwrite the prod config" "revoke the API key" \
         "rename the skill build to make" "delete the pack" "a breaking change to the public API" \
         "migrate the schema" "rm -rf the build dir"; do
  is_one_way_door "$t" && pass "flags one-way: $t" || fail "MISSED one-way door: $t"
done
# MUST NOT flag (reversible — safe to auto-decide)
for t in "rename the variable foo" "tweak a log message" "add a unit test" \
         "reword the comment" "bump the timeout to 30s"; do
  is_one_way_door "$t" && fail "false-positive on reversible: $t" || pass "reversible (auto-ok): $t"
done
echo ""
[ "$FAILED" -eq 0 ] && { echo "auto-decide: ALL PASS"; exit 0; } || { echo "auto-decide: FAILURES"; exit 1; }
