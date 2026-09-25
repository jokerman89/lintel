#!/usr/bin/env bash
# DESCRIPTION: Every canonical workflow has a bare name matching its source folder.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
bash "$ROOT/tests/shape/native-command-surface.sh" --check names
test -f "$ROOT/scaffolding/01-foundation/CORE-PRINCIPLES.md"
test -f "$ROOT/packs/_default/pack.yaml"
echo 'PASS: canonical identities, shared foundation and neutral baseline are present.'
