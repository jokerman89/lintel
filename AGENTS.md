# Codex session entry for JStack repo

This file is read by OpenAI Codex CLI when working **on the JStack repo itself**.

For canonical session bootstrap, see [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md).

---

## Repo overview

JStack is the MS-CAIP-SE session harness — markdown scaffolding for agent-based development.

- `skills/` — 74 slash-commands (foundation + ms-team layers)
- `agents/` — 44 subagent roles organized per domain
- `hooks/shared/` — 15 compliance + workflow hooks
- `scaffolding/` — templates copied INTO other repos
- `docs/design/jstack-v3-plan.md` — current architecture

## Session start ritual

1. Read [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) (canonical, applies to all CLIs)
2. Review `scaffolding/01-foundation/tasks/lessons.md` for accumulated lessons
3. Check `docs/design/jstack-v3-plan.md` for current phase

## Codex-specific notes

### Plugin install

This repo is a Codex plugin (see `.codex-plugin/plugin.json` with full `interface{}` block). Install via:

```
/plugins
> search jstack
> Install Plugin
```

Or for Codex App: sidebar → Plugins → `+`.

### Subagents in Codex

Codex doesn't have a first-class subagent abstraction like Claude Code's Task tool. The closest equivalent is `codex exec` subprocess. Agents in `agents/<category>/<Name>.md` are reference patterns — operator runs them via:

```bash
codex exec --prompt "$(cat agents/ms-specific/OneCSAuditor.md). Audit branch X."
```

### Plan mode

Codex's plan-first behavior is operator-driven, not enforced by the tool. The `AGENT-INSTRUCTIONS.md` rule still applies: plan before non-trivial work, write to `tasks/todo.md`, mark items as they finish.

### Tool permissions

Codex's tool-permission model is per-invocation. Auto-mode bounds in `AGENT-INSTRUCTIONS.md` still apply: file edits + feature-branch commits OK without per-call ask; production mutations require explicit authorization.

### Skill discovery

Skills at `skills/<name>/SKILL.md`. Codex doesn't have native slash-command discovery — operator references skills explicitly:

```bash
codex exec --prompt "$(cat skills/release-ev2/SKILL.md). Execute on current branch."
```

### Compliance

5+7+8 compliance tier in `scaffolding/02-sdl/`. Hard rules apply across all Codex invocations: no customer data, no secrets, no prod mutations without auth, MS SSO only, first-party-first.
