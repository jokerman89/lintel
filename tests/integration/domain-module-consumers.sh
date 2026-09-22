#!/usr/bin/env bash
# component: domain-module-consumer-runner
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/packages/P09.md
# constraints: synthetic released-provider tests; no native actor or installation claim
# last_intent_review: 2026-09-22
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python >/dev/null 2>&1 && python -c 'import sys; assert sys.version_info >= (3,9)' 2>/dev/null; then
  PYTHON=python
elif command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; assert sys.version_info >= (3,9)' 2>/dev/null; then
  PYTHON=python3
else
  echo 'ERROR: Python 3.9+ is required.' >&2
  exit 127
fi
export PYTHONDONTWRITEBYTECODE=1
"$PYTHON" "$ROOT/tests/integration/domain-module-consumers.py" --root "$ROOT" \
  --bash "$(command -v bash)" --git "$(command -v git)" "$@"
