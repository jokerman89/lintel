# TQ: testing and quality assurance

TQ verifies the requirements and promises from TA/DA/SC/DH through the
[canonical skill](../../skills/tq/SKILL.md) and [testing methods](../../skills/tq/references/decision-methods.md).
It follows the shared [engineering-module contract](engineering-modules.md), not
a new runner/approval system.

## Retained capabilities

| Capability | Receiver and output |
|---|---|
| coverage-audit | TestRunner measurements + Architect requirement/critical-path gaps |
| perf-budget-spec | LatencyAnalyzer baseline + PerfBudgetEnforcer justified budget/gate design |
| contract-test-design | APIDesigner interface + ContractTestArchitect consumer/version matrix |
| regression-suite | RegressionDetective isolated cause/fix mapping + TestRunner actual checks |
| chaos-plan | SecurityAuditor/SystemArchitect failure/recovery/abort plan |
| flaky-quarantine | TestRunner/RegressionDetective repeated outcomes, owner and bounded remediation |
| test-pyramid-review | TestRunner/Architect per-kind timing/flake/risk and rebalancing |

Full checkpoints: `coverage_targets_met`, `perf_budgets_locked`,
`contract_tests_complete`, `regression_suite_curated`, `chaos_scenarios_documented`.
Keep single capability and saved loop targeted; no test suite is run merely because
the capability table names it. Inspect actual commands, hooks, data and effects.

## Evidence methods

Line coverage cannot prove assertion quality. Map original requirements to behavior/
failure cases and inspect surviving mutations with their limitations. Critical batch
work can deserve tighter protection than an interactive endpoint; no global 80/100%
or arbitrary journey labels determine policy.

New enum values may break generated consumers despite valid provider schemas.
Test request/response direction, actual serializers and concurrent versions across
HTTP, GraphQL, protobuf, events or IPC as applicable. One shared schema, real link
verification; no duplicate oracle that agrees only with itself.

Performance comparison records source/env/workload/build/runtime, warmup and offered
load, repetitions and uncertainty. An unimplemented CI budget is a proposal, not
enforcement. Tiny samples cannot establish precise tails. A failed/zero/skipped
required case stays incomplete; do not drop it and report a green average.

Flakes retain the failed observation even after retry. Quarantine needs an owner,
time bound and replacement critical coverage. Chaos plans name the invariant,
failure injection, abort and recovery; disabled chaos is not a successful stub.
Live fault injection requires exact separate authorization.

## Continuation and acceptance

Persist actual named coverage/performance/contract/regression/chaos/quarantine/
pyramid artifacts, raw evidence, exit/counts and source identities. TestRunner and
other reviewers report; implementers fix. A separately attributable reviewer plus
actual P05 QA/reader evidence is required, not a second role label.

The shared explicit attempt/iteration and cold state table prevent implicit replay
of unknown side effects or reuse after changed inputs. Six advisory dimensions remain
coverage, performance, contracts, regression, recovery and distribution. Missing
mandatory evidence blocks regardless of scores. Historical feature-complete claims
do not close current runtime/client/installed acceptance.

Opt-in `tq-coverage-drop-warn`, `tq-perf-regression-warn` and
`tq-contract-break-warn` remain dormant absent actual compatible registration.
