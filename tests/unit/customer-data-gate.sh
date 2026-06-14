#!/usr/bin/env bash
# tests/unit/customer-data-gate.sh
# Executes the customer-data-block hook end-to-end (the A1 audit found the
# wrapper had no execution test — only the engine in hook-patterns.sh). Mirrors
# the secret-gate harness: a real sandbox repo, env seams keep every write
# inside $TMP, </dev/null gives the stdin reader instant EOF so argv1 is used.
# tag: v5.2 hook gate content
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/customer-data-gate.sh"
echo "================================="

command -v git >/dev/null 2>&1 || { echo "  SKIP: git unavailable"; exit 0; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
export LINTEL_HOME="$TMP/lintel-home" LINTEL_AUDIT_DIR="$TMP/audit"
mkdir -p "$LINTEL_AUDIT_DIR"
HOOK="$REPO_ROOT/hooks/shared/customer-data-block/run.sh"
[ -f "$HOOK" ] || { fail "hook missing: $HOOK"; echo "RESULT: FAIL"; exit 1; }

R="$TMP/repo"; mkdir -p "$R"
git -C "$R" init -q
git -C "$R" config user.email t@t.local
git -C "$R" config user.name t
git -C "$R" commit --allow-empty -qm init

# A Swedish phone on an added line — the format scan_customer is known to catch
# (hook-patterns.sh); built by concat so THIS file never trips a scanner. The
# point of this test is the WRAPPER (does run.sh block on a hit), not regex breadth.
PHONE="+46 ""70 123 4567"
printf 'contact: %s\n' "$PHONE" > "$R/notes.txt"
git -C "$R" add notes.txt

# 1. committing customer PII must BLOCK (exit 2), however the commit is phrased
rc=0; (cd "$R" && bash "$HOOK" "git commit -am x" </dev/null) >/dev/null 2>&1 || rc=$?
[ "$rc" = "2" ] && pass "customer PII commit BLOCKED (rc=2)" || fail "customer PII not blocked (rc=$rc)"

# 2. the legit leading-prefix override allows + audits (never an inline -m token)
rc=0; (cd "$R" && bash "$HOOK" "LINTEL_OVERRIDE_CUSTOMER_DATA=1 LINTEL_OVERRIDE_REASON=test git commit -am x" </dev/null) >/dev/null 2>&1 || rc=$?
[ "$rc" = "0" ] && pass "legit override allowed (rc=0)" || fail "legit override broke (rc=$rc)"
grep -q '"override":"true"' "$LINTEL_AUDIT_DIR/hooks.jsonl" 2>/dev/null \
  && pass "override audit-logged" || fail "override left no audit record"

# 3. a newline-forged override inside -m must NOT suppress the block (L-012)
rc=0; (cd "$R" && bash "$HOOK" "git commit -am \"ok
LINTEL_OVERRIDE_CUSTOMER_DATA=1 x\"" </dev/null) >/dev/null 2>&1 || rc=$?
[ "$rc" = "2" ] && pass "newline-forged override still BLOCKED" || fail "newline override forgery bypassed (rc=$rc)"

# 4. a clean commit (no PII) passes
git -C "$R" reset -q
printf 'just a clean note\n' > "$R/notes.txt"; git -C "$R" add notes.txt
rc=0; (cd "$R" && bash "$HOOK" "git commit -am x" </dev/null) >/dev/null 2>&1 || rc=$?
[ "$rc" = "0" ] && pass "clean commit allowed (rc=0)" || fail "clean commit wrongly blocked (rc=$rc)"

echo ""
if [ "$FAILED" = 1 ]; then echo "RESULT: FAIL"; exit 1; fi
echo "RESULT: PASS"
