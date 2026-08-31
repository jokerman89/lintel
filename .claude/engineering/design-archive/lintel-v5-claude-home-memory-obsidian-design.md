# component: claude-home-memory-v2-obsidian
# implements: ADR-0005 (draft), ADR-0006 (draft), ADR-0007 (draft)
# intent: .claude/engineering/design-archive/lintel-v5-claude-home-memory-obsidian-design.md
# constraints: frozen zones — packs/_default/pack.yaml contract, frontmatter contracts, AGENT-INSTRUCTIONS.md
# last_intent_review: 2026-06-12

# Lintel v5.0 — `.claude/` home, memory v2, Obsidian integration

**Status:** APPROVED-DIRECTION (operator locked D1–D4 on 2026-06-12) — implementation pending cost gate.
**Mode:** meta-infra (Gates M1–M4 active).
**Builds on:** `feat/capture-vault-sink` (vault sink Step 7b, `.obsidian/` gitignore).

## Problem

Three operator-stated problems, one architecture:

1. **Spread.** Lintel writes to ~60+ locations: `.lintel/state/` (repo), the root trio
   (`plan.md`/`spec.md`/`prompt.md`), `tasks/`, `docs/adr/`, `docs/v4.x/`, plus 20+ directories
   under `~/.lintel/` (jobs, sessions, audit, analytics, runs). Everything Lintel generates for a
   repo should live in that repo's `.claude/` — one circle of control. `docs/` is reserved for
   genuine app documentation, written on demand.
2. **Memory promises vs reality.** The 2026-06-12 audit verdicts: session-digest hook, jobs system,
   00-state, audit writer, granularity calibration are **mechanical and real**. But `lessons-surface`
   (declared in SENSE Step 0a), the entire context-save/restore family (5 skills, zero bash),
   brief-forge evaluators, and operator-profile reads are **prose-only**. Some writes are dead
   (operator-profile.jsonl written, never read). The operator's suspicion ("bara på ytan?") is
   confirmed for those mechanisms.
3. **Obsidian.** The vault sink exists (write-only, privacy-gated). The operator wants Lintel to
   *benefit from* a user's Obsidian workflow and make Lintel's work visualizable (graph), without
   building only for Obsidian.

**Competitive grounding (research 2026-06-12):** the field converged on exactly Lintel's model —
plain markdown + git + hooks (Cursor removed opaque Memories; Anthropic's harness guidance is
files + context engineering). Database systems (mem0, Zep, claude-mem) do more at infra costs that
violate Lintel's constraints. **Urgent finding:** Claude Code's native auto-memory is default-ON
since v2.1.59 and already runs a second, uncoordinated memory store per repo. Table stakes Lintel
lacks: hook-based capture (not "remember to write"), scoped/conditional loading, an update-phase
on capture, AGENTS.md interop.

## Locked decisions (operator, 2026-06-12)

| # | Decision | Choice |
|---|---|---|
| D1 | Git policy for `.claude/` artifacts | **Split:** knowledge committed, runtime gitignored |
| D2 | Consolidation scope | **Everything Lintel-owned** → `.claude/` (incl. `tasks/*`, ADRs → `.claude/decisions/`) |
| D3 | Claude Code native auto-memory | **Converge:** point `autoMemoryDirectory` at repo-local `.claude/memory/` — one store |
| D4 | Obsidian ambition | **The 4 verified patterns, pack-gated; write-only stays** |

## Target layout (any Lintel-connected repo)

```
<repo>/.claude/
  settings.json           # committed — incl. autoMemoryDirectory → .claude/memory/ (D3)
  agents/                 # committed — scaffolded subagents (unchanged)
  rules/                  # committed — path-scoped rules (paths: frontmatter), NEW
  memory/                 # committed — the knowledge home (D1, D3)
    MEMORY.md             #   index, ≤200 lines (native auto-memory format → free load on CC)
    lessons.md            #   L-NNN durable rules        (was tasks/lessons.md)
    working-state.md      #   cross-session state        (was tasks/memory.md)
    personas.md           #   operator calibration       (was tasks/personas.md)
  decisions/              # committed — ADRs NNNN-*.md   (was docs/adr/)
  plans/                  # committed — cold-executor trios + todo
    todo.md               #   (was tasks/todo.md)
    <slug>/{plan,spec,prompt}.md
  runtime/                # GITIGNORED (one line: .claude/runtime/) — local backup suffices
    state/                #   (was .lintel/state/) 00-state.md, build-log, scope, reports
    sessions/             #   (was ~/.lintel/sessions/<branch>/) context-saves
    jobs/                 #   (was ~/.lintel/jobs/<id>/) repo-scoped job data
    audit/                #   (was ~/.lintel/audit/) repo-scoped event jsonl
```

