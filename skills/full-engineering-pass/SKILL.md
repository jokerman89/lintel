---
name: full-engineering-pass
layer: foundation
workflow_root: true
description: v4.6 (v4.x feature-complete) — composes all 5 engineering-domain modules in DAG order (TA → DA‖SC → DH → TQ). Single invocation produces architecture decisions + data model + security posture + ops plan + quality validation for a customer engagement or major release.
color: cyan
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Customer engagements + major releases run with no end-to-end engineering discipline. Each module skipped is a class of debt that surfaces in production — either as architectural regret, schema corruption, security audit fail, ops incident, or undetected regression. The composition is what makes the 5 modules add up to more than their sum."
navigation:
  primary_intent: produce end-to-end engineering depth (architecture + data + security + ops + quality) for customer engagement or major release
  triggers:
    - customer engagement requiring full evidence package
    - new service production-ready release prep
    - operator types /li:full-engineering-pass
    - SENSE detects customer-engagement-deep mode + sufficient scope
  sibling_workflows:
    - /li:ta — tech-architecture (first stage, runs alone)
    - /li:da — data-architecture (second stage, parallel with SC)
    - /li:sc — security-compliance (second stage, parallel with DA)
    - /li:dh — devops-hosting (third stage, after DA + SC complete)
    - /li:tq — testing-qa (fourth stage, validates the prior 4)
  risk_level: high
  auto_mode_eligible: false
  estimated_tokens: 500000
domain:
  composition_dag:
    - stage: 1
      modules: [ta]
      parallel: false
    - stage: 2
      modules: [da, sc]
      parallel: true
    - stage: 3
      modules: [dh]
      parallel: false
    - stage: 4
      modules: [tq]
      parallel: false
  cap_soft: 500000
  cap_hard: 750000
  partial_rollout: gracefully_skip_missing_modules
  override_allowed: --skip-module <name>
---

You are the FULL-ENGINEERING-PASS — the composition that runs all 5 engineering-domain modules in DAG order.

## What this skill does

Orchestrates TA → DA‖SC → DH → TQ as a single end-to-end engineering pass. Produces the complete artifact set for a customer engagement or major release in one invocation.

```
Stage 1: TA (tech-architecture)
  ↓ produces: system-arch + ADRs + contracts + dependency graph + NFRs
  ↓
Stage 2: DA  +  SC   (run in parallel — independent concerns)
  ↓ DA produces: data-model + schema + migration + retention + query patterns
  ↓ SC produces: threat-model + secrets + auth + compliance + audit-path + runbook
  ↓
Stage 3: DH (devops-hosting)
  ↓ reads: TA scaling-plan, DA migration-plan, SC threat-model + audit-path
  ↓ produces: deployment + observability + SLI/SLO + cost + rollback + on-call
  ↓
Stage 4: TQ (testing-qa)
  ↓ reads: everything above
  ↓ produces: coverage + perf-budget + contract-tests + regression + chaos
  ↓
SHIP gate: aggregate 30-dim score (6 dims × 5 modules); ≥80 per module to ship
```

Each module has its own 5 checkpoints + 6-dim rubric. The composition is the **orchestration + ordering + cross-module brief handoffs + aggregate scoring**.

## When to use

- Customer engagement requiring complete engineering evidence (architecture review, audit prep, customer audit)
- New service approaching production
- Major release prep
- Annual engineering health review
- SENSE auto-recommends when customer-engagement-deep mode detected + scope is substantial

## When NOT to use

- Hotfix (use `/li:cycle --mode hotfix`)
- Single-module work (invoke the module directly: `/li:ta full`, `/li:da full`, etc.)
- Pre-feature exploration (use `/li:cycle --mode research-dive`)
- Routine work (the cap is 500k soft / 750k hard — overkill for small changes)

## Composition DAG

```yaml
stages:
  - stage: 1
    name: architecture
    modules: [ta]
    parallel: false
    why_first: "architecture decisions constrain everything downstream"

  - stage: 2
    name: data_and_security
    modules: [da, sc]
    parallel: true
    why_parallel: "data design + security posture are independent at this layer; both consume only TA's output"

  - stage: 3
    name: deployment
    modules: [dh]
    parallel: false
    depends_on: [ta, da, sc]
    why_after: "DH reads TA scaling-plan, DA migration-plan, SC threat-model + audit-path"

  - stage: 4
    name: validation
    modules: [tq]
    parallel: false
    depends_on: [ta, da, sc, dh]
    why_last: "TQ validates everything the prior 4 modules produced"
```

## Workflow

### Step 1 — Parse invocation + read pack policy

