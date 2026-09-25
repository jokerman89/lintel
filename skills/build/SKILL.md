---
name: build
layer: foundation
description: Use to execute an approved plan in bounded work packages, preserving short task IDs and acceptance evidence while reviewing each package for spec compliance and quality.
color: cyan
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
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
5. Apply configured voice review on customer-facing artifacts (`resolve_pack_field voice.gates_active`; none by default); do not claim automatic enforcement where no adapter is installed.
6. Continuous checkpoint (if checkpoint_mode=continuous)
7. Final code review after all tasks

This phase is where most token spend happens. Cost-estimate from PLAN sets expectations.

## When to use

- After PLAN has APPROVED plan.md within the operator's authorized scope
- For hotfix mode: lighter version, skip continuous review, fast iteration
- Standalone if operator has existing plan.md and wants execution

## When NOT to use

- No approved native plan or authorized mapped work → return to PLAN
- intent=review-only → use REVIEW directly
- intent=research-only → research mode ends at DISCOVER
- Trivial single-file edits — operator just edits directly

## Workflow

### Mapped work takes precedence over the legacy plan.md shorthand

Before the checks below, inspect an explicitly selected committed work.json using the
[shared work-map contract](../spec-kit/references/work-map.md) and `bin/li-work-artifacts.py`.
For mapped work, the map's `status` records plan approval within the operator's authorized
scope. Read requirements from `spec`, design from `plan`, and extract/update card IDs,
dependencies and checkboxes from `tasks`. Spec Kit plan.md is an implementation design and
need not contain Lintel's APPROVED heading or the task list. Throughout the steps below,
“plan.md task” means the mapped `tasks` artifact. Send its complete card text to reviewers
and implementers; never copy those tasks into a second Lintel plan. Native work without a
map keeps the existing plan.md path. Missing artifacts or draft scope return to planning.

Use package grouping from the mapped implementation plan or its explicitly linked handoff;
membership references the original `tasks` IDs without copying their text or checkboxes.
An ungrouped mapped feature uses singleton packages. Read acceptance from the original spec
and tasks; an APPROVED map is not evidence that a leaf was verified. Preserve the selected
work-map path through BUILD and RESUME. Helpers load from `LINTEL_SOURCE_ROOT`; artifact paths
resolve inside `LINTEL_REPO_ROOT`, the working repository.
Set `plan_path` and `tasks_path` from the validated map's original `plan` and `tasks` fields,
and retain `LINTEL_WORK_MAP` as the selected map path. Native work without a map uses plan.md
for both paths. Record these references in the ledger with the leaf results.
Use the shared lifecycle entry in [work-map.md](../spec-kit/references/work-map.md):
`workflow_resume` verifies the saved P07 reference and required policy, then
`workflow_inspect "$LINTEL_WORK_MAP"` reads the original task/package definitions.
A legacy native plan can be inspected without a map, but strict release clearance
requires a reconciled map and the shared bound evidence, not a parallel backlog.

Before a write, surface any advisory code-freeze scope and its stated limitation;
do not claim a universal filesystem lock or a host hook that has not been verified.
Honor an operator's explicit frozen scope even when enforcement is cooperative.


**Host portability:** `TodoWrite`, `Task`, `Read` and `Bash` below describe operations, not
requirements for tool names. Use available host tools, a file checklist if no todo tool exists,
and the current host's configured model. Haiku/Sonnet/Opus labels express complexity tiers;
they are not required model IDs on Copilot. If native delegation is unavailable, sequence
scoped implementation and review and record that the review was not an independent subagent.

### Mapped swarm entry condition

The established package-by-package workflow below remains the default. Enter `/li:swarm run` only when a
validated schema-version-1 work map declares both `execution_mode: "swarm"` and a `coordination`
pointer. One field without the other is invalid; no pointer means legacy sequential BUILD unchanged.

For an opted-in map:

