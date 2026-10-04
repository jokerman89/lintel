---
name: li-scaffold-internal-tool
description: Use for the retained internal-tool scaffold entry; delegates the selected CLI, service, dashboard or script intent to scaffold's owned method in internal-tool mode.
---

> **Lintel on GitHub Copilot.** Generated from `skills/scaffold-internal-tool/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/scaffold-internal-tool/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/scaffold-internal-tool/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Scaffold an internal tool

Delegate to [scaffold](../../../skills/scaffold/SKILL.md#application-mode-acceptance-one-owner)
with the existing `--mode internal-tool`. Preserve supplied `--name`, `--path`,
`--language`, `--type` and `--ci`, existing acceptance answers, selected map/profile
and authority. `--path` maps to the explicit working target, never a basename guess.

Scaffold owns the application acceptance/failure questions and the actual
`bin/li-scaffold init` operation. Retain CLI, service, dashboard and automation-script
intent, but do not repeat its interview, stack advice or foundation-copy procedure.
Intent-only options are not blindly forwarded as helper flags.

Follow that owner's source/target, collision, profile and recovery checks, no-install
without authority, actual flow verification and handoff limits. This alias grants no
extra write, deployment, publication or private synchronization authority.
