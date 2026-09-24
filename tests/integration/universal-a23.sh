#!/usr/bin/env bash
# component: universal-a23-runner
# implements: ADR-0028, ADR-0029, ADR-0030
# intent: .claude/plans/universal-implementation/packages/P14.md
# constraints: synthetic environment before Python; retain roots; no jq or global settings
# last_intent_review: 2026-09-24
# DESCRIPTION: Installed caller-child profile bridge and joined profile/work/domain/review/resume.
# TAGS: integration,p14-a23
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON="$(command -v python || command -v python3)" || { echo "FAIL: Python required" >&2; exit 2; }
GIT="$(command -v git)" || { echo "FAIL: Git required" >&2; exit 2; }
BASH_TOOL="$(command -v bash)"
if [ "$#" -gt 1 ]; then echo "Usage: universal-a23.sh [new-owned-work-directory]" >&2; exit 2; fi
if [ "$#" -eq 1 ]; then
  RUN="$1"
  if command -v cygpath >/dev/null 2>&1; then RUN="$(cygpath -u "$RUN")"; fi
  [ ! -e "$RUN" ] || { echo "FAIL: preserve occupied evidence root: $RUN" >&2; exit 2; }
  mkdir "$RUN"
else
  RUN="$(mktemp -d "${TMPDIR:-/tmp}/li-a23.XXXXXXXX")"
fi
RUN="$(cd "$RUN" && pwd -P)"
native() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi; }
mkdir -p "$RUN/h/AppData/Roaming" "$RUN/h/AppData/Local" "$RUN/h/config" \
  "$RUN/h/cache" "$RUN/h/data" "$RUN/h/state" "$RUN/t"
: > "$RUN/empty-git-config"
mount_line="$(mount | grep ' on /tmp ' || true)"
printf '%s\n' "$mount_line" > "$RUN/mount-before.txt"
[ -d /tmp ] || { echo "FAIL: existing /tmp mount is unavailable; no repair attempted" >&2; exit 2; }
PATH_SAFE="$(dirname "$PYTHON"):$(dirname "$GIT"):$(dirname "$BASH_TOOL"):/usr/bin:/bin"
SYSTEM_ROOT="${SystemRoot:-${SYSTEMROOT:-}}"
if command -v cygpath >/dev/null 2>&1; then PATH_SAFE="$PATH_SAFE:$(cygpath -u "$SYSTEM_ROOT")/System32"; fi
RN="$(native "$RUN")"; HN="$(native "$RUN/h")"
extra=()
if [ -n "${LINTEL_POWERSHELL:-}" ]; then extra+=("LINTEL_POWERSHELL=$LINTEL_POWERSHELL"); fi
rc=0
env -i PATH="$PATH_SAFE" PATHEXT='.COM;.EXE;.BAT;.CMD' \
  SystemRoot="$SYSTEM_ROOT" WINDIR="$SYSTEM_ROOT" COMSPEC="${COMSPEC:-${ComSpec:-}}" \
  HOME="$HN" USERPROFILE="$HN" APPDATA="$HN/AppData/Roaming" LOCALAPPDATA="$HN/AppData/Local" \
  XDG_CONFIG_HOME="$HN/config" XDG_CACHE_HOME="$HN/cache" XDG_DATA_HOME="$HN/data" XDG_STATE_HOME="$HN/state" \
  TEMP="$RN/t" TMP="$RN/t" TMPDIR="$RN/t" USER=synthetic-a23 USERNAME=synthetic-a23 \
  PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL="$RN/empty-git-config" GIT_CONFIG_SYSTEM="$RN/empty-git-config" \
  GIT_CEILING_DIRECTORIES="$RN" GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=Never \
  "${extra[@]}" "$PYTHON" -I -B "$ROOT/tests/integration/universal-a23.py" \
  --root "$(native "$ROOT")" --work-dir "$RN" --bash "$(native "$BASH_TOOL")" --git "$(native "$GIT")" \
  >"$RUN/outer.stdout.log" 2>"$RUN/outer.stderr.log" || rc=$?
cat "$RUN/outer.stdout.log"
cat "$RUN/outer.stderr.log" >&2
mount_after="$(mount | grep ' on /tmp ' || true)"
printf '%s\n' "$mount_after" > "$RUN/mount-shell-after.txt"
if [ "$mount_after" != "$mount_line" ] || [ ! -d /tmp ]; then
  echo "FAIL: shared /tmp mapping changed or became unavailable; no repair attempted" >&2
  [ "$rc" -ne 0 ] || rc=2
fi
printf 'A23 retained evidence: %s; exit %s\n' "$RN" "$rc"
exit "$rc"
