# Lintel v3 — OpenCode install instructions

These instructions are for OpenCode to follow when an operator runs:

```
Fetch and follow instructions from https://raw.githubusercontent.com/jokerman89/lintel/refs/heads/main/.opencode/INSTALL.md
```

## What Lintel is

Lintel is a session-harness scaffold for Microsoft Sweden CAIP solution engineers. It provides:
- ~74 skills (slash-commands) for daily engineering + MS-specific workflows
- ~44 agents (subagent roles) organized per domain
- 15 hooks for compliance enforcement
- 5+7+8 compliance tiering (RAIS, OneCS, AGT, EV2, OneBranch, etc.)
- Trailblazer voice corpus + calibration mechanism
- Repo scaffolding templates (CORE-PRINCIPLES, EVOLUTION-LOG, tasks/lessons.md, ADR templates)

## OpenCode install steps

1. **Read the canonical session ritual:**
   ```
   fetch https://raw.githubusercontent.com/jokerman89/lintel/refs/heads/main/AGENT-INSTRUCTIONS.md
   ```
   Treat this as the primary session bootstrap doc.

2. **Pull skills into OpenCode plugin directory:**
   - Skills live at `https://github.com/jokerman89/lintel/tree/main/skills/`
   - Per-skill: `<repo>/skills/<name>/SKILL.md`
   - OpenCode should clone or fetch these into its plugin/skills directory.

3. **Pull agents:**
   - Agents organized per category at `https://github.com/jokerman89/lintel/tree/main/agents/`
   - Categories: `ms-specific/`, `engineering/`, `doc-gen/`, `voice/`, `security/`, `compliance/`, `devops/`, `customer/`, `communication/`
   - Place per OpenCode's agent-discovery mechanism.

4. **Hooks (optional, opt-in):**
   - Hook specs at `https://github.com/jokerman89/lintel/tree/main/hooks/shared/`
   - Each has `HOOK.md` + `run.sh`. Install matching ones to OpenCode's hooks dir.

5. **Compliance docs (reference):**
   - `scaffolding/02-sdl/HARD-RULES.md` — 5 always-on rules
   - `scaffolding/02-sdl/ON-DEMAND-RULES.md` — 7 on-demand items
   - `scaffolding/02-sdl/REFERENCE-RULES.md` — 8 background docs
   - Read these as context; enforce via hooks where applicable.

6. **Voice corpus (if doing customer-facing copy):**
   - `scaffolding/03-ms-team/voice/OurVoice-corpus.md`
   - Status: see `OurVoice-calibration.md` (NOT_CALIBRATED until operator runs T0 calibration)

## Limitations on OpenCode

- Subagent spawning may differ from Claude Code's Task tool
- AskUserQuestion behavior depends on OpenCode interactive mode
- Hooks support depends on OpenCode hook API

## Update flow

To update Lintel, re-run this INSTALL.md instructions. OpenCode should re-fetch from main branch.

## Plugins directory

Per-skill OpenCode plugin shims (if needed) live in `.opencode/plugins/`. Currently empty — skills work via direct content load.

## Issues

Report problems to: https://github.com/jokerman89/lintel/issues
