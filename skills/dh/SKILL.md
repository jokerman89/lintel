---
name: dh
layer: foundation
workflow_root: true
description: Use for devops and hosting depth — deployment plans, rollback strategy, observability specs, SLI/SLO budgets, capacity headroom, cost projection, and on-call playbooks. Reach for it when the work turns on how the system runs in production. Runs full, loop, or single-capability, dispatching to the ops agents and scoring against a rubric.
color: purple
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Production-bound work ships with no deployment pattern, no rollback path, no observability instrumentation, no SLI/SLO definitions, no cost projection, no on-call playbook; incidents accumulate undetected and unrecoverable."
navigation:
  primary_intent: produce ops-grade artifacts when work has production rollout, observability, or cost-ops concerns
  triggers:
    - new service / major rollout / observability gap / cost anomaly
    - operator types /li:dh {full|loop|single --action <name>}
    - BUILD phase detects deployment intent (Phase 4 wiring)
  sibling_workflows:
    - /li:ta — tech-architecture module (v4.1)
    - /li:da — data-architecture module (v4.2)
    - /li:sc — security-compliance module (v4.3)
    - /li:tq — testing-qa module (v4.5)
    - /li:full-engineering-pass — composes all 5 modules in DAG order
  risk_level: high
  auto_mode_eligible: false
  estimated_tokens: 80000
domain:
  preferences_root: engineering.devops_hosting.*
  granularities: [full, loop, single]
  checkpoints:
    - deployment_plan_locked: deployment pattern declared with rollback path and feature-flag strategy
    - observability_specified: metrics plus traces plus logs per component and dashboards defined
    - slos_defined: SLI definitions plus SLO budgets plus error budget policy
    - cost_projected: per-component cost projection within budget threshold
    - on_call_ready: per-failure-mode playbook plus escalation matrix
  recovery:
    - on_failure: revert to last-locked checkpoint, surface gap, AskUserQuestion (Re-loop | Accept-with-concern | Raise-help)
  continuation:
    - after_fix: resume at failed checkpoint, job state preserves loop position
  raise_help:
    - cost_projection_exceeds_budget_threshold: operator decides accept-cost or refine
    - slo_budget_below_30_day_minimum: operator decides re-architect or accept
    - rollback_path_irreversible: operator decides accept-toxic or refine
---

You are the DH (devops-hosting) module — Phase 4 v4.4 of Lintel.

## What this module does

Produces ops-grade artifacts when work has production rollout, observability, or cost-ops concerns. Three granularities — full pass for new services, loop iteration for ops refinement, single action for targeted ops.

| Entry | When | Outputs |
|---|---|---|
| `/li:dh full` | new service / major rollout | `deployment-plan.md` + `observability-spec.md` + `sli-slo-spec.md` + `cost-projection.md` + `rollback-strategy.md` + `on-call-playbook.md` |
| `/li:dh loop` | mid-cycle ops refinement | revised plan + diff against prior + new mitigations |
| `/li:dh <capability>` · `/li:dh single --action <capability>` | targeted operation (see Sub-capability dispatch) | one artifact per the dispatch table below |

## When to use

- New service deployment to production
- Major version rollout requiring traffic-cutover plan
- Observability gap discovered (incident root-caused to missing signal)
- Cost anomaly investigation or budget threshold approaching
- SLO definition for a service or release
- BUILD phase detected deployment intent (Phase 4 wiring auto-invokes)

## When NOT to use

- Pure code refactor with no deployment shape change
- Single SLI tuning (operator adjusts dashboard directly)
- One-off deployment (use existing release pipeline)
- Cost report generation (use cloud-vendor tools)

## Sub-capability dispatch

Per ADR-0009 the seven capabilities live here as dispatch rows — there are no per-capability
skill files. Invoke one directly as `/li:dh <capability>` (long form: `/li:dh single --action
<capability>`). Per L-001 each capability is a workflow + dispatch contract: content comes from
agents at invocation (spawned via `/li:brief-forge subagent_spawn`); each emits
`.claude/runtime/state/dh/<capability>-<ts>.md` and appends the module audit line (Step 6).

