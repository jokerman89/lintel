---
name: build
layer: foundation
description: Use to execute an approved plan in bounded work packages, preserving short task IDs and acceptance evidence while reviewing each package for spec compliance and quality.
color: cyan
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: REQUIRED
gap_if_skipped: "No implementation is produced; the plan's tasks are never executed."
---

You are the BUILD skill — Phase 5 of the Lintel cycle.

## What this skill does

Executes plan.md with the hybrid contract in ADR-0026:
1. Read plan.md, extract all tasks with full text
2. Create TodoWrite for tasks
3. Per work package: dispatch one implementer with all member leaves → implement in dependency order → review the package for spec compliance THEN quality → fix findings → record evidence and completion for every leaf
4. Verify which requested compliance controls actually run on this host (`resolve_pack_field compliance.hooks`; none by default)
5. Apply configured voice review to customer-facing artifacts (`resolve_pack_field voice.gates_active`; none by default)
6. Continuous checkpoint (if checkpoint_mode=continuous)
7. Final code review after all tasks

This phase is where most token spend happens. Cost-estimate from PLAN sets expectations.

## When to use

- After PLAN has APPROVED plan.md with founder gate passed
- For hotfix mode: lighter version, skip continuous review, fast iteration
- Standalone if operator has existing plan.md and wants execution

## When NOT to use

- No APPROVED plan.md → return to PLAN
- intent=review-only → use REVIEW directly
- intent=research-only → research mode ends at DISCOVER
- Trivial single-file edits — operator just edits directly

## Workflow

### Step 1 — Pre-flight checks

Verify:
- plan.md exists and is APPROVED status
- Current branch is NOT main/master (if no explicit user consent for main)
- Resolve requested controls and the pack's mode/policy. Classify each as a compatible
  registered hook, an equivalent accepted by that policy with recorded evidence, or an
  unsatisfied requirement. An unavailable mandatory control blocks its affected action;
  continue independent authorized preparation. Advisory gaps remain explicit concerns.
  Recording a missing capability never counts as satisfying a mandatory requirement.
- Git worktree state clean OR operator confirms WIP state OK

If on main without consent: HARD STOP per superpowers rule. AskUserQuestion: "Switch to feature branch / proceed on main with confirmation / abort?"

### Step 2 — Read plan, extract tasks, create TodoWrite

**Surface relevant lessons (mirrors SENSE Step 0a — non-blocking):**

Before reading the plan and dispatching implementers, invoke `/li:lessons-surface` keyword-scoped to implementation so prior-session lessons inform task execution and subagent dispatch. Same mechanism SENSE uses (max 3 lessons, prepended to context, silent on no match, never a blocker):

Invocation: `/li:lessons-surface --keyword "implementation testing subagent"` (a portable skill call; silent if no relevant matches).

Read entire plan.md once. Extract:
- All task titles + IDs
- Dependencies between tasks
- Acceptance criteria
- Package membership, outcome, owner/edit boundary and review scope
- Recommended subagent and the available host's model configuration

Track existing leaf IDs in TodoWrite or the plan checklist. An old plan without packages
treats each leaf as a singleton package; no migration or new job-state schema is required.
Check that each leaf belongs to exactly one package and all external dependencies are met.
Execute packages sequentially by default. Group only leaves that deliver one outcome under
one write owner and compatible boundaries; separate different approval, risk or rollback
boundaries. Package membership cannot hide an unresolved dependency or scope change.

### Step 3 — Per-package execution cycle

For each ready package, execute its short leaves in dependency order. Preserve the 2–5 minute
leaf constraint; grouping reduces repeated context loading, not acceptance coverage.

#### 3a — Dispatch implementer subagent

**Record the package's start ref first:** note `HEAD`, the owned paths and any authorized
pre-existing diff. Review only attributable package changes; unrelated work in a shared
checkout is not evidence. Use an isolated worktree when overlapping writers would prevent
reliable attribution. Leaf log entries reference the same package start ref.

