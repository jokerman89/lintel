#!/usr/bin/env bash
# component: coordination-method-test-entry
# implements: ADR-0026, ADR-0029, ADR-0034, ADR-0036
# intent: skills/scope/references/method.md
# constraints: local inert fixtures; retained for inspection, no models or cleanup
# last_intent_review: 2026-10-03
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
if ! "$python" -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
  python=python
fi
exec "$python" -B "$root/tests/unit/coordination-methods.py" "$@"