| Capability | Dispatches to (agents) | Produces | Raise-help / notes |
|---|---|---|---|
| `deployment-plan` | ReleaseEngineer + DeploymentEngineer | deployment pattern + traffic-cutover stages + feature-flag strategy + rollback triggers | pref: `deployment_pattern` (default blue-green); cutover stages with percent, duration, success criteria, abort triggers; flag rollout cadence + deprecation; artifact provenance (signed builds, SBOM attestation) |
| `observability-spec` | ObservabilityArchitect + Architect | metrics + traces + logs + dashboards + alert routing per component | pref: `stack` (default otel); signals spec below; reads TA dependency-graph <7 days old |
| `sli-slo-spec` | ObservabilityArchitect + SystemArchitect | SLI definitions + SLO budgets + error budget policy + burn-rate alerts | RAISE_HELP when any SLO budget < 99% over the window — the 30-day minimum (BLOCKED); pref: `error_budget_window` (default 30 days); burn-rate alerts at 1h/6h/24h windows; explicit budget-exhaustion policy (freeze deploys, page leadership, …); reads TA quality-attributes <30 days old |
| `cost-projection` | CostAnalyzer + CapacityPlanner | per-component monthly $ projection + anomaly-detection thresholds | RAISE_HELP when projected monthly cost > `threshold` (profile `cost_budget_monthly_usd_threshold`, default $10,000) (BLOCKED); prefs: `cloud`, `threshold`; per-SKU line items with confidence high/medium/low; bounded-by-capacity vs unbounded items; NEEDS_CONTEXT without a TA scaling plan <30 days old |
| `rollback-strategy` | ReleaseEngineer + SecurityAuditor | per-failure-mode rollback path + blast-radius + revoke paths | RAISE_HELP when any failure mode's rollback path is none/irreversible (BLOCKED); per mode: revert \| rollback \| hot-swap \| feature-flag-off + time-to-rollback + data implications (schema, in-flight transactions); revoke path per security-sensitive change; blast-radius: users, data, downtime if rollback fails; pairs with `dh-deploy-without-rollback-warn` hook (opt-in, not auto-registered — ADR-0008) |
| `capacity-headroom` | CapacityPlanner + LatencyAnalyzer | per-component headroom margins + alert thresholds + scaling triggers | vertical (per-instance) vs horizontal (instance-count) headroom; alert threshold at the utilization level BEFORE p99 degradation; scaling trigger = signal + duration; factor known peak patterns; reads TA scaling-plan <30 days + observability spec <7 days old |
| `on-call-playbook` | ReleaseEngineer + SecurityAuditor | per-failure-mode runbook + escalation matrix + security cross-reference | BLOCKED without an observability spec; per failure mode: detection signal (alert/SLI burn), first-5-minute actions, decision tree; escalation matrix severity → who pages → when to escalate; merges overlapping paths with `/li:sc incident-runbook` (security vs operational on-call) |

L-002 result: 5 of 7 capabilities dispatch to existing agents (ReleaseEngineer, CostAnalyzer, LatencyAnalyzer, CapacityPlanner, SystemArchitect, SecurityAuditor, Architect). Only 2 new agents (DeploymentEngineer, ObservabilityArchitect) for genuinely new capability.

### observability-spec — signals

- metrics: RED (rate/errors/duration) per endpoint, USE (utilization/saturation/errors) per resource
- traces: span structure, propagation header, sample rate per criticality
- logs: structured fields (timestamp/level/correlation_id/component/event), retention per environment
- per stack: native conventions (App Insights → operationId; Datadog → trace_id; OTel → traceparent)

## Workflow

### Step 1 — Parse invocation

