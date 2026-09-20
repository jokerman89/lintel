---
name: context-save
layer: foundation
description: Use before the context window fills up or before clearing the session to save the current state to a checkpoint file. Reach for it when a session is getting heavy and you want to preserve where you are so a later session can pick up exactly here.
color: blue
tools: Read, Write, Bash, Grep, Glob
voice: internal
cli_support: [claude-code]
---

# /context-save

Save the current session's load-bearing state to a checkpoint file so a fresh session can resume cold. Use **before** context bloat hits productivity, OR when handing off to a teammate, OR when ending a session mid-task.

## When to use

- An actually available watcher or host observation suggests checkpointing before a fresh session
- You're ending a multi-day task mid-flight and the next session needs the full picture
- You're handing the session off to a teammate
- Before running `/clean` (it offers to call this first)

## When NOT to use

- Single short task that doesn't span sessions — save is overkill
- Pure question / lookup tasks — nothing stateful to save

## Inputs

- **No required arguments.** The skill reads:
  - Current checkpoint branch via `_context_branch` from `bin/_context.sh`, including
    the historical `HEAD` bucket for a detached committed checkout
  - SLUG via `_context_repo_slug` from `bin/_context.sh` (native — basename of the repo root; no external binary)
  - Recent uncommitted work via `git status -s` + `git diff --stat HEAD`
  - Active TODOs (this skill's own TodoWrite state if available, else `.claude/plans/todo.md`)
  - Last 3 user turns (operator pastes them if not introspectable)

- **Optional argument:** a short label describing the in-flight task (used as filename suffix, passed to `context_save_path` as `[label]`). `--label` covers the named-snapshot use case — the former standalone snapshot skill is folded into this one (its old name routes here via `config/aliases.yaml`).

## Workflow

1. Resolve slug + branch + timestamp.
2. Compute the checkpoint path via the mechanical core (`bin/_context.sh` owns naming + directory creation; checkpoint CONTENT stays LLM-written):

   ```bash
   source "${LINTEL_SOURCE_ROOT:?Set the trusted Lintel source root}/bin/_context.sh"
   path=$(context_save_path "${label:-}") || exit 1
   ```

   `context_save_path` reserves an empty file at `.claude/runtime/sessions/<branch>/<YYYYMMDD-HHMMSS>-r<repository-key>-<slug>[-<label>]-context-save.md` and creates the directory. It refuses unsafe directories and chooses a collision suffix instead of overwriting. The key identifies the canonical repository path, including the shared legacy directory. The filename ends `-context-save.md` so restore/warm readers match; empty reservations are not discoverable checkpoints.
3. Gather:
   - **What the task is** — one-line description (operator-provided or inferred from recent turns).
   - **What got done** — bulleted from todo-list completed items + recent commit messages on this branch.
   - **What's in-flight** — active todo items + dirty git tree summary.
   - **What's next** — top 1-3 next steps.
   - **Decisions taken** — surface any AskUserQuestion answers from the session (operator-noted).
   - **Failed attempts** — patterns/approaches tried that didn't work (so next session doesn't re-try).
   - **Files touched** — `git diff --name-only HEAD` + any uncommitted-but-staged files.
   - **Bounded restart sources** — explicit relative paths for the next step, not every file
     mentioned in the conversation. Use `context_select` to preview their actual sizes and
     missing/excluded files. Preserve any already-selected work/spec/task artifact references;
     do not guess a different initiative or create a second task source.
4. Write the checkpoint content to `$path` with this structure:

```markdown
# Checkpoint — <one-line task description>

**Slug:** <slug>
**Repository:** <canonical absolute repository root from _context_repo_identity>
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

5. Confirm the write succeeded and is nonempty, then run `context_checkpoint "$path"` to
   verify the owned read path and show its size/digest. Only then report a saved checkpoint.
   This reads metadata; the checkpoint content remains agent-written and must also be reviewed.
   Print the exact path so the operator can resume it.

## Report format

```
✓ Checkpoint saved
  Path: <full path>
  Size: <bytes>
  Resume: /context-restore <path>
```

## Edge cases

- **No git repo:** still save using the installed Git hashing tool, with branch `no-branch`.
  Slug derives from the explicit root/cwd basename. An unborn Git branch retains its actual name.
- **No `.claude/runtime/sessions/<branch>/`:** `context_save_path` creates it.
- **Existing checkpoint with same timestamp:** reserve a `-copyNNNN` suffix. Never overwrite.
- **Operator pastes recent turns inline:** capture them verbatim under a `## Recent turns (operator-pasted)` section.

## Compliance integration

This skill writes a checkpoint outside the committed tree (to the gitignored `.claude/runtime/sessions/`). Per Lintel Layer 2:
- The checkpoint file may contain references to in-flight work that touched files in the repo. Operator confirms NO customer-data is captured in the checkpoint before saving.
- Default sanity-grep before write: if the checkpoint text matches secret-shaped patterns, halt and surface to operator.

## Failure modes

- **Write fails (disk full / permission denied):** report failure and preserve any local draft;
  do not claim success or dump possibly sensitive checkpoint content to another surface.
- **Slug resolution fails:** fall back to `unknown-project`.
- **No Git branch:** `no-branch` placeholder; a detached committed checkout uses `HEAD`.
  A missing Git/Python tool or invalid directory is an explicit failure, not a saved checkpoint.

## Examples

**Mid-task save with label:**
```
> /context-save phase-2-skills-batch-1
✓ Checkpoint saved
  Path: .claude/runtime/sessions/main/20260527-153022-lintel-phase-2-skills-batch-1-context-save.md
  Resume: /context-restore .claude/runtime/sessions/main/20260527-153022-lintel-phase-2-skills-batch-1-context-save.md
```

**No label:**
```
> /context-save
✓ Checkpoint saved
  Path: .claude/runtime/sessions/main/20260527-153455-lintel-context-save.md
```

## See also

- `/context-restore` — read a checkpoint into a fresh session
- `/li:resume` — **paired with this skill**: resume discovers these checkpoints (newest-first via `context_latest`) and, when no cycle ledger exists, offers `/li:context-restore <path>` instead of misdirecting to a fresh cycle
- `/clean` — manual self-maintenance trigger (offers to call this first)
- Layer 4 `li-token-watcher` hook — surfaces this skill when token thresholds hit

This saves continuity notes, not a backup of source bytes or a change to the host's active
context. Owned file rollback uses `bin/li-snapshot.py` through `/li:safe-install`; never
confuse it with reading a Markdown checkpoint. Hook references above apply only when that
host integration was actually configured and observed.
