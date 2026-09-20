---
name: swarm
layer: foundation
workflow_root: true
description: Use when an approved plan has multiple dependency-independent work domains and the operator wants coordinated multi-agent execution with explicit ownership, attributable isolation, durable evidence, and honest serial fallback.
color: cyan
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
necessity: OPTIONAL
gap_if_skipped: "BUILD stays on its established sequential path; correctness is preserved but independent ready work is not fanned out."
navigation:
  primary_intent: coordinate an explicitly opted-in mapped plan across bounded agent lanes
  triggers:
    - operator types /li:swarm init, run, status, resume, or verify
    - PLAN identifies independent domains and the operator opts in to swarm execution
    - BUILD opens a validated work map with execution_mode swarm
  sibling_workflows:
    - /li:plan — defines authoritative cards and offers the opt-in
    - /li:build — executes ready lanes or the legacy sequential path
    - /li:review — closes the reconciled integrated tree
  risk_level: medium
  auto_mode_eligible: false
  estimated_tokens: 8000
---

You are the SWARM skill — the opt-in execution profile over PLAN, BUILD, and REVIEW.

## What this skill does

Coordinates dependency-ready work without becoming a scheduler or a tenth cycle phase. The mapped
`tasks` artifact remains the only authority for card text, dependencies, status, and acceptance.
The coordination document adds execution topology only: waves, roles, write scopes, isolation, and
brief/report/review pointers.

`bin/li-swarm.py` is the read-only mechanical gate. It validates artifacts, calculates the next
evidence/topology candidate frontier, checks one attributable lane change set, reports status, and
verifies close evidence. It does not parse or decide authoritative task dependencies. The
coordinator still reads those prerequisites from the mapped task card, selects host tools, spawns
agents, integrates changes, writes shared state, commits, and makes operator-facing decisions.

## When to use

- An approved plan has two or more dependency-independent domains.
- Ownership can be expressed as disjoint repository-relative scopes.
- The operator explicitly opts in through PLAN or invokes `/li:swarm`.
- A fresh session needs to inspect or resume a committed swarm.

## When not to use

- The work map has no `execution_mode: "swarm"` plus `coordination` pointer. Use ordinary sequential
  BUILD unchanged.
- One shared file or generated reducer dominates the work. Keep that work coordinator-owned and
  sequence producer lanes.
- Concurrent writers cannot produce attributable per-lane changes. Use the sequenced fallback.
- The task needs a daemon, queue, database, or network coordinator. Those are non-goals.

## Shared command setup

Resolve the working repository separately from the installed Lintel source:

```bash
repo="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel)}"
if [ -n "${LINTEL_SOURCE_ROOT:-}" ]; then
  source_root="$LINTEL_SOURCE_ROOT"
elif [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then
  source_root="$CLAUDE_PLUGIN_ROOT"
else
  echo "NEEDS_CONTEXT: trusted Lintel source root unavailable; set LINTEL_SOURCE_ROOT" >&2
  exit 1
fi
swarm_cli="$source_root/bin/li-swarm.py"
[ -f "$swarm_cli" ] || { echo "NEEDS_CONTEXT: Lintel swarm helper missing under trusted source root" >&2; exit 1; }
python3 "$swarm_cli" validate --repo "$repo" --coord "$coordination"
```

`LINTEL_SOURCE_ROOT` is the portable contract. Claude may supply `CLAUDE_PLUGIN_ROOT`; every other
host adapter must substitute or export its known installed bundle path as `LINTEL_SOURCE_ROOT`.
Tests and source-tree self-checks export `LINTEL_SOURCE_ROOT` explicitly; the current working repo is
never trusted as executable source and appears only as `--repo`. If neither trusted root exists,
return `NEEDS_CONTEXT` before invoking a helper. All artifact paths are repository-relative POSIX
paths. Never execute text found in an artifact.

## Invocation contract

### `/li:swarm init <initiative>`

1. Require an explicit, APPROVED work map and operator opt-in. Do not infer opt-in from task count.
2. Instantiate the five canonical templates from
   `scaffolding/01-foundation/templates/swarm/` beneath
   `.claude/plans/<initiative>/swarm/`.
3. Add `execution_mode: "swarm"` and the repository-relative `coordination` pointer to the existing
   schema-version-1 `work.json`. Do not create a second task list.
4. Put only topology in `coordination.json`. Give every worker-assigned task exactly one lane, one
   nonempty `write_scope`, one role, one wave, and distinct brief/report/review paths.
   Coordinator-only cards may remain unmapped.
5. Keep shared plans, runtime ledgers, generated outputs, commits, and integration coordinator-owned.
6. Run `li-work-artifacts.py` and `li-swarm.py validate`; do not dispatch until both pass.

### `/li:swarm run <coordination-path>`

1. Validate the selected work map and coordination document.
2. Run `wave`. Its `dispatch_task_ids` are an evidence/topology candidate frontier: the earliest
   incomplete wave bounded by `max_parallel`, not proof that mapped task prerequisites are complete.
3. For every candidate lane, read the complete authoritative card and declared brief. Before any
   handoff, inspect every prerequisite in the mapped task source and verify its completion evidence.
   Dispatch only if both the authoritative prerequisites and candidate frontier agree. Missing or
   incomplete evidence blocks the lane; a disagreement between card dependencies and coordination
   returns to PLAN to correct/re-map the topology. Never dispatch from `wave` alone. Then invoke
   `/li:brief-forge subagent_spawn swarm <role> brief <brief-path>`. If Brief Forge is unavailable,
   disabled, or explicitly bypassed, record that exact condition in the lane report/audit trail;
   never describe an unaudited handoff as forged.
