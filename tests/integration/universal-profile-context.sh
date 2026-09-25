#!/usr/bin/env bash
# component: universal-profile-context-test
# implements: ADR-0029
# intent: docs/concepts/pack-resolver.md
# constraints: synthetic fixtures and temporary homes only; no host or network activation
# last_intent_review: 2026-09-20
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python >/dev/null 2>&1 && python -c 'import sys; assert sys.version_info >= (3, 9)' 2>/dev/null; then
  PYTHON=python
elif command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; assert sys.version_info >= (3, 9)' 2>/dev/null; then
  PYTHON=python3
else
  echo 'FAIL: Python 3.9+ is required for structured profile verification' >&2
  exit 1
fi
export PYTHONDONTWRITEBYTECODE=1
"$PYTHON" "$ROOT/tests/integration/universal-profile-context.py" --root "$ROOT" --bash "$(command -v bash)" "$@"
