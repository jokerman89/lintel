---
name: li-perf-mode
description: Use for the retained resource-advice entry point on heavy work; delegates to context-budget without changing model capacity.
---

> **Lintel on GitHub Copilot.** Generated from `skills/perf-mode/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/perf-mode/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/perf-mode/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Perf mode compatibility

Use `/li-context-budget --advice` with the supplied arguments. The
[context-budget owner](../../../skills/context-budget/SKILL.md#advice---advice) owns the method,
observations, interpretation and recovery. Do not maintain a second procedure here.

Retain numeric `--budget`, `--ceiling`, `--decay-policy`, `--cost-estimate`, `--off`
and the original observation flags. This route is advice only, not a larger model
window, host setting or paid service. Do not add another routing selector.

The executable compatibility route uses the same owned reference:

```bash
source_root="${LINTEL_SOURCE_ROOT:?Set the trusted Lintel source root}"
bash "$source_root/skills/context-budget/references/route.sh" --advice "$@"
```
