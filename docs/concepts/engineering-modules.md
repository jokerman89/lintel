# Engineering modules — the v4.1+ pattern

**Last updated:** 2026-05-30 (v4.1 alpha)
**Status:** Concept doc — referenced by `skills/ta/SKILL.md` (TA, v4.1), and future `skills/da/` (DA), `skills/sc/` (SC), `skills/dh/` (DH), `skills/tq/` (TQ)

> Real engineering work has depth that the 9-step cycle alone doesn't capture. A new service needs architectural decisions; a new datastore needs schema work; a customer engagement needs compliance plumbing; a production rollout needs deployment + observability; a critical path needs test coverage. v4.0 ships the harness; v4.1+ ships the depth as **engineering domain modules** — workflow_root skills that operators can invoke standalone, call from inside BUILD as sub-modules, or compose into a "full engineering pass."

## The problem

Pre-v4.0, BUILD was a single phase. Operators with architectural depth (new microservice, schema-breaking migration, security-bound feature) had three bad options:

1. **Cram it into BUILD** — TDD discipline good, architectural reasoning bad. The 9-step cycle assumes the architecture is known going in.
2. **Drop to ad-hoc skills** — `/li:adr-draft`, `/li:api-review` exist scattered, no orchestration, no checkpoints, no recovery.
3. **Skip the depth** — ship shallow, regret later.

The user explicitly flagged this as "VERY important" — five domains where depth matters and the harness should match:

| Domain | When matters | Module name | v4.x ship |
|---|---|---|---|
| Tech architecture | new service, API, dependency restructure | `tech-architecture` (TA) | v4.1 (this one) |
| Data architecture | new schema, migration, analytics | `data-architecture` (DA) | v4.2 |
| Security + compliance | customer-bound, regulated, secrets | `security-compliance` (SC) | v4.3 |
| DevOps + hosting | production rollout, observability, cost | `devops-hosting` (DH) | v4.4 |
| Testing + QA | critical-path coverage, perf, contract tests | `testing-qa` (TQ) | v4.5 |

The module pattern is the **uniform shape every one of these takes**.

## The model

```
Operator invocation (one of three granularities)
       │
       ▼
Module workflow_root skill (e.g. skills/ta/SKILL.md)
       │
       │  Reads pack policy + operator preferences (engineering.<domain>.*)
       │
       ▼
Granularity dispatch:
       │  full   → multi-phase loop with checkpoints + recovery
       │  loop   → one iteration of the domain's iteration loop
       │  single → one targeted operation (e.g., "review API contract")
       │
       ▼
Capabilities (per-action workflows)
       │
       ▼
Agents (mostly existing 83, augmented as needed)
       │
       ▼
Hooks (domain-specific gates: ta-arch-drift-warn, ta-complexity-budget-warn, etc.)
       │
       ▼
Scoring rubric (6-dimensional, mirrors frontend-design-review)
       │
       ▼
Output: domain-specific artifact (system-arch.md, data-model.md, etc.)
       + audit entries
       + Brief Forge envelopes for hand-offs
```

Three granularities per module. Five default modules. Same shape; different domain.

## The three granularities

### `full`

The whole domain pass. Multi-phase loop with explicit checkpoints. Used when the work IS the domain (new microservice → full TA pass; new datastore → full DA pass).

Example:
```
/li:ta full
  → ta-discovery (map dependencies + consumers)
  → ta-decision-loop (ADR draft + alternatives + scoring)
  → ta-contract-lock (interface + versioning + consumer notification)
  → complexity-audit (cyclomatic + cognitive scoring)
  → ta-nfr-spec (latency + throughput + error rate)
  → SHIP gate: scoring rubric ≥ 80
```

Each checkpoint can fail. Recovery is documented per module.

### `loop`

One iteration of the domain's iteration loop. Used when the domain work is already in progress and the operator wants to push it one cycle further.

Example: `/li:ta loop` — re-runs the discovery + decision + contract checkpoints, surfaces deltas against the prior iteration's ADRs, produces diff + impact analysis.

