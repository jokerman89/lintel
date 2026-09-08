#!/usr/bin/env bash
# tests/unit/scale-estimator.sh
# Asserts the scale-estimator's mechanical contract that SENSE step 0e relies on:
#   T8  — fixture requests classify to the expected size + ambiguity
#   T9  — escalate=yes iff ambiguous (the gate-fire signal); clear ⇒ silent
#   T10 — mechanical labels are usable standalone (graceful no-AI fallback)
# tag: slice-1 scope-scaled-planning

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EST="$REPO_ROOT/lib/scale-estimator.sh"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/scale-estimator.sh"
echo "=============================="
[ -f "$EST" ] || { fail "$EST MISSING"; exit 1; }
# shellcheck disable=SC1090
source "$EST"

# expect_size <prompt> <expected-size>
expect_size() {
  local got; got=$(classify_size "$1")
  [ "$got" = "$2" ] && pass "size '$1' → $2" || fail "size '$1' → got $got, want $2"
}
# expect_amb <prompt> <yes|no>
expect_amb() {
  local got; got=$(scale_ambiguous "$1")
  [ "$got" = "$2" ] && pass "ambiguous '$1' → $2" || fail "ambiguous '$1' → got $got, want $2"
}

# ─── T8: size classification (the design trace cases) ────────────────────────
echo ""
echo "[T8] size classification"
expect_size "fix the typo in README"                     XS    # frictionless small
expect_size "deploy a website to azure"                  XL    # smoking gun → conservative large
expect_size "deploy the static landing page to azure"    S     # small qualifier downsizes
expect_size "stand up a full landing zone with CI/CD on azure" XL  # large qualifier
expect_size "rename a single file"                       XS
expect_size "add an oauth login flow"                    M     # one high-surface
expect_size "add multi-tenant support"                    L     # isolation crosses boundaries
expect_size "add multi tenant support"                    L
expect_size "add auth, database and API support"           XL    # preserve multi-surface sizing
expect_size "edit the capital letter in the title"        S     # capital is not API
expect_size "small wording change"                        XS    # small is not all
expect_size "update the forest heading"                   S     # forest is not REST
expect_size "update the draws label"                      S     # draws is not AWS
expect_size "add an API endpoint"                         M     # complete uppercase word still matches
expect_size "update the deployment notes"                 S     # deploy is not deployment

got_breadth=$(detect_breadth "small wording change")
[ "$got_breadth" = 0 ] && pass "small wording change has no broad-scope signal" \
                      || fail "small wording change breadth=$got_breadth, want 0"
got_surfaces=$(detect_surface_count "edit the capital letter in the title")
[ "$got_surfaces" = 0 ] && pass "capital letter has no API surface" \
                       || fail "capital letter surfaces=$got_surfaces, want 0"

# ─── T9: ambiguity = the gate-fire signal ────────────────────────────────────
echo ""
echo "[T9] ambiguity / gate-fire signal"
expect_amb "deploy a website to azure"                   yes   # bimodal, no qualifier → ask
expect_amb "deploy the static landing page to azure"     no    # qualifier present → silent
expect_amb "stand up a full landing zone on azure"       no    # qualifier present → silent
expect_amb "fix the typo in README"                      no    # not infra → silent
expect_amb "add multi-tenant support"                     no    # large but unambiguous
expect_amb "update the draws label"                       no    # no accidental AWS gate
# escalate tracks ambiguity: yes ⇒ gate fires, no ⇒ SENSE stays silent
for p in "deploy a website to azure" "fix the typo in README"; do
  amb=$(scale_ambiguous "$p"); esc=$(scale_escalate "$p" medium)
  [ "$amb" = "$esc" ] && pass "escalate tracks ambiguity for '$p' ($esc)" \
                       || fail "escalate '$p': amb=$amb esc=$esc (should match)"
done

# ─── T10: graceful no-AI fallback — mechanical labels usable standalone ───────
echo ""
echo "[T10] no-AI fallback (mechanical labels usable alone)"
# With NO agent escalation, classify_size + scale_ambiguous + size_to_depth_schema
# must still produce a complete, usable verdict (the degradation path).
s=$(classify_size "deploy a website to azure")
sch=$(size_to_depth_schema "$s")
[ -n "$s" ] && [ -n "$sch" ] && pass "mechanical verdict complete without AI: size=$s schema=$sch" \
            || fail "mechanical fallback incomplete: size='$s' schema='$sch'"
# depth_schema is well-formed for every size
for sz in XS S M L XL; do
  v=$(size_to_depth_schema "$sz")
  case "$v" in flat|phased|tree) pass "depth_schema($sz)=$v" ;; *) fail "depth_schema($sz)=$v invalid" ;; esac
done
# scale_estimate emits a parseable block with all required keys
blk=$(scale_estimate "deploy a website to azure" medium)
for key in "size:" "confidence:" "ambiguous:" "escalate:" "depth_schema:"; do
  printf '%s' "$blk" | grep -q "$key" && pass "scope block has $key" || fail "scope block missing $key"
done

echo ""
[ "$FAILED" -eq 0 ] && { echo "scale-estimator: ALL PASS"; exit 0; } || { echo "scale-estimator: FAILURES"; exit 1; }
