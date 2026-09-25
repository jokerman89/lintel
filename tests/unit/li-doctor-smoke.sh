#!/usr/bin/env bash
# tests/unit/li-doctor-smoke.sh
# li-doctor is the first command a new operator runs, yet had zero coverage
# (A3 audit). This smoke test asserts the CONTRACT — it runs to completion with
# a bounded exit code and prints its section headers — not exact strings, so it
# survives li-doctor's ongoing edits. Sandboxed HOME so it never reads or writes
# the operator's real ~/.lintel.
# tag: li-doctor smoke
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/li-doctor-smoke.sh"
echo "=============================="

DOC="$REPO_ROOT/bin/li-doctor"
[ -f "$DOC" ] || { fail "bin/li-doctor missing"; echo "RESULT: FAIL"; exit 1; }

# Parses without error (catches a half-applied edit before anyone runs it).
bash -n "$DOC" && pass "li-doctor parses (bash -n)" || fail "li-doctor has a syntax error"

# macOS mktemp ignores TMPDIR and answers under the /var link; Lintel refuses linked roots.
TMP="$(mktemp -d)" && TMP="$(cd "${TMP:?}" && pwd -P)" || exit 1; trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/home" "$TMP/target"
run_doctor() { # <arg...>  → captures output to $OUT, rc to $RC, sandboxed HOME
  OUT="$TMP/out.txt"; RC=0
  if command -v timeout >/dev/null 2>&1; then
    HOME="$TMP/home" LINTEL_HOME="$TMP/home/.lintel" timeout 30 bash "$DOC" \
      --source "$REPO_ROOT" --target "$TMP/target" "$@" > "$OUT" 2>&1 || RC=$?
  else
    HOME="$TMP/home" LINTEL_HOME="$TMP/home/.lintel" bash "$DOC" \
      --source "$REPO_ROOT" --target "$TMP/target" "$@" > "$OUT" 2>&1 || RC=$?
  fi
}

# 1. default run: bounded rc (0 clean / 1 warnings), never a crash (>1) or hang (124).
run_doctor
[ "$RC" != "124" ] && pass "default run does not hang" || fail "li-doctor HUNG (timeout)"
case "$RC" in 0|1) pass "default run rc bounded ($RC)";; *) fail "li-doctor crashed (rc=$RC)";; esac
[ -s "$OUT" ] && pass "default run produced output" || fail "li-doctor produced no output"
grep -q "Installed CLIs" "$OUT" && pass "section: Installed CLIs present" || fail "missing the Installed-CLIs section"

# 2. --verbose runs the same (the arithmetic-on-empty-stat path lives here).
run_doctor --verbose
case "$RC" in 0|1) pass "--verbose rc bounded ($RC)";; *) fail "--verbose crashed (rc=$RC)";; esac

# 3. an unknown flag is rejected cleanly (rc 2), not a stack trace.
run_doctor --no-such-flag
[ "$RC" = "2" ] && pass "unknown flag → clean rc 2" || fail "unknown flag rc=$RC (expected 2)"

# 4. Real structured health preserves local failure and the unverified host boundary.
run_doctor --quick --json
[ "$RC" = "1" ] && pass "incomplete target health retains exit 1" || fail "incomplete target health rc=$RC"
python="${LINTEL_PYTHON:-python3}"
if "$python" -I -B - "$OUT" "$TMP/target" <<'PY'
import json
from pathlib import Path
import sys
report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert Path(report["target"]).resolve() == Path(sys.argv[2]).resolve()
assert report["host_activation"] == report["hook_execution"] == "unverified"
assert report["issues"] and report["foundation_missing"]
assert report["status"] == "attention"
PY
then pass "JSON contains actual local findings, not invented activation"
else fail "invalid structured diagnostic output"; fi

echo ""
if [ "$FAILED" = 1 ]; then echo "RESULT: FAIL"; exit 1; fi
echo "RESULT: PASS"
