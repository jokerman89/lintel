---
name: jobs
layer: foundation
description: Curated-flow lifecycle controller — list / continue / replan / abort / branch in-flight Lintel jobs. Single source of truth for "what's open right now."
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: auto-pick-recommended
---

You are the `jobs` skill — lifecycle controller for in-flight Lintel curated flows (v3.8 Feature 1).

## What this skill does

Provides 5 subcommands to operate on `~/.lintel/jobs/`:

- `list` (default) — surface `_active.md` (regenerated from job.yaml on every state change)
- `continue <id>` — resume the job at its `current_step` (delegates to `/li:resume` mechanic)
- `replan <id>` — re-run the whole job or pick which steps to redo (supports build-on, not just start-over)
- `abort <id>` — move job to `_archive/` with `status: aborted`, apply discard policy, skip keep-promotion
- `branch <id>` — create a parallel job from the same starting point (new job-id, copies job.yaml + outputs/)

Each operation regenerates `_active.md` so `/li:status` reflects current truth.

## When to use

- "What's open right now?" → `list` (or invoke `/li:status` for the same)
- "I want to pick up that customer-engagement cycle from Tuesday" → `continue <id>`
- "Restart this plan but keep the discovery output" → `replan <id>` with partial-redo prompt
- "Kill this. I started wrong." → `abort <id>`
- "I want to try the same design with motion=kinetic instead of moderate" → `branch <id>`

## When NOT to use

- Mid-task code-editing — jobs is lifecycle, not editing
- For non-workflow_root skills — single-shot skills (`/li:doctor`, `/li:health`) don't spawn jobs
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
BIN_DIR="$(cd "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null && pwd)/bin"
[ -f "$BIN_DIR/_jobs.sh" ] || BIN_DIR="$HOME/.lintel/scaffolding/bin"
source "$BIN_DIR/_jobs.sh"
```

### Step 3 — Dispatch

**`list`:**
```bash
list_jobs
```

**`continue <id>`:**
1. Verify `~/.lintel/jobs/<id>/job.yaml` exists.
2. Determine the resume target. For a `tree`-schema plan, call
   `job_resume_point <id>` (deepest incomplete + startable WBS node-path, e.g.
   `1.1.a`); for flat/phased plans, read `current_step` from job.yaml. See
   `/li:resume` Step 2.5.
3. Invoke `/li:resume --job <id>` (resume skill reads from job dir, not loose `.lintel/state/00-state.md`).
4. Update last_touched.

**`replan <id>`:**
1. Verify job exists.
2. AskUserQuestion: "Replan whole job, OR pick a step to restart from?"
   - Whole → reset job.yaml steps to empty + invoke `/li:cycle` from the job's workflow start
   - From step → operator picks; `/li:resume --from <step>` style
3. Update last_touched.

**`abort <id>`:**
1. Verify job exists.
2. AskUserQuestion confirm + optional `--reason`.
3. Call `job_archive <id> ABORTED`.
4. Surface `[lintel] Job <id> aborted, archived to _archive/<date>/<id>/`.

**`branch <id>`:**
1. Verify source job exists.
2. Create new job-id with `--name` suffix (or auto-suffix `-branch-N`).
3. Copy `job.yaml` + `outputs/` + `inputs/` from source.
4. Reset new job's `current_step` to source's current_step (operator continues from there).
5. Update both jobs' last_touched.
6. Surface `[lintel] Branched <new-id> from <id>. Both active.`

### Step 4 — Audit

Every operation logs to `~/.lintel/audit/jobs.jsonl`:

```json
{"ts":"...","kind":"job_action","job_id":"...","action":"continue|replan|abort|branch"}
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
- `~/.lintel/jobs/_active.md`
- `~/.lintel/jobs/<id>/job.yaml`
- `~/.lintel/jobs/<id>/00-state.md`
- `~/.lintel/profile.yaml` (mode + stale threshold)

**Writes:**
- `~/.lintel/jobs/<id>/job.yaml` (last_touched updates)
- `~/.lintel/jobs/_active.md` (regenerated)
- `~/.lintel/jobs/_archive/<date>/<id>/` (on abort)
- `~/.lintel/audit/jobs.jsonl`

**Calls into:**
- `bin/_jobs.sh` helper (sourced) — incl. `job_resume_point` (node-path), `job_can_start` (blocked_until), `job_set_steps` / `job_step_status`
- `/li:resume` (for `continue` subcommand)
- `/li:cycle` (for `replan whole`)

**Hooks fire:**
- `job-begin` on new workflow_root invocation (not via this skill but via the underlying skill)
- `job-end` on `abort` or terminal status
- `job-stale-warn` at session-start (not via this skill but listed for context)

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
source "$LINTEL_REPO_ROOT/lib/cycle-footer.sh"   # fallback: "$(git rev-parse --show-toplevel)/lib/cycle-footer.sh"
render_cycle_footer                               # auto: thin when no cycle, full/--compact when in one
```

See [ADR-0003](../../docs/adr/0003-cycle-position-footer.md).
