---
name: da-analytics-readiness
layer: foundation
description: DA sub-skill — OLAP path, dimensional model, ETL boundaries. Dispatches to DataPipelineDesigner + SchemaArchitect (NEW).
color: blue
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are DA-ANALYTICS-READINESS — the workflow that produces the analytics-side spec for the data model.

## What this skill does

Reads operational data model + business questions the analytics should answer. Spawns `DataPipelineDesigner` for the OLAP path (warehouse choice, ingestion pattern, refresh cadence) and `SchemaArchitect` for the dimensional model (fact tables, dimensions, grain choices). Produces an analytics-readiness spec covering the OLTP→OLAP boundary, ETL approach, and refresh contract.

## When to use

- DA full pass (last checkpoint area — query patterns + analytics readiness)
- Single action `/li:da single --action analytics-readiness`
- Before introducing a BI tool or warehouse
- After business asks "can we answer X with our data?"

## When NOT to use

- Pure OLTP work with no analytics intent → skip
- Operational reporting (use existing query patterns) → `/li:da single --action query-pattern-audit`

## Workflow

### Step 1 — Read context

```bash
# Reuse OLTP data model + query patterns
data_model=".claude/runtime/state/da/data-model.md"
query_audit=$(find .claude/runtime/state/da -name "query-pattern-audit-*.md" -mtime -7 2>/dev/null | sort | tail -1)

primary_store="${primary_store:-postgres}"
# Business questions can be provided as arg or in current state
business_questions="${1:-${BUSINESS_QUESTIONS:-from .claude/runtime/state/da/business-questions.md}}"
```

### Step 2 — Spawn DataPipelineDesigner for OLAP path

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Design OLAP path from ${primary_store} OLTP to analytics warehouse
context_pointers:
  - $data_model
  - $query_audit
  - business questions: ${business_questions}
constraints:
  - warehouse choice: justify (BigQuery / Snowflake / Redshift / ClickHouse / DuckDB)
  - ingestion pattern: CDC vs batch vs hybrid
  - refresh cadence per business-question latency need
  - cost-aware (warehouse + compute + storage)
acceptance:
  - warehouse + ingestion + refresh contract
  - per-business-question latency SLA
EOF

/li:brief-forge subagent_spawn da-analytics-readiness DataPipelineDesigner brief "$brief_file"
```

### Step 3 — Spawn SchemaArchitect for dimensional model

```bash
dim_brief=$(mktemp)
cat > "$dim_brief" <<EOF
task: Design dimensional model (facts + dimensions + grain)
context_pointers:
  - $data_model
  - .claude/runtime/state/da/olap-path.md
  - business questions: ${business_questions}
constraints:
  - fact table grain documented per fact (one row per X)
  - slowly-changing-dimension strategy per dimension (Type 1 / Type 2 / Type 6)
  - conformed dimensions across facts (no duplicate "Customer" with different IDs)
acceptance:
  - star schema per business area + grain + SCD strategy + conformed dim list
EOF

/li:brief-forge subagent_spawn da-analytics-readiness SchemaArchitect brief "$dim_brief"
```

### Step 4 — Emit + audit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/da/analytics-readiness-$ts.md"
{
  echo "# Analytics readiness — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## OLAP path"
  cat .claude/runtime/state/da/olap-path.md
  echo ""
  echo "## Dimensional model"
  cat .claude/runtime/state/da/dimensional-model.md
  echo ""
  echo "## Refresh contract"
  cat .claude/runtime/state/da/refresh-contract.md
} > "$out"

printf '{"ts":"%s","kind":"da_analytics_readiness","primary_store":"%s","operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$primary_store" "$(whoami 2>/dev/null || echo unknown)" \
  >> ".claude/runtime/audit/da-decisions.jsonl"
```

## Status protocol

- **DONE** — analytics path + dimensional model emitted, per-question SLA documented
- **DONE_WITH_CONCERNS** — emitted but 1-2 business questions don't have latency SLA
- **BLOCKED** — DataPipelineDesigner couldn't infer warehouse fit
- **NEEDS_CONTEXT** — business questions not provided

## Integration

**Reads:** OLTP data model, query audit, business questions
**Writes:** `.claude/runtime/state/da/analytics-readiness-<ts>.md`, audit JSONL
**Dispatches to:** DataPipelineDesigner (OLAP path), SchemaArchitect (NEW, dimensional model)

## Anti-patterns

- **Skipping the dimensional model** — facts without grain decisions accumulate ambiguity
- **Single warehouse for all questions** — sometimes per-domain stores (OLAP + search + graph) are right
- **Hardcoding refresh cadence** — depends on business question + cost
- **Curating warehouse choice patterns** — DataPipelineDesigner reasons; this skill orchestrates (L-001)
