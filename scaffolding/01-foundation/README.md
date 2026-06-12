# Layer 1 — Foundation

The load-bearing layer. Every Lintel-scaffolded repo gets this. Every harness, every skill, every agent runs on top of it.

## What lives here

- **`CORE-PRINCIPLES.md`** — 10 load-bearing rules (Boris-style). Plan before code. Subagents for parallel work. Self-improvement loop. Verify before done. Deviation flagging. Auto-mode bounds. Cleanup when bound is crossed. Shared schema discipline. Simplicity first. Documented change beats silent change.
- **`EVOLUTION.md`** — process for changing scaffolding. Three change types: per-repo adaptation (free), template change (logged), core-principle change (requires explicit decision).
- **`EVOLUTION-LOG.md`** — changelog for scaffolding evolution. Most recent first.
- **`CLAUDE.md.template`** — Boris-style per-repo CLAUDE.md template. `scaffold-repo.sh` drops this into a target repo's root and operator fills the `<!-- PROJECT:START -->` blocks.
- **`.claude/memory/`** — `lessons.md` (corrections compound), `working-state.md` (long-running state), `personas.md` (operator calibration), `personas-example.md` (reference persona format).
- **`.claude/plans/`** — `todo.md` (ephemeral per-task).
- **`.claude/decisions/`** — decision-record (ADR) README + numbered template.
- **`.claude/agents/`** — 4 baseline subagents (ReadOnly, CodeReviewer, TestRunner, SanityChecker).
- **`.claude/SUBAGENT-GUIDE.md`** — how to add new subagents.

## Change rate

**Stable.** Changes go through `EVOLUTION.md`'s process. A change to `CORE-PRINCIPLES.md` is a CORE change — requires explicit decision + logged in `EVOLUTION-LOG.md`.

## Why this layer exists

Without it, every harness and skill operates against a blank slate. With it, Lintel — and any other harness the operator runs — sits on stable principles.

The cost of having scaffolding is one-time setup. The cost of not having it is rediscovery every session.

## Provenance

`CORE-PRINCIPLES.md` + `EVOLUTION.md` + `EVOLUTION-LOG.md` + `tasks/lessons.md` shape + ADR pattern + Boris CLAUDE.md template = inspired by the operator's pre-existing `claude-scaffolding/` work (Boris-style discipline). Lintel v1 preserves this layer AS-IS — it predates the 4-layer architecture and is the foundation everything else sits on.
