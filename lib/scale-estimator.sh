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
#   size_default_prior <size>      → integer est_tokens (mechanical fallback)
#   scale_calibrated_prior <size>  → integer est_tokens, corrected from history
#                                    (Slice 4 calibration loop; falls back to
#                                     size_default_prior when no history exists)
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

# sourced library: no 'set -uo pipefail' here (shell opts leak into every caller — skills/hooks/tests); functions guard their own vars

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
# flat (XS/S), phased (M), tree (L/XL) — full tree rendering shipped in Slice 2
# (plan.template.md is depth_schema-parametric; see skills/plan/SKILL.md).
size_to_depth_schema() {
  case "${1:-S}" in
    XS|S) printf 'flat' ;;
    M)    printf 'phased' ;;
    L|XL) printf 'tree' ;;
    *)    printf 'flat' ;;
  esac
}

# ─── Token priors (Slice 4 — calibration loop, design §3.5 / §3.7) ────────────
# The mechanical, hardcoded fallback prior per size — the "guess" used when no
# calibration history exists yet. scale_calibrated_prior corrects this from the
# audit log over time. Order-of-magnitude bands matching the design's readings
# (XS≈4k … XL≈120k). Override by exporting SCALE_PRIOR_<SIZE>.
size_default_prior() {
  case "${1:-S}" in
    XS) printf '%s' "${SCALE_PRIOR_XS:-4000}" ;;
    S)  printf '%s' "${SCALE_PRIOR_S:-12000}" ;;
    M)  printf '%s' "${SCALE_PRIOR_M:-30000}" ;;
    L)  printf '%s' "${SCALE_PRIOR_L:-70000}" ;;
    XL) printf '%s' "${SCALE_PRIOR_XL:-120000}" ;;
    *)  printf '%s' "${SCALE_PRIOR_S:-12000}" ;;
  esac
}

# ─── scale_calibrated_prior ───────────────────────────────────────────────────
# The compounding edge (design §3.5): correct the token prior for a given size
# from recorded actual-vs-estimated history instead of the hardcoded guess.
#
#   scale_calibrated_prior <size>  → integer est_tokens
#
# Reads CAPTURE's append-only log at .claude/runtime/audit/granularity.jsonl
# (written via `audit_log granularity ...`, scope-routed by bin/_audit.sh). For every record whose `size`
# field matches <size> and that carries a numeric `actual_tokens`, it takes the
# MEDIAN of those actuals as the corrected prior — median, not mean, so a single
# runaway cycle cannot skew the band.
#
# Graceful fallback (keeps Slice 1's behaviour intact): if the log is absent,
# unreadable, or holds no usable actual_tokens for that size, it returns
# size_default_prior — the exact mechanical guess used before this slice. This
# function is purely additive: callers that never had history simply get the
# old number.
scale_calibrated_prior() {
  local size="${1:-S}"
  local home="${LINTEL_HOME:-$HOME/.lintel}"
  local root
  root="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}"
  local log="$root/.claude/runtime/audit/granularity.jsonl"
  [ -r "$log" ] || log="${LINTEL_AUDIT_DIR:-$home/audit}/granularity.jsonl" # legacy-fallback-ok

  # No history → mechanical default (the Slice-1 guess).
  [ -r "$log" ] || { size_default_prior "$size"; return 0; }

  # Collect actual_tokens for records matching this size. Pure awk: match the
  # size field exactly, pull the numeric actual_tokens, sort, take the median.
  # If nothing matches, awk prints the empty string and we fall back.
  local median
  median=$(awk -v want="$size" '
    {
      # size field: "size":"<value>"
      if (match($0, /"size":"[^"]*"/)) {
        s = substr($0, RSTART+8, RLENGTH-9)
      } else { s = "" }
      if (s != want) next
      # actual_tokens field: "actual_tokens":"<n>" or :<n>
      if (match($0, /"actual_tokens":"?[0-9]+"?/)) {
        t = substr($0, RSTART, RLENGTH)
        gsub(/[^0-9]/, "", t)
        if (t != "") vals[n++] = t + 0
      }
    }
    END {
      if (n == 0) { print ""; exit }
      # insertion sort (n is small — one entry per cycle)
      for (i = 1; i < n; i++) {
        v = vals[i]; j = i - 1
        while (j >= 0 && vals[j] > v) { vals[j+1] = vals[j]; j-- }
        vals[j+1] = v
      }
      if (n % 2) print vals[(n-1)/2]
      else       print int((vals[n/2-1] + vals[n/2]) / 2)
    }
  ' "$log" 2>/dev/null)

  if [ -n "$median" ]; then printf '%s' "$median"; else size_default_prior "$size"; fi
}

# ─── scale_estimate ──────────────────────────────────────────────────────────
# Emits the scope block (YAML) for SENSE step 0e to read. Mechanical; the agent
# refines `readings` when escalate=yes (decision 1B).
scale_estimate() {
  local p="${1:-}" thr="${2:-medium}"
  local size amb conf esc schema breadth depth surfaces est_tokens
  size=$(classify_size "$p")
  amb=$(scale_ambiguous "$p")
  conf=$(scale_confidence "$p")
  esc=$(scale_escalate "$p" "$thr")
  schema=$(size_to_depth_schema "$size")
  # est_tokens: calibrated from CAPTURE history when present, else the
  # mechanical default (Slice 4, design §3.5). Additive — never changes the
  # pre-existing keys, only adds one informed by the calibration loop.
  est_tokens=$(scale_calibrated_prior "$size")
  breadth=$(detect_breadth "$p"); depth=$(detect_depth "$p"); surfaces=$(detect_surface_count "$p")
  cat <<EOF
scale:
  size: $size
  confidence: $conf
  ambiguous: $amb
  escalate: $esc
  depth_schema: $schema
  est_tokens: $est_tokens
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
    sz=$(classify_size "$p")
    printf '  prompt=%-58s size=%-3s ambiguous=%-3s schema=%-7s est_tokens=%s\n' \
      "\"$p\"" "$sz" "$(scale_ambiguous "$p")" "$(size_to_depth_schema "$sz")" "$(scale_calibrated_prior "$sz")"
  done
fi
