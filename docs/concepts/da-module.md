# DA: data architecture

DA provides schema, query, migration, retention and analytics decisions under the
[engineering-module contract](engineering-modules.md). The [canonical skill](../../skills/da/SKILL.md)
and [data methods](../../skills/da/references/decision-methods.md) retain the executable
caller procedure and worked locking/replay/lineage cases.

## Retained capabilities

| Capability | Receiver responsibility | Evidence/artifact |
|---|---|---|
| schema-design | DatabaseDesigner, SchemaArchitect for mixed stores | entity relationships, schema/constraints/index rationale |
| migration-plan | MigrationPlanner plans; Migrator drafts artifacts | ordered steps, lock/pre/post queries and recoverable states |
| retention-policy | DatabaseDesigner + Architect | purpose/class/period/hold/archive/delete decisions |
| query-pattern-audit | Explorer evidence, DatabaseDesigner interpretation | actual queries/workload/plans, index gaps and N+1 candidates |
| sharding-plan | SchemaArchitect + DatabaseDesigner | partition/co-location/skew and rebalance plan |
| data-contract-collision | DatabaseDesigner + Architect | active consumer compatibility and expand/contract transition |
| analytics-readiness | DataPipelineDesigner + SchemaArchitect | business questions, fact grain, SCD/conformed dimensions and lineage |

Full checkpoints: `data_model_complete`, `schema_locked`, `migration_safe`,
`retention_specified`, `query_patterns_documented`. Single and saved loop retain
their narrower scope. Do not collapse migration planning into execution: Migrator
also supports separately exact-authorized execution, with actual target/preconditions.
Neither a planning dispatch nor a rollback script grants that authority.

## Failure methods

DDL lock wait can matter more than statement duration. Concurrent PostgreSQL index
builds permit normal writes but have transaction and invalid-index recovery caveats.
An approved maintenance window can justify a simpler transition; data loss cannot
be reversed by re-adding a column. Record backup/replay/forward-repair evidence.

Pipelines distinguish event time, watermark assumptions, late corrections and sink
idempotency. Replaying a stable event ID must not double-count its effect. Trace
deletion through projections/backups and prevent a later backfill from resurrecting
deleted data. Hashing an identifier does not establish anonymization.

Partition keys require skew and co-location evidence, not cardinality alone.
Preserve dimensional grain/history when late facts join historical dimension versions.
Choose actual store/version mechanisms; no automatic shard-per-tenant, 1TB threshold
or warehouse/vendor selection from a template.

## Acceptance and continuation

Keep schema/SQL, migration/risk, retention, queries and analytics artifacts explicitly
bound to original work and actual policy. No universal 365-day retention or default
production window. Six advisory dimensions remain model, schema, migration, retention,
query evidence and consumer impact; mandatory failure/unknown still blocks.

The shared request/start/result and cold continuation preserve prior iterations.
Interrupted execution with unknown effects is reconciled, never blindly rerun or
rolled back. Reviewers assess separately and never repair their findings.
DA feeds DH recovery/rollout and TQ replay/compatibility checks. DA/SC run serially
unless the actual dependency/isolation contract supports parallel work.

Domain hooks `da-schema-drift-warn`, `da-migration-irreversible-warn` and
`da-retention-violation-warn` remain opt-in observations, not proven enforcement.
