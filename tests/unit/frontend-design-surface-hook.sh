#!/usr/bin/env bash
# tests/unit/frontend-design-surface-hook.sh
#
# Verifies v3.7 Fas C — frontend-design-surface hook structure + behavior.
# tag: v3.7 fas-c passive-hook

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/frontend-design-surface-hook.sh"
echo "=========================================="

HOOK_DIR="$REPO_ROOT/hooks/shared/frontend-design-surface"

# Step 1 — Hook directory + required files present
if [ -d "$HOOK_DIR" ]; then
  pass "frontend-design-surface hook directory present"

  if [ -f "$HOOK_DIR/HOOK.md" ]; then
    pass "HOOK.md present"
  else
    fail "HOOK.md missing"
  fi

  if [ -f "$HOOK_DIR/run.sh" ]; then
    pass "run.sh present"
  else
    fail "run.sh missing"
  fi
else
  fail "hooks/shared/frontend-design-surface/ directory missing"
  exit 1
fi

# Step 2 — HOOK.md frontmatter
HOOK_MD="$HOOK_DIR/HOOK.md"
for field in name tier event fires_on override audit; do
  if grep -qE "^${field}:" "$HOOK_MD"; then
    pass "HOOK.md frontmatter has: $field"
  else
    fail "HOOK.md frontmatter missing: $field"
  fi
done

# tier must be surface-only (Fas C convention; non-blocker)
if grep -qE "^tier: surface-only" "$HOOK_MD"; then
  pass "HOOK.md tier: surface-only (non-blocker per design doc)"
else
  fail "HOOK.md tier expected 'surface-only'"
fi

# Step 3 — run.sh basic validation
RUN_SH="$HOOK_DIR/run.sh"

# Has shebang
if head -1 "$RUN_SH" | grep -qE "^#!/usr/bin/env bash|^#!/bin/bash"; then
  pass "run.sh has bash shebang"
else
  fail "run.sh missing/wrong shebang"
fi

# References expected file extensions (filters)
for ext in tsx jsx svelte vue css scss; do
  if grep -q "$ext" "$RUN_SH"; then
    pass "run.sh filters on: $ext"
  else
    fail "run.sh missing filter for: $ext"
  fi
done

# Throttle marker logic
if grep -qE "marker|throttle" "$RUN_SH"; then
  pass "run.sh implements throttle/marker logic"
else
  fail "run.sh missing throttle logic"
fi

# Audit-log write (via unified audit_log helper → hooks category → hooks.jsonl)
if grep -qE 'audit_log[[:space:]]+"hooks"' "$RUN_SH"; then
  pass "run.sh writes to hooks audit via audit_log helper"
else
  fail "run.sh missing audit-log write"
fi

# Vault read
if grep -qE "design-patterns|VAULT" "$RUN_SH"; then
  pass "run.sh reads design-patterns vault"
else
  fail "run.sh missing vault read"
fi

# Operator-disable escape hatch
if grep -q "frontend-design-surface-disabled" "$RUN_SH"; then
  pass "run.sh respects --no-design-surface escape hatch"
else
  fail "run.sh missing operator-disable escape hatch"
fi

# Step 4 — Behavior smoke test (use temp HOME to avoid contaminating real state)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

export LINTEL_HOME="$TMP/.lintel"
export LINTEL_REPO_ROOT="$TMP"   # markerless sandbox: audit stays under LINTEL_HOME, not the real repo's .claude/runtime/
export LINTEL_SESSION_ID="test-session-$$"   # stable across $() subshells in tests
mkdir -p "$LINTEL_HOME/brand/design-patterns/test-pattern" "$LINTEL_HOME/sessions" "$LINTEL_HOME/audit"

# Mock a valid pattern
cat > "$LINTEL_HOME/brand/design-patterns/test-pattern/pattern.json" <<'JSON'
{"schema_version": 1, "name": "test-pattern"}
JSON
cat > "$LINTEL_HOME/brand/design-patterns/test-pattern/component-imports.json" <<'JSON'
{"fingerprint": "shadcn+aceternity", "imports": [{"name": "shadcn"}, {"name": "aceternity-ui"}]}
JSON

