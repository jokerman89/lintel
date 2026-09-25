#!/usr/bin/env bash
# component: planning-consolidation-test-entry
# implements: ADR-0026, ADR-0028, ADR-0029
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: synthetic test environment; no independent-review claim
# last_intent_review: 2026-09-25
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
if ! "$python" -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
  python=python
fi
exec "$python" -B "$root/tests/unit/planning-consolidation.py" "$@"
