#!/usr/bin/env bash
# DESCRIPTION: Portable Copilot onboarding, upgrades, drift, source isolation and hostile paths.
# TAGS: integration,codex-compatible
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null 2>&1; then PYTHON=python3
elif command -v python >/dev/null 2>&1; then PYTHON=python
else echo "FAIL copilot-kit: Python 3.9+ is required" >&2; exit 1
fi
export LINTEL_TEST_BASH="${BASH:-bash}"
"$PYTHON" "$ROOT/tests/integration/copilot-kit.py"
