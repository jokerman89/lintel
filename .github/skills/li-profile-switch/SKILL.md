---
name: li-profile-switch
description: Inspect host install state and guide explicitly supported activation or owned snapshot recovery, without inventing plugin controls.
---

> **Lintel on GitHub Copilot.** Generated from `skills/profile-switch/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** `<base>` and this skill's `scripts/`, `references/` and `data/` mean
>   `../../../skills/profile-switch/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/profile-switch/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Host install profiles

Preserve the useful status, temporary disable/re-enable, named snapshot and previous-setup
recovery entry points. This skill controls **host installation intent**, not the effective
company pack or a conversation's audience lens. Use `/li-pack-switch` for policy context
and `/li-role --audience <name>` for a temporary audience.

## Status and host operations

Resolve the exact client surface and [lifecycle roots](../../../docs/lifecycle.md). Start with:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" \
  host-profile status --client "$client"
```

The shipped helper reports activation as `unverified`; it does not infer activity from
cached plugin files, an executable in PATH, or a declared capability. `/li-doctor` checks
local file integrity separately.

`--dormant` and `--activate` map to `host-profile dormant|activate`. They currently return
`UNSUPPORTED_HOST_OPERATION` without mutation: no enable/disable binding ships here.
Keep the request useful by handing off to the exact host's documented controls or an
actually available authorized tool. Identify installed plugin identity/version first,
obtain any required host permission, perform only that operation, then inspect discovery
in a new session. Report success only after observing the requested change. If no such
operation is available, stop at unsupported/manual, not simulated success.

Never create a guessed disable marker, alter arbitrary plugin trees, rewrite model
configuration or treat a pack preference as a plugin on/off switch.

## Snapshot, list and restore aliases

`--snapshot <label>`, `--list` and `--restore <id>` retain their recovery purpose through
the [owned snapshot workflow](../../../skills/safe-install/SKILL.md):

- Select an explicit installation root, separate private store and exact owned paths.
- Use source-owned `bin/li-snapshot.py create|list|verify|restore`. Retain the returned
  exact snapshot ID; a human label is only a label, not a guessed directory selector.
- An operation must bind its own verified result before restore can replace changed
  files. A copied host directory without ownership/postimage evidence is not that result.
- Explicit restore preflights all bytes, refuses later edits and records per-file
  progress. Do not auto-restore another snapshot after failure.

Old named backups and predecessor archives remain available for read-only inspection.
They lack the verified ownership format, so restoration requires a separately reviewed
file-level plan; do not relabel them or remove them because they are old.

## Boundaries and result

No broad host-settings restore, recursive uninstall, private synchronization, hook
registration or default repository change occurs. File recovery cannot undo external
host/service side effects. Use actual host uninstall for activation removal; use an
owned installer receipt for file rollback, not deletion of the whole install root.

Report the requested mode, exact surface, observed status, performed mutation (or none),
snapshot/recovery identity, preserved user content and remaining manual host boundary.
One host succeeding never hides another host's failed or unverified operation.