### `single`

One targeted operation, no orchestration. Used when the operator knows exactly what they need.

Example: `/li:ta single --action api-design` — runs only `api-design`, no loop, no checkpoints.

Per design doc §3.9: "we are not the dumb tool" — operators can always go to single-action when they know better than the orchestrator.

## The contract: every module declares this shape

```yaml
name: <domain>-module
layer: foundation
workflow_root: true                    # spawns its own job
description: <domain> as a callable module — full / loop / single granularity
color: <module-color>                  # TA: amber. DA: blue. SC: red. DH: purple. TQ: green.
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
navigation:
  primary_intent: <one-line>
  triggers: [<list>]
  sibling_workflows: [<list>]
  risk_level: medium
  auto_mode_eligible: false
  estimated_tokens: 80000              # full granularity estimate
brief_forge:
  on_subagent_spawn:
    enabled: true
    evaluators: [<domain>-eval, security-eval]
  on_phase_transition:
    enabled: true
    evaluators: [completeness-eval]
domain:                                # NEW v4.1 concept
  preferences_root: engineering.<domain>.*
  granularities: [full, loop, single]
  checkpoints:
    - <name>: <pass-criterion>
  recovery:
    - on_failure: <strategy>
  continuation:
    - after_fix: <how-to-resume>
  raise_help:
    - <when>: <to-whom>
```

Every module's `SKILL.md` carries this. The shape is enforced by `tests/shape/engineering-module-contract.sh`.

## Composition — full engineering pass

Per design doc §3.8: a "full engineering pass" composes all five modules with the right ordering + parallelism.

```
Phase sequence:
  TA (architecture decisions first — everything else depends on these)
     │
     ├── DA ─┐    (data + security can run in parallel — independent concerns)
     ├── SC ─┘
     │
     ▼
  DH (deploys what TA+DA+SC produced)
     │
     ▼
  TQ (validates everything end-to-end)
```

`/li:full-engineering-pass` (Phase 4 composition skill, ships separately): orchestrates the sequence, respects pack-specific token budgets, allows operator interrupt at every module boundary.

Token budget per design doc §5.2: 5 modules × ~80k = 400k. Plus 100k overhead = 500k cap. customer-engagement-deep mode (750k/1000k cap) accommodates this.

## Capability discipline (L-001, L-002, L-004)

**L-001 (scaffolding-not-content):** Capabilities are workflow + dispatch contracts, not curated content. `api-design` is the workflow that invokes `APIDesigner` agent + writes structured output. The agent produces content at invocation. Same pattern as `generate-web`, `generate-app`, etc.

**L-002 (grep-first):** Before adding a new Capability, grep for existing skills/agents covering the need. Most TA Capabilities dispatch to existing agents (`APIDesigner`, `Architect`, `BackendArchitect`). Only two new agents this phase: `SystemArchitect` (system-of-systems thinking) + `CapacityPlanner` (scaling model).

**L-004 (decisions vs execution):** Every operator-visible decision in a module gets explicit surfacing. Checkpoint failures surface via AskUserQuestion with three paths (Re-loop / Accept-with-concern / Raise-help). No silent fallback.

## Profile preferences (per-operator domain tuning)

`~/.lintel/profile.yaml` adds an `engineering:` block:

```yaml
engineering:
  tech_architecture:
    api_style: rest
    versioning: semver-major-uri
    complexity_budget_cyclomatic: 12
    complexity_budget_cognitive: 18
    require_adr_on: [new_dependency, new_service, breaking_api_change]
    architectural_review_required_above_loc: 500
  data_architecture:
    primary_store: postgres
    migration_window: zero-downtime-required
    retention_default_days: 365
  security_compliance:
    sdl_active: true
    secret_management: keyvault
    threat_model_required_on: [new_external_dependency, new_data_path]
  devops_hosting:
    cloud: azure
    deployment_pattern: blue-green
    observability_stack: app-insights
  testing_qa:
    coverage_target: 80
    critical_path_coverage: 100
    perf_budget_p95_ms: 200
```

