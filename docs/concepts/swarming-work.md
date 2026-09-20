# Swarming work

Swarming is Lintel's opt-in execution profile for an approved plan whose work can be divided into
dependency-independent ownership domains. One coordinator dispatches bounded lanes, workers return
attributable changes and evidence, and independent reviewers check each lane before the coordinator
integrates it. The ordinary REVIEW phase then checks the reconciled tree.

Swarming changes how PLAN, BUILD and REVIEW execute. It does not add a cycle phase, replace the
authoritative task list, grant new permissions, or run a background scheduler.

## Decide whether to swarm

Use a swarm when all of these are true:

- The work map is approved and contains at least two domains that can become ready independently.
- Each worker can receive a bounded card with explicit acceptance checks.
- Writer ownership can be expressed as non-overlapping repository-relative paths.
- Concurrent writers can produce attributable changes in separate worktrees, patches, or an
  equivalent host-enforced scoped sandbox. Otherwise, the same swarm may run sequentially.
- One coordinator can own shared state, generated outputs, commits and integration.

Stay with ordinary sequential BUILD when one shared file or reducer dominates, the task boundaries
are still uncertain, or the overhead of briefs and lane reviews is larger than the work. Swarming is
never inferred from task count; the operator opts in during PLAN or invokes `/li:swarm init` for an
approved work map.

## The committed contract

A swarm adds one coordination directory beside the existing cold-executor trio:

```text
.claude/plans/<initiative>/
├── work.json
├── spec.md
├── plan.md
├── prompt.md
└── swarm/
    ├── coordination.json
    ├── charter.md
    ├── briefs/
    │   └── <card-id>.md
    ├── reports/
    │   └── <card-id>.md
    └── reviews/
        └── <card-id>.md
```

`work.json` keeps schema version 1 and adds `execution_mode: "swarm"` plus a repository-relative
`coordination` pointer. The mapped `tasks` artifact remains the only authority for card text,
dependencies, status and acceptance criteria. `coordination.json` references those task IDs and
adds execution topology only.

| Artifact | Authority | Writer |
|---|---|---|
| mapped `tasks` artifact | Cards, dependencies, status and acceptance | Coordinator |
| `work.json` | Artifact mapping and explicit swarm opt-in | Coordinator |
| `coordination.json` | Waves, roles, write scopes, isolation and evidence pointers | Coordinator |
| `charter.md` | Ownership, fan-out, fan-in and recovery rules | Coordinator |
| `briefs/<card>.md` | Card-specific startup, scope, inputs and checks | Coordinator |
| lane-owned paths | The implementation or documentation for one card | Assigned worker |
| `reports/<card>.md` | Changed paths, checks, findings and limitations | Assigned worker |
| `reviews/<card>.md` | Independent specification and quality verdict | Assigned reviewer |
| shared ledgers, reducers, commits and integration | Reconciled initiative state | Coordinator only |

A worker may write only its declared `write_scope` plus its own report. A reviewer writes only that
lane's review. Generated catalogs, synchronized instruction blocks and other fan-in reducers stay
coordinator-owned even when a worker edits their canonical sources.

## Start and inspect a swarm

1. Complete PLAN and approve the mapped cards.
2. Invoke `/li:swarm init <initiative>` and review the generated charter, topology and briefs.
3. Confirm that same-wave scopes do not overlap and that every concurrent writer has an accepted
   isolation backend.
4. Validate both the work map and the coordination contract before dispatch.

The helpers are read-only. Run them from a trusted Lintel installation, kept separate from the
repository whose artifacts they inspect:

```bash
export LINTEL_SOURCE_ROOT=/trusted/path/to/lintel
repo=/path/to/working-repository
work_map=.claude/plans/example/work.json
coord=.claude/plans/example/swarm/coordination.json

python3 "$LINTEL_SOURCE_ROOT/bin/li-work-artifacts.py" \
  --repo "$repo" --map "$work_map"
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" validate \
  --repo "$repo" --coord "$coord"
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" status \
  --repo "$repo" --coord "$coord"
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" wave \
  --repo "$repo" --coord "$coord"
```

Do not execute scripts named by a work artifact or use the target repository as an implicit tool
source. If the adapter cannot provide a trusted `LINTEL_SOURCE_ROOT`, stop with `NEEDS_CONTEXT`.

`status` derives lane state from the declared report and review evidence in the repository tree.
The coordinator still uses committed integration history as completion truth. `wave` returns the earliest
incomplete wave allowed by topology and evidence, bounded by `max_parallel`. That output is only a
candidate frontier: the coordinator must also read the authoritative task card and verify every
declared dependency before dispatch.

## Execute and integrate

