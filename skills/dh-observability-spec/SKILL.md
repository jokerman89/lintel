---
name: dh-observability-spec
layer: foundation
description: DH sub-skill — metrics + traces + logs + dashboards per component. Dispatches to ObservabilityArchitect (NEW) + Architect.
color: purple
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are DH-OBSERVABILITY-SPEC — the workflow that produces an observability specification.

## What this skill does

Reads component inventory (from TA dependency graph if present, else fresh enumeration) and active pack policy. Spawns `ObservabilityArchitect` (new in v4.4) for the signals spec and `Architect` for the dashboards + alert routing. Produces observability-spec covering metrics (RED + USE), traces (spans + propagation), logs (structured + retention), dashboards (per service + per journey), alert routing.

## When to use

- DH full pass observability_specified checkpoint
- Single action `/li:dh single --action observability-spec`
- Observability gap discovered (incident root-caused to missing signal)
- New service introduction

## When NOT to use

- Single-dashboard tuning (use stack tool directly)
- Log-format change only (use ad-hoc edit)

## Workflow

### Step 1 — Read context

```bash
observability_stack="${stack:-${observability_stack:-app-insights}}"   # app-insights | datadog | grafana-stack | new-relic | mixed
dep_graph=$(find .claude/runtime/state/ta -name "dependency-graph-*.md" -mtime -7 2>/dev/null | sort | tail -1)
```

### Step 2 — Spawn ObservabilityArchitect for signals

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Specify metrics + traces + logs per component for ${observability_stack}
context_pointers:
  - $dep_graph
  - existing observability config (if present)
constraints:
  - metrics: RED (rate/errors/duration) per endpoint, USE (utilization/saturation/errors) per resource
  - traces: span structure, propagation header, sample rate per criticality
  - logs: structured fields (timestamp/level/correlation_id/component/event), retention per environment
  - per stack: native conventions (App Insights → operationId; Datadog → trace_id; OTel → traceparent)
acceptance:
  - per-component: metrics list + trace spec + log spec
EOF

/li:brief-forge subagent_spawn dh-observability-spec ObservabilityArchitect brief "$brief_file"
```

### Step 3 — Spawn Architect for dashboards + alert routing

```bash
dashboard_brief=$(mktemp)
cat > "$dashboard_brief" <<EOF
task: Design dashboards + alert routing
context_pointers:
  - .claude/runtime/state/dh/signals-spec.md
constraints:
  - one dashboard per service + one per critical journey
  - alert routing per severity (page vs ticket vs surface)
  - dashboard widgets ranked by operator-relevance during incident response
acceptance:
  - dashboard catalog + alert routing matrix
EOF

/li:brief-forge subagent_spawn dh-observability-spec Architect brief "$dashboard_brief"
```

### Step 4 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/dh/observability-spec-$ts.md"
{
  echo "# Observability spec — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "## Stack: $observability_stack"
  echo ""
  echo "## Signals"
  cat .claude/runtime/state/dh/signals-spec.md
  echo ""
  echo "## Dashboards + alert routing"
  cat .claude/runtime/state/dh/dashboards-alerts.md
} > "$out"

printf '{"ts":"%s","kind":"dh_observability_spec","stack":"%s","components":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$observability_stack" "$component_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> ".claude/runtime/audit/dh-decisions.jsonl"
```

## Status protocol

- **DONE** — spec emitted covering every component with dashboards + alert routing
- **DONE_WITH_CONCERNS** — emitted but 1-2 components lack trace propagation
- **BLOCKED** — ObservabilityArchitect couldn't infer signal map

## Integration

**Reads:** dependency graph (from TA), existing observability config
**Writes:** `.claude/runtime/state/dh/observability-spec-<ts>.md`, audit JSONL
**Dispatches to:** ObservabilityArchitect (NEW, signals), Architect (dashboards + routing)

## Anti-patterns

- **Logs without correlation_id** — incidents become impossible to thread through
- **Single dashboard for everything** — per-service + per-journey
- **Alert without routing severity** — pages vs tickets matter for on-call
- **Hardcoding stack** — read profile