1. Resolve the working repo and installed Lintel source separately, then run the shared validators:

   ```bash
   repo="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel)}"
   if [ -n "${LINTEL_SOURCE_ROOT:-}" ]; then
     source_root="$LINTEL_SOURCE_ROOT"
   elif [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then
     source_root="$CLAUDE_PLUGIN_ROOT"
   else
     echo "NEEDS_CONTEXT: trusted Lintel source root unavailable; set LINTEL_SOURCE_ROOT" >&2
     exit 1
   fi
   [ -f "$source_root/bin/li-work-artifacts.py" ] && [ -f "$source_root/bin/li-swarm.py" ] || {
     echo "NEEDS_CONTEXT: Lintel swarm helpers missing under trusted source root" >&2
     exit 1
   }
   python3 "$source_root/bin/li-work-artifacts.py" --repo "$repo" --map "$work_map"
   python3 "$source_root/bin/li-swarm.py" validate --repo "$repo" --coord "$coordination"
   python3 "$source_root/bin/li-swarm.py" wave --repo "$repo" --coord "$coordination"
   ```

   Claude may provide `CLAUDE_PLUGIN_ROOT`; other adapters must substitute/export their known
   installed bundle as `LINTEL_SOURCE_ROOT`. Tests and self-checks set `LINTEL_SOURCE_ROOT`
   explicitly. Never execute helpers from the working repo merely because it is the current cwd.

2. Treat `frontier.dispatch_task_ids` as an evidence/topology candidate from the earliest incomplete
   wave, not authoritative dependency resolution. Re-read each candidate package's complete member
   leaves and brief. Before every worker handoff, inspect every leaf prerequisite and verify completion
   evidence. Dispatch only when the authoritative prerequisites and candidate frontier agree. If a
   prerequisite is incomplete or coordination disagrees with the mapped task graph, block and return
   to PLAN to correct/re-map; never dispatch from `wave` alone. Then invoke Brief Forge explicitly
   for `subagent_spawn`; when unavailable, disabled, or bypassed, record that audited condition rather
   than claiming a forged handoff.
3. Require the worker to run the Lintel startup named in the brief, stay inside `write_scope + own
   report`, execute acceptance checks, and emit the structured report evidence marker.
4. Use concurrent writers only with a native-subagent host, disjoint validated scopes, and an
   attributable isolation backend (`git-worktree`, `isolated-patch`, or `host-scoped-write`). A
   shared-tree union diff is not attribution. Sequenced/no-subagent hosts execute the same briefs in
   order; no-subagent execution cannot claim an independent implementer.
5. Run `li-swarm.py check-scope` against each lane's exact attributable changed-path list before
   integration. A failure blocks that lane and every dependent wave.
6. After a valid worker report, review the package with the aggregate-risk rule below: Stage 1 checks
   every leaf/spec and their integration, then Stage 2 checks quality. Both must PASS. A substantive
   package needs a distinct reviewer writing only its review artifact; an unavailable independent
   reviewer leaves it open. Mechanical packages may use explicitly recorded coordinator review.
7. The coordinator integrates passing lanes serially in deterministic task order, owns all commits,
   regenerates shared outputs after producer fan-in, runs focused checks, and asks `wave` again.
8. After every lane closes, run `li-swarm.py verify` and continue to ordinary REVIEW on the
   reconciled integration branch. Per-lane reviews do not replace final integrated review.

The detailed per-package rules below remain the worker/reviewer discipline for each swarm lane; only
candidate-wave scheduling and isolation change. Member leaf IDs, acceptance and prerequisites remain
authoritative; legacy ungrouped tasks are singleton packages.

### Step 1 — Pre-flight checks

Verify:
- Approved native plan.md exists, or the validated work map selects the authorized spec/design/tasks
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

Read the selected design and authoritative task artifact once (native plan.md or mapped
`plan` and `tasks`). Extract:
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
1. **Red:** For a behavior-changing code leaf, write the regression test first where executable testing applies. A verification-only leaf runs its approved checks; a documentation or configuration leaf uses its planned validation. Do not manufacture code changes or tests unrelated to acceptance.
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

