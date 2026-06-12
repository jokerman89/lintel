# Full engineering pass — the v4.x composition

**Last updated:** 2026-06-02 (v4.6, v4.x feature-complete)
**Status:** Concept doc — referenced by `skills/full-engineering-pass/SKILL.md`

> The 5 engineering-domain modules (TA, DA, SC, DH, TQ) shipped one at a time across v4.1-v4.5. Each module runs standalone for targeted depth. The **full-engineering-pass** is the composition: a single invocation orchestrates all 5 in DAG order (TA → DA‖SC → DH → TQ) and produces the complete engineering artifact set for a customer engagement or major release. **This is the final v4.x ship event — v4.x is feature-complete with v4.6.**

## The problem

5 modules ship as standalone workflows — operators can invoke `/li:ta full` for architecture-only work, `/li:dh full` for ops-only work, etc. That's the right shape for routine depth.

But high-stakes engagements (new service production-ready, customer audit prep, major release) need **all 5 modules in coordinated DAG order**. Pre-v4.6, the operator had to run each module manually, in the right order, with manual handoffs. Three failure modes:

1. **Wrong order** — operator runs DH before TA, DH can't read scaling-plan, produces qualitative-only cost projection
2. **Missed handoffs** — TQ runs without reading SC threat-model, chaos scenarios don't validate security-incident response
3. **Aggregate score invisible** — 5 individual scores; no per-engagement view of overall engineering health

The full-engineering-pass fixes all three by being **the single orchestration**.

## The DAG

```
Stage 1: TA (architecture decisions first; everything depends on these)
  ↓
  ↓ produces: system-arch + ADRs + contracts + dependency graph + NFRs
  ↓
Stage 2: DA  ‖  SC   (parallel — independent concerns at this layer)
  │            │
  │            └─ produces: threat-model + secrets + auth + compliance + audit-path + runbook
  │
  └─ produces: data-model + schema + migration + retention + query patterns + sharding + analytics
  ↓
  ↓ DA + SC both complete (synchronization point)
  ↓
Stage 3: DH (reads TA scaling-plan, DA migration-plan, SC threat-model + audit-path)
  ↓
  ↓ produces: deployment plan + observability + SLI/SLO + cost projection + rollback + on-call
  ↓
Stage 4: TQ (reads everything above; validates the assertions)
  ↓
  ↓ produces: coverage + perf budget + contract tests + regression suite + chaos plan + flaky quarantine + test pyramid
  ↓
SHIP gate: aggregate 30-dim score (6 dims × 5 modules)
```

## Why this DAG

### Stage 1 alone: TA

Architecture decisions constrain every downstream choice. Schema design (DA) depends on data-model boundary from architecture. Auth flow (SC) depends on API design. Deployment pattern (DH) depends on scaling-plan. Test pyramid (TQ) depends on component boundaries.

Without TA going first, every downstream module operates on incomplete inputs.

### Stage 2 parallel: DA ‖ SC

Data design and security posture are **independent concerns at this layer**:
- DA reasons about: schemas, migrations, retention, query patterns
- SC reasons about: threats, secrets, auth, compliance, audit

Neither needs the other's mid-flight state. Both consume TA's output (architecture + contracts). Running them in parallel halves wall-clock time for this stage.

(Implementation note: v4.6 ships sequential-within-parallel-stage. Phase 5+ may upgrade to subagent fan-out for actual concurrency.)

### Stage 3 after: DH

DH reads outputs from all three prior modules:
- TA scaling-plan → cost projection, capacity headroom
- DA migration-plan → deployment-pattern selection (zero-downtime migration constrains blue-green vs canary)
- SC threat-model → on-call playbook security overlap
- SC audit-path → observability event coverage

Running DH before DA + SC means DH operates on TA-only context, missing data + security implications.

### Stage 4 last: TQ

TQ validates everything the prior 4 modules asserted:
- TA contracts → contract tests (consumer-driven, version compatibility)
- DA query patterns → coverage of hot paths
- SC threat model → chaos scenarios (failure injection mapped to threats)
- DH SLO → perf budget alignment (budget tighter than SLO)

TQ runs last because it consumes everything above. Running TQ earlier means validating assertions that haven't been made yet.

## Aggregate scoring

Each module ships its own 6-dimensional scoring rubric (per `docs/concepts/engineering-modules.md`). Full-engineering-pass aggregates to **30 dimensions across 5 modules**:

| Module | Dimensions |
|---|---|
| TA | Decisions documented, Contracts locked, Complexity within budget, Non-functionals specified, Consumer impact analyzed, Alternatives considered |
| DA | Data model completeness, Schema locked, Migration safety, Retention specified, Query patterns documented, Consumer impact analyzed |
| SC | Threat model coverage, Mitigations declared, Secrets inventoried + rotation, Auth flow review verdict, Compliance evidence, Audit path verified |
| DH | Deployment + rollback locked, Observability instrumentation, SLI/SLO definitions, Cost projection, Capacity headroom, On-call playbook |
| TQ | Critical-path coverage, Perf budgets locked, Contract tests complete, Regression suite curated, Chaos scenarios documented, Test pyramid healthy |

