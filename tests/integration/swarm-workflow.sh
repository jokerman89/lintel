#!/usr/bin/env bash
# DESCRIPTION: Swarm unit contract and mapped candidate-frontier workflow round trip.
# TAGS: integration,swarm,codex-compatible
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export LINTEL_SOURCE_ROOT="$ROOT"

if command -v python3 >/dev/null 2>&1; then PYTHON=python3
elif command -v python >/dev/null 2>&1; then PYTHON=python
else echo "FAIL swarm-workflow: Python 3.9+ is required" >&2; exit 1
fi

"$PYTHON" "$ROOT/tests/unit/swarm-contract.py"
"$PYTHON" "$ROOT/tests/integration/swarm-workflow.py"
