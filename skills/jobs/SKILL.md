---
name: jobs
layer: foundation
description: Use to see and steer in-flight Lintel jobs — list what's open, continue, replan, abort, or branch a job. The single source of truth for "what's open right now"; reach for it when you've lost track of running work or need to redirect it.
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

You are the `jobs` skill — lifecycle controller for in-flight Lintel curated flows (v3.8 Feature 1).

## What this skill does

Provides 5 subcommands to operate on `.claude/runtime/jobs/` (the repo-local job store):

- `list` (default) — surface `_active.md` (regenerated from job.yaml on every state change)
- `continue <id>` — resume the job at its `current_step` (delegates to `/li:resume` mechanic)
- `replan <id>` — re-run the whole job or pick which steps to redo (supports build-on, not just start-over)
- `abort <id>` — move job to `_archive/` with `status: aborted`, apply discard policy, skip keep-promotion
- `branch <id>` — create a parallel job from the same starting point (new job-id, copies job.yaml + outputs/)

Each operation regenerates `_active.md` so `/li:status` reflects current truth.
Mutation helpers maintain that derived view; `list` reads actual job records without
regeneration. Missing records are unobserved, not proof that no mapped work is open.
Jobs auto-spawn/hooks remain dormant unless separately activated and verified.
Apply [task-relevant intake](../define/references/intake.md): no fixed question API
and no automatic choice when a material decision is unresolved.

## When to use

- "What's open right now?" → `list` (or invoke `/li:status` for the same)
- "I want to pick up that customer-engagement cycle from Tuesday" → `continue <id>`
- "Restart this plan but keep the discovery output" → `replan <id>` with partial-redo prompt
- "Kill this. I started wrong." → `abort <id>`
- "I want to try the same design with motion=kinetic instead of moderate" → `branch <id>`

## When NOT to use

- Mid-task code-editing — jobs is lifecycle, not editing
- For non-workflow_root skills — single-shot diagnostics such as `/li:doctor` don't spawn jobs
- To enforce ordering between steps — that's `job.yaml.blocked_until`, evaluated by `job_can_start <id> <step>` in `bin/_jobs.sh`, not this skill

## Inputs

**`list`** — no args
**`continue <id>`** — `<id>` required (validates against jobs/<id>/)
**`replan <id>`** — `<id>` required; optional `--from <step>` to restart from specific phase
**`abort <id>`** — `<id>` required; optional `--reason "<text>"` (audit-logged)
**`branch <id>`** — `<id>` required; optional `--name <suffix>` (default: <orig>-branch-<N>)

## Workflow

### Step 1 — Parse subcommand

```bash
sub="${1:-list}"
job_id="${2:-}"
case "$sub" in
  list|continue|replan|abort|branch) ;;
  *) echo "Usage: /li:jobs <list|continue|replan|abort|branch> [<id>]"; exit 2 ;;
esac
```

### Step 2 — Source helper

```bash
BIN_DIR="${LINTEL_SOURCE_ROOT:?select trusted source}/bin"
export LINTEL_JOBS_NO_INIT=1
source "$BIN_DIR/_jobs.sh"
```

### Step 3 — Dispatch

**`list`:**
```bash
list_jobs --read-only
stale_jobs 24
```

**`continue <id>`:**
1. Verify `.claude/runtime/jobs/<id>/job.yaml` exists.
2. Determine the resume target. For a `tree`-schema plan, call
   `job_resume_point <id>` (deepest incomplete + startable WBS node-path, e.g.
   `1.1.a`); for flat/phased plans, read `current_step` from job.yaml. See
   `/li:resume` Step 2.5.
   For mapped work the original tasks and verified lifecycle reference remain
   authoritative; job steps are execution observations, not a second backlog.
   Retain blocked and unknown-age work in the report even when it is not startable.
3. Invoke `/li:resume --job <id>` (resume skill reads from job dir, not loose `.claude/runtime/state/00-state.md`).
4. Update last_touched.

**`replan <id>`:**
1. Verify job exists.
2. AskUserQuestion: "Replan whole job, OR pick a step to restart from?"
   - Whole → preserve existing history and original map/IDs, then select an explicit
     retry/loop-back through `/li:cycle`; do not erase evidence to simulate a fresh start
   - From step → operator picks; `/li:resume --from <step>` style
3. Update last_touched.

**`abort <id>`:**
1. Verify job exists.
2. AskUserQuestion confirm + optional `--reason`.
3. Call `job_archive <id> ABORTED`.
4. Surface `[lintel] Job <id> aborted, archived to _archive/<date>/<id>/`.

**`branch <id>`:**
1. Verify source job exists.
2. Use `job_create` for a distinct record; never copy the old `job_id` into a new folder.
3. Retain the original selected map as a reference. A new initiative needs explicit
   map selection, not copied approval/status or a directory name stripped from the job ID.
