#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
PYTHONDONTWRITEBYTECODE=1 "$python" "$root/tests/unit/design-fragment-emission.py"
