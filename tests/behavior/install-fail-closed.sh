#!/usr/bin/env bash
# A failed runtime copy must fail installation instead of reporting success.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/shim"
REAL_CP="$(command -v cp)"
export REAL_CP
cat > "$TMP/shim/cp" <<'SH'
#!/usr/bin/env bash
for arg in "$@"; do
  case "$arg" in */lib/.) echo 'simulated runtime copy failure' >&2; exit 17 ;; esac
done
exec "$REAL_CP" "$@"
SH
chmod +x "$TMP/shim/cp"
rc=0
output=$(PATH="$TMP/shim:$PATH" LINTEL_HOME="$TMP/install" bash "$ROOT/install/install.sh" 2>&1) || rc=$?
[ "$rc" -ne 0 ] || { echo 'FAIL: installer hid a failed runtime copy'; exit 1; }
if printf '%s\n' "$output" | grep -q 'Install complete'; then
  echo 'FAIL: installer reported completion after copy failure'; exit 1
fi
printf '%s\n' "$output" | grep -q 'simulated runtime copy failure'
echo 'PASS: installer fails visibly on incomplete runtime copy'
