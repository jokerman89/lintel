---
name: li-lessons-promote
layer: foundation
description: Promote a repo-local lesson from tasks/lessons.md to Lintel's global lessons (scaffolding/01-foundation/tasks/lessons.md) so all future scaffolded repos inherit it.
color: cyan
tools: Read, Bash, Edit, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the lessons-promote skill.

## What this skill does

Promotes a single lesson from the current repo's `tasks/lessons.md` to Lintel's global `scaffolding/01-foundation/tasks/lessons.md`. Once promoted, every new repo scaffolded via `lintel scaffold init` includes that lesson as baseline.

This is how operator-discovered patterns become team-wide knowledge.

## When to use

- A lesson learned in current repo is genuinely general (not repo-specific)
- Multiple repos would benefit from the same correction
- Pattern is durable (not a passing fad)

## When NOT to use

- Repo-specific lesson (file paths, project-specific glue) — keep local
- Speculative — should be a discovery from real correction
- Lesson hasn't proven itself in current repo (let it bake first)

## Workflow

1. **Read current repo's lessons.md.** Verify file exists at `tasks/lessons.md`.

2. **Ask operator which lesson to promote.** AskUserQuestion with numbered list of lessons in current repo. Recommend the most-cited or oldest.

3. **Generalize the lesson.** Strip repo-specific paths, file names, project nouns. Replace with generic terms.

4. **Locate Lintel global lessons.**
   - Lintel repo path: `~/Workspace/jokerman-lintel` or operator-configured
   - Global lessons file: `scaffolding/01-foundation/tasks/lessons.md`

5. **Check for duplicate.** Grep the generalized lesson title in global lessons. Skip if duplicate.

6. **Append to global lessons.** Format:
   ```markdown
   ## YYYY-MM-DD — <generalized title>
   <generalized lesson body>
   <-- Promoted from <source-repo-name> on <date> by <operator>. -->
   ```

7. **Commit in Lintel repo.** Branch + commit:
   ```bash
   cd $LINTEL_HOME
   git checkout -b promote-lesson-<slug>
   git add scaffolding/01-foundation/tasks/lessons.md
   git commit -m "lessons: promote <title> from <source-repo>"
   ```

8. **Output PR link template** (operator pushes when ready).

## Output format

```
LESSONS-PROMOTE: <lesson title>

Source repo: <name>
Original entry: <date>
Generalized: <yes/no>

Generalized text:
---
<output>
---

Action:
- ✓ Appended to Lintel scaffolding/01-foundation/tasks/lessons.md
- ✓ Branch created: promote-lesson-<slug>
- Next: cd $LINTEL_HOME && git push && open PR
```

## Edge cases

- **Operator can't decide which lesson** — list with frequency-of-reference and let them pick.
- **Lesson contains customer data** — STOP, refuse. Recommend repo-only retention.
- **Multiple lessons could be promoted** — do one at a time. Run skill again for next.

## Why this matters

Session-harness compounds value when lessons travel across sessions and repos. Per-repo lessons stop at repo boundary. Promoted lessons reach every future engagement.

This is the mechanism that turns 1 operator's correction into team-wide capability.
