#!/usr/bin/env bash
# lib/brief-forge.sh — envelope construction helpers for skills/brief-forge.
#
# Sourced by skills/brief-forge/SKILL.md. Provides:
#   forge_envelope_head <kind> <from> <to>             → HEAD YAML
#   forge_envelope_body <content_type> <content_file>  → BODY YAML
#   forge_envelope_tail <score> <evaluators...> <hatches> <audit_pointer> → TAIL YAML
#   forge_envelope <kind> <from> <to> <ctype> <cfile>  → full envelope
#   generate_envelope_id                                → ULID-shaped id
#   write_bypass_audit <kind> <from> <to>              → bypass-stub audit
#   yaml_to_json <file>                                → JSON line
#   build_escape_hatches <ctype> <from>                → escape-hatch list
#   aggregate_evaluator_scores <results...>            → min score
#
# Ref: lib/envelope-schema.yaml v1
#      docs/concepts/envelope.md
#      docs/concepts/brief-forge.md

set -uo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
LINTEL_AUDIT_DIR="${LINTEL_AUDIT_DIR:-$LINTEL_HOME/audit}"

# Unified audit writer (lib/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../bin/_audit.sh"

# ─── generate_envelope_id ──────────────────────────────────────────────────
# Returns a sortable, unique id. ULID-like: 26 char Base32.
# Phase 3 uses a simple sortable id; Phase 4 may upgrade to full ULID.
generate_envelope_id() {
  local ts rand
  ts=$(date -u +%Y%m%d%H%M%S)
  rand=$(printf '%s' "$RANDOM$RANDOM$$" | head -c 12)
  printf '01J%s%s' "$ts" "$rand"
}

# ─── forge_envelope_head ───────────────────────────────────────────────────
forge_envelope_head() {
  local kind="${1:?}"
  local from="${2:?}"
  local to="${3:?}"
  local envelope_id ts pack operator voice_tier cycle_id
  envelope_id=$(generate_envelope_id)
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  pack="${LINTEL_ACTIVE_PACK:-${active_pack:-_default}}"
  operator=$(whoami 2>/dev/null || echo unknown)
  voice_tier="${VOICE_TIER:-internal}"
  cycle_id="${CYCLE_ID:-}"

  cat <<EOF
head:
  envelope_id: "$envelope_id"
  envelope_schema_version: "1"
  kind: $kind
  from: $from
  to: $to
  issued_at: "$ts"
  pack: $pack
  operator: $operator
  voice_tier: $voice_tier
EOF
  [ -n "$cycle_id" ] && echo "  cycle_id: $cycle_id"
}

# ─── forge_envelope_body ───────────────────────────────────────────────────
forge_envelope_body() {
  local content_type="${1:?}"
  local content_file="${2:?}"

  if [ ! -f "$content_file" ]; then
    echo "ERROR: content_file '$content_file' not found" >&2
    return 1
  fi

  cat <<EOF
body:
  content_type: $content_type
  content:
EOF

  # Indent content file with 4 spaces (since body.content is at column 2)
  sed 's/^/    /' "$content_file"
}

# ─── forge_envelope_tail ───────────────────────────────────────────────────
forge_envelope_tail() {
  local score="${1:?}"
  shift
  # Remaining args: evaluator-results... escape_hatches audit_pointer
  # We pull audit_pointer (last) and escape_hatches (second-to-last) off.
  local audit_pointer="${!#}"
  local args=("$@")
  local n="${#args[@]}"
  local escape_hatches="${args[$((n - 2))]}"
  # Evaluator names = args 0..n-3
  local evaluator_names=()
  local i=0
  while [ "$i" -lt "$((n - 2))" ]; do
    # evaluator_results have format "name:json" — split
    local entry="${args[$i]}"
    evaluator_names+=("${entry%%:*}")
    i=$((i + 1))
  done

  cat <<EOF
tail:
  completeness_score: $score
  evaluators_run:
EOF
  for e in "${evaluator_names[@]}"; do
    echo "    - $e"
  done
  cat <<EOF
  escape_hatches:
EOF
  # escape_hatches comes as newline-separated string
  printf '%s\n' "$escape_hatches" | while IFS= read -r line; do
    [ -n "$line" ] && echo "    - $line"
  done
  echo "  audit_pointer: $audit_pointer"
}

