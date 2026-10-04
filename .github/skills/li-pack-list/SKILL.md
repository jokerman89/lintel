---
name: li-pack-list
description: List configured-store, repository and installed-source packs with resolver precedence, validation results and the actual effective profile.
---

> **Lintel on GitHub Copilot.** Generated from `skills/pack-list/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/pack-list/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/pack-list/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Pack list

Retained read-only front door to [pack lifecycle: list](../../../skills/pack-switch/references/lifecycle.md#list).
Use its actual configured-root inventory, selected/shadowed origins, effective
profile and diagnostics. Preserve `--validate` as the request for per-row details,
not a new helper option.

Use before selecting or creating a pack, or after an explicitly authorized identity
change. Listing binds nothing, changes no pointer and does not prove host activation.
Use `pack-validate` for effective fields and `pack-switch` for a policy-context change.
