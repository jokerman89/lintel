# Subagent Guide

How to work with subagents in this repo.

## Discovering existing subagents

Lintel's canonical fleet ships from `agents/` in the installed Lintel source bundle. Ask the host
which agents it actually exposes before delegating; native, sequenced and no-subagent clients do
not share one discovery API. Select an operator-named agent first, then a repository override,
active-pack promotion, user-global definition and finally the main-agent fallback.

This scaffold deliberately creates no `.claude/agents/` directory. A repository-local agent is an
optional host-specific override and may shadow a same-named installed agent. Add one only for a
durable project-specific role, document that shadowing intent, and verify which definition the host
selected.

## When to create a new subagent

Create a new subagent when:

- You repeat the same kind of task across sessions (audit, review, research pattern)
- A task has a distinct tool need that does not match any existing agent
- The main context gets polluted by a particular kind of prompt instruction

Do **not** create a new subagent for:

- A one-off task (just do it in the main context)
- A task an existing subagent could handle with a better prompt

## Create a subagent

On a host that supports repository-local definitions, create `.claude/agents/<Name>.md` with:

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
4. **Separate implementation from review.** A scoped implementer may edit only its assigned paths;
   a reviewer reports and never fixes its own findings. The coordinator decides what is integrated.
5. **Cite sources.** A subagent should reference file:line, ADR number, or equivalent rather than assumptions.

## Swarm execution

Use swarming only when an approved work map explicitly opts in and independent cards have disjoint
ownership. In a Lintel source checkout, seed from
`scaffolding/01-foundation/templates/swarm/`; in a scaffolded consumer, use the five copied files
under `.claude/templates/swarm/`. Keep the committed charter, coordination map, briefs, reports and reviews under the initiative's
`.claude/plans/<initiative>/swarm/` directory. The task source remains authoritative; do not copy
task prose, dependencies, status or acceptance criteria into coordination metadata.

One coordinator owns shared plan/runtime ledgers, generated outputs, commits and integration. A
worker owns only its declared `write_scope` plus its report. A distinct reviewer owns only that
lane's review artifact. Concurrent writers require attributable isolation through separate Git
worktrees, isolated patches or a host-enforced scoped-write sandbox. Otherwise execute the same
briefs sequentially. Never treat a shared-tree union diff as per-lane attribution or claim an
independent review when the implementer and reviewer were the same agent.

Recover from committed swarm artifacts and attributable changes. Quarantine scope breaches or
unreviewed work for coordinator reconciliation; do not silently discard it. Final review runs on
the reconciled integration branch even after every lane review passes.

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

Remove it when no longer relevant. Difference vs. `.claude/memory/lessons.md`: lessons are permanent rules from corrections; heads-ups are short-term context.
