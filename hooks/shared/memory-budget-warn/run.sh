#!/usr/bin/env bash
# memory-budget-warn — Lintel warn-only hook (ADR-0006)
# Block budgets for the memory home: MEMORY.md over its 200-line auto-load cap
# or lessons.md over its soft lesson budget → one WARN, rate-limited to once
# per hour. Append-only memory bloat is the documented failure mode of
# file-based agent memory; the budget forces consolidation (supersede, don't
# delete). Fail-open: never blocks, never errors.

set -uo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[ -n "$REPO_ROOT" ] || exit 0
[ -f "$REPO_ROOT/.claude/lintel-layout.yaml" ] || exit 0   # pre-v5 repos: no budget contract yet

# Rate limit: once per hour per repo
STAMP="$REPO_ROOT/.claude/runtime/state/.last-memory-budget-warn"
if [ -f "$STAMP" ]; then
  now=$(date +%s)
  last=$(date -r "$STAMP" +%s 2>/dev/null || stat -c %Y "$STAMP" 2>/dev/null || echo 0)
  [ $((now - last)) -lt 3600 ] && exit 0
fi

# Helper lib (repo checkout → installed tree)
MEM_LIB="$REPO_ROOT/lib/memory.sh"
[ -f "$MEM_LIB" ] || MEM_LIB="$LINTEL_HOME/scaffolding/lib/memory.sh"
[ -f "$MEM_LIB" ] || MEM_LIB="$(dirname "${BASH_SOURCE[0]}")/../../../lib/memory.sh"
[ -f "$MEM_LIB" ] || exit 0
# shellcheck disable=SC1090
source "$MEM_LIB" 2>/dev/null || exit 0

warns="$(memory_budget_check 2>/dev/null || true)"
if [ -n "$warns" ]; then
  mkdir -p "$(dirname "$STAMP")" 2>/dev/null || true
  : > "$STAMP" 2>/dev/null || true
  command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh" 2>/dev/null || true
  command -v audit_log >/dev/null 2>&1 && audit_log "hooks" "memory_budget_warn" "hook=memory-budget-warn" "tier=warn" || true
  printf '%s\n' "$warns"
fi

exit 0
