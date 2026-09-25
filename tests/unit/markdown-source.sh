#!/usr/bin/env bash
# tag: universal markdown-source
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 -B -S "$ROOT/tests/unit/markdown-source.py"
