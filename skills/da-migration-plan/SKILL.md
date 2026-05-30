---
name: da-migration-plan
layer: foundation
description: DA sub-skill — reversible migration with zero-downtime path. Dispatches to MigrationPlanner (NEW) + Migrator. Raise-help on migrations above the row threshold.
color: blue
tools: Read, Write, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are DA-MIGRATION-PLAN — the workflow that produces a safe migration plan.

## What this skill does

Takes proposed schema delta + current schema state. Spawns `MigrationPlanner` (new in v4.2) to produce a reversible migration plan with zero-downtime path (per profile `migration_window` preference). Spawns `Migrator` to draft the actual SQL/DDL. Raises help when affected rows exceed `require_migration_review_above_rows`.

## When to use

- DA full pass migration_safe checkpoint
- Single action `/li:da single --action migration-plan`
- Before any migration touching ≥1 production table
- After schema redesign requires data backfill

## When NOT to use

- Schema-only additive change (new optional column, new index) — `Migrator` agent direct
- Application-level data transform (no schema change) — application code

## Workflow

### Step 1 — Read preferences + delta

```bash
migration_window="${migration_window:-zero-downtime-required}"   # zero-downtime-required | maintenance-window-ok | tolerated
review_threshold="${review_threshold:-100000}"

# Delta input: schema delta file OR explicit description
delta_file="${1:-.lintel/state/da/schema-delta.md}"
[ -f "$delta_file" ] || { echo "ERROR: $delta_file not found"; exit 1; }
```

### Step 2 — Estimate affected rows

```bash
# Heuristic: parse the delta for table names, run COUNT or read row-count cache
affected_rows=$(estimate_affected_rows "$delta_file")
```

### Step 3 — Spawn MigrationPlanner for plan

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Produce migration plan for declared schema delta
context_pointers:
  - $delta_file
  - .lintel/state/da/current-schema.sql (if present)
constraints:
  - migration_window: ${migration_window}
  - reversibility: required (down-migration declared)
  - per-step duration: estimated
  - affected rows: ${affected_rows}
acceptance:
  - migration steps with order + estimated duration
  - rollback path per step
  - lock acquisition strategy if zero-downtime
  - data validation queries pre + post
EOF

/li:brief-forge subagent_spawn da-migration-plan MigrationPlanner brief "$brief_file"
```

### Step 4 — Spawn Migrator for DDL

```bash
ddl_brief=$(mktemp)
cat > "$ddl_brief" <<EOF
task: Draft SQL/DDL for migration plan
context_pointers:
  - .lintel/state/da/migration-plan.md
constraints:
  - up-migration matches plan steps
  - down-migration is true inverse (no data loss for additive; documented loss for destructive)
  - transactional boundaries respect store capabilities
acceptance:
  - up.sql + down.sql per step
EOF

/li:brief-forge subagent_spawn da-migration-plan Migrator brief "$ddl_brief"
```

### Step 5 — Raise-help if affected rows > review_threshold

```bash
if [ "$affected_rows" -gt "$review_threshold" ]; then
  echo "RAISE_HELP: migration affects $affected_rows rows (>$review_threshold)"
  # DA module surfaces AskUserQuestion: operator confirms downtime window or refines plan
fi
```

### Step 6 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".lintel/state/da/migration-plan-$ts.md"
{
  echo "# Migration plan — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Window: $migration_window"
  echo "## Affected rows: $affected_rows"
  echo ""
  cat .lintel/state/da/migration-plan.md
  echo ""
  echo "## DDL"
  echo "### up.sql"
  cat .lintel/state/da/up.sql
  echo "### down.sql"
  cat .lintel/state/da/down.sql
} > "$out"

printf '{"ts":"%s","kind":"da_migration_plan","window":"%s","affected_rows":%d,"raise_help":%s,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$migration_window" "$affected_rows" \
  "$([ "$affected_rows" -gt "$review_threshold" ] && echo true || echo false)" \
  "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/da-decisions.jsonl"
```

## Status protocol

- **DONE** — plan + DDL produced, affected_rows ≤ threshold
- **DONE_WITH_CONCERNS** — plan + DDL produced, 1-2 reversibility gaps
- **BLOCKED** — raise_help triggered (rows > threshold) awaiting operator decision
- **NEEDS_CONTEXT** — schema delta file missing or malformed

## Integration

**Reads:** profile preferences, delta file, current schema
**Writes:** `.lintel/state/da/migration-plan-<ts>.md`, `up.sql`, `down.sql`, audit JSONL
**Dispatches to:** MigrationPlanner (NEW, plan), Migrator (DDL drafting)
**Hook integration:** `da-migration-irreversible-warn` hook fires pre-commit on migration files without rollback

## Anti-patterns

- **Skipping reversibility** — every up-migration has a down-migration; destructive cases document data loss
- **Hardcoding zero-downtime when pack says maintenance-window-ok** — read profile
- **Treating row count as unimportant** — review_threshold exists for a reason
- **Curating migration patterns** — MigrationPlanner produces, this skill orchestrates (L-001)
