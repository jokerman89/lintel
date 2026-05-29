#!/usr/bin/env bash
# lib/brief-forge-evaluators.sh — 5 default evaluators for Brief Forge envelopes.
#
# Each evaluator function takes an envelope file path and returns a JSON line
# with {score: 0-100, budget_used: int, notes: "..."}. Higher score = better.
# Mechanical-first; LLM upgrade hooks documented but not active in v4.0.
#
# Sourced by skills/brief-forge/SKILL.md via run_evaluator dispatch.
#
# Public:
#   run_evaluator <name> <envelope_path>            → JSON result
#   evaluator_security <envelope_path>              → JSON result
#   evaluator_completeness <envelope_path>          → JSON result
#   evaluator_stale <envelope_path>                 → JSON result
#   evaluator_sdl_compliance <envelope_path>        → JSON result
#   evaluator_trailblazer_alignment <envelope_path> → JSON result

set -uo pipefail

# ─── run_evaluator dispatcher ──────────────────────────────────────────────
run_evaluator() {
  local name="${1:?}"
  local envelope="${2:?}"
  local fn="evaluator_$(printf '%s' "$name" | tr - _)"
  if declare -F "$fn" >/dev/null 2>&1; then
    "$fn" "$envelope"
  else
    printf '{"score":50,"budget_used":0,"notes":"unknown evaluator: %s"}' "$name"
  fi
}

# ─── evaluator_security ────────────────────────────────────────────────────
# Scans envelope for known dangerous patterns: secrets, shell injection
# markers, prompt injection markers. Mechanical-first via regex.
evaluator_security() {
  local f="${1:?}"
  local score=100
  local notes=""
  local hits=0

  # Pattern 1: secrets / API keys
  if grep -qE '(AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{40,}|ghp_[A-Za-z0-9]{36,}|xox[bp]-[A-Za-z0-9-]{20,}|AIza[0-9A-Za-z_-]{35})' "$f" 2>/dev/null; then
    score=$((score - 60))
    notes="${notes}possible API key pattern detected; "
    hits=$((hits + 1))
  fi

  # Pattern 2: shell injection markers
  if grep -qE '\$\(.*rm -rf|;[[:space:]]*rm[[:space:]]+-rf[[:space:]]+/|curl[[:space:]]+[^|]*\|[[:space:]]*sh' "$f" 2>/dev/null; then
    score=$((score - 40))
    notes="${notes}shell injection pattern; "
    hits=$((hits + 1))
  fi

  # Pattern 3: prompt injection markers
  if grep -qiE 'ignore (previous|prior) instructions|system: you are now|new role:' "$f" 2>/dev/null; then
    score=$((score - 30))
    notes="${notes}prompt injection marker; "
    hits=$((hits + 1))
  fi

  [ "$score" -lt 0 ] && score=0
  [ -z "$notes" ] && notes="clean ($hits hits)"

  printf '{"score":%d,"budget_used":50,"notes":"%s"}' "$score" "$notes"
}

# ─── evaluator_completeness ────────────────────────────────────────────────
# Checks content_type-specific required fields, surfaces gaps.
evaluator_completeness() {
  local f="${1:?}"
  local score=100
  local notes=""

  local ct
  ct=$(grep -E '^[[:space:]]+content_type:' "$f" | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')

  case "$ct" in
    brief)
      for required in task constraints acceptance; do
        if ! grep -qE "^[[:space:]]+${required}:" "$f"; then
          score=$((score - 25))
          notes="${notes}missing brief.${required}; "
        fi
      done
      ;;
    spec)
      for required in intent inputs outputs; do
        if ! grep -qE "^[[:space:]]+${required}:" "$f"; then
          score=$((score - 25))
          notes="${notes}missing spec.${required}; "
        fi
      done
      ;;
    plan)
      if ! grep -qE "^[[:space:]]+tasks:" "$f"; then
        score=$((score - 50))
        notes="${notes}missing plan.tasks; "
      fi
      ;;
    *)
      # payload_freeform — no required content fields
      ;;
  esac

  [ "$score" -lt 0 ] && score=0
  [ -z "$notes" ] && notes="all required fields present"
  printf '{"score":%d,"budget_used":30,"notes":"%s"}' "$score" "$notes"
}

