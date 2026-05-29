#!/usr/bin/env bash
# tests/shape/pack-resolver-fallbacks.sh
# Asserts: pack-resolver handles all 9 documented failure scenarios.
# Delegates to tests/unit/pack-resolver-fallbacks.sh.
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UNIT="$REPO_ROOT/tests/unit/pack-resolver-fallbacks.sh"

echo "tests/shape/pack-resolver-fallbacks.sh"
echo "========================================"

if [ -f "$UNIT" ]; then
  bash "$UNIT"
  exit $?
else
  echo "  FAIL: tests/unit/pack-resolver-fallbacks.sh missing"
  echo "    The pack-resolver fallback test harness ships in Phase 1."
  exit 1
fi
