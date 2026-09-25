#!/usr/bin/env bash
# tag: universal client-capabilities consumer
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 "$ROOT/tests/integration/universal-adapters.py"
