#!/usr/bin/env bash
# tests/unit/design-tokens-emit.sh
# Behavior: emit_tokens.py reads a design profile and emits a three-layer
# design-tokens.css (primitive → semantic → component) — ADR-0017. Verifies the
# canonical tokens flow through to CSS and the layering is present. Skips without python3.
# tag: design-dna tokens three-layer behavior
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/design-tokens-emit.sh"
echo "================================"

if ! command -v python3 >/dev/null 2>&1; then
  echo "  SKIP: python3 not available"
  echo ""
  echo "design-tokens-emit: ALL PASS (skipped)"
  exit 0
fi

E="skills/design-dna/scripts/emit_tokens.py"
P="skills/design-dna/profiles/anthropic-default.yaml"

out=$(python3 "$E" --profile "$P" 2>&1); rc=$?
[ $rc -eq 0 ] && pass "emit rc=0" || fail "emit rc=$rc"

# All three layers present
echo "$out" | grep -q "Layer 1: primitive" && pass "primitive layer present" || fail "primitive layer missing"
echo "$out" | grep -q "Layer 2: semantic" && pass "semantic layer present" || fail "semantic layer missing"
echo "$out" | grep -q "Layer 3: component" && pass "component layer present" || fail "component layer missing"

# Canonical token flows to primitive layer (the parser must survive the "#hex in quotes" trap)
echo "$out" | grep -q -- "--dna-ink: #141413" && pass "canonical ink token emitted" || fail "ink token missing — parser ate the hex?"
echo "$out" | grep -q -- "--dna-accent-primary: #d97757" && pass "canonical accent token emitted" || fail "accent token missing"

# Semantic aliases reference primitives (theme-switch contract), not raw hex
echo "$out" | grep -q -- "--color-primary: var(--dna-accent-primary)" && pass "semantic aliases primitive (not raw)" || fail "semantic layer not aliasing primitive"

# Component layer references semantic, not primitive directly
echo "$out" | grep -q -- "--button-bg: var(--color-primary)" && pass "component references semantic" || fail "component layer not referencing semantic"

# Radius + fonts flow FROM the profile (inline-map parsing), not hardcoded emitter constants
echo "$out" | grep -q -- "--dna-radius-pill: 999px" && pass "radius incl pill flows from profile (inline map parsed)" || fail "radius not read from profile — inline-map parse regressed"
echo "$out" | grep -q -- '--dna-font-display: "Poppins"' && pass "font family flows from profile" || fail "type tokens not read from profile"
echo "$out" | grep -q -- "--font-body: var(--dna-font-body)" && pass "semantic font aliases primitive" || fail "font semantic layer missing"

# Negative: missing profile fails closed (no traceback, exit 1)
python3 "$E" --profile /tmp/no-such-profile.yaml >/dev/null 2>&1; rc=$?
[ $rc -eq 1 ] && pass "missing profile fails closed (exit 1)" || fail "missing profile exit $rc"

echo ""
[ "$FAILED" -eq 0 ] && { echo "design-tokens-emit: ALL PASS"; exit 0; } || { echo "design-tokens-emit: FAILURES"; exit 1; }
