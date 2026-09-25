#!/usr/bin/env bash
# DESCRIPTION: Reject retired workflow routing and unresolved current local references.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
for candidate in python python3; do
  if command -v "$candidate" >/dev/null 2>&1 &&
      "$candidate" -B -c 'import sys; raise SystemExit(sys.version_info < (3, 9))' >/dev/null 2>&1; then
    exec "$candidate" -B "$ROOT/tests/shape/native-command-surface.py" "$@"
  fi
done
echo 'ERROR: command-surface checks require Python 3.9+.' >&2
exit 2
