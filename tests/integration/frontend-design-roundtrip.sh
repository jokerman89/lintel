#!/usr/bin/env bash
# tests/integration/frontend-design-roundtrip.sh
#
# Minimum-viable roundtrip test för v3.7 Fas A1 (M-6 resolution from /plan-eng-review).
#
# Validates contract: a hand-crafted frontend-design-spec.json (matching the
# Step 5 schema specced i skills/frontend-design/SKILL.md) MUST be readable
# + actionable by future generate-web --from-frontend-design mode (Fas B).
#
# Fas A1 scope: this test verifies SCHEMA SHAPE, not actual rendering.
# Fas B will extend this test to invoke generate-web and assert HTML output.
#
# tag: v3.7 fas-a1 m-6-resolution

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/integration/frontend-design-roundtrip.sh"
echo "=============================================="

# Step 1 — Construct a minimal frontend-design-spec.json that adheres to
# the schema documented in skills/frontend-design/SKILL.md Step 5.
SPEC="$TMP/frontend-design-spec.json"
cat > "$SPEC" <<'JSON'
{
  "schema_version": 1,
  "generated_at": "2026-05-28T12:00:00Z",
  "brief_hash": "test-hash-fas-a1",
  "source": "frontend-design",
  "target_format": "single-file",
  "typography": {
    "schema_version": 1,
    "font_stacks": [
      {
        "role": "heading",
        "family": "Fraunces",
        "fallback_stack": ["Georgia", "serif"],
        "variable_axes": {"weight": [400, 700]},
        "loading_strategy": "Google Fonts CDN",
        "license": {"type": "free", "source": "Google Fonts"}
      },
      {
        "role": "body",
        "family": "Inter",
        "fallback_stack": ["-apple-system", "sans-serif"],
        "variable_axes": {"weight": [400, 600]},
        "loading_strategy": "Google Fonts CDN",
        "license": {"type": "free", "source": "Google Fonts"}
      }
    ],
    "size_scale": {"ratio": 1.25, "base_px": 16},
    "line_heights": {"tight": 1.1, "normal": 1.5, "relaxed": 1.625}
  },
  "motion": {
    "schema_version": 1,
    "energy_level": "moderate",
    "libraries": [
      {"name": "gsap", "purpose": "scroll-choreography", "version_min": "3.12.x", "npm": "gsap"},
      {"name": "@studio-freight/lenis", "purpose": "smooth-scroll", "version_min": "1.0.x", "npm": "@studio-freight/lenis"}
    ],
    "key_animations": [
      {"name": "hero-reveal", "trigger": "scroll-position 0% → 30%", "library": "gsap+ScrollTrigger"},
      {"name": "section-fade-up", "trigger": "section enters viewport 20%", "library": "gsap"}
    ],
    "perf_budget": {
      "fps_target": 60,
      "fallback_for_prefers_reduced_motion": "disable-all-scroll-animations"
    }
  },
  "shader": null,
  "component_libraries": [
    {"name": "shadcn", "kind": "primitive"},
    {"name": "aceternity-ui", "kind": "motion-enhanced"}
  ],
  "layout_grammar": {
    "max_width": "1200px",
    "section_spacing": "clamp(4rem, 8vw, 8rem)",
    "grid": "12-col"
  },
  "interaction_signature": {
    "scroll_smoothing": true,
    "hover_intent": "subtle",
    "page_transitions": "fade-or-slide"
  },
  "visual_thesis": "Editorial-grade legal-tech landing — Fraunces serif gravitas + Inter body precision, GSAP-driven scroll-choreography with Lenis smoothing, shadcn primitives augmented with Aceternity motion-cards.",
  "voice_tier": "internal"
}
JSON

if [ -f "$SPEC" ]; then
  pass "frontend-design-spec.json scaffolded"
else
  fail "spec scaffolding failed"
  exit 1
fi

