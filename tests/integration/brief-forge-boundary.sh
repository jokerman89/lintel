#!/usr/bin/env bash
# DESCRIPTION: Explicit handoff validates structured payloads before minimal audit and output.
# TAGS: integration,brief-forge,swarm,codex-compatible
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null 2>&1; then PYTHON=python3
elif command -v python >/dev/null 2>&1; then PYTHON=python
else echo "FAIL brief-forge-boundary: Python 3.9+ is required" >&2; exit 1
fi
exec "$PYTHON" "$ROOT/tests/integration/brief-forge-boundary.py"