For every candidate lane, the coordinator follows the same sequence:

1. Reconcile `wave` with the task card's authoritative dependencies and completion evidence.
2. Evaluate the complete lane brief with Brief Forge when that workflow has explicitly invoked it.
   Record an unavailable, disabled or bypassed forge honestly; pack configuration alone does not
   install a host callback.
3. Dispatch a fresh worker with the brief, accepted isolation and exact write scope.
4. Require the worker to perform the Lintel startup, change only owned paths, run focused checks and
   write the structured lane report.
5. Build a changed-path list from that lane's isolated change set and run `check-scope`:

   ```bash
   python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" check-scope \
     --repo "$repo" --coord "$coord" --task BC2 --paths-file changed-paths.txt
   ```

6. Assign a distinct reviewer to specification review and then quality review. The implementer does
   not write its own review.
7. Integrate passing lanes serially in deterministic task order and run focused checks after each
   integration. Regenerate coordinator-owned outputs only after their source lanes have fanned in.
8. Re-run `status` and `wave` until no eligible lane remains.

Parallel read-only research is safe when its outputs are separate. Parallel writing requires both
non-overlapping declared scopes and per-lane attribution; a union diff in one shared checkout cannot
prove which worker changed a path.

## Host capability and honest degradation

The `subagents` value in `lib/cli-tiers.yaml` controls execution shape, not correctness:

| Host tier | Execution | Evidence that may be claimed |
|---|---|---|
| `native` | Fan out ready writers up to the operator and topology cap only when every lane has attributable isolation; otherwise sequence them. | Concurrency and independent review only when the host actually produced those records. |
| `sequenced` | Replay the same lane briefs one at a time, preserving scopes, reports, reviews and gates. | Delegated work and review may be reported, but not concurrent writers. |
| `none` | The main agent executes cards serially, or exports replayable briefs for manual workers. | Do not label the implementer or self-review as independent. A lane without an independent review stays unclosed. |

Hooks are a separate capability. Lintel's Claude Code hooks do not activate on other clients, and
swarming does not emulate them. On hosts without compatible registered hooks, agents must read the
startup rules and state explicitly. See [multi-CLI support](../multi-cli.md) for the current adapter
matrix.

## Recover without guessing

Committed artifacts and attributable changes are the recovery source; chat history and worker
process labels are not.

| Situation | Recovery action |
|---|---|
| Worker process or local runtime state disappeared | Re-run `validate` and `status`. Preserve an attributable worktree or patch, scope-check it, then finish its report/review or replay the same brief. |
| Partial work has no lane attribution | Do not discard or integrate it silently. Quarantine the changes, report the discrepancy, and sequence a fresh attempt after the coordinator accounts for the partial work. |
| Worker changed an unowned path | Freeze the affected ownership domains. Narrow or reassign the scope, reconcile the isolated patch, or re-run the lane; do not hide the breach in fan-in. |
| Lane review failed | Return findings to the same card. Later dependent waves remain blocked until a distinct reviewer records passing evidence. |
| Two passing lanes conflict during integration | Stop integration, preserve both changes, and return to PLAN if ownership was wrong. The coordinator resolves only with an explicit, reviewed reconciliation. |
| Independent reviewer is unavailable | Record the host limitation and leave the lane open. A self-review can inform rework but cannot manufacture independent PASS evidence. |

Independent lanes may continue while a blocked lane's ownership domain is isolated and no dependency
requires it.

## Close a swarm

Run the deterministic evidence gate only after every lane report and review is present:

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" verify \
  --repo "$repo" --coord "$coord"
```

A passing `verify` result proves the declared lane evidence is structurally complete. The
coordinator must still confirm that every passing lane was integrated into the declared integration
branch, run focused integration checks, and hand the reconciled tree to ordinary REVIEW. REVIEW
repeats specification, quality and active-pack compliance across the full diff. Lane reviews never
replace that final integrated gate.

Swarm completion does not authorize a push, deployment, production change or other external
mutation. Those actions retain exactly the same approval and compliance requirements they would have
under sequential BUILD.

## Non-goals

Swarming does not introduce a daemon, distributed queue, database, generic agent runtime, automatic
merge, universal hook translation or required persistent agent memory. Its durable contract is
Markdown plus JSON, and its mechanical gates are local, read-only Python.

## See also

- [The cycle](../the-cycle.md) — where the profile enters PLAN, BUILD and REVIEW
- [Multi-CLI support](../multi-cli.md) — native, sequenced and no-subagent behavior
- [Brief Forge](brief-forge.md) — envelope construction and evaluator policy
- [Architecture](../architecture.md) — spine, pack and coordinator ownership
