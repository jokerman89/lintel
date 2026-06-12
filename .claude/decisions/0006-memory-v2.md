# ADR-0006: memory v2 — mechanical-or-subtracted

**Status:** Accepted (2026-06-12)
**Decided by:** operator (D3 convergence + "allt vi lovar ska vara på riktigt" directive) + implementation session
**Implements:** docs/design/lintel-v5-claude-home-memory-obsidian-design.md (workstream B)

## Context

The 2026-06-12 memory audit split Lintel's memory promises into REAL (session-digest, jobs,
00-state, audit writer, granularity calibration) and PROSE-ONLY (lessons-surface declared in
SENSE but unimplemented; the context-save family with zero bash; operator-profile written but
never read). Competitive research showed the field converged on Lintel's file-based model, and
identified the cheap table-stakes Lintel lacked: hook-based capture, an update-phase, scoped
loading, AGENTS.md interop. Claude Code's native auto-memory (default-on) had no contract with
Lintel's memory.

## Decision

Every memory promise becomes **mechanical or subtracted** — nothing stays prose-only:

1. **Convergence**: `.claude/memory/MEMORY.md` is the single index; native auto-memory reads
   and writes it (ADR-0005's `autoMemoryDirectory` pointer); session-digest covers other CLIs.
2. **Mechanical**: `lib/memory.sh` (lessons_surface / lessons_find_related / lessons_count /
   memory_budget_check), `bin/_context.sh` (checkpoint paths + discovery),
   `hooks/shared/memory-budget-warn` (block budgets, warn-only), `job_ready` + digest
   ready-work view.
3. **Conventions**: supersede-don't-delete (`superseded_by:` markers — Zep's bi-temporality in
   plain markdown); update-before-append in CAPTURE (mem0's update-phase); path-scoped rules in
   `.claude/rules/` (the four-mode loading pattern); AGENTS.md pointer emission in scaffold.
4. **Subtractions**: operator-profile.jsonl append (dead write); context-snapshot/dump/warmup
   skills (duplicates — aliased to save/restore/warm, grace to 2026-09-12); over-claiming gbrain
   prose (now honestly labeled "query loop not integrated").
5. **Not building**: embeddings, databases, consolidation daemons — the field's evidence says
   they don't pay for procedural memory at Lintel's scale. Revisit only on grep-scaling pain.

## Consequences

- SENSE Step 0a now has a real implementation to call; silent-skip risk drops to "didn't run
  the helper" (auditable) instead of "prose ignored" (invisible).
- Lessons stay sharp under growth: budgets warn, supersede markers keep surfacing relevant,
  CAPTURE classifies instead of appending.
- 3 fewer skills (169 → 166); alias grace window to 2026-09-12.
- bin/_context.sh + lib/memory.sh join lib/paths.sh in the handle-with-care helper contract (listed in CLAUDE.md frozen zones; pinned by tests/unit/memory-v2.sh + tests/shape/claude-home-paths.sh).
- Concept doc: docs/concepts/memory-v2.md. Structure change: docs/v4.x/structure-changes/2026-06-12-memory-v2.md.
