#!/usr/bin/env bash
# tests/unit/memory-v2.sh
# Behavior contract for ADR-0006: the memory promises are MECHANICAL.
# Pins lib/memory.sh (surfacing, supersede-skip, count, budgets) and
# bin/_context.sh (checkpoint path/list/latest) against a sandbox repo.

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/memory-v2.sh"
echo "======================="

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Sandbox migrated repo
SB="$TMP/repo"
mkdir -p "$SB/.claude/memory" "$SB/.claude/runtime/state"
( cd "$SB" && git init -q . && git -c user.email=t@t -c user.name=t commit --allow-empty -m init -q )
printf 'layout_version: 5\n' > "$SB/.claude/lintel-layout.yaml"
cat > "$SB/.claude/memory/lessons.md" <<'EOF'
# Lessons

## L-001 — Always grep before designing widgets
**Rule:** grep the widget codebase first.

## L-002 — Old widget rule that was wrong
superseded_by: L-003 (2026-06-01)
**Rule:** widgets never need tests.

## L-003 — Widgets need integration tests
**Rule:** every widget gets one integration test.

## L-004 — Unrelated database lesson
**Rule:** index your foreign keys.
EOF
cat > "$SB/.claude/memory/MEMORY.md" <<'EOF'
# Memory index
- lessons
EOF

echo ""
echo "[1] lessons_surface ranks by keyword and skips superseded"
out=$( cd "$SB" && LINTEL_REPO_ROOT="$SB" bash -c "source '$REPO_ROOT/lib/memory.sh'; lessons_surface widget tests" )
echo "$out" | grep -q 'L-003' && pass "L-003 surfaced for 'widget tests'" || fail "L-003 not surfaced: $out"
echo "$out" | grep -q 'L-002' && fail "superseded L-002 surfaced" || pass "superseded L-002 skipped"
echo "$out" | grep -q 'L-004' && fail "irrelevant L-004 surfaced" || pass "irrelevant L-004 not surfaced"

echo ""
echo "[2] lessons_count excludes superseded"
n=$( cd "$SB" && LINTEL_REPO_ROOT="$SB" bash -c "source '$REPO_ROOT/lib/memory.sh'; lessons_count" )
[ "$n" = "3" ] && pass "count=3 (4 entries, 1 superseded)" || fail "count=$n, expected 3"

echo ""
echo "[3] memory_budget_check warns over budget, silent within"
out=$( cd "$SB" && LINTEL_REPO_ROOT="$SB" bash -c "source '$REPO_ROOT/lib/memory.sh'; memory_budget_check" )
[ -z "$out" ] && pass "silent within budget" || fail "unexpected warn: $out"
out=$( cd "$SB" && LINTEL_REPO_ROOT="$SB" bash -c "source '$REPO_ROOT/lib/memory.sh'; LINTEL_MEMORY_INDEX_MAX_LINES=1 LINTEL_LESSONS_SOFT_MAX=2 memory_budget_check" )
echo "$out" | grep -q 'MEMORY.md' && pass "warns on index over budget" || fail "no index warn: $out"
echo "$out" | grep -q 'active lessons' && pass "warns on lessons over budget" || fail "no lessons warn: $out"

echo ""
echo "[4] _context.sh: save path under .claude/runtime/sessions/<branch>/, list+latest find it"
( cd "$SB" && git checkout -q -b feat/test-branch 2>/dev/null || true )
p=$( cd "$SB" && LINTEL_REPO_ROOT="$SB" LINTEL_HOME="$TMP/.lintel" bash -c "source '$REPO_ROOT/bin/_context.sh'; context_save_path mylabel" )
case "$p" in
  "$SB/.claude/runtime/sessions/feat/test-branch/"*-mylabel-context-save.md) pass "save path canonical: ${p#"$SB"/}" ;;
  *) fail "unexpected save path: $p" ;;
esac
echo "checkpoint content" > "$p"
latest=$( cd "$SB" && LINTEL_REPO_ROOT="$SB" LINTEL_HOME="$TMP/.lintel" bash -c "source '$REPO_ROOT/bin/_context.sh'; context_latest" )
[ "$latest" = "$p" ] && pass "context_latest finds the checkpoint" || fail "latest=$latest expected $p"

echo ""
echo "[5] legacy checkpoint dir included read-only (grace window)"
mkdir -p "$TMP/.lintel/sessions/feat/test-branch"
printf '**Repository:** %s\nold\n' "$(cd "$SB" && pwd -P)" > "$TMP/.lintel/sessions/feat/test-branch/20200101-000000-old-context-save.md"
n=$( cd "$SB" && LINTEL_REPO_ROOT="$SB" LINTEL_HOME="$TMP/.lintel" bash -c "source '$REPO_ROOT/bin/_context.sh'; context_list | wc -l" | tr -d ' ' )
[ "$n" = "2" ] && pass "list merges new + legacy (2 checkpoints)" || fail "list count=$n expected 2"

echo ""
echo "[6] job_ready: ACTIVE no-steps job is ready; blocked-step job is not"
export LINTEL_JOBS_DIR="$TMP/jobs" LINTEL_JOBS_REGISTRY="$TMP/.lintel/jobs/_active.md" LINTEL_AUDIT_DIR="$TMP/audit-sb" LINTEL_REPO_ROOT="$SB"
source "$REPO_ROOT/bin/_jobs.sh"
id=$(job_create testwf internal-tool)
[ "$(job_ready "$id")" = "yes" ] && pass "no-steps ACTIVE job ready" || fail "no-steps job not ready"
id2=$(job_create testwf2 internal-tool 'A|status=PENDING|blocked_until=B.status == DONE' 'B|status=PENDING')
# resume point = B (A blocked) → ready
[ "$(job_ready "$id2")" = "yes" ] && pass "job with startable step ready" || fail "startable-step job not ready"
job_archive "$id" DONE >/dev/null 2>&1
[ "$(job_ready "$id")" = "no" ] && pass "archived job not ready" || fail "archived job still ready"

echo ""
echo "[7] memory-budget-warn hook: warn-only, rate-limited, pre-v5 silent"
out=$( cd "$SB" && LINTEL_MEMORY_INDEX_MAX_LINES=1 bash "$REPO_ROOT/hooks/shared/memory-budget-warn/run.sh" )
echo "$out" | grep -q 'WARN' && pass "hook warns over budget" || fail "hook silent over budget: $out"
out2=$( cd "$SB" && LINTEL_MEMORY_INDEX_MAX_LINES=1 bash "$REPO_ROOT/hooks/shared/memory-budget-warn/run.sh" )
[ -z "$out2" ] && pass "rate-limited on second fire" || fail "not rate-limited: $out2"
SB2="$TMP/legacy-repo"; mkdir -p "$SB2"; ( cd "$SB2" && git init -q . )
out3=$( cd "$SB2" && LINTEL_MEMORY_INDEX_MAX_LINES=1 bash "$REPO_ROOT/hooks/shared/memory-budget-warn/run.sh" )
[ -z "$out3" ] && pass "pre-v5 repo: silent" || fail "pre-v5 repo warned: $out3"

echo ""
if [ "$FAILED" -eq 0 ]; then echo "ALL PASS"; else echo "FAILURES present"; exit 1; fi
