#!/usr/bin/env bash
# tests/unit/cycle-footer.sh
# Locks lib/cycle-footer.sh + lib/cycle-modes.sh — the cycle-position footer that
# closes every official Lintel report (ADR-0003). The render logic (tier auto-select,
# mode-aware skip glyphs, positional done-state, state-file parse) is the thing most
# likely to drift, so it gets a real test — a testable shell lib, not untestable prose.
# tag: cycle footer onboarding
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "$REPO_ROOT/lib/cycle-footer.sh"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
has(){ case "$1" in *"$2"*) return 0 ;; *) return 1 ;; esac; }
echo "tests/unit/cycle-footer.sh"
echo "=========================="

# ── mode→skip map (shared schema with the cycle presets) ──
[ "$(cycle_mode_skips research-dive)" = "SCOPE PLAN BUILD REVIEW SHIP CAPTURE" ] && pass "research-dive skip map" || fail "research-dive skip map = $(cycle_mode_skips research-dive)"
[ "$(cycle_mode_skips hotfix)" = "SCOPE DEFINE DISCOVER PLAN CAPTURE" ] && pass "hotfix skip map" || fail "hotfix skip map"
[ -z "$(cycle_mode_skips full)" ] && pass "full skips nothing" || fail "full skip map non-empty"
[ -z "$(cycle_mode_skips meta-infra)" ] && pass "meta-infra skips nothing" || fail "meta-infra skip map"
[ -z "$(cycle_mode_skips bananas)" ] && pass "unknown mode degrades to skip-nothing" || fail "unknown mode"
[ "$(cycle_phases | wc -l | tr -d ' ')" = "9" ] && pass "9 canonical phases" || fail "phase count"
cycle_phase_known plan && pass "cycle_phase_known case-insensitive" || fail "phase_known"

# ── thin ambient footer when no active cycle ──
out="$(render_cycle_footer --state /nonexistent-xyz)"
has "$out" "no active cycle" && pass "thin: ambient line when no state" || fail "thin ambient"
has "$out" "/li:cycle" && pass "thin: offers /li:cycle" || fail "thin cycle hint"
! has "$out" "You are here" && pass "thin: no heavy block" || fail "thin leaked full block"

# ── full block, our position: meta-infra @ PLAN ──
out="$(render_cycle_footer --mode meta-infra --here PLAN --next BUILD --state /nonexistent)"
has "$out" "PLAN 📍" && pass "full: here marker on PLAN" || fail "full here marker"
has "$out" "SENSE ✅" && pass "full: positional done (SENSE before PLAN = ✅)" || fail "full positional done"
has "$out" "BUILD ▢" && pass "full: pending after here (BUILD = ▢)" || fail "full pending"
has "$out" '`go` or `/li:build`' && pass "full: next-command lowercased" || fail "full next cmd"
has "$out" "mode \`meta-infra\`" && pass "full: mode surfaced" || fail "full mode"

# ── skip precedence: research-dive skips SCOPE (before here) + the tail ──
out="$(render_cycle_footer --mode research-dive --here DISCOVER --next PLAN --state /nonexistent)"
has "$out" "SCOPE ⊘" && pass "skip: SCOPE before here renders ⊘ not ✅" || fail "skip precedence"
has "$out" "PLAN ⊘" && pass "skip: tail phase PLAN renders ⊘" || fail "tail skip"
has "$out" "DEFINE ✅" && pass "skip: non-skipped before here still ✅" || fail "mixed done/skip"

# ── compact one-liner ──
out="$(render_cycle_footer --compact --mode meta-infra --here PLAN --next BUILD --state /nonexistent)"
has "$out" "next **\`BUILD\`**" && pass "compact: shows next" || fail "compact next"
[ "$(printf '%s\n' "$out" | grep -c '^>')" = "1" ] && pass "compact: single quoted line" || fail "compact multiline"

# ── ASCII fallback (no emoji) ──
out="$(render_cycle_footer --ascii --mode meta-infra --here PLAN --next BUILD --state /nonexistent)"
has "$out" "PLAN [>]" && pass "ascii: here = [>]" || fail "ascii here"
has "$out" "SENSE [x]" && pass "ascii: done = [x]" || fail "ascii done"
! has "$out" "📍" && pass "ascii: no emoji leak" || fail "ascii emoji leak"

# ── awaiting-answer mode flips the next block ──
out="$(render_cycle_footer --mode meta-infra --here DEFINE --awaiting "reply 1 or 2" --state /nonexistent)"
has "$out" "Awaiting your answer" && pass "awaiting: flips to question prompt" || fail "awaiting"
! has "$out" "Say / type" && pass "awaiting: suppresses next-command table" || fail "awaiting leaked table"

