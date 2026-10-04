---
name: li-pack-switch
description: Use to explicitly switch the effective pack through the structured profile lifecycle, preserving required policy, configured paths and generation-bound recovery.
---

> **Lintel on GitHub Copilot.** Generated from `skills/pack-switch/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/pack-switch/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/pack-switch/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Pack switch

This entry owns the [shared pack lifecycle](../../../skills/pack-switch/references/lifecycle.md#switch).
Follow its validation, authorization, real helper invocation, full returned
reference and interruption/recovery procedure. An explicit switch request already
authorizes its stated scope; ask only for missing decisions.

The existing `pack-list`, `pack-validate`, `pack-create` and `pack-switch` names
remain. Read-only discovery/validation never implies mutation. A switch changes
the selected policy context; it does not install plugins, activate hooks, grant
host permission or select models. Required-policy errors stay blocked.
