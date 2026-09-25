# Codex CLI session entry

This file redirects to `AGENT-INSTRUCTIONS.md`, which is the canonical source for session bootstrap behavior across all agent CLIs.

**→ See [../AGENT-INSTRUCTIONS.md](../AGENT-INSTRUCTIONS.md) for full session bootstrap.**

---

## Codex-specific notes

These are tips that only apply when running under Codex CLI. They do not override `AGENT-INSTRUCTIONS.md` — they layer on top.

### File locations

- Codex reads `AGENTS.md` from repo root by convention. This repo's root already carries `AGENTS.md`; this shim is for scaffolded repos that lack one.
- Memory + plans follow the same v5 layout as Claude Code (ADR-0005): `.claude/memory/{lessons,working-state,personas}.md` + `.claude/plans/todo.md`.

### Sub-agents

Codex documents configured subagents. Apply the shared agent precedence rules to the actual
inventory and permissions of the selected CLI, desktop or IDE surface. A separate subprocess
needs authorization and attributable read-only scope; its existence alone is not review clearance.

The preserved plugin is one route; the portable adapter generates `.agents/skills/li-*`.
Inspect the host's skill names and invocation rather than assuming `/li:<skill>` syntax.
The Claude hook bundle is not a Codex translation. Missing tools or safe write isolation retain
manual/serial work and outstanding independent review. See `universal/ADAPTER.md` in this tree.

### Plan mode

Codex's plan-first behavior is operator-driven, not enforced by the tool. The `AGENT-INSTRUCTIONS.md` rule still applies: plan before non-trivial work, write the plan to `.claude/plans/todo.md`, mark items off as they finish.

### Tool permissions

Codex's tool-permission model is per-invocation. The auto-mode bounds in `AGENT-INSTRUCTIONS.md` still apply: file edits and feature-branch commits OK without per-call ask; production mutations require explicit authorization.