# Step 2 — Validate schema_version field (M-5 contract)
if command -v jq >/dev/null 2>&1; then
  if jq -e '.schema_version == 1' "$SPEC" >/dev/null 2>&1; then
    pass "spec has schema_version: 1 (M-5)"
  else
    fail "spec missing schema_version (M-5 contract violation)"
  fi

  # Step 3 — Validate source-discriminator (M-1 contract)
  if jq -e '.source == "frontend-design"' "$SPEC" >/dev/null 2>&1; then
    pass "spec source-discriminator = frontend-design (M-1)"
  else
    fail "spec source-discriminator wrong or missing (M-1 contract)"
  fi

  # Step 4 — Validate required top-level fields per skills/frontend-design/SKILL.md Step 5
  for field in typography motion component_libraries layout_grammar interaction_signature visual_thesis voice_tier; do
    if jq -e ".$field" "$SPEC" >/dev/null 2>&1; then
      pass "spec has required field: $field"
    else
      fail "spec missing required field: $field"
    fi
  done

  # Step 5 — Validate embedded sub-schemas have own schema_version
  if jq -e '.typography.schema_version == 1' "$SPEC" >/dev/null 2>&1; then
    pass "embedded typography.schema_version: 1 (M-5 nested contract)"
  else
    fail "embedded typography.schema_version missing"
  fi

  if jq -e '.motion.schema_version == 1' "$SPEC" >/dev/null 2>&1; then
    pass "embedded motion.schema_version: 1 (M-5 nested contract)"
  else
    fail "embedded motion.schema_version missing"
  fi

  # Step 6 — Validate motion.json has perf-budget with prefers-reduced-motion fallback (accessibility contract)
  if jq -e '.motion.perf_budget.fallback_for_prefers_reduced_motion' "$SPEC" >/dev/null 2>&1; then
    pass "motion spec includes prefers-reduced-motion fallback (accessibility)"
  else
    fail "motion spec missing prefers-reduced-motion fallback"
  fi

  # Step 7 — Validate font_stacks have license-field per entry
  license_missing=$(jq '[.typography.font_stacks[] | select(.license == null)] | length' "$SPEC" 2>/dev/null || echo 1)
  if [ "$license_missing" = "0" ]; then
    pass "all typography font_stacks have license field"
  else
    fail "$license_missing font_stacks missing license field"
  fi
else
  echo "  WARN: jq not available — running grep fallback (CI has jq; local dev may not)"

  # Grep fallback — basic shape checks
  grep -q '"schema_version": 1' "$SPEC" && pass "spec has schema_version: 1 (grep fallback)" || fail "spec missing schema_version"
  grep -q '"source": "frontend-design"' "$SPEC" && pass "spec has source discriminator (grep fallback)" || fail "spec missing source discriminator"
  grep -q '"visual_thesis"' "$SPEC" && pass "spec has visual_thesis (grep fallback)" || fail "spec missing visual_thesis"
  grep -q '"typography"' "$SPEC" && pass "spec has typography (grep fallback)" || fail "spec missing typography"
  grep -q '"motion"' "$SPEC" && pass "spec has motion (grep fallback)" || fail "spec missing motion"
  grep -q '"component_libraries"' "$SPEC" && pass "spec has component_libraries (grep fallback)" || fail "spec missing component_libraries"
  grep -q '"layout_grammar"' "$SPEC" && pass "spec has layout_grammar (grep fallback)" || fail "spec missing layout_grammar"
  grep -q '"interaction_signature"' "$SPEC" && pass "spec has interaction_signature (grep fallback)" || fail "spec missing interaction_signature"
fi

# Step 8 — Verify skills/frontend-design/SKILL.md documents the schema we just validated
SKILL="$REPO_ROOT/skills/frontend-design/SKILL.md"
if [ -f "$SKILL" ]; then
  # Required schema fields documented in SKILL.md body
  for keyword in "schema_version" "source" "target_format" "typography" "motion" "visual_thesis" "voice_tier"; do
    if grep -q "$keyword" "$SKILL"; then
      pass "frontend-design SKILL.md documents field: $keyword"
    else
      fail "frontend-design SKILL.md missing schema field: $keyword"
    fi
  done
fi

# Step 9 — Future Fas B: this test will be extended to invoke generate-web
# --from-frontend-design "$TMP" and assert that HTML output references the
# typography family + GSAP imports. For Fas A1, schema-shape contract is the bar.

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All frontend-design-roundtrip tests PASSED"
  echo ""
  echo "Note: Fas B will extend this test to invoke generate-web --from-frontend-design"
  echo "and assert produced HTML references typography + motion choices. Fas A1 bar:"
  echo "schema-shape contract validated."
  exit 0
else
  echo "Some frontend-design-roundtrip tests FAILED"
  exit 1
fi
