---
name: li-hooks-status
description: Use to inspect recorded hook outcomes, overrides or unobserved hooks through the shared audit reader; absence is not an execution verdict.
---

> **Lintel on GitHub Copilot.** Generated from `skills/hooks-status/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/hooks-status/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/hooks-status/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Hooks status

Retained front door to audit's [hook observation method](../../../skills/audit/references/method.md#hook-views).
Select `--records`, `--overrides` or `--unobserved`, with optional `--days N`.
No view means `NEEDS_CONTEXT`; do not silently choose one.

Follow the shared reader, producer-field interpretation, aggregation and diagnostic
procedure. These flags choose a report, not new helper arguments. This entry writes
nothing and keeps absence unobserved.

This is not live hook detection or installation repair. For installed-byte questions,
use the doctor observation route named by the same method. Current host registration,
activation and execution remain unverified without their own actual evidence.