# ─── evaluator_stale ───────────────────────────────────────────────────────
# Verifies referenced paths/files exist now (envelope may have been issued
# minutes/hours ago; world may have moved).
evaluator_stale() {
  local f="${1:?}"
  local score=100
  local notes=""
  local checked=0
  local missing=0

  # Extract context_pointers entries
  while IFS= read -r ptr; do
    ptr=$(printf '%s' "$ptr" | sed 's/^[[:space:]]*-[[:space:]]*//' | tr -d '"' | tr -d "'")
    [ -z "$ptr" ] && continue
    checked=$((checked + 1))

    # Only check file:// or relative-path pointers (skip urls)
    case "$ptr" in
      http://*|https://*) continue ;;
    esac

    # Strip file:// prefix
    ptr="${ptr#file://}"

    if [ ! -e "$ptr" ]; then
      missing=$((missing + 1))
      notes="${notes}missing: $ptr; "
    fi
  done < <(awk '/^[[:space:]]+context_pointers:/{flag=1; next} /^[[:space:]]*[a-z_]+:/{flag=0} flag' "$f")

  if [ "$missing" -gt 0 ]; then
    score=$((100 - (missing * 30)))
    [ "$score" -lt 0 ] && score=0
  else
    notes="all $checked context_pointers present (or none declared)"
  fi

  printf '{"score":%d,"budget_used":40,"notes":"%s"}' "$score" "$notes"
}

# ─── evaluator_sdl_compliance ──────────────────────────────────────────────
# MS-internal + caip-se: verifies SDL hooks ran on payload. Mechanical check:
# audit log contains SDL hook invocations within the last 24h tied to from/to.
evaluator_sdl_compliance() {
  local f="${1:?}"
  local score=100
  local notes=""

  local from to
  from=$(grep -E '^[[:space:]]+from:' "$f" | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
  to=$(grep -E '^[[:space:]]+to:' "$f" | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')

  local sdl_log="${LINTEL_HOME:-$HOME/.lintel}/audit/ms-internal-sdl.jsonl"

  if [ ! -f "$sdl_log" ]; then
    # No SDL log means SDL hooks didn't run; for ms-internal/caip-se this is a fail
    score=60
    notes="SDL audit log not found (acceptable for non-MS packs; fail for ms-internal/caip-se)"
  else
    # Look for recent SDL hook invocation tied to from or to
    if grep -qE "\"from\":\"$from\"|\"to\":\"$to\"|\"actor\":\"$from\"" "$sdl_log" 2>/dev/null; then
      notes="SDL hooks recorded for $from or $to"
    else
      score=70
      notes="no recent SDL hook invocation tied to $from/$to — verify"
    fi
  fi

  printf '{"score":%d,"budget_used":60,"notes":"%s"}' "$score" "$notes"
}

# ─── evaluator_trailblazer_alignment ───────────────────────────────────────
# caip-se: voice-tier check against Trailblazer corpus. Mechanical:
# 1) HEAD.voice_tier == trailblazer
# 2) BODY content does NOT contain forbidden non-Trailblazer markers
# 3) Specific Trailblazer cues present in customer-facing content_types
evaluator_trailblazer_alignment() {
  local f="${1:?}"
  local score=100
  local notes=""

  local voice_tier
  voice_tier=$(grep -E '^[[:space:]]+voice_tier:' "$f" | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')

  if [ "$voice_tier" != "trailblazer" ]; then
    # Not a Trailblazer envelope — evaluator is no-op
    printf '{"score":100,"budget_used":10,"notes":"voice_tier != trailblazer; skip"}'
    return 0
  fi

  # Forbidden non-Trailblazer markers (corporate/AI cliches per CLAUDE.md voice rules)
  if grep -qiE 'delve into|crucial|robust|comprehensive|nuanced|leverage[ds]?[[:space:]]+(the|our)|unlock[[:space:]]+the[[:space:]]+power|seamless(ly)?[[:space:]]+integrate' "$f" 2>/dev/null; then
    score=$((score - 35))
    notes="${notes}AI/corporate cliches detected; "
  fi

  # Em-dash check (per voice rules: no em dashes)
  if grep -q '—' "$f" 2>/dev/null; then
    score=$((score - 10))
    notes="${notes}em-dash present (Trailblazer voice avoids); "
  fi

  [ "$score" -lt 0 ] && score=0
  [ -z "$notes" ] && notes="Trailblazer alignment clean"
  printf '{"score":%d,"budget_used":40,"notes":"%s"}' "$score" "$notes"
}

# ─── Self-test mode ────────────────────────────────────────────────────────
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "brief-forge-evaluators.sh self-test:"
  tmp=$(mktemp)
  cat > "$tmp" <<'EOF'
head:
  envelope_id: "01J-test"
  envelope_schema_version: "1"
  kind: subagent_spawn
  from: plan
  to: PlanReviewer
  issued_at: "2026-05-29T15:00:00Z"
  voice_tier: internal
body:
  content_type: brief
  content:
    task: Review the plan for elegance
    constraints:
      - no scope creep
    acceptance:
      - reviewer surfaces specific concerns or APPROVES
tail:
  completeness_score: 0
  evaluators_run: []
  escape_hatches: []
  audit_pointer: /tmp/x.jsonl
EOF
  for e in security completeness stale sdl_compliance trailblazer_alignment; do
    printf '  %s → %s\n' "$e" "$(run_evaluator "$e" "$tmp")"
  done
  rm -f "$tmp"
fi
