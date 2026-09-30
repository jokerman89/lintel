#!/usr/bin/env bash
# Documentary source and inert report-contract checks, not live agent behavior.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null 2>&1; then
  python_bin=python3
elif command -v python >/dev/null 2>&1; then
  python_bin=python
else
  echo 'ERROR: Python 3.9+ is required for the V2 agent-method contract checks.' >&2
  exit 127
fi
"$python_bin" "$ROOT/tests/behavior/v2-agent-methods.py" --root "$ROOT" "$@"
