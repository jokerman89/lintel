#!/usr/bin/env bash
# DESCRIPTION: Observed-color contrast math and explicit unsupported-paint refusals.
# TAGS: unit,codex-compatible
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
command -v "$python" >/dev/null 2>&1 || {
  printf '%s\n' 'Missing Python 3.9+; no dependency was installed.' >&2
  exit 127
}
exec "$python" -I -B "$root/tests/unit/design-contrast.py" "$@"
