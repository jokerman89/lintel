---
name: li-scaffold-mvp
description: Use for the retained MVP scaffold entry; delegates real-user and first-journey intent to scaffold's owned method in mvp mode, preserving evaluation and deployment boundaries.
---

> **Lintel on GitHub Copilot.** Generated from `skills/scaffold-mvp/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/scaffold-mvp/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/scaffold-mvp/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Scaffold an MVP

Delegate to [scaffold](../../../skills/scaffold/SKILL.md#application-mode-acceptance-one-owner)
with the existing `--mode mvp`. Preserve supplied `--name`, `--target-users`,
`--path`, `--stack`, `--has-ai`, `--deploy`, existing answers, selected work/profile
and authority. These are intent inputs, not new flags for the initializer.

Scaffold owns the first-journey success/failure questions, sanitized golden and
adversarial evaluation method, data/policy/voice concerns and actual
`bin/li-scaffold init` operation. Do not repeat its interview or foundation recipe.
Keep user framing and deployment preparation distinct from actual deployment.

Follow that owner's source/target, collision, profile and recovery checks,
no-install without authority, actual journey verification and independent
review/host handoff gates. A directory tree or deploy stub is not a working MVP.
