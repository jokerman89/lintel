---
name: li-doctor
description: Use to diagnose source, target, profile and installed-file integrity while keeping actual host activation explicitly unverified.
---

> **Lintel on GitHub Copilot.** Generated from `skills/doctor/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/doctor/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/doctor/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Doctor

Owns [local inspection](../../../skills/doctor/references/inspection.md) for diagnosis, instruction parity
and migration observations. Follow its real helper invocations and result interpretation,
not speculative host commands or a second path checklist.

Keep the existing options: `--json`, `--quick` / `--fast`, `--verbose`,
`--layers-only`, `--hooks-only`, `--upstream-only`. The filtered views are presentation,
not extra helper flags; JSON and the helper's full exit status remain intact.

`instruction-parity-check` and `migrations` retain their names and delegate to that
same owner. Diagnosis is read-only. Missing tools, drift, malformed inputs and
unverified host activation remain visible; any repair needs separate authority.
