#!/usr/bin/env bash
# Documentary source/template checks; no models or live domain operations.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null 2>&1; then
  python_bin=python3
elif command -v python >/dev/null 2>&1; then
  python_bin=python
else
  echo 'ERROR: Python 3.9+ is required for the agent-correctness contract checks.' >&2
  exit 127
fi
"$python_bin" "$ROOT/tests/behavior/v2-agent-correctness.py" --root "$ROOT" "$@"
