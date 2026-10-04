---
name: li-dh
description: Use for devops and hosting depth — deployment plans, rollback strategy, observability specs, SLI/SLO budgets, capacity headroom, cost projection, and on-call playbooks. Reach for it when the work turns on how the system runs in production. Runs full, loop, or single-capability, dispatching to the ops agents and scoring against a rubric.
---

> **Lintel on GitHub Copilot.** Generated from `skills/dh/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/dh/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/dh/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Hosting and operations

Preference metadata only: [optional engineering preferences](../../../skills/da/references/preferences.md)
explains the retained `preferences_root` hint; it is not a validated pack interface.

Read [operations decision methods](../../../skills/dh/references/decision-methods.md) for state-compatible
rollback, actual SLO/capacity/cost sources and uncertainty. Design artifacts do not
deploy services. `/li-dh full`, saved `/li-dh loop` and `/li-dh <capability>` or
`/li-dh single --action <capability>` preserve their distinct scope; a routine
already-approved deployment uses its existing runbook.

## Sub-capability dispatch

| Capability | Dispatches to (agents) | Produces | Decisions and checks |
|---|---|---|---|
| `deployment-plan` | DeploymentEngineer | pipeline stages, pattern, traffic stages, feature flags and abort signals | old/new state and consumer compatibility, capacity, artifact provenance; no universal blue-green choice |
| `observability-spec` | ObservabilityArchitect + Architect | RED/USE metrics, traces, logs, dashboards and routing | real stack/SDK conventions; privacy/cardinality/sampling budgets, applicable retention |
| `sli-slo-spec` | ObservabilityArchitect + SystemArchitect | good/eligible-event queries, objectives and burn-rate/budget policy | derive target/window from user need; no universal 99%/30-day minimum; no-data is unknown |
| `cost-projection` | CostAnalyzer + CapacityPlanner | per-component/SKU range and anomaly thresholds | price source/date/region/currency/commitments, measured workload and egress; no invented dollar ceiling |
| `rollback-strategy` | DeploymentEngineer + SecurityAuditor | per-failure-mode recovery, blast radius and revoke paths | binary/schema/event compatibility, in-flight effects, actual rehearsal or unverified recovery |
| `capacity-headroom` | CapacityPlanner + LatencyAnalyzer | per-resource/failure-domain headroom and scaling triggers | current load mix, queueing, saturation and peak/failover; trigger before observed degradation |
| `on-call-playbook` | DeploymentEngineer + SecurityAuditor | signal-to-action decision tree and escalation matrix | named owners, permitted first diagnostics, live-action approvals and failed-recovery path |

DeploymentEngineer returns planning content; the caller owns persistence. ReleaseEngineer
retains **authorized-execution** for separately approved release work, not these planning
dispatches. No deployment, registry
push, IAM change, live database action or external notification is granted by a role name.
DevOpsToolchain implements scoped repository configuration when requested, separately
from reviewer assessment.

## Workflow

Read and execute the [shared module caller procedure](../../../skills/full-engineering-pass/references/domain-handoff.md#module-caller-procedure)
before domain work. It is the sole owner of original work/package/leaf admission,
live P07/policy checks, immutable obligations, checkpoint publication, cold continuation
and final QA/independent acceptance. Apply this operations method inside that procedure:

1. Read the relevant TA architecture/scaling, DA migration and SC threat/audit
   evidence, not a newer unrelated SLO report. Required missing upstream evidence
   blocks dependent work. Inspect the actual environment/version and policy inputs.
2. Use the capability and checkpoint tables for rollout/state compatibility,
   observability, SLOs, capacity/cost and recovery ownership. State assumptions and
   unknowns; explicit advice is not a measured service objective.
3. Inspect commands and exact-target authority before any authorized observation:
   local `act` or a deploy dry-run may still have effects. Reviews report findings;
   implementers repair. A suggested command is not an executed operation.

## Checkpoint ownership

| Checkpoint | Owner/method | Observable acceptance |
|---|---|---|
| `deployment_plan_locked` | DeploymentEngineer | selected pipeline/pattern, state compatibility, stage criteria/abort and actual rehearsal limits |
| `observability_specified` | ObservabilityArchitect | emitted/derived signal queries, cardinality/privacy/retention and missing-series handling |
| `slos_defined` | SystemArchitect + ObservabilityArchitect | agreed journey/window/objective, source query and error-budget action |
| `cost_projected` | CostAnalyzer + CapacityPlanner | per-component priced units, normal/peak/failure assumptions, uncertainty and applicable budget |
| `on_call_ready` | DeploymentEngineer + SecurityAuditor | per-failure trigger, read-only diagnostics, recovery/escalation owners and approval boundaries |

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

## Reusable patterns

Follow the [reusable pattern consumer contract](../../../skills/pattern/references/consumer-contract.md).
Module entry resolves the delivery and operations expectations bound to the current target
context and passes each sub-capability only its projected clauses (`project` for the mapped
package, or the clauses mapped to it). An unknown deployment environment yields `needs-context`
and blocks the dependent design; no live cloud, tenant or environment discovery is implied, and
requirements are never inferred from generic recommendations. When the runtime reports no
patterns, the module is unchanged.

## Integration and dormant hooks

DA/SC can feed DH only through verified selected artifacts; TQ exercises its promises.
Optional audit/Brief Forge use must be an observed configured invocation, not a
fabricated enforcement claim. Preserve these dormant ADR-0008 hook resources:

- `hooks/shared/dh-deploy-without-rollback-warn/`
- `hooks/shared/dh-observability-gap-warn/`
- `hooks/shared/dh-cost-budget-warn/`

These optional warnings are unobserved without actual registration/execution
evidence and do not establish recovery, observability or cost compliance.
This module does not enable them, publish anything or complete the enclosing phase.
