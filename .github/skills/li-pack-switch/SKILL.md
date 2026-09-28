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

Change policy context only for the selected working repository and configured operator
store. Follow [lifecycle paths](../../../docs/lifecycle.md); a bare install, source bundle,
working target and profile pointer are different things.

## Workflow

1. Read the current `profile-status`, then `pack-validate <target>` through the source-owned
   helper. Show the current and requested effective voice, compliance, navigation, persona,
   role and extension fields. A changed policy can invalidate the current plan and review.
2. Establish authorization for this target and reason. An explicit operator switch is
   already authorization; ask only for a missing decision. Never replace a repository's
   required pack or silently remove `LINTEL_PROFILE_PACK` to make the switch succeed.
3. Run the actual helper and retain its exit status:

   ```bash
   bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
     --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" \
     pack-switch "$target" --reason "$reason"
   ```

4. Report `changed`, the effective pack, actual configured pointer and full returned
   reference: schema_version, context_id, generation, digest, name and version. A repeated
   switch to the already effective target is a verified no-op, not a new activation.
5. Carry the returned reference into subsequent work only as part of this explicit switch.
   Older handoffs must fail their reference check; replan affected work and obtain fresh
   review. Ordinary bootstrap verifies a pin and never silently adopts the new generation.

The helper consumes `LINTEL_PACKS_DIR` and `LINTEL_ACTIVE_PACK_FILE`, validates before
writing, atomically writes the configured pointer and invokes the accepted structured
rebind API. Profile history retains the previous generation and reason. Do not maintain
another parser, raw cache, home pointer or independent hand-written audit receipt.

## Drift and interrupted switching

`PROFILE_DRIFT`, missing history, invalid required packs and incompatible schema/product/
capability constraints are unresolved errors, never neutral success. A failed binding
after the pointer write is `PROFILE_SWITCH_INCOMPLETE`, not "active next session".
Preserve both pointer and history, inspect the error, then use an explicitly reasoned
rebind through the same helper:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" \
  profile-rebind --pack "$target" --reason "$recovery_reason"
```

Do not automatically roll back, delete a context, forge a reference or retry against a
different target. The legacy `clear_pack_cache` accessor remains an explicit reasoned
rebind compatibility path, not a way to discard history.

## Extension and host boundary

An extension pack still contributes its declared namespace, workflow and specialist
methods. Show those from the validated target values, including which surfaces it
declares. Identity selection does **not** install/discover plugins, register hooks, grant
permissions, copy private packs or switch models. Use the actual host-supported extension
operation separately with its own authorization and observed discovery evidence.
