---
name: li-role
description: Use to take on or change a working role — activate one for a lightweight lens, turn it off, swap mid-session, apply its lens to an artifact, or load its full definition on demand. Reach for it when work would benefit from a specific role's perspective; one role is active at a time.
---

> **Lintel on GitHub Copilot.** Generated from `skills/role/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/role/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/role/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

The role skill owns the [shared role lifecycle](../../../skills/role/references/lifecycle.md) used by
this entry, `role-new` and `roles-list`. Read its selected procedure before acting.

## Actions

| Invocation | Does |
|---|---|
| `/li-role <role-id>` | Activate — light load (~500 tokens), sets `role_active` in profile |
| `/li-role --off` | Deactivate — clears overlay, voice tier reverts to mode/profile default |
| `/li-role --rotate <role-id>` | One validated set; failure retains the previous selection |
| `/li-role --frame <artifact>` | Apply the active role's outcome-lens to an artifact |
| `/li-role --deep-dive [role-id]` | Load the FULL role file (~2-3k tokens) on demand |
| `/li-role --audience [name]` | List or load an explicitly selected audience persona for this conversation without changing role/profile state |
| `/li-role --clear-audience` | Stop applying the audience overlay to future responses; persisted data and prior conversation remain |

Create or evolve role files with `/li-role-new` (and `/li-role-new --update <id>`); discover them with `/li-roles-list`.

## Method and authority

The shared lifecycle owns resolution, private consent, the real CLI invocations,
create/update interview, expected-digest conflict handling, listing, activation,
failure-safe rotation, off, framing, deep-dive and audience context. No additional
role parser or selector belongs here.

One working role is active at a time. A role file is not an installed agent or a
grant of host authority. Audience changes remain conversation-only, while persistent
set/off and role publication need the scope stated in that method.
