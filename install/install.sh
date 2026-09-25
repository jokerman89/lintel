#!/usr/bin/env bash
# Native bare installation; Python-based runtime operations remain separate.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
case "${OSTYPE:-}" in
  msys*|cygwin*)
    case "${LINTEL_HOME:-}" in /)
      echo 'ERROR: destination must be separate from the source checkout and cannot be a filesystem root.' >&2
      exit 1 ;;
    esac
    previous=""
    for argument in "$@"; do
      case "$previous:$argument" in --home:/|-Home:/|-home:/)
        echo 'ERROR: destination must be separate from the source checkout and cannot be a filesystem root.' >&2
        exit 1 ;;
      esac
      previous="$argument"
    done
    NATIVE_POWERSHELL="${LINTEL_POWERSHELL:-}"
    if [ -n "$NATIVE_POWERSHELL" ]; then
      case "$NATIVE_POWERSHELL" in [A-Za-z]:*|\\\\*) NATIVE_POWERSHELL="$(cygpath -u "$NATIVE_POWERSHELL")" ;; esac
      [ -f "$NATIVE_POWERSHELL" ] || { echo 'ERROR: selected LINTEL_POWERSHELL executable is unavailable; no fallback.' >&2; exit 2; }
    else
      for candidate in powershell.exe pwsh.exe; do
        if command -v "$candidate" >/dev/null 2>&1; then NATIVE_POWERSHELL="$candidate"; break; fi
      done
    fi
    [ -n "$NATIVE_POWERSHELL" ] || { echo 'ERROR: Windows native installation needs an available PowerShell 5.1+; no files changed.' >&2; exit 2; }
    "$NATIVE_POWERSHELL" -NoProfile -NonInteractive -Command \
      'if ($PSVersionTable.PSVersion -lt [version]"5.1") { exit 2 }' || exit $?
    if [ -n "${LINTEL_RECOVERY_STORE:-}" ]; then set -- -Store "$LINTEL_RECOVERY_STORE" "$@"; fi
    exec "$NATIVE_POWERSHELL" -NoProfile -NonInteractive -File "$SCRIPT_DIR/install.ps1" \
      -Home "${LINTEL_HOME:-$HOME/.lintel}" "$@"
    ;;
esac
source "$SCRIPT_DIR/native.sh"
lintel_native_main "$@"
