# Claude Code session entry for JStack repo

This file is read by Claude Code when working **on the JStack repo itself**.

For canonical session bootstrap, see [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md).

---

## Repo overview

JStack is the MS-CAIP-SE session harness — markdown scaffolding for agent-based development.

- `skills/` — 74 slash-commands (foundation + ms-team layers)
- `agents/` — 44 subagent roles organized per domain (ms-specific, engineering, doc-gen, voice, security, compliance, devops, customer, communication)
- `hooks/shared/` — 15 compliance + workflow hooks
- `scaffolding/` — templates that get copied INTO other repos via `bin/jstack-scaffold`
- `docs/design/jstack-v3-plan.md` — current architecture
- `docs/per-cli/` — per-CLI plugin setup guides

## Session start ritual

1. Read [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) (canonical, applies to all CLIs)
2. Review `scaffolding/01-foundation/tasks/lessons.md` for accumulated lessons (this repo's own lessons, not target-repo lessons)
3. Check `docs/design/jstack-v3-plan.md` for current execution phase
4. Use [LAYERS.md](LAYERS.md) for understanding the 2-category model (Agent-invokable vs Repo-scaffolding)

## Claude Code-specific notes

### Plugin structure

This repo IS a Claude Code plugin (see `.claude-plugin/plugin.json`). Skills live at `skills/<name>/SKILL.md`. Agents at `agents/<category>/<Name>.md`. When operator installs via `/plugin install jstack@jokerman-session-setup`, all skills become available as `/jstack:<skill>` (namespaced).

### Local testing

To test changes without committing:
```bash
claude --plugin-dir E:/Workspace/jokerman-session-setup
```

### Skill namespacing

Skills are namespaced `/jstack:qa`, `/jstack:release-ev2`, etc. Inside this repo's own session, the slash-commands work directly because Claude Code reads SKILL.md files via the plugin manifest.

### Subagent invocation

Subagents in `agents/<category>/<Name>.md` are spawned via the Task tool. Agent name resolution uses the `description:` field for affinity match. To invoke explicitly: "Use the OneCSAuditor agent for this check."

### Plan mode

Plan mode (read-only) for any non-trivial change. Auto-mode bounds documented in [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md).

## Per-CLI portability

JStack v3 supports 8 CLIs via plugin manifests. See [docs/per-cli/](docs/per-cli/) for setup guides per CLI. The same skills/agents/hooks work in:
- Claude Code (this file)
- Codex CLI/App (via [AGENTS.md](AGENTS.md))
- Cursor (via `.cursor-plugin/plugin.json`)
- Gemini CLI (via [GEMINI.md](GEMINI.md) + `gemini-extension.json`)
- OpenCode (via `.opencode/INSTALL.md`)
- GitHub Copilot CLI (via `.copilot-plugin/plugin.json`)
- Factory Droid (via `.droid-plugin/plugin.json`)