Modules read these via `lib/profile-reader.sh` (Phase 4 helper). Operators override per-cycle via `--pref <key>=<value>`.

## Scoring rubric pattern

Each module ships a 6-dimensional scoring rubric, mirroring `frontend-design-review`. TA's:

| Dimension | Score 0-100 | Pass threshold |
|---|---|---|
| Decisions documented (ADR coverage) | _ | 80 |
| Contracts locked (interfaces signed + versioned) | _ | 80 |
| Complexity within budget | _ | 80 |
| Non-functionals specified | _ | 80 |
| Consumer impact analyzed | _ | 80 |
| Alternatives considered | _ | 80 |

Module's `--full` exit gate: every dimension ≥ pass threshold OR explicit operator override (audited).

`--loop` exit gate: target dimension(s) improved vs prior iteration OR re-loop.

## Hook discipline

Each module ships 2-5 hooks specific to its concerns. Hooks fire on operator's normal work (pre-edit, pre-commit) and surface warnings inline — never block silently.

TA hooks:
- `ta-arch-drift-warn` (pre-edit) — file is claimed by an ADR's "decisions" block; warn if change contradicts ADR
- `ta-contract-collision-warn` (pre-edit) — file is an interface with declared consumers; warn about breaking-change risk
- `ta-complexity-budget-warn` (pre-commit) — cyclomatic exceeds threshold from preferences

All three are warn-only in v4.1; v4.2 may tighten to block based on operator feedback.

## Module color convention

Modules carry a color for visual identification in `/li:status` output:

- TA — amber (architectural, foundational)
- DA — blue (data, structured)
- SC — red (security, gating)
- DH — purple (deployment, operational)
- TQ — green (validation, complete)

Wiki gen uses these in the showcase HTML for the system map.

## What this enables

After all 5 modules ship (v4.1 through v4.5):

- Operator runs `/li:ta full` for a new microservice → produces ADRs + contracts + complexity budget + NFRs
- Operator runs `/li:full-engineering-pass` for a customer engagement → all 5 modules in DAG order
- Operator runs `/li:ta single --action api-design` mid-cycle when they just need API design help
- Pack authors override hooks per-pack (e.g., a Fintech pack adds `pci-data-flow-warn` to SC)
- Module rubrics aggregate into operator's quality dashboard via `bin/li-doctor --rubrics`

## Anti-patterns

- **Skipping the module pattern for one-off domain work** — even single-action invocations go through the module's Capability
- **Putting curated content in Capabilities** — Capabilities are dispatch contracts; content is produced by agents at invocation (L-001)
- **Adding a new agent when an existing one covers the need** — L-002 inventory pre-PR
- **Silent checkpoint failures** — every checkpoint failure surfaces AskUserQuestion with the three paths (L-004)
- **Letting hooks block** — hooks warn; blocking is the operator's explicit decision via Brief Forge or pack policy
- **Hardcoding preferences** — every domain-specific tunable goes under `engineering.<domain>.*` in profile

## Integration points

**Reads:**
- `~/.lintel/profile.yaml` `engineering.*` block
- `pack.yaml.brief_forge_handoffs.*` for module-internal hand-offs
- Existing agents in `agents/engineering/`

**Writes:**
- Module-specific artifacts under `.claude/runtime/state/<domain>/` (e.g., `.claude/runtime/state/ta/system-arch.md`)
- `.claude/runtime/audit/<domain>-decisions.jsonl`
- Brief Forge envelopes through the standard gate

**Triggered by:**
- Operator: `/li:<domain> {full|loop|single}`
- BUILD phase: invokes modules as sub-modules when SENSE detects domain-bound intent
- `/li:full-engineering-pass`: composition skill (ships separately)

**Tested by:**
- `tests/shape/engineering-module-contract.sh` (every module declares the contract)
- Per-module unit + integration tests
