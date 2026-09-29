#!/usr/bin/env bash
# tag: unit copilot native-artifacts
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 -B -S "$ROOT/tests/unit/native-artifacts.py"
