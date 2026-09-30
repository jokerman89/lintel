---
name: ta
layer: foundation
workflow_root: true
description: Use for technical-architecture depth — service boundaries, API contracts, dependency graphs, scaling plans, complexity audits, and quality attributes. Reach for it when a design needs architectural rigor beyond what PLAN gives. Runs full, loop, or single-capability, dispatching to the architecture agents and scoring against a rubric.
color: amber
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Architecturally-deep work proceeds with no ADRs, no locked/versioned interface contracts, and no complexity-budget or non-functional checks; boundary drift and breaking changes reach consumers undetected."
navigation:
  primary_intent: produce architecture-grade decisions and contracts when work has architectural depth
  triggers:
    - new service / API design / dependency restructure / cross-system boundary
    - operator types /li:ta {full|loop|single --action <name>}
    - active BUILD workflow requests architectural depth
  sibling_workflows:
    - /li:da — data architecture
    - /li:sc — security and compliance
    - /li:dh — hosting and operations
    - /li:tq — testing and QA
    - /li:full-engineering-pass — composes all 5 modules in DAG order
  risk_level: medium
  auto_mode_eligible: false
  estimated_tokens: 80000
domain:
  preferences_root: engineering.tech_architecture.*
  granularities: [full, loop, single]
  checkpoints:
    - discovery_complete: all dependencies mapped and all consumers identified
    - decision_documented: ADR drafted with alternatives + trade-offs
    - contract_locked: versioned interface and required consumer transition evidence
    - complexity_within_budget: actual measurements meet applicable agreed budgets
    - non_functionals_specified: latency + throughput + error rate declared
  recovery:
    - on_failure: preserve the failed attempt, verify evidence, and reconcile the unmet checkpoint
  continuation:
    - after_fix: verify saved evidence and select the unmet checkpoint
  raise_help:
    - new_dependency_tree_shake_reveals_unknown_service: operator confirms scope
    - material_alternatives_unresolved: decision owner selects with grounded trade-offs
    - active_consumer_break: agree the migration before changing its contract
---

# Technical architecture

## What this module does

Produces architecture-grade decisions and contracts when work has architectural depth. Three granularities — full pass for new projects, loop iteration for refinement, single action for targeted ops.

For invariant/topology choices, failure isolation, tail-latency composition and capacity
assumptions, read [architecture decision methods](references/decision-methods.md).

| Entry | When | Outputs |
|---|---|---|
| `/li:ta full` | new project / major scope change | `system-arch.md` + ADR set + interface contracts + dependency graph + non-functional requirements |
| `/li:ta loop` | mid-cycle architecture iteration | revised ADRs + diff against prior decisions + impact analysis |
| `/li:ta <capability>` · `/li:ta single --action <capability>` | targeted operation (see Sub-capability dispatch) | one artifact per the dispatch table below |

## When to use

- New service, API, dependency restructure, cross-system boundary
- Operator wants explicit architectural decisions documented as ADRs
- The active workflow explicitly requests architectural depth; no automatic hook dispatch is implied
- Work requires architecture-grade artifacts

## When NOT to use

- Bug fix, small refactor, single-file change → use `/li:cycle --mode hotfix`
- Data-model work without architectural impact → use `/li:da`
- Pure observability/deployment work → use `/li:dh`

## Sub-capability dispatch

The seven capabilities remain direct entry points, not separate skills. Read the
named role from the trusted source and use the actual host's delegation operation
or an explicit serial handoff. The caller persists returned artifacts under the
selected attempt through the shared procedure required in Workflow below.

