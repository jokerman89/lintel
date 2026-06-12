# DH module — devops-hosting for engineering depth

**Last updated:** 2026-06-02 (v4.4)
**Status:** Concept doc — referenced by `skills/dh/SKILL.md` + 7 Capabilities + 2 new agents + 3 hooks

> When work has deployment/runtime concerns — new service, major rollout, observability gap, cost anomaly, SLO definition — running it through plain BUILD discards what the operator needs: deployment pattern + rollback, observability instrumentation, SLI/SLO with error budget, per-component cost projection, on-call playbook. DH is the **fourth engineering-domain module in v4.x**, following the same pattern as TA + DA + SC documented in [engineering-modules.md](engineering-modules.md).

## The problem

Pre-v4.4, ops-bound work happened through ad-hoc:
- Deploy pipelines copied + tweaked between services
- Observability added retrospectively after incidents
- SLOs negotiated in customer calls without measurement basis
- Cost projection invented at budget-review time
- On-call playbook written post-incident

The user explicitly named the gap: "When the work has deployment / runtime concerns ... invoke DH to produce ops-grade artifacts."

The module fixes it with three granularities — `full`, `loop`, `single` — and 5 checkpoints with recovery.

## The model

```
Operator invocation
       │
       ▼
/li:dh {full|loop|single --action <name>}
       │
       │  Read pack policy + profile.engineering.devops_hosting.*
       ▼
Granularity dispatch:
       │
       ├── full   → deployment_plan_locked → observability_specified
       │           → slos_defined → cost_projected → on_call_ready
       │           → 6-dim scoring rubric → SHIP (score ≥80) or surface
       │
       ├── loop   → re-run deployment_plan + observability + cost → diff vs prior
       │
       └── single → direct Capability (no checkpoints, no orchestration)
                   deployment-plan / observability-spec / sli-slo-spec /
                   cost-projection / rollback-strategy /
                   capacity-headroom / on-call-playbook
                       │
                       ▼
                   Spawn agent via Brief Forge:
                   ReleaseEngineer / DeploymentEngineer (NEW) /
                   ObservabilityArchitect (NEW) / CostAnalyzer / CapacityPlanner /
                   LatencyAnalyzer / SystemArchitect / SecurityAuditor / Architect
                       │
                       ▼
                   Output → .claude/runtime/state/dh/<action>-<ts>.md
                   Audit → .claude/runtime/audit/dh-decisions.jsonl
```

## The five checkpoints (full pass)

### 1. `deployment_plan_locked`
Pattern declared + rollback documented + feature-flag strategy. Produced by `deployment-plan` + ReleaseEngineer + DeploymentEngineer.
Pass criterion: pattern (blue-green/canary/rolling) chosen + cutover stages + flag rollout + rollback triggers. Raise-help on irreversible rollback.

### 2. `observability_specified`
Metrics + traces + logs per component + dashboards defined. Produced by `observability-spec` + ObservabilityArchitect + Architect.
Pass criterion: RED metrics per endpoint + USE per resource; trace propagation; structured logs with correlation_id; dashboards per service + per critical journey.

### 3. `slos_defined`
SLI definitions + SLO budgets + error budget policy. Produced by `sli-slo-spec` + ObservabilityArchitect + SystemArchitect.
Pass criterion: SLI per critical journey with measurable signal; SLO with explicit budget; burn-rate alerts; budget-exhaustion policy. Raise-help on SLO below 30-day minimum.

### 4. `cost_projected`
Per-component projection within budget threshold. Produced by `cost-projection` + CostAnalyzer + CapacityPlanner.
Pass criterion: per-component monthly $ + anomaly detection thresholds. Raise-help on threshold breach.

### 5. `on_call_ready`
Per-failure-mode playbook + escalation matrix. Produced by `on-call-playbook` + ReleaseEngineer + SecurityAuditor.
Pass criterion: detection signal per failure mode + first-5-minute actions + escalation matrix. Cross-reference with SC incident runbook if present.

## The 6-dimensional scoring rubric (full pass exit gate)

| Dimension | Score 0-100 | Pass threshold | Source artifact |
|---|---|---|---|
| Deployment pattern + rollback path locked | _ | 80 | `.claude/runtime/state/dh/deployment-plan-<ts>.md` + `rollback-strategy-<ts>.md` |
| Observability instrumentation coverage | _ | 80 | `.claude/runtime/state/dh/observability-spec-<ts>.md` |
| SLI/SLO definitions complete | _ | 80 | `.claude/runtime/state/dh/sli-slo-spec-<ts>.md` |
| Cost projection per component | _ | 80 | `.claude/runtime/state/dh/cost-projection-<ts>.md` |
| Capacity headroom documented | _ | 80 | `.claude/runtime/state/dh/capacity-headroom-<ts>.md` |
| On-call playbook (per failure mode) | _ | 80 | `.claude/runtime/state/dh/on-call-playbook-<ts>.md` |

## Capability catalog

