#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
"${LINTEL_PYTHON:-python3}" -B "$root/tests/unit/role-runtime-helpers.py" "$@"
