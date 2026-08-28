#!/usr/bin/env bash
# component: lintel-paths
# implements: ADR-0005
# intent: .claude/engineering/design-archive/lintel-v5-claude-home-memory-obsidian-design.md
# constraints: frozen zone — ~30 skills + bin tools resolve paths through this contract
# last_intent_review: 2026-06-12
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
#   <repo>/.claude/runtime/     GITIGNORED — state/, sessions/, jobs/, audit/
# Operator identity stays in ~/.lintel (packs, profile.yaml, roles, brand, config)
# — identity is configuration, not output.
#
# Migration marker: <repo>/.claude/lintel-layout.yaml (layout_version: 5).
# Un-migrated repos resolve to the legacy locations until bin/li-migrate-claude-home
# runs — grace window to 2026-09-12, then legacy fallback is removed.

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"

lintel_repo_root() {
  printf '%s' "${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}"
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
           lintel_sessions_dir lintel_repo_jobs_dir; do
    printf '  %-28s %s\n' "$f" "$($f)"
  done
fi
