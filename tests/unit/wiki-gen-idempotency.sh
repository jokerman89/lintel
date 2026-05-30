#!/usr/bin/env bash
# tests/unit/wiki-gen-idempotency.sh
# Asserts: bin/li-wiki-gen produces deterministic output given identical
# sources. Two runs back-to-back produce byte-identical outputs.
# tag: v4.0 phase-3 wiki

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WIKI_GEN="$REPO_ROOT/bin/li-wiki-gen"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/wiki-gen-idempotency.sh"
echo "===================================="

if [ ! -x "$WIKI_GEN" ]; then
  fail "bin/li-wiki-gen MISSING or not executable"
  exit 1
fi

TMP1=$(mktemp -d)
TMP2=$(mktemp -d)
trap 'rm -rf "$TMP1" "$TMP2"' EXIT

# Externalize timestamp so two runs produce same output
export WGEN_TS="2026-05-29T00:00:00Z"

# ─── Run 1 ───────────────────────────────────────────────────────────────
"$WIKI_GEN" --output "$TMP1" >/dev/null 2>&1 || { fail "run 1 failed"; exit 1; }
pass "run 1 completed"

# ─── Run 2 (same sources, no changes) ────────────────────────────────────
"$WIKI_GEN" --output "$TMP2" >/dev/null 2>&1 || { fail "run 2 failed"; exit 1; }
pass "run 2 completed"

# ─── Compare outputs ─────────────────────────────────────────────────────
diffs=$(diff -r "$TMP1/docs/wiki" "$TMP2/docs/wiki" 2>&1 | head -20)
if [ -z "$diffs" ]; then
  pass "wiki outputs byte-identical across runs"
else
  fail "wiki outputs differ between runs (non-deterministic)"
  echo "$diffs" | head -20 | sed 's/^/    /'
fi

if [ -f "$TMP1/docs/showcase/lintel-the-harness.html" ] && [ -f "$TMP2/docs/showcase/lintel-the-harness.html" ]; then
  if diff -q "$TMP1/docs/showcase/lintel-the-harness.html" "$TMP2/docs/showcase/lintel-the-harness.html" >/dev/null 2>&1; then
    pass "showcase HTML byte-identical across runs"
  else
    fail "showcase HTML differs between runs (non-deterministic)"
  fi
else
  fail "showcase HTML missing from one or both runs"
fi

# ─── --check mode: should report clean against committed wiki ────────────
echo ""
echo "[check mode]"
if "$WIKI_GEN" --check 2>&1 | grep -qE "clean"; then
  pass "--check reports clean against committed wiki"
else
  echo "  WARN: --check reports differences (committed wiki may need regen)"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All wiki-gen-idempotency scenarios PASSED"; exit 0
else echo "Some wiki-gen-idempotency scenarios FAILED"; exit 1; fi
