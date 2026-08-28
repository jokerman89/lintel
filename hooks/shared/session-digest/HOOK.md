---
name: session-digest
tier: context-inject
event: SessionStart (Claude Code)
fires_on: session start / resume / clear (Claude Code SessionStart hook)
override: set `~/.lintel/.digest-disabled` or env `NO_DIGEST=1`
necessity: REQUIRED
gap_if_skipped: "Lintel's memory snowball (lessons, memory, active pack/mode/role, open jobs, recent ADRs) never reaches the session — the discipline does not compound across sessions. This is the gap ADR-0002 closes."
audit: .claude/runtime/audit/hooks.jsonl
---

# session-digest

Auto-loads Lintel's memory snowball at session start by injecting a compact digest
(≤ ~400 tokens) into context — the mechanical equivalent of the operator's global
`MEMORY.md`. Implements [ADR-0002](../../../.claude/decisions/0002-session-digest-auto-load.md).

## Why this exists

Claude Code auto-loads `CLAUDE.md`, skill descriptions, `.claude/agents/`, and hooks — but NOT
`.claude/memory/lessons.md`, `.claude/memory/working-state.md`, `.claude/memory/personas.md`, `~/.lintel/profile.yaml`,
`.claude/runtime/state/`, or `.claude/decisions/`. Those are plain files. Without this hook the snowball is written
but never read on a fresh session, so it never compounds.

## What it injects

```
LINTEL SESSION DIGEST
Pack: <active_pack> · mode: <default_mode> · role: <role_active> · compliance: <mode>
Recent lessons: L-NNN <slug> · …
Memory: <highlights from .claude/memory/working-state.md>
Open jobs: <N> (<names>)
Recent decisions: ADR-NNNN <title> · …
Pending migrations: <N>
```

Sources (each optional — the hook degrades silently when absent, so it works in a fresh
scaffolded repo): `~/.lintel/profile.yaml`, `.claude/memory/lessons.md`, `.claude/memory/working-state.md`,
`~/.lintel/jobs/_active.md` (the cross-repo jobs registry), `.claude/decisions/`, `docs/migrations/`.

## Wiring (Claude Code)

Register as a SessionStart hook in `settings.json` (the installer / `li-scaffold` does this):

```json
{ "hooks": { "SessionStart": [ { "hooks": [
  { "type": "command", "command": "bash ~/.lintel/hooks/session-digest/run.sh" }
] } ] } }
```

Non-hook CLIs (Codex, Gemini, …) do not run SessionStart hooks — they fall back to the
`## Session-start ritual` in CLAUDE.md, which reads the same files explicitly.

## Override

- `~/.lintel/.digest-disabled` present, or env `NO_DIGEST=1` → emit nothing (exit 0).

## Output contract

Emits a single JSON object on stdout using the SessionStart envelope:
`{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"<digest>"}}`.
On any error or empty digest it exits 0 with no output (fail-open — never blocks a session).
