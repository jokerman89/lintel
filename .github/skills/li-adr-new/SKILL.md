---
name: li-adr-new
description: Use when a non-trivial decision needs recording to bootstrap a new Architecture Decision Record from the template, asking context-gathering questions to fill Status, Context, Decision, and Consequences. Reach for it whenever you've made or are about to make an architectural choice worth a durable record.
---

> **Lintel on GitHub Copilot.** Generated from `skills/adr-new/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the adr-new skill.

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

1. **Locate ADR directory.** Check `.claude/decisions/` exists. If not, recommend scaffolding init first.

2. **Find next ADR number.** Scan existing `.claude/decisions/NNNN-*.md` files. Next = max + 1.

3. **Read template.** `.claude/decisions/TEMPLATE.md` exists? If yes, load. If no, fall back to standard ADR format.

4. **Gather context via ask_user (sequence):**

   - **Title** — one-line decision summary.
   - **Context** — what is the situation that prompts this decision?
   - **Decision** — what we will do.
   - **Alternatives considered** — what else was on the table?
   - **Consequences** — what becomes easier? Harder? What risks?
   - **Related ADRs** — supersedes / informed by?

5. **Generate slug.** From title, kebab-case, ≤6 words.

6. **Write ADR file.** `.claude/decisions/<NNNN>-<slug>.md`. Status: Proposed by default.

7. **Commit.** Branch + commit:
   ```bash
   git checkout -b adr-<NNNN>-<slug>
   git add .claude/decisions/<NNNN>-<slug>.md
   git commit -m "adr: <NNNN> <title>"
   ```

8. **Report.** Path + branch + next-step prompt.

## Output format

```
ADR-NEW: <NNNN>-<slug>

Title: <title>
Status: Proposed
File: .claude/decisions/<NNNN>-<slug>.md
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

- **No `.claude/decisions/` directory** — recommend `bin/li-scaffold init` first.
- **Decision already documented in lessons.md** — recommend cross-reference.
- **Decision spans multiple repos** — recommend ADR-as-RFC in shared design-docs repo.
- **TEMPLATE.md custom** — respect repo customization; load whatever's there.

## ADR is part of session-harness

ADRs travel with the repo. Future Claude sessions read them at session-start (per CLAUDE.md). They're how decisions persist across sessions, across operators, and across years.

This skill is the bootstrap. Maintaining ADRs is operator-discipline.
