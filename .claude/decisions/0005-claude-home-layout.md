# ADR-0005: the .claude/ home layout — one circle of control per repo

**Status:** Accepted (2026-06-12)
**Decided by:** operator (D1–D4 gate, 2026-06-12) + implementation session
**Implements:** docs/design/lintel-v5-claude-home-memory-obsidian-design.md (workstream A)

## Context

Lintel wrote artifacts to ~60+ locations: `.lintel/state/` (repo), the root trio
`plan.md`/`spec.md`/`prompt.md`, `tasks/`, `docs/adr/`, plus 20+ directories under `~/.lintel/`
(jobs, sessions, audit, analytics). The operator's call: everything Lintel generates FOR a repo
belongs IN that repo, under `.claude/` — one circle of control, visualizable, clone-portable.
Simultaneously, Claude Code's native auto-memory (default-on since v2.1.59) writes a second,
uncoordinated memory store per repo under `~/.claude/projects/<slug>/memory/` — two memory
systems with no contract.

## Decision

1. **Layout** (D2): repo-scoped Lintel output consolidates under `<repo>/.claude/`:
   - committed knowledge: `memory/` (MEMORY.md index + lessons.md + working-state.md +
     personas.md), `decisions/` (ADRs), `plans/` (todo.md + `<slug>/{plan,spec,prompt}.md` trios)
   - gitignored runtime: `runtime/{state,sessions,jobs,audit}/` (one .gitignore line)
2. **Git policy** (D1): knowledge committed, runtime local-only ("backup räcker lokalt" applies to
   runtime; knowledge compounds via git).
3. **Native auto-memory convergence** (D3): `autoMemoryDirectory` points at the repo's
   `.claude/memory/` so native auto-memory and Lintel share ONE store. The key only accepts
   absolute paths → the pointer lives in `.claude/settings.local.json` (machine-local), written by
   `bin/li-migrate-claude-home` and verified/repaired by `li-doctor`. MEMORY.md (≤200 lines) is
   the index; Claude Code auto-loads it natively, the session-digest hook covers the other CLIs.
4. **Identity stays global**: `~/.lintel/{packs,profile.yaml,roles,brand,config.yaml,hooks,
   compliance}` is operator configuration, not output. Transient deliverables
   (`~/.lintel/*-runs/`, `draft/`) also stay out of repos.
5. **Jobs registry pattern**: job data lives in `.claude/runtime/jobs/`; `~/.lintel/jobs/_active.md`
   becomes a thin cross-repo registry (one pointer line per open job) so `/li:resume`'s
   "what's open anywhere" view survives.
6. **Audit scope routing**: `bin/_audit.sh` routes repo-work categories to
   `.claude/runtime/audit/`; operator categories (pack-lifecycle, pack-resolver, migration(s),
   usage-*) stay in `~/.lintel/audit/`. The former `~/.lintel/analytics/` files fold into the
   repo audit dir (subtraction: one runtime sink).
7. **Single path source**: `lib/paths.sh` defines every location once; bash sources it, prose
   states the canonical paths. The migration marker `.claude/lintel-layout.yaml`
   (`layout_version: 5`) switches resolution; un-migrated repos fall back to legacy paths until
   the grace window closes (2026-09-12).

## Consequences

- `bin/li-migrate-claude-home` migrates any repo idempotently (git mv + redirect stubs +
  .gitignore + MEMORY.md seed + auto-memory pointer + marker). Lintel itself is migrated (L-006).
- `li-scaffold` installs the v5 layout from birth; templates moved to
  `scaffolding/01-foundation/.claude/`.
- ~195 files of skills/agents/hooks/tests/docs prose updated to the new canonical paths
  (L-005 widest-token-set sweep). `tests/shape/claude-home-paths.sh` guards against regression.
- Repos become self-contained: clone → knowledge arrives; open in Obsidian → `.claude/` is a
  readable mini-vault (workstream C builds on this).
- Cross-machine job/session data no longer syncs via `~/.lintel` (it never really did); the
  registry keeps the cross-repo view.
- Risk accepted: two read paths during the grace window (new + legacy fallback); removed after
  2026-09-12.
