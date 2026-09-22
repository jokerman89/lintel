#!/usr/bin/env bash
# Compact discovery is metadata evidence, not live host execution.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null 2>&1; then
  python3 -B "$ROOT/tests/unit/catalog-metadata.py"
elif command -v python >/dev/null 2>&1; then
  python -B "$ROOT/tests/unit/catalog-metadata.py"
else
  printf 'ERROR: catalog metadata tests require Python 3.9+.\n' >&2
  exit 1
fi
