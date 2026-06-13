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

echo ""
if [ "$FAILED" = 1 ]; then echo "RESULT: FAIL"; exit 1; fi
echo "RESULT: PASS"