**SHIP gate:** per-module score ≥ 80 AND aggregate ≥ 80. Either condition failed → SHIP verdict YELLOW or RED.

## Graceful degradation

v4.x has stacking-rollout windows where some module PRs are open and some merged. The composition handles partial state:

1. Scans `skills/` for which of `ta/`, `da/`, `sc/`, `dh/`, `tq/` exist
2. Surfaces missing modules to operator before running
3. Asks confirmation to proceed with partial pass
4. Runs available modules in DAG order, skipping missing ones (audit logs the gap)
5. SHIP verdict YELLOW even with full pass if modules were skipped (operator can override)

When all 5 are present on main, composition runs the full DAG. During v4.6 rollout window (this PR stacks on v4.5 which stacks on v4.4 which stacks on v4.3), composition gracefully handles partial state.

## Resume semantics

The composition saves stage-by-stage state to `.claude/runtime/state/full-engineering-pass/00-state.md`. After interruption (operator pause, network failure, pre-checkpoint review), `/li:full-engineering-pass --resume` continues from the last-completed stage.

This is critical because the composition is expensive: 500k tokens soft cap, 750k hard cap. Re-running from scratch wastes prior module output.

## Cap + cost

Token budget per design doc §5.2: 5 modules × ~80k = 400k. Plus overhead (cross-module brief forge handoffs, aggregate scoring) = ~500k soft cap. Hard cap 750k accommodates re-runs of low-score checkpoints.

For pack-specific overrides:
- `_default`: 500k / 750k
- `ms-internal`: same
- `caip-se`: 750k / 1000k (customer-engagement-deep mode allowance)

Operator sees projected cost before Stage 1 starts.

## Cross-module Brief Forge handoffs

Between stages, Brief Forge emits a `phase_transition` envelope. Each handoff:
- Carries the completed module's output paths
- Runs evaluators per pack policy (security + sdl_compliance + completeness)
- Surfaces gaps before the next module starts

This means each module's input is validated; if the prior module produced low-completeness output, the next module gets the warning + can choose to refine first.

## What this enables

Customer engagement workflow:

```
operator: /li:cycle --mode customer-engagement
  → SENSE detects deep scope
  → SENSE recommends /li:full-engineering-pass
operator: /li:full-engineering-pass
  → Stage 1: TA runs (architecture artifacts produced)
  → operator inspects, optionally re-loops
  → Stage 2: DA + SC run (data + security)
  → operator inspects
  → Stage 3: DH runs (deployment + ops)
  → Stage 4: TQ runs (validation)
  → composition report: aggregate score + module breakdown
  → SHIP gate
operator: /li:ship
  → caip-se pack adds Trailblazer voice to customer-facing artifacts
  → deliverable package ready
```

Five modules + composition + customer-engagement mode + caip-se pack = the operator runs one command + decides at gates. Everything else is mechanical.

## Anti-patterns

- **Running composition for hotfix-shaped work** — use `/li:cycle --mode hotfix`
- **Skipping TA** — no module operates correctly without TA's architecture decisions
- **Treating aggregate score as the only signal** — per-module dimension breakdown is the actionable view
- **Hardcoding module list** — composition reads available modules from filesystem (handles v4.x stacking-rollout)
- **Skipping the resume mechanism** — re-running 500k tokens wastes operator + cost
- **Running parallel-stage modules with shared mid-flight state** — DA + SC must be independent within Stage 2

## What this closes

With v4.6 shipping (this composition skill), **v4.x is feature-complete**:

- v4.0: harness with packs + orientator + Brief Forge + wiki
- v4.1: TA (tech-architecture) — first engineering-domain module
- v4.2: DA (data-architecture)
- v4.3: SC (security-compliance)
- v4.4: DH (devops-hosting)
- v4.5: TQ (testing-qa) — final engineering-domain module
- **v4.6: full-engineering-pass — composition skill that runs all 5 in DAG order**

Per design doc §5.2 total estimate: 17-27 CC-days for v4.0 ship + ~10-15 CC-days for engineering-depth = ~30-40 CC-days for complete v4.x.

What remains after v4.6 is operational: pack-specific tuning, additional module capabilities as operator needs surface, future v5.x design decisions.

## Integration points

**Reads:**
- All 5 module SKILL.md files (or as-many-as-exist for graceful degradation)
- `lib/pack-resolver.sh` for pack policy
- `~/.lintel/profile.yaml` `engineering.*` block
- All 5 modules' state directories (`.claude/runtime/state/{ta,da,sc,dh,tq}/`) for cross-module brief handoffs

**Writes:**
- `.claude/runtime/state/full-engineering-pass/composition-report-<ts>.md`
- `.claude/runtime/state/full-engineering-pass/00-state.md` (resume state)
- `.claude/runtime/audit/full-engineering-pass.jsonl`
- Brief Forge `phase_transition` envelopes between stages

**Tested by:**
- `tests/shape/full-engineering-pass-contract.sh`
- `tests/unit/full-engineering-pass-dag.sh`
