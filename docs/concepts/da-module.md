# DA module — data-architecture for engineering depth

**Last updated:** 2026-05-30 (v4.2)
**Status:** Concept doc — referenced by `skills/da/SKILL.md` + 7 sub-skills + 2 agents + 3 hooks

> When work touches data — new datastore, schema migration, retention policy, sharding plan, analytics readiness — running it through plain BUILD discards what the operator needs: versioned schemas, zero-downtime migration discipline, retention compliance, query-pattern surface, consumer-impact analysis. DA is the **second engineering-domain module in v4.x**, following the same pattern as TA documented in [engineering-modules.md](engineering-modules.md).

## The problem

Pre-v4.2, data-touching work happened through ad-hoc invocations:
- DatabaseDesigner spawned manually when operator remembered
- Migrations written without explicit rollback paths
- Retention policy in scattered docs or operator memory
- Schema changes shipped without consumer-impact analysis
- N+1 queries surfaced in production, not pre-merge

The user explicitly named the gap: "When the work touches data models, schemas, storage, migrations, or analytics, invoke DA to produce schema-grade decisions and migrations."

The module fixes it with three granularities — `full`, `loop`, `single` — and 5 checkpoints with recovery.

## The model

```
Operator invocation
       │
       ▼
/li:da {full|loop|single --action <name>}
       │
       │  Read pack policy + profile.engineering.data_architecture.*
       ▼
Granularity dispatch:
       │
       ├── full   → data_model_complete → schema_locked → migration_safe
       │           → retention_specified → query_patterns_documented
       │           → 6-dim scoring rubric → SHIP (score ≥80) or surface
       │
       ├── loop   → re-run schema + migration + retention → diff vs prior
       │
       └── single → direct sub-skill (no checkpoints, no orchestration)
                   da-schema-design / da-migration-plan / da-retention-policy /
                   da-query-pattern-audit / da-sharding-plan /
                   da-data-contract-collision / da-analytics-readiness
                       │
                       ▼
                   Spawn agent via Brief Forge:
                   DatabaseDesigner / DataPipelineDesigner / Migrator /
                   SchemaArchitect (NEW) / MigrationPlanner (NEW) /
                   Architect / Explorer
                       │
                       ▼
                   Output → .claude/runtime/state/da/<action>-<ts>.{md,sql,json}
                   Audit → .claude/runtime/audit/da-decisions.jsonl
```

## The five checkpoints (full pass)

### 1. `data_model_complete`
Entities + relationships mapped. Produced by `da-schema-design` + DatabaseDesigner.
Pass criterion: every entity has a name, primary key, and cardinality-declared relationships.

### 2. `schema_locked`
Schema with versioning + migration path declared. Produced by `da-schema-design` + `da-data-contract-collision` (consumer side).
Pass criterion: schema_versioning strategy applied; if changes from prior iteration, migration path declared; if ≥3 consumers break, raise-help.

### 3. `migration_safe`
Zero-downtime OR reversible per pack policy. Produced by `da-migration-plan` + MigrationPlanner.
Pass criterion: every up-migration has a documented down-migration OR explicit data-loss acceptance; affected-rows below threshold OR explicit downtime-window confirmation.

### 4. `retention_specified`
Per-data-class retention + archival + deletion. Produced by `da-retention-policy`.
Pass criterion: every classified data class has retention days + archival mechanism + deletion verification; no compliance conflicts (or explicit override).

### 5. `query_patterns_documented`
Read/write ratios + hot paths. Produced by `da-query-pattern-audit`.
Pass criterion: query enumeration complete; hot paths identified; missing-index recommendations surfaced.

## The 6-dimensional scoring rubric (full pass exit gate)

| Dimension | Score 0-100 | Pass threshold | Source artifact |
|---|---|---|---|
| Data model completeness | _ | 80 | `.claude/runtime/state/da/data-model.md` |
| Schema locked | _ | 80 | `.claude/runtime/state/da/schema-<ts>.sql` + version metadata |
| Migration safety | _ | 80 | `.claude/runtime/state/da/migration-plan-<ts>.md` |
| Retention specified | _ | 80 | `.claude/runtime/state/da/retention-policy-<ts>.md` |
| Query patterns documented | _ | 80 | `.claude/runtime/state/da/query-pattern-audit-<ts>.md` |
| Consumer impact analyzed | _ | 80 | `.claude/runtime/state/da/data-contract-collision-<ts>.md` |

Full-pass exit gate: every dimension ≥ 80 OR explicit operator override.

## Sub-skill catalog

| Sub-skill | Primary agent | Other agents | Output |
|---|---|---|---|
| `da-schema-design` | DatabaseDesigner | SchemaArchitect (NEW, polyglot) | schema with versioning + relationships |
| `da-migration-plan` | MigrationPlanner (NEW) | Migrator | reversible migration with zero-downtime path |
| `da-retention-policy` | DatabaseDesigner | Architect | per-data-class retention + archival + deletion |
| `da-query-pattern-audit` | Explorer | DatabaseDesigner | hot paths + index gaps + N+1 candidates |
| `da-sharding-plan` | SchemaArchitect (NEW) | DatabaseDesigner | partition strategy + rebalancing playbook |
| `da-data-contract-collision` | DatabaseDesigner | Architect | consumer breakage + migration plan |
| `da-analytics-readiness` | DataPipelineDesigner | SchemaArchitect (NEW) | OLAP path + dimensional model |

