#!/usr/bin/env bash
# component: lintel-paths
# implements: ADR-0005, ADR-0038
# intent: .claude/engineering/design-archive/lintel-v5-claude-home-memory-obsidian-design.md
# constraints: frozen zone — ~30 skills + bin tools resolve paths through this contract
# last_intent_review: 2026-09-28
#
# lib/paths.sh — single source of truth for where Lintel reads and writes.
# Sourced by bin tools, hooks and lib helpers. SKILL.md prose references the
# same layout via the path map in CLAUDE.md / AGENT-INSTRUCTIONS.md.
#
# v5 layout (one circle of control per repo):
#   <repo>/.claude/memory/      committed knowledge — MEMORY.md index, lessons.md,
#                               working-state.md, personas.md
#   <repo>/.claude/decisions/   committed ADRs (NNNN-*.md)
#   <repo>/.claude/plans/       committed plans — todo.md, <slug>/{plan,spec,prompt}.md
#   <repo>/.claude/patterns/    committed reusable-pattern catalog + bindings (ADR-0038)
#   <repo>/.claude/runtime/     GITIGNORED — state/, sessions/, jobs/, audit/, patterns/<run-id>/
# Operator identity stays in ~/.lintel (packs, profile.yaml, roles, brand, config)
# — identity is configuration, not output.
#
# Migration marker: <repo>/.claude/lintel-layout.yaml (layout_version: 5).
# Un-migrated repos resolve to the legacy locations until bin/li-migrate-claude-home
# runs — grace window to 2026-09-12, then legacy fallback is removed.

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"

lintel_repo_root() {
  local root
  root="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}"
  # Git for Windows returns C:/... paths; the shell's writable temp mount is
  # /tmp/... and must remain in that namespace for mkdir/redirection to agree.
  case "$root" in
    [A-Za-z]:*)
      if command -v cygpath >/dev/null 2>&1; then root="$(cygpath -u "$root")" || return 1; fi ;;
  esac
  printf '%s' "$root"
}

# A repo is "migrated" when the layout marker declares layout_version >= 5.
lintel_layout_migrated() { # [root] → rc 0 if v5 layout
  local root="${1:-$(lintel_repo_root)}"
  [ -n "$root" ] || return 1
  [ -f "$root/.claude/lintel-layout.yaml" ] || return 1
  local v
  v=$(grep -E '^layout_version:' "$root/.claude/lintel-layout.yaml" 2>/dev/null \
      | head -1 | awk '{print $2}' | tr -d '\r')
  [ "${v:-0}" -ge 5 ] 2>/dev/null
}

# Outside a git repo there IS no repo home — every repo-scoped function
# returns empty + rc 1 rather than a filesystem-root path like /.claude/.
_lintel_require_root() {
  [ -n "$(lintel_repo_root)" ]
}

# Resolution rule: migrated repo → new path, always. Un-migrated repo → legacy
# path if it exists, else new path (fresh repos get the v5 layout by default).
_lintel_pick() { # <new> <legacy>
  local new="$1" legacy="$2"
  if lintel_layout_migrated; then printf '%s' "$new"; return; fi
  if [ -e "$legacy" ]; then printf '%s' "$legacy"; else printf '%s' "$new"; fi
}

# ── repo-scoped: committed knowledge ─────────────────────────────────────────
lintel_claude_dir()    { _lintel_require_root || return 1; printf '%s/.claude' "$(lintel_repo_root)"; }
lintel_memory_dir()    { _lintel_require_root || return 1; local r; r=$(lintel_repo_root); _lintel_pick "$r/.claude/memory" "$r/tasks"; }
lintel_memory_index()  { _lintel_require_root || return 1; printf '%s/.claude/memory/MEMORY.md' "$(lintel_repo_root)"; }
lintel_lessons_file()  { _lintel_require_root || return 1; local r; r=$(lintel_repo_root); _lintel_pick "$r/.claude/memory/lessons.md" "$r/tasks/lessons.md"; }
lintel_working_state_file() { _lintel_require_root || return 1; local r; r=$(lintel_repo_root); _lintel_pick "$r/.claude/memory/working-state.md" "$r/tasks/memory.md"; }
lintel_personas_file() { _lintel_require_root || return 1; local r; r=$(lintel_repo_root); _lintel_pick "$r/.claude/memory/personas.md" "$r/tasks/personas.md"; }
lintel_decisions_dir() { _lintel_require_root || return 1; local r; r=$(lintel_repo_root); _lintel_pick "$r/.claude/decisions" "$r/docs/adr"; }
lintel_plans_dir()     { _lintel_require_root || return 1; printf '%s/.claude/plans' "$(lintel_repo_root)"; }
lintel_todo_file()     { _lintel_require_root || return 1; local r; r=$(lintel_repo_root); _lintel_pick "$r/.claude/plans/todo.md" "$r/tasks/todo.md"; }

