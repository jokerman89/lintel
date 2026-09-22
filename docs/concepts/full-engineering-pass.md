# Full engineering pass

The [canonical composition](../../skills/full-engineering-pass/SKILL.md) coordinates
the five [engineering modules](engineering-modules.md) in dependency order without
introducing an execution engine.

| Stage | Why this order | Handoff |
|---|---|---|
| TA first | component/consumer boundaries constrain later decisions | architecture, contracts, NFRs and scaling assumptions |
| DA and SC after TA | data and security use those boundaries | schema/recovery/retention and threats/auth/applicable controls |
| DH after TA/DA/SC | rollout must fit state, threats and workload | deployment/recovery, observability/SLOs, cost and on-call |
| TQ last | verifies actual promises of the prior domains | consumer contracts, perf/coverage/regression and recovery evidence |

DA/SC are not always independent: privacy/retention or shared artifact decisions
can couple them. Default to serial. Concurrency requires an already opted-in
validated Swarm map, disjoint writes and actual attributable isolation. Reuse that
contract; neither an environment variable nor `parallel: true` proves it happened.

## Invocation

Use for the explicitly requested cross-domain outcome. For a bounded API decision,
use TA single capability; for a data-only question use DA. No mandatory founder
interview or company-deep mode is required to make the neutral harness useful.
Full/`--resume`/dry-run retain their meanings; dry-run does not fabricate artifacts.

Discovery reads the trusted installed **source**, not `<target>/skills`.
Before work, the caller fixes original map/package/leaves, mandatory domains and QA
obligations, verified P07 context and explicit advisory inputs. Actual role receivers
get exact modes/scopes and checkable outputs. Follow the
[shared caller procedure](../../skills/full-engineering-pass/references/domain-handoff.md#module-caller-procedure).

## No average-based acceptance

Retain six advisory dimensions per module (30 total) with evidence and uncertainty.
Four domains scoring 100 cannot clear a missing or failed mandatory fifth.
Missing required modules/artifacts/checkpoints block dependent work. Optional
exclusions need an explicit grounded decision; `--skip-module` cannot remove an
approved obligation. Changing acceptance requires a new bound decision/evidence.

GREEN/YELLOW/RED are presentation only: observed required gates/independent
acceptance, advisory residuals, or blocked required work respectively. The data core
always returns `release_clearance: false`. Actual SHIP still consumes the latest
P05 review and same-context QA and requires separate publication authority.

## Persistence and cold continuation

Use immutable requests/start/results under
`.claude/runtime/state/domains/<operation>/iNNNN/` and explicitly named domain
artifacts. Timestamps belong in fields, not unsafe Windows filenames. Record
original preimages before publication; later user edits remain conflicts.

The selected handoff carries cycle ID, original map/tasks, request/contexts,
observed last checkpoint, pending output/review, next owner and unknown side effects.
`workflow_resume` verifies the existing cycle/profile/map; it does not create a
new initiative. The agent reads actual saved evidence to identify the first unmet
checkpoint. Start without result is interrupted, never implicit permission to
repeat migration, deployment or side-effecting tests.

A loop creates an explicitly revised attempt/iteration and compares prior decisions;
reuse only unchanged relevant evidence. No automatic rollback/reset. Resume is a
utility, not a phase; the canonical nine-phase lifecycle is unchanged.

## Limits

The historic 500k/750k module planning hints are uncalibrated estimates, not host
context limits, measured cost or paid-execution authority. Optional Brief Forge and
audit invocation must actually occur before it can be claimed; no dormant hook is
activated by this procedure. Installed-resource closure and native-client behavior
need separate evidence. Historical v4.x feature-complete labels are not acceptance.

Check declarations with `tests/shape/full-engineering-pass-contract.sh` and
`tests/unit/full-engineering-pass-dag.sh`; actual mechanical consumption is covered
by `tests/integration/domain-module-consumers.sh`, while native handoff reports
identify the actual actors/tools and their limits. Reviewers never repair their findings.
