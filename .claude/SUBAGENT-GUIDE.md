# Subagent Guide

How to work with subagents in this repo.

## Existing subagents

Listed in `.claude/agents/`. Each file is a `.md` with YAML frontmatter.

## When to create a new subagent

Create a new subagent when:

- You repeat the same kind of task across sessions (audit, review, research pattern)
- A task has a distinct tool need that does not match any existing agent
- The main context gets polluted by a particular kind of prompt instruction

Do **not** create a new subagent for:

- A one-off task (just do it in the main context)
- A task an existing subagent could handle with a better prompt

## Create a subagent

Create `.claude/agents/<Name>.md` with:

```markdown
---
name: <Name>
description: <one-line description shown when main-agent picks an agent>
color: <blue|purple|green|red|orange|yellow>
tools: <Read, Grep, Glob, Bash, Edit, Write — only what is needed>
---
You are a <role> for this repo.

<Concrete description of the agent's job>

<Workflow steps>

<Report format>

<Edge cases / what to do when blocked>
```

## Best practices

1. **Minimal tools.** Read-only agents get only Read/Grep/Glob. Write access only when truly needed.
2. **Explicit report format.** The main agent reads the output as context — structured output > prose.
3. **One clear role.** "Agent that does X", not "agent that can do X, Y, or Z".
4. **No fixes from a subagent.** A subagent reports; the main agent decides. Exception: TestRunner and similar agents that actually run things — but they still do not fix code.
5. **Cite sources.** A subagent should reference file:line, ADR number, or equivalent rather than assumptions.

## Revise an existing subagent

Free to do. Adjust the prompt; add date-stamped heads-ups if something is temporary.

If the revision is generalizable and the repo was scaffolded from `jokerman-lintel`: consider lifting the change to the scaffolded template and logging it in `EVOLUTION-LOG.md`.

## Temporary heads-ups for subagents

If a subagent needs to know something temporary ("we are migrating from X to Y, avoid Y code until migration is done"):

Add a date-stamped section to the agent's `.md`:

```markdown
## TEMP — 2026-05-11 — Migration in progress

We are migrating from X to Y. Ignore Y references until migration is complete.
Remove this block when the migration is done.
```

Remove it when no longer relevant. Difference vs. `tasks/lessons.md`: lessons are permanent rules from corrections; heads-ups are short-term context.
