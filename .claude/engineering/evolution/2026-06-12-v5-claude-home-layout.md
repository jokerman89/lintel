---
slug: v5-claude-home-layout
date: 2026-06-12
cycle_id: claude-home-20260612
operator: jokerman
affected_paths:
  - lib/paths.sh
  - bin/_audit.sh
  - bin/_jobs.sh
  - bin/li-migrate-claude-home
  - bin/li-scaffold
  - bin/li-doctor
  - hooks/shared/session-digest/run.sh
  - hooks/shared/job-end/run.sh
  - scaffolding/01-foundation/.claude/
  - skills/ (~100 SKILL.md path updates)
  - tests/ (fixtures + expected strings)
risk_class: high
breaking_change: true
---

# Structure change: v5-claude-home-layout

> Gate M1 (structure-impact analysis) artifact — ADR-0005.

## What changed (shape)

Repo-scoped Lintel output moved from scattered locations into `<repo>/.claude/`:

| Old | New | Git |
|---|---|---|
| `tasks/lessons.md` | `.claude/memory/lessons.md` | committed |
| `tasks/memory.md` | `.claude/memory/working-state.md` | committed |
| `tasks/personas.md` | `.claude/memory/personas.md` | committed |
| `tasks/todo.md` | `.claude/plans/todo.md` | committed |
| `docs/adr/` | `.claude/decisions/` | committed |
| `docs/plans/<slug>/` (trio) | `.claude/plans/<slug>/` | committed |
| `.lintel/state/` | `.claude/runtime/state/` | ignored |
| `~/.lintel/sessions/` (context saves) | `.claude/runtime/sessions/` | ignored |
| `~/.lintel/jobs/<id>/` | `.claude/runtime/jobs/<id>/` | ignored |
| `~/.lintel/audit/<repo-cat>.jsonl` | `.claude/runtime/audit/` | ignored |
| `~/.lintel/analytics/` | `.claude/runtime/audit/` | ignored |
| `~/.lintel/retros/` | `.claude/memory/retros/` | committed |

New artifacts: `lib/paths.sh` (single path source), `.claude/lintel-layout.yaml` (migration
marker, `layout_version: 5`), `bin/li-migrate-claude-home`, MEMORY.md index seed,
`autoMemoryDirectory` pointer in `.claude/settings.local.json` (native auto-memory convergence),
`~/.lintel/jobs/_active.md` re-purposed as cross-repo registry.

## Backward-compat

Un-migrated repos (no layout marker) keep working unchanged: `lib/paths.sh`, `bin/_audit.sh`,
`bin/_jobs.sh`, session-digest, cycle-footer, job-end and the review/granularity readers all
resolve new-path-then-legacy. Explicit env overrides (`LINTEL_JOBS_DIR`, `LINTEL_AUDIT_DIR`)
still win (test seam preserved).

## Migration path

`bin/li-migrate-claude-home [--dry-run]` — idempotent, git-mv-based, leaves one-line redirect
stubs at old paths. Grace window for legacy fallback: until **2026-09-12**. Indexed in
`docs/migrations/_INDEX.md`.

## Forward-compat

All future skills/hooks reference `lib/paths.sh` functions (bash) or the canonical paths in
CLAUDE.md's memory map (prose). `tests/shape/claude-home-paths.sh` fails CI on new unguarded
legacy paths in bash tooling and on a missing layout marker in this repo.

## Verification

- `tests/shape/claude-home-paths.sh` ALL PASS (19 checks) — incl. dogfood marker on this repo
- unit 37/37, integration + e2e green post-sweep (see PR run)
- `bin/li-migrate-claude-home --dry-run` then real run on this repo: clean `git status`, only
  expected renames + stubs

## Rollback

`git revert` the layout commits; the migration tool's moves are plain git renames (reversible);
delete `.claude/lintel-layout.yaml` to re-activate legacy resolution everywhere.
