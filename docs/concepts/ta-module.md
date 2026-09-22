# TA: technical architecture

TA turns architectural requirements into interfaces, decisions and verifiable
invariants, not automatic implementation. Use the [canonical skill](../../skills/ta/SKILL.md)
for invocation and [worked methods](../../skills/ta/references/decision-methods.md)
for failure isolation, retries/deadlines, tail latency and capacity reasoning.
The shared [engineering-module contract](engineering-modules.md) governs work/
profile identity, evidence, actual host operations and recovery.

## Retained capabilities and roles

| Capability | Distinct responsibility | Output |
|---|---|---|
| api-design | APIDesigner designs REST/GraphQL/gRPC surfaces | versioned contract and actual consumer impact |
| dependency-graph | Explorer locates; Architect synthesizes | dependencies, cycles, layering and consumers |
| boundary-review | BackendArchitect + Architect | bounded-context leaks, invariants and fault isolation |
| complexity-audit | Architect interprets measured metrics | tool/scope/budget evidence and refactor options |
| scaling-plan | CapacityPlanner + BackendArchitect | workload/resource model, bottlenecks and uncertainty |
| contract-collision | APIDesigner + Architect | consumer-version compatibility and migration decisions |
| quality-attributes | SystemArchitect + Architect | NFRs with requirement source, boundary and verification |

SystemArchitect owns system-wide constraints, not component redesign. A boundary
review needs an explicit SystemArchitect subtask when that expertise is requested,
not a fictional default dispatch. ADRDrafter records proposed/accepted decisions
only under the actual decision owner's authority.

## Checkpoints and examples

Full order is `discovery_complete`, `decision_documented`, `contract_locked`,
`complexity_within_budget`, `non_functionals_specified`. Single capability stays
targeted; loop revisits actual changed dependencies and retained prior artifacts.

An invariant such as one captured payment per order comes before choosing services
and queues. A durable outbox plus idempotent consumer has different failure/replay
obligations from a local transaction. A breaker does not isolate a shared pool.
Component p99 values cannot be summed to obtain end-to-end p99; use correlated
request evidence and avoid overlapping spans.

Retain `system-arch.md`, ADRs, OpenAPI/SDL/protobuf, dependency graph and NFR outputs.
Explicitly selected old `state/ta/` artifacts remain history, not default current truth.
New checkpoint metadata uses the common safe attempt namespace.

## Advice is not policy

Read actual API/versioning/budget preferences through verified pack fields or explicit
advisory inputs, without personal-home parsing. A 12/18 complexity suggestion, 3x
growth guess or 90-day sunset is not universal policy. Tool availability/version,
actual workload and supported consumers decide; missing facts stay unknown.
Offer three alternatives when viable, not three artificial designs.

Six advisory dimensions remain decisions, contracts, complexity, NFRs, consumer
impact and alternatives. No score clears missing mandatory evidence or independent
review. Dormant `ta-arch-drift-warn`, `ta-contract-collision-warn` and
`ta-complexity-budget-warn` stay opt-in; presence is not enforcement.

TA supplies selected evidence to DA/SC/DH/TQ. Verify original IDs/profile and cold
checkpoint state through the shared procedure. A completed design is not deployment,
task completion or permission to ship.