L-002 inventory: 5 of 7 dispatches reuse existing agents (DatabaseDesigner, DataPipelineDesigner, Migrator, Architect, Explorer). Only 2 new agents (SchemaArchitect, MigrationPlanner) for genuinely new capability.

## Agent additions (v4.2)

### `SchemaArchitect`
- **Purpose:** cross-store reasoning, partition-key selection, dimensional modeling
- **Why new:** DatabaseDesigner is single-store; SchemaArchitect reasons across boundaries
- **Spawned by:** `da-schema-design` (when polyglot), `da-sharding-plan`, `da-analytics-readiness`

### `MigrationPlanner`
- **Purpose:** zero-downtime migration planning, reversibility analysis, lock-acquisition strategy
- **Why new:** Migrator drafts DDL; MigrationPlanner reasons about safety + sequencing
- **Spawned by:** `da-migration-plan`

## Hook additions (v4.2)

All three are warn-only (per engineering-modules pattern). Each uses unified `audit_log` from `bin/_audit.sh`.

### `da-schema-drift-warn`
Pre-edit on files claimed by schema-flavored ADRs. Surfaces: "schema file is claimed by ADR-X — consider updating the ADR."

### `da-migration-irreversible-warn`
Pre-commit on migration files lacking rollback OR with destructive operations. Surfaces: "destructive operations detected ($ops) without paired rollback — consider expand-and-contract via `/li:da single --action migration-plan`."

### `da-retention-violation-warn`
Pre-edit on data-access code skipping retention filters. Surfaces: "data access without retention filter — $table/$filter."

## Profile preferences

Under `engineering.data_architecture.*` in `~/.lintel/profile.yaml`:

```yaml
engineering:
  data_architecture:
    primary_store: postgres                      # postgres | mongodb | cassandra | clickhouse | mixed
    migration_window: zero-downtime-required     # zero-downtime-required | maintenance-window-ok | tolerated
    retention_default_days: 365
    schema_versioning: timestamp-prefix
    require_migration_review_above_rows: 100000
```

Hooks + sub-skills read these. Defaults baked in when absent.

## Pack overrides

Packs can declare `data_architecture.*` overrides:

```yaml
# packs/some-pack/pack.yaml
data_architecture:
  migration_glob: "db/migrations/*.sql,supabase/migrations/*.sql"
  external_consumer_registries:
    - https://internal.registry/data-consumers
  deprecation_window_days: 90
```

## Audit trail

Every module + sub-skill + checkpoint writes to `.claude/runtime/audit/da-decisions.jsonl`:

```jsonl
{"ts":"...","kind":"da_module_complete","granularity":"full","score":85,"checkpoints_passed":5,"primary_store":"postgres"}
{"ts":"...","kind":"da_schema_design","primary_store":"postgres","schema_versioning":"timestamp-prefix"}
{"ts":"...","kind":"da_migration_plan","window":"zero-downtime-required","affected_rows":250000,"raise_help":true}
{"ts":"...","kind":"da_data_contract_collision","consumers":12,"breaking":4,"raise_help":true}
```

## Composition — DA as parallel branch in full engineering pass

Per engineering-modules.md §"Composition":

```
TA
  │
  ├── DA  ┐  (parallel — data + security are independent at this layer)
  ├── SC  ┘
  │
  ▼
DH
  │
  ▼
TQ
```

DA runs in parallel with SC after TA produces architecture decisions. SC reads compliance-bound fields (which DA needs for retention policy); DA reads architectural boundaries (which SC needs for threat modeling). Each module makes its own decisions on its own clock.

## Anti-patterns

- **Running migrations without `migration_safe` checkpoint** — production migrations fail loud in expensive ways
- **Single retention value for all data** — classify first
- **Sharding without query-pattern audit** — partition key choice is query-dependent
- **Inventing new agents when existing cover** — L-002 inventory pre-PR
- **Curating data-model patterns in sub-skills** — sub-skills are dispatch contracts (L-001)
- **Hardcoding primary_store** — read from profile
- **Skipping retention conflict detection** — compliance hooks exist for a reason

## Integration points

**Reads:**
- `~/.lintel/profile.yaml` `engineering.data_architecture.*`
- `lib/pack-resolver.sh` for pack policy
- Existing data agents + 2 new agents
- Schema-flavored ADR locations

**Writes:**
- `.claude/runtime/state/da/*.{md,sql,json}` (per-action artifacts)
- `.claude/runtime/audit/da-decisions.jsonl`
- Brief Forge envelopes through the standard gate

**Triggered by:**
- Operator: `/li:da {full|loop|single --action <name>}`
- BUILD phase: invokes as sub-module when data-model intent detected
- `/li:full-engineering-pass` (when composition skill ships): parallel branch after TA

**Tested by:**
- `tests/shape/da-module-contract.sh` (engineering-module-contract for DA)
- `tests/unit/da-routing.sh` (granularity dispatch + sub-skill enumeration)
