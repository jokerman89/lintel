# TQ module — testing-qa for engineering depth

**Last updated:** 2026-06-02 (v4.5)
**Status:** Concept doc — referenced by `skills/tq/SKILL.md` + 7 sub-skills + 2 new agents + 3 hooks

> **Final engineering-domain module of v4.x.** When work needs quality validation — critical-path coverage, perf budgets, contract tests, regression suite, chaos validation — running it through plain BUILD discards what the operator needs: explicit coverage targets, perf budgets with regression detection, consumer-driven contract tests, curated regression suite, chaos scenarios with recovery validation. TQ closes the loop on the 5-module engineering pass.

## The problem

Pre-v4.5, quality work happened through ad-hoc:
- Coverage measured occasionally but no critical-path discipline
- Perf budgets invented at customer-engagement time
- Contract tests written only after a break
- Regression suite accumulated without curation (every bug fix added a test, no pruning)
- Chaos engineering practiced once and forgotten

The user explicitly named the gap: "When the work needs quality validation — critical-path coverage, perf budgets, contract tests — invoke TQ."

The module fixes it with three granularities — `full`, `loop`, `single` — and 5 checkpoints with recovery.

## The model

```
Operator invocation
       │
       ▼
/li:tq {full|loop|single --action <name>}
       │
       │  Read pack policy + profile.engineering.testing_qa.*
       ▼
Granularity dispatch:
       │
       ├── full   → coverage_targets_met → perf_budgets_locked
       │           → contract_tests_complete → regression_suite_curated
       │           → chaos_scenarios_documented
       │           → 6-dim scoring rubric → SHIP (score ≥80) or surface
       │
       ├── loop   → re-run coverage + perf + contracts → diff vs prior
       │
       └── single → direct sub-skill (no checkpoints, no orchestration)
                   tq-coverage-audit / tq-perf-budget-spec / tq-contract-test-design /
                   tq-regression-suite / tq-chaos-plan /
                   tq-flaky-quarantine / tq-test-pyramid-review
                       │
                       ▼
                   Spawn agent via Brief Forge:
                   TestRunner / RegressionDetective / LatencyAnalyzer /
                   APIDesigner / SecurityAuditor / SystemArchitect / Architect /
                   PerfBudgetEnforcer (NEW) / ContractTestArchitect (NEW)
                       │
                       ▼
                   Output → .claude/runtime/state/tq/<action>-<ts>.md
                   Audit → .claude/runtime/audit/tq-decisions.jsonl
```

## The five checkpoints (full pass)

### 1. `coverage_targets_met`
Critical-path coverage at threshold + branch coverage adequate. Produced by `tq-coverage-audit` + TestRunner + Architect.
Pass criterion: overall ≥ profile.coverage_target; critical paths ≥ profile.critical_path_coverage. Raise-help on critical-path below threshold.

### 2. `perf_budgets_locked`
Per-critical-journey perf budget with regression detection. Produced by `tq-perf-budget-spec` + LatencyAnalyzer + PerfBudgetEnforcer.
Pass criterion: every critical journey has p50/p95/p99 budget; regression detection thresholds set; enforcement mode chosen per criticality. Raise-help on regression above budget.

### 3. `contract_tests_complete`
Consumer + provider contract tests passing. Produced by `tq-contract-test-design` + APIDesigner + ContractTestArchitect.
Pass criterion: every active consumer covered; version compatibility matrix verified. Raise-help on active-consumer break.

### 4. `regression_suite_curated`
Golden-path tests + recent-bug-fix tests. Produced by `tq-regression-suite` + RegressionDetective + TestRunner.
Pass criterion: every golden path has at least 1 happy + 1 edge-case test; every recent fix maps to a test or has documented "impossible-to-test" reason.

### 5. `chaos_scenarios_documented`
Failure injection scenarios + recovery validation. Produced by `tq-chaos-plan` + SecurityAuditor + SystemArchitect.
Pass criterion: scenarios per high-severity threat with recovery criteria + abort conditions. Skipped (stub) when `chaos_active: false`.

## The 6-dimensional scoring rubric (full pass exit gate)

| Dimension | Score 0-100 | Pass threshold | Source artifact |
|---|---|---|---|
| Critical-path coverage at target | _ | 80 | `.claude/runtime/state/tq/coverage-audit-<ts>.md` |
| Perf budgets locked with regression detection | _ | 80 | `.claude/runtime/state/tq/perf-budget-<ts>.md` |
| Contract tests complete | _ | 80 | `.claude/runtime/state/tq/contract-test-suite-<ts>.md` |
| Regression suite curated | _ | 80 | `.claude/runtime/state/tq/regression-suite-<ts>.md` |
| Chaos scenarios documented + recovery validated | _ | 80 | `.claude/runtime/state/tq/chaos-plan-<ts>.md` |
| Test pyramid healthy | _ | 80 | `.claude/runtime/state/tq/test-pyramid-<ts>.md` |

## Sub-skill catalog

| Sub-skill | Primary agent | Other agents | Output |
|---|---|---|---|
| `tq-coverage-audit` | TestRunner | Architect | per-component coverage + critical-path verdict |
| `tq-perf-budget-spec` | LatencyAnalyzer | PerfBudgetEnforcer (NEW) | per-journey budget + regression detection |
| `tq-contract-test-design` | APIDesigner | ContractTestArchitect (NEW) | consumer-driven tests + version matrix |
| `tq-regression-suite` | RegressionDetective | TestRunner | golden-path + bug-fix tests + execution health |
| `tq-chaos-plan` | SecurityAuditor | SystemArchitect | failure scenarios + recovery criteria |
| `tq-flaky-quarantine` | TestRunner | RegressionDetective | flake list + remediation plan |
| `tq-test-pyramid-review` | Architect | TestRunner | per-kind distribution + rebalancing |