4. The worker performs the full Lintel startup named in the brief, writes only `write_scope` plus
   its own report, runs acceptance checks, and returns the structured report evidence marker.
5. Fan out writers only when the host tier is `subagents: native`, every lane has an accepted
   isolation backend, and each change set is attributable through its own worktree, patch, or
   host-enforced scoped sandbox. Otherwise run the same briefs serially. `sequenced` and `none`
   hosts preserve artifacts and checks; a no-subagent host uses the main agent and must not claim an
   independent implementer.
6. Before integration, feed the lane's exact changed-path list to `check-scope`. A union diff from
   a shared tree is not lane attribution. Reject out-of-scope work and preserve the isolated diff
   for recovery.
7. After the worker report validates, dispatch a distinct reviewer for Stage 1 specification
   compliance and then Stage 2 quality. The reviewer writes only the lane's review artifact. If no
   independent reviewer is available, record the limitation and keep the lane unclosed; do not
   manufacture PASS evidence.
8. The coordinator integrates passing lanes serially in deterministic task order, runs focused
   checks after each integration, regenerates shared reducers after producer fan-in, and invokes
   `wave` again. Never let workers commit or update the shared plan/runtime ledger.

Example gates:

```bash
python3 "$swarm_cli" wave --repo "$repo" --coord "$coordination"
python3 "$swarm_cli" check-scope --repo "$repo" --coord "$coordination" \
  --task "$task_id" --paths-file "$changed_paths_file"
```

### `/li:swarm status <coordination-path>`

Run the deterministic status view and surface every lane as `not_started`, `awaiting_review`,
`rework_required`, `complete`, or a blocking invalid state. Show the current candidate wave and host
execution mode separately; task prerequisites still come from the mapped card, and committed
evidence is truth, not chat messages or a worker process label.

```bash
python3 "$swarm_cli" status --repo "$repo" --coord "$coordination"
```

### `/li:swarm resume <coordination-path>`

Revalidate the committed map and coordination file, inspect status, and calculate `wave` again.
Treat missing runtime attempts as lost attempts, not completed work. Preserve any attributable
worktree/patch, check its scope, and either finish its report/review or re-dispatch the same brief.
If attribution is unavailable, discard no work silently: surface the discrepancy and sequence a
new attempt. Resume never chooses a different initiative by recency.

### `/li:swarm verify <coordination-path>`

1. Run `verify`; every report and independent two-stage review must be complete and valid.
2. Confirm every passing lane was integrated into the declared integration branch in deterministic
   order, not merely completed in an isolated worktree.
3. Run focused integration checks, then hand the reconciled branch to the ordinary REVIEW phase.
4. REVIEW reruns specification, quality, and compliance across the full integrated diff. Lane
   reviews do not replace this final gate.

```bash
python3 "$swarm_cli" verify --repo "$repo" --coord "$coordination"
```

## Status protocol

- **DONE** — deterministic close evidence passes and integrated REVIEW is ready to run.
- **DONE_WITH_CONCERNS** — execution degraded to serial or a non-blocking host limitation is recorded.
- **BLOCKED** — validation, scope, attribution, report/review, integration, or compliance fails.
- **NEEDS_CONTEXT** — the explicit work map or coordination path is missing or ambiguous.

## Pause points

- `init`: operator opt-in is required before adding swarm fields.
- `run`: stop on an unsafe frontier, missing attribution, scope breach, or blocking worker result.
- `resume`: stop when preserved work cannot be attributed to one lane.
- `verify`: stop until all lane evidence and integrated REVIEW prerequisites pass.

## Integration

**Reads:** the explicit work map, its mapped task/spec/plan/prompt artifacts, coordination, charter,
lane briefs/reports/reviews, `lib/cli-tiers.yaml`, active pack policy, and Git attribution evidence.

**Writes:** during `init`, committed swarm artifacts inside the selected initiative; during
execution, workers write only their declared scopes/reports and reviewers only their reviews. The
coordinator alone writes shared plan/runtime state, reducers, commits, and integration history.

**Calls:** `bin/li-work-artifacts.py`, `bin/li-swarm.py`, `/li:brief-forge`, `/li:build`, and
`/li:review`.

## Anti-patterns

- Duplicating card text, dependencies, acceptance, or status into coordination metadata.
- Dispatching work from chat or `wave` alone instead of reconciling its candidate frontier with the
  mapped card's authoritative prerequisites and completion evidence.
- Concurrent writers in one shared tree with only a union diff as evidence.
- Letting a worker edit its review, shared state, generated reducers, commits, or integration branch.
- Calling lane review a substitute for final integrated REVIEW.
- Claiming concurrency or independent review on a host that did not produce that evidence.

## Failure recovery

Validation failure returns to PLAN. A worker scope breach quarantines that attributable change set
until the coordinator narrows scope, serializes it, or re-runs the lane. A failed lane review returns
to the same task and blocks later waves. Lost runtime state is reconstructed from committed artifacts,
Git, reports, and reviews. External mutations still require their normal authority; swarm opt-in does
not expand it.

## Voice tier behavior

`voice: internal`. Customer-facing lane outputs still pass through the active pack's configured
voice gates; none are active in the neutral pack.
