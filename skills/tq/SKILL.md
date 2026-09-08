---
name: tq
layer: foundation
workflow_root: true
description: Use for testing and QA-strategy depth — test-pyramid review, coverage audits, contract-test design, regression suites, flaky-test quarantine, perf budgets, and chaos plans. Reach for it when test strategy needs deliberate design rather than ad-hoc tests. Runs full, loop, or single-capability, dispatching to the test agents and scoring against a rubric.
color: green
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Quality-bearing work proceeds with no coverage targets, no perf budgets, no contract tests, no regression discipline, no chaos validation; regressions reach production undetected and incidents repeat because no test catches the recurring failure mode."
navigation:
  primary_intent: produce quality-grade testing artifacts when work needs coverage / perf / contract / regression / chaos discipline
  triggers:
    - critical-path feature / release prep / regression-fix-with-test / perf-budget concern
    - operator types /li:tq {full|loop|single --action <name>}
    - BUILD phase detects quality-validation intent (Phase 4 wiring)
  sibling_workflows:
    - /li:ta — tech-architecture module (v4.1)
    - /li:da — data-architecture module (v4.2)
    - /li:sc — security-compliance module (v4.3)
    - /li:dh — devops-hosting module (v4.4)
    - /li:full-engineering-pass — composes all 5 modules in DAG order
  risk_level: medium
  auto_mode_eligible: false
  estimated_tokens: 80000
domain:
  preferences_root: engineering.testing_qa.*
  granularities: [full, loop, single]
  checkpoints:
    - coverage_targets_met: critical-path coverage at threshold + branch coverage adequate
    - perf_budgets_locked: per-critical-journey perf budget with regression detection
    - contract_tests_complete: consumer plus provider contract tests passing
    - regression_suite_curated: golden-path tests plus recent-bug-fix tests
    - chaos_scenarios_documented: failure injection scenarios plus recovery validation
  recovery:
    - on_failure: revert to last-locked checkpoint, surface gap, AskUserQuestion (Re-loop | Accept-with-concern | Raise-help)
  continuation:
    - after_fix: resume at failed checkpoint, job state preserves loop position
  raise_help:
    - critical_path_coverage_below_threshold: operator decides accept-risk or backfill
    - perf_regression_above_budget: operator decides accept-cost or refactor
    - contract_break_against_active_consumer: operator decides break-and-notify or refine
---

You are the TQ (testing-qa) module — Phase 4 v4.5 of Lintel. **Final engineering-domain module of v4.x.**

## What this module does

Produces quality-grade testing artifacts when work needs coverage / perf / contract / regression / chaos discipline. Three granularities — full pass for release prep, loop iteration for refinement, single action for targeted ops.

| Entry | When | Outputs |
|---|---|---|
| `/li:tq full` | new service / major release prep | `coverage-spec.md` + `perf-budget.md` + `contract-test-suite.md` + `regression-suite.md` + `chaos-plan.md` + `flaky-quarantine.md` + `test-pyramid.md` |
| `/li:tq loop` | mid-cycle refinement | revised coverage + perf + contracts + diff vs prior |
| `/li:tq <capability>` · `/li:tq single --action <capability>` | targeted operation (see Sub-capability dispatch) | one artifact per the dispatch table below |

## When to use

- New service approaching release
- Critical-path feature requiring coverage discipline
- Post-incident: add regression test
- Perf-budget refresh (annual SLO review, ramp prep)
- Contract test design for new API consumers
- Chaos plan for resilience validation
- BUILD phase detected quality-validation intent (Phase 4 wiring auto-invokes)

## When NOT to use

- Single test add (write inline)
- Pure dev-loop test runs (use test framework directly)
- One-time coverage report (use coverage tool directly)

## Sub-capability dispatch

Per ADR-0009 the seven capabilities live here as dispatch rows — there are no per-capability
skill files. Invoke one directly as `/li:tq <capability>` (long form: `/li:tq single --action
<capability>`). Per L-001 each capability is a workflow + dispatch contract: content comes from
agents at invocation (spawned via `/li:brief-forge subagent_spawn`); each emits
`.claude/runtime/state/tq/<capability>-<ts>.md` and appends the module audit line (Step 6).