| Capability | Primary agent | Other agents | Output |
|---|---|---|---|
| `deployment-plan` | ReleaseEngineer | DeploymentEngineer (NEW) | deployment pattern + cutover + flags |
| `observability-spec` | ObservabilityArchitect (NEW) | Architect | signals + dashboards + alert routing |
| `sli-slo-spec` | ObservabilityArchitect (NEW) | SystemArchitect | SLI + SLO + error budget policy |
| `cost-projection` | CostAnalyzer | CapacityPlanner | per-component projection + thresholds |
| `rollback-strategy` | ReleaseEngineer | SecurityAuditor | rollback mechanics + blast-radius |
| `capacity-headroom` | CapacityPlanner | LatencyAnalyzer | headroom + alert + scaling triggers |
| `on-call-playbook` | ReleaseEngineer | SecurityAuditor | per-failure-mode runbook + escalation |

**L-002 result:** 5 of 7 Capabilities dispatch to existing agents (ReleaseEngineer, CostAnalyzer, LatencyAnalyzer, CapacityPlanner, SystemArchitect, SecurityAuditor, Architect). Only 2 new agents (DeploymentEngineer, ObservabilityArchitect) for genuinely new capability.

## Agent additions (v4.4)

### `DeploymentEngineer`
- **Purpose:** deployment pattern reasoning, traffic-cutover stages, feature-flag rollout
- **Why new:** ReleaseEngineer handles pipeline mechanics (what runs); DeploymentEngineer handles cutover strategy (how the change reaches users)
- **Spawned by:** `deployment-plan`

### `ObservabilityArchitect`
- **Purpose:** signals design (metrics/traces/logs), SLI definitions tied to measurable queries
- **Why new:** existing agents (LatencyAnalyzer) focus on perf analysis; ObservabilityArchitect specifies what the system tells operators
- **Spawned by:** `observability-spec`, `sli-slo-spec`

## Hook additions (v4.4)

All three are warn-only. Each uses unified `audit_log` from `bin/_audit.sh`.

### `dh-deploy-without-rollback-warn`
Pre-commit on deploy/IaC files lacking rollback declaration in same commit or recent `rollback-strategy-*.md`.

### `dh-observability-gap-warn`
Pre-edit on service entry-point files lacking metric/trace/log markers.

### `dh-cost-budget-warn`
Pre-commit on IaC with cost-increasing patterns (SKU upsizing, replica increases, premium storage, always-on resources).

## Profile preferences

Under `engineering.devops_hosting.*` in `~/.lintel/profile.yaml`:

```yaml
engineering:
  devops_hosting:
    cloud: azure                           # azure | aws | gcp | oci | on-prem
    deployment_pattern: blue-green         # blue-green | canary | rolling
    observability_stack: app-insights      # app-insights | datadog | grafana-stack | new-relic | mixed
    error_budget_window_days: 30
    cost_budget_monthly_usd_threshold: 10000
```

Hooks + Capabilities read these. Defaults baked in when absent.

## Pack overrides

```yaml
# packs/some-pack/pack.yaml
devops_hosting:
  deploy_path_glob: "infra/**/*.tf,helm/**/*.yaml"
  service_entry_glob: "src/api/**/*,src/handlers/**/*"
  iac_glob: "infra/**/*,terraform/**/*"
```

## Audit trail

```jsonl
{"ts":"...","kind":"dh_module_complete","granularity":"full","score":86,"cloud":"azure","deployment_pattern":"blue-green"}
{"ts":"...","kind":"dh_deployment_plan","pattern":"canary","cloud":"azure"}
{"ts":"...","kind":"dh_cost_projection","cloud":"azure","projected_usd":8500,"threshold_usd":10000,"raise_help":false}
{"ts":"...","kind":"dh_sli_slo_spec","window_days":30,"slos":12,"below_minimum":1}
```

## Composition — DH as third stage in full engineering pass

Per engineering-modules.md §"Composition":

```
TA
  │
  ├── DA  ┐
  ├── SC  ┘
  │
  ▼
DH   ← reads TA scaling-plan, DA migration-plan, SC threat-model + audit-path
  │
  ▼
TQ
```

DH consumes outputs from TA + DA + SC. It maps capacity → cost, threat surface → on-call playbook, schema migrations → rollback mechanics. Without those inputs, DH operates on operator-provided context.

## Anti-patterns

- **Treating deployment as IaC-only** — pattern + cutover + flag strategy matter as much as YAML
- **Single SLO for entire service** — per-critical-journey SLO; aggregate hides hot paths
- **Cost projection without per-component breakdown** — total $ unactionable
- **On-call playbook without detection signals** — runbook needs trigger pattern
- **Inventing new agents when existing cover** — 5 of 7 Capabilities reuse
- **Hardcoding deployment_pattern / observability_stack** — read from profile
- **Skipping rollback for "obviously safe" deploys** — every deploy has rollback documented

## Integration points

**Reads:**
- `~/.lintel/profile.yaml` `engineering.devops_hosting.*`
- `lib/pack-resolver.sh` for pack policy
- Existing agents (7) + 2 new agents
- Prior TA scaling-plan + DA migration-plan + SC threat-model + audit-path

**Writes:**
- `.claude/runtime/state/dh/*.{md,json}` (per-action artifacts)
- `.claude/runtime/audit/dh-decisions.jsonl`
- Brief Forge envelopes through the standard gate

**Triggered by:**
- Operator: `/li:dh {full|loop|single --action <name>}`
- BUILD phase: invokes as sub-module when deployment intent detected
- `/li:full-engineering-pass` (when composition skill ships): third stage after TA + DA‖SC

**Tested by:**
- `tests/shape/dh-module-contract.sh`
- `tests/unit/dh-routing.sh`
