#!/usr/bin/env bash
# tests/shape/cycle-footer-present.sh
# Consistency floor: every cycle phase-skill must close with the shared cycle-position
# footer (ADR-0003), so an operator entering the cycle at ANY phase — standalone or via
# /li:cycle — always gets "you are here / next / say go". Asserts each of the 9 phase
# skills references render_cycle_footer, and that the helper + ADR they cite exist.
# tag: cycle footer drift-guard
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/shape/cycle-footer-present.sh"
echo "==================================="

# The helper the skills source must exist.
[ -f lib/cycle-footer.sh ] && pass "lib/cycle-footer.sh exists" || fail "lib/cycle-footer.sh missing"
[ -f lib/cycle-modes.sh ] && pass "lib/cycle-modes.sh exists" || fail "lib/cycle-modes.sh missing"
[ -f .claude/decisions/0003-cycle-position-footer.md ] && pass "ADR-0003 exists" || fail "ADR-0003 missing"

# Every phase skill (the 9 cycle steps) must render the footer at its close.
PHASE_SKILLS="sense scope define discover plan build review ship capture"
for s in $PHASE_SKILLS; do
  f="skills/$s/SKILL.md"
  if [ ! -f "$f" ]; then fail "$s: SKILL.md missing"; continue; fi
  if grep -q "render_cycle_footer" "$f"; then pass "$s: renders cycle footer"; else fail "$s: missing render_cycle_footer"; fi
done

# The orchestrator itself references the footer (renders at its gates + completion).
grep -q "render_cycle_footer" skills/cycle/SKILL.md && pass "cycle orchestrator references footer" || fail "cycle orchestrator missing footer"

# The orchestrator must persist cycle_mode into state so the footer resolves skips without --mode.
grep -qE "cycle_mode[:=]" skills/cycle/SKILL.md && pass "orchestrator persists cycle_mode to state" || fail "orchestrator missing cycle_mode write"

# High-traffic non-phase entry points also close with the footer (thin ambient outside a cycle).
ENTRY_SKILLS="welcome jobs resume status"
for s in $ENTRY_SKILLS; do
  f="skills/$s/SKILL.md"
  if [ ! -f "$f" ]; then fail "$s: SKILL.md missing"; continue; fi
  if grep -q "render_cycle_footer" "$f"; then pass "$s: renders cycle footer"; else fail "$s: missing render_cycle_footer"; fi
done

echo ""
[ "$FAILED" -eq 0 ] && { echo "cycle-footer-present: ALL PASS"; exit 0; } || { echo "cycle-footer-present: FAILURES"; exit 1; }
