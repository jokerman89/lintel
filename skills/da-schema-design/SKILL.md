---
name: da-schema-design
layer: foundation
description: DA sub-skill — schema definitions with versioning + relationships. Dispatches to DatabaseDesigner + SchemaArchitect agents.
color: blue
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are DA-SCHEMA-DESIGN — the workflow that produces a versioned schema spec.

## What this skill does

Reads operator's data-model intent + profile preferences (primary_store, schema_versioning). Spawns `DatabaseDesigner` for store-specific schema + `SchemaArchitect` for cross-store reasoning (when polyglot persistence applies). Validates output against checklist. Writes `.lintel/state/da/schema-<ts>.sql` (or `.cql` / `.json` per store).

Per L-001: workflow + dispatch contract. Content comes from agents at invocation.

## When to use

- DA full pass schema_locked checkpoint
- Single action `/li:da single --action schema-design`
- New datastore introduction
- Major model evolution within an existing store

## When NOT to use

- Trivial column additions handled in `da-migration-plan`
- Cross-system contract design without persistence shape → `/li:ta single --action api-design`

## Workflow

### Step 1 — Read preferences

```bash
primary_store="${primary_store:-postgres}"     # postgres | mongodb | cassandra | clickhouse | mixed
schema_versioning="${schema_versioning:-timestamp-prefix}"
```

### Step 2 — Spawn DatabaseDesigner through Brief Forge

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Design ${primary_store} schema for [operator's data-model intent]
constraints:
  - versioning: ${schema_versioning}
  - relationship integrity preserved
  - index strategy declared per access pattern
acceptance:
  - schema written to .lintel/state/da/schema-<ts>.{sql|cql|json}
  - relationships documented with cardinality
  - index strategy per query pattern
EOF

/li:brief-forge subagent_spawn da-schema-design DatabaseDesigner brief "$brief_file"
```

### Step 3 — Spawn SchemaArchitect for cross-store reasoning (if mixed primary_store)

```bash
if [ "$primary_store" = "mixed" ]; then
  cross_brief=$(mktemp)
  cat > "$cross_brief" <<EOF
task: Reason about polyglot persistence across declared stores
context_pointers:
  - .lintel/state/da/db-schema.md
constraints:
  - identify which entities live where + why
  - document consistency model across stores
  - declare eventual-vs-strong consistency boundaries
acceptance:
  - per-store partition justified + consistency model documented
EOF
  /li:brief-forge subagent_spawn da-schema-design SchemaArchitect brief "$cross_brief"
fi
```

### Step 4 — Validate against checklist

```
[ ] Each entity has primary key + indexes per query pattern
[ ] Relationships declared with cardinality (1:1, 1:N, N:M)
[ ] Versioning strategy applied (timestamp-prefix or alembic-style)
[ ] Constraints + invariants documented
[ ] Index strategy justified per access pattern
[ ] If polyglot: consistency model documented per store boundary
```

### Step 5 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
audit="$LINTEL_HOME/audit/da-decisions.jsonl"
printf '{"ts":"%s","kind":"da_schema_design","primary_store":"%s","schema_versioning":"%s","operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$primary_store" "$schema_versioning" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$audit"
```

## Status protocol

- **DONE** — schema written, checklist all-pass
- **DONE_WITH_CONCERNS** — written, 1-2 checklist gaps surfaced
- **BLOCKED** — DatabaseDesigner couldn't produce (insufficient context)
- **NEEDS_CONTEXT** — operator's data-model intent unclear

## Integration

**Reads:** profile preferences, existing schema conventions, Brief Forge gate
**Writes:** `.lintel/state/da/schema-<ts>.*`, audit JSONL
**Dispatches to:** DatabaseDesigner (primary), SchemaArchitect (NEW, cross-store)

## Anti-patterns

- **Curating schema patterns in this skill** — DatabaseDesigner's job at invocation (L-001)
- **Skipping index strategy** — required for non-trivial schemas
- **Ignoring polyglot when primary_store is mixed** — SchemaArchitect dispatch matters
