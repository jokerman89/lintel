#!/usr/bin/env bash
# TAGS: unit,ci
# component: unittest-chunk-test
# implements: ADR-0041
# intent: .claude/decisions/0041-weighted-shards-kit-chunks-pr-cancellation.md
# constraints: temporary fixture modules; lists the Copilot kit's chunks without running its tests
# last_intent_review: 2026-09-29
# Prevents a chunked unittest entry from dropping, duplicating or silently narrowing tests, and the
# Copilot kit's chunk wrappers from drifting away from a complete, disjoint cover of its tests.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null && python3 -c 'import sys; assert sys.version_info >= (3, 9)' 2>/dev/null; then
  python=python3
elif command -v python >/dev/null && python -c 'import sys; assert sys.version_info >= (3, 9)' 2>/dev/null; then
  python=python
else
  echo 'ERROR: Python 3.9+ is required for the unittest chunk tests.' >&2
  exit 1
fi
export LINTEL_TEST_BASH="${BASH:-bash}"
PYTHONDONTWRITEBYTECODE=1 "$python" "$root/tests/unit/unittest-chunk.py"
