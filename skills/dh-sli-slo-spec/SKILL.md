---
name: dh-sli-slo-spec
layer: foundation
description: DH sub-skill — SLI definitions + SLO budgets + error budget policy. Dispatches to ObservabilityArchitect (NEW) + SystemArchitect.
color: purple
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are DH-SLI-SLO-SPEC — the workflow that produces SLI/SLO definitions.

## What this skill does

Reads NFR spec (from TA quality-attributes if present, else operator's targets). Spawns `ObservabilityArchitect` for SLI definitions tied to measurable signals and `SystemArchitect` for SLO budget reasoning (per critical journey, not global). Produces sli-slo-spec covering SLI per indicator + SLO budget + error budget policy + burn-rate alert thresholds.

## When to use

- DH full pass slos_defined checkpoint
- Single action `/li:dh single --action sli-slo-spec`
- Pre-release SLA negotiation
- After repeated incidents to formalize tolerance

## When NOT to use

- Operational uptime monitoring (use stack)
- Single SLO target tuning (adjust dashboard directly)

## Workflow

### Step 1 — Read NFR + window preference

```bash
error_budget_window="${error_budget_window:-30}"
nfr_spec=$(find .lintel/state/ta -name "quality-attributes-*.md" -mtime -30 2>/dev/null | sort | tail -1)
```

### Step 2 — Spawn ObservabilityArchitect for SLI definitions

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Define SLIs tied to measurable signals
context_pointers:
  - $nfr_spec
  - .lintel/state/dh/observability-spec-*.md (latest, if present)
constraints:
  - SLI per critical journey (not per service — journeys cross services)
  - measurement window per SLI
  - data source per SLI (which metric, which query)
acceptance:
  - SLI list with measurement spec
EOF

/li:brief-forge subagent_spawn dh-sli-slo-spec ObservabilityArchitect brief "$brief_file"
```

### Step 3 — Spawn SystemArchitect for SLO budgets + error budget policy

```bash
slo_brief=$(mktemp)
cat > "$slo_brief" <<EOF
task: Set SLO budgets + error budget policy
context_pointers:
  - .lintel/state/dh/sli-definitions.md
  - $nfr_spec
constraints:
  - SLO per SLI with explicit budget (e.g. 99.9% over ${error_budget_window} days)
  - error budget burn-rate alerts (1h, 6h, 24h windows)
  - policy: what happens when budget exhausted (freeze deploys, page leadership, etc.)
acceptance:
  - SLO table + burn-rate alert thresholds + budget exhaustion policy
EOF

/li:brief-forge subagent_spawn dh-sli-slo-spec SystemArchitect brief "$slo_brief"
```

### Step 4 — Raise-help on below-minimum SLO

```bash
slo_below_minimum=$(jq -r '.slos[] | select(.budget_pct < 99) | .name' .lintel/state/dh/slos.json 2>/dev/null | wc -l)
if [ "$slo_below_minimum" -gt 0 ]; then
  echo "RAISE_HELP: $slo_below_minimum SLO(s) below 30-day minimum (99%)"
fi
```

### Step 5 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".lintel/state/dh/sli-slo-spec-$ts.md"
{
  echo "# SLI/SLO spec — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "## Window: ${error_budget_window} days"
  echo ""
  echo "## SLIs"
  cat .lintel/state/dh/sli-definitions.md
  echo ""
  echo "## SLOs + error budget"
  cat .lintel/state/dh/slos-and-budget.md
} > "$out"

printf '{"ts":"%s","kind":"dh_sli_slo_spec","window_days":%d,"slos":%d,"below_minimum":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$error_budget_window" "$slo_count" "$slo_below_minimum" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/dh-decisions.jsonl"
```

## Status protocol

- **DONE** — SLI + SLO + policy emitted, all SLOs at minimum
- **DONE_WITH_CONCERNS** — 1-2 SLOs below minimum with operator accept
- **BLOCKED** — raise-help triggered (below 30-day minimum)

## Integration

**Reads:** TA NFR spec, observability spec
**Writes:** `.lintel/state/dh/sli-slo-spec-<ts>.md`, audit JSONL
**Dispatches to:** ObservabilityArchitect (NEW, SLIs), SystemArchitect (SLO budgets)

## Anti-patterns

- **Single global SLO** — per critical journey; aggregates hide hot paths
- **SLO without data source** — every SLI ties to a queryable signal
- **Budget exhaustion without policy** — what changes when burn-rate alert fires?
- **Curating SLO targets** — agents reason from NFR; this skill orchestrates (L-001)
