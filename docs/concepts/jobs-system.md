# Jobs system — single source of truth for curated flows in flight

**Last updated:** 2026-09-20 (selected work and observable runtime state)
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

The committed [work map](../../skills/spec-kit/references/work-map.md) owns
specification/design/tasks/handoff paths and original task IDs. Job records are
optional execution observations, not another task backlog or proof of review.
Automatic job hooks remain dormant under ADR-0008. An empty job registry therefore
cannot establish that no initiative is open.

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

A frontmatter field declaring a workflow entry point. It does not itself spawn a
job or prove that the optional job hook is registered. Initial set:

- `skills/cycle/SKILL.md`
- `skills/plan/SKILL.md`

Other workflows can use the same explicit helpers; a flag does not authorize hook activation.

### `job-begin` hook

Dormant historical hook for a compatible PreToolUse adapter. When explicitly called,
it creates a job record; no native registration or live invocation is inferred here.

Source: `hooks/shared/job-begin/run.sh`

### `job-end` hook

Dormant historical promotion/archive recipe. Its promotion is not accepted as a
safe producer for mapped work: failed/aborted candidates and colliding initiative
or ADR filenames must not replace approved artifacts. Keep it inactive pending
its owned behavior evidence. The stored cleanup policy remains readable:

```yaml
cleanup_policy:
  keep: [adr, lessons, plan.md, spec.md, prompt.md]
  discard: [scratch/*]
```

- Historical intended **keep** destinations:
  - ADRs → `.claude/decisions/`
  - Lessons → never appended. The hook only suggests `/li:learn` review and
    `/li:lessons-promote` for general lessons; candidates stay in the archived job outputs.
  - Plan/spec/prompt → `.claude/plans/<slug>/`
- Explicit archive operations use `job_archive`; they are separate from approval
  or promotion of durable artifacts. Preserve failed candidates for diagnosis.

Source: `hooks/shared/job-end/run.sh`

### `job-stale-warn` hook

Optional, dormant session-start warning. Explicit `stale_jobs` reads actual records
without filtering blocked/overdue work out of the observation. Missing/unparseable
timestamps report `age-unknown` instead of becoming recent or disappearing:

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

Single command: `list_jobs --read-only` over the selected repository's actual
records, plus stale/unknown-age observations and the explicitly selected work map.
It creates no registry/audit directories when sourced with `LINTEL_JOBS_NO_INIT=1`.
Cross-repository registry reading requires its own explicit selection.

### `bin/_jobs.sh` — sourced helper

Cross-repository registry updates hold an exclusive directory lock across reading and
replacing the derived view. Readers see an atomically replaced complete file. A writer
that cannot acquire the lock reports failure and preserves the existing registry; it
does not remove another writer's lock. After an interrupted process, verify no writer
remains before removing its empty `_active.md.lock` directory and regenerating the view.
The per-repository job files remain authoritative.

Functions used by hooks + skills:

- `job_create <workflow> <mode> [<step-spec> ...]` → new job; optional inline step contracts
- `job_set_steps <id> <step-spec> ...` → (re)write the `steps[]` block with per-step contracts
- `job_update <id> <step> <status>` → step transition + last_touched (step-scoped when `<step>` is a populated step; otherwise legacy top-level status)
- `job_step_status <id> <step>` → echo one named step's status
- `job_can_start <id> <step>` → `yes`/`no` — evaluates the step's `blocked_until` predicate
- `job_resume_point <id>` → deepest incomplete + startable step name (WBS node-path for `tree` plans)
- `job_archive <id> <result>` → cleanup + move to archive
- `regenerate_active` → rebuild `_active.md`
- `list_jobs` → compatible derived registry view; `--read-only` inspects actual local records
- `stale_jobs <hours>` → retain old and unknown-age observations without treating age as completion
- `job_path <id>` → echo absolute job-dir path

## State unification (design §3.6 — closes split-brain state)

There is **one canonical home for each kind of state**, split by ownership:

| State | Canonical home | Owner |
|---|---|---|
| Durable artifacts — the trio (`plan.md` / `spec.md` / `prompt.md`) + `scope.md` + WBS | **`.claude/plans/<slug>/`** (in the repo, committed) | the repo — "documented in the repo" |
| Job control — `job.yaml`, `_active.md`, `00-state.md`, `outputs/`, `inputs/` | **`<repo>/.claude/runtime/jobs/<id>/`** (gitignored) | the harness |

Native PLAN writes the durable trio/map at the selected committed paths. Spec Kit
keeps its original files and IDs. Jobs may reference them; no default pipeline
depends on dormant `job-end` promotion. The shared cycle ledger carries the map's
paths and actually verified profile reference/policy. Its correlated cycle history
survives interleaved initiatives and a later explicit resume without resetting SENSE.

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
because it is a useful native convention. The selected work map, not sibling
guessing, lets resume, ANALYZE, CAPTURE and handoff budgeting locate original
artifacts; external task/spec/handoff paths need not co-locate. The two
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
silently unblocks this predicate. It is a mechanical helper a caller must use,
not universal host enforcement. A job's DONE is not P05 review/QA clearance.

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
- `job-stale-warn` is dormant unless a compatible adapter was explicitly activated.
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

- Does not gate hooks. Actual blocking behavior depends on the verified host adapter;
  the Claude block protocol uses exit 2, not a generic exit-1 claim.
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
