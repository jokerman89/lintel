#!/usr/bin/env bash
# session-digest — Lintel SessionStart hook (v4.8, ADR-0002)
# Injects a compact memory digest into a fresh Claude Code session.
# Fail-open: any error or empty digest → exit 0 with no output (never blocks a session).

set -uo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"

# Operator override
[ -f "$LINTEL_HOME/.digest-disabled" ] && exit 0
[ -n "${NO_DIGEST:-}" ] && exit 0

# Repo root (for tasks/, docs/). Outside a repo → still emit profile/jobs.
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"

PROFILE="$LINTEL_HOME/profile.yaml"

# ── helpers ──────────────────────────────────────────────────────────────────
_yaml() { # _yaml <file> <key>  → scalar value or empty
  [ -f "$1" ] || return 0
  grep -E "^[[:space:]]*$2:" "$1" 2>/dev/null | head -1 \
    | sed -E "s/^[[:space:]]*$2:[[:space:]]*//; s/[[:space:]]*#.*$//" | tr -d '"' | tr -d "'" \
    | sed 's/[[:space:]]*$//'
}

# ── gather (each section optional) ───────────────────────────────────────────
lines=""
add() { lines="${lines}$1"$'\n'; }

# Identity from profile (+ optional compliance.mode via pack-resolver)
pack="$(_yaml "$PROFILE" active_pack)";    pack="${pack:-_default}"
mode="$(_yaml "$PROFILE" default_mode)";   mode="${mode:-internal-tool}"
role="$(_yaml "$PROFILE" role_active)";    role="${role:-none}"
compliance=""
_resolver="${REPO_ROOT:-$LINTEL_HOME}/lib/pack-resolver.sh"
[ -f "$_resolver" ] || _resolver="$LINTEL_HOME/lib/pack-resolver.sh"
if [ -f "$_resolver" ]; then
  compliance="$( ( source "$_resolver" 2>/dev/null && resolve_pack_field compliance.mode 2>/dev/null ) | tr -d '[:space:]' )"
fi
[ -n "$compliance" ] && compliance=" · compliance: $compliance"
add "Pack: ${pack} · mode: ${mode} · role: ${role}${compliance}"

# v5 layout (ADR-0005): knowledge lives in .claude/; legacy paths are the
# pre-migration fallback (grace window to 2026-09-12).
_first_existing() { for p in "$@"; do [ -e "$p" ] && { printf '%s' "$p"; return; }; done; }
LESSONS_FILE=""; MEMORY_FILE=""; DECISIONS_DIR=""
if [ -n "$REPO_ROOT" ]; then
  LESSONS_FILE="$(_first_existing "$REPO_ROOT/.claude/memory/lessons.md" "$REPO_ROOT/tasks/lessons.md")"
  MEMORY_FILE="$(_first_existing "$REPO_ROOT/.claude/memory/working-state.md" "$REPO_ROOT/tasks/memory.md")"
  DECISIONS_DIR="$(_first_existing "$REPO_ROOT/.claude/decisions" "$REPO_ROOT/docs/adr")"
fi

# Recent lessons (last 3 ## L-NNN headers)
if [ -n "$LESSONS_FILE" ]; then
  les="$(grep -E '^## L-[0-9]' "$LESSONS_FILE" 2>/dev/null | tail -3 \
        | sed -E 's/^## //; s/ — / /' | paste -sd '|' - | sed 's/|/ · /g')"
  [ -n "$les" ] && add "Recent lessons: $les"
fi

# Memory highlights (first 2 non-blank, non-comment, non-heading content lines)
if [ -n "$MEMORY_FILE" ]; then
  mem="$(grep -vE '^\s*$|^\s*#|^\s*<!--|^---' "$MEMORY_FILE" 2>/dev/null \
        | head -2 | sed 's/^[[:space:]]*//' | paste -sd '|' - | sed 's/|/ · /g' | cut -c1-200)"
  [ -n "$mem" ] && add "Memory: $mem"
fi

