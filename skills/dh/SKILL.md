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
gap_if_skipped: "Production-bound work lacks state-compatible recovery, observable service objectives, capacity/cost assumptions and actionable on-call evidence."
navigation:
  primary_intent: produce ops-grade decisions for rollout, observability and cost
  triggers:
    - new service / major rollout / observability gap / cost anomaly
    - operator types /li:dh {full|loop|single --action <name>}
    - active workflow requests operational depth
  sibling_workflows:
    - /li:ta — technical architecture
    - /li:da — data architecture
    - /li:sc — security and compliance
    - /li:tq — testing and QA
    - /li:full-engineering-pass — dependency-ordered composition
  risk_level: high
  auto_mode_eligible: false
  estimated_tokens: 80000
domain:
  preferences_root: engineering.devops_hosting.*
  granularities: [full, loop, single]
  checkpoints:
    - deployment_plan_locked: traffic, compatibility and abort conditions agreed
    - observability_specified: required signals and query coverage evidenced
    - slos_defined: user journeys, objectives and budget policy grounded
    - cost_projected: sourced cost ranges and workload assumptions explicit
    - on_call_ready: detection, recovery and escalation responsibilities verified
  recovery:
    - on_failure: preserve actual state and reconcile the affected checkpoint
  continuation:
    - after_fix: verify unchanged inputs or begin an explicitly revised iteration
  raise_help:
    - cost_exceeds_approved_budget: refer the supported trade-off to its owner
    - slo_requirement_unmet: surface measured gap and alternatives
    - recovery_uncertain: stop before unsafe reversal or replay
---

# Hosting and operations

Read [operations decision methods](references/decision-methods.md) for state-compatible
rollback, actual SLO/capacity/cost sources and uncertainty. Design artifacts do not
deploy services. `/li:dh full`, saved `/li:dh loop` and `/li:dh <capability>` or
`/li:dh single --action <capability>` preserve their distinct scope; a routine
already-approved deployment uses its existing runbook.

## Sub-capability dispatch

| Capability | Dispatches to (agents) | Produces | Decisions and checks |
|---|---|---|---|
| `deployment-plan` | ReleaseEngineer planning-only + DeploymentEngineer | pattern, traffic stages, feature flags and abort signals | old/new state and consumer compatibility, capacity, artifact provenance; no universal blue-green choice |
| `observability-spec` | ObservabilityArchitect + Architect | RED/USE metrics, traces, logs, dashboards and routing | real stack/SDK conventions; privacy/cardinality/sampling budgets, applicable retention |
| `sli-slo-spec` | ObservabilityArchitect + SystemArchitect | good/eligible-event queries, objectives and burn-rate/budget policy | derive target/window from user need; no universal 99%/30-day minimum; no-data is unknown |
| `cost-projection` | CostAnalyzer + CapacityPlanner | per-component/SKU range and anomaly thresholds | price source/date/region/currency/commitments, measured workload and egress; no invented dollar ceiling |
| `rollback-strategy` | ReleaseEngineer planning-only + SecurityAuditor | per-failure-mode recovery, blast radius and revoke paths | binary/schema/event compatibility, in-flight effects, actual rehearsal or unverified recovery |
| `capacity-headroom` | CapacityPlanner + LatencyAnalyzer | per-resource/failure-domain headroom and scaling triggers | current load mix, queueing, saturation and peak/failover; trigger before observed degradation |
| `on-call-playbook` | ReleaseEngineer planning-only + SecurityAuditor | signal-to-action decision tree and escalation matrix | named owners, permitted first diagnostics, live-action approvals and failed-recovery path |

ReleaseEngineer retains **authorized-execution** for separately approved release work;
this module's planning handoff is not blanket prohibition. No deployment, registry
push, IAM change, live database action or external notification is granted by a role name.
DevOpsToolchain implements scoped repository configuration when requested, separately
from reviewer assessment.

## Workflow

1. Execute [shared admission and live-policy verification](../full-engineering-pass/references/domain-handoff.md#module-caller-procedure)
   against the original map/package/leaves. Reuse accepted `work_context`,
   `workflow_inspect`/`workflow_resume`; never take a newer unrelated SLO report.
2. Read TA architecture/scaling, DA migration and SC threat/audit evidence relevant
   to this request. Required missing upstream evidence blocks dependent work. Inspect
   the actual environment/version; use explicit advice and typed verified pack values.
3. Prepare P05 obligations and expected domain checkpoints before observations.
   Assign receiver mode/scope and exact original publication state. No personal-file parser.
4. Record start, perform the scoped method, persist results and actual checks.
   Suggested commands are not executed operations; local `act` or a deploy dry-run
   may still have effects and requires command inspection/target authority.
5. Externally prepare final P05 context, fresh domain verification, real QA and
   independent spec then quality. Reviews report findings; the implementer repairs.

## Checkpoint ownership

| Checkpoint | Owner/method | Observable acceptance |
|---|---|---|
| `deployment_plan_locked` | DeploymentEngineer + ReleaseEngineer | selected pattern, state compatibility, stage criteria/abort and actual rehearsal limits |
| `observability_specified` | ObservabilityArchitect | emitted/derived signal queries, cardinality/privacy/retention and missing-series handling |
| `slos_defined` | SystemArchitect + ObservabilityArchitect | agreed journey/window/objective, source query and error-budget action |
| `cost_projected` | CostAnalyzer + CapacityPlanner | per-component priced units, normal/peak/failure assumptions, uncertainty and applicable budget |
| `on_call_ready` | ReleaseEngineer + SecurityAuditor | per-failure trigger, read-only diagnostics, recovery/escalation owners and approval boundaries |

Keep rollback and capacity-headroom artifacts in deployment/cost/on-call checks, not
lost between checkpoint names. RED measures request work, USE resource consumption.
Wire propagation headers and stored trace IDs are distinct; test the selected SDK's
mapping. Log-level names do not establish retention law or required sampling rates.

Worked choice: a canary writing an enum old readers cannot parse cannot safely
reverse traffic just because the load balancer can switch quickly. Design reader-first
compatibility or verified forward repair. A 99.9% objective over five million
requests permits 5,000 bad events, while zero eligible events proves no availability.

## Handoff and recovery

Preserve deployment/cutover/flags, observability, SLI/SLO, cost, capacity, rollback and
on-call artifacts with their actual sources. Request/result files use safe explicit
operation/iteration paths; selected legacy `state/dh/` artifacts are retained as
history, not automatically current. Carry the next owner and unverified checks.

Cold resume uses the shared table: started-without-result is interrupted. Reconcile
unknown effects before repeating or undoing any operation. Loops retain prior
artifact references and validate changed dependencies; no automatic rollback command.

Advisory dimensions remain Deployment pattern (including recovery),
Observability instrumentation, SLI/SLO definitions, Cost projection, Capacity headroom and On-call playbook,
measured against the observable checkpoint criteria. Scores cannot erase one missing mandatory domain. DONE means
selected required evidence and independent acceptance; DONE_WITH_CONCERNS is only
advisory residue. Unresolved evidence/authority is BLOCKED/NEEDS_CONTEXT.

## Integration and dormant hooks

DA/SC can feed DH only through verified selected artifacts; TQ exercises its promises.
Optional audit/Brief Forge use must be an observed configured invocation, not a
fabricated enforcement claim. Preserve these dormant ADR-0008 hook resources:

- `hooks/shared/dh-deploy-without-rollback-warn/`
- `hooks/shared/dh-observability-gap-warn/`
- `hooks/shared/dh-cost-budget-warn/`

This module does not enable them, publish anything or complete the enclosing phase.
