# Gemini CLI session entry for Lintel repo

This file is read by Gemini CLI when working **on the Lintel repo itself**.

For canonical session bootstrap, see [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md).

---

## Repo overview

Lintel is a company-neutral, pack-driven session harness — markdown scaffolding for agent-based development. Company identity (the Microsoft CAIP-SE workprofile) loads from the separate lintel-caip-pack.

- `skills/` — slash-commands (9-step cycle + engineering modules + session-harness)
- `agents/` — subagent roles organized per domain
- `hooks/shared/` — compliance + workflow hooks
- `scaffolding/` — templates copied INTO other repos
- `docs/design/lintel-v4.0-reframe-design.md` — current architecture (decisions since: `.claude/decisions/`, ADR-0005..0017)

## Session start ritual

1. Read [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) (canonical, applies to all CLIs)
2. Review `.claude/memory/lessons.md` for accumulated lessons
3. Check `docs/design/lintel-v4.0-reframe-design.md` + recent ADRs in `.claude/decisions/` for current architecture state

## Gemini-specific notes

### Extension install

This repo is a Gemini extension (see `gemini-extension.json`). Install via:

```bash
gemini extensions install https://github.com/jokerman89/lintel
```

Update via (the extension is named `li`):

```bash
gemini extensions update li
```

### Skill discovery on Gemini

Gemini CLI extensions are simpler than Claude Code plugins — they rely on this context file (GEMINI.md) plus markdown content. There's no explicit skill-discovery mechanism.

To invoke a skill on Gemini, reference the file path:

```
Follow instructions from skills/ship/SKILL.md and execute on the current branch.
```

### Available skill catalog

Common skills (see `skills/` for full list):
- `/li:qa` — run test suite, fix failures
- `/li:cycle` — 9-step work cycle (sense→capture)
- `/li:ship` — pre-flight checks + PR creation
- `/li:investigate` — bug investigation
- `/li:code-freeze` / `/li:code-unfreeze` — freeze controls
- `/li:plan-eng-review`, `/li:plan-ceo-review`, `/li:plan-design-review`, `/li:plan-devex-review` — phased reviews
- `/li:office-hours` — Socratic design refinement
- `/li:ta`, `/li:da`, `/li:sc`, `/li:dh`, `/li:tq` — engineering-domain modules
- `/li:compliance-gate` — runs the active pack's compliance gates
- `/li:generate-ppt`, `/li:generate-word`, `/li:generate-web` — doc generation
- `/li:scaffold`, `/li:scaffold-internal-tool`, `/li:scaffold-mvp` — repo scaffolds

### Subagents

Gemini's subagent model differs from Claude Code's Task tool. For multi-agent workflows, run Gemini in interactive mode and ask it to consult `agents/<category>/<Name>.md` for role context.

### Compliance

Compliance is pack-driven (`resolve_pack_field compliance.*`). Neutral baselines: no customer data, no secrets in prompts, no prod mutations without auth. Tiered rules (SSO policy, vendor preference, regulatory gates) come from the active pack — see the lintel-caip-pack example.

### Voice corpus

Voice is supplied by the active pack (`resolve_pack_field voice.corpus`; none in `_default`). The Microsoft CAIP-SE Trailblazer corpus ships in the lintel-caip-pack example.
