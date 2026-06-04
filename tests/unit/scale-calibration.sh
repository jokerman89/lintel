#!/usr/bin/env bash
# tests/unit/scale-calibration.sh
# Asserts the Slice-4 calibration loop the scale-estimator gained:
#   C1 — scale_calibrated_prior reads ~/.lintel/audit/granularity.jsonl and
#        returns the MEDIAN actual_tokens for a size (corrected prior)
#   C2 — graceful fallback to size_default_prior when the log is absent/empty
#        (Slice-1 behaviour must be preserved exactly when there is no history)
#   C3 — scale_estimate still emits every required key WITH calibration present
#        (additive: the pre-existing keys stay; est_tokens is added)
# tag: slice-4 scope-scaled-planning calibration

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EST="$REPO_ROOT/lib/scale-estimator.sh"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/scale-calibration.sh"
echo "==============================="
[ -f "$EST" ] || { fail "$EST MISSING"; exit 1; }

# ─── Isolated LINTEL_HOME so we never touch the operator's real audit log ─────
TMP_HOME="$(mktemp -d 2>/dev/null || mktemp -d -t lintel-calib)"
trap 'rm -rf "$TMP_HOME"' EXIT
export LINTEL_HOME="$TMP_HOME"
unset LINTEL_AUDIT_DIR 2>/dev/null || true   # let it derive from LINTEL_HOME
AUDIT_DIR="$LINTEL_HOME/audit"
mkdir -p "$AUDIT_DIR"
GRAN="$AUDIT_DIR/granularity.jsonl"

# shellcheck disable=SC1090
source "$EST"

# ─── C2 first: absent log → mechanical default (the graceful fallback) ────────
echo ""
echo "[C2] graceful fallback when no history exists"
[ -e "$GRAN" ] && rm -f "$GRAN"
for sz in XS S M L XL; do
  got=$(scale_calibrated_prior "$sz")
  want=$(size_default_prior "$sz")
  [ "$got" = "$want" ] && [ -n "$got" ] \
    && pass "no-history prior($sz)=$got equals mechanical default" \
    || fail "no-history prior($sz)=$got, want default $want"
done

# ─── C1: history present → median actual_tokens for the matching size ─────────
echo ""
echo "[C1] calibrated prior = median actual_tokens for the size"
# Fixture: three XL cycles (median of 100000,110000,150000 = 110000), two M
# cycles (median of 20000,40000 = 30000), one S cycle (single value 9000).
# Records mirror CAPTURE's `audit_log granularity actual_vs_estimated ...` shape.
cat > "$GRAN" <<'JSONL'
{"ts":"2026-01-01T00:00:00Z","kind":"actual_vs_estimated","operator":"t","cycle_id":"c1","size":"XL","est_tokens":"120000","actual_tokens":"150000","task_count":"40","depth_schema":"tree"}
{"ts":"2026-01-02T00:00:00Z","kind":"actual_vs_estimated","operator":"t","cycle_id":"c2","size":"XL","est_tokens":"120000","actual_tokens":"100000","task_count":"33","depth_schema":"tree"}
{"ts":"2026-01-03T00:00:00Z","kind":"actual_vs_estimated","operator":"t","cycle_id":"c3","size":"XL","est_tokens":"120000","actual_tokens":"110000","task_count":"35","depth_schema":"tree"}
{"ts":"2026-01-04T00:00:00Z","kind":"actual_vs_estimated","operator":"t","cycle_id":"c4","size":"M","est_tokens":"30000","actual_tokens":"20000","task_count":"8","depth_schema":"phased"}
{"ts":"2026-01-05T00:00:00Z","kind":"actual_vs_estimated","operator":"t","cycle_id":"c5","size":"M","est_tokens":"30000","actual_tokens":"40000","task_count":"12","depth_schema":"phased"}
{"ts":"2026-01-06T00:00:00Z","kind":"actual_vs_estimated","operator":"t","cycle_id":"c6","size":"S","est_tokens":"12000","actual_tokens":"9000","task_count":"3","depth_schema":"flat"}
JSONL

got=$(scale_calibrated_prior "XL")
[ "$got" = "110000" ] && pass "XL median actual = $got (corrected from default 120000)" \
                      || fail "XL prior = $got, want median 110000"

got=$(scale_calibrated_prior "M")
[ "$got" = "30000" ] && pass "M median actual = $got (even count → midpoint)" \
                     || fail "M prior = $got, want median 30000"

got=$(scale_calibrated_prior "S")
[ "$got" = "9000" ] && pass "S single actual = $got (corrected from default 12000)" \
                    || fail "S prior = $got, want 9000"

# A size with NO matching records in a present log must still fall back.
got=$(scale_calibrated_prior "L")
want=$(size_default_prior "L")
[ "$got" = "$want" ] && pass "L (no records in log) falls back to default $got" \
                     || fail "L prior = $got, want default $want"

# The correction must actually differ from the hardcoded guess (proves it read
# the history rather than silently defaulting).
def_xl=$(size_default_prior "XL")
cal_xl=$(scale_calibrated_prior "XL")
[ "$cal_xl" != "$def_xl" ] && pass "calibrated XL ($cal_xl) ≠ mechanical default ($def_xl)" \
                           || fail "calibration had no effect: both $cal_xl"

# ─── C3: scale_estimate still emits every required key (with calibration) ─────
echo ""
echo "[C3] scale_estimate stable + est_tokens informed by calibration"
blk=$(scale_estimate "stand up a full landing zone with CI/CD on azure" medium)
for key in "size:" "confidence:" "ambiguous:" "escalate:" "depth_schema:" "est_tokens:" "signals:"; do
  printf '%s' "$blk" | grep -q "$key" && pass "scope block has $key" || fail "scope block missing $key"
done
# est_tokens for that XL prompt must equal the calibrated XL prior (110000),
# proving scale_estimate routes through scale_calibrated_prior.
emitted=$(printf '%s' "$blk" | grep 'est_tokens:' | tr -dc '0-9')
[ "$emitted" = "110000" ] && pass "scale_estimate est_tokens=$emitted (calibrated XL prior)" \
                          || fail "scale_estimate est_tokens=$emitted, want calibrated 110000"

# And with the log removed, scale_estimate falls back cleanly to the default.
rm -f "$GRAN"
blk2=$(scale_estimate "stand up a full landing zone with CI/CD on azure" medium)
emitted2=$(printf '%s' "$blk2" | grep 'est_tokens:' | tr -dc '0-9')
def2=$(size_default_prior "XL")
[ "$emitted2" = "$def2" ] && pass "no-history scale_estimate est_tokens=$emitted2 (mechanical default)" \
                          || fail "no-history est_tokens=$emitted2, want default $def2"

echo ""
[ "$FAILED" -eq 0 ] && { echo "scale-calibration: ALL PASS"; exit 0; } || { echo "scale-calibration: FAILURES"; exit 1; }
