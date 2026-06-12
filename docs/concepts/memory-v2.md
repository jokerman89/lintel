# Memory v2 — honest, mechanical, cheap

> Implements ADR-0006. Companion to the v5 `.claude/` home layout (ADR-0005).

## The contract

One memory home per repo: `.claude/memory/`. `MEMORY.md` is the index (≤200 lines — Claude
Code's native auto-memory loads it for free at session start, and writes there too via the
`autoMemoryDirectory` pointer). The other 7 CLIs get the same content through the
`session-digest` hook + the CLAUDE.md/AGENTS.md ritual. One store, two read paths, zero
duplication.

## What is mechanical (not prose)

| Mechanism | Implementation |
|---|---|
| Lesson surfacing (SENSE Step 0a) | `lib/memory.sh: lessons_surface` — grep-rank, supersede-aware, top-3 |
| Capture update-phase | `lessons_find_related` feeds add / update / supersede / no-op classification in CAPTURE Step 2 |
| Block budgets | `memory_budget_check` + `hooks/shared/memory-budget-warn` (MEMORY.md ≤200 lines; ≤30 active lessons, warn-only, 1/hour) |
| Checkpoint paths/discovery | `bin/_context.sh: context_save_path · context_list · context_latest` (content stays LLM-written) |
| Ready-work view | `bin/_jobs.sh: job_ready` + session-digest "ready in this repo: N" |
| Session digest | `hooks/shared/session-digest` (unchanged contract, v5 paths) |

## Conventions

- **Supersede, don't delete.** A contradicted lesson gets `superseded_by: L-NNN (YYYY-MM-DD)`
  as its first body line; surfacing skips it; git keeps the history. Never edit a lesson away.
- **Update before append.** CAPTURE classifies every candidate against existing lessons —
  append-only growth is the documented failure mode of file-based agent memory.
- **Path-scoped rules.** `.claude/rules/*.md` with `paths:` globs — loads only when relevant
  files are touched (native on Claude Code; digest-indexed elsewhere). Promote path-specific
  lessons here.
- **AGENTS.md pointer.** Scaffolded repos carry an AGENTS.md pointing at CLAUDE.md so every
  AGENTS.md-aware CLI finds the instructions natively.

## What was subtracted (and why)

- `operator-profile.jsonl` append (CAPTURE Step 9) — written, never read. Removed; the
  granularity calibration record is the real feedback loop.
- `context-snapshot`, `context-dump`, `context-warmup` skills — duplicates of save / restore /
  warm. Aliased (grace to 2026-09-12); `bin/_context.sh` is the shared core.
- Honest labels on gbrain (query loop not yet integrated) instead of implying integration.

## What stays deliberately simple

No embeddings, no database, no background consolidation daemon. The 2026 field evidence:
plain markdown + git + hooks is where surviving systems converged; semantic retrieval adds
infra cost without helping procedural memory (which is what lessons/ADRs are). If a corpus
ever outgrows grep, the proven retrofit is "files as source of truth, SQLite as disposable
index" — a later phase, on evidence.
