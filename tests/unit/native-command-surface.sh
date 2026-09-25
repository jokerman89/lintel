#!/usr/bin/env bash
# DESCRIPTION: Synthetic acceptance/refusal cases for current workflow references.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
for candidate in python python3; do
  if command -v "$candidate" >/dev/null 2>&1 &&
      "$candidate" -B -c 'import sys; raise SystemExit(sys.version_info < (3, 9))' >/dev/null 2>&1; then
    exec "$candidate" -B "$ROOT/tests/unit/native-command-surface.py" "$@"
  fi
done
echo 'ERROR: command-surface tests require Python 3.9+.' >&2
exit 2
