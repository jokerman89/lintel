#!/usr/bin/env bash
# lib/scale-estimator.sh — mechanical scale estimation for SENSE (Slice 1)
#
# Sourced by skills/sense/SKILL.md (step 0b + step 0e). Provides the SIZE axis
# the harness lacked: turns a raw request into a T-shirt size (XS-XL) plus an
# ambiguity verdict, so the clarifying gate knows when to ask before PLAN burns
# tokens. Single source for breadth/size signals — the elephant-hint (step 0b)
# calls detect_breadth here instead of keeping its own copy.
#
#   detect_breadth <prompt>        → integer breadth score (elephant-hint corpus)
#   detect_depth <prompt>          → shallow | high | bimodal
#   detect_surface_count <prompt>  → integer count of distinct surfaces touched
#   classify_size <prompt>         → XS | S | M | L | XL
#   scale_ambiguous <prompt>       → yes | no   (bimodal reading, no size qualifier)
#   scale_confidence <prompt>      → low | high  (low ⇒ escalate to agent judgment)
#   scale_escalate <prompt> <thr>  → yes | no
#   size_to_depth_schema <size>    → flat | phased | tree
#   scale_estimate <prompt>        → emits the scope block (YAML) for the skill
#   elephant_score <prompt>        → alias of detect_breadth (back-compat)
#
# Design: docs/design/lintel-scope-and-scaled-planning-design.md §3.1
# Decisions: 1B (AI-from-start — the agent judges ambiguity when escalate=yes;
#            this lib emits the signal, SENSE step 0e handles the judgment),
#            2A (this lib is the single source; elephant-hint calls it).
#
# AI escalation note: in a markdown+bash harness the agent IS the LLM. This lib
# does the mechanical first-pass and emits `escalate: yes` when it is unsure;
# SENSE step 0e then asks the agent to judge ambiguity + sharpen the two
# readings. With no agent escalation available the mechanical labels stand
# (graceful fallback) — `classify_size` + `scale_ambiguous` are always usable
# on their own.

set -uo pipefail

# ─── Domain lexicon ──────────────────────────────────────────────────────────
# Bimodal-prone nouns: present without a size qualifier ⇒ the request could be
# small or large (static page vs landing zone). Slice 1 ships a thin universal
# set here; packs override via pack.yaml `scale.domain_lexicon` (deferred to
# the pack-load wiring — see design §8 R4). Override by exporting the vars.
SCALE_BIMODAL_LEXICON="${SCALE_BIMODAL_LEXICON:-azure|aws|gcp|k8s|kubernetes|cluster|deploy|hosting|landing.?zone|alz|terraform|bicep|cdk|front.?door|waf|cdn|ci/?cd|pipeline|infrastructure|infra}"
SCALE_SURFACE_LEXICON="${SCALE_SURFACE_LEXICON:-auth|oauth|login|sso|payment|billing|database|schema|migration|api|endpoint|multi.?tenant|tenant|rbac|permission|network|vnet|dns}"
SCALE_SMALL_QUALIFIER="${SCALE_SMALL_QUALIFIER:-static|single.?page|one.?page|just.?a|simple|small|tiny|typo|rename|minimal|landing.?page|quick|one.?file}"
SCALE_LARGE_QUALIFIER="${SCALE_LARGE_QUALIFIER:-platform|enterprise|production.?grade|full.?system|multi.?region|multi.?tenant|high.?availability|landing.?zone|alz|end.?to.?end|at.?scale}"

_scale_lc() { printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]'; }

# ─── detect_breadth ──────────────────────────────────────────────────────────
# Absorbs the elephant-hint corpus (was skills/sense step 0b). Single source.
detect_breadth() {
  local p; p="$(_scale_lc "${1:-}")"
  local score=0
  printf '%s' "$p" | grep -qiE "entire|all |every|whole|full system|complete rewrite|across all" && score=$((score+2))
  printf '%s' "$p" | grep -qiE "redesign|refactor everything|new architecture|from scratch" && score=$((score+2))
  printf '%s' "$p" | grep -qiE "and also|while we'?re at it|maybe also|could we also" && score=$((score+1))
  local wc; wc=$(printf '%s' "$p" | wc -w | tr -d ' ')
  [ "${wc:-0}" -gt 80 ] 2>/dev/null && score=$((score+1))
  printf '%s' "$score"
}

# Back-compat alias for the elephant-hint call site.
elephant_score() { detect_breadth "${1:-}"; }

# ─── detect_depth ────────────────────────────────────────────────────────────
# shallow → no infra/surface depth. high → high-surface (auth/data/api/net).
# bimodal → infra/hosting noun present (could be a static page or a cluster).
detect_depth() {
  local p; p="$(_scale_lc "${1:-}")"
  if printf '%s' "$p" | grep -qiE "$SCALE_BIMODAL_LEXICON"; then printf 'bimodal'; return 0; fi
  if printf '%s' "$p" | grep -qiE "$SCALE_SURFACE_LEXICON"; then printf 'high'; return 0; fi
  printf 'shallow'
}

# ─── detect_surface_count ────────────────────────────────────────────────────
# Distinct high-surface areas named (auth, data, api, network, …).
detect_surface_count() {
  local p; p="$(_scale_lc "${1:-}")"
  local n=0
  printf '%s' "$p" | grep -qiE "auth|oauth|login|sso|rbac|permission" && n=$((n+1))
  printf '%s' "$p" | grep -qiE "database|schema|migration|data model|sql" && n=$((n+1))
  printf '%s' "$p" | grep -qiE "api|endpoint|rest|graphql|grpc" && n=$((n+1))
  printf '%s' "$p" | grep -qiE "network|vnet|dns|firewall|front.?door|cdn|waf" && n=$((n+1))
  printf '%s' "$p" | grep -qiE "payment|billing" && n=$((n+1))
  printf '%s' "$p" | grep -qiE "multi.?tenant|tenant" && n=$((n+1))
  printf '%s' "$n"
}

