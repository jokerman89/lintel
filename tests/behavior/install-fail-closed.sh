#!/usr/bin/env bash
# A real publication/copy failure must not produce installation success.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
case "${OSTYPE:-}" in
  msys*|cygwin*)
    bash "$ROOT/tests/integration/universal-lifecycle.sh" --native-small \
      NativeInstallLifecycle.test_bash_entry_interruption_recovery_and_consumed_permission
    exit $?
    ;;
esac
# macOS mktemp ignores TMPDIR and answers under the /var link; Lintel refuses linked roots.
TMP="$(mktemp -d)" && TMP="$(cd "${TMP:?}" && pwd -P)" || exit 1
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/shim"
export REAL_CP="$(command -v cp)"
export INSTALL_TEST_SOURCE="$ROOT"
cat > "$TMP/shim/cp" <<'SH'
#!/usr/bin/env bash
for arg in "$@"; do
  case "$arg" in "$INSTALL_TEST_SOURCE"/lib/*)
    echo 'simulated runtime copy failure' >&2
    exit 17 ;;
  esac
done
exec "$REAL_CP" "$@"
SH
chmod +x "$TMP/shim/cp"
rc=0
output=$(PATH="$TMP/shim:$PATH" HOME="$TMP/home" LINTEL_HOME="$TMP/install" \
  bash "$ROOT/install/install.sh" 2>&1) || rc=$?
[ "$rc" -ne 0 ] || { echo 'FAIL: installer hid a failed runtime copy'; exit 1; }
if printf '%s\n' "$output" | grep -q 'Install complete'; then
  echo 'FAIL: installer reported completion after copy failure'; exit 1
fi
printf '%s\n' "$output" | grep -q 'simulated runtime copy failure'
echo 'PASS: installer fails visibly on incomplete runtime copy'
