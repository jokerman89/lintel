---
name: personas-rotate
layer: foundation
description: Load persona context from .claude/memory/personas.md for demo-prep, workshop-facilitation, or audience-aware writing.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the personas-rotate skill.

## What this skill does

Loads persona definitions from the active pack's persona source (`resolve_pack_field persona.source`; none in `_default`) plus any operator-local `.claude/memory/personas.md` / `docs/personas/`, into session context. Lets operator name a persona (e.g., "load the CIO-Acme persona") to bias subsequent agent outputs (proposal, demo narration, email drafting) toward that persona's needs and language.

## When to use

- Pre-demo prep — load audience persona before demo-narration work
- Customer-meeting prep — load customer persona before proposal / exec-brief drafting
- Workshop design — load multi-persona context before workshop facilitation
- Internal review with persona simulation

## When NOT to use

- Generic content not tied to specific audience
- No personas defined yet — recommend `bin/li-scaffold` first

## Workflow

1. **Locate persona sources.**
   - Primary: the active pack's persona source (`resolve_pack_field persona.source`; none in `_default`)
   - Operator-local: `.claude/memory/personas.md` (list of personas this repo cares about)
   - Detailed: `docs/personas/<Name>.md` (one file per persona)

2. **List available personas.** Output names + 1-line description per persona.

3. **Operator selects persona.** Via AskUserQuestion or command argument (`/personas-rotate CIO-Acme`).

4. **Load persona detail.** Read `docs/personas/<Name>.md`. Parse:
   - Role + responsibilities
   - Key concerns (top 3)
   - Language preferences (formal / direct / technical)
   - Decision criteria
   - Anti-patterns (what makes them disengage)
   - Sample-good messages they've responded to (if archived)

5. **Inject into session context.** Tell the agent: "For the next interactions, optimize for this persona: <full detail>."

6. **Persist for session.** Note persona name in session memory (`.claude/memory/working-state.md` short-term context) so subagents inherit.

## Output format

```
PERSONAS-ROTATE: <persona name>

Loaded:
- Role: <role>
- Concerns: <top 3>
- Language: <formal/direct/technical>
- Decision criteria: <list>

Active for session: yes
Subagents will inherit: yes

To rotate: /personas-rotate <other-name>
To clear: /personas-rotate --clear
```

## Edge cases

- **Persona not found** — list available, ask operator to pick.
- **Multiple personas need to be active** — recommend running each persona-rotation in series, taking notes per persona, not loading multiple simultaneously.
- **Customer-anonymous persona** — verify no real customer name leaks if persona is composite or example.
- **Voice tier conflict** — if persona requires an elevated voice tier but current task is internal, surface conflict.

## Part of session-harness

Personas are how Lintel scales voice + audience-awareness across sessions. Without persona-rotation, every demo prep starts from blank. With it, operator's persona library compounds value.

Persona detail lives in the active pack (`persona.source`) or operator-local `docs/personas/` — travels with the pack or the code, evolves with the engagement.
