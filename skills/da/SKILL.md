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
gap_if_skipped: "Data-touching work proceeds with no schema versioning, no zero-downtime migration discipline, no retention policy, no query-pattern surface; production migrations break consumers and orphaned data accumulates undetected."
navigation:
  primary_intent: produce schema-grade decisions and migration safety when work touches data models
  triggers:
    - new datastore / major migration / analytics path
    - operator types /li:da {full|loop|single --action <name>}
    - BUILD phase detects data-model intent (Phase 4 wiring)
  sibling_workflows:
    - /li:ta — tech-architecture module (v4.1)
    - /li:sc — security-compliance module (v4.3)
    - /li:dh — devops-hosting module (v4.4)
    - /li:tq — testing-qa module (v4.5)
    - /li:full-engineering-pass — composes all 5 modules in DAG order
  risk_level: medium
  auto_mode_eligible: false
  estimated_tokens: 80000
domain:
  preferences_root: engineering.data_architecture.*
  granularities: [full, loop, single]
  checkpoints:
    - data_model_complete: all entities and relationships mapped
    - schema_locked: schema with versioning + migration path declared
    - migration_safe: zero-downtime or reversible per pack policy
    - retention_specified: retention + archival + deletion policy per data class
    - query_patterns_documented: read/write ratios + hot paths surfaced
  recovery:
    - on_failure: revert to last-locked checkpoint, surface gap, AskUserQuestion (Re-loop | Accept-with-concern | Raise-help)
  continuation:
    - after_fix: resume at failed checkpoint, job state preserves loop position
  raise_help:
    - migration_against_table_above_100k_rows: operator confirms downtime window
    - retention_conflicts_with_compliance_policy: operator decides override or comply
    - schema_change_breaks_3_plus_consumers: operator decides migration path
---

You are the DA (data-architecture) module — Phase 4 v4.2 of Lintel.

## What this module does

Produces schema-grade decisions and migration safety when work touches data models. Three granularities — full pass for new datastores, loop iteration for schema refinement, single action for targeted ops.

| Entry | When | Outputs |
|---|---|---|
| `/li:da full` | new datastore / major migration | `data-model.md` + schema definitions + migration plan + retention policy + access patterns |
| `/li:da loop` | iterative schema refinement | revised schema + diff against prior + backward-compat analysis |
| `/li:da <capability>` · `/li:da single --action <capability>` | targeted operation (see Sub-capability dispatch) | one artifact per the dispatch table below |

## When to use

- New datastore (Postgres / MongoDB / Cassandra / ClickHouse / etc.)
- Major migration touching ≥1 table with consumers
- Retention policy for new data class
- Analytics pipeline design (OLAP, dimensional modeling)
- BUILD phase detected data-model intent (Phase 4 wiring auto-invokes)

## When NOT to use

- Pure code refactor that doesn't touch persistence → `/li:cycle`
- API design without schema impact → `/li:ta api-design`
- Deployment of an unchanged schema → `/li:dh` (v4.4)

## Sub-capability dispatch

Per ADR-0009 the seven capabilities live here as dispatch rows — there are no per-capability
skill files. Invoke one directly as `/li:da <capability>` (long form: `/li:da single --action
<capability>`). Per L-001 each capability is a workflow + dispatch contract: content comes from
agents at invocation (spawned via `/li:brief-forge subagent_spawn`); each emits
`.claude/runtime/state/da/<capability>-<ts>.md` and appends the module audit line (Step 6).

