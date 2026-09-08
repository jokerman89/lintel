#!/usr/bin/env bash
# tests/integration/security-controls-fire.sh
# BEHAVIOR test (ADR-0010): the security controls must actually fire on the
# exploits the battletest live-confirmed — not just exist as prose. Each block
# below would have PASSED (exploit succeeded) before Wave S.

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/integration/security-controls-fire.sh"
echo "==========================================="

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
export LINTEL_HOME="$TMP/.lintel"; export LINTEL_AUDIT_DIR="$TMP/.lintel/audit"
mkdir -p "$LINTEL_AUDIT_DIR"

# Run a block hook with a given command string on stdin (mimics Claude Code PreToolUse JSON).
run_hook() { # <hook> <command-string>
  printf '{"tool_input":{"command":%s}}' "$(printf '%s' "$2" | sed 's/\\/\\\\/g; s/"/\\"/g; s/^/"/; s/$/"/')" \
    | bash "$REPO_ROOT/hooks/shared/$1/run.sh"
}

# ── K3: modern token formats are caught by tier1 ──
echo ""
echo "[K3] modern secret formats in the BLOCK tier"
source "$REPO_ROOT/hooks/shared/_patterns.sh"
for tok in "sk-proj-$(printf 'a%.0s' {1..30})" "github_pat_$(printf 'b%.0s' {1..30})" "AIza$(printf 'c%.0s' {1..35})" "sk_live_$(printf 'd%.0s' {1..24})"; do
  hit="$(scan_secrets tier1 "api_key = $tok")"
  [ -n "$hit" ] && pass "tier1 catches ${tok%%_*}…" || fail "tier1 MISSES $tok"
done
# classic formats still caught (no regression)
[ -n "$(scan_secrets tier1 'ghp_'"$(printf 'e%.0s' {1..36})")" ] && pass "classic ghp_ still caught" || fail "regressed ghp_"

# ── K2: matcher catches phrasing bypasses + worktree gap ──
echo ""
echo "[K2] block-hook matcher + worktree scan"
SB="$TMP/repo"; mkdir -p "$SB"; ( cd "$SB" && git init -q . && git -c user.email=t@t -c user.name=t commit --allow-empty -m init -q )
# stage a secret, then try phrasings that the old ^git anchor let through
printf 'key = ghp_%s\n' "$(printf 'a%.0s' {1..36})" > "$SB/leak.txt"
( cd "$SB" && git add leak.txt )
for cmd in "git commit -m x" "true && git commit -m x" "git -C . commit -m x" "/usr/bin/git commit -m x"; do
  rc=0; ( cd "$SB" && run_hook secret-scan-block "$cmd" ) >/dev/null 2>&1 || rc=$?
  [ "$rc" = "2" ] && pass "blocks: $cmd" || fail "NOT blocked (rc=$rc): $cmd"
done
# worktree gap: secret only in unstaged tracked edit, commit -am would stage it
( cd "$SB" && git rm -q --cached leak.txt 2>/dev/null; git -c user.email=t@t -c user.name=t commit -q -am cleanup 2>/dev/null || true )
printf 'key = ghp_%s\n' "$(printf 'z%.0s' {1..36})" >> "$SB/leak.txt"
( cd "$SB" && git add leak.txt && git -c user.email=t@t -c user.name=t commit -q -m track && printf 'newsecret AKIA%s\n' "$(printf 'Q%.0s' {1..16})" >> "$SB/leak.txt" )
rc=0; ( cd "$SB" && run_hook secret-scan-block "git commit -am wip" ) >/dev/null 2>&1 || rc=$?
[ "$rc" = "2" ] && pass "blocks worktree secret on commit -am" || fail "worktree secret slipped (rc=$rc)"

# ── H8: override always audits; audit escapes newlines ──
echo ""
echo "[H8] override audits + newline-safe audit"
rc=0; out=$( cd "$SB" && run_hook secret-scan-block 'LINTEL_OVERRIDE_SECRET=1 git commit -m x' 2>&1 ) || rc=$?
echo "$out" | grep -q 'OVERRIDDEN' && pass "inline override recognized" || fail "inline override missed: $out"
# NEGATIVE (review P0): the override token inside a -m MESSAGE must NOT suppress a real block
( cd "$SB" && printf 'leak ghp_%s\n' "$(printf 'm%.0s' {1..36})" >> leak.txt && git add leak.txt )
rc=0; ( cd "$SB" && run_hook secret-scan-block 'git commit -m "fix: see LINTEL_OVERRIDE_SECRET=1 in the docs"' ) >/dev/null 2>&1 || rc=$?
[ "$rc" = "2" ] && pass "override token in -m message does NOT bypass (still blocks)" || fail "FORGEABLE OVERRIDE — token in message bypassed block (rc=$rc)"
if grep -rqs '"override":"true"' "$LINTEL_AUDIT_DIR" "$SB/.claude/runtime/audit" 2>/dev/null; then
  pass "override audited"