# ── state-file parse: append-log → same as explicit args ──
TMP="$(mktemp 2>/dev/null || echo /tmp/cf-state.$$)"
printf 'phase: SENSE\nstatus: DONE\n\nphase: DEFINE\nstatus: DONE\ncycle_mode: research-dive\n\nphase: DISCOVER\nstatus: DONE\nnext_recommended: PLAN\ncycle_mode: research-dive\n' > "$TMP"
out="$(render_cycle_footer --state "$TMP")"
has "$out" "DISCOVER 📍" && pass "state: last phase = here" || fail "state here"
has "$out" "Next:** \`PLAN\`" && pass "state: next_recommended parsed" || fail "state next"
has "$out" "mode \`research-dive\`" && pass "state: cycle_mode parsed" || fail "state mode"
has "$out" "SCOPE ⊘" && pass "state: mode-aware skip applied" || fail "state skip"
rm -f "$TMP"

# ── cycle_complete → thin ambient even with history ──
TMP2="$(mktemp 2>/dev/null || echo /tmp/cf-state2.$$)"
printf 'phase: CAPTURE\nstatus: DONE\ncycle_complete: true\n' > "$TMP2"
out="$(render_cycle_footer --state "$TMP2")"
has "$out" "no active cycle" && pass "complete: falls to thin ambient" || fail "complete→thin"
rm -f "$TMP2"

# ── REVIEW-hardening regressions (close the ADR "fail-open" claim) ──
# P0-A: a trailing value-flag with no value must not hang (shift-2 infinite loop).
if command -v timeout >/dev/null 2>&1; then
  hang=0
  for f in --mode --here --next --state --awaiting; do
    timeout 5 bash -c "source '$REPO_ROOT/lib/cycle-footer.sh'; render_cycle_footer --here PLAN $f >/dev/null 2>&1"
    [ "$?" = "124" ] && hang=1
  done
  [ "$hang" = "0" ] && pass "P0-A: no hang on trailing value-flag" || fail "P0-A: HANG on trailing value-flag"
else
  # no timeout(1): call directly — post-fix it returns; pre-fix this line would hang the suite
  out="$(render_cycle_footer --here PLAN --mode --state /nonexistent)"; pass "P0-A: trailing flag returns (no timeout available)"
fi

# P1-A: unknown --here degrades visibly, not to a silent all-pending footer.
out="$(render_cycle_footer --here BOGUS --mode full --state /nonexistent)"
has "$out" "position unresolved" && pass "P1-A: unknown here → visible unresolved line" || fail "P1-A unresolved"
! has "$out" "📍" && pass "P1-A: no false here-marker on bad input" || fail "P1-A false marker"

# P1-B: lowercase phase tokens in state resolve (case-normalized).
TMP3="$(mktemp 2>/dev/null || echo /tmp/cf-state3.$$)"
printf 'phase: plan\nstatus: DONE\nnext_recommended: build\ncycle_mode: meta-infra\n' > "$TMP3"
out="$(render_cycle_footer --state "$TMP3")"
has "$out" "PLAN 📍" && pass "P1-B: lowercase state phase → here marker" || fail "P1-B lowercase here"
has "$out" '/li:build' && pass "P1-B: lowercase next → valid command" || fail "P1-B lowercase next"
rm -f "$TMP3"

# Fail-open: a garbage state file must not crash or error the footer.
TMP4="$(mktemp 2>/dev/null || echo /tmp/cf-state4.$$)"
printf '\x00\x01garbage{not yaml]\n::::\nphase\n' > "$TMP4" 2>/dev/null
out="$(render_cycle_footer --state "$TMP4" 2>&1)"; rc=$?
[ "$rc" = "0" ] && pass "fail-open: garbage state returns rc=0" || fail "fail-open rc=$rc"
has "$out" '`li`' && pass "fail-open: garbage state → ambient footer" || fail "fail-open output"
rm -f "$TMP4"

# P2-E: known non-terminal here with no next derives next from canonical order.
out="$(render_cycle_footer --here PLAN --mode meta-infra --state /nonexistent)"
has "$out" "Next:** \`BUILD\`" && pass "P2-E: derives next when here mid-pipeline" || fail "P2-E derive"
! has "$out" "cycle complete" && pass "P2-E: no false 'cycle complete'" || fail "P2-E false complete"

# P2-D: multi-word --next collapses to a single valid command token.
out="$(render_cycle_footer --here PLAN --next 'BUILD NOW' --mode meta-infra --state /nonexistent)"
has "$out" '`go` or `/li:build`' && pass "P2-D: multi-word next → single command token" || fail "P2-D multiword"

echo ""
[ "$FAILED" -eq 0 ] && { echo "cycle-footer: ALL PASS"; exit 0; } || { echo "cycle-footer: FAILURES"; exit 1; }