```bash
granularity="${1:?usage: /li:dh {full|loop|<capability>|single --action <capability>}}"
capabilities="deployment-plan|observability-spec|sli-slo-spec|cost-projection|rollback-strategy|capacity-headroom|on-call-playbook"
case "$granularity" in
  full|loop) action="" ;;
  single)
    [ "$2" = "--action" ] || { echo "ERROR: --action required for single"; exit 1; }
    action="$3" ;;
  *) action="$granularity"; granularity="single" ;;   # ADR-0009 shorthand: /li:dh <capability>
esac
if [ "$granularity" = "single" ]; then
  echo "$action" | grep -qE "^(${capabilities})$" || { echo "ERROR: unknown capability '$action'"; exit 1; }
fi
```

### Step 2 — Read pack + profile preferences

```bash
source "${LINTEL_SOURCE_ROOT:-$LINTEL_REPO_ROOT}/lib/pack-resolver.sh"

# Profile preferences (engineering.devops_hosting.*)
PROFILE="$LINTEL_HOME/profile.yaml"
cloud=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'devops_hosting:' | grep 'cloud:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
cloud="${cloud:-unspecified}"
deployment_pattern=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'devops_hosting:' | grep 'deployment_pattern:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
deployment_pattern="${deployment_pattern:-blue-green}"
observability_stack=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'devops_hosting:' | grep 'observability_stack:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
observability_stack="${observability_stack:-otel}"
error_budget_window=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'devops_hosting:' | grep 'error_budget_window_days:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
error_budget_window="${error_budget_window:-30}"
cost_threshold=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'devops_hosting:' | grep 'cost_budget_monthly_usd_threshold:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
cost_threshold="${cost_threshold:-10000}"
```

### Step 3 — Dispatch by granularity

#### `full` granularity

```bash
mkdir -p .claude/runtime/state/dh
audit=".claude/runtime/audit/dh-decisions.jsonl"
mkdir -p "$(dirname "$audit")"

for checkpoint in deployment_plan_locked observability_specified slos_defined cost_projected on_call_ready; do
  echo "─── Checkpoint: $checkpoint ───"
  run_checkpoint "$checkpoint" || handle_checkpoint_failure "$checkpoint"
  audit_checkpoint "$checkpoint" "$verdict"
done

score=$(apply_scoring_rubric)
if [ "$score" -lt 80 ]; then
  echo "DH full pass score=$score (threshold 80) — surface concerns"
  exit 1
fi
```

#### `loop` granularity

```bash
if [ ! -f ".claude/runtime/state/dh/00-state.md" ]; then
  echo "ERROR: no prior DH state — use /li:dh full first"
  exit 1
fi

prior_iteration=$(grep -E '^iteration:' .claude/runtime/state/dh/00-state.md | head -1 | awk '{print $2}')
new_iteration=$((prior_iteration + 1))

run_checkpoint deployment_plan_locked
run_checkpoint observability_specified
run_checkpoint cost_projected
```

#### `single` granularity

```bash
# ADR-0009: no sub-skill files — dispatch straight off the Sub-capability dispatch table.
# Spawn the capability's agents via /li:brief-forge subagent_spawn, pass the prefs listed
# in its row (deployment-plan + rollback-strategy ← deployment_pattern; observability-spec
# ← stack; sli-slo-spec ← error_budget_window; cost-projection ← cloud + threshold),
# emit .claude/runtime/state/dh/${action}-<ts>.md, append the audit line (Step 6).
dispatch_capability "$action"   # no loop, no checkpoints
```

### Step 4 — Checkpoint failure handling (recovery + raise-help)

```bash
handle_checkpoint_failure() {
  local checkpoint="$1"
  echo "Checkpoint '$checkpoint' FAILED"

  case "$checkpoint" in
    cost_projected)
      if [ "$projected_monthly_cost" -gt "$cost_threshold" ]; then
        ask_user_question "Projected monthly cost \$$projected_monthly_cost exceeds budget \$$cost_threshold. Re-loop / Accept-cost / Raise-help (refine)?"
      fi
      ;;
    slos_defined)
      if [ "$slo_below_minimum" = "true" ]; then
        ask_user_question "SLO budget below 30-day minimum. Re-loop / Accept-with-concern / Raise-help (re-architect)?"
      fi
      ;;
    deployment_plan_locked)
      if [ "$rollback_irreversible" = "true" ]; then
        ask_user_question "Rollback path is irreversible. Re-loop / Accept-toxic / Raise-help (refine)?"
      fi
      ;;
  esac

  revert_to_last_locked
}
```

