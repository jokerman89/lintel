#!/usr/bin/env bash
# tag: universal adapter-navigation
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 -B -S "$ROOT/tests/unit/adapter-navigation.py"
