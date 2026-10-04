# Testing decision methods

Use for contract, coverage, regression, performance and resilience test design.
ContractTestArchitect designs checks; TestRunner runs/classifies without fixing;
RegressionDetective investigates in an owned trial; implementers repair separately.
The role name PerfBudgetEnforcer is retained, but a written budget is not CI enforcement.

## Synthetic worked example: additive is consumer-specific

A response enum originally permits `queued` and `done`; the provider adds `paused`.
A generated client with a closed enum rejects deserialization. A tolerant client
renders unknown values as `unknown`. The same wire change has different outcomes:
provider schema validation alone cannot establish backwards compatibility.

Build a matrix of exact provider and consumer/schema versions. Exercise the real
serializer and behavior, not just field presence. Required-request additions can
break old senders; optional-response additions can still break strict readers.
For GraphQL, examine null propagation and generated union/enum handling. For
protobuf, preserve field numbers and reserve removed numbers/names; test generated
clients and application semantics as well as wire decoding. For events/IPC/database
links, cover duplicates, ordering, malformed messages, version skew and missing data.

APIDesigner owns the declared interface; ContractTestArchitect owns consumer
expectations and runnable verification design. Reuse one schema rather than copying
it into an oracle that can agree with itself while the real consumer breaks.

## Comparable performance evidence

PerformanceAnalyzer owns measurement analysis; LatencyAnalyzer is its latency view
of this same evidence method. Choose one analysis for one source/workload/window.
PerfBudgetEnforcer transforms supplied evidence into budgets and detection proposals
without profiling. CapacityPlanner keeps capacity projections and failure headroom;
SystemArchitect keeps invariant/NFR design. These distinct purposes consume the
same measurements rather than repeating collection in a new role context.

Reuse the exact measurement artifact and its provenance; do not rerun a profiler
just to reformat results for TA, TQ or another report. Request a new authorized
measurement only for changed inputs, an unresolved measurement question or missing
evidence, naming the required observation and owner. A file labelled "profile" is
not sufficient evidence of its scope or comparability.

Record baseline/candidate revisions, dependency/config identity, build mode, runtime,
hardware, dataset, concurrency/arrival process, duration, warmup and cache/thermal
conditions. Interleave or randomize repeated runs where feasible to expose drift.
A closed-loop generator may hide stalls by sending less work when the service slows;
state the offered load and coordinated-omission limitation.

Record the actual request sample count, retained trace/profile sample count, dropped
events/errors, histogram boundaries and head/tail sampling policy/probability.
Distinguish an unbiased population histogram from deliberately tail-selected traces;
the latter cannot alone establish population percentiles. Explain coverage and
collection overhead, correlation between traces and duration boundaries, and any
coordinated-omission correction actually used (not merely recommended).

Report raw run counts and distribution summaries, effect size and uncertainty,
not just the faster of two runs. A baseline p95 range of 95-112 ms and a candidate
range of 101-114 ms does not establish a 5% regression from one pair. Choose a
practically meaningful threshold, adequate sample and suitable statistical method
before declaring the gate; do not invent precision from tiny tail samples.
Report tail uncertainty explicitly: p99 from 100 observations has only about one
observation beyond that rank; it does not characterize rare stalls reliably.
Use a suitable uncertainty method or state the unsupported tail, rather than
inventing confidence intervals. Missing baseline or zero samples is unmeasured.
A zero baseline makes percentage drift undefined; report the absolute change with
units and resolve the denominator before proposing a relative threshold.

Rank hot paths by measured exclusive cost and critical-path wall time, not traffic
frequency alone. Separate CPU, queue, lock and I/O waits. Inclusive spans overlap;
component p99s and p99-minus-p50 contributor labels are not additive. Use correlated
request evidence for end-to-end attribution and preserve multimodal workload splits.

Verify a budget gate with deliberately fast and slow synthetic fixtures, plus
missing baseline, no samples, runner error and skipped checks. The last four are
not successful performance results. Report the actual CI job/command and exits
before calling enforcement implemented.

## Coverage, flakes and failure injection

Map requirements to assertions and failure cases; line coverage does not show
assertion quality or the behavior of an external contract. A mutation score's
surviving mutants require triage (uncovered fault, equivalent mutation, limitation),
not a universal target detached from criticality.

Reproduce a flake on unchanged code/environment with run order and seed recorded.
Passing on retry does not erase the first failure. Quarantine needs an owner,
bounded duration, retained signal and replacement protection for critical behavior.
Design chaos around a named invariant: dependency timeout, duplicate delivery,
capacity loss or partial write; give an abort condition and exact recovery evidence.
Production fault injection needs separate authority; a stub cannot prove recovery.

## Sources

- Pact, [Consumer-driven contracts](https://docs.pact.io/consumer): actual consumer
  interactions and provider verification are distinct from a schema-only check.
- Protocol Buffers, [Updating a message type](https://protobuf.dev/programming-guides/proto3/#updating):
  wire safety and application compatibility are distinct.
- Google Benchmark, [User guide](https://google.github.io/benchmark/user_guide.html):
  repetitions, statistics and benchmark context.
- [ADR-0021](../../../.claude/decisions/0021-eval-harness.md) separates structural
  harness checks from actual model evaluations.
- [Shared review/QA evidence](../../review/references/evidence.md) preserves required
  outcomes, exact content identity and zero-run/unverified boundaries.
