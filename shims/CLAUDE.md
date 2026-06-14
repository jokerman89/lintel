# Claude Code session entry

This file redirects to `AGENT-INSTRUCTIONS.md`, which is the canonical source for session bootstrap behavior across all agent CLIs.

**→ See [../AGENT-INSTRUCTIONS.md](../AGENT-INSTRUCTIONS.md) for full session bootstrap.**

---

## Claude Code-specific notes

These are tips that only apply when running under Claude Code. They do not override `AGENT-INSTRUCTIONS.md` — they layer on top.

### File locations

- **Memory + plans** live under `.claude/` (v5 layout, ADR-0005): `.claude/memory/{lessons,working-state,personas}.md` + `.claude/plans/todo.md`.
- **Repo-level subagents** live in `.claude/agents/<Name>.md` (Markdown with YAML frontmatter — name, description, color, tools).
- **Repo-level subagent guide** is `.claude/SUBAGENT-GUIDE.md`.
- **User-global subagents** live in `~/.claude/agents/`. Repo-level versions override user-global of the same name.

### Subagent invocation

Claude Code picks subagents based on the `description:` field in the frontmatter. Match by task affinity — if multiple agents could apply, the operator can name one explicitly ("use the ReadOnly agent for this audit").

A subagent's output is a single message back to the main agent. Treat it as context, not as a final answer. The main agent decides what to do with subagent output.

### Slash commands

Claude Code supports project-local and user-global slash commands (skills). Project-local skills can live alongside this scaffolding.

### Plan mode

Use plan mode for any non-trivial task (3+ steps or an architectural decision). Plan mode operates read-only — it cannot mutate code or run commands that change state. Exit plan mode only after the plan is approved.
