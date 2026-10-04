---
name: li-lessons-promote
description: Promote one ID-managed project lesson into an explicitly named Lintel work tree's scaffolding baseline, with recorded provenance and no implicit branch, commit or push.
---

> **Lintel on GitHub Copilot.** Generated from `skills/lessons-promote/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/lessons-promote/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/lessons-promote/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the lessons-promote skill. You run `bin/li-lessons-promote`; there is no separate Git
recipe in this skill.

## When to use

- A lesson learned in current repo is genuinely general (not repo-specific)
- Multiple repos would benefit from the same correction
- Pattern is durable (not a passing fad)

## When NOT to use

- Repo-specific lesson (file paths, project-specific glue) — keep local
- Speculative — should be a discovery from real correction
- Lesson hasn't proven itself in current repo (let it bake first)

## Workflow

1. **Select the lesson by ID.** The source is the project store (`lintel_lessons_file`) or an
   explicit `--source <file>`. List candidates with `lessons_index` from `lib/memory.sh`, then
   choose one `L-NNN`; interactive use lists every lesson by ID, never only the first 30.
   Apply the [benefit and recurrence method](../../../skills/lessons-add/references/benefit.md):
   explain observed application, outcome and generalizability. Unknown benefit or
   unresolved repeat failures stay visible and can defer promotion; no automated
   reference counter or success score exists.
2. **Generalize the lesson.** Strip repo-specific paths, file names, project nouns and anything
   sensitive. Write the generalized text with exactly one level-two heading; the bin rewrites that
   heading to the destination's next ID.
3. **Choose the destination explicitly.** `--lintel-dir <work tree>` or `LINTEL_DIR`; a linked
   worktree is fine. The file `scaffolding/01-foundation/.claude/memory/lessons.md` must exist
   there. There is no default destination.
4. **Record a source label explicitly.** `--source-label` (`[A-Za-z0-9._-]{1,64}`) so a private
   or customer repository name is never copied implicitly. Add `--record-source-commit` or
   `--operator` only when the operator wants those recorded.
5. **Run the bin.** Default mode conditionally writes only the target file, prints its diff and
   the suggested commands, and leaves HEAD, branches and the index unchanged:
   ```bash
   bash "${LINTEL_SOURCE_ROOT:?select trusted source}/bin/li-lessons-promote" \
     --lintel-dir "$lintel_dir" --id L-NNN --generalized-file "$generalized" \
     --source-label "$label"
   ```
   To commit, add `--commit --expect-branch <branch>`: it commits only the target on that branch
   after checking that nothing is staged and the target is clean, then verifies that the new
   commit changed only the target. It never checks out, switches or creates a branch, pushes or
   opens a pull request.
6. **Report the exit.** 7 means already promoted (the existing ID is named, nothing written);
   8 a commit precondition; 9 a conditional-write conflict; 10 a failed commit whose bytes were
   restored; 11 a commit that was left in place because verification failed — follow the printed
   remedy, never reset automatically. The operator pushes and opens a pull request when ready.

## Provenance

The bin appends one comment to the promoted lesson:

```html
<!-- lintel-promotion: source_label=<label>; source_id=L-NNN; source_commit=<sha|unrecorded>; promoted_on=<YYYY-MM-DD> -->
```

The promoted lesson is then retrievable in the destination with
`bin/li-lessons.py get --id L-NNN --store <target>`.

## Output format

```
LESSONS-PROMOTE: L-NNN → <destination next ID>

Source: <label> <source id> (source_commit=<sha|unrecorded>)
Target: <destination>/scaffolding/01-foundation/.claude/memory/lessons.md
Sensitivity: operator-attested; no shared scanner ran on the generalized text.
<diff of the target>

Next (not run):
- git -C <destination> add -- scaffolding/01-foundation/.claude/memory/lessons.md
- git -C <destination> commit -m "docs(lessons): promote ..." -- scaffolding/01-foundation/.claude/memory/lessons.md
```

## Edge cases

- **Operator can't decide which lesson** — list IDs and the actual benefit/recurrence
  evidence, with unknowns explicit; let them choose or defer, never invent usage counts.
- **Lesson contains customer data** — STOP, refuse. Recommend repo-only retention.
- **Multiple lessons could be promoted** — do one at a time. Run skill again for next.
- **Destination or label missing** — the bin exits 2 before resolving anything; ask for them.

## Why this matters

Session-harness compounds value when lessons travel across sessions and repos. Per-repo lessons stop at repo boundary. Promoted lessons reach every future engagement.

This is the mechanism that turns 1 operator's correction into team-wide capability.
