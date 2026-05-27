# Power-user patterns

Patterns that pay off once the basic setup is running. Not required for everyday work — these are the "next level" once the muscle memory is there.

## 1. Cross-session memory protocols

`scaffolding/tasks/memory.md` is the canonical place for cross-session memory. Four sections: operator profile, project context, feedback patterns, external references.

**Protocols that compound:**

- **Update on change, not on cadence.** Memory entries become noise if you write one per session. Write one when something changes — a new stakeholder, a new constraint, a feedback pattern that crystallizes.
- **Date and source.** Every entry has the date you wrote it. If it came from a conversation, link / quote it. Memories without provenance become claims without evidence.
- **Prune on session start.** When you read memory at session start, kill entries that are no longer true. Five lean memories beat fifty stale ones.
- **Tier by recency.** Operator profile and project context are read every session. External references are read on demand. Structure the file so the high-traffic sections are at the top.

## 2. Workflow templates per project type

Different project shapes benefit from different scaffolding subsets.

Common shapes the CAIP team encounters:

- **PoC for customer demo.** Short-lived. ADRs are overkill. Keep `tasks/todo.md` and `tasks/lessons.md`, skip `docs/adr/`.
- **Reference implementation.** Long-lived, externally-visible. Full scaffolding including ADRs, with extra weight on `tasks/personas.md` (different consumers have different needs).
- **Internal tool / utility.** Solo maintainership. Lean scaffolding: keep `tasks/lessons.md` and `docs/adr/` for traceability, skip `tasks/personas.md`.
- **Customer engagement repo.** Customer-data-sensitive. Full scaffolding **plus** customized `CLAUDE.md` that hardens compliance for that customer's contract.

Make a template script (one per shape) under `install/templates/` once you have repeated a setup more than twice.

## 3. Custom hooks

Hooks intercept agent behavior at specific lifecycle points. Useful for:

- **Pre-prompt context injection.** Before the agent acts, inject current branch state or open ticket context.
- **Post-tool guard.** After a tool call, validate that the result is in scope.
- **Session-start enforcement.** Run the compliance check programmatically rather than relying on the agent to do it.

Claude Code has first-class hooks (`~/.claude/hooks/`). Other CLIs vary. Hooks are powerful and easy to mis-configure — when a hook fires incorrectly it can break every session. Always test hooks against a throwaway repo before relying on them.

If you write a hook that is useful across the team: PR it into this repo under `scaffolding/.claude/hooks/` and document it in this file.

## 4. Multi-repo workspace patterns

Working across multiple repos in one session (e.g., a backend + frontend pair, or a service + its consumers):

- **One CLI session per logical workspace, not per repo.** Switching agents loses cross-repo context. Open the parent directory and let the agent navigate.
- **Shared `tasks/memory.md` at the parent level.** Symlink each repo's `tasks/memory.md` to a single source so insights about the system aggregate.
- **Per-repo `CLAUDE.md` stays per-repo.** Repo-specific rules do not promote upward.
- **ADRs that span repos go in the source-of-truth repo.** The other repo references via link in its own ADR ("see ADR-0042 in <other-repo>").

This is harder than it sounds because most CLIs are repo-scoped by default. Worth the friction when the work genuinely spans multiple repos.

## 5. Audit-trail discipline

A clean audit trail is what lets you reconstruct decisions 6 months later when nobody remembers.

The four artifacts:

1. **Commits.** Atomic, conventional-commits format, one logical change per commit. PR-based merges to `main`.
2. **ADRs.** Non-trivial decisions captured at the time the decision is made, not retroactively.
3. **`tasks/lessons.md` entries.** Every correction generates a one-line rule.
4. **`scaffolding/EVOLUTION-LOG.md` entries.** Every change to the canonical instructions is logged with date + reason.

Bypass any one of these and the chain breaks. Discipline beats tooling — no automation forces this; it has to be a habit.

## 6. Skill activation rules per harness-context

A skill can behave differently depending on the harness running it. Examples:

- **Claude Code interactive session:** the skill can ask clarifying questions.
- **Claude Code under `/loop`:** the skill should not ask; it should make the reasonable call and proceed.
- **Codex CLI:** the skill cannot delegate to subagents; sequentialize.
- **GitHub Copilot Enterprise:** the skill has a smaller context window; produce shorter outputs.

If a skill has harness-conditional behavior, document the conditions in its SKILL.md frontmatter or body, and verify the skill detects the harness correctly.

## 7. Cross-session lessons compounding

The compounding mechanism in this setup is `tasks/lessons.md`. To make it actually compound:

- **Write the rule, not the incident.** "Don't run `--force` against shared registries" beats "yesterday I broke the registry".
- **Generalize across sessions.** If the same shape of mistake happens twice from different operators, the rule is wrong or not visible enough. Fix the rule, or surface it earlier in the session-start.
- **Re-read lessons on session start.** Not all of them — the most recent 10–15. Older ones are reference material.
- **Demote lessons that have not bit in a year.** They have served their purpose; they are now noise.

`tasks/lessons.md` should be growable but not infinite. A team of 5–10 SEs working actively for a year should produce 30–60 lessons total, not 300.

## 8. Operator-specific routing

Different operators have different preferences. The `tasks/personas.md` file is where to capture them.

Patterns:

- **One-operator repos:** one persona file, the operator. Simple.
- **Team repos:** one persona per active contributor. The agent picks the right communication style based on who is at the keyboard.
- **Customer-engagement repos:** add a persona for the customer's lead engineer if their style is known. The agent generates work-in-progress that anticipates their preferences.

Personas are not for hypothetical users. If you have not actually worked with the person, do not write a persona for them.

## 9. Scoping subagent context budgets

Subagents inherit a chunk of the main context. Long subagent prompts + large file reads = the subagent burns its budget before producing output.

Pattern:
- Subagent prompts should be 200–400 words. Above that, the prompt has not been distilled enough.
- Subagent file-read budget: 10–20 files max. More than that, the question is too broad — split into multiple subagents.
- Subagent output budget: 500–1000 words. Above that, the subagent is doing the main agent's synthesis work.

If a subagent consistently runs out of context: revise its description or split its responsibility.

## 10. When to skip the scaffolding entirely

Some work genuinely does not benefit from this setup:

- A throwaway exploration repo.
- A spike that will be deleted in a week.
- A pure data-analysis notebook (no production target).

Forcing the scaffolding on a throwaway repo wastes time. Use judgment. If the work has zero audit-trail requirement and zero need for cross-session memory: skip.
