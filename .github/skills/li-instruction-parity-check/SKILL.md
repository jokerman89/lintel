---
name: li-instruction-parity-check
description: Use to verify shared session protocol equality and client-entry links without overwriting project prose or confusing similarity with authority.
---

> **Lintel on GitHub Copilot.** Generated from `skills/instruction-parity-check/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/instruction-parity-check/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/instruction-parity-check/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Instruction parity

Retained front door to doctor's [instruction parity procedure](../../../skills/doctor/references/inspection.md#instruction-parity).
Read that full method for ADR-0025's exact shared-protocol checks, client-entry links,
real source/consumer commands, malformed-marker handling and project-prose preservation.

This is read-only verification, not synchronization or a new doctor CLI flag.
Reuse a current actual adapter check rather than repeating it. Missing source,
failed checks and host limits stay explicit; repairs belong to an authorized owner.
