#!/usr/bin/env bash
# tests/shape/hooks-registration-safe.sh
# Behavior: hooks/hooks.json registers every hook in a form that ACTUALLY FIRES on a clean
# cross-platform plugin install. Guards the #1 silent-breakage class that bit obra/superpowers
# for ~7 versions (issues #383, #292): single-quoted ${CLAUDE_PLUGIN_ROOT} (cmd.exe treats the
# quote as a literal char; bash never expands the var → hook installed but inert, no error), a
# .cmd/.bat wrapper, or a `-l`/--login flag (spawns a stray Windows terminal). For Lintel a
# silently-dead hook means the SAFETY layer (secret-scan-block, customer-data-block) becomes a
# no-op — worse than a visible failure. Every registered command must: use the double-quoted
# ${CLAUDE_PLUGIN_ROOT} form, invoke a real executable .sh, carry no login-shell flag — and that
# .sh must exist under hooks/shared/ and be executable (100755).
# tag: hooks registration safety cross-platform
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/shape/hooks-registration-safe.sh"
echo "======================================"

HJ="hooks/hooks.json"
[ -f "$HJ" ] && pass "hooks.json present" || { fail "hooks.json missing"; echo "hooks-registration-safe: FAILURES"; exit 1; }

# 1. Valid JSON
if command -v node >/dev/null 2>&1; then
  node -e 'JSON.parse(require("fs").readFileSync(process.argv[1],"utf8"))' "$HJ" 2>/dev/null \
    && pass "hooks.json is valid JSON" || fail "hooks.json is NOT valid JSON"
  CMDS="$(node -e '
    const h=JSON.parse(require("fs").readFileSync(process.argv[1],"utf8"));
    const out=[];
    for(const ev of Object.values(h.hooks||{}))
      for(const grp of ev||[])
        for(const hk of (grp.hooks||[]))
          if(hk.command) out.push(hk.command);
    process.stdout.write(out.join("\n"));
  ' "$HJ" 2>/dev/null)"
else
  # no node — fall back to grepping command lines (still catches the regressions)
  pass "node absent — using grep fallback for command extraction"
  CMDS="$(grep -oE '"command"[[:space:]]*:[[:space:]]*"[^"]*"' "$HJ" | sed -E 's/.*:[[:space:]]*"//; s/"$//')"
fi

[ -n "$CMDS" ] && pass "found registered hook commands" || fail "no hook commands extracted from hooks.json"

# 2. Per-command safety + 3. referenced script exists & is executable
while IFS= read -r cmd; do
  [ -z "$cmd" ] && continue
  short="$(printf '%s' "$cmd" | sed -E 's#.*hooks/shared/##; s#/run.sh.*##')"

  # double-quoted ${CLAUDE_PLUGIN_ROOT} — NOT single-quoted/unquoted (the superpowers #383 bug:
  # single-quoted won't expand in bash and is a literal char in cmd.exe → installed but inert).
  case "$cmd" in
    *'"${CLAUDE_PLUGIN_ROOT}'*)
      pass "[$short] uses double-quoted \${CLAUDE_PLUGIN_ROOT}" ;;
    *'${CLAUDE_PLUGIN_ROOT}'*)
      fail "[$short] \${CLAUDE_PLUGIN_ROOT} is single-quoted or unquoted — silent no-op on a plugin install; use the double-quoted form" ;;
    *)
      fail "[$short] command does not reference \${CLAUDE_PLUGIN_ROOT} — path may not resolve on a plugin install" ;;
  esac

  # no .cmd/.bat wrapper (the superpowers #292 root cause) — invoke .sh directly
  case "$cmd" in
    *.cmd*|*.bat*) fail "[$short] routes through a .cmd/.bat wrapper — invoke the .sh directly (cross-platform)" ;;
    *) : ;;
  esac

  # no login-shell flag (spawns a stray terminal window on Windows — superpowers #292)
  case "$cmd" in
    *" -l "*|*" --login "*) fail "[$short] uses a login-shell flag (-l/--login) — opens a stray window on Windows" ;;
    *) : ;;
  esac

  # the referenced run.sh must exist and be executable
  rel="$(printf '%s' "$cmd" | grep -oE 'hooks/shared/[A-Za-z0-9_-]+/run\.sh' | head -1)"
  if [ -n "$rel" ]; then
    if [ -f "$rel" ]; then
      pass "[$short] run.sh exists"
      if [ -x "$rel" ] || git ls-files -s "$rel" 2>/dev/null | grep -q '^100755'; then
        pass "[$short] run.sh is executable (100755)"
      else
        fail "[$short] run.sh is NOT executable — needs mode 100755 (git update-index --chmod=+x)"
      fi
    else
      fail "[$short] registered run.sh does not exist: $rel"
    fi
  fi
done <<EOF
$CMDS
EOF

echo ""
[ "$FAILED" -eq 0 ] && { echo "hooks-registration-safe: ALL PASS"; exit 0; } || { echo "hooks-registration-safe: FAILURES"; exit 1; }
