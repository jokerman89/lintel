#!/usr/bin/env bash
# component: universal-profile-scenario-preparation-entry
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P14.md
# constraints: synthetic environment before Python; never dispatch native actors
# last_intent_review: 2026-09-23
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [ "$#" -gt 0 ]; then
  : "${P14_ISOLATION_ROOT:?Explicit arguments require an inspected synthetic environment}"
  : "${P14_PYTHON:?Supply the explicit inspected Python executable}"
  PYTHON="$P14_PYTHON"
  if command -v cygpath >/dev/null 2>&1; then PYTHON="$(cygpath -u "$PYTHON")"; fi
  exec "$PYTHON" -I -B "$ROOT/tests/integration/universal-profile-scenarios.py" --root "$ROOT" "$@"
fi

# The ordinary test-runner entry has no arguments. No Python/product code runs
# before this new root and the allowlisted environment are established.
PYTHON="$(command -v python || command -v python3)" || { echo "Python required" >&2; exit 2; }
GIT="$(command -v git)" || { echo "Git required" >&2; exit 2; }
BASH_TOOL="$(command -v bash)" || { echo "Bash required" >&2; exit 2; }
native() {
  if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi
}
RUN="$(mktemp -d "${TMPDIR:-/tmp}/p14-profile-prep.XXXXXXXX")"
RUN="$(cd "$RUN" && pwd -P)"
HOME_DIR="$RUN/outer-home"
TARGET="$RUN/outer-target"
mkdir -p "$HOME_DIR/AppData/Roaming" "$HOME_DIR/AppData/Local" \
  "$HOME_DIR/.config" "$HOME_DIR/.cache" "$HOME_DIR/.local/share" "$HOME_DIR/.local/state" \
  "$HOME_DIR/.lintel/packs" "$RUN/temp" "$TARGET/.claude/runtime/audit" "$TARGET/.claude/runtime/state"
: > "$RUN/empty-git-config"
: > "$RUN/launcher.stdout.log"
: > "$RUN/launcher.stderr.log"
SAFE_PATH="$(dirname "$PYTHON"):$(dirname "$GIT"):$(dirname "$BASH_TOOL"):/usr/bin:/bin"
SYSTEM_ROOT="${SystemRoot:-${SYSTEMROOT:-}}"
if command -v cygpath >/dev/null 2>&1; then
  [ -n "$SYSTEM_ROOT" ] || { echo "SystemRoot is required on Windows" >&2; exit 2; }
  SAFE_PATH="$SAFE_PATH:$(cygpath -u "$SYSTEM_ROOT")/System32"
fi
RUN_N="$(native "$RUN")"; HOME_N="$(native "$HOME_DIR")"; TARGET_N="$(native "$TARGET")"
ROOT_N="$(native "$ROOT")"; PYTHON_N="$(native "$PYTHON")"
GIT_N="$(native "$GIT")"; BASH_N="$(native "$BASH_TOOL")"
rc=0
env -i PATH="$SAFE_PATH" PATHEXT='.COM;.EXE;.BAT;.CMD' \
  SystemRoot="$SYSTEM_ROOT" WINDIR="$SYSTEM_ROOT" COMSPEC="${COMSPEC:-${ComSpec:-}}" \
  HOME="$HOME_N" USERPROFILE="$HOME_N" \
  APPDATA="$HOME_N/AppData/Roaming" LOCALAPPDATA="$HOME_N/AppData/Local" \
  XDG_CONFIG_HOME="$HOME_N/.config" XDG_CACHE_HOME="$HOME_N/.cache" \
  XDG_DATA_HOME="$HOME_N/.local/share" XDG_STATE_HOME="$HOME_N/.local/state" \
  TEMP="$RUN_N/temp" TMP="$RUN_N/temp" TMPDIR="$RUN_N/temp" \
  USER=synthetic-p14 USERNAME=synthetic-p14 \
  P14_ISOLATION_ROOT="$RUN_N" P14_PYTHON="$PYTHON_N" \
  LINTEL_SOURCE_ROOT="$ROOT_N" LINTEL_REPO_ROOT="$TARGET_N" \
  LINTEL_HOME="$HOME_N/.lintel" LINTEL_PACKS_DIR="$HOME_N/.lintel/packs" \
  LINTEL_ACTIVE_PACK_FILE="$HOME_N/.lintel/packs/active-pack" \
  LINTEL_AUDIT_DIR="$TARGET_N/.claude/runtime/audit" LINTEL_STATE_DIR="$TARGET_N/.claude/runtime/state" \
  PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL="$RUN_N/empty-git-config" \
  GIT_CONFIG_SYSTEM="$RUN_N/empty-git-config" GIT_CEILING_DIRECTORIES="$RUN_N" \
  GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=Never \
  "$PYTHON" -I -B "$ROOT/tests/integration/universal-profile-scenarios.py" \
  --root "$ROOT_N" --run-root "$RUN_N" --git "$GIT_N" --bash "$BASH_N" \
  >"$RUN/launcher.stdout.log" 2>"$RUN/launcher.stderr.log" || rc=$?
cat "$RUN/launcher.stdout.log"
cat "$RUN/launcher.stderr.log" >&2
printf 'P14 retained preparation evidence: %s (exit %s)\n' "$RUN_N" "$rc"
exit "$rc"
