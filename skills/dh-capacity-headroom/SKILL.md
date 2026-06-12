---
name: dh-capacity-headroom
layer: foundation
description: DH sub-skill — headroom margins + alert thresholds + scaling triggers. Dispatches to CapacityPlanner + LatencyAnalyzer.
color: purple
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are DH-CAPACITY-HEADROOM — the workflow that produces capacity headroom guidance.

## What this skill does

Reads capacity model (from TA scaling-plan if present) + observability spec (from `dh-observability-spec` if present). Spawns `CapacityPlanner` to compute headroom margins per component and `LatencyAnalyzer` to map latency degradation to capacity threshold. Produces capacity-headroom with margin per component + alert thresholds + scaling-trigger conditions.

## When to use

- DH full pass (between cost_projected and on_call_ready, informs both)
- Single action `/li:dh single --action capacity-headroom`
- Post-incident review wanting threshold refinement
- Pre-customer ramp planning

## When NOT to use

- Single autoscaling rule tuning (use cloud tools)
- Runtime capacity emergency (use ops, not this scaffold)

## Workflow

### Step 1 — Read context

```bash
scaling_plan=$(find .claude/runtime/state/ta -name "scaling-plan-*.md" -mtime -30 2>/dev/null | sort | tail -1)
observability_spec=$(find .claude/runtime/state/dh -name "observability-spec-*.md" -mtime -7 2>/dev/null | sort | tail -1)
```

### Step 2 — Spawn CapacityPlanner for headroom margins

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Compute headroom margins per component
context_pointers:
  - $scaling_plan
  - $observability_spec
constraints:
  - per component: current utilization, target utilization, headroom margin
  - distinguish: vertical headroom (resource per instance) vs horizontal headroom (instance count)
  - factor in known peak patterns (weekly cycle, marketing events)
acceptance:
  - per-component headroom margins with reasoning
EOF

/li:brief-forge subagent_spawn dh-capacity-headroom CapacityPlanner brief "$brief_file"
```

### Step 3 — Spawn LatencyAnalyzer for degradation thresholds

```bash
latency_brief=$(mktemp)
cat > "$latency_brief" <<EOF
task: Map capacity utilization to latency degradation thresholds
context_pointers:
  - .claude/runtime/state/dh/headroom-margins.md
constraints:
  - per component: utilization level at which p99 latency begins to degrade
  - alert threshold: utilization level that triggers scaling action (typically before degradation)
  - scaling-trigger condition: which signal + duration
acceptance:
  - per-component degradation curve + alert + scaling trigger
EOF

/li:brief-forge subagent_spawn dh-capacity-headroom LatencyAnalyzer brief "$latency_brief"
```

### Step 4 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/dh/capacity-headroom-$ts.md"
{
  echo "# Capacity headroom — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-component headroom"
  cat .claude/runtime/state/dh/headroom-margins.md
  echo ""
  echo "## Alert + scaling triggers"
  cat .claude/runtime/state/dh/scaling-triggers.md
} > "$out"

printf '{"ts":"%s","kind":"dh_capacity_headroom","components":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$component_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> ".claude/runtime/audit/dh-decisions.jsonl"
```

## Status protocol

- **DONE** — headroom + triggers emitted per component
- **DONE_WITH_CONCERNS** — emitted but 1-2 components lack peak-pattern data

## Integration

**Reads:** TA scaling plan, DH observability spec
**Writes:** `.claude/runtime/state/dh/capacity-headroom-<ts>.md`, audit JSONL
**Dispatches to:** CapacityPlanner (margins), LatencyAnalyzer (degradation thresholds)

## Anti-patterns

- **Headroom without peak-pattern factoring** — week-day-only margin breaks on Black Friday
- **Alert threshold = scaling threshold** — alert should fire BEFORE scaling, not at scaling
- **Single headroom number** — vertical vs horizontal matter differently per component
