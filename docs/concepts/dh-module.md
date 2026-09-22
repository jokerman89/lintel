# DH: hosting and operations

DH connects architecture, data and threat decisions to production operability.
The [canonical skill](../../skills/dh/SKILL.md), [operations methods](../../skills/dh/references/decision-methods.md)
and [engineering-module contract](engineering-modules.md) define the actual procedure.
Planning is not deployment authority.

## Retained capabilities

| Capability | Receiver and evidence |
|---|---|
| deployment-plan | DeploymentEngineer cutover + ReleaseEngineer planning-only pipeline/flags/abort |
| observability-spec | ObservabilityArchitect/Architect metrics, traces, logs, dashboards and routing |
| sli-slo-spec | ObservabilityArchitect/SystemArchitect measurable journey/window/objective and budget policy |
| cost-projection | CostAnalyzer/CapacityPlanner sourced per-unit/component forecast |
| rollback-strategy | ReleaseEngineer planning-only/SecurityAuditor state-compatible recovery and revoke paths |
| capacity-headroom | CapacityPlanner/LatencyAnalyzer workload/resource/failover and scaling signals |
| on-call-playbook | ReleaseEngineer planning-only/SecurityAuditor trigger, first diagnostics and escalation |

Full checkpoints remain `deployment_plan_locked`, `observability_specified`,
`slos_defined`, `cost_projected`, `on_call_ready`. Rollback and headroom remain
explicit outputs within that chain. Direct capability and saved loop retain scope.
ReleaseEngineer still supports separately exact-authorized execution, not only planning.

## Methods and false assumptions

Blue-green traffic reversal does not undo incompatible data. Test old/new readers,
writers, queues and side effects; a feature flag cannot erase a delivered event.
Canary evidence needs representative volume, matched baseline and abort criteria,
not just a timer or fixed percentages.

Use RED for request work and USE for resources. Distinguish propagation headers from
stored trace IDs, and emitted signals from derived SLI queries. Retention/sampling/
cardinality/privacy follow actual need/policy/cost, not template defaults.
Zero eligible requests is unknown availability. Five million eligible requests at
99.9% allows 5,000 bad events; burn rate and observation windows still need context.

Price forecasts identify source/date/currency/region/commitments and workload units.
Manifests aren't invoices. Low utilization can be necessary failover capacity;
an unattached disk can be a retained recovery asset, not automatic waste.
There is no universal cloud, $10k budget or 99%/30-day minimum.

## Handoff and gates

TA scaling/contracts, DA migration and SC threat/audit evidence feed DH. TQ tests
DH promises. Preserve cutover, rollback, observability, SLO, cost, headroom and on-call
artifacts with original map/profile identity and actual check results.

Use safe request/start/result paths and the shared cold continuation table. Missing
results or uncertain external effects stop automatic rerun/rollback. Required gaps
block dependent work; six advisory dimensions (deploy/recovery, signals, SLO, cost,
headroom, on-call) cannot override them. Actual independent review stays separate.

Domain hooks `dh-deploy-without-rollback-warn`, `dh-observability-gap-warn` and
`dh-cost-budget-warn` remain opt-in. File presence is not an observed registration,
and an advisory warn-hook is not the authoritative deployment gate.
