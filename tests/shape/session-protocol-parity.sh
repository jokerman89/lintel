#!/usr/bin/env bash
# Every primary entry and scaffold template must carry the full canonical startup protocol.
# tag: shape instructions copilot cross-cli
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON="$(command -v python3 || command -v python || true)"
if [ -z "$PYTHON" ]; then
  echo "SKIP: Python 3.9+ required"
  exit 0
fi
"$PYTHON" "$ROOT/bin/li-instructions.py" check
