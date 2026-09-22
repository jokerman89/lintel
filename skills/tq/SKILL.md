---
name: tq
layer: foundation
workflow_root: true
description: Use for testing and QA-strategy depth — test-pyramid review, coverage audits, contract-test design, regression suites, flaky-test quarantine, perf budgets, and chaos plans. Reach for it when test strategy needs deliberate design rather than ad-hoc tests. Runs full, loop, or single-capability, dispatching to the test agents and scoring against a rubric.
color: green
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Quality-bearing work lacks consumer-specific contracts, comparable performance evidence, regression coverage and verified recovery."
navigation:
  primary_intent: produce evidence-led test strategy and validation
  triggers:
    - critical-path feature / release prep / regression / performance concern
    - operator types /li:tq {full|loop|single --action <name>}
    - active workflow requests deliberate validation
  sibling_workflows:
    - /li:ta — technical architecture
    - /li:da — data architecture
    - /li:sc — security and compliance
    - /li:dh — hosting and operations
    - /li:full-engineering-pass — dependency-ordered composition
  risk_level: medium
  auto_mode_eligible: false
  estimated_tokens: 80000
domain:
  preferences_root: engineering.testing_qa.*
  granularities: [full, loop, single]
  checkpoints:
    - coverage_targets_met: scoped requirement assertions and required coverage evidenced
    - perf_budgets_locked: comparable baseline and justified detection/enforcement
    - contract_tests_complete: actual consumer and provider verification
    - regression_suite_curated: fix-to-test and golden-path evidence
    - chaos_scenarios_documented: explicit recovery claims, authorized scenarios and actual limits
  recovery:
    - on_failure: retain failing output and select the unmet checkpoint after verification
  continuation:
    - after_fix: rerun affected checks against the new actual result
  raise_help:
    - critical_requirement_unverified: retain required acceptance gap
    - perf_regression_exceeds_approved_budget: present measured effect and uncertainty
    - active_consumer_break: stop dependent acceptance until resolved
---

# Testing and quality assurance

Read [testing decision methods](references/decision-methods.md) for consumer-specific
compatibility, comparable baselines, uncertainty and actual runtime evidence.
`/li:tq full` covers all checkpoints; saved `/li:tq loop` revisits the affected strategy/results;
`/li:tq <capability>` or `/li:tq single --action <capability>` stays targeted. Ordinary test execution can
use the existing runner/QA workflow without creating a domain plan.

## Sub-capability dispatch

| Capability | Dispatches to (agents) | Produces | Decisions and checks |
|---|---|---|---|
| `coverage-audit` | TestRunner + Architect | per-component requirement/line/branch/mutation gaps and backfill priorities | approved critical-path targets, observed commands/counts and exclusions; no universal 80/100% acceptance |
| `perf-budget-spec` | LatencyAnalyzer + PerfBudgetEnforcer | per-journey budgets, detection and CI-gate design | comparable baseline, workload/environment/repetitions/uncertainty; a spec is not enforcement |
| `contract-test-design` | APIDesigner + ContractTestArchitect | interface surface, consumer expectations and version matrix | actual serializers and active consumers; REST/GraphQL/gRPC/events/IPC as applicable; no mandatory Pact |
| `regression-suite` | RegressionDetective + TestRunner | fix-to-test mapping and golden-path execution health | select relevant history explicitly; isolated bisection with original-state protection, not automatic caller changes |
| `chaos-plan` | SecurityAuditor + SystemArchitect | failure matrix, abort/recovery criteria and owners | selected threat/on-call evidence; disabled chaos is a scoped not-run/N/A decision, not a passing stub |
| `flaky-quarantine` | TestRunner + RegressionDetective | repeated-outcome evidence, remediation owner and bounded quarantine | same source/env/seed/order; passing on retry does not erase failure; policy-derived duration and critical coverage |
| `test-pyramid-review` | TestRunner + Architect | test-kind distribution, time, flake rate and rebalancing options | unit/integration/e2e/contract/perf; optimize feedback per risk, not a universal count ratio |

