# Agent selection precedence

When a task could be delegated to one of several agents, this is how to pick.

The model has five levels. Higher level wins. Within a level, the agent whose `description:` field most closely matches the current task wins.

## The five levels

### Level 1 — Operator pin

The operator named a specific agent in the prompt. Use that agent. Do not second-guess, do not "improve" the choice.

Examples:
- "Use the ReadOnly agent for this audit"
- "Run CodeReviewer on the diff"
- "/qa this branch"

If the named agent does not exist: surface that, ask for the right name. Do not silently substitute.

### Level 2 — Repo-level override

An agent defined in this repo at `.claude/agents/<Name>.md` (or the equivalent for non-Claude CLIs).

A repo-level agent always wins over a same-named user-global agent. The intent: per-project tailoring.

Use Level 2 when:
- The repo has a project-specific subagent
- The repo's `CLAUDE.md` explicitly references an agent by name
- The task scope is clearly inside this repo's domain

### Level 3 — Promoted list

Agents listed in [promoted-agents.md](promoted-agents.md). The team has vetted these; they are the default for cross-project work.

Promoted agents are typically installed from upstream (gstack skills, AgentShield, Trail of Bits, Anthropic). They are invoked via their installed path or registered name.

Use Level 3 when:
- No repo-level override applies
- The task matches a promoted agent's description
- The work is something we would want consistent behavior across projects

### Level 4 — User-global

Agents installed globally at `~/.claude/agents/` (or `~/.claude/skills/` for slash commands). Picked when no repo-specific or promoted version exists.

Use Level 4 when:
- An operator has personal customizations they want available everywhere
- The promoted list does not have a match but the user-global one does

### Level 5 — Fallback

Main agent handles the task directly, no delegation.

Use Level 5 when:
- The task is small enough that subagent overhead exceeds the benefit
- No agent at any level matches well
- The operator has not asked for delegation

The fallback is the default — when in doubt, just do the work.

## Tie-breaking inside a level

Two agents at the same level could each plausibly handle the task. The tie-breaker:

1. **Description-match.** Read each candidate's `description:` field. Pick the one whose phrasing best fits the current task.
2. **Tool scope.** If one agent has tools the task needs and the other doesn't, pick the one that has them.
3. **Recency of use.** If still tied, prefer the one used more recently in this repo (operator is already familiar with its output style).
4. **Ask.** If still tied: ask the operator.

## When the precedence model produces the wrong agent

If the model says "use agent X" but X is clearly wrong for the current task, the issue is usually one of:

- **Description rot.** X's description is outdated and no longer matches what it does. Fix the description; do not work around it.
- **Promotion mistake.** X was promoted but its niche is too narrow. File a demotion PR.
- **Repo override mismatch.** This repo's `.claude/agents/X.md` is wrong for the current branch's reality. Update the agent.

Don't bypass the precedence model silently. Bypassing once is fine if the override is explicit ("ignoring precedence — using Y because Z"). Bypassing twice without fixing the root cause is the failure mode.

## Subagent vs. main-agent decision

Before picking which agent at all, the prior question: should this be delegated?

Delegate when:
- The task has a clean input / output contract (a query, a review pass, a parallel research thread).
- The main context is at risk of getting polluted (long output, many file reads, exploratory search).
- The work is parallelizable (multiple independent subtasks).

Do not delegate when:
- The task requires holding context the main agent already has and the subagent would have to re-derive.
- The output is small and the agent overhead would dominate.
- The operator wants a conversational thread, not a single report back.

## CLI capability degradation

The precedence model assumes the CLI supports subagents.

- **Claude Code:** Full support. Apply as described.
- **Codex:** No first-class subagent. Treat "delegate to agent X" as "spawn a new Codex run with the prompt agent X would have produced". Same selection logic, different mechanism.
- **GitHub Copilot Enterprise:** No subagent equivalent. Sequentialize what would be parallel. Skip Level 3 in practice — promoted-list agents typically can't be invoked from Copilot.

When operating on a degraded CLI, the precedence model still informs **which prompt to use** even if the delegation mechanism is manual.
