---
name: li-adr-new
layer: foundation
description: Bootstrap a new ADR (Architecture Decision Record) from template, with context-gathering questions.
color: cyan
tools: Read, Bash, Edit, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the adr-new skill.

## What this skill does

Creates a new ADR file from `docs/adr/TEMPLATE.md`, named per next-available number (e.g., `0042-<slug>.md`). Asks context-questions to populate Title, Context, Decision, Consequences sections. Commits on feature branch.

## When to use

- Non-trivial architectural decision being made
- Operator wants to record decision rationale durably
- Pattern emerges that future contributors should understand
- After /office-hours or /plan-eng-review session that produced a decision

## When NOT to use

- Trivial decisions (file names, single-line config) — comment in code suffices
- Decisions that aren't final yet — wait until decision lands
- Replays of existing ADRs — update existing, don't create new

## Workflow

1. **Locate ADR directory.** Check `docs/adr/` exists. If not, recommend scaffolding init first.

2. **Find next ADR number.** Scan existing `docs/adr/NNNN-*.md` files. Next = max + 1.

3. **Read template.** `docs/adr/TEMPLATE.md` exists? If yes, load. If no, fall back to standard ADR format.

4. **Gather context via AskUserQuestion (sequence):**

   - **Title** — one-line decision summary.
   - **Context** — what is the situation that prompts this decision?
   - **Decision** — what we will do.
   - **Alternatives considered** — what else was on the table?
   - **Consequences** — what becomes easier? Harder? What risks?
   - **Related ADRs** — supersedes / informed by?

5. **Generate slug.** From title, kebab-case, ≤6 words.

6. **Write ADR file.** `docs/adr/<NNNN>-<slug>.md`. Status: Proposed by default.

7. **Commit.** Branch + commit:
   ```bash
   git checkout -b adr-<NNNN>-<slug>
   git add docs/adr/<NNNN>-<slug>.md
   git commit -m "adr: <NNNN> <title>"
   ```

8. **Report.** Path + branch + next-step prompt.

## Output format

```
ADR-NEW: <NNNN>-<slug>

Title: <title>
Status: Proposed
File: docs/adr/<NNNN>-<slug>.md
Branch: adr-<NNNN>-<slug>

Sections populated:
- ✓ Context
- ✓ Decision
- ✓ Alternatives
- ✓ Consequences
- ✓ Related ADRs

Next:
- [ ] Review draft
- [ ] git push + open PR
- [ ] Update status to "Accepted" when merged
```

## Edge cases

- **No `docs/adr/` directory** — recommend `bin/lintel:li-scaffold init` first.
- **Decision already documented in lessons.md** — recommend cross-reference.
- **Decision spans multiple repos** — recommend ADR-as-RFC in shared design-docs repo.
- **TEMPLATE.md custom** — respect repo customization; load whatever's there.

## ADR is part of session-harness

ADRs travel with the repo. Future Claude sessions read them at session-start (per CLAUDE.md). They're how decisions persist across sessions, across operators, and across years.

This skill is the bootstrap. Maintaining ADRs is operator-discipline.
