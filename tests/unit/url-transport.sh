#!/usr/bin/env bash
# Uses a real urllib opener with injected I/O; never makes an external request.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 -B "$root/tests/unit/url-transport.py" "$@"
