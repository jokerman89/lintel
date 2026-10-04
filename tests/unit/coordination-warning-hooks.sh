#!/usr/bin/env bash
# component: coordination-warning-hook-test-entry
# implements: ADR-0008, ADR-0029
# intent: skills/da/references/preferences.md
# constraints: only two optional hooks on inert text, no activation or cleanup
# last_intent_review: 2026-10-03
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
if ! "$python" -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
  python=python
fi
exec "$python" -B "$root/tests/unit/coordination-warning-hooks.py" "$@"
