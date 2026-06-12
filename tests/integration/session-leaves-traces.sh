#!/usr/bin/env bash
# tests/integration/session-leaves-traces.sh
# BEHAVIOR test (ADR-0008): a session must leave observable traces — not just
# carry prose promising them. The fit audit found the shape tests asserted
# documentation while zero state/digest/audit records existed on the machine.
# This test runs the actual machinery in a hermetic sandbox and asserts the
# traces appear.

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/integration/session-leaves-traces.sh"
echo "==========================================="

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
export LINTEL_HOME="$TMP/.lintel"
export LINTEL_AUDIT_DIR="$TMP/.lintel/audit"
mkdir -p "$LINTEL_HOME/audit"

# Hermetic migrated repo with memory content
SB="$TMP/repo"
mkdir -p "$SB/.claude/memory" "$SB/.claude/decisions"
( cd "$SB" && git init -q . && git -c user.email=t@t -c user.name=t commit --allow-empty -m init -q )
printf 'layout_version: 5\n' > "$SB/.claude/lintel-layout.yaml"
printf '# Lessons\n\n## L-001 — Test lesson\n**Rule:** test.\n' > "$SB/.claude/memory/lessons.md"
printf '## current\nworking on traces\n' > "$SB/.claude/memory/working-state.md"
printf '# ADR-0001: test decision\n' > "$SB/.claude/decisions/0001-test.md"

echo ""
echo "[1] session-digest FIRES and leaves traces (stdout envelope + audit record)"
out=$( cd "$SB" && bash "$REPO_ROOT/hooks/shared/session-digest/run.sh" )
echo "$out" | grep -q 'LINTEL SESSION DIGEST' && pass "digest envelope emitted" || fail "no digest envelope: $out"
echo "$out" | grep -q 'Test lesson' && pass "digest carries lessons" || fail "lessons missing from digest"
echo "$out" | grep -q 'ADR-0001' && pass "digest carries decisions" || fail "decisions missing from digest"
if grep -q 'session_digest' "$SB/.claude/runtime/audit/hooks.jsonl" 2>/dev/null \
   || grep -q 'session_digest' "$LINTEL_AUDIT_DIR/hooks.jsonl" 2>/dev/null; then
  pass "digest left an audit record"
else
  fail "no audit record from digest"
fi

echo ""
echo "[2] state ledger: state_append writes, footer + state_last read it back"
( cd "$SB" && bash -c "
  source '$REPO_ROOT/lib/state.sh'
  state_append SENSE DONE next=SCOPE mode=internal-tool
  state_append SCOPE DONE next=DEFINE size=S
" )
[ -f "$SB/.claude/runtime/state/00-state.md" ] && pass "00-state.md created" || fail "no state file"
last=$( cd "$SB" && bash -c "source '$REPO_ROOT/lib/state.sh'; state_last phase" )
[ "$last" = "SCOPE" ] && pass "state_last reads last phase" || fail "state_last got '$last'"
footer=$( cd "$SB" && bash -c "source '$REPO_ROOT/lib/cycle-footer.sh'; LINTEL_ASCII=1 render_cycle_footer --compact" )
echo "$footer" | grep -q 'SCOPE' && pass "footer resolves position from ledger" || fail "footer blind to ledger: $footer"
nxt=$( cd "$SB" && bash -c "source '$REPO_ROOT/lib/state.sh'; state_last next_recommended" )
[ "$nxt" = "DEFINE" ] && pass "next_recommended readable" || fail "next_recommended got '$nxt'"

echo ""
echo "[3] memory-budget-warn FIRES over budget (and stays silent within)"
out=$( cd "$SB" && LINTEL_MEMORY_INDEX_MAX_LINES=1000 bash "$REPO_ROOT/hooks/shared/memory-budget-warn/run.sh" )
[ -z "$out" ] && pass "silent within budget" || fail "noisy within budget: $out"
printf '# big index\n' > "$SB/.claude/memory/MEMORY.md"
out=$( cd "$SB" && LINTEL_MEMORY_INDEX_MAX_LINES=0 bash "$REPO_ROOT/hooks/shared/memory-budget-warn/run.sh" )
echo "$out" | grep -q 'WARN' && pass "warns over budget" || fail "silent over budget"

echo ""
echo "[4] plugin hook auto-registration manifest is valid and complete"
HJ="$REPO_ROOT/hooks/hooks.json"
[ -f "$HJ" ] && pass "hooks/hooks.json exists" || fail "hooks/hooks.json missing"
if python -c "import json,sys; json.load(open(sys.argv[1], encoding='utf-8'))" "$HJ" 2>/dev/null \
   || python3 -c "import json,sys; json.load(open(sys.argv[1], encoding='utf-8'))" "$HJ" 2>/dev/null; then
  pass "hooks.json parses as JSON"
else
  fail "hooks.json invalid JSON"
fi
for h in session-digest no-secrets-in-edit secret-scan-block customer-data-block no-direct-main-push memory-budget-warn; do
  grep -q "$h" "$HJ" && pass "registers $h" || fail "missing registration: $h"
done
# Every referenced script must exist relative to plugin root (= repo root) and be executable in the index
while IFS= read -r script; do
  rel="${script#\$\{CLAUDE_PLUGIN_ROOT\}/}"
  [ -f "$REPO_ROOT/$rel" ] && pass "script exists: $rel" || fail "registered script missing: $rel"
  mode=$(cd "$REPO_ROOT" && git ls-files -s "$rel" 2>/dev/null | awk '{print $1}')
  [ "$mode" = "100755" ] && pass "executable in index: $rel" || fail "not 100755 in index: $rel ($mode)"
done < <(grep -o '\${CLAUDE_PLUGIN_ROOT}[^"]*' "$HJ")

echo ""
if [ "$FAILED" -eq 0 ]; then echo "ALL PASS"; else echo "FAILURES present"; exit 1; fi
