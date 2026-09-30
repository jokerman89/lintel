#!/usr/bin/env bash
# Source contracts and real helpers in synthetic fixtures; no model or hook execution.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python >/dev/null 2>&1; then
  PYTHON=python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
else
  echo 'ERROR: Python 3.9+ is required.' >&2
  exit 127
fi
export PYTHONDONTWRITEBYTECODE=1
"$PYTHON" -B "$ROOT/tests/unit/v2-skill-methods.py" --root "$ROOT" \
  --bash "$(command -v bash)" --git "$(command -v git)" "$@"