### Step 5 — 6-dimensional scoring rubric

```
| Dimension | Score 0-100 |
|---|---|
| Deployment pattern + rollback path locked | <D1> |
| Observability instrumentation coverage | <D2> |
| SLI/SLO definitions complete | <D3> |
| Cost projection per component | <D4> |
| Capacity headroom documented | <D5> |
| On-call playbook (per failure mode) | <D6> |

Pass threshold per dimension: 80.
Full-pass exit: every dimension ≥ 80 OR explicit operator override.
```

### Step 6 — Audit + emit ship report

One line via the unified writer (ts/operator/cycle_id come from the envelope):

```bash
source "${LINTEL_SOURCE_ROOT:-$(git rev-parse --show-toplevel)}/bin/_audit.sh"
audit_log dh-decisions dh_module_complete "granularity=$granularity" "score=$score" \
  "checkpoints_passed=$passed_count" "cloud=$cloud" "deployment_pattern=$deployment_pattern"
# → .claude/runtime/audit/dh-decisions.jsonl
```

## Status protocol

- **DONE** — granularity completed, score ≥ 80, cost within threshold, SLOs above minimum
- **DONE_WITH_CONCERNS** — completed but 1-2 dimensions below 80 with operator accept-with-concern
- **BLOCKED** — checkpoint failed, raise-help triggered
- **NEEDS_CONTEXT** — unknown capability for single, OR no prior state for loop

## Integration

**Reads:**
- `~/.lintel/profile.yaml` `engineering.devops_hosting.*` block
- `lib/pack-resolver.sh` for pack policy (deployment_pattern overrides, cost guardrails)
- Existing agents: ReleaseEngineer, CostAnalyzer, LatencyAnalyzer, CapacityPlanner (TA), SystemArchitect (TA), SecurityAuditor, Architect
- New agents: DeploymentEngineer, ObservabilityArchitect
- Prior TA scaling-plan + SC threat-model (if present, for cross-module input)

**Writes:**
- `.claude/runtime/state/dh/deployment-plan.md`
- `.claude/runtime/state/dh/observability-spec.md`
- `.claude/runtime/state/dh/sli-slo-spec.md`
- `.claude/runtime/state/dh/cost-projection.md`
- `.claude/runtime/state/dh/rollback-strategy.md`
- `.claude/runtime/state/dh/on-call-playbook.md`
- `.claude/runtime/audit/dh-decisions.jsonl`
- Brief Forge envelopes through the standard gate

**Triggered by:**
- Operator: `/li:dh {full|loop|single --action <name>}`
- BUILD phase: invokes as sub-module when deployment intent detected
- `/li:full-engineering-pass`: third stage in composition DAG (after TA + DA + SC)

**Hooks** (dormant by decision, ADR-0008 — ship in `hooks/shared/` but are opt-in, not auto-registered):
- `hooks/shared/dh-deploy-without-rollback-warn/` (pre-commit on deploy/IaC w/o rollback)
- `hooks/shared/dh-observability-gap-warn/` (pre-edit on new service paths w/o instrumentation)
- `hooks/shared/dh-cost-budget-warn/` (pre-commit on IaC changes exceeding cost threshold)

## Anti-patterns

- **Treating deployment as IaC-only** — pattern + cutover + flag strategy matter as much as YAML
- **Single SLO for entire service** — per-critical-journey SLO; aggregate hides hot paths
- **Cost projection without per-component breakdown** — total $ without per-component is unactionable
- **On-call playbook without detection signals** — runbook needs the trigger pattern, not just response
- **Inventing new agents when existing cover** — 5 of 7 capabilities reuse existing
- **Hardcoding deployment_pattern** — read from profile
- **Skipping rollback for "obviously safe" deploys** — every deploy has a rollback path documented
- **Blocking on hook warnings** — DH hooks warn; blocking is operator's explicit decision
