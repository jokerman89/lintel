#!/usr/bin/env bash
# tests/integration/no-merge-without-review.sh
# Locks the no-merge-without-review hook's review-log lookup after the 2026-06-09 fix.
# Two silent mismatches had left the gate effectively dead: it read the legacy
# ~/.lintel/review-log/entries.jsonl (nothing writes it) instead of the audit log that
# bin/li-review-log actually writes (~/.lintel/audit/reviews.jsonl), and it matched the
# FULL HEAD sha while li-review-log stores the SHORT one. This test drives the real
# run.sh against a temp LINTEL_HOME to prove a CLEARED review for HEAD now suppresses
# the warning, and its absence still warns.
# tag: hooks no-merge-without-review review-log
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HOOK="$REPO_ROOT/hooks/shared/no-merge-without-review/run.sh"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/integration/no-merge-without-review.sh"
echo "============================================"

[ -f "$HOOK" ] || { fail "run.sh MISSING"; exit 1; }
short_head="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo "")"
[ -n "$short_head" ] || { fail "cannot resolve short HEAD"; exit 1; }

TMP="$(mktemp -d 2>/dev/null || echo "/tmp/nmwr.$$")"
mkdir -p "$TMP/audit"
trap 'rm -rf "$TMP"' EXIT

# LINTEL_REPO_ROOT pinned to the markerless sandbox so the hook's audit_log
# ("hooks" category, repo-scoped under v5) cannot write into the real repo's
# .claude/runtime/audit/ — it falls back to the sandboxed LINTEL_HOME.
run_hook(){ ( cd "$REPO_ROOT" && LINTEL_HOME="$TMP" LINTEL_REPO_ROOT="$TMP" bash "$HOOK" "$1" </dev/null 2>&1 ); }

# ── negative: no review log → merge to main WARNS ──
out="$(run_hook 'gh pr merge 7 --squash')"
case "$out" in *"WARN"*) pass "no review log → warns on merge";; *) fail "expected WARN, got: $out";; esac

# ── positive: a CLEARED review for the current short HEAD in audit/reviews.jsonl → NO warn ──
printf '{"ts":"2026-06-09T00:00:00Z","kind":"code-review","status":"CLEARED","commit":"%s","raw":"{}"}\n' "$short_head" > "$TMP/audit/reviews.jsonl"
out="$(run_hook 'gh pr merge 7 --squash')"
case "$out" in *"WARN"*) fail "CLEARED review should suppress warn, got: $out";; *) pass "CLEARED review for HEAD → no warn (correct path + short-commit match)";; esac

# ── path regression: the SAME record written to the LEGACY path must NOT clear (proves we read audit/) ──
mkdir -p "$TMP/review-log"
mv "$TMP/audit/reviews.jsonl" "$TMP/review-log/entries.jsonl"
out="$(run_hook 'gh pr merge 7 --squash')"
case "$out" in *"WARN"*) pass "record at legacy path does NOT clear → confirms audit/reviews.jsonl is the source";; *) fail "should warn when record is only at legacy path";; esac

# ── non-merge command → silent (exit 0, no warn) ──
out="$(run_hook 'git status')"
case "$out" in *"WARN"*) fail "non-merge command should not warn, got: $out";; *) pass "non-merge command → silent";; esac

echo ""
[ "$FAILED" -eq 0 ] && { echo "no-merge-without-review: ALL PASS"; exit 0; } || { echo "no-merge-without-review: FAILURES"; exit 1; }