| Capability | Dispatches to (agents) | Produces | Raise-help / notes |
|---|---|---|---|
| `schema-design` | DatabaseDesigner (+ SchemaArchitect when `primary_store=mixed`) | versioned schema spec `schema-<ts>.{sql\|cql\|json}` with relationships + index strategy | prefs: `primary_store` (postgres\|mongodb\|cassandra\|clickhouse\|mixed), `schema_versioning` (timestamp-prefix); validation checklist below |
| `migration-plan` | MigrationPlanner + Migrator | migration plan + per-step `up.sql`/`down.sql` | RAISE_HELP when affected rows > `review_threshold` (default 100000) — downtime-window confirmation (BLOCKED); prefs: `migration_window` (zero-downtime-required\|maintenance-window-ok\|tolerated), `review_threshold`; pairs with `da-migration-irreversible-warn` hook; acceptance below |
| `retention-policy` | DatabaseDesigner + Architect | per-data-class retention + archival + deletion policy | RAISE_HELP when pack compliance hooks match gdpr/pii AND `retention_default` > 365 days (BLOCKED); classes: PII / customer-data / operational-telemetry / aggregate-only; lifecycle: active → warm → cold → archived → deleted; pairs with `da-retention-violation-warn` hook |
| `query-pattern-audit` | Explorer + DatabaseDesigner | read/write ratios, hot paths (top-5 by frequency), index gaps, N+1 candidates | no prefs; output reused by sharding-plan + analytics-readiness; index gaps = DONE_WITH_CONCERNS |
| `sharding-plan` | SchemaArchitect + DatabaseDesigner | partition strategy + rebalancing playbook + cross-shard query workarounds | partition key: cardinality + co-location; tenant-isolation → shard-per-tenant; per-store mechanics (postgres → declarative/Citus; mongodb → zone tags; cassandra → token-aware); reuses query-pattern-audit + TA scaling-plan <1 day old; no sharding below single-machine Postgres <1TB |
| `data-contract-collision` | DatabaseDesigner + Architect (when breaking > 0) | schema change impact across consumers + migration plan | RAISE_HELP at ≥3 breaking consumers (BLOCKED); breaking = column drop / type narrowing / null→not-null; prefer expand-and-contract (add → backfill → switch reads → drop); grace window from pack `data_architecture.deprecation_window_days`; triggered by `da-schema-drift-warn` hook |
| `analytics-readiness` | DataPipelineDesigner + SchemaArchitect | OLAP path (warehouse + CDC/batch ingestion + refresh cadence) + dimensional model | NEEDS_CONTEXT without business questions (arg, `$BUSINESS_QUESTIONS`, or `business-questions.md`); pref: `primary_store`; reuses query-pattern-audit <7 days old; dimensional rules below |

### schema-design — validation checklist

- [ ] Each entity has primary key + indexes per query pattern
- [ ] Relationships declared with cardinality (1:1, 1:N, N:M)
- [ ] Versioning strategy applied (timestamp-prefix or alembic-style)
- [ ] Constraints + invariants documented
- [ ] Index strategy justified per access pattern
- [ ] If polyglot: consistency model documented per store boundary

### migration-plan — acceptance

- migration steps with order + estimated duration
- rollback path per step
- lock acquisition strategy if zero-downtime
- data validation queries pre + post

### analytics-readiness — dimensional-model rules

- fact table grain documented per fact (one row per X)
- slowly-changing-dimension strategy per dimension (Type 1 / Type 2 / Type 6)
- conformed dimensions across facts (no duplicate "Customer" with different IDs)

## Workflow

### Step 1 — Parse invocation

```bash
granularity="${1:?usage: /li:da {full|loop|<capability>|single --action <capability>}}"
capabilities="schema-design|migration-plan|retention-policy|query-pattern-audit|sharding-plan|data-contract-collision|analytics-readiness"
case "$granularity" in
  full|loop) action="" ;;
  single)
    [ "$2" = "--action" ] || { echo "ERROR: --action required for single"; exit 1; }
    action="$3" ;;
  *) action="$granularity"; granularity="single" ;;   # ADR-0009 shorthand: /li:da <capability>
esac
if [ "$granularity" = "single" ]; then
  echo "$action" | grep -qE "^(${capabilities})$" || { echo "ERROR: unknown capability '$action'"; exit 1; }
fi
```

