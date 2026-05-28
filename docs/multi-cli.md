# Multi-CLI architecture

How the same scaffolding works across multiple agent CLIs without duplication.

## The shape

One canonical file. Multiple shims. Each shim is a thin pointer.

```
jokerman-lintel/
├── AGENT-INSTRUCTIONS.md          ← canonical, CLI-agnostic source
└── shims/
    ├── CLAUDE.md                   ← Claude Code reads this
    ├── AGENTS.md                   ← Codex CLI reads this
    └── copilot-instructions.md     ← GitHub Copilot reads this
```

Each shim is short:

1. One line that points at `AGENT-INSTRUCTIONS.md` (the canonical source).
2. A "CLI-specific notes" section with details that only apply to that CLI (subagent mechanism, model picker, etc.).

The shim never overrides core behavior. If a CLI quirk forces a different behavior, the canonical file changes — not the shim. This keeps the cross-CLI surface consistent.

## Why the indirection

Three reasons.

1. **Single source of truth.** Update `AGENT-INSTRUCTIONS.md` once, every CLI gets the change at next session-start. No copy-paste drift.
2. **CLI-specific tips have somewhere to live.** Claude Code's subagent model and Copilot's model picker are different concerns. Each shim owns its quirks without polluting the canonical file.
3. **Future CLIs are cheap.** A new agent tool that reads "foo.md" gets a new `shims/foo.md` in 30 seconds. No restructuring.

## Per-CLI behavior

### Claude Code

- **Reads:** `CLAUDE.md` at user-global (`~/.claude/CLAUDE.md`) and per-repo (`<repo>/CLAUDE.md`). Per-repo wins.
- **Subagents:** First-class. Repo-level subagents live in `.claude/agents/<Name>.md`. User-global subagents in `~/.claude/agents/`. Subagents are invoked by name or by description match.
- **Skills (slash commands):** User-global in `~/.claude/skills/`. Project-local skills can also be defined.
- **Plan mode:** Built-in. Read-only mode for planning before any mutation.

This is the most full-featured target. The canonical instructions assume Claude Code's capabilities and gracefully degrade for other CLIs.

### GitHub Copilot Enterprise (with Opus model picker)

- **Reads:** `.github/copilot-instructions.md` at repo root. (Per-repo only — no user-global equivalent.)
- **Subagents:** No first-class equivalent. Copilot Extensions exist but are integrations, not delegated workers. When `AGENT-INSTRUCTIONS.md` says "use a subagent for X", the Copilot operator either sequences manually or opens a separate conversation.
- **Skills:** No equivalent. Skills installed via the installer (gstack, AgentShield, etc.) are not callable from Copilot.
- **Model picker:** Enterprise tenants can pick Claude Opus as the backend. Pick it for agent-style work — default Copilot completions are tuned for inline suggestions, not session-level reasoning.
- **Context window:** Smaller than a fresh Claude Code Opus session. Keep `tasks/memory.md` lean.

Copilot is the **degraded mode**. It can follow the canonical instructions, but the subagent and skill plumbing does not apply.

### Codex CLI

- **Reads:** `AGENTS.md` at repo root. By convention only — not enforced by the tool.
- **Subagents:** No first-class equivalent. Closest: spawn a separate Codex run with a scoped prompt.
- **Skills:** No equivalent.
- **Plan-first:** Operator-driven discipline, not tool-enforced. The canonical rules still apply.
- **Tool permissions:** Per-invocation.

Codex is **between** Claude Code and Copilot in capability. Subagents degrade to sequenced runs.

### Other agent CLIs

Pattern:

1. Identify what file the CLI reads at session start.
2. Add a `shims/<filename>` that points at `AGENT-INSTRUCTIONS.md`.
3. Add a CLI-specific notes section in that shim.
4. Document the per-repo wiring (symlink or copy) in [getting-started.md](getting-started.md).

If the CLI does not read any per-repo file: you cannot use this scaffolding with that CLI.

## What the canonical file assumes

`AGENT-INSTRUCTIONS.md` is written to:

- Operate even on a degraded CLI (no subagents, smaller context window).
- Use file-system conventions that work everywhere (`tasks/`, `docs/adr/`, `.claude/agents/`).
- Cite where each piece of state lives rather than relying on a CLI-specific tool.
- Treat subagent invocations as "delegate this; if you cannot delegate, sequence it instead".

This means a Copilot user gets the same compliance check, the same memory protocol, and the same precedence rules as a Claude Code user — they just execute them more manually.

## When the canonical file should change

Change it when:

- A behavior should be uniform across all CLIs (new compliance step, new memory section, revised precedence).
- A new section is needed (a recurring failure mode is generalizable).
- A section is wrong and the same wrongness applies to every CLI.

Do **not** change it when:

- The need is specific to one CLI (put it in that CLI's shim).
- The change is for a single repo (put it in that repo's `CLAUDE.md`).
- The change is a personal preference (put it in user-global `~/.claude/CLAUDE.md`).

## Conflict resolution

If a per-repo rule conflicts with the canonical instructions, the per-repo rule wins. If a CLI shim contradicts the canonical instructions, the canonical wins — the shim is meant to layer, not override.

If a conflict surfaces during work: the agent halts, reports the conflict, and waits for the operator to resolve it.
