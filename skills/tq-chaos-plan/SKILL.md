---
name: tq-chaos-plan
layer: foundation
description: TQ sub-skill — failure injection scenarios + dependency-chaos + recovery validation. Dispatches to SecurityAuditor + SystemArchitect agents.
color: green
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are TQ-CHAOS-PLAN — the workflow that produces a chaos engineering plan.

## What this skill does

Reads threat model (from SC if present) + dependency graph (from TA if present) + on-call playbook (from DH if present). Spawns `SecurityAuditor` to identify failure injection scenarios mapped to threats and `SystemArchitect` to design dependency-chaos paths + recovery validation. Produces chaos-plan covering scenarios, blast-radius, success criteria, schedule, abort conditions.

## When to use

- TQ full pass chaos_scenarios_documented checkpoint
- Single action `/li:tq single --action chaos-plan`
- Pre-customer-engagement resilience validation
- After incident: validate the fix actually fixes it

## When NOT to use

- Production stability period (don't chaos during fragile time)
- Single-component failure test (use ad-hoc fault injection)

## Workflow

### Step 1 — Read context

```bash
chaos_active="${active:-${chaos_active:-true}}"
threat_model=$(find .claude/runtime/state/sc -name "threat-model-*.md" -mtime -30 2>/dev/null | sort | tail -1)
dep_graph=$(find .claude/runtime/state/ta -name "dependency-graph-*.md" -mtime -30 2>/dev/null | sort | tail -1)
on_call_playbook=$(find .claude/runtime/state/dh -name "on-call-playbook-*.md" -mtime -30 2>/dev/null | sort | tail -1)

if [ "$chaos_active" != "true" ]; then
  echo "chaos_active=false; chaos plan not required by profile"
  echo "DONE_WITH_CONCERNS: chaos plan stub-only because chaos_active=false"
  exit 0
fi
```

### Step 2 — Spawn SecurityAuditor for failure-injection scenarios

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Identify failure injection scenarios mapped to threats
context_pointers:
  - $threat_model
  - $on_call_playbook
constraints:
  - per scenario: what fails, blast-radius (users / data / dependencies), expected behavior, abort condition
  - prefer scenarios that validate specific on-call playbook entries
acceptance:
  - per-scenario spec
EOF

/li:brief-forge subagent_spawn tq-chaos-plan SecurityAuditor brief "$brief_file"
```

### Step 3 — Spawn SystemArchitect for dependency-chaos + recovery validation

```bash
dep_brief=$(mktemp)
cat > "$dep_brief" <<EOF
task: Design dependency-chaos paths + recovery validation
context_pointers:
  - $dep_graph
  - .claude/runtime/state/tq/chaos-scenarios.md
constraints:
  - per dependency: kill / latency-spike / partial-failure
  - per scenario: recovery success criteria (RTO + RPO + auto-recovery vs manual)
  - schedule (game-day cadence) + abort conditions
acceptance:
  - dependency-chaos matrix + recovery validation criteria
EOF

/li:brief-forge subagent_spawn tq-chaos-plan SystemArchitect brief "$dep_brief"
```

### Step 4 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/tq/chaos-plan-$ts.md"
{
  echo "# Chaos plan — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Scenarios"
  cat .claude/runtime/state/tq/chaos-scenarios.md
  echo ""
  echo "## Dependency-chaos + recovery validation"
  cat .claude/runtime/state/tq/dependency-chaos.md
} > "$out"

printf '{"ts":"%s","kind":"tq_chaos_plan","scenarios":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$scenario_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/tq-decisions.jsonl"
```

## Status protocol

- **DONE** — plan emitted with scenarios + recovery criteria
- **DONE_WITH_CONCERNS** — chaos_active=false (stub-only plan), OR 1-2 scenarios lack abort conditions
- **BLOCKED** — neither threat model nor on-call playbook present (run /li:sc + /li:dh first)

## Integration

**Reads:** SC threat-model, TA dependency-graph, DH on-call-playbook
**Writes:** `.claude/runtime/state/tq/chaos-plan-<ts>.md`, audit JSONL
**Dispatches to:** SecurityAuditor (scenarios), SystemArchitect (dep-chaos + recovery)

## Anti-patterns

- **Chaos without abort conditions** — production chaos with no stop signal is a self-inflicted outage
- **Scenarios without recovery validation** — chaos validates resilience; success criteria are required
- **Same scenario for all dependencies** — kill vs latency-spike vs partial-failure all matter
- **Curating scenarios** — agents reason from threat + dep + playbook (L-001)
