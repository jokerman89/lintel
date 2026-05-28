# Gemini CLI session entry for JStack repo

This file is read by Gemini CLI when working **on the JStack repo itself**.

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

## Gemini-specific notes

### Extension install

This repo is a Gemini extension (see `gemini-extension.json`). Install via:

```bash
gemini extensions install https://github.com/Azureflipper/jokerman-session-setup
```

Update via:

```bash
gemini extensions update jstack
```

### Skill discovery on Gemini

Gemini CLI extensions are simpler than Claude Code plugins — they rely on this context file (GEMINI.md) plus markdown content. There's no explicit skill-discovery mechanism.

To invoke a skill on Gemini, reference the file path:

```
Follow instructions from skills/release-ev2/SKILL.md and execute on the current branch.
```

### Available skill catalog

Common skills (see `skills/` for full list):
- `/qa` — run test suite, fix failures
- `/release-ev2` — pre-flight checks + PR creation
- `/safe-deploy-ring` — canary deploy
- `/investigate` — bug investigation
- `/code-freeze` / `/code-unfreeze` — freeze controls
- `/plan-eng-review`, `/plan-ceo-review`, `/plan-design-review`, `/plan-devex-review` — phased reviews
- `/office-hours` — Socratic design refinement
- `/rais-customer-voice-check` — Trailblazer voice gate
- `/onecs-check` — 1CS compliance check
- `/agt-tier-stamp` — Agent Governance tier stamp
- `/generate-ppt`, `/generate-word`, `/generate-web` — doc generation
- `/scaffold-engagement-demo`, `/scaffold-internal-tool`, `/scaffold-mvp` — repo scaffolds

### Subagents

Gemini's subagent model differs from Claude Code's Task tool. For multi-agent workflows, run Gemini in interactive mode and ask it to consult `agents/<category>/<Name>.md` for role context.

### Compliance

5+7+8 compliance tier in `scaffolding/02-sdl/`. Apply hard rules: no customer data, no secrets in prompts, MS SSO only, first-party-first.

### Voice corpus

`scaffolding/03-ms-team/voice/OurVoice-corpus.md` for Trailblazer voice calibration. Status: see `OurVoice-calibration.md`.
