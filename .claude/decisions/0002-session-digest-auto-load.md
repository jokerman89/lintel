# ADR-0002: Session-digest hook auto-loads Lintel's memory snowball

- **Status:** Accepted
- **Date:** 2026-06-05
- **Deciders:** jokerman89 (operator)
- **Supersedes:** —
- **Superseded by:** —

## Context

Lintel stores a rich memory + capability system, but Claude Code only auto-loads a subset of it.
Auto-loaded: `CLAUDE.md`, skill names + descriptions, `.claude/agents/`, and hooks. NOT
auto-loaded: `tasks/lessons.md`, `tasks/memory.md`, `tasks/personas.md`, `~/.lintel/profile.yaml`,
`.lintel/state/`, `docs/adr/`. Those are plain files — read only if `CLAUDE.md` instructs, a hook
injects, or the user asks.

The consequence: the snowball never compounded. Lessons accumulated in `tasks/lessons.md` but never
reached a fresh session unless someone explicitly read the file. The operator's global memory does
not have this problem because the harness injects a `MEMORY.md` index into every session. Lintel had
no equivalent. The `/office-hours` design
([.claude/engineering/design-archive/claude-md-capability-and-memory-surfacing.md](../design/claude-md-capability-and-memory-surfacing.md))
established that the fix must be **mechanical** (inject), not a soft `CLAUDE.md` "please read these
files" instruction — the soft version is exactly what silently failed.

Constraint: SessionStart hooks are a Claude Code mechanism; other CLIs (Codex, Gemini, …) do not run
them. The non-hook CLIs must still get the snowball some other way.

## Decision

Add a Claude Code **SessionStart** hook (`hooks/shared/session-digest/`) that reads the snowball +
active profile and injects a compact digest (≤ ~400 tokens) into context every session: active
pack/mode/role, compliance mode, recent lessons, memory highlights, open jobs, recent ADR/decision
titles, pending migrations. It degrades silently when a source is absent (works in a fresh scaffolded
repo). For non-hook CLIs, `CLAUDE.md`'s session-start ritual is kept as the explicit fallback ("read
these files here"). Ships in both Lintel's own repo and the scaffolded template.

## Alternatives considered

- **`CLAUDE.md` instruction only ("read lessons/memory/profile at session start").** Rejected:
  relies on the agent obeying every session and costs full-file context each time. This is the soft
  mechanism that already silently failed.
- **`tasks/INDEX.md` always-read index (mirror global MEMORY.md exactly).** Rejected as the primary
  mechanism (still a plain file that depends on being read), but adopted as the digest's *content
  model*: the hook emits an index-style digest, not full files.
- **A generated skill-routing map in CLAUDE.md.** Rejected: skills already auto-surface (names +
  descriptions are in context); a map is redundant for discovery and rots as skills change. A light
  routing *nudge* is kept instead.

## Consequences

- **Positive:** the snowball reaches every Claude Code session mechanically — lessons, active
  identity, open jobs, recent decisions — so it actually compounds. Scaffolded repos inherit it.
  Cheap (~400 tokens, index-style).
- **Negative:** Claude-Code-only for the mechanical path; other CLIs depend on the CLAUDE.md ritual
  fallback (softer). A new hook to maintain; the digest's source list must track where state lives.
- **Neutral:** introduces a SessionStart wiring step in `install/` + `li-scaffold`; `li-doctor` gains
  a "digest hook wired?" check.

## Implementation notes

- Hook output uses the SessionStart `hookSpecificOutput.additionalContext` envelope.
- Sources: `~/.lintel/profile.yaml`, `tasks/lessons.md` (recent `^## L-NNN` headers), `tasks/memory.md`,
  `~/.lintel/jobs/_active.md`, `docs/adr/NNNN-*.md` titles, `docs/migrations/`.
- Budget: ~400 tokens default; pack-overridable later (deferred — see design doc open questions).

## References

- [.claude/engineering/design-archive/claude-md-capability-and-memory-surfacing.md](../design/claude-md-capability-and-memory-surfacing.md)
- [ADR-0001](0001-lintel-dogfoods-its-own-scaffolding.md) — the dogfooding decision this builds on
