---
name: ta-quality-attributes
layer: foundation
description: TA sub-skill — non-functional requirement spec (latency, throughput, reliability, observability). Dispatches to SystemArchitect (NEW) + Architect.
color: amber
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are TA-QUALITY-ATTRIBUTES — the workflow that produces a non-functional requirement spec.

## What this skill does

Reads operator's functional requirements + existing performance/reliability targets. Spawns `SystemArchitect` (new in v4.1) to produce structured NFR spec: latency budgets (p50/p95/p99), throughput targets, error rate budgets, availability targets, observability minimums. Spawns `Architect` to map NFRs to architectural constraints. Writes spec to `.claude/runtime/state/ta/quality-attributes-<ts>.md`.

## When to use

- TA full pass, non_functionals_specified checkpoint (mandatory for full pass exit)
- Single action: `/li:ta single --action quality-attributes`
- Before customer engagement requires SLA negotiation
- After perf-regression discovery to formalize targets going forward

## When NOT to use

- Pure SLA monitoring (use `/li:dh` v4.4 + observability stack)
- Coverage targets — use `/li:tq` v4.5

## Workflow

### Step 1 — Read existing targets if present

```bash
existing_sla=".claude/runtime/state/sla-targets.md"
existing_baseline=".claude/runtime/state/perf-baseline.md"

[ -f "$existing_sla" ] && has_sla=1 || has_sla=0
[ -f "$existing_baseline" ] && has_baseline=1 || has_baseline=0
```

### Step 2 — Spawn SystemArchitect for NFR spec

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Produce non-functional requirement spec for [operator's system description]
context_pointers:
  - $existing_sla (if present)
  - $existing_baseline (if present)
constraints:
  - latency: p50, p95, p99 per critical user journey
  - throughput: target RPS per endpoint
  - error rate: % budget per endpoint
  - availability: yearly SLA (e.g. 99.9%)
  - observability: required signals per component (metrics, traces, logs)
acceptance:
  - structured NFR document covering all 5 dimensions
EOF

/li:brief-forge subagent_spawn ta-quality-attributes SystemArchitect brief "$brief_file"
```

### Step 3 — Spawn Architect for architectural constraints

```bash
constraints_brief=$(mktemp)
cat > "$constraints_brief" <<EOF
task: Map NFR spec to architectural constraints + verification approach
context_pointers:
  - .claude/runtime/state/ta/nfr-spec.md
constraints:
  - per NFR: which architectural decision enables / threatens it
  - per NFR: how it'll be verified (load test / chaos test / monitoring assertion)
acceptance:
  - per-NFR constraints + verification approach
EOF

/li:brief-forge subagent_spawn ta-quality-attributes Architect brief "$constraints_brief"
```

### Step 4 — Emit + audit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/ta/quality-attributes-$ts.md"
{
  echo "# Quality attributes — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## NFR spec"
  cat .claude/runtime/state/ta/nfr-spec.md
  echo ""
  echo "## Architectural constraints + verification"
  cat .claude/runtime/state/ta/architect-constraints.md
} > "$out"

printf '{"ts":"%s","kind":"ta_quality_attributes","nfr_count":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$nfr_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/ta-decisions.jsonl"
```

## Status protocol

- **DONE** — NFR spec emitted, all 5 dimensions covered, verification approach per NFR
- **DONE_WITH_CONCERNS** — emitted but 1-2 dimensions not specified (gap surfaced)
- **BLOCKED** — SystemArchitect couldn't infer NFRs (insufficient context)
- **NEEDS_CONTEXT** — operator didn't specify system description

## Integration

**Reads:** existing SLA + baseline files, operator's system description
**Writes:** `.claude/runtime/state/ta/quality-attributes-<ts>.md`, audit JSONL
**Dispatches to:** SystemArchitect (NEW agent, NFR spec), Architect (constraints + verification)

## Anti-patterns

- **Skipping verification approach** — every NFR has a verification path; "how would we know?" is mandatory
- **Hardcoding SLA numbers** — operator-driven via brief
- **Curating NFR templates** — SystemArchitect produces; this skill orchestrates (L-001)