```bash
mode="${1:-full}"               # full | resume | dry-run
skip_modules="${SKIP_MODULES:-}" # CSV of module names to skip

source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh"
voice=$(resolve_pack_field voice.default_tier)

# Activate customer-engagement-deep mode if pack defines it
deep_mode=$(resolve_pack_field navigation.customer_engagement_deep 2>/dev/null || echo false)
```

### Step 2 — Enumerate available modules + check graceful degradation

```bash
all_modules=(ta da sc dh tq)
available_modules=()
missing_modules=()

for module in "${all_modules[@]}"; do
  if [ -f "$LINTEL_REPO_ROOT/skills/$module/SKILL.md" ]; then
    available_modules+=("$module")
  else
    missing_modules+=("$module")
  fi
done

if [ "${#missing_modules[@]}" -gt 0 ]; then
  echo "⚠ MODULES NOT FOUND: ${missing_modules[*]}"
  echo "⚠ Composition will gracefully skip missing modules + audit the gap."
  echo "⚠ Operator: confirm to proceed with partial pass, or land missing modules first."
  # Wait for operator confirm unless --auto
fi
```

### Step 3 — Resolve skip-list + final module set

```bash
final_modules=()
for module in "${available_modules[@]}"; do
  case ",$skip_modules," in
    *",$module,"*)
      echo "Skipping $module (operator-requested via --skip-module)"
      ;;
    *)
      final_modules+=("$module")
      ;;
  esac
done

if [ "${#final_modules[@]}" -eq 0 ]; then
  echo "ERROR: no modules to run (all available skipped or missing)"
  exit 1
fi
```

### Step 4 — Dispatch by DAG stage

```bash
mkdir -p .lintel/state/full-engineering-pass
state_file=".lintel/state/full-engineering-pass/00-state.md"
audit="$LINTEL_HOME/audit/full-engineering-pass.jsonl"
mkdir -p "$(dirname "$audit")"

declare -A module_score
declare -A module_status

# ─── Stage 1: TA ──────────────────────────────────────
if [[ " ${final_modules[*]} " =~ " ta " ]]; then
  echo "════ Stage 1: TA (tech-architecture) ════"
  /li:ta full || module_status[ta]="FAILED"
  module_score[ta]=$(read_module_score ta)
  forge_envelope phase_transition full-engineering-pass ta--complete brief .lintel/state/ta/...
fi

# ─── Stage 2: DA + SC (parallel) ──────────────────────
echo "════ Stage 2: DA + SC (parallel) ════"
stage2_modules=()
[[ " ${final_modules[*]} " =~ " da " ]] && stage2_modules+=(da)
[[ " ${final_modules[*]} " =~ " sc " ]] && stage2_modules+=(sc)

for module in "${stage2_modules[@]}"; do
  # Phase 4 may upgrade to actual parallel execution via subagent fan-out;
  # v4.6 ships sequential-within-stage with parallel-eligible marker
  /li:"$module" full || module_status["$module"]="FAILED"
  module_score["$module"]=$(read_module_score "$module")
done

# ─── Stage 3: DH ──────────────────────────────────────
if [[ " ${final_modules[*]} " =~ " dh " ]]; then
  echo "════ Stage 3: DH (devops-hosting) ════"
  /li:dh full || module_status[dh]="FAILED"
  module_score[dh]=$(read_module_score dh)
fi

# ─── Stage 4: TQ ──────────────────────────────────────
if [[ " ${final_modules[*]} " =~ " tq " ]]; then
  echo "════ Stage 4: TQ (testing-qa) ════"
  /li:tq full || module_status[tq]="FAILED"
  module_score[tq]=$(read_module_score tq)
fi
```

### Step 5 — Aggregate 30-dim score (6 dims × 5 modules)

```bash
total_score=0
module_count=0

for module in "${final_modules[@]}"; do
  score="${module_score[$module]:-0}"
  total_score=$((total_score + score))
  module_count=$((module_count + 1))

  if [ "$score" -lt 80 ]; then
    echo "FAIL: $module score $score < 80"
  fi
done

aggregate_score=$((total_score / module_count))
```

### Step 6 — SHIP gate

```bash
ship_verdict="GREEN"
[ "$aggregate_score" -lt 80 ] && ship_verdict="YELLOW"

# Any module BLOCKED → composition BLOCKED regardless of aggregate
for module in "${final_modules[@]}"; do
  [ "${module_status[$module]:-}" = "FAILED" ] && ship_verdict="RED"
done

# Missing modules → DONE_WITH_CONCERNS
[ "${#missing_modules[@]}" -gt 0 ] && [ "$ship_verdict" = "GREEN" ] && ship_verdict="YELLOW"
```

### Step 7 — Audit + emit composition report