| Capability | Dispatches to (agents) | Produces | Raise-help / notes |
|---|---|---|---|
| `api-design` | APIDesigner | REST/GraphQL/gRPC interface spec with versioning + breaking-change analysis | prefs: `api_style`, `versioning`; validation checklist below |
| `dependency-graph` | Explorer + Architect | module dependency map + `graph.dot`, circular-detection, layering audit | use project manifest clues below; distinguish static edges from observed runtime dependencies |
| `boundary-review` | BackendArchitect + Architect | bounded-context drift and failure-isolation report | reuse dependency evidence only when its relevant input identity is unchanged; request SystemArchitect explicitly for an invariant/NFR question |
| `complexity-audit` | Architect | per-component cyclomatic + cognitive scoring and refactor options | obtain actual project budgets or label exploratory measurements advisory; report tool/version and excluded files |
| `scaling-plan` | CapacityPlanner + BackendArchitect | capacity model, ranked bottlenecks and priced/qualitative projection | target and baseline come from the brief; missing measurements remain unknown, not default 3x growth |
| `contract-collision` | APIDesigner + Architect | impact across actual consumer versions and migration options | requires named interface/change; even one mandatory consumer break needs a decision; no universal deprecation window |
| `quality-attributes` | SystemArchitect + Architect | non-functional requirement spec + verification path per NFR | backs the `non_functionals_specified` checkpoint; dims: latency p50/p95/p99 per journey, throughput RPS, error-rate %, availability SLA, observability signals per component |

### api-design — invariant and consumer checks

- [ ] Name the invariant, authoritative writer and transaction boundary before choosing endpoints or topology.
- [ ] Define method/path, request/response/error schema and allowed state transitions in the applicable OpenAPI/Protobuf/SDL contract.
- [ ] Check actual consumer versions and migration needs even for a first-version or nominally additive change.
- [ ] Bind authentication and object/tenant authorization to the protected action, not merely a noted mechanism.
- [ ] Define idempotency, end-to-end deadlines, retry ownership and overload/quota behavior from actual requirements.
- [ ] Give representative payloads and observable failure cases for duplicate effects, partial completion and consumer compatibility.

### complexity-audit — available analysis

Inspect project manifests and installed analyzer documentation/version before
selecting a command. Use only an available, authorized analyzer with a metric and
language scope that answer the question; do not install a guessed tool or invoke
a package-fetching runner by default. Record command, version, exclusions and the
applicable budget. Missing analyzer/output is unverified; source inspection may
support an explicitly advisory assessment, not measured complexity.

### dependency-graph — project manifest clues

`package.json` → node · `go.mod` → go · `Cargo.toml` → rust ·
`pyproject.toml`/`requirements.txt` → python · `pom.xml`/`build.gradle` → jvm · `*.csproj`/`*.sln` → dotnet

## Workflow

