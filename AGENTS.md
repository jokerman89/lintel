# Codex session entry for Lintel repo

This file is read by OpenAI Codex CLI when working **on the Lintel repo itself**.

For canonical session bootstrap, see [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md).

---

## Repo overview

Lintel is a company-neutral, pack-driven session harness — markdown scaffolding for agent-based development. Company identity loads from a separate, installable pack.

- `skills/` — slash-commands (9-step cycle + engineering modules + session-harness)
- `agents/` — subagent roles organized per domain
- `hooks/shared/` — compliance + workflow hooks
- `scaffolding/` — templates copied INTO other repos
- `docs/architecture.md` — the architecture reference (decisions: `.claude/decisions/`)

## Session start ritual

1. Read [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) (canonical, applies to all CLIs)
2. Review `.claude/memory/lessons.md` for accumulated lessons
3. Check [docs/architecture.md](docs/architecture.md) + recent ADRs in `.claude/decisions/` for current architecture state

## Codex-specific notes

### Plugin install

This repo is a Codex plugin (see `.codex-plugin/plugin.json` with full `interface{}` block). Install via:

```
/plugins
> search lintel
> Install Plugin
```

Or for Codex App: sidebar → Plugins → `+`.

### Subagents in Codex

Codex has native subagent support (`lib/cli-tiers.yaml`: `subagents: native`). Agents in `agents/<category>/<Name>.md` load through the plugin manifest and can be delegated to directly. For scripted one-shot runs, the `codex exec` subprocess pattern still works:

```bash
codex exec --prompt "$(cat agents/security/SecurityAuditor.md). Audit branch X."
```

### Plan mode

Codex's plan-first behavior is operator-driven, not enforced by the tool. The `AGENT-INSTRUCTIONS.md` rule still applies: plan before non-trivial work, write to `.claude/plans/todo.md`, mark items as they finish.

### Tool permissions

Codex's tool-permission model is per-invocation. Auto-mode bounds in `AGENT-INSTRUCTIONS.md` still apply: file edits + feature-branch commits OK without per-call ask; production mutations require explicit authorization.

### Skill discovery

Skills live at `skills/<name>/SKILL.md` and surface natively as `/li:<skill>` once the plugin is
installed (`/plugins`, search lintel, Install). Codex is a **full-tier** CLI: native skills and
native subagents. The one thing it does not get is the hook enforcement layer, which is a Claude
Code mechanism.

For a scripted one-shot run outside an interactive session:

```bash
codex exec --prompt "$(cat skills/ship/SKILL.md). Execute on current branch."
```

### Compliance

Compliance is pack-driven (`resolve_pack_field compliance.*`). Neutral baselines apply across all Codex invocations: no customer data, no secrets, no prod mutations without auth. Tiered rules (identity policy, vendor preference, regulatory gates) come from the active pack.
