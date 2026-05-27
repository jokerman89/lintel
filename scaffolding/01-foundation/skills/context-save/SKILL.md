---
name: jstack-context-save
description: Save current session state to a checkpoint file. Use before context bloat or before /clean.
color: blue
tools: Read, Write, Bash, Grep, Glob
voice: internal
cli_support: [claude-code]
---

# /context-save

Save the current session's load-bearing state to a checkpoint file so a fresh session can resume cold. Use **before** context bloat hits productivity, OR when handing off to a teammate, OR when ending a session mid-task.

## When to use

- Token watcher fired a warning (~50k tokens or more) and you want to restart in a fresh session
- You're ending a multi-day task mid-flight and the next session needs the full picture
- You're handing the session off to a teammate
- Before running `/clean` (it offers to call this first)

## When NOT to use

- Single short task that doesn't span sessions — save is overkill
- Pure question / lookup tasks — nothing stateful to save

## Inputs

- **No required arguments.** The skill reads:
  - Current branch via `git branch --show-current`
  - SLUG via `gstack-slug` if available, else basename of repo
  - Recent uncommitted work via `git status -s` + `git diff --stat HEAD`
  - Active TODOs (this skill's own TodoWrite state if available, else `tasks/todo.md`)
  - Last 3 user turns (operator pastes them if not introspectable)

- **Optional argument:** a short label describing the in-flight task (used as filename suffix).

## Workflow

1. Resolve slug + branch + timestamp.
2. Compute checkpoint path: `~/.gstack/projects/<slug>/checkpoints/<branch>-<YYYYMMDD-HHMMSS>[-<label>].md`.
3. Gather:
   - **What the task is** — one-line description (operator-provided or inferred from recent turns).
   - **What got done** — bulleted from todo-list completed items + recent commit messages on this branch.
   - **What's in-flight** — active todo items + dirty git tree summary.
   - **What's next** — top 1-3 next steps.
   - **Decisions taken** — surface any AskUserQuestion answers from the session (operator-noted).
   - **Failed attempts** — patterns/approaches tried that didn't work (so next session doesn't re-try).
   - **Files touched** — `git diff --name-only HEAD` + any uncommitted-but-staged files.
4. Write the checkpoint file with this structure:

```markdown
# Checkpoint — <one-line task description>

**Slug:** <slug>
**Branch:** <branch>
**Timestamp:** <ISO 8601>
**Last commit:** <sha> — <message>

## Task

<2-3 sentences on what's being done and why>

## Done

- [x] item 1
- [x] item 2

## In flight

- [ ] item 3 — <current state, what's blocking>
- [ ] item 4

## Next

1. <very specific next step>
2. <step 2>
3. <step 3>

## Decisions taken

- D1: <decision> — <one-line rationale>
- D2: ...

## Failed attempts

- <approach tried> — <why it didn't work>

## Files touched

- file1.ts
- file2.md

## Resume command

To restore this session: `/context-restore <checkpoint-path>` OR paste this file into a fresh session.
```

5. Print the path so operator can copy/share it.

## Report format

```
✓ Checkpoint saved
  Path: <full path>
  Size: <bytes>
  Resume: /context-restore <path>
```

## Edge cases

- **No git repo:** still save, but `branch` field is `no-git`. Slug derived from cwd basename.
- **No `~/.gstack/projects/<slug>/`:** create it.
- **Existing checkpoint with same timestamp:** suffix with `-2`, `-3`, etc. Never overwrite.
- **Operator pastes recent turns inline:** capture them verbatim under a `## Recent turns (operator-pasted)` section.

## Compliance integration

This skill writes a file outside the repo (to `~/.gstack/`). Per JStack Layer 2:
- The checkpoint file may contain references to in-flight work that touched files in the repo. Operator confirms NO customer-data is captured in the checkpoint before saving.
- Default sanity-grep before write: if the checkpoint text matches secret-shaped patterns, halt and surface to operator.

## Failure modes

- **Write fails (disk full / permission denied):** report error, print checkpoint content to stdout so operator can copy it manually.
- **Slug resolution fails:** fall back to `unknown-project`.
- **Branch resolution fails:** `no-git` placeholder.

## Examples

**Mid-task save with label:**
```
> /context-save phase-2-skills-batch-1
✓ Checkpoint saved
  Path: ~/.gstack/projects/jstack/checkpoints/main-20260527-153022-phase-2-skills-batch-1.md
  Resume: /context-restore ~/.gstack/projects/jstack/checkpoints/main-20260527-153022-phase-2-skills-batch-1.md
```

**No label:**
```
> /context-save
✓ Checkpoint saved
  Path: ~/.gstack/projects/jstack/checkpoints/main-20260527-153455.md
```

## See also

- `/context-restore` — read a checkpoint into a fresh session
- `/clean` — manual self-maintenance trigger (offers to call this first)
- Layer 4 `jstack-token-watcher` hook — surfaces this skill when token thresholds hit
