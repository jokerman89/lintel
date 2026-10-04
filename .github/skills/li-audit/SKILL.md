---
name: li-audit
description: Use to read selected audit records and diagnostics, including hook or usage observations, without inferring execution from missing logs.
---

> **Lintel on GitHub Copilot.** Generated from `skills/audit/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/audit/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/audit/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Audit

Owns the [shared audit and hook observation method](../../../skills/audit/references/method.md).
Retain `--category <name>`, `--kind <kind>`, `--since <days>` and `--limit <N>`
(default 50 displayed rows). No arguments lists actual categories and counts.

Follow the shared method and its source-owned `read.sh`; it delegates path selection
to `_audit.sh` and parsing to `li-events.py`. `hooks-status` delegates its existing
view flags to that same method. Neither front door writes logs or creates state.
Missing logs remain unobserved; malformed records and reader errors stay visible.

In-flight work belongs to `status`/`jobs`; Git history is not this event trail.
Producers keep the existing audit writer. Do not edit history or treat a reader as
proof of enforcement, host activation or delivery.
