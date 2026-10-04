#!/usr/bin/env bash
# DESCRIPTION: Generation controls, owned outputs and source-preserving publication.
# TAGS: integration,codex-compatible
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
command -v "$python" >/dev/null 2>&1 || {
  printf '%s\n' 'Missing Python 3.9+; no dependency was installed.' >&2
  exit 127
}
export TMPDIR="${TMPDIR:-$("$python" -I -B -c 'import tempfile; print(tempfile.gettempdir())')}"
if command -v cygpath >/dev/null 2>&1; then
  TMPDIR="$(cygpath -w "$TMPDIR")"
  export LINTEL_TEST_BASH="${LINTEL_TEST_BASH:-$(cygpath -w "$(command -v bash)")}"
else
  export LINTEL_TEST_BASH="${LINTEL_TEST_BASH:-$(command -v bash)}"
fi
exec "$python" -I -B "$root/tests/integration/generation-safety.py" "$@"
