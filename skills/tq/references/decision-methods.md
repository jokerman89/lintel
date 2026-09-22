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

Record baseline/candidate revisions, dependency/config identity, build mode, runtime,
hardware, dataset, concurrency/arrival process, duration, warmup and cache/thermal
conditions. Interleave or randomize repeated runs where feasible to expose drift.
A closed-loop generator may hide stalls by sending less work when the service slows;
state the offered load and coordinated-omission limitation.

Report raw run counts and distribution summaries, effect size and uncertainty,
not just the faster of two runs. A baseline p95 range of 95-112 ms and a candidate
range of 101-114 ms does not establish a 5% regression from one pair. Choose a
practically meaningful threshold, adequate sample and suitable statistical method
before declaring the gate; do not invent precision from tiny tail samples.

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