**Stays in `~/.lintel/` (operator identity + cross-repo, NOT output):** packs/, profile.yaml,
roles/, brand/, config.yaml, browser-profiles/, global audit categories (pack-lifecycle,
cross-repo usage), transient generate/design run outputs. `~/.lintel/jobs/_active.md` becomes a
thin **cross-repo registry** (repo path + job id + status pointers); job data lives in-repo.

**Keystone — `lib/paths.sh`:** every path above is defined ONCE (shared schema discipline):
`lintel_memory_dir`, `lintel_decisions_dir`, `lintel_plans_dir`, `lintel_runtime_dir`,
`lintel_state_dir`, `lintel_jobs_dir`, `lintel_sessions_dir`, `lintel_audit_dir` — with
fallback to legacy paths during the grace window. Bash sources it; SKILL.md prose references the
canonical path map in CLAUDE.md/AGENT-INSTRUCTIONS.md. Never hardcode a path in two places again.

## Workstream A — `.claude/` home + migration

1. `lib/paths.sh` + shape test asserting no skill/hook/bin hardcodes a legacy path outside it.
2. `bin/li-migrate-claude-home` — idempotent, reversible: `git mv` knowledge files, create
   `runtime/`, update `.gitignore`, leave one-line redirect stubs at old paths (grace window per
   v4.x migration discipline), update `settings.json` (D3).
3. Sweep all ~60 write sites (L-005 discipline: widest token set — `tasks/lessons.md`,
   `tasks/memory.md`, `tasks/personas.md`, `tasks/todo.md`, `docs/adr`, `.lintel/state`,
   `~/.lintel/jobs`, `~/.lintel/sessions`, `~/.lintel/audit`, root-trio refs) across skills/,
   hooks/, lib/, bin/, agents/, scaffolding/, AGENT-INSTRUCTIONS.md, CLAUDE.md template.
4. `bin/_audit.sh` gains scope routing: repo events → `.claude/runtime/audit/`, operator-global →
   `~/.lintel/audit/`. `bin/_jobs.sh` writes job data in-repo + registry line globally.
5. session-digest hook reads new paths (with legacy fallback). li-doctor checks layout + warns on
   un-migrated repos. Scaffolding templates updated to install the new layout.
6. Run the migration on Lintel itself (dogfood, L-006). Gate M1 structure-changes entry +
   compatibility audit (M2) + shape tests (M3). ADR-0005.

## Workstream B — memory v2 (honest, mechanical, cheap)

**Convergence contract (D3).** `.claude/memory/MEMORY.md` is the ≤200-line index pointing into
lessons.md / working-state.md / personas.md / decisions/. On Claude Code, native auto-memory loads
it for free (and the agent maintains it natively); on the other 7 CLIs the session-digest hook +
AGENT-INSTRUCTIONS ritual cover the same read. One store, two read paths, zero duplication.

**Close the prose-only gaps (make mechanical or subtract):**

| Mechanism | Action |
|---|---|
| lessons-surface | **Implement** `lib/memory.sh: lessons_surface <keywords>` (grep-rank, top-3) — called mechanically from SENSE Step 0a |
| context-save family (8 skills) | **Consolidate to 3** (`context-save`, `context-restore`, `context-warm` + budget flag); implement `bin/_context.sh` (save/list/restore against `.claude/runtime/sessions/`); fold snapshot→save, dump→restore, budgetwatch already removed in v4.11 |
| brief-forge evaluators | **Honest scope:** implement the one cheap evaluator (completeness = field check vs envelope-schema.yaml in bash); delete the unimplemented evaluator promises from SKILL.md prose |
| operator-profile.jsonl | **Subtract** the dead write from CAPTURE Step 9 (granularity calibration already provides the real feedback loop) |
| context-budget | Keep advisory; surface one line in digest (no hard gate) |
| gbrain | Label honestly as opt-in/integration-pending in SKILL.md; no build |

