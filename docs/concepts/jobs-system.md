# Jobs system — single source of truth for curated flows in flight

**Last updated:** 2026-05-29 (v3.8 Feature 1 implementation)
**Status:** Concept doc — referenced by skills/jobs/SKILL.md, skills/status/SKILL.md, hooks/shared/job-{begin,end,stale-warn}/

> Curated flows in Lintel (cycle, plan, future Azure-e2e recipes, safe-install) carry implicit state — which phase are we in, what produced what, what's waiting on what. Before v3.8 that state lived scattered across `00-state.md`, `.planner-checkpoint.md`, and operator memory. The jobs system is **the place that lists in-flight curated work, a rule that abandoned ones must be cleaned up, and a way to operate on them as units.**

## The problem

In a shell/CLI session the operator and AI can digress freely. Without a jobs system:

- Plans get forgotten mid-flight. Open planfiles nobody is actively working against → nothing detects them.
- Output between phases is propagated by convention, not enforced contract.
- Resuming a flow means hunting for the right `00-state.md`.
- Killing a flow means manually deleting files in unclear places.
- Two flows on the same repo collide on the same loose state files.

## The model

```
~/.lintel/jobs/
├── _active.md              ← regenerated on every state change. /li:status reads this.
├── <job-id>/
│   ├── job.yaml            ← workflow, current_step, waiting-on, started_at, last_touched
│   ├── 00-state.md         ← existing log, scoped to this job
│   ├── outputs/            ← what this job produced
│   └── inputs/             ← refs to upstream job outputs
└── _archive/<date>/<job-id>/    ← completed/aborted jobs
```

`<job-id>` format: `<workflow>-<YYYYMMDD-HHMM>-<short-hash>`.

Example: `cycle-20260529-1430-a3b2c1`.

## Components

### `workflow_root: true` frontmatter flag

A new frontmatter field that marks a skill as job-spawning. Initial set:

- `skills/cycle/SKILL.md`
- `skills/plan/SKILL.md`

Future: any new e2e recipe, safe-install flow, Azure-e2e, etc. Adding the flag is what makes a skill participate in the jobs system.

### `job-begin` hook

Fires on PreToolUse for a workflow_root skill. Creates `~/.lintel/jobs/<id>/` with `job.yaml`, moves the skill's `00-state.md` into the job folder, regenerates `_active.md`.

Source: `hooks/shared/job-begin/run.sh`

### `job-end` hook

Fires on `status=DONE`, operator-abort, or fatal phase failure. Reads cleanup policy from `job.yaml`:

```yaml
cleanup_policy:
  keep: [adr, lessons, plan.md, spec.md, prompt.md]
  discard: [scratch/*]
```

- **Keep** items promoted to permanent homes:
  - ADRs → `docs/adr/`
  - Lessons → `tasks/lessons.md` (via existing `lessons-promote` skill)
  - Plan/spec/prompt → `docs/plans/<slug>/`
- **Discard** items deleted.
- Job moved to `_archive/<YYYY-MM-DD>/<job-id>/`.
- `_active.md` regenerated.

Source: `hooks/shared/job-end/run.sh`

### `job-stale-warn` hook

Fires at session-start (first `/li:cycle`, `/li:resume`, `/li:sense`, OR `/li:status` of a session). Reads `_active.md`. For each job untouched > N hours (default 24, configurable), surfaces:

```
⚠ Job <workflow>-<id> open, untouched 4d. Continue / abort / branch?
```

Same pattern as `brand-staleness-warn`. Read-only — never blocks.

Source: `hooks/shared/job-stale-warn/run.sh`

### `/li:jobs` skill — controller

5 subcommands:

- `list` → `cat _active.md`. Default action.
- `continue <id>` → invoke the job's current phase. Delegates to existing `resume` mechanic.
- `replan <id>` → re-run whole job, or operator picks parts. Build-on supported.
- `abort <id>` → move to `_archive/` with `status: aborted`. Apply discard. Fast kill.
- `branch <id>` → create parallel job from same starting point. New job-id, copies job.yaml + outputs/.

### `/li:status` skill — quick read

Single command, single purpose: show what's open right now. `cat ~/.lintel/jobs/_active.md`. Operator-friendly alias for `/li:jobs list`.