| Capability | Dispatches to (agents) | Produces | Raise-help / notes |
|---|---|---|---|
| `coverage-audit` | TestRunner + Architect | per-component line/branch/mutation coverage + gap analysis + backfill priority | RAISE_HELP when any critical path below `critical_path` threshold (default 100%) (BLOCKED); prefs: `target` (default 80), `critical_path` (default 100); per-language tools below; reads TA boundary-review <30 days old; pairs with `tq-coverage-drop-warn` hook (opt-in, not auto-registered — ADR-0008) |
| `perf-budget-spec` | LatencyAnalyzer + PerfBudgetEnforcer | per-journey p50/p95/p99 budgets + regression alert thresholds + enforcement mode | pref: `p95` (default 200ms); budgets must be tighter than SLO to allow burndown; regression detection: % drift, sample-window size, alarm fan-out; enforcement: CI gate (block PR) \| warn-only \| off; BLOCKED without inferable baseline; reads DH sli-slo-spec <30 days + `perf-baseline.md`; pairs with `tq-perf-regression-warn` hook (opt-in, not auto-registered — ADR-0008) |
| `contract-test-design` | APIDesigner + ContractTestArchitect | contract surface + consumer-driven tests + version compatibility matrix | RAISE_HELP when any contract breaks an active consumer (BLOCKED); pref: `framework` (pact \| consumer-driven-internal \| none, default pact); pairs with `tq-contract-break-warn` hook (opt-in, not auto-registered — ADR-0008) |
| `regression-suite` | RegressionDetective + TestRunner | fix-to-test mapping + golden-path suite + execution health | scans fix commits 90 days back (top 50); per fix: caught-by-existing \| needs-new-test \| impossible-to-test; ≥1 happy-path + 1 edge-case test per golden path; 1-3 uncovered fixes = DONE_WITH_CONCERNS; BLOCKED on golden-path failures |
| `chaos-plan` | SecurityAuditor + SystemArchitect | failure-injection scenarios + dependency-chaos matrix + recovery criteria | exits early with a DONE_WITH_CONCERNS stub when `chaos_active=false` (pref: `active`); per dependency: kill / latency-spike / partial-failure; per scenario: RTO + RPO + auto-vs-manual recovery; game-day cadence + abort conditions; BLOCKED without SC threat model or DH on-call playbook (<30 days old) |
| `flaky-quarantine` | TestRunner + RegressionDetective | flake list + per-test remediation + quarantine durations | pref: `threshold` (default 3 — flake = inconsistent across ≥3 runs on same code); root cause: timing-race \| external-dep \| order-dependent \| env-specific \| unknown; remediation: deflake \| rewrite \| delete \| accept-flake; quarantine cap 14 days; >5 quarantined = DONE_WITH_CONCERNS (systemic); BLOCKED without test history/CI logs |
| `test-pyramid-review` | TestRunner + Architect | per-kind test enumeration + distribution verdict + rebalancing recommendations | classifies: unit \| integration \| e2e \| contract \| perf; per kind: count, total/average execution time, flake rate, CI time; no prefs, no prior-context read |

L-002 result: 5 of 7 capabilities dispatch to existing agents (TestRunner, RegressionDetective, LatencyAnalyzer, APIDesigner, SecurityAuditor, SystemArchitect, Architect). Only 2 new agents (PerfBudgetEnforcer, ContractTestArchitect) for genuinely new capability.

### coverage-audit — per-language tools

go → `go test -coverprofile` · python → `pytest --cov` · node → `jest --coverage` ·
rust → `cargo tarpaulin` · other → `lcov` / language-specific

## Workflow

### Step 1 — Parse invocation

```bash
granularity="${1:?usage: /li:tq {full|loop|<capability>|single --action <capability>}}"
capabilities="coverage-audit|perf-budget-spec|contract-test-design|regression-suite|chaos-plan|flaky-quarantine|test-pyramid-review"
case "$granularity" in
  full|loop) action="" ;;
  single)
    [ "$2" = "--action" ] || { echo "ERROR: --action required for single"; exit 1; }
    action="$3" ;;
  *) action="$granularity"; granularity="single" ;;   # ADR-0009 shorthand: /li:tq <capability>
esac
if [ "$granularity" = "single" ]; then
  echo "$action" | grep -qE "^(${capabilities})$" || { echo "ERROR: unknown capability '$action'"; exit 1; }
fi
```