### Step 2 — Read pack + profile preferences

```bash
source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh"

# Profile preferences (engineering.data_architecture.*)
PROFILE="$LINTEL_HOME/profile.yaml"
primary_store=$(grep -A20 '^engineering:' "$PROFILE" 2>/dev/null | grep -A8 'data_architecture:' | grep 'primary_store:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
primary_store="${primary_store:-postgres}"
migration_window=$(grep -A20 '^engineering:' "$PROFILE" 2>/dev/null | grep -A8 'data_architecture:' | grep 'migration_window:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
migration_window="${migration_window:-zero-downtime-required}"
retention_default=$(grep -A20 '^engineering:' "$PROFILE" 2>/dev/null | grep -A8 'data_architecture:' | grep 'retention_default_days:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
retention_default="${retention_default:-365}"
review_threshold=$(grep -A20 '^engineering:' "$PROFILE" 2>/dev/null | grep -A8 'data_architecture:' | grep 'require_migration_review_above_rows:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
review_threshold="${review_threshold:-100000}"
```

### Step 3 — Dispatch by granularity

#### `full` granularity

```bash
mkdir -p .claude/runtime/state/da
audit=".claude/runtime/audit/da-decisions.jsonl"
mkdir -p "$(dirname "$audit")"

# Run checkpoint chain
for checkpoint in data_model_complete schema_locked migration_safe retention_specified query_patterns_documented; do
  echo "─── Checkpoint: $checkpoint ───"
  run_checkpoint "$checkpoint" || handle_checkpoint_failure "$checkpoint"
  audit_checkpoint "$checkpoint" "$verdict"
done

# Apply 6-dim scoring rubric
score=$(apply_scoring_rubric)
if [ "$score" -lt 80 ]; then
  echo "DA full pass score=$score (threshold 80) — surface concerns"
  exit 1
fi

echo "DA full pass complete — score=$score, output .claude/runtime/state/da/"
```

#### `loop` granularity

```bash
if [ ! -f ".claude/runtime/state/da/00-state.md" ]; then
  echo "ERROR: no prior DA state — use /li:da full first"
  exit 1
fi

prior_iteration=$(grep -E '^iteration:' .claude/runtime/state/da/00-state.md | head -1 | awk '{print $2}')
new_iteration=$((prior_iteration + 1))

# Re-run schema + migration + retention checkpoints
run_checkpoint schema_locked
run_checkpoint migration_safe
run_checkpoint retention_specified

# Diff against prior iteration (schema backward-compat focus)
echo "Schema diff vs iteration $prior_iteration:" > .claude/runtime/state/da/iteration-${new_iteration}-diff.md
diff .claude/runtime/state/da/iteration-${prior_iteration}-schema.sql .claude/runtime/state/da/iteration-${new_iteration}-schema.sql \
  >> .claude/runtime/state/da/iteration-${new_iteration}-diff.md || true
```

#### `single` granularity

```bash
# ADR-0009: no sub-skill files — dispatch straight off the Sub-capability dispatch table.
# Spawn the capability's agents via /li:brief-forge subagent_spawn, pass the prefs listed
# in its row (schema-design ← primary_store; migration-plan ← migration_window +
# review_threshold; retention-policy ← retention_default), emit
# .claude/runtime/state/da/${action}-<ts>.md, append the audit line (Step 6).
dispatch_capability "$action"   # no loop, no checkpoints
```

### Step 4 — Checkpoint failure handling (recovery + raise-help)

