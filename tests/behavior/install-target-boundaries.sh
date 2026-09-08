#!/usr/bin/env bash
# Refuse self-install and linked managed destinations before writing anything.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
source_root="$TMP/source"
mkdir -p "$source_root/install" "$source_root/lib"
cp "$ROOT/install/install.sh" "$source_root/install/install.sh"
cp "$ROOT/lib/frontmatter.sh" "$source_root/lib/frontmatter.sh"
for destination in "$source_root" "$source_root/nested" "$source_root/nested/.." "$TMP" /; do
  rc=0
  output=$(LINTEL_HOME="$destination" bash "$source_root/install/install.sh" 2>&1) || rc=$?
  [ "$rc" -ne 0 ] || { echo "FAIL: unsafe install accepted: $destination"; exit 1; }
  printf '%s\n' "$output" | grep -q 'source checkout'
  [ ! -e "$source_root/profile.yaml" ] || { echo 'FAIL: self-install wrote profile'; exit 1; }
done
[ ! -e "$source_root/nested" ] || { echo 'FAIL: rejected nested install created destination'; exit 1; }
mkdir -p "$TMP/home" "$TMP/home-file/lib" "$TMP/home-seed" "$TMP/outside"
printf 'outside sentinel\n' > "$TMP/outside/sentinel"
if ! command -v python3 >/dev/null 2>&1; then
  echo 'PASS: overlapping installer destinations refused before mutation'
  echo 'SKIP: python3 required for native Windows/POSIX symlink assertions'
  exit 0
fi
# Python creates actual Windows symlinks; Git Bash ln may silently copy instead.
python3 - "$TMP" <<'PY'
import os
from pathlib import Path
import sys
root = Path(sys.argv[1])
try:
    os.symlink(root / 'outside', root / 'home/bin', target_is_directory=True)
    os.symlink(root / 'outside/sentinel', root / 'home-file/lib/paths.sh')
    os.symlink(root / 'outside/absent-profile', root / 'home-seed/profile.yaml')
    os.symlink(root / 'source', root / 'source-alias', target_is_directory=True)
except OSError as exc:
    print(f'SKIP: host refused native symlink creation: {exc}')
    sys.exit(77)
PY
rc=0
output=$(LINTEL_HOME="$source_root" bash "$TMP/source-alias/install/install.sh" 2>&1) || rc=$?
[ "$rc" -ne 0 ] || { echo 'FAIL: source-alias self-install accepted'; exit 1; }
printf '%s\n' "$output" | grep -q 'source checkout'
[ ! -e "$source_root/profile.yaml" ] || { echo 'FAIL: source-alias install mutated checkout'; exit 1; }
for destination in "$TMP/home" "$TMP/home-file" "$TMP/home-seed"; do
  rc=0
  output=$(LINTEL_HOME="$destination" bash "$source_root/install/install.sh" 2>&1) || rc=$?
  [ "$rc" -ne 0 ] || { echo 'FAIL: linked install accepted'; exit 1; }
  printf '%s\n' "$output" | grep -q 'Linked'
  [ ! -e "$destination/profile.yaml" ] || { echo 'FAIL: linked install changed profile'; exit 1; }
  [ "$(cat "$TMP/outside/sentinel")" = 'outside sentinel' ] || { echo 'FAIL: wrote through install link'; exit 1; }
done
[ ! -e "$TMP/outside/absent-profile" ] || { echo 'FAIL: seeded through dangling profile link'; exit 1; }
echo 'PASS: unsafe installer destinations refused before mutation'
