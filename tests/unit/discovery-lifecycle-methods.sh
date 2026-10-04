#!/usr/bin/env bash
# Local source/helper regression entry; no installation or profile bootstrap.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 -B "$root/tests/unit/discovery-lifecycle-methods.py" "$@"
