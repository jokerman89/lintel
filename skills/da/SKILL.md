---
name: da
layer: foundation
workflow_root: true
description: Use for data-architecture depth — schema design, migrations, sharding and partitioning, query-pattern audits, retention policy, and analytics readiness. Reach for it when the work turns on the data model or storage. Runs full, loop, or single-capability, dispatching to the data agents and scoring against a rubric.
color: blue
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Data-touching work lacks explicit schema evolution, recovery, retention and query evidence; consumers can break or data can be lost."
navigation:
  primary_intent: produce schema-grade decisions and migration safety when work touches data models
  triggers:
    - new datastore / major migration / analytics path
    - operator types /li:da {full|loop|single --action <name>}
    - active workflow requests data-model depth
  sibling_workflows:
    - /li:ta — technical architecture
    - /li:sc — security and compliance
    - /li:dh — hosting and operations
    - /li:tq — testing and QA
    - /li:full-engineering-pass — dependency-ordered composition
  risk_level: medium
  auto_mode_eligible: false
  estimated_tokens: 80000
domain:
  preferences_root: engineering.data_architecture.*
  granularities: [full, loop, single]
  checkpoints:
    - data_model_complete: entities, ownership and relationships mapped
    - schema_locked: versioned schema and consumer transition agreed
    - migration_safe: verified recovery and approved availability requirement
    - retention_specified: applicable retention, archival and deletion per data class
    - query_patterns_documented: measured access patterns and evidence gaps visible
  recovery:
    - on_failure: preserve failed attempt and reconcile observed state before continuation
  continuation:
    - after_fix: verify original work and profile, then revisit the affected checkpoint
  raise_help:
    - unknown_migration_window_or_recovery: ask for the missing authorized decision
    - retention_conflicts_with_policy: stop the affected action and refer to policy owner
    - active_consumer_break: agree the migration before cutover
---

# Data architecture

Preserve logical models, SQL artifacts, migration plans, retention policies and
analytics designs. Read [data decision methods](references/decision-methods.md)
for locking, rollback/replay, late data, idempotency and lineage. This is agent-owned
work within the selected lifecycle phase, not an automatic migration engine.

`/li:da full` covers the five checkpoints below; `/li:da loop` revisits a saved iteration;
`/li:da <capability>` or `/li:da single --action <capability>` selects only that capability.
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

1. Follow the [shared module caller procedure](../full-engineering-pass/references/domain-handoff.md#module-caller-procedure):
   select the original map/package/leaves, actual `work_context` binding and live
   P07 pin/policy. Do not grep personal preference files or select the newest report.
2. Read the schema/version, complete selected leaf text, access patterns and prior
   attributable evidence. Bind explicit advisory inputs separately from pack policy.
3. Prepare P05 obligations and the existing domain request before work; list expected
   artifacts and original output states. Name receiver mode and target authority.
4. Record start, execute only the authorized method, persist actual outputs/checks,
   and record result. Analysis/planning does not run production DDL/DML.
5. Externally prepare final P05 context after artifacts exist; fresh domain verification,
   QA and independent spec then quality remain required. Reviewers never repair their findings.

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

## Integration and dormant hooks

TA contracts/scaling inform data design; DH consumes migration/recovery and TQ
validates consumer/replay behavior. No new backlog, parser, scheduler or policy override.
Optional Brief Forge/audit use needs an actual configured invocation and persisted
evidence; recording is not review. These hooks remain opt-in under ADR-0008:

- `hooks/shared/da-schema-drift-warn/`
- `hooks/shared/da-migration-irreversible-warn/`
- `hooks/shared/da-retention-violation-warn/`

Do not infer that any hook fired from its presence. Retain direct single-capability
use and supported store expertise; unknown mandatory data evidence cannot be averaged away.
