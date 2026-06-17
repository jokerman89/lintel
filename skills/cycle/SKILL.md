---
name: cycle
layer: foundation
workflow_root: true
description: Use to run a real multi-step task through the full SENSE-to-CAPTURE pipeline, or a chosen subset of phases. Supports mode presets, hopping in at any phase, and a cost-estimate gate before BUILD. The default entry point for substantial work.
color: cyan
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Ad-hoc phase sequencing without cost-estimate gate, founder-approval gate, or compliance gates between REVIEW and SHIP."
navigation:
  primary_intent: full feature/cycle work with structured 9-step pipeline
  triggers:
    - operator types /li:cycle (cold start)
    - operator wants the full path with gates between phases
    - resume from prior state via /li:resume
  sibling_workflows:
    - /li:hotfix — bug fix without DESIGN/PLAN gates
    - /li:plan — standalone planner (subset of cycle)
    - /li:review — standalone review (subset of cycle)
  risk_level: medium
  auto_mode_eligible: false
  estimated_tokens: 40000
---

You are the CYCLE orchestrator — the entry point for running the full Lintel cycle or operator-specified subset.

## What this skill does

Coordinates execution of the Lintel cycle (8 core phases + the light SCOPE phase between SENSE and DEFINE). Operator picks granularity via flags:
- Full: `/li:cycle` → SENSE → SCOPE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE
- Mode preset: `/li:cycle --mode hotfix` → runs preset's phase-subset
- Custom: `/li:cycle --from <phase> --to <phase> --skip <phases>` → operator-specified subset
- Auto: `/li:cycle --mode auto` → SENSE detects intent + recommends mode

SCOPE is a light, skippable phase (like DEFINE): it sizes + disambiguates the request before DEFINE burns tokens. Light modes (hotfix) skip it.

Each phase is its own skill (`/li:sense`, `/li:define`, etc.). CYCLE chains them with gates between, propagates context, handles pause-points.

## When to use

- Full feature/cycle work where operator wants the structured path
- When operator types `/li:cycle` (cold start)
- When `/li:resume` decides to re-orchestrate from a phase

## When NOT to use

