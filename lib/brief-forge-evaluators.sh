#!/usr/bin/env bash
# lib/brief-forge-evaluators.sh — generic default evaluators for Brief Forge envelopes.
#
# Each evaluator function takes an envelope file path and returns a JSON line
# with {score: 0-100, budget_used: int, notes: "..."}. Higher score = better.
# Mechanical-first; LLM upgrade hooks documented but not active in v4.0.
#
# These are the company-neutral evaluators that ship with Lintel. Custom
# evaluators (e.g. compliance-specific or voice-alignment checks) live in the
# active pack under packs/<pack>/brief-forge/evaluators/ and are sourced by the
# pack, not by this lib. For the _default pack the generic set below is all that
# runs.
#
# Sourced by skills/brief-forge/SKILL.md via run_evaluator dispatch.
#
# Public:
#   run_evaluator <name> <envelope_path>            → JSON result
#   evaluators_for_handoff <handoff_key>            → space-separated evaluator names
#   evaluator_security <envelope_path>              → JSON result
#   evaluator_completeness <envelope_path>          → JSON result
#   evaluator_stale <envelope_path>                 → JSON result

# sourced library: no 'set -uo pipefail' here (shell opts leak into every caller — skills/hooks/tests); functions guard their own vars

# ─── Pack resolution ───────────────────────────────────────────────────────
# Resolve which evaluators to run for a given hand-off from the active pack.
# Reads brief_forge_handoffs.<handoff_key>.evaluators via resolve_pack_field.
# For the _default pack this yields only the generic evaluators; an external
# pack (e.g. lintel-caip-pack) may declare its own additional evaluators that
# it ships under packs/<pack>/brief-forge/evaluators/.
_BFE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
if [ -f "$_BFE_DIR/pack-resolver.sh" ]; then
  # shellcheck source=lib/pack-resolver.sh
  source "$_BFE_DIR/pack-resolver.sh"
fi

evaluators_for_handoff() {
  local handoff="${1:?}"
  if declare -F resolve_pack_field >/dev/null 2>&1; then
    # YAML inline-list form: [security, stale] — strip brackets/commas.
    resolve_pack_field "brief_forge_handoffs.${handoff}.evaluators" \
      | tr -d '[]' | tr ',' ' '
  fi
}

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

# Pack-specific evaluators (compliance, voice-alignment, etc.) are NOT defined
# here. They live in the active pack under packs/<pack>/brief-forge/evaluators/
# and are resolved per hand-off via evaluators_for_handoff / resolve_pack_field.

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
  for e in security completeness stale; do
    printf '  %s → %s\n' "$e" "$(run_evaluator "$e" "$tmp")"
  done
  printf '  evaluators_for_handoff on_subagent_spawn → %s\n' "$(evaluators_for_handoff on_subagent_spawn)"
  rm -f "$tmp"
fi
