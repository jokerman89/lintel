---
name: build
layer: foundation
description: Phase 5 of Lintel cycle — execute plan via TDD + subagent-driven-development. Fresh subagent per task with two-stage review (spec compliance then quality). Per-task status protocol.
color: cyan
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: REQUIRED
gap_if_skipped: "No implementation is produced; the plan's tasks are never executed."
---

You are the BUILD skill — Phase 5 of the Lintel cycle.

## What this skill does

Executes plan.md task-by-task using superpowers' Subagent-Driven Development pattern:
1. Read plan.md, extract all tasks with full text
2. Create TodoWrite for tasks
3. Per task: dispatch fresh implementer subagent → implementer executes (TDD red-green-refactor) → two-stage review (spec compliance THEN code quality) → fix loop if needed → mark complete
4. The active pack's compliance hooks fire automatically (`resolve_pack_field compliance.hooks`; none by default)
5. The active pack's voice gates fire on customer-facing artifacts (`resolve_pack_field voice.gates_active`; none by default)
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
- Active pack's compliance hooks status (`resolve_pack_field compliance.hooks`; none by default — when present, e.g. customer-data-block + secret-scan-block, they must be activated)
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
- Recommended subagent per task
- Model selection per task

Create TodoWrite with tasks. Mark T1 as in_progress.

### Step 3 — Per-task execution cycle

For each task in dependency order:

#### 3a — Dispatch implementer subagent

**Record the task's start ref first:** note the current `HEAD` sha (one `git rev-parse HEAD`)
in the build-log entry for this task — 3b-guard diffs against it after the implementer returns.

