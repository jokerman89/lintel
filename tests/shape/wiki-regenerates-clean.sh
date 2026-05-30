#!/usr/bin/env bash
# tests/shape/wiki-regenerates-clean.sh
# Asserts (v4.0 Phase 3): bin/li-wiki-gen + lib/wiki-gen.sh exist + outputs
# present + --check flag implemented.
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/wiki-regenerates-clean.sh"
echo "======================================="

# Generator + helpers
if [ -x "$REPO_ROOT/bin/li-wiki-gen" ]; then
  pass "bin/li-wiki-gen exists + executable"
else
  fail "bin/li-wiki-gen MISSING or not executable"
fi

if [ -f "$REPO_ROOT/lib/wiki-gen.sh" ]; then
  pass "lib/wiki-gen.sh present"
else
  fail "lib/wiki-gen.sh MISSING"
fi

# --check flag implemented
if grep -qE '\-\-check' "$REPO_ROOT/bin/li-wiki-gen" 2>/dev/null; then
  pass "bin/li-wiki-gen documents --check flag (CI integration)"
else
  fail "bin/li-wiki-gen MISSING --check flag"
fi

# Outputs (regenerated at any time)
for out in docs/wiki/README.md docs/wiki/skills.md docs/wiki/agents.md docs/wiki/packs.md docs/wiki/schemas.md docs/showcase/lintel-the-harness.html; do
  if [ -f "$REPO_ROOT/$out" ]; then
    pass "output $out present"
  else
    fail "output $out MISSING (run bin/li-wiki-gen)"
  fi
done

# Wiki outputs declare "do not hand-edit"
for f in docs/wiki/README.md docs/wiki/skills.md docs/wiki/packs.md; do
  if [ -f "$REPO_ROOT/$f" ] && grep -qi "do not hand-edit\|hand edits will be overwritten\|generated" "$REPO_ROOT/$f" 2>/dev/null; then
    pass "$f declares hand-edit warning"
  else
    fail "$f MISSING hand-edit warning"
  fi
done

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All wiki-regenerates-clean assertions PASSED"; exit 0
else echo "Some wiki-regenerates-clean assertions FAILED"; exit 1; fi
