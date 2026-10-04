# Data decision methods

Use for schema, migration, retention or analytics decisions. DatabaseDesigner owns
logical/schema/query and cross-store/partition design; DataPipelineDesigner owns
pipeline and dimensional design. SchemaArchitect is the compatible read-only view
of those methods and keeps its existing polyglot/partition/dimensional output shapes.
Choose one view for the requested outcome; do not dispatch both to repeat reasoning.
MigrationPlanner alone supplies sequencing/risk design; Migrator consumes that plan
and produces artifacts unless execution on an exact target is separately authorized.
No result schema or role tool changes follow from sharing these methods.

## Exact design-to-migration handoff

Carry the original work map, package/leaf IDs, requested capability, schema delta
and source revision, engine/version, consumer/writer inventory, workload, approved
window, lock/backfill constraints and known recovery evidence. DatabaseDesigner
supplies these inputs, not a second migration sequence. MigrationPlanner returns
one ordered plan with per-step validation, stop conditions, restart/failure states,
last reversible state and recovery owner. Missing inputs remain named gaps.

Only after that sequence is accepted does Migrator consume the same plan revision
to prepare SQL/artifacts and synthetic rehearsals. No duplicate sequencing or
parallel planning/execution dispatch: changed inputs return to the sequence owner.
A plan, role handoff or artifact-only rehearsal is not live execution authority.

## Locking and recoverable states

Read the actual engine/version, table shape, dependencies, workload and approved
maintenance window. Estimate both lock acquisition wait and lock hold time; a short
DDL statement can queue behind a long transaction and block later work. Choose bounded
lock/statement timeouts and stop conditions from the workload, not a universal row count.

In PostgreSQL, concurrent index creation allows ordinary writes but is not lock-free:
it waits for relevant transactions, does additional scans, adds I/O and cannot run
inside a transaction block. Failure can leave an invalid index; a failed concurrent
unique index can still enforce uniqueness. Inspect the catalog before recovery.
An existing index name alone does not prove the intended definition or valid state.
Constant-default column addition can avoid a rewrite on supporting versions;
volatile defaults and other constraints need separate analysis. Neither case proves
zero lock wait. Rehearse using the same engine version and representative shape.

For a breaking change, expand, backfill in restartable bounded batches, compare old
and new reads, switch consumers, then contract after evidence that old readers/writers
are gone. Record the last reversible state. Re-adding a dropped column does not
restore its values; name restore/replay or forward repair, its data-loss window and
the actual rehearsal. An approved downtime window may make a simpler migration safer.

## Synthetic worked example: replay and late data

An hourly aggregate receives `(e1, 3)`, `(e2, 5)`, then a replay of `(e1, 3)`.
Blind append-and-sum yields 11; one committed effect per stable event ID yields 8.
Commit the deduplication decision and sink effect atomically where the store permits.
A crash after the effect but before recording the ID must not double-count on retry.
Reusing an ID with a different payload is a conflict to investigate, not a silent drop.

Choose an event-time window, source watermark semantics, permitted lateness and
correction policy from the consumer's freshness/correctness need. A heuristic
watermark is not proof that no older event will arrive. A late event may update an
aggregate, produce a correction, or be rejected to an observed side path according
to that policy. An accumulating pane is a revised total, not an extra increment:
appending every pane can double-count even after input deduplication.

A backfill uses a named source interval/snapshot, transform revision and sink mode.
Verify counts, keys and domain totals, replay the same interval, and interleave a
late event with live processing. "Exactly once" at a broker does not establish
exactly-once effects in an unrelated external sink.

## Cross-store and partition design

For each store, state the authoritative writer, projection version/lag, reconciliation
query and repair owner. A search index is a projection, not a second authority by
accident. For partitioning, compare skew as well as cardinality: one very large tenant
can overload a tenant-key shard despite millions of tenant IDs. Preserve co-location
where transactions need it; quantify scatter/gather and rebalance cost.
Compare candidate keys against actual access patterns, cardinality and heavy-key
distribution, locality and cross-shard transactions. State how a key is routed,
split/rebalanced and migrated, and what workload would falsify the proposed fit.
A second store needs a concrete query/retention need and its continuing coordination
cost, not polyglot variety for its own sake.

## Dimensional design, lineage and retention

For analytics, name fact grain and event identity before measures. Distinguish event
time from ingestion time and SCD effective intervals; a late event must join to the
intended historical dimension version. Trace source fields through transforms to
destinations, including exported files, logs, caches and backups.
Choose SCD Type 1 for explicitly overwritable attributes, Type 2 for required history,
or Type 6 only when its combined current/historical view is justified. Name effective
interval and late-correction rules. Reuse conformed dimensions across facts rather
than inventing a new dimension per fact; test grain/identity, referential joins and
source-to-sink totals before claiming analytics readiness.

Retention and deletion follow applicable purpose, policy, legal holds and contracts.
Hashing an identifier is usually pseudonymization, not proof of anonymization.
Propagate tombstones/corrections through projections and prevent a later restore or
backfill from resurrecting deleted data. Verify with synthetic deletion/replay cases;
do not fetch private records just to demonstrate the method.

## Sources

- PostgreSQL, [CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html),
  concurrent builds and invalid-index recovery.
- PostgreSQL, [Modifying tables](https://www.postgresql.org/docs/current/ddl-alter.html),
  default-value behavior; use the target engine's versioned documentation.
- Apache Beam, [AfterWatermark](https://beam.apache.org/releases/javadoc/current/org/apache/beam/sdk/transforms/windowing/AfterWatermark.html),
  strict versus heuristic watermarks and late firings.
- [GDPR primary text](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng), Articles 5,
  17 and 25 where applicable; interpretation remains with the qualified policy owner.
- [P03 recovery role](../../../agents/engineering/Migrator.md): known failure states,
  exact-scope recovery authority and owned-file snapshot protection remain intact.
