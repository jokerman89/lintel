#!/usr/bin/env bash
# component: universal-lifecycle-scenarios
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P10.md
# constraints: isolated synthetic source, install, consumer and private state only
# last_intent_review: 2026-09-20
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 &&
    "$candidate" -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done
[ -n "$PYTHON" ] || { echo 'ERROR: lifecycle tests require Python 3.9+' >&2; exit 2; }
export PYTHONDONTWRITEBYTECODE=1
"$PYTHON" "$ROOT/tests/integration/universal-lifecycle.py" --root "$ROOT" --bash "$(command -v bash)" "$@"