### `bin/_jobs.sh` — sourced helper

Functions used by hooks + skills:

- `job_create <workflow> <mode>` → new job
- `job_update <id> <step> <status>` → step transition + last_touched
- `job_archive <id> <result>` → cleanup + move to archive
- `regenerate_active` → rebuild `_active.md`
- `list_jobs` → cat `_active.md`
- `stale_jobs <hours>` → list jobs untouched > N hours
- `job_path <id>` → echo absolute job-dir path

## Mechanics

### Output handoff between steps is mechanical, not advisory

`job.yaml` declares per-step contracts:

```yaml
workflow: cycle
called_by: operator
mode: customer-engagement
started_at: 2026-05-29T10:00:00Z
last_touched: 2026-05-29T10:12:00Z
current_step: PLAN
status: ACTIVE
steps:
  - name: DEFINE
    produces: [design.md]
    status: DONE
  - name: PLAN
    consumes: [design.md]
    produces: [plan.md, spec.md, prompt.md]
    status: IN_PROGRESS
  - name: BUILD
    consumes: [plan.md, spec.md, prompt.md]
    blocked_until: PLAN.status == DONE
```

`blocked_until` is a mechanical gate. BUILD literally cannot start until `PLAN.status == DONE` and all `consumes` exist.

### Resume re-points, doesn't rebuild

The existing `resume` skill changes from "find a loose `00-state.md`" to "read `~/.lintel/jobs/<id>/00-state.md`". The skill's logic is unchanged — only the file path.

### Nothing runs in the background

- `_active.md` is regenerated on writes, never on a timer.
- `job-stale-warn` runs at session-start, not continuously.
- No daemon, no watcher, no scheduler.

A folder, three hooks, two skills, one frontmatter flag, one helper. That's the whole system.

## Anti-patterns

- **Direct edit of `_active.md`** — regenerated. Edit `job.yaml` instead.
- **Manual `rm -rf jobs/<id>/`** — bypasses cleanup-policy + audit. Use `/li:jobs abort`.
- **Branching to keep multiple "active" versions of same work** — branch is for divergent exploration, not version-control.
- **Nesting jobs** — if `/li:cycle` calls `/li:plan` as Phase 4, the inner PLAN should pass `--no-job` (or `NO_JOB=1`) so it doesn't spawn a nested job.

## What this closes

| Operator concern | Solved by |
|---|---|
| "Tappad tråd mitt i flödet" | `job-stale-warn` at session-start |
| "Öppna planfiler utan aktivt arbete" | `job-end` cleanup + stale-warn |
| "Snabbt avbryta och starta" | `/li:jobs abort` + `branch` |
| "Bygga på planer / köra om / komplettera" | `/li:jobs replan` (whole or parts) |
| "Modulära flöden som börjar och slutar där de vill" | Hop-in via `/li:jobs continue` + `workflow_root` flag on any skill |
| "Se vad som pågår direkt" | `/li:status` reads one generated file |

## What this explicitly does NOT do

- Does not gate hooks. Hooks still block via existing `exit 1`.
- Does not replace `00-state.md`. That file lives inside the job folder; format unchanged.
- Does not add a daemon, watcher, or scheduler.
- Does not invent new state mechanics — surfaces existing pieces.

## L-001 / L-002 application

- **L-001:** the jobs system ships **structure** (folder layout, hooks, helper, skills). Job content (job.yaml schemas, step transitions, cleanup outcomes) is produced at invocation per workflow.
- **L-002:** before designing, enumerated existing infrastructure (`00-state.md`, `.planner-checkpoint.md`, `lessons-promote`, `usage-log`, `hooks/shared/`). Jobs system **lifts** these into a visible structure — 95% lift, 5% net-new.

## See also

- `skills/jobs/SKILL.md` — controller
- `skills/status/SKILL.md` — quick read
- `hooks/shared/job-begin/HOOK.md`
- `hooks/shared/job-end/HOOK.md`
- `hooks/shared/job-stale-warn/HOOK.md`
- `bin/_jobs.sh` — helper
- `docs/concepts/planner-as-module.md` — the second half of this feature pair
