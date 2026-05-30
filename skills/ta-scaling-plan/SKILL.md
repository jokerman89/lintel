---
name: ta-scaling-plan
layer: foundation
description: TA sub-skill — capacity model + bottleneck identification + cost projection. Dispatches to CapacityPlanner (NEW) + BackendArchitect.
color: amber
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are TA-SCALING-PLAN — the workflow that produces a capacity + cost model.

## What this skill does

Reads existing performance/SLA targets + operator's scaling intent (e.g. "10x users in 12 months"). Spawns `CapacityPlanner` (new in v4.1) to produce capacity model (component-level throughput / latency / resource projections), identifies bottlenecks against current architecture, projects infrastructure cost. Output is a scaling plan document.

## When to use

- TA full pass, non_functionals_specified checkpoint
- Single action: `/li:ta single --action scaling-plan`
- Before a major customer ramp / load increase
- After a perf-regression discovery (Phase 4 TQ module surfaces; this maps it to scaling impact)

## When NOT to use

- Single-component perf tuning (use language-appropriate profiler)
- Deployment / hosting plan — use `/li:dh` (v4.4)

## Workflow

### Step 1 — Read scaling intent + current baselines

```bash
# Operator can provide intent as arg or in current cycle's state
scaling_target="${1:-${SCALING_TARGET:-3x-12-months}}"

# Read existing perf baselines if present
baseline_file=".lintel/state/perf-baseline.md"
[ -f "$baseline_file" ] || echo "WARN: no perf baseline at $baseline_file — model will be qualitative"
```

### Step 2 — Spawn CapacityPlanner for capacity model

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Produce capacity model for scaling target: $scaling_target
context_pointers:
  - $baseline_file
  - .lintel/state/ta/dependency-graph-*.md (if present)
constraints:
  - per-component throughput + latency + resource projection
  - identify top-3 bottlenecks
  - cost projection (qualitative if no cloud config; quantitative if cloud manifests present)
acceptance:
  - structured capacity model with current → target deltas
  - bottleneck identification with mitigation options
EOF

/li:brief-forge subagent_spawn ta-scaling-plan CapacityPlanner brief "$brief_file"
```

### Step 3 — Spawn BackendArchitect for mitigation refinement

```bash
mitigation_brief=$(mktemp)
cat > "$mitigation_brief" <<EOF
task: Refine bottleneck mitigations into specific architectural changes
context_pointers:
  - .lintel/state/ta/capacity-model.md
constraints:
  - per-bottleneck: 2-3 concrete mitigation options with trade-offs
  - prefer extraction + caching over rewrite
acceptance:
  - per-bottleneck mitigation menu
EOF

/li:brief-forge subagent_spawn ta-scaling-plan BackendArchitect brief "$mitigation_brief"
```

### Step 4 — Emit + audit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".lintel/state/ta/scaling-plan-$ts.md"
{
  echo "# Scaling plan — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Target"
  echo "$scaling_target"
  echo ""
  echo "## Capacity model"
  cat .lintel/state/ta/capacity-model.md
  echo ""
  echo "## Bottleneck mitigations"
  cat .lintel/state/ta/bottleneck-mitigations.md
} > "$out"

printf '{"ts":"%s","kind":"ta_scaling_plan","target":"%s","bottlenecks":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$scaling_target" "$bottleneck_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/ta-decisions.jsonl"
```

## Status protocol

- **DONE** — capacity model + mitigations emitted
- **DONE_WITH_CONCERNS** — emitted with qualitative-only projections (no baseline)
- **BLOCKED** — CapacityPlanner couldn't model (insufficient context)
- **NEEDS_CONTEXT** — operator didn't specify scaling target

## Integration

**Reads:** perf baseline, scaling target, dependency graph
**Writes:** `.lintel/state/ta/scaling-plan-<ts>.md`, audit JSONL
**Dispatches to:** CapacityPlanner (NEW agent), BackendArchitect (mitigation refinement)

## Anti-patterns

- **Hardcoding scaling target** — operator-driven
- **Quantitative projections without baseline** — surface qualitative-only and flag the gap
- **Curating mitigation patterns** — Architect proposes; this skill orchestrates (L-001)
