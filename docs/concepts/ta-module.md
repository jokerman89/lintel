# TA module — tech-architecture for engineering depth

**Last updated:** 2026-05-30 (v4.1)
**Status:** Concept doc — referenced by `skills/ta/SKILL.md` + 7 Capabilities + 2 agents + 3 hooks

> When work has architectural depth — new service, API redesign, dependency restructure, cross-system boundary — running it through plain BUILD discards what the operator needs: explicit decisions, locked contracts, complexity discipline, non-functional requirements. The TA module is the **first engineering-domain module in v4.1+**, producing architecture-grade artifacts with checkpoint discipline and recovery. It is the canonical example of the engineering-modules pattern documented in [engineering-modules.md](engineering-modules.md).

## The problem

Pre-v4.1, architectural work happened through ad-hoc invocations:
- `/li:adr-draft` for individual decisions (no orchestration)
- BackendArchitect spawned manually when operator remembered
- Complexity audits via language-specific tools, not aggregated
- Non-functional requirements often left to memory

The user explicitly named this gap when defining engineering depth: "When work has architectural depth ... invoke TA to produce architecture-grade decisions and contracts."

The module fixes it with three granularities — `full`, `loop`, `single` — and 5 checkpoints with recovery.

## The model

```
Operator invocation
       │
       ▼
/li:ta {full|loop|single --action <name>}
       │
       │  Read pack policy + profile.engineering.tech_architecture.*
       ▼
Granularity dispatch:
       │
       ├── full   → discovery_complete → decision_documented → contract_locked
       │           → complexity_within_budget → non_functionals_specified
       │           → 6-dim scoring rubric → SHIP (score ≥80) or surface
       │
       ├── loop   → re-run discovery + decision + contract → diff vs prior iteration
       │
       └── single → direct Capability (no checkpoints, no orchestration)
                   api-design / dependency-graph / complexity-audit /
                   boundary-review / scaling-plan / contract-collision /
                   quality-attributes
                       │
                       ▼
                   Spawn agent via Brief Forge:
                   APIDesigner / Architect / BackendArchitect /
                   SystemArchitect (NEW) / CapacityPlanner (NEW)
                       │
                       ▼
                   Output → .claude/runtime/state/ta/<action>-<ts>.md
                   Audit → .claude/runtime/audit/ta-decisions.jsonl
```

Three granularities; one shape; per-action dispatch through existing-where-possible / new-where-needed agents.

## The five checkpoints (full pass)

### 1. `discovery_complete`

All dependencies mapped, all consumers identified. Produced by `dependency-graph` + `contract-collision` (consumer side).

Pass criterion: dependency graph has 0 cycles, consumer registry is non-stale.

Failure recovery: if raise-help trigger fires (unknown service surfaced), AskUserQuestion: A) Re-loop with operator-provided context / B) Accept-with-concern / C) Raise-help.

### 2. `decision_documented`

ADR drafted with alternatives + trade-offs. Produced by `api-design` (if interface decisions involved) + ADRDrafter agent.

Pass criterion: at least one ADR per architectural decision; each ADR has 2+ alternatives with documented trade-offs.

Failure recovery: if ADR alternatives all score within 5% (per design doc raise-help), surface to operator to pick.

### 3. `contract_locked`

Interface signed, versioned, consumers notified. Produced by `api-design` (interface spec) + `contract-collision` (notification path).

Pass criterion: interface has version tag; if breaking change, migration plan exists; if ≥3 consumers break, raise-help triggered.

Failure recovery: re-spawn APIDesigner with operator's clarification, or document migration timeline.

### 4. `complexity_within_budget`

Cyclomatic + cognitive complexity below profile thresholds. Produced by `complexity-audit`.

Pass criterion: verdict GREEN (0 components over) or YELLOW with operator acceptance.

Failure recovery: Architect refactor recommendations spawned; operator picks accept or refactor.

### 5. `non_functionals_specified`

Latency + throughput + error rate + availability + observability declared. Produced by `quality-attributes` via SystemArchitect.

Pass criterion: all 5 NFR dimensions specified per critical journey; each NFR has verification approach.

Failure recovery: re-spawn SystemArchitect with operator-provided context (typically the gap is operator-side, not agent-side).

## The 6-dimensional scoring rubric (full pass exit gate)

Mirrors `frontend-design-review`'s pattern. Every dimension scored 0-100 by reading the produced artifact against a checklist.

| Dimension | Score 0-100 | Pass threshold | Source artifact |
|---|---|---|---|
| Decisions documented (ADR coverage) | _ | 80 | `.claude/runtime/state/ta/iteration-N-adrs.md` |
| Contracts locked (interfaces signed + versioned) | _ | 80 | `.claude/runtime/state/ta/api-design-<ts>.md` + version metadata |
| Complexity within budget | _ | 80 | `.claude/runtime/state/ta/complexity-audit-<ts>.md` verdict |
| Non-functionals specified | _ | 80 | `.claude/runtime/state/ta/quality-attributes-<ts>.md` |
| Consumer impact analyzed | _ | 80 | `.claude/runtime/state/ta/contract-collision-<ts>.md` |
| Alternatives considered | _ | 80 | ADRs have 2+ alternatives per decision |

Full-pass exit gate: every dimension ≥ 80 OR explicit operator override (audited to `ta-decisions.jsonl` with operator reason).

`/li:ta loop` exit gate: target dimension(s) improved vs prior iteration OR re-loop.

## Capability catalog

