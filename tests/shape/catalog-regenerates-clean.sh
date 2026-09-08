#!/usr/bin/env bash
# tests/shape/catalog-regenerates-clean.sh
# Asserts: CATALOG.md regeneration is idempotent (re-run produces no diff)
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/catalog-regenerates-clean.sh"
echo "=========================================="

CATALOG="$REPO_ROOT/skills/CATALOG.md"

if [ -f "$CATALOG" ]; then
  pass "skills/CATALOG.md exists"
  if head -1 "$CATALOG" | grep -qE "^#.*[Cc]atalog"; then
    pass "CATALOG.md header is well-formed"
  else
    fail "CATALOG.md header malformed"
  fi
  if grep -qE "^\| .*/li:" "$CATALOG"; then
    pass "CATALOG.md contains skill invocation patterns"
  else
    fail "CATALOG.md has no skill rows"
  fi
else
  fail "skills/CATALOG.md missing"
fi

if command -v python3 >/dev/null 2>&1; then
  python3 "$REPO_ROOT/bin/li-catalog.py" --check && pass "catalog matches deterministic generator" || fail "catalog has drifted"
else
  echo '  SKIP: python3 required for catalog drift verification'
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All catalog-regenerates-clean assertions PASSED"; exit 0
else echo "Some catalog-regenerates-clean assertions FAILED"; exit 1; fi
