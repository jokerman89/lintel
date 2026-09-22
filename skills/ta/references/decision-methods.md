# Architecture decision methods

Read for boundary review, quality attributes or scaling design. These are reasoning
methods, not a scheduler, new result format or permission to implement a topology.
Architect owns component interfaces; BackendArchitect owns distributed interaction;
SystemArchitect specifies cross-system invariants and measurable quality attributes.

## Invariants before topology

Start with an observable rule, its owner and its failure mechanism. "One captured
payment per order" is an invariant; "three services and a queue" is a topology.
Trace each writer, transaction, retry and asynchronous consumer that can violate the
rule. A service boundary does not create a transaction boundary guarantee.

Compare a local transaction, an outbox plus idempotent consumer, and a compensating
workflow only where each is viable. Name the price: local coupling, delayed delivery
and deduplication state, or intermediate externally visible states. Do not call
compensation a rollback of an already delivered email or captured payment. Give the
implementer a failure-injection case and the reviewer an observable invariant.

## Failure isolation and deadlines

Follow a request through queues, pools and dependencies, including shared resources.
A circuit breaker can stop repeated calls to a failing dependency, but does not
isolate a shared exhausted connection pool. Bound concurrency and queues at the
actual contention point; define overload rejection and which work may degrade.
Distinguish a correctness-critical read from an optional recommendation widget.

Propagate a remaining end-to-end deadline, including queue time and backoff. Budget
retries in one appropriate layer and classify retriable failures. Retrying an
operation with unknown side effects requires an idempotency contract, not optimism.
Three layers each making three total attempts can cause 27 downstream attempts.
Specify how tests observe cancellation, duplicate effects and load after failure.

## Synthetic worked example: composing a tail

For 100 aligned requests, service A takes 101 ms on request 1 and 1 ms otherwise.
Service B takes 101 ms on request 2 and 1 ms otherwise. Using nearest-rank percentiles,
each component p99 is 1 ms, so their sum is 2 ms. The serial end-to-end sample has
98 requests at 2 ms and two at 102 ms: its p99 is **102 ms**.

For a single request, serial exclusive durations add; concurrent branches contribute
their critical path, not their sum. Component percentiles are not request durations:
adding p99s need not yield the end-to-end p99 and may under- or over-estimate it.
Prefer correlated traces or end-to-end histograms with consistent boundaries,
sampling, workload and windows. Do not add overlapping parent/child spans.

A 500 ms request budget with 120 ms already elapsed leaves at most 380 ms for
remaining work, including network and response overhead. Giving every downstream
call a fresh two-second timeout contradicts that budget.

## Capacity is a hypothesis to test

Inventory workload mix, per-request service demand, saturation, queueing, concurrency,
tenant skew, cache state and failure headroom. In steady state, 2,000 requests/s
with mean in-system time 0.08 s implies mean concurrency 160; it does not prove
that 160 workers meet a tail SLO. Heavy requests and failover can dominate capacity.
Compare measured load steps before extrapolating, and bound uncertainty explicitly.
A manifest supplies configured resources, not actual utilization or a priced bill.

For each proposed NFR or invariant, explain the requirement source, owner, measurement
boundary, environment, sample/window, failure case and unresolved evidence in the
existing report prose. Do not invent schema fields or mark an estimate as a run.

## Sources

Original synthesis, not copied playbooks. Consult the deployment's versions at use:

- Google SRE, [Addressing cascading failures](https://sre.google/sre-book/addressing-cascading-failures/):
  retries, deadlines, load shedding and shared-resource failure.
- Google SRE, [Handling overload](https://sre.google/sre-book/handling-overload/):
  resource demand and workload-dependent capacity rather than QPS alone.
- Google SRE Workbook, [Implementing SLOs](https://sre.google/workbook/implementing-slos/):
  stakeholder-approved targets and observable good/eligible events.
- [ADR-0026](../../../.claude/decisions/0026-hybrid-work-packages.md) and
  [Universal adapter](../../../shims/universal/ADAPTER.md): artifact ownership and
  evidence are distinct from implementation, native dispatch and review acceptance.
