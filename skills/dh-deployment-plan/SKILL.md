---
name: dh-deployment-plan
layer: foundation
description: DH sub-skill — deployment pattern + traffic cutover + feature-flag strategy. Dispatches to ReleaseEngineer + DeploymentEngineer (NEW) agents.
color: purple
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are DH-DEPLOYMENT-PLAN — the workflow that produces a deployment plan.

## What this skill does

Reads operator's deployment intent + active pack policy. Spawns `ReleaseEngineer` for the release-pipeline mechanics and `DeploymentEngineer` (new in v4.4) for the pattern + cutover + feature-flag strategy. Produces deployment-plan document covering pattern (blue-green/canary/rolling), traffic-cutover stages, feature-flag rollout, rollback trigger conditions.

## When to use

- DH full pass deployment_plan_locked checkpoint
- Single action `/li:dh single --action deployment-plan`
- New service first deploy
- Major version rollout

## When NOT to use

- Routine deploy (use existing pipeline)
- Single-flag toggle (toggle directly)

## Workflow

### Step 1 — Read preferences

```bash
deployment_pattern="${deployment_pattern:-blue-green}"   # blue-green | canary | rolling
cloud="${cloud:-azure}"
```

### Step 2 — Spawn ReleaseEngineer for pipeline mechanics

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Specify release-pipeline mechanics for ${deployment_pattern} on ${cloud}
context_pointers:
  - existing CI/CD configs (if present)
constraints:
  - per stage: trigger, validation gates, promotion criteria
  - artifact provenance (signed builds, SBOM attestation)
acceptance:
  - per-stage spec + promotion criteria
EOF

/li:brief-forge subagent_spawn dh-deployment-plan ReleaseEngineer brief "$brief_file"
```

### Step 3 — Spawn DeploymentEngineer for pattern + cutover

```bash
pattern_brief=$(mktemp)
cat > "$pattern_brief" <<EOF
task: Design ${deployment_pattern} cutover + feature-flag rollout
context_pointers:
  - .claude/runtime/state/dh/release-pipeline.md
constraints:
  - traffic-cutover stages: percent, duration, success criteria, abort triggers
  - feature-flag strategy: which flags, default state, rollout cadence, deprecation
  - rollback trigger conditions (auto + manual)
acceptance:
  - per-stage cutover + flag rollout + rollback triggers
EOF

/li:brief-forge subagent_spawn dh-deployment-plan DeploymentEngineer brief "$pattern_brief"
```

### Step 4 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/dh/deployment-plan-$ts.md"
{
  echo "# Deployment plan — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "## Pattern: $deployment_pattern (cloud: $cloud)"
  echo ""
  echo "## Pipeline mechanics"
  cat .claude/runtime/state/dh/release-pipeline.md
  echo ""
  echo "## Cutover + flag rollout"
  cat .claude/runtime/state/dh/cutover-strategy.md
} > "$out"

printf '{"ts":"%s","kind":"dh_deployment_plan","pattern":"%s","cloud":"%s","operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$deployment_pattern" "$cloud" "$(whoami 2>/dev/null || echo unknown)" \
  >> ".claude/runtime/audit/dh-decisions.jsonl"
```

## Status protocol

- **DONE** — plan emitted with cutover + rollback triggers
- **DONE_WITH_CONCERNS** — emitted but 1-2 trigger conditions incomplete
- **BLOCKED** — DeploymentEngineer couldn't infer cutover (insufficient context)

## Integration

**Reads:** profile preferences, existing CI/CD configs
**Writes:** `.claude/runtime/state/dh/deployment-plan-<ts>.md`, audit JSONL
**Dispatches to:** ReleaseEngineer (pipeline), DeploymentEngineer (NEW, pattern + cutover)

## Anti-patterns

- **Hardcoding deployment_pattern** — read profile
- **Cutover without abort triggers** — every stage needs explicit abort condition
- **Curating cutover patterns** — DeploymentEngineer produces (L-001)
