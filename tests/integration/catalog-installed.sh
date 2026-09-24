#!/usr/bin/env bash
# DESCRIPTION: Accepted lifecycle installation, compact discovery, aliases and dependency preservation.
# TAGS: integration,codex-compatible
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null 2>&1; then PYTHON=python3
elif command -v python >/dev/null 2>&1; then PYTHON=python
else echo "FAIL installed catalog: Python 3.9+ with the existing YAML reader is required" >&2; exit 1
fi
"$PYTHON" -B "$ROOT/tests/integration/catalog-installed.py" "$@"
