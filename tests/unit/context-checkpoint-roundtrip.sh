#!/usr/bin/env bash
# tests/unit/context-checkpoint-roundtrip.sh
# Exercises bin/_context.sh mechanically (the A2 audit flagged the context-save
# machinery as wired-but-never-exercised). Sandboxed env seams keep every write
# inside $TMP; the roundtrip is save_path → write content → context_latest finds
# it → context_list counts it.
# tag: context checkpoint roundtrip
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/context-checkpoint-roundtrip.sh"
echo "==========================================="

command -v git >/dev/null 2>&1 || { echo "  SKIP: git unavailable"; exit 0; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
# A sandbox repo with NO v5 layout marker → _context falls back to
# $LINTEL_HOME/sessions/<branch>/ (lintel_sessions_dir's documented fallback).
export LINTEL_HOME="$TMP/lintel-home"
export LINTEL_REPO_ROOT="$TMP/repo"
mkdir -p "$LINTEL_REPO_ROOT"
git -C "$LINTEL_REPO_ROOT" init -q
git -C "$LINTEL_REPO_ROOT" config user.email t@t.local
git -C "$LINTEL_REPO_ROOT" config user.name t
git -C "$LINTEL_REPO_ROOT" commit --allow-empty -qm init

# shellcheck disable=SC1091
source "$REPO_ROOT/bin/_context.sh"

cd "$LINTEL_REPO_ROOT" || { fail "cd sandbox repo"; echo "RESULT: FAIL"; exit 1; }

# no checkpoints yet → context_latest empty + rc 1
if context_latest >/dev/null 2>&1; then fail "context_latest non-empty on a fresh repo"; else pass "fresh repo: context_latest empty (rc 1)"; fi

# save → write content
P="$(context_save_path mywork)"
case "$P" in
  "$TMP"/*) pass "save_path lands inside the sandbox" ;;
  *) fail "save_path escaped the sandbox: $P" ;;
esac
case "$P" in *-context-save.md) pass "save_path has the canonical suffix" ;; *) fail "save_path suffix wrong: $P" ;; esac
printf '# checkpoint\nphase: BUILD\n' > "$P"
[ -f "$P" ] && pass "checkpoint file written" || fail "checkpoint file not written"

# latest finds exactly what we wrote
L="$(context_latest)"
[ "$L" = "$P" ] && pass "context_latest returns the saved checkpoint" || fail "context_latest=$L expected=$P"
[ "$(context_list | wc -l | tr -d ' ')" = "1" ] && pass "context_list counts the one checkpoint" || fail "context_list count wrong"

# a second save is newest
sleep 1
P2="$(context_save_path later)"; printf 'second\n' > "$P2"
[ "$(context_latest)" = "$P2" ] && pass "newest checkpoint wins" || fail "context_latest did not advance to the newer save"

echo ""
if [ "$FAILED" = 1 ]; then echo "RESULT: FAIL"; exit 1; fi
echo "RESULT: PASS"
