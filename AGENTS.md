# Codex session entry for Lintel repo

This file is read by OpenAI Codex CLI when working **on the Lintel repo itself**.

For canonical session bootstrap, see [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md).

---

## Repo overview

Lintel is a company-neutral, pack-driven session harness — markdown scaffolding for agent-based development. Company identity (the Microsoft CAIP-SE workprofile) loads from the separate lintel-caip-pack.

- `skills/` — slash-commands (9-step cycle + engineering modules + session-harness)
- `agents/` — subagent roles organized per domain
- `hooks/shared/` — compliance + workflow hooks
- `scaffolding/` — templates copied INTO other repos
- `docs/design/lintel-v3-plan.md` — current architecture

## Session start ritual

1. Read [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) (canonical, applies to all CLIs)
2. Review `scaffolding/01-foundation/tasks/lessons.md` for accumulated lessons
3. Check `docs/design/lintel-v3-plan.md` for current phase

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

Codex doesn't have a first-class subagent abstraction like Claude Code's Task tool. The closest equivalent is `codex exec` subprocess. Agents in `agents/<category>/<Name>.md` are reference patterns — operator runs them via:

```bash
codex exec --prompt "$(cat agents/security/SecurityAuditor.md). Audit branch X."
```

### Plan mode

Codex's plan-first behavior is operator-driven, not enforced by the tool. The `AGENT-INSTRUCTIONS.md` rule still applies: plan before non-trivial work, write to `tasks/todo.md`, mark items as they finish.

### Tool permissions

Codex's tool-permission model is per-invocation. Auto-mode bounds in `AGENT-INSTRUCTIONS.md` still apply: file edits + feature-branch commits OK without per-call ask; production mutations require explicit authorization.

### Skill discovery

Skills at `skills/<name>/SKILL.md`. Codex doesn't have native slash-command discovery — operator references skills explicitly:

```bash
codex exec --prompt "$(cat skills/ship/SKILL.md). Execute on current branch."
```

### Compliance

Compliance is pack-driven (`resolve_pack_field compliance.*`). Neutral baselines apply across all Codex invocations: no customer data, no secrets, no prod mutations without auth. Tiered rules (SSO policy, vendor preference, regulatory gates) come from the active pack — see the lintel-caip-pack example for the Microsoft CAIP-SE ruleset.
