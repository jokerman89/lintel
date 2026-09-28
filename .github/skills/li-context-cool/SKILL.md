---
name: li-context-cool
description: Exclude explicitly selected files from future context reads without claiming to remove already-sent conversation content.
---

> **Lintel on GitHub Copilot.** Generated from `skills/context-cool/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** `<base>` and this skill's `scripts/`, `references/` and `data/` mean
>   `../../../skills/context-cool/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/context-cool/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Context cool

Reduce the next working set when the task changes. Cooling cannot remove messages already
sent to the model. It performs no disk cleanup and cannot enlarge or reset a context window.
For an actual smaller conversation, save a checkpoint and use the host's new-session
operation, then restore only needed references.

## Workflow

1. Read the available source history (`.claude/runtime/state/context-budget.md`) and
   current selection manifests. Distinguish recorded reads from assumed active context.
2. Let the operator select literal paths or bounded globs to exclude. Reuse explicit
   authorization, but do not infer that an entire customer, repository or phase can be
   discarded from a vague "cool" request. Essential task/authority context must be retained.
3. Apply future exclusions through the shared reader:

```bash
source_root="${LINTEL_SOURCE_ROOT:?Set the trusted Lintel source root}"
source "$source_root/bin/_context.sh"
context_cool "$@"
```

Examples of argument arrays: `--path 'docs/old notes.md'`, `--glob 'experiments/**/*.md'`,
or `--clear` to allow those sources again. The helper writes the root-bound JSON file
`context-ignore.json` in the directory returned by `lintel_state_dir`. `context_select`
actually consumes it; a malformed or foreign record fails rather than silently losing
the exclusions. Show the exact source root and the resulting path/pattern list.
Literal exclusions also compare actual in-root file identity. Glob comparisons fold case
only when a read-only filesystem probe confirms a case alias for that path component;
case-sensitive directories retain distinct spelling, regardless of the operating system.

Historical `context-ignore.md` notes remain readable, but are not parsed as executable
selection policy. Review their literal paths and explicitly migrate the intended choices
with this command; never assert that an unconsumed old marker was enforced.

## Result and recovery

Report **future exclusions applied**, zero current-context tokens removed and zero disk
bytes removed. Do not subtract excluded-file estimates from observed or historical usage.
The policy applies to the selected repository's shared selector, not arbitrary host reads,
other agents or other repositories. Include it explicitly in a delegated retrieval handoff.

If saving state helps:

1. `/li-pause <label>` preserves decisions and next work.
2. Start a fresh session using the actual host operation.
3. `/li-resume --from <checkpoint>` reads the owned checkpoint and a bounded current-file set.
4. `/li-context-warm` previews only still-needed sources.

On a failed exclusions write, report failure; leave previous exclusions intact. Do not
delete source files, archives or checkpoints as a substitute for cooling.
