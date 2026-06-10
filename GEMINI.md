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
- `docs/design/lintel-v3-plan.md` — current architecture

## Session start ritual

1. Read [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) (canonical, applies to all CLIs)
2. Review `scaffolding/01-foundation/tasks/lessons.md` for accumulated lessons
3. Check `docs/design/lintel-v3-plan.md` for current phase

## Gemini-specific notes

### Extension install

This repo is a Gemini extension (see `gemini-extension.json`). Install via:

```bash
gemini extensions install https://github.com/jokerman89/jokerman-lintel
```

Update via:

```bash
gemini extensions update lintel
```

### Skill discovery on Gemini

Gemini CLI extensions are simpler than Claude Code plugins — they rely on this context file (GEMINI.md) plus markdown content. There's no explicit skill-discovery mechanism.

To invoke a skill on Gemini, reference the file path:

```
Follow instructions from skills/ship/SKILL.md and execute on the current branch.
```

### Available skill catalog

Common skills (see `skills/` for full list):
- `/qa` — run test suite, fix failures
- `/cycle` — 9-step work cycle (sense→capture)
- `/ship` — pre-flight checks + PR creation
- `/investigate` — bug investigation
- `/code-freeze` / `/code-unfreeze` — freeze controls
- `/plan-eng-review`, `/plan-ceo-review`, `/plan-design-review`, `/plan-devex-review` — phased reviews
- `/office-hours` — Socratic design refinement
- `/ta`, `/da`, `/sc`, `/dh`, `/tq` — engineering-domain modules
- `/compliance-gate` — runs the active pack's compliance gates
- `/generate-ppt`, `/generate-word`, `/generate-web` — doc generation
- `/scaffold`, `/scaffold-internal-tool`, `/scaffold-mvp` — repo scaffolds

### Subagents

Gemini's subagent model differs from Claude Code's Task tool. For multi-agent workflows, run Gemini in interactive mode and ask it to consult `agents/<category>/<Name>.md` for role context.

### Compliance

Compliance is pack-driven (`resolve_pack_field compliance.*`). Neutral baselines: no customer data, no secrets in prompts, no prod mutations without auth. Tiered rules (SSO policy, vendor preference, regulatory gates) come from the active pack — see the lintel-caip-pack example.

### Voice corpus

Voice is supplied by the active pack (`resolve_pack_field voice.corpus`; none in `_default`). The Microsoft CAIP-SE Trailblazer corpus ships in the lintel-caip-pack example.
