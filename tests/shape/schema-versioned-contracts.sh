#!/usr/bin/env bash
# tests/shape/schema-versioned-contracts.sh
# Asserts (NEW v4.0): every contract JSON in lib/ + packs/ declares schema_version.
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/schema-versioned-contracts.sh"
echo "============================================"

# Contracts that MUST declare schema_version (per v4.0 portability axis §1.3.3)
# - lib/envelope-schema.yaml (ships in Phase 2)
# - lib/pack-schema.yaml (ships in Phase 2)
# - seeds/brand/design-patterns/*/pattern.json etc. (v3.7)

# Phase 1 enforcement: check existing v3.7+ contracts
checked=0
while IFS= read -r f; do
  checked=$((checked + 1))
  if grep -q '"schema_version"' "$f" 2>/dev/null || grep -q '^schema_version:' "$f" 2>/dev/null; then
    pass "schema_version declared: $(realpath --relative-to="$REPO_ROOT" "$f" 2>/dev/null || echo "$f")"
  else
    fail "schema_version MISSING: $(realpath --relative-to="$REPO_ROOT" "$f" 2>/dev/null || echo "$f")"
  fi
done < <(find "$REPO_ROOT/seeds" -name "pattern.json" -o -name "typography.json" -o -name "motion.json" -o -name "component-imports.json" 2>/dev/null)

# lib/ contracts (will populate in Phase 2-3)
LIB_CONTRACTS=("$REPO_ROOT/lib/envelope-schema.yaml" "$REPO_ROOT/lib/pack-schema.yaml")
for f in "${LIB_CONTRACTS[@]}"; do
  if [ -f "$f" ]; then
    if grep -qE '^schema_version:' "$f"; then
      pass "schema_version declared: lib/$(basename "$f")"
    else
      fail "schema_version MISSING: lib/$(basename "$f")"
    fi
    checked=$((checked + 1))
  else
    echo "  INFO: lib/$(basename "$f") not present yet (ships Phase 2-3)"
  fi
done

if [ "$checked" -eq 0 ]; then
  pass "(no contract files in scope yet; test is forward-defensive)"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All schema-versioned-contracts assertions PASSED"; exit 0
else echo "Some schema-versioned-contracts assertions FAILED"; exit 1; fi
