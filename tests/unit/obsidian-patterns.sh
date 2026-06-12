#!/usr/bin/env bash
# tests/unit/obsidian-patterns.sh
# Contract for ADR-0007: li-vault-init installs the three vault files
# idempotently and never overwrites; CAPTURE prose pins the locked
# session-note schema that sessions.base queries.

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/obsidian-patterns.sh"
echo "==============================="

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
# Hermetic: no real install (pack resolution) and no real audit dir may be touched
export LINTEL_HOME="$TMP/no-home"
export LINTEL_AUDIT_DIR="$TMP/audit"

# Sandbox repo + vault
SB="$TMP/myrepo"
mkdir -p "$SB" "$TMP/vault/50-sessions"
( cd "$SB" && git init -q . && git -c user.email=t@t -c user.name=t commit --allow-empty -m init -q )

echo ""
echo "[1] li-vault-init installs base + hub + index"
out=$( cd "$SB" && bash "$REPO_ROOT/bin/li-vault-init" --vault "$TMP/vault/50-sessions" 2>&1 )
[ -f "$TMP/vault/50-sessions/sessions.base" ] && pass "sessions.base installed" || fail "sessions.base missing: $out"
[ -f "$TMP/vault/50-sessions/myrepo.md" ] && pass "repo hub created" || fail "hub missing"
[ -f "$TMP/vault/50-sessions/00-index.md" ] && pass "index seed created" || fail "index missing"
grep -q 'type: repo-hub' "$TMP/vault/50-sessions/myrepo.md" && pass "hub has typed frontmatter" || fail "hub frontmatter wrong"

echo ""
echo "[2] idempotent — second run never overwrites"
printf 'OPERATOR EDIT\n' >> "$TMP/vault/50-sessions/myrepo.md"
out=$( cd "$SB" && bash "$REPO_ROOT/bin/li-vault-init" --vault "$TMP/vault/50-sessions" 2>&1 )
grep -q 'OPERATOR EDIT' "$TMP/vault/50-sessions/myrepo.md" && pass "hub edit preserved" || fail "hub overwritten"
echo "$out" | grep -q 'skip' && pass "reports skips" || fail "no skip reporting: $out"

echo ""
echo "[3] fails loud without a vault path; dry-run writes nothing"
rc=0; ( cd "$SB" && bash "$REPO_ROOT/bin/li-vault-init" >/dev/null 2>&1 ) || rc=$?
[ "$rc" != "0" ] && pass "no vault path → non-zero exit" || fail "silent success without vault"
mkdir -p "$TMP/vault2/50-sessions"
rc=0; out=$( cd "$SB" && bash "$REPO_ROOT/bin/li-vault-init" --vault "$TMP/vault2/50-sessions" --dry-run 2>&1 ) || rc=$?
[ "$rc" = "0" ] && echo "$out" | grep -q '\[dry-run\]' && pass "dry-run runs clean + reports" || fail "dry-run rc=$rc out=$out"
n=$(find "$TMP/vault2/50-sessions" -type f | wc -l | tr -d ' ')
[ "$n" = "0" ] && pass "dry-run writes nothing" || fail "dry-run wrote $n files"

echo ""
echo "[4] locked schema pinned in CAPTURE Step 7b"
CAP="$REPO_ROOT/skills/capture/SKILL.md"
for fld in 'type: session' 'branch:' 'outcome: shipped | in-progress | blocked | exploration'; do
  grep -qF "$fld" "$CAP" && pass "schema field: $fld" || fail "schema field missing: $fld"
done
grep -q '00-index.md' "$CAP" && pass "index maintenance documented" || fail "index maintenance missing"
grep -q 'repo hub' "$CAP" && pass "hub link documented" || fail "hub link missing"

echo ""
echo "[5] sessions.base template filters on the schema"
TPL="$REPO_ROOT/templates/obsidian/sessions.base"
grep -q 'type == "session"' "$TPL" && pass "base filters type=session" || fail "base filter missing"
grep -q 'outcome' "$TPL" && pass "base uses outcome property" || fail "base outcome missing"

echo ""
if [ "$FAILED" -eq 0 ]; then echo "ALL PASS"; else echo "FAILURES present"; exit 1; fi
