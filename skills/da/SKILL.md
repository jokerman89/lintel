---
name: da
layer: foundation
workflow_root: true
description: Phase 4 v4.2 — data-architecture module. Three granularities (full / loop / single). Sub-skills dispatch to existing data agents. 5 checkpoints, 6-dim scoring rubric, 3 warn-only hooks, profile-driven preferences.
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
| `/li:da single --action <name>` | targeted operation (see sub-skill catalog) | one of: schema-design / migration-plan / retention-policy / query-pattern-audit / sharding-plan / data-contract-collision / analytics-readiness |

## When to use

- New datastore (Postgres / MongoDB / Cassandra / ClickHouse / etc.)
- Major migration touching ≥1 table with consumers
- Retention policy for new data class
- Analytics pipeline design (OLAP, dimensional modeling)
- BUILD phase detected data-model intent (Phase 4 wiring auto-invokes)

## When NOT to use

- Pure code refactor that doesn't touch persistence → `/li:cycle`
- API design without schema impact → `/li:ta single --action api-design`
- Deployment of an unchanged schema → `/li:dh` (v4.4)

## Sub-skill catalog

Per L-001: sub-skills are workflow + dispatch contracts. Content comes from agents at invocation.

| Sub-skill | Dispatches to | Output |
|---|---|---|
| `da-schema-design` | DatabaseDesigner + SchemaArchitect (NEW) | schema definitions with versioning + relationships |
| `da-migration-plan` | MigrationPlanner (NEW) + Migrator | reversible migration with zero-downtime path |
| `da-retention-policy` | DatabaseDesigner + Architect | per-data-class retention + archival + deletion policy |
| `da-query-pattern-audit` | DatabaseDesigner + Explorer | read/write ratios, hot paths, missing indexes |
| `da-sharding-plan` | SchemaArchitect (NEW) + DatabaseDesigner | partitioning strategy + rebalancing approach |
| `da-data-contract-collision` | DatabaseDesigner + Architect | schema change impact across consumers |
| `da-analytics-readiness` | DataPipelineDesigner + SchemaArchitect (NEW) | OLAP path, dimensional model, ETL boundaries |

## Workflow

### Step 1 — Parse invocation

```bash
granularity="${1:?usage: /li:da {full|loop|single --action <name>}}"
case "$granularity" in
  full|loop) action="" ;;
  single)
    [ "$2" = "--action" ] || { echo "ERROR: --action required for single"; exit 1; }
    action="$3"
    case "$action" in
      schema-design|migration-plan|retention-policy|query-pattern-audit|sharding-plan|data-contract-collision|analytics-readiness) ;;
      *) echo "ERROR: unknown action '$action'"; exit 1 ;;
    esac
    ;;
esac
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
case "$action" in
  schema-design)
    /li:da-schema-design --pref primary_store="$primary_store"
    ;;
  migration-plan)
    /li:da-migration-plan --pref migration_window="$migration_window" --pref review_threshold="$review_threshold"
    ;;
  retention-policy)
    /li:da-retention-policy --pref retention_default="$retention_default"
    ;;
  query-pattern-audit)
    /li:da-query-pattern-audit
    ;;
  sharding-plan)
    /li:da-sharding-plan
    ;;
  data-contract-collision)
    /li:da-data-contract-collision
    ;;
  analytics-readiness)
    /li:da-analytics-readiness
    ;;
esac
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
- **NEEDS_CONTEXT** — `--action` missing for single, OR no prior state for loop

## Pause-points

- Per checkpoint failure: AskUserQuestion with three paths (Re-loop / Accept-with-concern / Raise-help)
- Pre-ship if score < 80: surface dimension breakdown, ask to re-loop or accept
- Migration against >`review_threshold` rows: explicit downtime-window confirmation

## Hop-in support

YES. `/li:da loop` resumes from prior state at `.claude/runtime/state/da/00-state.md`. `/li:da single --action <name>` enters at the specific sub-skill without orchestration.

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

## Voice tier behavior

`voice: internal`. DA produces operator-facing data-model artifacts. Customer-facing voice picks up at the SHIP phase when the active pack adds voice alignment via Brief Forge (an external pack like lintel-caip-pack supplies this; none by default).
