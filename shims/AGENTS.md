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

Codex has native subagents (`lib/cli-tiers.yaml`: `subagents: native`), so the agent precedence rules in `AGENT-INSTRUCTIONS.md` apply directly. For a scripted one-shot outside an interactive session, a separate `codex exec` run with a scoped prompt is the equivalent.

Skills surface natively as `/li:<skill>` once the plugin is installed. The one capability Codex does not get is the hook enforcement layer, which is a Claude Code mechanism.

### Plan mode

Codex's plan-first behavior is operator-driven, not enforced by the tool. The `AGENT-INSTRUCTIONS.md` rule still applies: plan before non-trivial work, write the plan to `.claude/plans/todo.md`, mark items off as they finish.

### Tool permissions

Codex's tool-permission model is per-invocation. The auto-mode bounds in `AGENT-INSTRUCTIONS.md` still apply: file edits and feature-branch commits OK without per-call ask; production mutations require explicit authorization.