**New conventions (the cheap steals from the field):**

1. **Update-phase capture** (mem0's good idea): CAPTURE Step 2 greps existing lessons first and
   classifies each candidate add / update / **supersede** / no-op — append-only bloat is the
   documented failure mode of file-based memory.
2. **Supersede-don't-delete** (Zep's bi-temporality, free): entries get
   `superseded_by: L-NNN (YYYY-MM-DD)` markers instead of edits; git holds ingestion history.
3. **Block budgets** (Letta/native-MEMORY.md pattern): MEMORY.md ≤200 lines hard; lessons.md gets
   a consolidation warning at threshold (warn-only hook).
4. **Path-scoped rules**: `.claude/rules/*.md` with `paths:` glob frontmatter — loads only when
   relevant files are touched on Claude Code; digest lists titles as index for other CLIs.
   Lessons that are path-specific get promoted into rules.
5. **AGENTS.md emission**: scaffold generates AGENTS.md (the Linux Foundation standard) alongside
   CLAUDE.md so the other 7 CLIs get instructions natively — serves the 8-CLI promise.
6. **Ready-work view** (beads' `bd prime`): digest shows open jobs *with blockers resolved*
   (`blocked_by:` field in job.yaml), not just a job list.

ADR-0006. The memory map table in CLAUDE.md/AGENT-INSTRUCTIONS is rewritten to the new single-home
model.

## Workstream C — Obsidian (pack-gated, write-only)

Config: extend the pack `capture.*`/new `obsidian.*` flat keys (two-level resolver limit respected).

1. **Locked frontmatter schema** for session notes: `type: session`, `date`, `repo`, `branch`,
   `outcome` (controlled vocabulary), `tags` — flat typed properties (Bases-compatible).
2. **`sessions.base`** shipped in Lintel (`templates/obsidian/`), installed by new
   `bin/li-vault-init` together with a `<repo>` hub note — sortable session dashboard in-app,
   `obsidian base:query --format=json` for agents later.
3. **Index + wikilinks in CAPTURE Step 7b:** regenerate `50-sessions/00-index.md` (last N,
   one wikilinked line each); each note links `[[<repo-hub>]]` + predecessor session. Backlinks
   give per-repo session history; the graph comes free — we build nothing graph-specific.
4. **Repo as read-vault:** already enabled (`.obsidian/` gitignored). D2 makes `<repo>/.claude/`
   itself a mini-vault — lessons/decisions/plans are wikilink-friendly markdown; document the
   "open repo in Obsidian" workflow in docs/concepts/.

**Deliberately skipped** (research-validated): vault read path into SENSE (token pain), canvas
generation, Smart Connections/Copilot, weekly-rollup skill (the operator's vault already has
`weekly-review`; Lintel's job is well-formed notes, not duplicate synthesis). ADR-0007.

## Phasing and estimates

| Phase | Content | PR | Est |
|---|---|---|---|
| A | layout + lib/paths.sh + migration tool + sweep + dogfood on Lintel | feat/claude-home | ~60–100k tokens |
| B | memory v2 (convergence, mechanical helpers, subtractions, conventions) | feat/memory-v2 | ~80–120k |
| C | Obsidian patterns (schema, base, vault-init, index, wikilinks) | feat/obsidian-patterns | ~40–60k |

Within meta-infra envelope (600k soft). Each phase: shape+unit tests green locally before push,
Gate M1 entry per structural change, M2 compat audit (RED expected on path moves → migration doc +
grace-window stubs), M3 shape tests updated, M4 migration index entry.

## Risks

- **Path sweep misses callsites** → L-005 widest-token-set sweep + legacy fallback in lib/paths.sh
  + shape test greps for stragglers.
- **Cross-repo jobs view breaks** → registry pattern keeps `_active.md` as index; `/li:resume`
  reads registry then repo data.
- **Native auto-memory format drift** (Anthropic changes conventions) → MEMORY.md stays valid
  plain markdown regardless; convergence is a settings pointer, reversible.
- **Vault-sink branch unmerged** → Phase A branches off `feat/capture-vault-sink`; its PR goes
  first.
