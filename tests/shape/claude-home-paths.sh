#!/usr/bin/env bash
# tests/shape/claude-home-paths.sh
# v5 layout contract (ADR-0005): lib/paths.sh is the single source of truth for
# where Lintel reads/writes. Bash tooling (bin/, lib/, hooks/shared/*/run.sh)
# must not hardcode legacy knowledge paths outside the allowlisted fallback
# sites, and the migration tool + layout marker machinery must exist.
# tag: claude-home layout drift-guard
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/shape/claude-home-paths.sh"
echo "================================"

# 1 — the contract pieces exist
[ -f lib/paths.sh ] && pass "lib/paths.sh exists" || fail "lib/paths.sh missing"
[ -x bin/li-migrate-claude-home ] && pass "bin/li-migrate-claude-home executable" || fail "bin/li-migrate-claude-home missing/not executable"

# 2 — paths.sh self-test runs clean and resolves every function
if bash lib/paths.sh >/dev/null 2>&1; then
  pass "paths.sh self-test runs"
else
  fail "paths.sh self-test errors"
fi
for fn in lintel_lessons_file lintel_working_state_file lintel_personas_file \
          lintel_decisions_dir lintel_todo_file lintel_state_dir \
          lintel_sessions_dir lintel_repo_jobs_dir lintel_layout_migrated; do
  if grep -q "^${fn}()" lib/paths.sh || grep -q "^${fn}() *{" lib/paths.sh; then
    pass "paths.sh defines $fn"
  else
    fail "paths.sh missing $fn"
  fi
done

# 3 — no NEW hardcoded legacy knowledge paths in bash tooling.
# Allowlist: paths.sh (defines the fallbacks), the migration tool (moves them),
# and lines annotated `legacy-fallback-ok` or clearly fallback-guarded
# (the session-digest hook resolves new-then-legacy explicitly).
violations=$(grep -rnE 'tasks/(lessons|memory|personas|todo)\.md|docs/adr/' \
    bin lib hooks/shared --include='*.sh' 2>/dev/null \
  | grep -v 'lib/paths\.sh' \
  | grep -v 'li-migrate-claude-home' \
  | grep -v 'legacy-fallback-ok' \
  | grep -v '_first_existing' \
  | grep -v '_lintel_pick' \
  | grep -vE '^\s*#' \
  | grep -vE ':\s*#' || true)
if [ -z "$violations" ]; then
  pass "no unguarded legacy knowledge paths in bash tooling"
else
  fail "unguarded legacy paths found:"
  echo "$violations" | sed 's/^/    /'
fi

# 4 — scope routing present in the shared writers
grep -q '_audit_out_dir' bin/_audit.sh && pass "_audit.sh routes by scope" || fail "_audit.sh missing scope routing"
grep -q '_registry_sync' bin/_jobs.sh && pass "_jobs.sh syncs cross-repo registry" || fail "_jobs.sh missing registry sync"
grep -q 'lintel-layout.yaml' bin/_jobs.sh && pass "_jobs.sh layout-aware" || fail "_jobs.sh not layout-aware"

# 5 — the dogfooded repo itself carries the v5 marker (L-006: factory runs on itself)
if [ -f .claude/lintel-layout.yaml ] && grep -qE '^layout_version: *5' .claude/lintel-layout.yaml; then
  pass "this repo is migrated (layout_version: 5)"
else
  fail "this repo lacks the v5 layout marker — run bin/li-migrate-claude-home"
fi

# 6 — runtime is gitignored, knowledge is not
if grep -qE '^\.claude/runtime/' .gitignore 2>/dev/null; then
  pass ".claude/runtime/ gitignored"
else
  fail ".claude/runtime/ not in .gitignore"
fi
if git check-ignore -q .claude/memory/lessons.md 2>/dev/null; then
  fail ".claude/memory/ is gitignored (knowledge must be committed)"
else
  pass ".claude/memory/ is committable"
fi

echo ""
[ "$FAILED" -eq 0 ] && { echo "claude-home-paths: ALL PASS"; exit 0; } || { echo "claude-home-paths: FAILURES"; exit 1; }
