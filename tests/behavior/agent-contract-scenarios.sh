#!/usr/bin/env bash
# Documentary role contracts and synthetic worked examples, not live model behavior.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null 2>&1; then
  python_bin=python3
elif command -v python >/dev/null 2>&1; then
  python_bin=python
else
  echo 'ERROR: Python 3.9+ is required for the documentary scenario checks.' >&2
  exit 127
fi
"$python_bin" "$ROOT/tests/behavior/agent_contract_scenarios.py" --root "$ROOT" "$@"