Spawn fresh subagent with:
- **Full task text** from plan.md (verbatim, not "read plan.md")
- **Scene-setting context** (what came before this task, why, what's expected)
- **Acceptance criteria** (test or verify command)
- **Companion skills**: TDD discipline, verification-before-completion
- **Tool restrictions**: scoped per task (e.g., only Read+Write+Edit+Bash for code, no Grep needed)
- **Model selection** per task complexity:
  - Mechanical (single-file edit) → Haiku
  - Multi-file integration → Sonnet
  - Architecture / design judgment → Opus

#### 3b — Implementer executes (TDD red-green-refactor)

Per `/li:tdd-cycle`:
1. **Red:** Write failing test first (REQUIRED — code without failing test = block)
2. **Green:** Write minimum code to pass
3. **Refactor:** Improve while tests still pass
4. **Commit:** WIP commit with task ID in message (per continuous-checkpoint if mode on)

Implementer self-reviews. Returns status:
- **DONE** — task complete, tests pass, ready for spec review
- **DONE_WITH_CONCERNS** — concerns logged in implementer message
- **NEEDS_CONTEXT** — implementer asked for info, provide + re-dispatch
- **BLOCKED** — implementer can't proceed, root-cause hypothesis, escalate to operator

#### 3b-guard — Empty-diff check (fail-closed, v4.11)

Before dispatching ANY review — inline or dedicated — verify the implementer actually changed
the tree. Compare against the task's start ref recorded in 3a: `git diff <start_ref>` covers
both committed (WIP commits) and uncommitted work; if the start ref is somehow missing, fall
back to `git status --porcelain` + `git diff HEAD` AND check `git log` for WIP commits carrying
this task's ID before concluding "no change".

- **Diff is empty or whitespace-only** (`git diff -w <start_ref>` produces nothing) → the review
  MUST NOT run and the task CANNOT be marked DONE. Treat as **BLOCKED**: the implementer
  no-op'd, reported success without editing, or wrote outside the repo. Re-dispatch with the
  discrepancy stated, or escalate.
- Rationale: a reviewer fed a no-op tree rubber-stamps it — "looks complete" with nothing to look
  at (the superpowers #1701 failure mode). A green review must have reviewed *something*.

#### 3c — Two-stage review (complexity-gated)

**Review-routing gate (per `docs/concepts/agent-dispatch-rules.md` rule (c) — inline when cheap + deterministic):**

Route the review by the task's complexity tier (the same tier that drove model selection in 3a):

- **Mechanical / Haiku-tier leaf task** (single-file edit, rename, add a log line, a trivial test) → **inline review.** The implementer's own diff + acceptance command is reviewed inline in the main thread; a dedicated reviewer subagent is skipped (its base-context warmup cost exceeds the review value for a one-file mechanical change — rule (c)). Still apply both lenses inline: spec-compliance THEN quality. Note in the build-log that the review was inline.
- **Substantive task** (multi-file integration / Sonnet, or architecture/design-judgment / Opus) → **full two-stage dedicated review below** (UNCHANGED). Fresh reviewer context is the point (rule (b)); never inline these.

This is an off-switch for trivial tasks ONLY — it does NOT remove the two-stage review for substantive work. When in doubt about a task's tier, default to the full two-stage dedicated review.

**Stage 1 — Spec compliance review (substantive tasks — dedicated; mechanical tasks — inline):**

Dispatch reviewer subagent (CodeReviewer or general-purpose):
"Does the implementation match task requirements EXACTLY? List any deviations. Be strict — 'close enough' is not acceptable."

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

#### 3e — Compliance hooks (auto-fire per active pack)

The active pack's hooks (`resolve_pack_field compliance.hooks`; none by default) run automatically on every edit/commit when present. Example hooks a pack may activate:
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

TodoWrite mark task as completed. Move to next task.

### Step 4 — Continuous checkpoint (if checkpoint_mode=continuous)

After each task DONE:
```bash
git add <intentional files only — NEVER git add -A>
git commit -m "WIP: <task title>

[lintel-context]
Decisions: <key choices made>
Remaining: <what's left in logical unit>
Skill: /li:build (task T<N> of plan.md)
[/lintel-context]"
```

NEVER `git add -A`. NEVER commit broken state. Operator can resume from any WIP via `/li:context-restore`.

If `checkpoint_push: true`: also push WIP to origin.

### Step 5 — Build log

Append to `.lintel/state/build-log.md`:
```yaml
task: T<N>
title: <title>
start_ref: <HEAD sha at 3a dispatch>   # 3b-guard diffs against this
status: DONE | DONE_WITH_CONCERNS | BLOCKED
implementer_status: <as returned>
review_mode: dedicated | inline   # inline for mechanical/Haiku-tier leaf tasks (3c gate)
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
3. If `pair-agent` mode: invoke for operator-pair-programming-style final walkthrough
4. Write 00-state.md BUILD entry

### Step 7 — 00-state.md append

```yaml
phase: BUILD
ts: <timestamp>
plan_path: <path>
tasks_completed: <N>
tasks_blocked: <count>
spec_review_iterations_total: <sum>
quality_review_iterations_total: <sum>
tokens_used_total: <approx>
voice_gate_failures: <count>
hard_rule_blocks: <count>
status: DONE | DONE_WITH_CONCERNS | BLOCKED
next_recommended: REVIEW
```

## Status protocol

- **DONE** — all tasks complete, both reviews PASS, all tests green
- **DONE_WITH_CONCERNS** — done but P2/P3 concerns logged per-task
- **BLOCKED** — implementer can't complete a task, escalated to operator
- **NEEDS_CONTEXT** — implementer needs more info, can't proceed

## Pause-points

- Before BUILD starts: pre-flight checks (branch state, hooks active)
- After each task review-pass: TodoWrite mark complete (no operator pause unless concerns)
- Every Nth task (N=5 default): optional summary report
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
- `tasks/lessons.md` (via `/li:lessons-surface`, keyword-scoped, non-blocking)

**Writes:**
- source code (edits via implementer subagents)
- WIP commits (if continuous mode)
- `.lintel/state/build-log.md`
- `.lintel/state/00-state.md` (BUILD entry per task + final)
- `~/.lintel/analytics/build-metrics.jsonl`

**Triggers:**
- `/li:review` next (or REVIEW in /li:cycle)
- Hook execution (settings.json hooks fire on edit/commit events)

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
- **Dispatching multiple implementers in parallel within one phase** — sequential (gives reviewer context)
- **Making subagent read plan.md** — give them task text directly (subagent has no plan-context unless given)
- **Skipping scene-setting context for implementer** — they need to understand WHY this task
- **Ignoring subagent questions** — answer + re-dispatch, don't proceed without
- **Accepting "close enough" on spec compliance** — Stage 1 must PASS exactly
- **Skipping review loops** — minimum 1 spec + 1 quality per task (inline for mechanical tasks, dedicated for substantive — but both lenses always apply)
- **Letting implementer self-review replace actual review** — never
- **Starting code quality review before spec compliance is ✅** — order matters

## Failure recovery

- **Implementer returns BLOCKED**: assess root cause:
  - Plan error (task description wrong) → fix plan, re-dispatch
  - Missing context (deps not built) → check task order, reschedule
  - Complexity underestimated → decompose into subtasks, update plan
  - Plan correct but environment broken → escalate to operator
- **Reviewer subagent unavailable**: skip review, note in build-log "unreviewed task". Status: DONE_WITH_CONCERNS.
- **Test suite breaks during task**: revert task, mark BLOCKED, investigate via `/li:investigate`.
- **A blocking compliance hook fires repeatedly**: STOP. Investigate why operator's content keeps triggering. Likely real issue.
- **Voice gate fails 3x for same artifact**: surface to operator, decide accept-with-caveat or re-write from scratch.

## Model selection strategy (from superpowers)

- **Mechanical task** (rename variable, add log line, single-file edit, simple test): Haiku
- **Multi-file integration** (add new endpoint touching 3-5 files): Sonnet
- **Architecture/design judgment** (changing data model, new module structure, security-critical): Opus

Plan.md should specify which model per task. If not specified, default Sonnet.

## Voice tier behavior

`voice: internal`. Code is engineering-internal. Customer-facing artifacts (if any in BUILD) flow through the active pack's voice gates (`resolve_pack_field voice.gates_active`; none by default).

## Cycle-position footer

Close your report with the shared position footer so the operator always knows where they are in the
cycle and the one logical next action — whether this phase ran standalone or inside `/li:cycle`:

```bash
source "$LINTEL_REPO_ROOT/lib/cycle-footer.sh"   # fallback: "$(git rev-parse --show-toplevel)/lib/cycle-footer.sh"
render_cycle_footer                               # reads .lintel/state/00-state.md; --compact for short replies
```

Skipped phases render `⊘`; ASCII via `LINTEL_ASCII=1`. See [ADR-0003](../../docs/adr/0003-cycle-position-footer.md).
