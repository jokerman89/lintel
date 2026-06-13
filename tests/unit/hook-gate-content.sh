#!/usr/bin/env bash
# tests/unit/hook-gate-content.sh
# Locks hook_git_gate_content (hooks/shared/_input.sh) — the diff-content
# builder the secret + customer-data block gates scan. Regression for two
# v5.2 battletest follow-ups:
#   1. raw-diff metadata false-positives: `new file mode 100644` and
#      `index <hash>..<hash>` both match the loose phone regex, so every
#      new-file commit was blocked once the K2 matcher fix made the hook
#      actually fire. The gate must scan ADDED lines only.
#   2. `git -C <path> commit` fired the matcher but scanned cwd's repo —
#      the gate must follow every -C target in the command.
# tag: v5.2 hook gate content
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/hook-gate-content.sh"
echo "================================="

# shellcheck disable=SC1091
source "$REPO_ROOT/hooks/shared/_input.sh"
# shellcheck disable=SC1091
source "$REPO_ROOT/hooks/shared/_patterns.sh"

command -v hook_git_gate_content >/dev/null 2>&1 || { fail "hook_git_gate_content MISSING"; exit 1; }

mkrepo() { # <dir>
  git -C "$1" init -q
  git -C "$1" config user.email t@t.local
  git -C "$1" config user.name t
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
A="$TMP/repo-a"; B="$TMP/repo-b"
mkdir -p "$A" "$B"; mkrepo "$A"; mkrepo "$B"

# ── 1. new-file commit with clean content must NOT trip the phone pattern ──
# (old behavior: `new file mode 100644` + `index 0000000..` matched phone)
echo "just a clean note, no PII" > "$A/note.md"
git -C "$A" add note.md
CONTENT="$(cd "$A" && hook_git_gate_content 'git commit -m x')"
printf '%s' "$CONTENT" | grep -q "new file mode" && fail "metadata lines leak into gate content" || pass "metadata lines stripped from gate content"
[ -z "$(scan_customer "$CONTENT")" ] && pass "clean new-file commit → no PII hit" || fail "clean new-file commit false-positives ($(scan_customer "$CONTENT"))"

# ── 2. a real phone on an ADDED line must still be caught ──
echo "call +46 70 123 4567 now" >> "$A/note.md"
git -C "$A" add note.md
CONTENT="$(cd "$A" && hook_git_gate_content 'git commit -m x')"
case ",$(scan_customer "$CONTENT")," in *,phone,*) pass "added-line phone detected";; *) fail "added-line phone missed";; esac

# ── 3. `git -C <repo>` target is scanned even from another cwd ──
CONTENT="$(cd "$B" && hook_git_gate_content "git -C $A commit -m x")"
case ",$(scan_customer "$CONTENT")," in *,phone,*) pass "-C target repo scanned";; *) fail "-C target repo NOT scanned (cwd-only)";; esac

# ── 4. a phone on a REMOVED line must NOT block (the fix-it commit) ──
git -C "$A" commit -qm seed
sed -i.bak 's/call .* now/call REDACTED now/' "$A/note.md" && rm -f "$A/note.md.bak"
git -C "$A" add note.md
CONTENT="$(cd "$A" && hook_git_gate_content 'git commit -m x')"
[ -z "$(scan_customer "$CONTENT")" ] && pass "removing a phone does not block" || fail "removal commit blocked ($(scan_customer "$CONTENT"))"

# ── 5-8: newline-class bypasses + push path (launch register B3) ──
# These run the REAL block hook end-to-end. Env seams keep every write inside
# the sandbox; </dev/null gives the stdin reader instant EOF so argv1 is used.
# The token is built by concatenation so THIS source line never matches tier1.
export LINTEL_HOME="$TMP/lintel-home" LINTEL_AUDIT_DIR="$TMP/audit"
mkdir -p "$LINTEL_AUDIT_DIR"
SEC="$TMP/repo-sec"; mkdir -p "$SEC"; mkrepo "$SEC"
AKIA_T="AKIA""ABCDEFGHIJKLMNOP"
printf 'aws_key=%s\n' "$AKIA_T" > "$SEC/cfg.txt"
git -C "$SEC" add cfg.txt
HOOK="$REPO_ROOT/hooks/shared/secret-scan-block/run.sh"

# 5. a line-continuation between `git` and the subcommand must still BLOCK
#    (line-oriented grep saw two half-lines and exited 0 with no scan, no audit)
rc=0; (cd "$SEC" && bash "$HOOK" "git -C $SEC \\
commit -am x" </dev/null) >/dev/null 2>&1 || rc=$?
[ "$rc" = "2" ] && pass "line-continuation phrasing still BLOCKED" || fail "line-continuation bypassed the gate (rc=$rc)"

# 6. a newline-injected override token inside -m must NOT suppress the block
#    (the '^' anchor matched the forged second line — L-012 class)
rc=0; (cd "$SEC" && bash "$HOOK" "git commit -am \"innocent
LINTEL_OVERRIDE_SECRET=1 x\"" </dev/null) >/dev/null 2>&1 || rc=$?
[ "$rc" = "2" ] && pass "newline-forged override still BLOCKED" || fail "newline override forgery suppresses the block (rc=$rc)"

# 7. the legit leading-prefix override still works, and still audits
rc=0; (cd "$SEC" && bash "$HOOK" "LINTEL_OVERRIDE_SECRET=1 git commit -am x" </dev/null) >/dev/null 2>&1 || rc=$?
[ "$rc" = "0" ] && pass "legit leading override still allowed" || fail "legit override broken (rc=$rc)"
grep -q '"override":"true"' "$LINTEL_AUDIT_DIR/hooks.jsonl" 2>/dev/null && pass "legit override audit-logged" || fail "override left no audit record"

# 8. pushing an already-COMMITTED secret must BLOCK (outgoing-range scan;
#    staged/unstaged are empty here — the old gate was a push no-op)
git -C "$SEC" commit -qm seed
rc=0; (cd "$SEC" && bash "$HOOK" "git push" </dev/null) >/dev/null 2>&1 || rc=$?
[ "$rc" = "2" ] && pass "push of a committed secret BLOCKED" || fail "push path fail-open (rc=$rc)"

echo ""
if [ "$FAILED" = 1 ]; then echo "RESULT: FAIL"; exit 1; fi
echo "RESULT: PASS"