Read and execute the [shared module caller procedure](../full-engineering-pass/references/domain-handoff.md#module-caller-procedure)
before domain work. It is the sole owner of original work/package/leaf admission,
live P07/policy checks, immutable obligations, checkpoint publication, cold continuation
and final QA/independent acceptance. Apply the following architecture method inside
that procedure, not as a substitute for it.

1. Select `full`, an explicitly saved `loop`, or one named capability/`single --action`.
   Unknown capability or absent saved iteration is NEEDS_CONTEXT, not a new guessed run.
2. Start from the observable invariant and its writer/transaction/retry boundaries.
   Trace dependencies and consumers before choosing topology. Preserve existing API
   style/framework, accepted ADRs and verified `engineering.tech_architecture.*`
   preferences; explicit invocation advice does not replace policy.
3. Use the capability and checkpoint tables to compare alternatives, failure
   isolation, deadlines, capacity assumptions and consumer transitions. Explorer
   locates; Architect synthesizes/designs; independent reviewers assess, not repair.
   Missing measurements remain unverified, not invented budget compliance.

## Checkpoint ownership

| Checkpoint | Method and receiver | Artifact and observable acceptance |
|---|---|---|
| `discovery_complete` | Explorer evidence lookup, then Architect dependency synthesis | dependency graph + consumer registry; distinguish observed edges, dynamic unknowns and intentional cycles |
| `decision_documented` | Architect/BackendArchitect options; ADRDrafter proposed record | viable alternatives, invariant, decision owner and downside; proposed is not accepted |
| `contract_locked` | APIDesigner contract, actual consumer-version verification | OpenAPI/SDL/protobuf + migration/notification evidence where required; additive is consumer-specific |
| `complexity_within_budget` | Architect interprets actual analyzer output | measured scope/tool, applicable budget and bounded refactor recommendation; no metric-only rewrite |
| `non_functionals_specified` | SystemArchitect constraints, Architect fit | NFR/invariant spec with source, workload, boundary and verification path; no sum of component p99s |

For `loop`, compare the selected prior ADRs/contracts and changed dependencies; retain
old artifacts and revisit affected checkpoints with new input identity. Returning
to a checkpoint never restores source files. For single API design, do not perform
a capacity sweep unless its unresolved requirement truly depends on it.

### Advisory six-dimensional rubric

```
| Dimension | Score 0-100 |
|---|---|
| Decisions documented (ADR coverage) | <D1> |
| Contracts locked (interfaces signed + versioned) | <D2> |
| Complexity within budget | <D3> |
| Non-functionals specified | <D4> |
| Consumer impact analyzed | <D5> |
| Alternatives considered | <D6> |

Record each score's evidence and untested coverage. Any applicable mandatory
failure/error/unverified control blocks regardless of scores or operator preference.
```

Use the observable checkpoint criteria above, citing the actual artifact and missing
evidence. A checklist count alone is not calibrated architectural quality.

### Handoff and recovery

Return named architecture artifacts, exact original work/profile/attempt references,
control/evidence links, advisory scores, limitations and next owner. Use the shared
start/result publication and cold-continuation table. Interrupted/failed output stays
visible. An audit record is optional observation unless policy explicitly requires it;
then verify real persistence without claiming it grants acceptance.

## Reusable patterns

Follow the [reusable pattern consumer contract](../pattern/references/consumer-contract.md).
Module entry resolves the architecture expectations bound to the current target context and
passes each sub-capability only its projected clauses (`project` for the mapped package, or the
clauses mapped to it). An unknown deployment target or platform yields `needs-context` and
blocks the dependent design; no live cloud, tenant or environment discovery is implied, and
requirements are never inferred from generic recommendations. When the runtime reports no
patterns, the module is unchanged.

## Status protocol

- **DONE** — selected results, required checks and independent acceptance complete
- **DONE_WITH_CONCERNS** — required gates pass; remaining concerns are advisory only
- **BLOCKED** — required checkpoint/evidence/policy/review failed or unavailable
- **NEEDS_CONTEXT** — unknown capability for single, OR no prior state for loop

## Integration

**Reads:**
- Original mapped artifacts and pinned pack fields; explicit advisory inputs, no automatic personal preference read
- `lib/pack-resolver.sh` for pack policy
- Architecture roles: Architect, BackendArchitect, APIDesigner, SystemArchitect, CapacityPlanner
- Existing ADRs in the repository's declared decision location

**Writes:**
- Selected `system-arch.md`, interface/ADR/NFR artifacts and iteration comparison;
  runtime start/result files under `.claude/runtime/state/domains/<operation>/iNNNN/`.
- Existing `state/ta/` artifacts remain usable only when explicitly selected and verified.
- Brief Forge only when explicitly invoked/configured; no automatic hook activation

**Triggered by:**
- Operator: `/li:ta {full|loop|single --action <name>}`
- BUILD phase: invokes as sub-module when architectural intent detected
- `/li:full-engineering-pass`: first module in the composition DAG

**Hooks** (dormant by decision, ADR-0008 — ship in `hooks/shared/` but are opt-in, not auto-registered):
- `hooks/shared/ta-arch-drift-warn/` (pre-edit on ADR-claimed files)
- `hooks/shared/ta-contract-collision-warn/` (pre-edit on interface files)
- `hooks/shared/ta-complexity-budget-warn/` (pre-commit)

These optional warnings are unobserved unless actual host registration and execution
are evidenced. They neither supply architectural measurements nor clear a required gate.

## Anti-patterns

- **Skipping single granularity to "be safe"** — single is the operator's explicit choice; honor it
- **Treating checkpoint failure as terminal** — checkpoints surface, recover, continue
- **Inventing new agents when existing ones cover** — Architect/BackendArchitect/APIDesigner cover most TA work; new agents only for genuinely new capability
- **Hardcoding api_style / versioning** — use actual verified pack fields or explicit advisory inputs
- **Silent score-below-threshold** — surface to operator with dimension breakdown; never auto-pass
- **Confusing a warn-hook with policy** — advisory warnings are not enforced controls;
  applicable mandatory requirements still block independently of the warning mechanism
