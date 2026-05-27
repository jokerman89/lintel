# Evolution Process

The scaffolding system needs to evolve — otherwise it ossifies. But the core principles are load-bearing and must not drift silently.

This document describes how changes are made.

## Three kinds of change

### 1. Per-repo adaptation (free)

No process required. The repo owner may:
- Adapt their own `CLAUDE.md` with project-specific sections
- Add new subagents in `<repo>/.claude/agents/`
- Write lessons in `<repo>/tasks/lessons.md`
- Add optional files in `<repo>/tasks/`

This must NOT touch the scaffolding template.

### 2. Template change (logged)

Changes in `template/`, e.g. an improved generic subagent, a new generic subagent, an updated CLAUDE.md template.

Process:
1. Make the change in `template/`
2. Add an entry in [EVOLUTION-LOG.md](EVOLUTION-LOG.md) with date and motivation
3. Commit in the scaffolding repo
4. Existing repos do not adopt automatically — they pull the change manually if relevant

Bar for lifting a per-repo subagent into the template: it has proven value in 2+ repos OR captures a sufficiently generic pattern.

### 3. Core-principle change (requires explicit decision)

Changes to [CORE-PRINCIPLES.md](CORE-PRINCIPLES.md) are load-bearing. Requirements:

1. Write the proposed change in `EVOLUTION-LOG.md` as `PROPOSAL` with date, motivation, and what breaks if we do not make it
2. Wait for explicit user approval
3. On approval: change `CORE-PRINCIPLES.md`, mark the entry `ACCEPTED` with decision date
4. Note whether existing repos need retro-updates

Rationale for this friction: the core principles are the result of actual incidents and corrections. Silently changing them would destroy the institutional memory.

## When the scaffolding template is not the right place

Some things belong per-repo, not in the template:

- Technology-specific configuration (Bicep, Terraform, a specific test runner)
- Project-specific ADR mappings
- Domain vocabulary
- Cost models

These belong in the per-repo CLAUDE.md and per-repo subagents, not in the template.

Heuristic: if another project would get no value from it → per-repo.

## Temporary heads-ups to subagents

Sometimes a subagent needs to know something temporary ("we are currently migrating X, avoid Y until Z is done"). Two options:

- **Short heads-up (a few days):** add a section to the specific subagent's `.md` file with a date stamp. Remove it when no longer relevant.
- **Lesson (permanent):** add to `tasks/lessons.md` with date and rule.

Difference: lessons capture what-should-have-been-done; heads-ups capture what-is-happening-now.

## Promotion flow (per-repo → template)

1. A subagent exists and works in one repo
2. The same pattern appears in a second repo
3. Create a new file in `template/.claude/agents/<Name>.md` with a generic version
4. Reference it in `template/.claude/SUBAGENT-GUIDE.md` if relevant
5. Log it in `EVOLUTION-LOG.md`

Inverse: if a subagent in the template proves unnecessary or bad → archive it in `EVOLUTION-LOG.md` with the reason and remove from `template/`.
