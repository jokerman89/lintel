---
name: li-da
description: Use for data-architecture depth — schema design, migrations, sharding and partitioning, query-pattern audits, retention policy, and analytics readiness. Reach for it when the work turns on the data model or storage. Runs full, loop, or single-capability, dispatching to the data agents and scoring against a rubric.
---

> **Lintel on GitHub Copilot.** Generated from `skills/da/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/da/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/da/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Data architecture

Preserve logical models, SQL artifacts, migration plans, retention policies and
analytics designs. Read [data decision methods](../../../skills/da/references/decision-methods.md)
for locking, rollback/replay, late data, idempotency and lineage. This is agent-owned
work within the selected lifecycle phase, not an automatic migration engine.

`/li-da full` covers the five checkpoints below; `/li-da loop` revisits a saved iteration;
`/li-da <capability>` or `/li-da single --action <capability>` selects only that capability.
On Copilot use the corresponding native spelling when available, otherwise read
this canonical source. Unknown capabilities or absent prior attempts need context.
Pure code/API work without data impact belongs to the existing TA/cycle workflows.

## Sub-capability dispatch

Use the actual host operation or an explicit serial handoff, not assumed native role
registration. Every receiver gets the original leaf/acceptance and exact mode/scope.

| Capability | Dispatches to (agents) | Produces | Decisions and checks |
|---|---|---|---|
| `schema-design` | DatabaseDesigner; SchemaArchitect for mixed stores | versioned SQL/CQL/JSON schema, keys, relationships and index rationale | existing engine/version first; constraints, writer ownership and consumer compatibility |
| `migration-plan` | MigrationPlanner planning; Migrator artifact-only | ordered plan, forward SQL and verified recovery instructions | approved window, lock acquisition/hold, pre/post queries and restart states; a down script is not proof of reversibility |
| `retention-policy` | DatabaseDesigner + Architect | per-class active/warm/cold/archive/delete plan | applicable purpose/policy/holds; no universal 365-day rule; backups/projections and deletion propagation |
| `query-pattern-audit` | Explorer evidence, DatabaseDesigner interpretation | read/write mix, hot queries, index gaps and N+1 candidates | actual query plans/workload, not assumed indexes; EXPLAIN ANALYZE executes the query |
| `sharding-plan` | SchemaArchitect + DatabaseDesigner | partition key, co-location, rebalance and cross-shard plan | skew as well as cardinality; measure single-store limits, no arbitrary 1TB or shard-per-tenant mandate |
| `data-contract-collision` | DatabaseDesigner + Architect | active consumer/version impact and transition | drops/type narrowing/NOT NULL/semantic changes; even one required consumer break matters |
| `analytics-readiness` | DataPipelineDesigner + SchemaArchitect | business-question-driven ingestion/OLAP and dimensional model | fact grain, SCD/conformed dimensions, event time, correction/replay and lineage |

Preserve primary-store, migration-window, schema-versioning and review-threshold
preferences as explicit advice unless applicable policy makes a requirement mandatory.
Use actual supported mechanisms (for example PostgreSQL partitions/Citus, MongoDB
zone placement or Cassandra partitioning), not a stack picked from a template.
Unknown business questions need clarification; they do not justify inventing a warehouse.

## Workflow

Read and execute the [shared module caller procedure](../../../skills/full-engineering-pass/references/domain-handoff.md#module-caller-procedure)
before domain work. It is the sole owner of original work/package/leaf admission,
live P07/policy checks, immutable obligations, checkpoint publication, cold continuation
and final QA/independent acceptance. Apply this data method inside that procedure:

1. Read the actual engine/schema version, writers, access patterns and prior
   attributable evidence. Keep explicit advice separate from required pack policy.
2. Use the capability and checkpoint tables for constraints, mixed-version migration,
   locking/recovery, retention and analytics choices. Analysis/planning does not run
   production DDL/DML; receiver mode and exact-target authority remain explicit.
3. Explain restart states, last reversible state, consumer transition and measured
   query/replay evidence. Unknown effects require reconciliation, not an assumed
   down migration. Reviewers assess the resulting evidence, never repair it.

## Checkpoint ownership

| Checkpoint | Owner/method | Observable output |
|---|---|---|
| `data_model_complete` | DatabaseDesigner/SchemaArchitect | entities, relationship cardinalities, authoritative writers, query requirements |
| `schema_locked` | DatabaseDesigner + consumer owner | schema revision, constraints/indexes and explicit mixed-version compatibility |
| `migration_safe` | MigrationPlanner; Migrator in requested mode | step/precondition/lock/recovery plan and actual synthetic rehearsal when required |
| `retention_specified` | DatabaseDesigner + applicable policy owner | purpose/period/hold/deletion evidence per class, including replicas/backfills |
| `query_patterns_documented` | Explorer + DatabaseDesigner | source/time/workload-specific plans and performance, or explicit unverified gaps |

MigrationPlanner does not execute migrations. Migrator retains **authorized-execution**
for a separately authorized exact target/action; artifact-only is the mode of the
planning handoff, not a restriction on the entire role. Preserve P03's partial-state
recovery and unrelated-file protection. A large row count is a risk input, not blanket
permission or a universal prohibition. An approved maintenance window is valid input.

Synthetic choice: adding a required field with active old writers can need expand,
bounded backfill, validation, read/write switch and later contraction. Re-adding a
dropped column does not recover data. A late analytics event may require a correction,
not another increment. Use the retained worked examples and test those mechanisms.

## Evidence, loop and recovery

Keep `data-model.md`, versioned schema, `migration-plan.md`, risk/validation SQL,
`retention-policy.md`, query and dimensional artifacts as named outputs in the
selected request. Old `.claude/runtime/state/da/` files are history until explicitly
selected and verified. New start/results use
`.claude/runtime/state/domains/<operation>/iNNNN/`; safe filenames, no timestamp colons.

A loop links original iteration artifacts and compares affected schema/consumer/
retention decisions. Cold entry uses `workflow_resume` and the shared state table:
missing result means interrupted, not rerun. Unknown migration effects must be
reconciled before any forward/recovery execution. No generic rollback or file reset.

Advisory rubric: Data model completeness, Schema locked, Migration safety,
Retention specified, Query patterns documented and Consumer impact analyzed,
each against the observable checkpoint criteria with evidence and uncertainty. Scores cannot
clear a failed/unknown mandatory control. DONE requires actual selected checks and
independent acceptance; DONE_WITH_CONCERNS only allows advisory residuals. Missing
authority/evidence is BLOCKED or NEEDS_CONTEXT, never a green partial pass.

## Reusable patterns

Follow the [reusable pattern consumer contract](../../../skills/pattern/references/consumer-contract.md).
Module entry resolves the data expectations bound to the current target context and passes each
sub-capability only its projected clauses (`project` for the mapped package, or the clauses
mapped to it). An unknown data classification or store yields `needs-context` and blocks the
dependent design; no live cloud, tenant or environment discovery is implied, and requirements
are never inferred from generic recommendations. When the runtime reports no patterns, the
module is unchanged.

## Integration and dormant hooks

TA contracts/scaling inform data design; DH consumes migration/recovery and TQ
validates consumer/replay behavior. No new backlog, parser, scheduler or policy override.
Optional Brief Forge/audit use needs an actual configured invocation and persisted
evidence; recording is not review. These hooks remain opt-in under ADR-0008:

- `hooks/shared/da-schema-drift-warn/`
- `hooks/shared/da-migration-irreversible-warn/`
- `hooks/shared/da-retention-violation-warn/`

Their execution is unobserved unless separately evidenced. A warning or down-script
check does not prove data recovery or satisfy a mandatory migration criterion.
Do not infer that any hook fired from its presence. Retain direct single-capability
use and supported store expertise; unknown mandatory data evidence cannot be averaged away.
