---
name: context-restore
layer: foundation
description: Restore session state from a checkpoint file. Run at start of a fresh session that continues prior work.
color: blue
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code]
---

# /context-restore

Read a checkpoint file (written by `/context-save`) into a fresh session. Outputs a concise summary so you can pick up cold. The former cross-session dump skill is folded into this one — its old name routes here via `config/aliases.yaml`.

## When to use

- Starting a fresh session that continues yesterday's (or a teammate's) in-flight work
- After `/clean` led you to restart with reduced context
- When picking up a checkpoint shared by another SE on the team

## When NOT to use

- Starting fresh on a NEW task — there's no checkpoint to read
- Pure question / lookup — you don't need state restoration

## Inputs

- **Optional argument:** path to a specific checkpoint file.
- **No argument:** skill auto-discovers the most recent checkpoint for the current slug + branch.

## Workflow

1. **Resolve slug + branch** via `_context_repo_slug` (from `bin/_context.sh`, native — basename of the repo root; no external binary) + `git branch --show-current`.
2. **Find checkpoint** via the mechanical core (no raw `ls`/`find`):

   ```bash
   source "$LINTEL_REPO_ROOT/bin/_context.sh"   # fallback: "$(git rev-parse --show-toplevel)/bin/_context.sh"
   path=$(context_latest)        # newest checkpoint for the current branch
   context_list [branch]         # all checkpoints newest-first, when the operator wants to pick one
   ```

   - If argument provided: validate the path exists, read it (skip discovery).
   - Else: read `$(context_latest)`. Discovery already includes the legacy `~/.lintel/sessions/<branch>/` fallback (read-only; grace window to 2026-09-12).
3. **Parse checkpoint structure** — extract: task description, done, in-flight, next, decisions, failed attempts, files touched.
4. **Read referenced files** — for each file under "Files touched," `Read` it so subsequent edits land on accurate state (post-checkpoint changes may exist).
5. **Diff check** — `git log <last-commit-in-checkpoint>..HEAD` to surface any commits landed since checkpoint was written.
6. **Print restoration summary.**

## Report format

```
✓ Restored from <path>
  Original timestamp: <ISO>
  Slug/branch: <slug>/<branch>
  Last commit at save: <sha> (now: <current-sha> — <N commits since>)

## Task
<one-line>

## Where we were
- Done: <count> items
- In-flight: <count> items — <first item summary>
- Next: <count> steps — <first step summary>

## Important context
- <decision summaries, max 5>
- <failed attempts to avoid, max 3>

## Files in-flight
<list>

## Ready to continue
Suggested next action: <verbatim "next" step #1 from checkpoint>
```

## Edge cases

- **No checkpoint found:** report "no checkpoint for <slug>/<branch>. Start fresh or specify --path." Don't error — just inform.
- **Checkpoint references files that no longer exist:** flag each missing file, don't fail. Operator decides if it matters.
- **Commits landed since checkpoint:** state count + suggest `git log <checkpoint-sha>..HEAD` to review.
- **Checkpoint older than 7 days:** warn — "stale checkpoint, project state may have drifted significantly."
- **Multiple branches share checkpoints (rebase happened):** restore reads only checkpoints matching the current branch name.

## Compliance integration

- This skill READS a file outside the repo. The file may contain decisions, failed attempts, file paths.
- Operator confirms the checkpoint is theirs (or shared with them by an authorized teammate) before reading. Sharing checkpoints across SEs is fine for same project; cross-customer checkpoints are NOT fine.

## Failure modes

- **Checkpoint file unreadable:** report error, suggest operator pastes content inline as fallback.
- **Slug/branch mismatch:** the checkpoint was for a different project. Surface, ask operator if they want to continue anyway.
- **Files referenced moved/renamed since checkpoint:** flag, operator clarifies new paths.

## Examples

**Auto-discover latest:**
```
> /context-restore
✓ Restored from .claude/runtime/sessions/main/20260527-153022-lintel-phase-2-skills-batch-1-context-save.md
  Original timestamp: 2026-05-27T15:30:22Z
  Slug/branch: lintel/main
  Last commit at save: 7e7a021 (now: 7e7a021 — 0 commits since)

## Task
Phase 2 internal-voice skills, batch 1 (5 skills)

## Where we were
- Done: 2 items (Phase 1, voice eval skeletons)
- In-flight: 1 item — writing 5 operational skills
- Next: 3 steps — finish remaining skills, commit, push

## Files in-flight
- scaffolding/01-foundation/skills/context-save/SKILL.md
- scaffolding/01-foundation/skills/context-restore/SKILL.md

## Ready to continue
Suggested next action: complete /clean, /help, /health skills
```

**With explicit path:**
```
> /context-restore .claude/runtime/sessions/main/20260526-225146-lintel-context-save.md
...
```

## See also

- `/context-save` — write the checkpoint this skill reads
- `/li:resume` — **paired with this skill**: resume discovers context-save checkpoints (newest-first via `context_latest`) and, when no cycle ledger exists, routes the operator here with `/li:context-restore <path>`
- `/clean` — companion self-maintenance command
