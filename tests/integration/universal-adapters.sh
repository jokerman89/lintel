#!/usr/bin/env bash
# tag: universal client-capabilities consumer
# SHARD-WEIGHT: 3245
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 "$ROOT/tests/integration/universal-adapters.py"