# Test 4a: TSX file triggers surface
mkdir -p "$TMP/project"
touch "$TMP/project/Hero.tsx"
output=$(bash "$RUN_SH" "$TMP/project/Hero.tsx" 2>&1)
if echo "$output" | grep -qE "Lintel.*design-patterns.*test-pattern"; then
  pass "behavior: .tsx file triggers surface line"
else
  fail "behavior: .tsx surface didn't fire (output: $output)"
fi

# Test 4b: non-frontend file silent exit
output=$(bash "$RUN_SH" "$TMP/project/README.md" 2>&1)
if [ -z "$output" ]; then
  pass "behavior: non-frontend file silent exit"
else
  fail "behavior: non-frontend file produced output: $output"
fi

# Test 4c: throttle — second invocation on same file silent
output=$(bash "$RUN_SH" "$TMP/project/Hero.tsx" 2>&1)
if [ -z "$output" ]; then
  pass "behavior: throttle prevents double-surface on same file"
else
  fail "behavior: throttle failed, second surface fired: $output"
fi

# Test 4d: empty vault → silent
rm -rf "$LINTEL_HOME/brand/design-patterns"/*
touch "$TMP/project/Empty.tsx"
output=$(bash "$RUN_SH" "$TMP/project/Empty.tsx" 2>&1)
if [ -z "$output" ]; then
  pass "behavior: empty vault → silent (MVP behavior)"
else
  fail "behavior: empty vault produced output: $output"
fi

# Test 4e: operator-disable escape hatch works
mkdir -p "$LINTEL_HOME/brand/design-patterns/test-pattern"
cat > "$LINTEL_HOME/brand/design-patterns/test-pattern/pattern.json" <<'JSON'
{"schema_version": 1, "name": "test-pattern"}
JSON
cat > "$LINTEL_HOME/brand/design-patterns/test-pattern/component-imports.json" <<'JSON'
{"fingerprint": "shadcn"}
JSON
touch "$LINTEL_HOME/.frontend-design-surface-disabled"
touch "$TMP/project/Disabled.tsx"
output=$(bash "$RUN_SH" "$TMP/project/Disabled.tsx" 2>&1)
if [ -z "$output" ]; then
  pass "behavior: disable-flag respected"
else
  fail "behavior: disable-flag ignored, output: $output"
fi
rm -f "$LINTEL_HOME/.frontend-design-surface-disabled"

# Step 5 — Performance budget. Documented target <200ms for a 1-3 pattern vault.
# Wall-clock of a single bash subprocess is runner-dependent (Git-for-Windows
# bash startup alone can exceed 500ms), so the hard-fail ceiling guards against a
# pathological regression (unindexed huge vault, hang) rather than runner variance.
# Exceeding the documented target is surfaced as a soft note, not a CI failure.
touch "$TMP/project/Perf.tsx"
# Reset throttle marker for this test
rm -f "$LINTEL_HOME/sessions"/*-design-surfaced 2>/dev/null
start_ms=$(date +%s%N | cut -c1-13)
bash "$RUN_SH" "$TMP/project/Perf.tsx" >/dev/null 2>&1 || true
end_ms=$(date +%s%N | cut -c1-13)
elapsed_ms=$((end_ms - start_ms))
if [ "$elapsed_ms" -lt 2000 ]; then
  if [ "$elapsed_ms" -ge 500 ]; then
    pass "performance: hook ran in ${elapsed_ms}ms (<2000ms regression ceiling; over 200ms target — likely runner overhead)"
  else
    pass "performance: hook ran in ${elapsed_ms}ms (<500ms; budget target <200ms documented)"
  fi
else
  fail "performance: hook took ${elapsed_ms}ms (>2000ms — pathological, vault-index-optimization needed)"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All frontend-design-surface-hook tests PASSED"
  exit 0
else
  echo "Some frontend-design-surface-hook tests FAILED"
  exit 1
fi
