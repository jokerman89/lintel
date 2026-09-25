#!/usr/bin/env bash
# tag: unit native-routing
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
if ! command -v "$python" >/dev/null 2>&1; then
  python=python
fi
"$python" -B "$root/tests/unit/native-route-consolidation.py"
