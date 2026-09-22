#!/usr/bin/env bash
# Source projection only; installed closure and live host evidence remain separate.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null 2>&1; then
  python3 -B "$ROOT/tests/unit/catalog-selection.py"
elif command -v python >/dev/null 2>&1; then
  python -B "$ROOT/tests/unit/catalog-selection.py"
else
  printf 'ERROR: catalog selection tests require Python 3.9+.\n' >&2
  exit 1
fi
