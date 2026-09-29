#!/usr/bin/env bash
# component: reusable-patterns-launcher-roots-test
# implements: ADR-0038, ADR-0029
# intent: .claude/plans/reusable-patterns/plan.md
# constraints: synthetic temporary roots only; Python 3.10+ is an explicit prerequisite of pattern runtime tests
# last_intent_review: 2026-09-28
# tag: unit patterns pack portability
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null && python3 -c 'import sys; assert sys.version_info >= (3, 10)' 2>/dev/null; then
  python=python3
elif command -v python >/dev/null && python -c 'import sys; assert sys.version_info >= (3, 10)' 2>/dev/null; then
  python=python
else
  echo 'ERROR: Python 3.10+ is required for reusable-pattern tests.' >&2
  exit 1
fi
LINTEL_TEST_BASH="$BASH"
if command -v cygpath >/dev/null 2>&1; then LINTEL_TEST_BASH="$(cygpath -m "$BASH")"; fi
export LINTEL_TEST_BASH
PYTHONDONTWRITEBYTECODE=1 "$python" -I -B "$root/tests/unit/pattern-launcher-roots.py"