Use [the accepted evidence contract](../review/references/evidence.md) for each
package: prepare its exact selected source/acceptance snapshot and immutable
`qa_requirements`, obtain actual review, persist it with the real writer, then
consume the latest applicable decision with its expected context/corroboration.
Do not omit, retype or downgrade obligations after seeing observations. Old/empty/
positive-string review records remain history only; direct `verify` is not latest-log
clearance. Carry verified profile context/generation/digest and required policy into
delegation and cold resume unchanged. An unavailable independent reviewer remains open.

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

After a coherent package passes review, keep a scoped Conventional Commit and the
durable mapped handoff. Existing `checkpoint_mode` and `checkpoint_push` preferences
remain readable; they never authorize publication outside the current task.
```bash
git add <intentional files only — NEVER git add -A>
git commit -m "<type>: <package outcome>

Decisions: <key choices made>
Remaining: <what's left in logical unit>
Work-map: <selected work.json>
Package: <original package ID>
Leaves: <original leaf IDs>"
```

NEVER `git add -A`. NEVER commit broken state. Use `/li:pause` for an owned checkpoint;
`/li:resume --from <path>` reads it without discarding the selected work map.

If `checkpoint_push: true`, push only when the current authorization covers that
reviewed batch and destination. Otherwise retain the checkpoint locally.

### Step 5 — Build log

Append to `.claude/runtime/state/build-log.md`:
Use an explicitly linked per-cycle log for new work; retain legacy logs as history.
Each entry identifies the same map, original task source and profile, so two
initiatives' results cannot be merged by task ID alone:
```yaml
cycle_id: <original cycle ID>
work_map: <selected work.json>
tasks_path: <original mapped tasks>
profile: <verified complete P07 reference>
required_policy: <unchanged bridge>
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
1. Run the applicable final test suite through `/li:verify` without edits
2. Check no regressions in unmentioned areas
3. Invoke `/li:analyze --map <same selected map>` with trigger `build-final` (ADR-0004) — the PLAN↔BUILD leg: every original
   task has a terminal status, no untasked work shipped, deviations reflected back. Surface the
   report verdict; RED/YELLOW findings go to the operator (advisory, not a hard block).
4. If a specialist walkthrough was requested, delegate a bounded review through the
   actual native host or preserve the same brief for an independent external actor.
   Include original work/leaf IDs, profile, exact result and read scope. Reviewers
   report; implementers fix. Serial self-review is not independent review.
5. Write the 00-state.md BUILD entry via `state_append` (Step 7)

### Step 7 — 00-state.md append

Mechanical since v5.0 (ADR-0008) — one command, not a YAML obligation (per-task metrics live in build-log.md, Step 5):

```bash
source "${LINTEL_SOURCE_ROOT:?select the trusted source}/lib/state.sh"
# Set these from the reviewed package/leaf results, never from an intended outcome.
case "${build_status:?set actual BUILD status}" in
  DONE|DONE_WITH_CONCERNS) build_next=REVIEW ;;
  BLOCKED) build_next=BUILD; : "${build_next_action:?record blocked package/leaf repair step}" ;;
  *) echo "Unsupported BUILD status" >&2; exit 1 ;;
esac
state_append BUILD "$build_status" next="$build_next" \
  plan_path="${plan_path:?set approved plan path}" \
  work_map_path="${LINTEL_WORK_MAP:-}" tasks_path="${tasks_path:-$plan_path}" \
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
- **Dispatching multiple implementers outside a validated mapped swarm** — ordinary BUILD stays
  sequential; opted-in swarms may fan out only the safe isolated frontier
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
- **Test suite breaks during task**: preserve the owned change, mark the affected
  leaf BLOCKED and diagnose via `/li:diagnose`. A rollback requires its own scoped
  authority and must preserve unrelated or later edits.
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
source "${LINTEL_SOURCE_ROOT:?select trusted source}/lib/cycle-footer.sh"
render_cycle_footer                               # reads .claude/runtime/state/00-state.md; --compact for short replies
```

Skipped phases render `⊘`; ASCII via `LINTEL_ASCII=1`. See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