```bash
handle_checkpoint_failure() {
  local checkpoint="$1"
  echo "Checkpoint '$checkpoint' FAILED"

  case "$checkpoint" in
    migration_safe)
      if [ "$affected_rows" -gt "$review_threshold" ]; then
        ask_user_question "Migration affects $affected_rows rows (>$review_threshold). Re-loop / Accept-with-concern / Raise-help (confirm downtime window)?"
      fi
      ;;
    retention_specified)
      if [ "$compliance_conflict" = "true" ]; then
        ask_user_question "Retention policy conflicts with compliance. Re-loop / Accept-with-concern / Raise-help (decide override or comply)?"
      fi
      ;;
    schema_locked)
      if [ "$breaking_consumer_count" -ge 3 ]; then
        ask_user_question "Schema change breaks $breaking_consumer_count consumers. Re-loop / Accept-with-concern / Raise-help?"
      fi
      ;;
  esac

  revert_to_last_locked
}
```

### Step 5 — 6-dimensional scoring rubric

```
| Dimension | Score 0-100 |
|---|---|
| Data model completeness (entities + relationships) | <D1> |
| Schema locked (versioning + migration path) | <D2> |
| Migration safety (zero-downtime or reversible) | <D3> |
| Retention specified (per data class) | <D4> |
| Query patterns documented (read/write ratios) | <D5> |
| Consumer impact analyzed | <D6> |

Pass threshold per dimension: 80.
Full-pass exit: every dimension ≥ 80 OR explicit operator override.
```

### Step 6 — Audit + emit ship report

```bash
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
printf '{"ts":"%s","kind":"da_module_complete","granularity":"%s","score":%d,"checkpoints_passed":%d,"primary_store":"%s","operator":"%s"}\n' \
  "$ts" "$granularity" "$score" "$passed_count" "$primary_store" "$(whoami 2>/dev/null || echo unknown)" \
  >> ".claude/runtime/audit/da-decisions.jsonl"
```

## Status protocol

- **DONE** — granularity completed, score ≥ 80 (full) or target dimension improved (loop) or action complete (single)
- **DONE_WITH_CONCERNS** — completed but score 60-79 OR raise-help triggered without operator resolution
- **BLOCKED** — checkpoint failed, operator chose Raise-help, awaiting decision
- **NEEDS_CONTEXT** — unknown capability for single, OR no prior state for loop

## Integration

**Reads:**
- `~/.lintel/profile.yaml` `engineering.data_architecture.*` block
- `lib/pack-resolver.sh` for pack policy
- Existing data agents: DatabaseDesigner, DataPipelineDesigner, Migrator
- New agents: SchemaArchitect, MigrationPlanner
- Existing schema ADRs (`.claude/decisions/`, `docs/decisions/`)

**Writes:**
- `.claude/runtime/state/da/data-model.md` (full)
- `.claude/runtime/state/da/iteration-N-schema.sql` (per iteration)
- `.claude/runtime/state/da/iteration-N-diff.md` (loop)
- `.claude/runtime/state/da/migration-plan.md`
- `.claude/runtime/state/da/retention-policy.md`
- `.claude/runtime/audit/da-decisions.jsonl`
- Brief Forge envelopes through the standard gate

**Triggered by:**
- Operator: `/li:da {full|loop|single --action <name>}`
- BUILD phase: invokes as sub-module when data-model intent detected
- `/li:full-engineering-pass`: parallel branch with SC in the composition DAG (after TA)

**Hooks:**
- `hooks/shared/da-schema-drift-warn/` (pre-edit on schema-ADR-claimed files)
- `hooks/shared/da-migration-irreversible-warn/` (pre-commit on migration without rollback)
- `hooks/shared/da-retention-violation-warn/` (pre-edit on data-access code skipping retention)

## Anti-patterns

- **Skipping zero-downtime requirement without explicit accept** — pack policy is the master gate
- **Treating migration size as terminal** — surface threshold, operator confirms downtime
- **Inventing new agents when existing cover** — DatabaseDesigner + DataPipelineDesigner cover most DA work
- **Hardcoding primary_store** — read from profile preferences
- **Silent score-below-threshold** — surface to operator with dimension breakdown
- **Blocking on hook warnings** — DA hooks warn; blocking is operator's explicit decision