**L-002:** 5 of 7 sub-skills dispatch to existing agents (TestRunner, RegressionDetective, LatencyAnalyzer, APIDesigner, SecurityAuditor, SystemArchitect, Architect). Only 2 new agents.

## Agent additions (v4.5)

### `PerfBudgetEnforcer`
- **Purpose:** turns perf baselines into enforceable budgets with regression detection
- **Why new:** LatencyAnalyzer reports baseline; PerfBudgetEnforcer turns it into policy
- **Spawned by:** `tq-perf-budget-spec`

### `ContractTestArchitect`
- **Purpose:** consumer-driven contract test design + version compatibility matrix
- **Why new:** APIDesigner specifies the contract; ContractTestArchitect specifies how it's verified
- **Spawned by:** `tq-contract-test-design`

## Hook additions (v4.5)

All three are warn-only. Each uses unified `audit_log` from `bin/_audit.sh`.

### `tq-coverage-drop-warn`
Pre-commit on coverage drops below profile threshold.

### `tq-perf-regression-warn`
Pre-commit on edits to perf-budget-bound paths.

### `tq-contract-break-warn`
Pre-commit on provider edits without paired contract-test update.

## Profile preferences

Under `engineering.testing_qa.*` in `~/.lintel/profile.yaml`:

```yaml
engineering:
  testing_qa:
    coverage_target: 80
    critical_path_coverage: 100
    perf_budget_p95_ms: 200
    contract_test_framework: pact          # pact | consumer-driven-internal | none
    chaos_active: true
    flaky_quarantine_threshold: 3
```

Hooks + sub-skills read these. Defaults baked in when absent.

## Pack overrides

```yaml
# packs/some-pack/pack.yaml
testing_qa:
  perf_path_glob: "src/api/**/*,pkg/critical/**/*"
  provider_glob: "src/api/**/*,*.openapi.yaml"
```

## Audit trail

```jsonl
{"ts":"...","kind":"tq_module_complete","granularity":"full","score":85,"coverage_target":80}
{"ts":"...","kind":"tq_coverage_audit","language":"go","target":80,"critical_below_threshold":0}
{"ts":"...","kind":"tq_perf_budget_spec","default_p95_ms":200,"journeys":12}
{"ts":"...","kind":"tq_contract_test_design","framework":"pact","contracts":24,"breaks_active":0}
```

## Composition — TQ as final stage in full engineering pass

Per engineering-modules.md §"Composition":

```
TA
  │
  ├── DA  ┐
  ├── SC  ┘
  │
  ▼
DH
  │
  ▼
TQ   ← reads everything: TA contracts, DA hot paths, SC threats, DH SLOs
```

TQ consumes outputs from all four prior modules. It validates that the architecture decisions, data design, security posture, and ops plan actually hold up under test + perf + contract + regression + chaos pressure. Without those inputs, TQ operates on operator-provided context.

## Anti-patterns

- **Single coverage number** — critical-path coverage is the discipline
- **Perf budgets without regression detection** — declarative, not enforced
- **Provider-only contract tests** — consumer-driven catches breaks the provider didn't expect
- **Regression suite of every bug fix** — curate to actually-recurring + critical
- **Chaos without recovery validation** — every scenario validates a specific resilience claim
- **Quarantine without remediation plan** — quarantine is temporary
- **Inverted test pyramid** — slow CI, brittle, hard to debug
- **Inventing new agents when existing cover** — 5 of 7 sub-skills reuse
- **Hardcoding profile values** — coverage / perf / framework / threshold all profile-driven

## Integration points

**Reads:**
- `~/.lintel/profile.yaml` `engineering.testing_qa.*`
- `lib/pack-resolver.sh` for pack policy
- Existing agents (7) + 2 new agents
- Prior modules: TA contracts/api-design, DA query-pattern-audit, SC threat-model + audit-path, DH SLI/SLO

**Writes:**
- `.claude/runtime/state/tq/*.{md,json}` (per-action artifacts)
- `.claude/runtime/audit/tq-decisions.jsonl`
- Brief Forge envelopes through the standard gate

**Triggered by:**
- Operator: `/li:tq {full|loop|single --action <name>}`
- BUILD phase: invokes as sub-module when quality-validation intent detected
- `/li:full-engineering-pass` (when composition skill ships): final stage after DH

**Tested by:**
- `tests/shape/tq-module-contract.sh`
- `tests/unit/tq-routing.sh`

## What this closes

With TQ shipping as v4.5, **all 5 engineering-domain modules per design doc §3 are complete**. The harness now ships:
- TA (v4.1) — tech-architecture
- DA (v4.2) — data-architecture
- SC (v4.3) — security-compliance
- DH (v4.4) — devops-hosting
- TQ (v4.5) — testing-qa

Remaining v4.x work per design doc §5.2:
- `/li:full-engineering-pass` composition skill — runs all 5 modules in DAG order (TA → DA‖SC → DH → TQ)

After that ships, v4.x engineering depth is feature-complete.
