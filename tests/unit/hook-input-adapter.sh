#!/usr/bin/env bash
# tests/unit/hook-input-adapter.sh
# Regression test (T9) for hooks/shared/_input.sh — the dual-mode hook input
# adapter. Closes the v4.9 audit's blocking finding: hooks read $1 but Claude Code
# delivers tool data as JSON on stdin, so they silently no-op'd. The adapter reads
# stdin JSON when present and falls back to $1 otherwise (preserving every existing
# call site). This test locks both paths.
# tag: v4.9 hooks input-adapter
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ADAPTER="$REPO_ROOT/hooks/shared/_input.sh"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/hook-input-adapter.sh"
echo "================================="

[ -f "$ADAPTER" ] || { fail "_input.sh MISSING"; exit 1; }

# ── argv fallback: no stdin → returns $1 (existing call sites preserved) ──
r=$( source "$ADAPTER"; hook_input file_path "/repo/src/auth.ts" </dev/null )
[ "$r" = "/repo/src/auth.ts" ] && pass "no stdin → file_path falls back to \$1" || fail "file_path fallback got '$r'"

r=$( source "$ADAPTER"; hook_input command "git push origin main" </dev/null )
[ "$r" = "git push origin main" ] && pass "no stdin → command falls back to \$1" || fail "command fallback got '$r'"

# ── no-hang: empty stdin returns promptly and falls back ──
r=$( source "$ADAPTER"; hook_input payload "ARG" </dev/null )
[ "$r" = "ARG" ] && pass "empty stdin → payload falls back to \$1 (no hang)" || fail "payload fallback got '$r'"

# ── malformed JSON payload: raw passthrough so scanners still grep it ──
r=$( printf 'not json at all' | ( source "$ADAPTER"; hook_input payload "" ) )
case "$r" in *"not json"*) pass "malformed stdin → payload returns raw (greppable)";; *) fail "malformed payload got '$r'";; esac

# ── jq-gated: real Claude Code JSON extraction (enforced in CI) ──
if command -v jq >/dev/null 2>&1; then
  J='{"tool_input":{"command":"git push origin main","file_path":"src/auth.ts","content":"AKIA0000000000000000"}}'
  r=$( printf '%s' "$J" | ( source "$ADAPTER"; hook_input command "" ) )
  [ "$r" = "git push origin main" ] && pass "stdin JSON → command extracted" || fail "command got '$r'"
  r=$( printf '%s' "$J" | ( source "$ADAPTER"; hook_input file_path "" ) )
  [ "$r" = "src/auth.ts" ] && pass "stdin JSON → file_path extracted" || fail "file_path got '$r'"
  r=$( printf '%s' "$J" | ( source "$ADAPTER"; hook_input payload "" ) )
  case "$r" in *AKIA*) pass "stdin JSON → payload joins fields (scanner sees the secret)";; *) fail "payload got '$r'";; esac
  P='{"prompt":"customer Jane Doe details"}'
  r=$( printf '%s' "$P" | ( source "$ADAPTER"; hook_input prompt "" ) )
  case "$r" in *Jane*) pass "stdin JSON → prompt extracted";; *) fail "prompt got '$r'";; esac
  r=$( printf '%s' '{"tool_input":{}}' | ( source "$ADAPTER"; hook_input command "FALLBACK" ) )
  [ "$r" = "FALLBACK" ] && pass "stdin JSON with field absent → falls back to \$1" || fail "absent-field got '$r'"
else
  echo "  NOTE: jq absent — JSON-extraction asserts skipped (enforced in CI); fallback asserts above still ran"
fi

# ── jq-free extraction (v4.10 fix): _json_str_field never uses jq, so the
# command/push/PII block hooks still fire on machines lacking jq (e.g. stock
# Git-bash on Windows). Runs in BOTH CI and jq-less environments. ──
r=$( source "$ADAPTER"; _json_str_field command '{"tool_name":"Bash","tool_input":{"command":"git push origin main"}}' )
[ "$r" = "git push origin main" ] && pass "jq-free: _json_str_field extracts command (no jq needed)" || fail "jq-free command got '$r'"
r=$( source "$ADAPTER"; _json_str_field file_path '{"tool_input":{"file_path":"src/auth.ts"}}' )
[ "$r" = "src/auth.ts" ] && pass "jq-free: _json_str_field extracts file_path (no jq needed)" || fail "jq-free file_path got '$r'"

echo ""
[ "$FAILED" -eq 0 ] && { echo "hook-input-adapter: ALL PASS"; exit 0; } || { echo "hook-input-adapter: FAILURES"; exit 1; }