# ── repo-scoped: gitignored runtime ──────────────────────────────────────────
lintel_runtime_dir()   { _lintel_require_root || return 1; printf '%s/.claude/runtime' "$(lintel_repo_root)"; }
lintel_state_dir()     { _lintel_require_root || return 1; local r; r=$(lintel_repo_root); _lintel_pick "$r/.claude/runtime/state" "$r/.lintel/state"; }
lintel_sessions_dir()  { _lintel_require_root || return 1; local r; r=$(lintel_repo_root); _lintel_pick "$r/.claude/runtime/sessions" "$LINTEL_HOME/sessions"; }
lintel_repo_audit_dir(){ _lintel_require_root || return 1; printf '%s/.claude/runtime/audit' "$(lintel_repo_root)"; }
lintel_repo_jobs_dir() { _lintel_require_root || return 1; local r; r=$(lintel_repo_root); _lintel_pick "$r/.claude/runtime/jobs" "$LINTEL_HOME/jobs"; }

# ── repo-scoped: reusable patterns (ADR-0038) ────────────────────────────────
# No legacy location exists. Personal patterns live in $LINTEL_HOME/patterns and
# are derived by lib/patterns.py from the roots envelope, never from these helpers.
lintel_patterns_dir()  { _lintel_require_root || return 1; printf '%s/.claude/patterns' "$(lintel_repo_root)"; }
# Scratch output is addressed by an explicit run ID, never by latest-mtime lookup.
# Run IDs follow the core's portable segment rules (no dot/dash lead, "..",
# trailing dot or Windows device name); the refusal never echoes the raw input.
_lintel_pattern_run_id_ok() {
  case "$1" in
    ''|.*|-*|*..*|*.|*[!A-Za-z0-9._-]*) return 1 ;;
  esac
  [ "${#1}" -le 128 ] || return 1
  case "${1%%.*}" in
    [Cc][Oo][Nn]|[Pp][Rr][Nn]|[Aa][Uu][Xx]|[Nn][Uu][Ll]|[Cc][Oo][Mm][1-9]|[Ll][Pp][Tt][1-9]) return 1 ;;
  esac
}
lintel_pattern_runtime_dir() { # [run-id] → base dir, or the run's dir
  _lintel_require_root || return 1
  local base
  base="$(lintel_repo_root)/.claude/runtime/patterns"
  if [ "$#" -eq 0 ]; then printf '%s' "$base"; return 0; fi
  _lintel_pattern_run_id_ok "$1" || {
    printf '[lintel/paths] invalid pattern run ID: use 1-128 of A-Z a-z 0-9 . _ -, no leading dot or dash, no "..", trailing dot or device name\n' >&2
    return 2
  }
  printf '%s/%s' "$base" "$1"
}

# ── operator-global (identity + cross-repo registry — unchanged in v5) ───────
lintel_global_audit_dir() { printf '%s/audit' "$LINTEL_HOME"; }
lintel_jobs_registry()    { printf '%s/jobs/_active.md' "$LINTEL_HOME"; }
lintel_profile_file()     { printf '%s/profile.yaml' "$LINTEL_HOME"; }

# Self-test
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "lib/paths.sh self-test (repo: $(lintel_repo_root)):"
  if lintel_layout_migrated; then echo "  layout: v5 (migrated)"; else echo "  layout: legacy (un-migrated)"; fi
  for f in lintel_lessons_file lintel_working_state_file lintel_personas_file \
           lintel_decisions_dir lintel_todo_file lintel_state_dir \
           lintel_sessions_dir lintel_repo_jobs_dir lintel_patterns_dir \
           lintel_pattern_runtime_dir; do
    printf '  %-28s %s\n' "$f" "$($f)"
  done
fi
