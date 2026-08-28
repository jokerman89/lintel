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
<repo>/.claude/runtime/jobs/
├── _active.md              ← regenerated on every state change. /li:status reads this.
├── <job-id>/
│   ├── job.yaml            ← workflow, current_step, waiting-on, started_at, last_touched
│   ├── 00-state.md         ← existing log, scoped to this job
│   ├── outputs/            ← what this job produced
│   └── inputs/             ← refs to upstream job outputs
└── _archive/<date>/<job-id>/    ← completed/aborted jobs
```

Job data is repo-scoped (v5 layout, ADR-0005). `~/.lintel/jobs/_active.md` remains
as the thin **cross-repo registry** — one line per open job anywhere, each pointing
at its owning repo — so `/li:resume` and `/li:status` keep their "what's open
anywhere" view.

`<job-id>` format: `<workflow>-<YYYYMMDD-HHMM>-<short-hash>`.

Example: `cycle-20260529-1430-a3b2c1`.

## Components

### `workflow_root: true` frontmatter flag

A new frontmatter field that marks a skill as job-spawning. Initial set:

- `skills/cycle/SKILL.md`
- `skills/plan/SKILL.md`

Future: any new e2e recipe, safe-install flow, Azure-e2e, etc. Adding the flag is what makes a skill participate in the jobs system.

### `job-begin` hook

Fires on PreToolUse for a workflow_root skill. Creates `<repo>/.claude/runtime/jobs/<id>/` with `job.yaml`, moves the skill's `00-state.md` into the job folder, regenerates `_active.md`.

Source: `hooks/shared/job-begin/run.sh`

### `job-end` hook

Fires on `status=DONE`, operator-abort, or fatal phase failure. Reads cleanup policy from `job.yaml`:

```yaml
cleanup_policy:
  keep: [adr, lessons, plan.md, spec.md, prompt.md]
  discard: [scratch/*]
```

- **Keep** items promoted to permanent homes:
  - ADRs → `.claude/decisions/`
  - Lessons → `.claude/memory/lessons.md` (via existing `lessons-promote` skill)
  - Plan/spec/prompt → `.claude/plans/<slug>/`
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

Single command, single purpose: show what's open right now. `cat ~/.lintel/jobs/_active.md` (the cross-repo registry). Operator-friendly alias for `/li:jobs list`.

### `bin/_jobs.sh` — sourced helper

Functions used by hooks + skills:

- `job_create <workflow> <mode> [<step-spec> ...]` → new job; optional inline step contracts
- `job_set_steps <id> <step-spec> ...` → (re)write the `steps[]` block with per-step contracts
- `job_update <id> <step> <status>` → step transition + last_touched (step-scoped when `<step>` is a populated step; otherwise legacy top-level status)
- `job_step_status <id> <step>` → echo one named step's status
- `job_can_start <id> <step>` → `yes`/`no` — evaluates the step's `blocked_until` predicate
- `job_resume_point <id>` → deepest incomplete + startable step name (WBS node-path for `tree` plans)
- `job_archive <id> <result>` → cleanup + move to archive
- `regenerate_active` → rebuild `_active.md`
- `list_jobs` → cat `_active.md`
- `stale_jobs <hours>` → list jobs untouched > N hours
- `job_path <id>` → echo absolute job-dir path

## State unification (design §3.6 — closes split-brain state)

There is **one canonical home for each kind of state**, split by ownership:

| State | Canonical home | Owner |
|---|---|---|
| Durable artifacts — the trio (`plan.md` / `spec.md` / `prompt.md`) + `scope.md` + WBS | **`.claude/plans/<slug>/`** (in the repo, committed) | the repo — "documented in the repo" |
| Job control — `job.yaml`, `_active.md`, `00-state.md`, `outputs/`, `inputs/` | **`<repo>/.claude/runtime/jobs/<id>/`** (gitignored) | the harness |

The trio is **born** in `<repo>/.claude/runtime/jobs/<id>/outputs/` during a job and **promoted**
to the repo at `.claude/plans/<slug>/` by `job-end` on DONE. The committed tree is the durable,
version-controlled home; `.claude/runtime/jobs/` is transient job control that the
`_archive/` sweep eventually reclaims.

### Canonical plan.md path — the one true location

The audit (design hole 4) found **three divergent `plan.md` path conventions**.
Slice 3 resolves them: **`.claude/plans/<slug>/plan.md` is canonical** (v5 home;
was `docs/plans/<slug>/plan.md` pre-ADR-0005). The other two are **deprecated**
(still read for back-compat during the grace window, never written going forward):

| Convention | Status | Note |
|---|---|---|
| `.claude/plans/<slug>/plan.md` (directory-per-plan) | **CANONICAL** | the trio + `spec.md` + `prompt.md` + `scope.md` all co-locate here; matches `job-end` promotion and `jobs-system.md` |
| `docs/plans/<slug>-<datetime>.md` (flat file, slug+datetime) | **deprecated** | was `skills/plan/SKILL.md:198`; loses trio co-location |
| root / cwd `plan.md` (or bare `docs/plans/`) | **deprecated** | was `skills/plan/SKILL.md:255,262` "root or …" + `.claude/engineering/design-archive/lintel-v3.5-cycle-and-roles.md`; ambiguous, collides across concurrent jobs |

`<slug>` is the wedge/title slug. A directory (not a flat file) is canonical
because the trio + scope + WBS must co-locate so resume, `handoff-size-check`, and
the cold-executor handoff all find their siblings by a single path. The two
deprecated forms remain readable for the grace window noted in
`docs/migrations/` but are no longer emitted.

## Mechanics

### Output handoff between steps is mechanical, not advisory

`job.yaml` declares per-step contracts. As of Slice 3 (design §3.4) these are
**populated and enforced** by `bin/_jobs.sh`, not merely documented — `job_create`
no longer writes a literal `steps: []` when step-specs are supplied, and
`job_set_steps` renders one record per step:

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
    consumes: []
    produces: [design.md]
    status: DONE
  - name: PLAN
    consumes: [design.md]
    produces: [plan.md, spec.md, prompt.md]
    status: IN_PROGRESS
  - name: BUILD
    consumes: [plan.md, spec.md, prompt.md]
    produces: []
    status: PENDING
    blocked_until: PLAN.status == DONE
```

Each step carries `name / consumes / produces / status` (always) and an optional
`blocked_until` predicate. For a `tree`-schema plan (L/XL) the `name` is a **WBS
node-path** (`1.1.a`); for flat/phased plans it is a phase token (`BUILD`).

**Step-spec grammar** (the argument form `job_create` / `job_set_steps` accept —
one pipe-delimited record per step):

```
NAME|consumes=a.md,b.md|produces=c.md|status=PENDING|blocked_until=PLAN.status == DONE
```

The first field is the `NAME`; the rest are `key=value` in any order. `consumes`
/ `produces` are comma-separated (→ rendered as YAML inline sequences; omit → `[]`).
`status` defaults to `PENDING`.

**`blocked_until` is a mechanical gate, enforced by `job_can_start <id> <step>`**
(echoes `yes`/`no`, returns 0/1). The predicate grammar is deliberately small:

```
<predicate> := <clause> ( "&&" <clause> )*
<clause>    := <STEP>.status == DONE
```

i.e. a conjunction (`&&`) of "this named step has reached DONE" tests — no `||`,
no negation, no other status values. An empty/absent predicate means "never
blocked". A clause whose referenced step is not yet DONE (including a
missing/unknown step) evaluates false → the step is blocked. Anything outside the
grammar is treated conservatively as unsatisfiable, so a malformed predicate never
silently unblocks a gate. BUILD literally cannot start until `PLAN.status == DONE`.

`job_update <id> <step> <status>` updates a **named step's** status when `<step>`
is a populated `steps[]` entry (the job stays `ACTIVE`; terminal transitions are
`job_archive`'s job). When `<step>` is not a populated step, it preserves the
legacy behaviour of writing the top-level `status:` — so pre-Slice-3 callers are
unaffected.

### Resume re-points, doesn't rebuild

The existing `resume` skill changes from "find a loose `00-state.md`" to "read
`<repo>/.claude/runtime/jobs/<id>/00-state.md`". For **flat/phased** plans the resume target is
unchanged — `current_step`. For **`tree`** plans, `job_resume_point <id>` returns
the deepest incomplete **and startable** WBS node-path (`1.1.a`) so a half-done
big plan resumes to the exact subtask, skipping any leaf still gated by its
`blocked_until` predicate. If every leaf is DONE (or no `steps[]` are populated),
it returns empty and resume falls back to `current_step`. See
`skills/resume/SKILL.md` Step 2.5.

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
| "Dropped the thread mid-flow" | `job-stale-warn` at session-start |
| "Open plan files with no active work" | `job-end` cleanup + stale-warn |
| "Abort and restart quickly" | `/li:jobs abort` + `branch` |
| "Build on plans / re-run / supplement them" | `/li:jobs replan` (whole or parts) |
| "Modular flows that start and end where they want" | Hop-in via `/li:jobs continue` + `workflow_root` flag on any skill |
| "See what's in flight at a glance" | `/li:status` reads one generated file |

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