### Step 2 — Read pack + profile preferences

```bash
source "${LINTEL_SOURCE_ROOT:-$LINTEL_REPO_ROOT}/lib/pack-resolver.sh"

PROFILE="$LINTEL_HOME/profile.yaml"
coverage_target=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'testing_qa:' | grep 'coverage_target:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
coverage_target="${coverage_target:-80}"
critical_path_coverage=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'testing_qa:' | grep 'critical_path_coverage:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
critical_path_coverage="${critical_path_coverage:-100}"
perf_budget_p95=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'testing_qa:' | grep 'perf_budget_p95_ms:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
perf_budget_p95="${perf_budget_p95:-200}"
contract_test_framework=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'testing_qa:' | grep 'contract_test_framework:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
contract_test_framework="${contract_test_framework:-pact}"
chaos_active=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'testing_qa:' | grep 'chaos_active:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
chaos_active="${chaos_active:-true}"
flaky_threshold=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'testing_qa:' | grep 'flaky_quarantine_threshold:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
flaky_threshold="${flaky_threshold:-3}"
```

### Step 3 — Dispatch by granularity

#### `full` granularity

```bash
mkdir -p .claude/runtime/state/tq
audit=".claude/runtime/audit/tq-decisions.jsonl"
mkdir -p "$(dirname "$audit")"

for checkpoint in coverage_targets_met perf_budgets_locked contract_tests_complete regression_suite_curated chaos_scenarios_documented; do
  echo "─── Checkpoint: $checkpoint ───"
  run_checkpoint "$checkpoint" || handle_checkpoint_failure "$checkpoint"
  audit_checkpoint "$checkpoint" "$verdict"
done

score=$(apply_scoring_rubric)
if [ "$score" -lt 80 ]; then
  echo "TQ full pass score=$score (threshold 80) — surface concerns"
  exit 1
fi
```

#### `loop` granularity

```bash
if [ ! -f ".claude/runtime/state/tq/00-state.md" ]; then
  echo "ERROR: no prior TQ state — use /li:tq full first"
  exit 1
fi

prior_iteration=$(grep -E '^iteration:' .claude/runtime/state/tq/00-state.md | head -1 | awk '{print $2}')
new_iteration=$((prior_iteration + 1))

run_checkpoint coverage_targets_met
run_checkpoint perf_budgets_locked
run_checkpoint contract_tests_complete
```

#### `single` granularity

```bash
# ADR-0009: no sub-skill files — dispatch straight off the Sub-capability dispatch table.
# Spawn the capability's agents via /li:brief-forge subagent_spawn, pass the prefs listed
# in its row (coverage-audit ← target + critical_path; perf-budget-spec ← p95;
# contract-test-design ← framework; chaos-plan ← active; flaky-quarantine ← threshold),
# emit .claude/runtime/state/tq/${action}-<ts>.md, append the audit line (Step 6).
dispatch_capability "$action"   # no loop, no checkpoints
```

### Step 4 — Checkpoint failure handling (recovery + raise-help)

```bash
handle_checkpoint_failure() {
  local checkpoint="$1"
  echo "Checkpoint '$checkpoint' FAILED"

  case "$checkpoint" in
    coverage_targets_met)
      if [ "$critical_below_threshold" -gt 0 ]; then
        ask_user_question "$critical_below_threshold critical paths below coverage threshold. Re-loop / Accept-risk / Raise-help (backfill)?"
      fi
      ;;
    perf_budgets_locked)
      if [ "$perf_above_budget" -gt 0 ]; then
        ask_user_question "$perf_above_budget journey(s) above perf budget. Re-loop / Accept-cost / Raise-help (refactor)?"
      fi
      ;;
    contract_tests_complete)
      if [ "$active_consumer_break" -gt 0 ]; then
        ask_user_question "$active_consumer_break active consumer(s) break against new contract. Re-loop / Break-and-notify / Raise-help (refine)?"
      fi
      ;;
  esac

  revert_to_last_locked
}
```

