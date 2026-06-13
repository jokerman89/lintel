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

Codex does not have a first-class subagent abstraction equivalent to Claude Code's. The closest pattern is invoking a separate Codex run with a scoped prompt. Treat agent precedence rules in `AGENT-INSTRUCTIONS.md` as guidance for how to scope those nested runs.

If a task in this repo lists a Claude Code subagent (e.g., "use the ReadOnly agent"), the Codex equivalent is to start a new Codex conversation with the prompt the subagent definition would have produced. The behavior is approximately the same; the mechanism differs.

### Plan mode

Codex's plan-first behavior is operator-driven, not enforced by the tool. The `AGENT-INSTRUCTIONS.md` rule still applies: plan before non-trivial work, write the plan to `.claude/plans/todo.md`, mark items off as they finish.

### Tool permissions

Codex's tool-permission model is per-invocation. The auto-mode bounds in `AGENT-INSTRUCTIONS.md` still apply: file edits and feature-branch commits OK without per-call ask; production mutations require explicit authorization.
