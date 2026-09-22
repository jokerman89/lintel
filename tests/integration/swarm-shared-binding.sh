#!/usr/bin/env bash
# DESCRIPTION: Swarm consumes actual accepted review/profile/domain evidence without replacing their contracts.
# TAGS: integration,swarm,codex-compatible
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null 2>&1; then PYTHON=python3
elif command -v python >/dev/null 2>&1; then PYTHON=python
else echo "FAIL swarm-shared-binding: Python 3.9+ is required" >&2; exit 1
fi
exec "$PYTHON" -B "$ROOT/tests/integration/swarm-shared-binding.py"
