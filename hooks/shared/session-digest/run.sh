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

# Recent lessons (last 3 ## L-NNN headers)
if [ -n "$REPO_ROOT" ] && [ -f "$REPO_ROOT/tasks/lessons.md" ]; then
  les="$(grep -E '^## L-[0-9]' "$REPO_ROOT/tasks/lessons.md" 2>/dev/null | tail -3 \
        | sed -E 's/^## //; s/ — / /' | paste -sd '|' - | sed 's/|/ · /g')"
  [ -n "$les" ] && add "Recent lessons: $les"
fi

# Memory highlights (first 2 non-blank, non-comment, non-heading content lines)
if [ -n "$REPO_ROOT" ] && [ -f "$REPO_ROOT/tasks/memory.md" ]; then
  mem="$(grep -vE '^\s*$|^\s*#|^\s*<!--|^---' "$REPO_ROOT/tasks/memory.md" 2>/dev/null \
        | head -2 | sed 's/^[[:space:]]*//' | paste -sd '|' - | sed 's/|/ · /g' | cut -c1-200)"
  [ -n "$mem" ] && add "Memory: $mem"
fi

# Open jobs
if [ -f "$LINTEL_HOME/jobs/_active.md" ]; then
  jc="$(grep -cE '^\s*[-*|] ' "$LINTEL_HOME/jobs/_active.md" 2>/dev/null || echo 0)"
  [ "${jc:-0}" -gt 0 ] 2>/dev/null && add "Open jobs: $jc (see ~/.lintel/jobs/_active.md)"
fi

# Recent decisions (last 3 ADR titles)
if [ -n "$REPO_ROOT" ] && [ -d "$REPO_ROOT/docs/adr" ]; then
  adrs="$(grep -hE '^# ADR-[0-9]' "$REPO_ROOT"/docs/adr/[0-9]*.md 2>/dev/null | tail -3 \
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

digest="LINTEL SESSION DIGEST (auto-loaded · tasks/lessons.md, tasks/memory.md, docs/adr/ for detail)
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
