---
name: tq-perf-budget-spec
layer: foundation
description: TQ sub-skill — per-journey perf budget + regression detection thresholds. Dispatches to LatencyAnalyzer + PerfBudgetEnforcer (NEW).
color: green
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are TQ-PERF-BUDGET-SPEC — the workflow that produces a per-journey perf budget.

## What this skill does

Reads SLI/SLO spec (from DH if present, else operator's perf targets) + existing perf baseline. Spawns `LatencyAnalyzer` to identify perf-sensitive paths and `PerfBudgetEnforcer` (new in v4.5) to set per-journey budgets with regression detection thresholds (how much drift triggers alarm). Produces perf-budget with per-journey p50/p95/p99 budget + regression alert thresholds + enforcement mechanism.

## When to use

- TQ full pass perf_budgets_locked checkpoint
- Single action `/li:tq single --action perf-budget-spec`
- Pre-release perf gate
- Post-perf-regression incident: formalize budget

## When NOT to use

- Single-endpoint perf tuning (use profiler)
- Runtime perf monitoring (use APM/observability — `/li:dh-observability-spec`)

## Workflow

### Step 1 — Read context

```bash
perf_budget_p95="${p95:-${perf_budget_p95_ms:-200}}"
slo_spec=$(find .lintel/state/dh -name "sli-slo-spec-*.md" -mtime -30 2>/dev/null | sort | tail -1)
perf_baseline=".lintel/state/perf-baseline.md"
```

### Step 2 — Spawn LatencyAnalyzer for sensitive-path identification

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Identify perf-sensitive paths from current baseline
context_pointers:
  - $perf_baseline (if present)
  - $slo_spec (for criticality)
constraints:
  - per critical journey: current p50/p95/p99
  - identify paths with thin margin vs current SLO
acceptance:
  - per-journey baseline + margin assessment
EOF

/li:brief-forge subagent_spawn tq-perf-budget-spec LatencyAnalyzer brief "$brief_file"
```

### Step 3 — Spawn PerfBudgetEnforcer for budget + regression detection

```bash
budget_brief=$(mktemp)
cat > "$budget_brief" <<EOF
task: Set per-journey perf budget with regression detection
context_pointers:
  - .lintel/state/tq/sensitive-paths.md
  - default p95 budget: ${perf_budget_p95}ms
constraints:
  - per journey: p50/p95/p99 budget (must be tighter than SLO to allow burndown)
  - regression detection: % drift that triggers alarm, sample-window size, alarm fan-out
  - enforcement: CI gate (block PR), warn-only (surface), or off
acceptance:
  - per-journey budget + regression alert + enforcement mode
EOF

/li:brief-forge subagent_spawn tq-perf-budget-spec PerfBudgetEnforcer brief "$budget_brief"
```

### Step 4 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".lintel/state/tq/perf-budget-$ts.md"
{
  echo "# Perf budget — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "## Default p95: ${perf_budget_p95}ms"
  echo ""
  echo "## Sensitive paths"
  cat .lintel/state/tq/sensitive-paths.md
  echo ""
  echo "## Per-journey budget + regression detection"
  cat .lintel/state/tq/perf-budgets.md
} > "$out"

printf '{"ts":"%s","kind":"tq_perf_budget_spec","default_p95_ms":%d,"journeys":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$perf_budget_p95" "$journey_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/tq-decisions.jsonl"
```

## Status protocol

- **DONE** — budget + regression detection per journey
- **DONE_WITH_CONCERNS** — emitted but 1-2 journeys have thin SLO margin
- **BLOCKED** — LatencyAnalyzer couldn't infer baseline

## Integration

**Reads:** DH SLI/SLO spec, perf baseline, profile preferences
**Writes:** `.lintel/state/tq/perf-budget-<ts>.md`, audit JSONL
**Dispatches to:** LatencyAnalyzer (baseline), PerfBudgetEnforcer (NEW, budget + detection)
**Hook integration:** `tq-perf-regression-warn` hook fires pre-commit on changes affecting perf-budget paths

## Anti-patterns

- **Budget equal to SLO** — needs margin so burndown doesn't cross the line
- **Regression detection without sample window** — single-sample alarms are noise
- **Budget without enforcement mode** — declared budget without enforcement = aspirational
- **Curating budget numbers** — agents reason from baseline (L-001)
