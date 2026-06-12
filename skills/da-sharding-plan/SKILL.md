---
name: da-sharding-plan
layer: foundation
description: DA sub-skill — partitioning strategy + rebalancing approach. Dispatches to SchemaArchitect (NEW) + DatabaseDesigner.
color: blue
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are DA-SHARDING-PLAN — the workflow that produces a partitioning + rebalancing strategy.

## What this skill does

Takes scaling target (from `/li:ta-scaling-plan` if available, else operator) + current data shape + query patterns (from `/li:da-query-pattern-audit` if available). Spawns `SchemaArchitect` for partition-key selection + `DatabaseDesigner` for store-specific sharding mechanics. Produces a sharding plan with rebalancing approach.

## When to use

- DA full pass after query_patterns_documented (informs partition key choice)
- Single action `/li:da single --action sharding-plan`
- Anticipated growth beyond single-node capacity
- After hotspot identification in production

## When NOT to use

- Read replicas / read-scaling only — that's deployment territory `/li:dh` v4.4
- Single-shard databases (SQLite, single-machine Postgres < 1TB) — no sharding needed

## Workflow

### Step 1 — Read context

```bash
# Reuse outputs from prior sub-skills if recent
query_audit=$(find .claude/runtime/state/da -name "query-pattern-audit-*.md" -mtime -1 2>/dev/null | sort | tail -1)
scaling_plan=$(find .claude/runtime/state/ta -name "scaling-plan-*.md" -mtime -1 2>/dev/null | sort | tail -1)

primary_store="${primary_store:-postgres}"
scaling_target="${SCALING_TARGET:-from-ta-scaling-plan}"
```

### Step 2 — Spawn SchemaArchitect for partition-key selection

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Select partition key for declared data + query patterns
context_pointers:
  - $query_audit
  - $scaling_plan
  - .claude/runtime/state/da/data-model.md
constraints:
  - cardinality: high enough to spread, not so high it explodes per-shard cost
  - co-location: keep frequently-joined entities on same shard
  - scaling target: ${scaling_target}
acceptance:
  - partition key per shardable entity + justification
  - co-location boundaries documented
  - flagged: tenant-isolation cases (shard-per-tenant pattern)
EOF

/li:brief-forge subagent_spawn da-sharding-plan SchemaArchitect brief "$brief_file"
```

### Step 3 — Spawn DatabaseDesigner for store-specific mechanics

```bash
mechanics_brief=$(mktemp)
cat > "$mechanics_brief" <<EOF
task: Translate partition strategy to ${primary_store} sharding mechanics
context_pointers:
  - .claude/runtime/state/da/partition-strategy.md
constraints:
  - per primary_store (postgres → declarative partitioning / Citus / native; mongodb → sharded cluster + zone tags; cassandra → token-aware)
  - rebalancing approach: online vs maintenance-window
  - cross-shard query handling documented
acceptance:
  - shard-key DDL per table
  - rebalancing playbook
  - cross-shard query patterns + workarounds
EOF

/li:brief-forge subagent_spawn da-sharding-plan DatabaseDesigner brief "$mechanics_brief"
```

### Step 4 — Emit + audit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/da/sharding-plan-$ts.md"
{
  echo "# Sharding plan — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Target store: $primary_store"
  echo "## Scaling target: $scaling_target"
  echo ""
  echo "## Partition strategy"
  cat .claude/runtime/state/da/partition-strategy.md
  echo ""
  echo "## Store mechanics"
  cat .claude/runtime/state/da/sharding-mechanics.md
} > "$out"

printf '{"ts":"%s","kind":"da_sharding_plan","store":"%s","scaling_target":"%s","operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$primary_store" "$scaling_target" "$(whoami 2>/dev/null || echo unknown)" \
  >> ".claude/runtime/audit/da-decisions.jsonl"
```

## Status protocol

- **DONE** — sharding plan emitted with rebalancing playbook
- **DONE_WITH_CONCERNS** — emitted but cross-shard query workarounds incomplete
- **BLOCKED** — SchemaArchitect couldn't pick partition key (operator review needed)

## Integration

**Reads:** prior sub-skill outputs (query audit + scaling plan), data model
**Writes:** `.claude/runtime/state/da/sharding-plan-<ts>.md`, audit JSONL
**Dispatches to:** SchemaArchitect (NEW, partition selection), DatabaseDesigner (store mechanics)

## Anti-patterns

- **Sharding without query-pattern audit** — partition key choice is query-pattern-dependent
- **Hardcoding shard count** — depends on scaling target + workload shape
- **Skipping rebalancing approach** — sharding is a forever-cost; rebalancing playbook required
