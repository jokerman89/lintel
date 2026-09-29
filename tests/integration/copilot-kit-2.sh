#!/usr/bin/env bash
# DESCRIPTION: Portable Copilot onboarding, upgrades, drift, source isolation and hostile paths (chunk 2 of 8).
# TAGS: integration,codex-compatible
# SHARD-WEIGHT: 865
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null 2>&1; then PYTHON=python3
elif command -v python >/dev/null 2>&1; then PYTHON=python
else echo "FAIL copilot-kit: Python 3.9+ is required" >&2; exit 1
fi
export LINTEL_TEST_BASH="${BASH:-bash}"
# One of 8 disjoint chunks of copilot-kit.py (ADR-0041); running the module directly still runs every test.
LINTEL_TEST_CHUNK=2/8 "$PYTHON" "$ROOT/tests/runner/unittest_chunk.py" "$ROOT/tests/integration/copilot-kit.py" "$@"
