---
name: dh-cost-projection
layer: foundation
description: DH sub-skill — per-component cost projection + anomaly detection thresholds. Dispatches to CostAnalyzer + CapacityPlanner. Raises help on budget threshold breach.
color: purple
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are DH-COST-PROJECTION — the workflow that produces a per-component cost projection.

## What this skill does

Reads capacity model (from TA scaling-plan if present, else fresh estimate) + active pack cloud preference. Spawns `CostAnalyzer` for the projection per cloud line-item and `CapacityPlanner` to map workload growth to cost growth. Produces cost-projection with monthly $ per component + total + anomaly detection thresholds. Raises help when projection exceeds budget threshold.

## When to use

- DH full pass cost_projected checkpoint
- Single action `/li:dh single --action cost-projection`
- Pre-release budget conversation
- After cost anomaly investigation

## When NOT to use

- Single-instance pricing lookup (use cloud calculator)
- Historical cost retrospective (use cloud billing portal)

## Workflow

### Step 1 — Read preferences + scaling context

```bash
cloud="${cloud:-unspecified}"
threshold="${threshold:-${cost_budget_monthly_usd_threshold:-10000}}"
scaling_plan=$(find .claude/runtime/state/ta -name "scaling-plan-*.md" -mtime -30 2>/dev/null | sort | tail -1)
```

### Step 2 — Spawn CostAnalyzer for projection

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Project monthly cost per component on ${cloud}
context_pointers:
  - $scaling_plan
  - existing cloud manifests / IaC (if present)
constraints:
  - per component: compute + storage + egress + ancillary services
  - line-item granularity (per cloud SKU)
  - estimate confidence per line (high/medium/low)
acceptance:
  - per-component cost table + total + confidence distribution
EOF

/li:brief-forge subagent_spawn dh-cost-projection CostAnalyzer brief "$brief_file"
```

### Step 3 — Spawn CapacityPlanner for workload-to-cost mapping

```bash
mapping_brief=$(mktemp)
cat > "$mapping_brief" <<EOF
task: Map workload growth to cost growth
context_pointers:
  - .claude/runtime/state/dh/cost-line-items.md
  - $scaling_plan
constraints:
  - per workload signal (users, requests, data volume): which line items scale
  - identify which line items are bounded by capacity vs. unbounded
  - anomaly detection thresholds (deviation from baseline that signals a problem)
acceptance:
  - workload→cost mapping + anomaly thresholds per component
EOF

/li:brief-forge subagent_spawn dh-cost-projection CapacityPlanner brief "$mapping_brief"
```

### Step 4 — Threshold check + raise-help

```bash
projected_monthly_cost=$(jq -r '.total_monthly_usd // 0' .claude/runtime/state/dh/cost-projection.json 2>/dev/null)
projected_monthly_cost=${projected_monthly_cost%.*}

if [ "${projected_monthly_cost:-0}" -gt "$threshold" ]; then
  echo "RAISE_HELP: projected monthly cost \$${projected_monthly_cost} exceeds threshold \$${threshold}"
fi
```

### Step 5 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/dh/cost-projection-$ts.md"
{
  echo "# Cost projection — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "## Cloud: $cloud"
  echo "## Threshold: \$${threshold}/month"
  echo "## Projected: \$${projected_monthly_cost:-unknown}/month"
  echo ""
  echo "## Per-component"
  cat .claude/runtime/state/dh/cost-line-items.md
  echo ""
  echo "## Anomaly thresholds"
  cat .claude/runtime/state/dh/anomaly-thresholds.md
} > "$out"

printf '{"ts":"%s","kind":"dh_cost_projection","cloud":"%s","projected_usd":%d,"threshold_usd":%d,"raise_help":%s,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$cloud" "${projected_monthly_cost:-0}" "$threshold" \
  "$([ "${projected_monthly_cost:-0}" -gt "$threshold" ] && echo true || echo false)" \
  "$(whoami 2>/dev/null || echo unknown)" \
  >> ".claude/runtime/audit/dh-decisions.jsonl"
```

## Status protocol

- **DONE** — projection emitted within threshold
- **DONE_WITH_CONCERNS** — projection emitted with 1-2 low-confidence line items
- **BLOCKED** — raise-help triggered (exceeds threshold)
- **NEEDS_CONTEXT** — no scaling context (run /li:ta-scaling-plan first or provide explicit scaling)

## Integration

**Reads:** TA scaling plan, cloud manifests, pack policy
**Writes:** `.claude/runtime/state/dh/cost-projection-<ts>.md`, audit JSONL
**Dispatches to:** CostAnalyzer (line items), CapacityPlanner (workload mapping)

## Anti-patterns

- **Total cost without per-component breakdown** — unactionable
- **Single confidence number** — per-line confidence is the operator's lever
- **Hardcoding threshold** — read from profile
- **Anomaly detection without thresholds** — alert without trigger condition is noise