4. Copy only authorized inputs/output candidates, preserving source history and conflicts.
   They are candidates, not independently reviewed completion.
5. Use `job_update` for the new current step and verify actual persistence before
   reporting both records. There is no autonomous branch scheduler.

### Step 4 — Audit

The helpers in `bin/_jobs.sh` record their own operations in the `jobs` category
(`.claude/runtime/audit/jobs.jsonl` on the v5 layout): `job_begin` (`job_create`),
`job_set_steps`, `job_update` and `job_end` (`job_archive`). `job_stale_warn` is recorded by the
dormant `job-stale-warn` hook, not by `bin/_jobs.sh`. This skill emits no separate `job_action`
record; `continue`, `replan` and `branch` leave only the helper records they cause. These audit
lines are advisory, while a failed `job.yaml` write makes the helper return non-zero:

```json
{"ts":"...","kind":"job_update","operator":"...","cycle_id":"...","job_id":"...","step":"PLAN","status":"IN_PROGRESS"}
```

## Voice tier behavior

`voice: internal`. No customer-bound output. Operator-only.

## Status protocol

- **DONE** — operation completed, `_active.md` regenerated
- **DONE_WITH_CONCERNS** — operation succeeded with warnings (e.g., source job partially missing files; branch operation proceeded with caveats)
- **BLOCKED** — subcommand requires `<id>` but not provided, OR job doesn't exist
- **NEEDS_CONTEXT** — `replan` asked operator to pick scope but no answer

## Pause-points

- `abort` requires AskUserQuestion confirm (destructive — moves files out of working set)
- `replan whole` requires AskUserQuestion confirm (re-runs from scratch)
- `branch` proceeds without confirm (additive, non-destructive)

## Hop-in support

YES — solo-invocable. Designed to be called anytime.

## Integration

**Reads:**
- `.claude/runtime/jobs/_active.md` (repo-local active list)
- `~/.lintel/jobs/_active.md` (cross-repo registry — one line per open job across all repos, pointing at the owning repo)
- `.claude/runtime/jobs/<id>/job.yaml`
- `.claude/runtime/jobs/<id>/00-state.md`
- `~/.lintel/profile.yaml` (mode + stale threshold)

**Writes:**
- `.claude/runtime/jobs/<id>/job.yaml` (last_touched updates)
- `.claude/runtime/jobs/_active.md` (regenerated)
- `~/.lintel/jobs/_active.md` (cross-repo registry line updated to point at the owning repo)
- `.claude/runtime/jobs/_archive/<date>/<id>/` (on abort)
- `.claude/runtime/audit/jobs.jsonl`

**Calls into:**
- `bin/_jobs.sh` helper (sourced) — incl. `job_resume_point` (node-path), `job_can_start` (blocked_until), `job_set_steps` / `job_step_status`
- `/li:resume` (for `continue` subcommand)
- `/li:cycle` (for `replan whole`)

**Optional hooks (dormant by default):**
- `job-begin`, `job-end` and `job-stale-warn` are not activated by this skill.
- File presence is not registration/execution. Do not use dormant promotion recipes
  to copy failed/colliding outputs over original mapped artifacts.

## Anti-patterns

- **Direct edit of `_active.md`** — it's regenerated. Edit job.yaml instead.
- **Manual `rm -rf jobs/<id>/`** — bypasses cleanup-policy + audit. Use `abort`.
- **Branching to keep multiple "active" versions of same work** — branch is for divergent exploration, not version-control.
- **Replan whole on customer-engagement jobs** — destroys voice-gate provenance. Branch instead.

## Failure recovery

- `<id>` not found: BLOCKED with diagnostic
- `_active.md` corrupt: regenerate via helper
- `job.yaml` malformed: surface diff, offer manual repair
- Operation succeeds but `_active.md` regeneration fails: warn, continue (non-critical)

## Recommended next steps after invocation

- After `list`: pick an id, run `continue` / `abort` / `branch`
- After `continue`: work proceeds in the job's current_step
- After `abort`: review `_archive/<date>/<id>/job.yaml` for forensics
- After `branch`: both jobs visible in next `list`
- After `replan`: cycle continues from chosen step

## See also

- `/li:status` (alias for `/li:jobs list`)
- `/li:resume` (the underlying state-recovery mechanic)
- `/li:cycle` (the most common workflow_root skill)
- `/li:plan` (also workflow_root post-v3.8 Feature 2.1)
- `docs/concepts/jobs-system.md` (architecture doc)

## Cycle-position footer

Close your report with the shared position footer. Outside an active cycle it renders the thin
ambient line; inside one it shows the operator's position + next step:

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/lib/cycle-footer.sh"
render_cycle_footer                               # auto: thin when no cycle, full/--compact when in one
```

See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
