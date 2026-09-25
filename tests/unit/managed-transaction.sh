#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 &&
    "$candidate" -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
    PYTHONDONTWRITEBYTECODE=1 "$candidate" "$ROOT/tests/unit/managed-transaction.py" --root "$ROOT" "$@"
    exit $?
  fi
done
echo 'ERROR: transaction tests require Python 3.9+' >&2
exit 2