# ─── forge_envelope (composes head + body + tail) ──────────────────────────
forge_envelope() {
  local kind="${1:?}" from="${2:?}" to="${3:?}" content_type="${4:?}" content_file="${5:?}"
  forge_envelope_head "$kind" "$from" "$to"
  forge_envelope_body "$content_type" "$content_file"
  # Tail is added by caller after running evaluators
}

# ─── write_bypass_audit ────────────────────────────────────────────────────
# Unified writer → .claude/runtime/audit/brief-forge.jsonl (scope-routed by
# _audit.sh; operator field now supplied by audit_log itself, no longer inlined here).
write_bypass_audit() {
  local kind="${1:?}" from="${2:?}" to="${3:?}"
  audit_log "brief-forge" "brief_forge_bypassed" "event=$kind" "from=$from" "to=$to"
}

# ─── yaml_to_json ──────────────────────────────────────────────────────────
# Best-effort YAML-to-JSON conversion for audit line. Falls back to base64
# if no YAML parser available, so the audit line is always a valid JSON.
yaml_to_json() {
  local file="${1:?}"
  if command -v yq >/dev/null 2>&1; then
    yq -o=json '.' "$file" 2>/dev/null | tr -d '\n'
  elif command -v python3 >/dev/null 2>&1; then
    python3 -c "
import sys, json
try:
    import yaml
    print(json.dumps(yaml.safe_load(open('$file'))))
except ImportError:
    import base64
    print(json.dumps({'_raw_yaml_b64': base64.b64encode(open('$file','rb').read()).decode()}))
" 2>/dev/null
  else
    # Last resort: emit as raw base64-wrapped JSON
    local raw
    raw=$(base64 -w0 < "$file" 2>/dev/null || base64 < "$file" | tr -d '\n')
    printf '{"_raw_yaml_b64":"%s"}' "$raw"
  fi
}

# ─── build_escape_hatches ──────────────────────────────────────────────────
build_escape_hatches() {
  local content_type="${1:?}"
  local from="${2:?}"

  case "$content_type" in
    brief)
      printf 'Re-invoke source skill %s with --more-detail flag\n' "$from"
      printf 'Read .claude/runtime/state/00-state.md for full prior context\n'
      printf 'Ask operator for elaboration if score < 60\n'
      ;;
    spec)
      printf 'Read full design doc referenced in content.intent\n'
      printf 'Cross-check inputs against DISCOVER report\n'
      ;;
    plan)
      printf 'Re-run /li:plan with smaller granularity\n'
      printf 'Read prior cycle CAPTURE for lessons\n'
      ;;
    *)
      printf 'Request additional context from source: %s\n' "$from"
      ;;
  esac
}

# ─── aggregate_evaluator_scores ────────────────────────────────────────────
# Args: name:json-result name:json-result ...
# Returns: minimum score across evaluators (worst evaluator wins).
aggregate_evaluator_scores() {
  local min=100
  for entry in "$@"; do
    local json="${entry#*:}"
    local score
    score=$(printf '%s' "$json" | grep -oE '"score"[[:space:]]*:[[:space:]]*[0-9]+' | head -1 | grep -oE '[0-9]+' | head -1)
    score="${score:-100}"
    if [ "$score" -lt "$min" ]; then
      min="$score"
    fi
  done
  printf '%d' "$min"
}

# ─── Self-test mode ────────────────────────────────────────────────────────
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "brief-forge.sh self-test:"
  tmp_content=$(mktemp)
  cat > "$tmp_content" <<'EOF'
task: Sample task for self-test
constraints:
  - no scope creep
acceptance:
  - reviewer surfaces specific concerns or APPROVES
EOF
  echo "--- HEAD ---"
  forge_envelope_head subagent_spawn plan PlanReviewer
  echo "--- BODY ---"
  forge_envelope_body brief "$tmp_content"
  echo "--- TAIL ---"
  forge_envelope_tail 85 "security:{\"score\":95}" "completeness:{\"score\":85}" "$(build_escape_hatches brief plan)" "/tmp/audit.jsonl"
  rm -f "$tmp_content"
fi