- Single skill invocation (just call the phase-skill directly: `/li:review`)
- Operator already knows exactly which 1-2 phases they want — invoke them standalone
- Inside another cycle (cycles don't nest)

## Mode presets (operator picks via --mode)

```yaml
hotfix:
  phases: [SENSE, BUILD, REVIEW, SHIP]
  skip: [SCOPE, DEFINE, DISCOVER, PLAN, CAPTURE]
  audience: solo
  voice_tier: pack          # resolve_pack_field voice.default_tier (default internal)
  compliance: pack-minimal  # resolve_pack_field compliance.hooks (none by default)
  cost_estimate: ~5k tokens, 10-30 min
  use_when: known bug + fix path clear + ship now

internal-tool:
  phases: ALL_8 (+ SCOPE; lighter REVIEW)
  audience: team
  voice_tier: pack          # resolve_pack_field voice.default_tier (default internal)
  compliance: pack-standard # resolve_pack_field compliance.hooks (none by default)
  cost_estimate: ~25-50k tokens, 45 min - 2 hours
  use_when: internal tool / scaffolding

research-dive:
  phases: [SENSE, DEFINE, DISCOVER]
  skip: [SCOPE, PLAN, BUILD, REVIEW, SHIP, CAPTURE]
  audience: solo
  voice_tier: pack          # resolve_pack_field voice.default_tier (default internal)
  compliance: none
  cost_estimate: ~10-20k tokens, 20-40 min
  use_when: explore + understand, no code yet

meta-infra:
  phases: ALL_8  # + SCOPE; heavier REVIEW + CAPTURE
  audience: operator + future-operator
  voice_tier: internal
  compliance: scaffolding-only  # skip customer-facing gates; activate Gates M1-M4
  cap_soft: 600k
  cap_hard: 900k
  cost_estimate: ~80-200k tokens, 2-6 hours
  gates_active: [M1_structure_impact, M2_compatibility_audit, M3_shape_tests, M4_future_operator_clarity]
  use_when: change touches skills/, agents/, hooks/, bin/_*.sh, install/, LAYERS.md, lib/, packs/, core templates
  detection: auto-detected by SENSE Step 0c (path-glob on cwd diff); operator can override

auto:
  phases: SENSE recommends, operator confirms before chain
  use_when: operator unsure which preset fits
```

### Pack-contributed modes

The presets above ship with Lintel and are company-neutral. A pack may contribute
additional modes with their own voice/compliance posture — e.g. an external pack
(installable via lintel-caip-pack) can add `customer-engagement` or `demo-prep`
modes that set a customer audience, a non-internal voice tier, and the pack's
compliance gates. CYCLE merges pack-contributed modes into the preset list at
invocation; their voice/compliance behavior resolves through `resolve_pack_field`
(voice.default_tier, voice.gates_active, compliance.hooks), never hardcoded here.

### Meta-infra mode mechanics

`meta-infra` is the operator's mode when modifying Lintel itself (scaffolding). Lintel changes ripple across every downstream cycle, so REVIEW + CAPTURE run heavier and four meta-gates activate:

**M1 — Structure-impact assessment** (in DEFINE)
Before merging design, write a structure-changes/<date>-<slug>.md entry documenting: what changed, backward-compat, migration path, forward-compat, verification, rollback. Template: `docs/v4.x/structure-changes/_TEMPLATE.md`.

**M2 — Compatibility audit** (in REVIEW)
Run `bin/li-compat-audit` to produce mechanical GREEN/YELLOW/RED sweep across four questions:
1. Did any frontmatter contract change? (REQUIRED_SKILL_FIELDS, REQUIRED_AGENT_FIELDS)
2. Were skills/agents/hooks renamed or moved?
3. Did defaults change for any existing field?
4. Did any shared helper signature change? (lib/*.sh)

Output: `docs/v4.x/compatibility-audits/<date>-<slug>.md`. RED requires explicit override.

**M3 — Shape-tests** (in REVIEW)
Run `bash tests/runner/run-all.sh --shape-only`. The 8 shape-tests assert structural invariants (see `tests/shape/_README.md`). Any FAIL blocks SHIP.

**M4 — Future-operator clarity** (in CAPTURE)
CAPTURE writes a recap that future-operator (or future-you) can use cold. Specifically: surface every migration that future operators need to run, every new convention introduced, every deprecated path. Append to `docs/v4.x/migrations/_INDEX.md` if any migration ships.

## Workflow

### Step 0 — Dry-run mode (v3.6 cohort 3 item 2.5)

If `--dry-run` flag present, this skill SHOWS what cycle would do without executing:

```
LINTEL CYCLE DRY-RUN — would-execute plan
==========================================

Mode:           <preset>
Phases:         <list>
Skipped:        <list>
Mode envelope:  <soft>k soft / <hard>k hard (per context-budget)
Estimated cost: <X k tokens total>

Per-phase forecast:
  [1/N] SENSE     est ~0.5k tokens   agents-wake: none
  [2/N] SCOPE     est ~0.5k tokens   agents-wake: none (1 gate only if bimodal)
  [3/N] DEFINE    est ~3k tokens     agents-wake: DesignReviewer
  [4/N] DISCOVER  est ~2k tokens     agents-wake: ArchitectureScout
  [5/N] PLAN      est ~5k tokens     agents-wake: PlanReviewer, CostAnalyzer
  ...

No state mutated. Exit.
```

Paired with Step 4 phase-progress output (v3.6 cohort 2 item 1.5) — dry-run and progress show the same format but dry-run does not run phases.

### Step 1 — Parse invocation

```bash
# Parse flags from operator's invocation
mode="${flag_mode:-auto}"        # --mode <preset>
from_phase="${flag_from:-SENSE}" # --from <phase>
to_phase="${flag_to:-CAPTURE}"   # --to <phase>
skip_phases="${flag_skip:-}"     # --skip PHASE1,PHASE2
auto_decide="${flag_auto:-no}"   # --auto (skip pause gates at recommended choice)
```

If conflicting flags (e.g., --mode hotfix AND --from DEFINE): surface conflict, ask operator.

### Step 2 — Run SENSE (always, first)

```bash
/li:sense
```

SENSE returns: intent, mode recommendation, workprofile state, role, context budget, **scale pre-read** (size + depth_schema; a bimodal flag if the request is ambiguous).

If `--mode auto`: use SENSE's recommendation. AskUserQuestion: "SENSE recommends mode=<X>. Proceed?"

### Step 2.5 — Run SCOPE (unless skipped by mode)

SCOPE runs between SENSE and DEFINE in every mode that doesn't skip it (hotfix + research-dive skip it; see presets). It sizes + disambiguates the request, fires **at most one** clarifying question (only when SENSE flagged the request bimodal), can override a confidently-wrong orientator route, and emits `scope.md`.

```bash
if phase_in_list SCOPE "$phases_to_run"; then
  /li:scope
fi
```

SCOPE returns: resolved `size`, `depth_schema`, `chosen_reading`, and any `route_override`. `scope.md` flows to DEFINE (the wedge) and PLAN (the depth_schema that selects the WBS template variant). If SCOPE overrode the route (e.g. `deploy→ship` → full cycle from DEFINE), CYCLE adopts the override for the remaining phase list. SCOPE is silent on clear small requests — no pause.

### Step 3 — Determine phase list

Based on mode preset + flags:

```
if mode != auto:
  phases_to_run = mode.phases
else:
  phases_to_run = [SENSE, SCOPE, DEFINE, DISCOVER, PLAN, BUILD, REVIEW, SHIP, CAPTURE]
  # 8 core phases + the light SCOPE phase between SENSE and DEFINE

# Apply --skip
phases_to_run = phases_to_run - skip_phases

# Apply --from/--to
phases_to_run = phases_to_run.filter(p in [from_phase, to_phase])

# Verify dependencies (e.g., BUILD requires PLAN before it; if PLAN skipped, error)
verify_phase_deps(phases_to_run)
```

Surface to operator:
```
Cycle plan:
  Mode: <preset>
  Phases to run: [<list>]
  Phases skipped: [<list>]
  Estimated cost: <X tokens / Y min / $Z>
  
  Proceed? [Y/n/edit]
```

If operator confirms: continue. If edit: loop back to Step 2.

### Step 4 — Run phases sequentially (with phase-progress per v3.6 cohort 2 item 1.5)

For each phase in phases_to_run order:

```
0. Phase-progress output: "Phase N/M <PHASE> — next <NEXT> — est ~<X>k tokens"
   (text-only, no graphics per 1.5 spec)
1. Pre-phase: `state_append <PHASE> STARTING`
2. Invoke /li:<phase>
3. Phase runs (with its own pause-gates per phase-skill)
4. Post-phase: `state_last status` (still `STARTING` after the phase returned = the phase crashed before its closing append → treat as BLOCKED) — check the phase's recorded status
5. If status=DONE or DONE_WITH_CONCERNS: continue to next phase
6. If status=BLOCKED: pause cycle, surface to operator
7. If status=NEEDS_CONTEXT: pause, gather, re-invoke phase
```

State writes/reads are mechanical since v5.0 (ADR-0008) — `_sl="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}/lib/state.sh"
[ -f "$_sl" ] || _sl="$HOME/.lintel/lib/state.sh"; source "$_sl"   # installed by install.sh in consumer repos` once, then one command (`state_append` / `state_last`), not a YAML obligation.

**Mark the cycle started — the FIRST mechanical action, non-negotiable.** The moment the phase
list + mode are fixed (Step 3), and before running any phase, run ONCE:
`state_append CYCLE STARTING cycle_id=<id> cycle_mode=<mode> branch=$(git branch --show-current) commit=$(git rev-parse --short HEAD)`

This is not bookkeeping — it is load-bearing. Three mechanisms now DEPEND on it: (1) the
`cycle-incomplete-warn` **Stop hook** fires at turn end and surfaces the position footer only if a
cycle is marked active — so if you skip this, a turn that ends mid-work stays silent (the exact
L-008/L-016 "did lots of work, then total silence" failure); (2) the `session-digest` re-injects
"Current cycle: phase X · next Y" only when this segment exists, so a compacted or resumed session
that skipped the marker cannot recover where it was; (3) the `cycle-position-inject` **UserPromptSubmit
hook** (ADR-0023) re-asserts your position at the START of every turn and reminds you to render the
footer + advance — but only if this marker exists. `render_cycle_footer` and `/li:resume` also read
this segment for the stepper glyphs + integrity check. **Skipping `CYCLE STARTING` is the single most
common way the harness loses the thread — write it first.**
See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md) + [ADR-0023](../../.claude/decisions/0023-turn-start-continuity-inject.md) + L-016/L-018.

**Phase-progress format** (printed to stdout at each phase boundary):

```
─────────────────────────────────────────────────────────
[3/8] DISCOVER → next: PLAN
Token est this phase: ~3k (default — not yet calibrated)  |  cycle total so far: ~9k (uncalibrated)
─────────────────────────────────────────────────────────
```

The token-est numbers come from the phase-skill's frontmatter `tokens_est_typical:` **when the skill
declares it**. Today **zero skills declare it**, so the value falls back to the `~3k per phase`
default — which is a placeholder, not a measurement. When the fallback is in play, label it
**`~3k (default — not yet calibrated)`** rather than printing a bare `~3.5k` that implies precision
the system does not have. (Calibration lands when CAPTURE records actuals; see
`lib/scale-estimator.sh` `scale_calibrated_prior`.)

Between phases:
- Propagate phase output as input to next (e.g., DEFINE's design doc → PLAN's source)
- Check if mode-specific gates apply (e.g., a pack-contributed customer mode may auto-run the active pack's voice gates after SHIP — `resolve_pack_field voice.gates_active`)

**Cycle-position footer.** Each phase skill closes its own report with the shared position footer
(see [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md)), so the operator always knows where
they are and the one logical next action — regardless of where they entered the cycle. The
orchestrator does **not** double-render between phases; it renders the footer only at its **own
gates** (mode-confirm, the cost-estimate gate) and at **cycle completion**:

```bash
source "$LINTEL_REPO_ROOT/lib/cycle-footer.sh"   # or: git rev-parse --show-toplevel
render_cycle_footer --awaiting "Proceed with BUILD? [Y/n/edit-plan]"   # at a gate
render_cycle_footer                                                    # at completion
```

The footer is mode-aware (skipped phases render `⊘`) and auto-falls to a thin ambient line when no
cycle is active. Glyphs degrade to ASCII under `LINTEL_ASCII=1`.

### Step 5 — Pre-BUILD confirm gate (BEFORE BUILD)

If BUILD is in phases_to_run, before invoking it, confirm with the operator using the **honest
signals PLAN recorded** — task count, the phase list, and the labelled token estimate. No dollar
figure (Lintel has no pricing table); no bare-number duration unless `--with-time` was set. Pull the
values PLAN wrote to state (`tasks_count`, `tokens_est`, `tokens_est_basis`):

```
Plan signals (from PLAN):
- Tasks: <N>
- Phases remaining: <phase list>
- Token estimate: ~<total> (<CALIBRATED | UNCALIBRATED — no actuals recorded yet>)
  (only when --with-time:  Duration: ~<hours>)

Proceed with BUILD? [Y/n/edit-plan]
```

This is the SECOND confirm gate (PLAN already had one). Its job is unchanged — confirm before the
token-heavy phase — but it presents the **task count + uncalibrated estimate**, never an invented
dollar/duration figure. The estimate is `UNCALIBRATED` until CAPTURE has recorded actuals for this
size (`lib/scale-estimator.sh` `scale_calibrated_prior`).

If `--auto`: auto-decide the recommended option on reversible gates, but still stop at one-way doors. This is MECHANICAL, not a prose promise (issue I3): run each pending decision through `lib/auto-decide.sh` before auto-deciding —

```bash
source "$LINTEL_REPO_ROOT/lib/auto-decide.sh"
if is_one_way_door "$decision_text"; then ask_operator; else auto_decide_recommended; fi
```

`is_one_way_door` flags the irreversible classes (delete/drop/migrate/schema-change/production/
force-push/secret/rename-skill-agent/breaking-change) regardless of how the decision was framed, so
`--auto` can't run past a sovereignty decision. Operator can interrupt anytime.

### Step 6 — Pause-points between phases (operator can interrupt)

Between each phase, brief progress report:
```
LINTEL CYCLE — <cycle-id>

✓ SENSE (30 sec, 500 tokens)
✓ SCOPE (20 sec, 400 tokens) — size=M, depth_schema=phased
✓ DEFINE (5 min, 4k tokens) — design APPROVED
✓ DISCOVER (3 min, 2k tokens) — 8 ADRs identified
→ PLAN (in progress, est. 10 min)

Continue? [Y/pause/abort]
```

If operator pauses: state saved to .claude/runtime/state/00-state.md with `cycle_paused: true`. Resume via `/li:resume`.

If operator aborts: clean shutdown, save state for next time.

### Step 7 — Failure recovery (per phase BLOCKED)

If a phase returns BLOCKED:
1. Read phase's BLOCKED reason from 00-state.md
2. Surface to operator: phase + reason + recovery options
3. Options:
   - Retry (with same args)
   - Skip (to next phase, document why)
   - Loop-back (to earlier phase, e.g., BUILD blocked → loop to PLAN to re-plan)
   - Abort cycle (save state, exit)

Adopts Architect image's FAILURE RECOVERY PROTOCOL: retry → operator-choice → stub-doc + issue-log → continue.

### Step 8 — Cycle complete

After last phase DONE:
- Surface cycle summary (per CAPTURE phase output if CAPTURE ran)
- If CAPTURE didn't run (e.g., custom subset without CAPTURE): write light summary
- `state_append CYCLE DONE cycle_complete=true` (CAPTURE's own entry covers this when CAPTURE ran)
- Telemetry — one mechanical line via the unified writer (ts/operator/cycle_id come from the envelope):

```bash
source "$(git rev-parse --show-toplevel)/bin/_audit.sh"
audit_log cycle cycle_complete mode=<mode> phases=<n> outcome=<DONE|DONE_WITH_CONCERNS|BLOCKED|ABORTED>
# → .claude/runtime/audit/cycle.jsonl
```

> No `cost_estimate_dollars` field: Lintel has no pricing table, so a dollar figure here would be
> fabricated (K6). Token actuals for estimator calibration are CAPTURE Step 1b's stream
> (`granularity.jsonl` — dormant by decision, ADR-0008), not this one.

## Status protocol

- **DONE** — all phases in chain DONE, cycle complete
- **DONE_WITH_CONCERNS** — chain complete but some phases returned WITH_CONCERNS
- **BLOCKED** — phase BLOCKED, cycle paused, awaiting operator decision
- **ABORTED** — operator aborted mid-cycle, state saved

## Pause-points

- After SENSE: confirm mode (if --auto) or accept SENSE recommendation
- Pre-BUILD: cost-estimate gate
- Between every phase: optional pause (if operator interrupts)
- On any phase BLOCKED: pause for failure-recovery decision

## Hop-in support

YES — `/li:cycle --from <phase>` enters at specified phase.

Verify dependencies:
- BUILD requires PLAN (or existing plan.md)
- REVIEW requires BUILD (or existing diff)
- SHIP requires REVIEW PASS

If dependency not met: surface, ask operator to satisfy or pick different `--from`.

## Integration

**Reads:**
- `~/.lintel/profile.yaml` (defaults)
- `.claude/runtime/state/00-state.md` (resume state)
- Each phase's outputs as inputs to next

**Writes:**
- `.claude/runtime/state/00-state.md` (orchestrator entries per phase)
- `.claude/runtime/audit/cycle.jsonl` (one `audit_log cycle ...` line at cycle complete; failure events use the same stream)

**Triggers:**
- Each phase-skill in sequence: `/li:sense`, `/li:scope`, `/li:define`, etc.

## Anti-patterns

- **Skipping SENSE** — even with --from PLAN, run SENSE first (cheap, sets context)
- **Skipping cost-estimate gate before BUILD** — token-heavy phase, must confirm
- **Auto-mode that auto-decides everything** — operator should at minimum confirm mode recommendation
- **Nesting cycles** — one cycle at a time, no recursive /li:cycle from within
- **Ignoring phase BLOCKED status** — never silently continue past a blocked phase
- **Losing operator's --skip choice** — respect operator decisions, don't override "for safety"

## Failure recovery (per Architect FAILURE RECOVERY PROTOCOL)

1. Phase returns BLOCKED → orchestrator surfaces issue
2. AskUserQuestion: retry / skip / loop-back / abort
3. If skip: write stub-doc + issue-log entry, document gap
4. If loop-back: re-invoke target earlier phase with corrected input
5. If abort: clean state, save resume point, exit

Failure events get one line in the same stream as Step 8 — `audit_log cycle cycle_failure phase=<phase> action=<retry|skip|loop-back|abort>` → `.claude/runtime/audit/cycle.jsonl`.

## Voice tier behavior

`voice: internal`. Cycle orchestrator output is operator-internal coordination. Individual phases inherit the voice tier of the active mode, which resolves through the active pack (`resolve_pack_field voice.default_tier`; default: internal). Pack-contributed customer modes can raise it for customer-facing phases.