Existing tooling can include `go test -coverprofile`, `pytest --cov`, the project's
Jest/Vitest coverage, `cargo tarpaulin` or equivalent. Inspect manifests and effects
first; do not install a guessed tool, use production services or claim unrun checks.

## Workflow

1. Follow [shared module admission](../full-engineering-pass/references/domain-handoff.md#module-caller-procedure):
   original work/package/leaves and public `work_context`, live profile/policy,
   explicit invocation advice and source identity. Use `workflow_resume` for the
   actual saved cycle rather than starting another test phase.
2. Read relevant TA contracts/NFRs, DA query/migration invariants, SC threats and DH
   SLO/recovery criteria. Reuse only evidence for unchanged relevant inputs.
3. Fix required QA controls before observations and build the accepted domain request.
   Record starts and original output preimages. TestRunner is an independent
   run/classify/report receiver when actually separate; it never edits failures.
4. Execute inspected, authorized checks; retain stdout/stderr, counts, skips, exits,
   source/env and limitations. ContractTestArchitect designs; real consumer/provider
   runners verify. A toy example or grep is not live compatibility evidence.
5. Persist results, externally prepare final P05 context and consume actual QA/fresh
   domain verification. Independent spec then quality assess the selected result;
   no self-labelled actor or fabricated corroboration.

## Checkpoint ownership

| Checkpoint | Method/owner | Observable acceptance |
|---|---|---|
| `coverage_targets_met` | TestRunner measures, Architect maps risk | exact requirement-to-assertion gaps and applicable targets, not coverage alone |
| `perf_budgets_locked` | LatencyAnalyzer + PerfBudgetEnforcer | baseline/candidate identity, sample distributions, meaningful thresholds and real positive/negative gate evidence |
| `contract_tests_complete` | APIDesigner + ContractTestArchitect + actual runner | each supported consumer/version checked; required failed/unknown consumers remain blockers |
| `regression_suite_curated` | RegressionDetective + TestRunner | reproduced failure, retained fix-to-test link, golden and edge paths, flake disposition |
| `chaos_scenarios_documented` | SecurityAuditor + SystemArchitect | scenario/control/abort/owner plan; actual recovery if required, otherwise explicitly unexecuted design |

Worked contrast: adding `paused` to an enum breaks a closed generated consumer but
may work with a tested unknown-value branch. Similarly, a single faster benchmark
run does not prove improvement: retain variance/environment, offered load and tail
sample limits. Production fault injection always needs its own exact authority.

## Handoff, loop and honest failure

Preserve coverage, performance, contract/version matrix, regression, chaos,
quarantine and test-pyramid artifacts. Bind actual commands/output to original
requirements, receiver mode and safe operation/iteration paths. Existing
`state/tq/` reports remain available when explicitly selected, not newest-file truth.

A failed or interrupted runner stays failed/incomplete. Do not drop NaNs, skipped
scenarios or timeouts from the denominator and call the remainder a required pass.
Cold resume uses the shared state table; do not automatically repeat a side-effecting
test or erase an earlier failure. A loop creates new evidence for affected inputs.

Six advisory dimensions remain Critical-path coverage, Perf budgets, Contract tests,
Regression suite, Chaos scenarios and Test pyramid, measured against the observable
checkpoint criteria. Missing/failed mandatory evidence blocks despite a
high average. DONE requires actual selected checks and independent acceptance;
DONE_WITH_CONCERNS retains only advisory issues; BLOCKED/NEEDS_CONTEXT names required
gaps. Module completion is not SHIP permission or enclosing-task completion.

## Integration and dormant hooks

TQ validates the promises of TA/DA/SC/DH; it does not rewrite their schemas or policy.
It is the final engineering-domain module in composition order, not proof that all
client/installed or compound acceptance is complete.
Optional audit/Brief Forge use remains explicit. Preserve opt-in ADR-0008 hooks:

- `hooks/shared/tq-coverage-drop-warn/`
- `hooks/shared/tq-perf-regression-warn/`
- `hooks/shared/tq-contract-break-warn/`

The hook file is not proof of registration, enforcement or a successful test run.
