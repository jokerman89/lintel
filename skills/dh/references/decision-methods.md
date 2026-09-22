# Hosting and operations decision methods

Use for rollout, observability, SLO, capacity, cost and on-call decisions.
DeploymentEngineer designs traffic progression; ReleaseEngineer designs the pipeline,
recovery/runbook and authorized release sequence; DevOpsToolchain implements scoped
repository artifacts. None of these planning outputs authorizes deployment.

## Traffic reversal is not state rollback

For every old/new binary pair, check schema reads/writes, event formats, cache entries,
feature-flag effects, in-flight jobs and external side effects. Blue-green reverses
traffic quickly only if the old environment can still process current state. A flag
can hide a feature without undoing data it already wrote.

Stage by a representative population and enough observations, not just elapsed time.
Inspect routing/stickiness, failure-domain coverage, background consumers, available
capacity and matched control traffic. Define progress/abort signals, their measurement
windows, false-alarm handling, recovery owner and the point of no return.

Synthetic worked example: v2 writes an enum value that v1 cannot parse. Routing all
traffic back to v1 would turn a localized canary problem into widespread read failures.
Keep the old reader compatible before enabling the new writer, or choose a tested
forward repair. A "rollout undo" command alone does not establish recoverability.
Rehearse failure after a write, not only failure before the new binary starts.

## Observable SLOs and unknown telemetry

Specify the user journey, eligible events, good events, exclusions, window and source
query. Treat an absent series or zero eligible events as unknown, not perfect uptime.
Reconcile edge and server observations, retries and timeouts; client failures should
not vanish simply because they never reached the application's success counter.

For a synthetic 99.9% request-success target over 5,000,000 eligible requests,
the error budget is 5,000 bad requests. A measured 2% failure rate burns at 20 times
the target's 0.1% failure allowance while that rate holds. A short-window alarm must
be evaluated against traffic volume and longer-window confirmation; a low-volume
canary with no errors is not proof of safety.

Use bounded metric labels; per-user IDs cause cardinality growth and may expose data.
State sampling effects before deriving rates from traces. Tail sampling can aid
diagnosis but biases naive population estimates. Set retention by signal purpose,
access controls, cost and applicable policy, not a blanket seven-year rule.

## Capacity and cost decisions

Join CapacityPlanner's measured workload/service demand to actual SKU, region,
currency, price date, commitment/discount terms, storage, request and egress units.
Keep forecast ranges separate from invoices and configured resources. An annual
commitment does not disappear when an instance is removed. A low-CPU failover node
may be necessary headroom; an unattached disk may be a retained recovery asset.

Compare at least normal, expected peak and a named failure scenario. A quoted
"50% fewer instances" is not "50% lower bill" when storage, network and commitments
remain. Recommend an owner-approved experiment and remeasure SLO/cost, not deletion.

Runbooks begin with a specific signal and last-known-good state. Separate authorized
read-only diagnostics, reversible local steps, live mutations and escalation.
Include loss of telemetry, unavailable approver and failed recovery; absence of an
alert cannot establish health.

## Sources

- Google SRE Workbook, [Implementing SLOs](https://sre.google/workbook/implementing-slos/)
  and [Canarying releases](https://sre.google/workbook/canarying-releases/).
- Google SRE, [Handling overload](https://sre.google/sre-book/handling-overload/).
- Kubernetes, [Pod QoS](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/):
  equal requests/limits can be intentional; no fixed memory ratio is universal.
- [Universal adapter](../../../shims/universal/ADAPTER.md): actual tool/permission
  evidence and explicit unsupported operations.