| Capability | Primary agent | Other agents | Output |
|---|---|---|---|
| `api-design` | APIDesigner | — | API spec (REST/GraphQL/gRPC) with versioning |
| `dependency-graph` | Explorer | Architect | dependency graph + cycle/layering report |
| `complexity-audit` | Architect | CodeReviewer | per-component complexity scoring |
| `boundary-review` | BackendArchitect | Architect | bounded-context leak report |
| `scaling-plan` | CapacityPlanner (NEW) | BackendArchitect | capacity model + bottlenecks + cost |
| `contract-collision` | APIDesigner | Architect | consumer breakage assessment + migration |
| `quality-attributes` | SystemArchitect (NEW) | Architect | NFR spec + verification approach |

L-002 inventory: 5 of 7 Capabilities dispatch to existing agents. Only 2 new agents (SystemArchitect, CapacityPlanner) for genuinely new capability.

## Agent additions (v4.1)

### `SystemArchitect`
- **Purpose:** system-of-systems thinking — NFRs, cross-system invariants, emergent properties
- **Why new:** existing agents (Architect, BackendArchitect) are component-level; SystemArchitect is system-level
- **Spawned by:** `quality-attributes`, `boundary-review`

### `CapacityPlanner`
- **Purpose:** capacity modeling + bottleneck identification + cost projection
- **Why new:** existing perf-adjacent agents (LatencyAnalyzer) focus on observed perf, not projected capacity
- **Spawned by:** `scaling-plan`

## Hook additions (v4.1)

All three are warn-only (per engineering-modules.md pattern):

### `ta-arch-drift-warn`
Pre-edit on files claimed by an ADR's `decisions:` block. Surfaces: "this file is claimed by ADR-X; consider updating the ADR if revising the decision."

### `ta-contract-collision-warn`
Pre-edit on files matching `pack.tech_architecture.interface_glob` or appearing in `.claude/runtime/state/ta/consumer-registry.json`. Surfaces: "$N consumers registered; consider `/li:ta single --action contract-collision`."

### `ta-complexity-budget-warn`
Pre-commit (or post-edit when integrated). Surfaces: "cyclomatic=$N (budget $M); consider `/li:ta single --action complexity-audit`."

## Profile preferences

Under `engineering.tech_architecture.*` in `~/.lintel/profile.yaml`:

```yaml
engineering:
  tech_architecture:
    api_style: rest                      # rest | graphql | grpc | mixed
    versioning: semver-major-uri         # semver-major-uri | accept-header | none
    complexity_budget_cyclomatic: 12
    complexity_budget_cognitive: 18
    require_adr_on:
      - new_dependency
      - new_service
      - breaking_api_change
    architectural_review_required_above_loc: 500
    deprecation_window_days: 90
```

Hooks + Capabilities read these. Defaults baked in when not set (cyclomatic 12, cognitive 18).

## Pack overrides

Packs can declare `tech_architecture.*` overrides:

```yaml
# packs/some-pack/pack.yaml
tech_architecture:
  interface_glob: "**/*.proto,**/openapi/**/*.yaml"
  external_consumer_registries:
    - https://internal.registry/api-consumers
```

Per design doc: pack overrides allow domain-specific tuning without per-operator profile edits.

## Audit trail

Every module + Capability + checkpoint writes to `.claude/runtime/audit/ta-decisions.jsonl`:

```jsonl
{"ts":"...","kind":"ta_module_complete","granularity":"full","score":87,"checkpoints_passed":5}
{"ts":"...","kind":"ta_api_design","api_style":"rest","versioning":"semver-major-uri"}
{"ts":"...","kind":"ta_complexity_audit","language":"go","over_cyclomatic":2,"over_cognitive":1,"verdict":"YELLOW"}
{"ts":"...","kind":"ta_contract_collision","consumers":7,"breaking":2,"raise_help":false}
```

Operators inspect via `bin/li-doctor --module ta` (Phase 4 tool when shipped).

## Composition — TA as first module in full engineering pass

Per engineering-modules.md §"Composition":

```
TA (this module)
  │
  ├── DA  ┐  (parallel — independent concerns)
  ├── SC  ┘
  │
  ▼
DH  (deploys what TA+DA+SC produced)
  │
  ▼
TQ  (validates everything end-to-end)
```

TA goes first because architectural decisions constrain everything downstream. DA + SC can run in parallel because data and security are independent concerns at this level.

## Anti-patterns

- **Running `single` granularity for everything to avoid checkpoint discipline** — checkpoints exist for a reason; use full for new work
- **Skipping the NFR checkpoint** — full-pass exit requires it; without NFRs, the architecture is unfinished
- **Treating hook warnings as blocking** — hooks warn; blocking is operator's explicit decision via override or pack policy
- **Inventing new agents when existing cover** — L-002 inventory pre-PR; SystemArchitect + CapacityPlanner are the only v4.1 additions because they cover genuinely new capability
- **Curating architectural patterns in Capabilities** — Capabilities are dispatch contracts (L-001); patterns come from agents at invocation
- **Hardcoding complexity budgets** — read from profile; defaults are starting points, not rules

## Integration points

**Reads:**
- `~/.lintel/profile.yaml` `engineering.tech_architecture.*`
- `lib/pack-resolver.sh` for pack policy
- Existing arch agents + 2 new agents
- ADR locations (`.claude/decisions/` canonical; legacy `docs/decisions/`, `docs/adr/`)

**Writes:**
- `.claude/runtime/state/ta/*.md` (per-action artifacts)
- `.claude/runtime/audit/ta-decisions.jsonl`
- Brief Forge envelopes through the standard gate

**Triggered by:**
- Operator: `/li:ta {full|loop|single --action <name>}`
- BUILD phase: invokes as sub-module when architectural intent detected
- `/li:full-engineering-pass` (when composition skill ships in v4.x): first module in DAG

**Tested by:**
- `tests/shape/ta-module-contract.sh` (engineering-module-contract for TA)
- `tests/unit/ta-routing.sh` (granularity dispatch + Capability enumeration)