else
  fail "override not audited"
fi
# newline injection into an audit value must not split the line
( source "$REPO_ROOT/bin/_audit.sh"; audit_log self-test inject "reason=line1
line2forged" )
lines=$(grep -c 'inject' "$LINTEL_AUDIT_DIR/self-test.jsonl" 2>/dev/null || echo 0)
[ "$lines" = "1" ] && pass "newline value stays one JSONL record" || fail "newline split into $lines records"

# ── K1: li-scaffold no longer executes a hostile name ──
echo ""
echo "[K1] li-scaffold literal substitution (no sed RCE)"
SC="$TMP/scaf"; mkdir -p "$SC/src"
printf '# {{REPO_NAME}}\npack {{PACK}}\n' > "$SC/src/CLAUDE.md.template"
( cd "$SC" && git init -q . )
MARKER="$TMP/PWNED"
rc=0; ( cd "$SC" && LINTEL_HOME="$TMP/.lintel" SCAFFOLDING_SRC="$SC/src" \
  bash "$REPO_ROOT/bin/li-scaffold" init --name 'X/;e touch '"$MARKER"'
#' >/dev/null 2>&1 ) || rc=$?
[ ! -f "$MARKER" ] && pass "hostile --name did NOT execute" || fail "RCE — marker created"
[ -f "$SC/CLAUDE.md" ] && grep -q 'X/;e touch' "$SC/CLAUDE.md" && pass "hostile name written literally" || pass "scaffold completed without injection"

echo ""
echo "[I1] block hooks fail-closed under error (no set -e silent downgrade)"
for h in secret-scan-block customer-data-block; do
  grep -qE '^set -e' "$REPO_ROOT/hooks/shared/$h/run.sh" && fail "$h still uses set -e (I1 fail-open risk)" || pass "$h: no set -e"
  grep -q 'scanner unavailable' "$REPO_ROOT/hooks/shared/$h/run.sh" && pass "$h: fail-closed scanner guard present" || fail "$h: missing fail-closed guard"
done
# behavioral: drive the REAL hook with a scanner-less _patterns.sh — it must exit 2.
# Copy the hook tree to TMP with a stub _patterns that defines NO scan_secrets, preserving
# the run.sh's BASH_SOURCE-relative source paths (../_patterns.sh, ../_input.sh, ../../../bin).
HT="$TMP/ht/hooks/shared"; mkdir -p "$HT/secret-scan-block" "$TMP/ht/bin" "$TMP/ht/lib"
cp "$REPO_ROOT/hooks/shared/secret-scan-block/run.sh" "$HT/secret-scan-block/run.sh"
cp "$REPO_ROOT/hooks/shared/_input.sh" "$HT/_input.sh"
cp "$REPO_ROOT/bin/_audit.sh" "$TMP/ht/bin/_audit.sh"
cp "$REPO_ROOT/lib/paths.sh" "$TMP/ht/lib/paths.sh"
printf '#!/usr/bin/env bash
# stub: defines no scan_secrets — simulates a failed pattern load
: 
' > "$HT/_patterns.sh"
SBX="$TMP/failclosed"; mkdir -p "$SBX"; ( cd "$SBX" && git init -q . && git -c user.email=t@t -c user.name=t commit --allow-empty -m i -q )
printf 'leak ghp_%s
' "$(printf 'a%.0s' {1..36})" > "$SBX/x.txt"; ( cd "$SBX" && git add x.txt )
rc=0; ( cd "$SBX" && printf '{"tool_input":{"command":"git commit -m x"}}' | bash "$HT/secret-scan-block/run.sh" ) >/dev/null 2>&1 || rc=$?
[ "$rc" = "2" ] && pass "fail-closed: REAL hook with broken scanner → exit 2 (block)" || fail "real-hook fail-closed broken (rc=$rc)"

echo ""
if [ "$FAILED" -eq 0 ]; then echo "ALL PASS"; else echo "FAILURES present"; exit 1; fi