```bash
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
out=".lintel/state/full-engineering-pass/composition-report-$ts.md"
{
  echo "# Full engineering pass — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "## Aggregate score: $aggregate_score / 100"
  echo "## SHIP verdict: $ship_verdict"
  echo ""
  echo "## Per-module scores"
  for module in "${final_modules[@]}"; do
    echo "- $module: ${module_score[$module]}/100 (${module_status[$module]:-DONE})"
  done
  if [ "${#missing_modules[@]}" -gt 0 ]; then
    echo ""
    echo "## Missing modules (skipped gracefully)"
    for module in "${missing_modules[@]}"; do
      echo "- $module (not present on this branch)"
    done
  fi
  echo ""
  echo "## Cross-module artifacts produced"
  echo "- .lintel/state/ta/ (architecture decisions, ADRs, contracts, NFRs)"
  echo "- .lintel/state/da/ (data model, migrations, retention)"
  echo "- .lintel/state/sc/ (threat model, secrets, auth, compliance, audit)"
  echo "- .lintel/state/dh/ (deployment, observability, SLO, cost, on-call)"
  echo "- .lintel/state/tq/ (coverage, perf budget, contracts, regression, chaos)"
} > "$out"

printf '{"ts":"%s","kind":"full_engineering_pass_complete","aggregate_score":%d,"modules_run":%d,"modules_missing":%d,"verdict":"%s","operator":"%s"}\n' \
  "$ts" "$aggregate_score" "${#final_modules[@]}" "${#missing_modules[@]}" "$ship_verdict" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$audit"

echo ""
echo "════════════════════════════════════════════════════"
echo "  Full engineering pass: $ship_verdict (aggregate $aggregate_score/100)"
echo "  Modules: ${final_modules[*]}"
echo "  Skipped (missing): ${missing_modules[*]:-none}"
echo "  Report: $out"
echo "════════════════════════════════════════════════════"
```

## Status protocol

- **DONE** — all available modules score ≥ 80; aggregate ≥ 80; SHIP verdict GREEN
- **DONE_WITH_CONCERNS** — aggregate ≥ 60 OR 1-2 modules in DONE_WITH_CONCERNS; SHIP verdict YELLOW
- **BLOCKED** — any module BLOCKED OR aggregate < 60; SHIP verdict RED
- **NEEDS_CONTEXT** — pack policy missing customer-engagement-deep mode for high-stakes engagements

## Pause-points

- Pre-Stage 2: if Stage 1 score < 80, surface dimension breakdown, ask to re-loop TA or accept
- Pre-Stage 3: if either DA or SC BLOCKED, surface gap, ask to refine or skip
- Pre-Stage 4: same as Stage 3
- Pre-SHIP: if aggregate < 80, surface module-level breakdown, ask to re-loop or accept-with-concern

## Hop-in support

YES via `--resume`:

```bash
/li:full-engineering-pass --resume
# reads .lintel/state/full-engineering-pass/00-state.md
# continues from the stage where the prior run paused
```

## Integration

**Reads:**
- All 5 module SKILL.md files (or as-many as exist)
- `lib/pack-resolver.sh` for pack policy
- `~/.lintel/profile.yaml` `engineering.*` block (per-module preferences)

**Writes:**
- `.lintel/state/full-engineering-pass/composition-report-<ts>.md`
- `.lintel/state/full-engineering-pass/00-state.md` (for `--resume`)
- `~/.lintel/audit/full-engineering-pass.jsonl`
- Brief Forge envelopes through the standard gate (one per stage transition)

**Triggered by:**
- Operator: `/li:full-engineering-pass`
- SENSE auto-recommendation when customer-engagement-deep mode + sufficient scope

## Graceful degradation

If 1-4 of the 5 modules are missing from the repo (partial-rollout state), the composition:
1. Surfaces the gap to operator before running
2. Asks confirmation to proceed
3. Runs the available modules in DAG order
4. Audits which modules were missing
5. SHIP verdict goes YELLOW even with full pass if modules were skipped (operator can override)

This handles the v4.x stacking-rollout window where SC + DH + TQ + composition land in stacked PRs.

## Anti-patterns

- **Running full-engineering-pass on a hotfix** — overkill; use `/li:cycle --mode hotfix`
- **Skipping TA** — every downstream module depends on architecture decisions
- **Running DA before TA** — DA reads TA's scaling-plan + boundary-review
- **Parallel-stage modules accessing each other's mid-flight state** — DA + SC must be independent within Stage 2
- **Treating aggregate score as the only signal** — per-module dimension breakdown is the actionable view
- **Hardcoding module list** — composition reads available modules from filesystem

## Voice tier behavior

`voice: internal`. Composition produces operator-facing engineering artifacts. Customer-facing voice picks up at SHIP phase when caip-se pack adds Trailblazer alignment via Brief Forge — composition artifacts are inputs to that, not the customer-facing output.
