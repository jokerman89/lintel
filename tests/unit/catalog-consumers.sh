#!/usr/bin/env bash
# Actual documented callers plus structural guidance checks; no live model evaluation.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null 2>&1; then
  python3 -B "$ROOT/tests/unit/catalog-consumers.py"
elif command -v python >/dev/null 2>&1; then
  python -B "$ROOT/tests/unit/catalog-consumers.py"
else
  printf 'ERROR: catalog consumer tests require Python 3.9+.\n' >&2
  exit 1
fi
