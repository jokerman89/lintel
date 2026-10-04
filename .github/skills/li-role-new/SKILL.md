---
name: li-role-new
description: Use to create a durable role through a guided interview or update its expertise with a reviewed-digest, sensitivity-aware change.
---

> **Lintel on GitHub Copilot.** Generated from `skills/role-new/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/role-new/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/role-new/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Role new

The retained create/update entry delegates to the role owner's
[complete lifecycle](../../../skills/role/references/lifecycle.md#create-and-update-entrypoints).

- `/li-role-new`: use the adaptive interview and reviewed-draft publication.
- `/li-role-new --update <id>`: use the targeted update procedure and expected digest;
  when omitted, the ID defaults to the actual active role, never an invented choice.

Read that method before acting. Preserve every expertise section, explicit sensitivity,
private-body consent, destination review and conflict-safe update. Neither operation
activates a role or private synchronization. One-off personas stay conversation context;
customer PII and credentials do not belong in a role file.

Existing-role selection remains `/li-role <id>`; discovery remains `/li-roles-list`.
