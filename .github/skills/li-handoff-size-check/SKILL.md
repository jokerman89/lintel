---
name: li-handoff-size-check
description: Use for the retained handoff-budget entry point; delegates selected artifacts and supplied observations to context-budget.
---

> **Lintel on GitHub Copilot.** Generated from `skills/handoff-size-check/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/handoff-size-check/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/handoff-size-check/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Handoff-size check compatibility

Use `/li-context-budget --handoff` with the supplied selection and observation
arguments. The [context-budget owner](../../../skills/context-budget/SKILL.md#handoff---handoff)
owns artifact admission, interpretation, policy boundaries and recovery.
PLAN/CAPTURE invoke that owner directly; this name remains compatible.

Retain explicit `--map`, the verified lifecycle's `LINTEL_WORK_MAP`, literal
`--warm-path`, observation/reserve flags and original work/profile/task identities.
Advisory unknown headroom remains unknown. Caller skip flags mean not run, never
a pass or a waiver of a required bound. Do not add another routing selector.

For mapped work, the compatibility recipe calls the same owned reference:

```bash
source_root="${LINTEL_SOURCE_ROOT:?Set the trusted Lintel source root}"
bash "$source_root/skills/context-budget/references/route.sh" --handoff "$@"
```

Legacy positional plans and `--plan <path>` keep the owner's
[explicit selected-plan/manual join](../../../skills/context-budget/SKILL.md#legacy-selected-plan).
They are not passed to the mapped reader, dropped or converted into an invented map.