### Step 5 — 6-dimensional scoring rubric

```
| Dimension | Score 0-100 |
|---|---|
| Critical-path coverage at target | <D1> |
| Perf budgets locked with regression detection | <D2> |
| Contract tests complete (consumer + provider) | <D3> |
| Regression suite curated (golden + bug-fix) | <D4> |
| Chaos scenarios documented + recovery validated | <D5> |
| Test pyramid healthy (unit/integration/e2e ratio) | <D6> |

Pass threshold per dimension: 80.
Full-pass exit: every dimension ≥ 80 OR explicit operator override.
```

### Step 6 — Audit + emit ship report

One line via the unified writer (ts/operator/cycle_id come from the envelope):

```bash
source "${LINTEL_SOURCE_ROOT:-$(git rev-parse --show-toplevel)}/bin/_audit.sh"
audit_log tq-decisions tq_module_complete "granularity=$granularity" "score=$score" \
  "checkpoints_passed=$passed_count" "coverage_target=$coverage_target"
# → .claude/runtime/audit/tq-decisions.jsonl
```

## Status protocol

- **DONE** — granularity completed, score ≥ 80, all critical paths at coverage
- **DONE_WITH_CONCERNS** — completed but 1-2 dimensions below 80 with operator accept
- **BLOCKED** — checkpoint failed, raise-help triggered
- **NEEDS_CONTEXT** — unknown capability for single, OR no prior state for loop

## Integration

**Reads:**
- `~/.lintel/profile.yaml` `engineering.testing_qa.*` block
- `lib/pack-resolver.sh` for pack policy
- Existing agents: TestRunner, RegressionDetective, LatencyAnalyzer, APIDesigner, SecurityAuditor, SystemArchitect (TA), Architect
- New agents: PerfBudgetEnforcer, ContractTestArchitect
- Prior modules' output: TA api-design + boundary-review (for contract tests), DA query-pattern-audit (for hot-path coverage), SC threat-model (for chaos scenarios), DH SLO spec (for perf budget alignment)

**Writes:**
- `.claude/runtime/state/tq/coverage-spec.md`
- `.claude/runtime/state/tq/perf-budget.md`
- `.claude/runtime/state/tq/contract-test-suite.md`
- `.claude/runtime/state/tq/regression-suite.md`
- `.claude/runtime/state/tq/chaos-plan.md`
- `.claude/runtime/state/tq/flaky-quarantine.md`
- `.claude/runtime/state/tq/test-pyramid.md`
- `.claude/runtime/audit/tq-decisions.jsonl`
- Brief Forge envelopes through the standard gate

**Triggered by:**
- Operator: `/li:tq {full|loop|single --action <name>}`
- BUILD phase: invokes as sub-module when quality-validation intent detected
- `/li:full-engineering-pass`: final stage in composition DAG (after DH)

**Hooks** (dormant by decision, ADR-0008 — ship in `hooks/shared/` but are opt-in, not auto-registered):
- `hooks/shared/tq-coverage-drop-warn/` (pre-commit on coverage drops)
- `hooks/shared/tq-perf-regression-warn/` (pre-commit on changes affecting perf-budget paths)
- `hooks/shared/tq-contract-break-warn/` (pre-commit on provider changes breaking consumer contracts)

## Anti-patterns

- **Single coverage number for entire codebase** — critical-path coverage matters most; aggregate hides hot paths
- **Perf budgets without regression detection** — budget without alarm = aspirational, not enforced
- **Contract tests on provider only** — consumer-driven is the discipline that catches breakage
- **Regression suite of all bug fixes** — curate to golden-path + actually-recurring; exhaustive is unmaintainable
- **Chaos for chaos sake** — every scenario validates a specific resilience claim
- **Quarantining flaky without remediation plan** — quarantine is temporary; remediation tracks the work
- **Inverted test pyramid (more e2e than unit)** — slow + flaky; surface the imbalance
- **Inventing new agents when existing cover** — 5 of 7 capabilities reuse
- **Hardcoding coverage_target / perf_budget** — read profile
