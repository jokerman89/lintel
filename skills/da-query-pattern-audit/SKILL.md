---
name: da-query-pattern-audit
layer: foundation
description: DA sub-skill — read/write ratios, hot paths, missing indexes. Dispatches to DatabaseDesigner + Explorer.
color: blue
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are DA-QUERY-PATTERN-AUDIT — the workflow that surfaces access patterns + index gaps.

## What this skill does

Scans application code for queries (ORM calls + raw SQL). Aggregates by table + operation type (read/write/aggregate). Spawns `Explorer` for the enumeration + `DatabaseDesigner` for index-gap analysis against the schema. Produces a query-pattern report with hot-path identification + recommended index additions.

## When to use

- DA full pass query_patterns_documented checkpoint
- Single action `/li:da single --action query-pattern-audit`
- After perf regression discovery (correlate with hot paths)
- Pre-migration to confirm migration doesn't break a hot query

## When NOT to use

- Runtime query profiling (use observability stack — `/li:dh` v4.4)
- Single-query EXPLAIN-tuning (use database tool directly)

## Workflow

### Step 1 — Enumerate queries via Explorer

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Enumerate all queries (ORM calls + raw SQL) against declared schema
context_pointers:
  - .claude/runtime/state/da/data-model.md (if present)
constraints:
  - one entry per (table, operation, frequency-hint)
  - capture filter columns + join columns
  - flag queries inside loops as potential N+1
acceptance:
  - structured list: table → [{op, frequency, filters, joins, n_plus_1}]
EOF

/li:brief-forge subagent_spawn da-query-pattern-audit Explorer brief "$brief_file"
```

### Step 2 — Spawn DatabaseDesigner for index-gap analysis

```bash
index_brief=$(mktemp)
cat > "$index_brief" <<EOF
task: Identify index gaps against documented queries
context_pointers:
  - .claude/runtime/state/da/query-enumeration.json
  - .claude/runtime/state/da/current-schema.sql (if present)
constraints:
  - per query: existing index sufficient | needs new index | composite index needed
  - flag missing-index candidates by query frequency
acceptance:
  - per-query index verdict + new-index recommendations ranked by impact
EOF

/li:brief-forge subagent_spawn da-query-pattern-audit DatabaseDesigner brief "$index_brief"
```

### Step 3 — Compute hot paths + read/write ratios

```bash
# Hot paths = top-5 by frequency
hot_paths=$(jq -r '.queries | sort_by(.frequency_hint) | reverse | .[0:5]' .claude/runtime/state/da/query-enumeration.json)

# Read/write ratio per table
read_write_ratios=$(compute_rw_ratios .claude/runtime/state/da/query-enumeration.json)
```

### Step 4 — Emit + audit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/da/query-pattern-audit-$ts.md"
{
  echo "# Query pattern audit — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Hot paths (top-5 by frequency)"
  echo "$hot_paths"
  echo ""
  echo "## Read/write ratios per table"
  echo "$read_write_ratios"
  echo ""
  echo "## Index gaps"
  cat .claude/runtime/state/da/index-gaps.md
  echo ""
  echo "## N+1 candidates"
  jq -r '.queries[] | select(.n_plus_1 == true) | "- \(.table) (\(.op)): \(.location)"' .claude/runtime/state/da/query-enumeration.json
} > "$out"

printf '{"ts":"%s","kind":"da_query_pattern_audit","queries":%d,"hot_paths":%d,"index_gaps":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$query_count" "$hot_path_count" "$index_gap_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> ".claude/runtime/audit/da-decisions.jsonl"
```

## Status protocol

- **DONE** — audit emitted, 0 critical index gaps
- **DONE_WITH_CONCERNS** — index gaps surfaced (operator decides add or accept)
- **BLOCKED** — Explorer couldn't enumerate (unfamiliar ORM)

## Integration

**Reads:** application code, current schema, data model
**Writes:** `.claude/runtime/state/da/query-pattern-audit-<ts>.md`, audit JSONL
**Dispatches to:** Explorer (enumeration), DatabaseDesigner (index-gap analysis)

## Anti-patterns

- **Hardcoding ORM patterns** — Explorer reads codebase; ORM-agnostic
- **Ranking only by query count** — frequency-hint accounts for "called once per page load" vs "called per item"
- **Skipping N+1 flagging** — common perf footgun; surface even if no index gap