# Open jobs (registry = cross-repo view) + ready-work for THIS repo (ADR-0006)
if [ -f "$LINTEL_HOME/jobs/_active.md" ]; then
  jc="$(grep -cE '^\s*[-*|] ' "$LINTEL_HOME/jobs/_active.md" 2>/dev/null || echo 0)"
  ready=""
  _jobs_helper="${REPO_ROOT:-.}/bin/_jobs.sh"
  [ -f "$_jobs_helper" ] || _jobs_helper="$LINTEL_HOME/scaffolding/bin/_jobs.sh"
  if [ -n "$REPO_ROOT" ] && [ -f "$REPO_ROOT/.claude/lintel-layout.yaml" ] && [ -f "$_jobs_helper" ]; then
    ready="$( (
      # shellcheck disable=SC1090
      source "$_jobs_helper" 2>/dev/null || exit 0
      r=0
      for d in "$LINTEL_JOBS_DIR"/*/; do
        [ -f "$d/job.yaml" ] || continue
        id=$(grep '^job_id:' "$d/job.yaml" | head -1 | awk '{print $2}')
        [ "$(job_ready "$id" 2>/dev/null)" = "yes" ] && r=$((r+1))
      done
      printf '%s' "$r"
    ) 2>/dev/null )"
  fi
  if [ "${jc:-0}" -gt 0 ] 2>/dev/null; then
    line="Open jobs: $jc (registry: ~/.lintel/jobs/_active.md)"
    [ -n "$ready" ] && line="$line · ready in this repo: $ready"
    add "$line"
  fi
fi

# Path-scoped rules index (.claude/rules/*.md — loaded natively by Claude Code,
# listed here as an index for the other CLIs)
if [ -n "$REPO_ROOT" ] && [ -d "$REPO_ROOT/.claude/rules" ]; then
  rl="$(ls "$REPO_ROOT/.claude/rules"/*.md 2>/dev/null | head -5 | while IFS= read -r f; do basename "$f" .md; done | paste -sd '|' - | sed 's/|/ · /g')"
  [ -n "$rl" ] && add "Path-scoped rules: $rl (.claude/rules/)"
fi

# Recent decisions (last 3 ADR titles)
if [ -n "$DECISIONS_DIR" ] && [ -d "$DECISIONS_DIR" ]; then
  adrs="$(grep -hE '^# ADR-[0-9]' "$DECISIONS_DIR"/[0-9]*.md 2>/dev/null | tail -3 \
         | sed -E 's/^# (ADR-[0-9]+): /\1 /' | paste -sd '|' - | sed 's/|/ · /g')"
  [ -n "$adrs" ] && add "Recent decisions: $adrs"
fi

# Pending migrations
if [ -n "$REPO_ROOT" ] && [ -d "$REPO_ROOT/docs/v4.x/migrations" ]; then
  mig="$(find "$REPO_ROOT/docs/v4.x/migrations" -maxdepth 1 -name '*.md' ! -name '_*' 2>/dev/null | wc -l | tr -d ' ')"
  [ "${mig:-0}" -gt 0 ] 2>/dev/null && add "Pending migrations: $mig (see docs/v4.x/migrations/)"
fi

# Nothing but the identity line and no repo context? Still worth emitting identity.
[ -z "$lines" ] && exit 0

# Repo-relative paths in the header (readability)
_rel() { printf '%s' "${1#"$REPO_ROOT"/}"; }
digest="LINTEL SESSION DIGEST (auto-loaded · $(_rel "${LESSONS_FILE:-.claude/memory/lessons.md}"), $(_rel "${MEMORY_FILE:-.claude/memory/working-state.md}"), $(_rel "${DECISIONS_DIR:-.claude/decisions}") for detail)
${lines}"

# ── audit (best-effort, via the unified writer — keeps stdout clean for the envelope) ──
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh" 2>/dev/null || true
audit_log "hooks" "session_digest" "hook=session-digest" "pack=$pack" "mode=$mode" >/dev/null 2>&1 || true

# ── emit SessionStart envelope ───────────────────────────────────────────────
if command -v jq >/dev/null 2>&1; then
  jq -nc --arg c "$digest" '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$c}}'
else
  # Portable JSON escape (\, ", newline, tab, CR)
  esc="$(printf '%s' "$digest" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | awk 'BEGIN{ORS="\\n"} {print}' | sed 's/\\n$//')"
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$esc"
fi
exit 0