_has_small_qual() { printf '%s' "$(_scale_lc "${1:-}")" | grep -qiE "$SCALE_SMALL_QUALIFIER"; }
_has_large_qual() { printf '%s' "$(_scale_lc "${1:-}")" | grep -qiE "$SCALE_LARGE_QUALIFIER"; }

# ─── classify_size ───────────────────────────────────────────────────────────
# XS | S | M | L | XL. Threshold table — design §3.1.
# When the request is bimodal-ambiguous the LARGER reading is returned
# (conservative: assume big until the gate disambiguates), and scale_ambiguous
# returns yes so the gate fires and can downsize.
classify_size() {
  local p="${1:-}"
  local breadth depth surfaces
  breadth=$(detect_breadth "$p")
  depth=$(detect_depth "$p")
  surfaces=$(detect_surface_count "$p")

  # Bimodal (infra) dominates: qualifier decides, else assume large (gate fires)
  if [ "$depth" = "bimodal" ]; then
    if _has_large_qual "$p"; then printf 'XL'; return 0; fi
    if _has_small_qual "$p"; then printf 'S';  return 0; fi
    printf 'XL'; return 0                       # ambiguous ⇒ conservative large
  fi

  # Non-infra: combine breadth + surface + qualifier
  if [ "$surfaces" -ge 3 ] 2>/dev/null; then printf 'XL'; return 0; fi
  if [ "$breadth" -ge 4 ] 2>/dev/null || [ "$surfaces" -ge 2 ] 2>/dev/null; then printf 'L'; return 0; fi
  if [ "$breadth" -ge 2 ] 2>/dev/null || [ "$surfaces" -ge 1 ] 2>/dev/null || [ "$depth" = "high" ]; then printf 'M'; return 0; fi
  if _has_small_qual "$p"; then printf 'XS'; return 0; fi
  printf 'S'
}

# ─── scale_ambiguous ─────────────────────────────────────────────────────────
# yes when a bimodal (infra) noun is present with NO size qualifier — the
# "static page or landing zone?" case the clarifying gate exists for.
scale_ambiguous() {
  local p="${1:-}"
  [ "$(detect_depth "$p")" = "bimodal" ] || { printf 'no'; return 0; }
  if _has_small_qual "$p" || _has_large_qual "$p"; then printf 'no'; return 0; fi
  printf 'yes'
}

# ─── scale_confidence ────────────────────────────────────────────────────────
# low ⇒ the gate should escalate to agent judgment. Ambiguous is always low.
scale_confidence() {
  [ "$(scale_ambiguous "${1:-}")" = "yes" ] && { printf 'low'; return 0; }
  printf 'high'
}

# ─── scale_escalate ──────────────────────────────────────────────────────────
# Mirrors orientator's threshold semantics: escalate when confidence < threshold.
scale_escalate() {
  local conf thr c_rank t_rank
  conf=$(scale_confidence "${1:-}")
  thr="${2:-medium}"
  [ "$thr" = "never" ] && { printf 'no'; return 0; }
  case "$conf" in low) c_rank=1 ;; medium) c_rank=2 ;; high) c_rank=3 ;; *) c_rank=1 ;; esac
  case "$thr"  in low) t_rank=1 ;; medium) t_rank=2 ;; high) t_rank=3 ;; *) t_rank=2 ;; esac
  [ "$c_rank" -lt "$t_rank" ] && printf 'yes' || printf 'no'
}

# ─── size_to_depth_schema ────────────────────────────────────────────────────
# Slice 1 renders flat (XS/S) and phased (M). tree (L/XL) ships in Slice 2 —
# until then L/XL fall back to phased so a big plan is at least sectioned.
size_to_depth_schema() {
  case "${1:-S}" in
    XS|S) printf 'flat' ;;
    M)    printf 'phased' ;;
    L|XL) printf 'tree' ;;
    *)    printf 'flat' ;;
  esac
}

# ─── scale_estimate ──────────────────────────────────────────────────────────
# Emits the scope block (YAML) for SENSE step 0e to read. Mechanical; the agent
# refines `readings` when escalate=yes (decision 1B).
scale_estimate() {
  local p="${1:-}" thr="${2:-medium}"
  local size amb conf esc schema breadth depth surfaces
  size=$(classify_size "$p")
  amb=$(scale_ambiguous "$p")
  conf=$(scale_confidence "$p")
  esc=$(scale_escalate "$p" "$thr")
  schema=$(size_to_depth_schema "$size")
  breadth=$(detect_breadth "$p"); depth=$(detect_depth "$p"); surfaces=$(detect_surface_count "$p")
  cat <<EOF
scale:
  size: $size
  confidence: $conf
  ambiguous: $amb
  escalate: $esc
  depth_schema: $schema
  signals: { breadth: $breadth, depth: $depth, surfaces: $surfaces }
EOF
}

# ─── Self-test mode ──────────────────────────────────────────────────────────
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "scale-estimator.sh self-test:"
  for p in \
    "fix the typo in README" \
    "deploy a website to azure" \
    "deploy the static landing page to azure" \
    "stand up a full landing zone with CI/CD and front door on azure" \
    "add multi-tenant support" \
    "research how others do feature flags"; do
    printf '  prompt=%-58s size=%-3s ambiguous=%-3s schema=%s\n' \
      "\"$p\"" "$(classify_size "$p")" "$(scale_ambiguous "$p")" "$(size_to_depth_schema "$(classify_size "$p")")"
  done
fi
