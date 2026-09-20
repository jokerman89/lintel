#!/usr/bin/env bash
# tag: universal client-capabilities
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 "$ROOT/tests/unit/client-capabilities.py"
