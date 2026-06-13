# Multi-CLI architecture

How the same scaffolding works across multiple agent CLIs without duplication. The per-CLI
capability truth is `lib/cli-tiers.yaml` (single source); the README's table is generated from it.

## The shape

Two mechanisms, one source:

1. **Instructions** — one canonical file (`AGENT-INSTRUCTIONS.md`), reached through each CLI's
   native root entry file: `CLAUDE.md` (Claude Code), `AGENTS.md` (Codex and other
   AGENTS.md-convention CLIs), `GEMINI.md` (Gemini CLI), `.github/copilot-instructions.md`
   (Copilot Enterprise). The repo root carries these files; `shims/` holds the thin templates
   for scaffolded repos that lack them.
2. **Skills + agents** — written once at repo root, shipped through small per-CLI plugin
   manifests (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `gemini-extension.json`;
   OpenCode follows `.opencode/INSTALL.md`) that all point at the same `./skills/` and
   `./agents/`. Copilot CLI and Factory Droid read the `.claude-plugin/` manifest via
   Claude-plugin interop.

Each root entry file / shim is short:

1. One line that points at `AGENT-INSTRUCTIONS.md` (the canonical source).
2. A "CLI-specific notes" section with details that only apply to that CLI (subagent mechanism, model picker, etc.).

The entry file never overrides core behavior. If a CLI quirk forces a different behavior, the canonical file changes — not the shim. This keeps the cross-CLI surface consistent.

## Why the indirection

Three reasons.

1. **Single source of truth.** Update `AGENT-INSTRUCTIONS.md` once, every CLI gets the change at next session-start. No copy-paste drift.
2. **CLI-specific tips have somewhere to live.** Claude Code's subagent model and Copilot's model picker are different concerns. Each shim owns its quirks without polluting the canonical file.
3. **Future CLIs are cheap.** A new agent tool that reads "foo.md" gets a new `shims/foo.md` in 30 seconds. No restructuring.

## Per-CLI behavior

### Claude Code

- **Reads:** `CLAUDE.md` at user-global (`~/.claude/CLAUDE.md`) and per-repo (`<repo>/CLAUDE.md`). Per-repo wins.
- **Subagents:** First-class. Repo-level subagents live in `.claude/agents/<Name>.md`. User-global subagents in `~/.claude/agents/`. Subagents are invoked by name or by description match.
- **Skills (slash commands):** Lintel's skills install as a plugin (`/plugin install li@jokerman-lintel`) and surface as `/li:<skill>`. Project-local and user-global skills can also be defined.
- **Hooks:** The enforcement layer — a Claude-Code-only mechanism. Auto-registered on a plugin install; armed manually on a bare install.
- **Plan mode:** Built-in. Read-only mode for planning before any mutation.

This is the most full-featured target. The canonical instructions assume Claude Code's capabilities and gracefully degrade for other CLIs.

### GitHub Copilot Enterprise (with Opus model picker)

- **Reads:** `.github/copilot-instructions.md` at repo root. (Per-repo only — no user-global equivalent.)
- **Subagents:** No first-class equivalent. Copilot Extensions exist but are integrations, not delegated workers. When `AGENT-INSTRUCTIONS.md` says "use a subagent for X", the Copilot operator either sequences manually or opens a separate conversation.
- **Skills:** No equivalent. Lintel's `/li:*` skills are not callable from Copilot Enterprise — apply their SKILL.md content manually. (Copilot **CLI** is different: it reads the `.claude-plugin/` manifest via interop.)
- **Model picker:** Enterprise tenants can pick Claude Opus as the backend. Pick it for agent-style work — default Copilot completions are tuned for inline suggestions, not session-level reasoning.
- **Context window:** Smaller than a fresh Claude Code Opus session. Keep `.claude/memory/working-state.md` lean.

Copilot is the **degraded mode**. It can follow the canonical instructions, but the subagent and skill plumbing does not apply.

### Codex CLI

- **Reads:** `AGENTS.md` at repo root. By convention only — not enforced by the tool.
- **Subagents:** Native (`lib/cli-tiers.yaml`: `subagents: native`). For scripted one-shot runs, a separate `codex exec` with a scoped prompt also works.
- **Skills:** Native — install the plugin via `/plugins`, skills surface as `/li:<skill>`.
- **Plan-first:** Operator-driven discipline, not tool-enforced. The canonical rules still apply.
- **Tool permissions:** Per-invocation.

Codex is a **full-tier** CLI alongside Claude Code and Cursor — the one thing it never gets is the hook enforcement layer (Claude-Code-only).

### Other agent CLIs

Cursor, Gemini CLI, OpenCode, Copilot CLI, Factory Droid, and Cline/Continue/Aider each have an
entry in `lib/cli-tiers.yaml` — that file is the live per-CLI capability truth. For a CLI not yet
listed, the pattern:

1. Identify what file the CLI reads at session start.
2. Add a `shims/<filename>` that points at `AGENT-INSTRUCTIONS.md`.
3. Add a CLI-specific notes section in that shim.
4. Document the per-repo wiring (symlink or copy) in [getting-started.md](getting-started.md).

If the CLI does not read any per-repo file: you cannot use this scaffolding with that CLI.

## What the canonical file assumes

`AGENT-INSTRUCTIONS.md` is written to:

- Operate even on a degraded CLI (no subagents, smaller context window).
- Use file-system conventions that work everywhere (`.claude/memory/`, `.claude/plans/`, `.claude/decisions/`, `.claude/agents/`).
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
