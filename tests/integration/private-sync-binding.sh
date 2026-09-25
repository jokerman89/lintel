#!/usr/bin/env bash
# DESCRIPTION: Explicit private-sync bindings and preserved local Git round trips.
# TAGS: integration,private-sync,codex-compatible
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null 2>&1; then PYTHON=python3
elif command -v python >/dev/null 2>&1; then PYTHON=python
else echo "FAIL private-sync-binding: Python 3.9+ is required" >&2; exit 1
fi
export LINTEL_TEST_BASH="${BASH:-bash}"
exec "$PYTHON" "$ROOT/tests/integration/private-sync-binding.py" "$@"