Spawn one fresh implementer for the package with:
- **Full text of every member leaf**, stable IDs, package outcome and dependency order
- **Scene-setting context** (what came before this task, why, what's expected)
- **Acceptance criteria** (test or verify command)
- **Companion skills**: TDD discipline, verification-before-completion
- **Tool restrictions**: scoped per task (e.g., only Read+Write+Edit+Bash for code, no Grep needed)
- **Host capability and model configuration:** use the available host tools and configured
  model; do not invent access to a named model. If delegation is unavailable, execute the
  same bounded package in the coordinator and disclose that limitation.

#### 3b — Implementer executes (TDD red-green-refactor)

The TDD red-green-refactor discipline:
1. **Red:** Write failing test first (REQUIRED — code without failing test = block)
2. **Green:** Write minimum code to pass
3. **Refactor:** Improve while tests still pass
4. **Checkpoint:** retain leaf results; make an atomic package commit only when the logical
   change and its verification are coherent (per continuous-checkpoint if enabled)

Implementer self-reviews. Returns status:
- **DONE** — implementation ready for review, with an evidence result for every leaf; final leaf completion waits for both package reviews
- **DONE_WITH_CONCERNS** — concerns logged in implementer message
- **NEEDS_CONTEXT** — implementer asked for info, provide + re-dispatch
- **BLOCKED** — implementer can't proceed, root-cause hypothesis, escalate to operator

#### 3b-guard — Empty-diff check (fail-closed, v4.11)

Before dispatching review, verify the package produced its planned changes and evidence.
Compare owned changes against the package start ref recorded in 3a: `git diff <start_ref>` covers
both committed (WIP commits) and uncommitted work; if the start ref is somehow missing, fall
back to `git status --porcelain` + `git diff HEAD` AND check `git log` for WIP commits carrying
the package's leaf IDs before concluding "no change". A nonempty aggregate diff cannot
prove every member leaf was implemented: check each leaf's own acceptance and evidence.

For a task explicitly planned as verification-only, review its recorded command, result and
evidence against acceptance criteria; no source diff is expected. This exception must be in
the approved task, not invented after an implementation task produces no changes. Keep the
empty-diff block below for tasks whose acceptance requires a code or artifact change.

- **Diff is empty or whitespace-only** (`git diff -w <start_ref>` produces nothing) → the review
  MUST NOT run and the task CANNOT be marked DONE. Treat as **BLOCKED**: the implementer
  no-op'd, reported success without editing, or wrote outside the repo. Re-dispatch with the
  discrepancy stated, or escalate.
- Rationale: a reviewer fed a no-op tree rubber-stamps it — "looks complete" with nothing to look
  at (the superpowers #1701 failure mode). A green review must have reviewed *something*.

#### 3c — Two-stage review (complexity-gated)

**Review-routing gate (per `docs/concepts/agent-dispatch-rules.md` rule (c) — inline when cheap + deterministic):**

Route review by the **aggregate package** complexity and risk, not by the smallest leaf:

- **Mechanical package** (a bounded deterministic change with no substantive integration or
  risk boundary) → coordinator reviews spec compliance then quality inline; log that mode.
- **Substantive package** (multi-file integration, architecture or security-sensitive work)
  → dedicated independent review in the two stages below. Several small leaves do not make
  the combined change mechanical. Implementer self-review cannot replace this review.

This is an off-switch for trivial tasks ONLY — it does NOT remove the two-stage review for substantive work. When in doubt about a task's tier, default to the full two-stage dedicated review.

**Stage 1 — Spec compliance review (substantive tasks — dedicated; mechanical tasks — inline):**

Dispatch reviewer subagent (CodeReviewer or general-purpose):
"Review this package against every member leaf's requirements and evidence. Map findings
to leaf IDs, identify missing acceptance and cross-leaf integration gaps, and report the
package verdict. Review only the supplied owned diff and relevant surrounding code."

If Stage 1 FAILS:
- Fix the gaps (Edit tool, or re-dispatch implementer with specific fix-list)
- Re-dispatch Stage 1 review
- Max 3 iterations per stage

#### 3d — Stage 2 — Code quality review (ONLY after Stage 1 PASS):

Dispatch reviewer subagent:
"Quality dimensions: correctness, security, performance, code-style, edge-cases, error handling, test coverage. Score each. P1/P2/P3 findings."

If Stage 2 FAILS:
- Fix per finding severity (P1 = block, P2 = fix, P3 = log + defer if pressed for time)
- Re-dispatch
- Max 3 iterations

#### 3e — Compliance controls available on the host

The active pack's hook list (`resolve_pack_field compliance.hooks`; none by default) declares
requested controls. Automatic execution requires compatible registered hooks on the current
host; Lintel's hook bundle implements the Claude Code protocol. On another host, record the
available policy-accepted equivalent and its evidence, or retain the unsatisfied requirement
under the preflight rule. A pack label or hook file is not proof of execution. Example controls:
- `customer-data-block`: BLOCKS commit with customer-PII patterns
- `secret-scan-block`: BLOCKS commit with detected secrets
- `no-direct-main-push`: WARNS on direct main push

If a hook BLOCKS: hard stop. Operator decides override (rarely warranted).

#### 3f — Voice gate (if customer-facing artifact + pack defines voice gates)

If task produces customer-facing output (docs, copy, demo content):
- Run the active pack's voice gates (`resolve_pack_field voice.gates_active`; none by default)
- Score against the pack's voice corpus (`resolve_pack_field voice.corpus`; none by default)
- If score <85%, surface findings, suggest edits, re-review

#### 3g — Mark complete

After both review stages pass, record every leaf's acceptance evidence and final status.
Mark the package complete only when every member is verified and no blocking finding remains.
If one leaf fails, keep the package open; retain completed evidence and retry the affected
leaves and their impacted verification. Do not repeat unrelated checks without a reason.

### Step 4 — Continuous checkpoint (if checkpoint_mode=continuous)

After a coherent package passes review:
```bash
git add <intentional files only — NEVER git add -A>
git commit -m "<type>: <package outcome>

[lintel-context]
Decisions: <key choices made>
Remaining: <what's left in logical unit>
Skill: /li:build (package P<N>, leaves <IDs> in plan.md)
[/lintel-context]"
```

NEVER `git add -A`. NEVER commit broken state. Operator can resume from any WIP via `/li:context-restore`.

If `checkpoint_push: true`: also push WIP to origin.

### Step 5 — Build log

Append to `.claude/runtime/state/build-log.md`:
```yaml
task: T<N>
package_id: P<N>                  # annotation, not a new job/state schema
title: <title>
start_ref: <HEAD sha at 3a dispatch>   # 3b-guard diffs against this
status: DONE | DONE_WITH_CONCERNS | BLOCKED
implementer_status: <as returned>
acceptance_evidence: <command/result or reviewed artifact reference for this leaf>
package_review: <report reference covering all member leaves>
review_mode: dedicated | inline   # based on aggregate package complexity (3c)
spec_review_iterations: <N>
quality_review_iterations: <N>
voice_gate_score: <% if applicable>
tokens_used: <approx>
time_elapsed: <minutes>
ts: <timestamp>
```

### Step 6 — All tasks complete: final pass

After last task DONE:
1. Run full test suite (`/li:qa` invoked)
2. Check no regressions in unmentioned areas
3. Invoke `/li:analyze` with trigger `build-final` (ADR-0004) — the PLAN↔BUILD leg: every plan
   task has a terminal status, no untasked work shipped, deviations reflected back. Surface the
   report verdict; RED/YELLOW findings go to the operator (advisory, not a hard block).
4. If `pair-agent` mode: invoke for operator-pair-programming-style final walkthrough
5. Write the 00-state.md BUILD entry via `state_append` (Step 7)

### Step 7 — 00-state.md append

Mechanical since v5.0 (ADR-0008) — one command, not a YAML obligation (per-task metrics live in build-log.md, Step 5):

```bash
_sl="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}/lib/state.sh"
[ -f "$_sl" ] || _sl="$HOME/.lintel/lib/state.sh"; source "$_sl"   # installed by install.sh in consumer repos
# Set these from the reviewed package/leaf results, never from an intended outcome.
case "${build_status:?set actual BUILD status}" in
  DONE|DONE_WITH_CONCERNS) build_next=REVIEW ;;
  BLOCKED) build_next=BUILD; : "${build_next_action:?record blocked package/leaf repair step}" ;;
  *) echo "Unsupported BUILD status" >&2; exit 1 ;;
esac
state_append BUILD "$build_status" next="$build_next" \
  plan_path="${plan_path:?set approved plan path}" \
  tasks_completed="${tasks_completed:?set verified leaf count}" \
  tasks_blocked="${tasks_blocked:?set blocked leaf count}" \
  note="${build_next_action:-review completed implementation}"
```

For BLOCKED, set `build_next_action` to the unresolved package/leaf and its repair step;
preserve its owned diff, acceptance results and review evidence for a cold session. Emit
DONE_WITH_CONCERNS only when all required leaf acceptance and reviews have passed.

## Status protocol

- **DONE** — all tasks complete, both reviews PASS, all tests green
- **DONE_WITH_CONCERNS** — done but P2/P3 concerns logged per-task
- **BLOCKED** — implementer can't complete a task, escalated to operator
- **NEEDS_CONTEXT** — implementer needs more info, can't proceed

## Pause-points

- Before BUILD starts: pre-flight checks (branch state, hooks active)
- After each package review-pass: record leaf completion and package evidence (no extra approval unless a boundary requires it)
- At meaningful package milestones: concise progress report
- On BLOCKED: pause, root-cause hypothesis, operator decision
- On a blocking compliance hook fire: hard stop, never silently proceed
- On voice gate fail: surface, operator decides override or re-write

## Hop-in support

YES — operator can `/li:build` with existing plan.md.

Skip-conditions: intent=review-only, intent=research-only, intent=plan-only.

## Integration

**Reads:**
- plan.md (canonical, MANDATORY)
- CORE-PRINCIPLES.md
- the active pack's compliance hooks (`resolve_pack_field compliance.hooks`; none by default)
- role file (if active, voice/tone signals only)
- recent test results
- `.claude/memory/lessons.md` (via `/li:lessons-surface`, keyword-scoped, non-blocking)

**Writes:**
- source code (edits via implementer subagents)
- WIP commits (if continuous mode)
- `.claude/runtime/state/build-log.md`
- `.claude/runtime/state/00-state.md` (BUILD entry per task + final)
- `.claude/runtime/audit/build-metrics.jsonl`

**Triggers:**
- `/li:review` next (or REVIEW in /li:cycle)
- Registered compatible hook execution on supported hosts

## Recommended subagents per task (from plan.md mapping)

- **TestRunner** (engineering/) — TDD red phase + verification
- **Refactorer** (engineering/) — refactor phase
- **Migrator** (engineering/) — schema/API migrations
- **BackendArchitect / FrontendBuilder** (engineering/) — per task domain
- **K8sManifestReviewer / TerraformReviewer** (devops/) — infra tasks
- **CostAnalyzer / LatencyAnalyzer / RegressionDetective** (engineering/) — perf-related tasks
- **SecurityAuditor / SecretsScanReviewer / ThreatModelDrafter** (security/) — security tasks
- **CodeReviewer** (engineering/) — reviewer for both stages

## Anti-patterns (from superpowers)

- **Starting on main/master without explicit user consent** — hard rule
- **Skipping review entirely** because "task is simple" — never. Mechanical tasks get INLINE review (3c gate), not NO review; substantive tasks keep the full two-stage dedicated review.
- **Proceeding with unfixed P1 issues** — never
- **Splitting one package across competing implementers** — one write owner; packages run sequentially by default
- **Making subagent read plan.md** — give them task text directly (subagent has no plan-context unless given)
- **Skipping scene-setting context for implementer** — they need to understand WHY this task
- **Ignoring subagent questions** — answer + re-dispatch, don't proceed without
- **Accepting "close enough" on spec compliance** — Stage 1 must PASS exactly
- **Skipping leaf coverage in a package review** — one spec stage + one quality stage per package, covering every leaf and their integration
- **Letting implementer self-review replace actual review** — never
- **Starting code quality review before spec compliance is ✅** — order matters

## Failure recovery

- **Implementer returns BLOCKED**: assess root cause:
  - Plan error (task description wrong) → fix plan, re-dispatch
  - Missing context (deps not built) → check task order, reschedule
  - Complexity underestimated → decompose into subtasks, update plan
  - Plan correct but environment broken → escalate to operator
- **Reviewer unavailable**: preserve implementation evidence; keep a substantive package open
  until independent review is available. For an eligible mechanical package, the coordinator
  can apply the documented inline review. Never label missing review as completed review.
- **Test suite breaks during task**: revert task, mark BLOCKED, investigate via `/li:investigate`.
- **A blocking compliance hook fires repeatedly**: STOP. Investigate why operator's content keeps triggering. Likely real issue.
- **Voice gate fails 3x for same artifact**: surface to operator, decide accept-with-caveat or re-write from scratch.

## Model selection

Match package complexity to the current host's available configuration. Honor an explicit
operator model choice. Record actual usage when available; do not infer model access or cost
from a complexity label.

## Voice tier behavior

`voice: internal`. Code is engineering-internal. Customer-facing artifacts (if any in BUILD) flow through the active pack's voice gates (`resolve_pack_field voice.gates_active`; none by default).

## Cycle-position footer

Close your report with the shared position footer so the operator always knows where they are in the
cycle and the one logical next action — whether this phase ran standalone or inside `/li:cycle`:

```bash
source "$LINTEL_REPO_ROOT/lib/cycle-footer.sh"   # fallback: "$(git rev-parse --show-toplevel)/lib/cycle-footer.sh"
render_cycle_footer                               # reads .claude/runtime/state/00-state.md; --compact for short replies
```

Skipped phases render `⊘`; ASCII via `LINTEL_ASCII=1`. See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
