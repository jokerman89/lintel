# Curated Lintel workflow context

Apply these source-grounded process instructions to this local build. This is a bounded adaptation, not an installed plugin run. Source revision 275a35447c4ad271e05816ade43ac48f1acec24f.

## Local execution adaptation
The operator already authorized this local pilot build. Write all artifacts inside this arm only; do not use shared repo runtime paths or change Lintel. The scope is a local frontend pilot, not infrastructure. Work in short, checkable leaves grouped into coherent implementation/review packages; minute estimates are planning heuristics, not measured guarantees. Questions use the same supplied stakeholder-answers.md available to the baseline; do not invent extra facts. Carry out inline plan/spec and quality reviews; no independent reviewer is available in this build lane, so label them self-reviews. A common independent behavioral evaluation happens after both runs freeze. Capture only justified candidate lessons and proposed decisions locally; do not promote global knowledge. No full cycle shell helper, hook, pack or cloud enforcement is invoked.


## SCOPE — skills/scope/SKILL.md:15-19

## What this skill does

Turns a raw request into a **sized, disambiguated scope**. One responsibility: take the operator's prompt + the orientator's route (from SENSE) and produce a `scope.md` carrying the resolved size, the chosen reading, and the `depth_schema` that drives PLAN.

SCOPE is the canonical home for the **scale axis** + the **clarifying gate** (design §3.2). It is deliberately *light* — the failure mode is ceremony (R1). It is read-only except for emitting `scope.md`, runs the mechanical estimator first, and pauses **only** when the request is genuinely bimodal.


## SCOPE — skills/scope/SKILL.md:83-86

**Mechanical-first, agent on escalation (decision 1B):**

- **If `scale_amb=no`** (clear): **no question.** `chosen_reading` = the single reading. If `scale_size` is `L`/`XL`, note in the SCOPE report that PLAN will use a deeper `depth_schema` — but do not interrupt. Clear small requests feel nothing (success criterion 2; risk R1).
- **If `scale_amb=yes`** (bimodal): **you (the agent) are the escalation.** Judge the request's two plausible readings, give each a sharp label + size, and fire **exactly one** AskUserQuestion — the clarifying gate. Example for "deploy a website to azure":


## PLAN — skills/plan/SKILL.md:70-73

**Existing authorization:** record the operator's authorized scope before the gates below.
Present plan signals and a reviewable plan, but do not ask again for execution already explicitly
authorized in this session. Ask once when a material scope/authority decision remains unanswered.
Approval does not extend to production actions, secrets or unrelated work.


## PLAN — skills/plan/SKILL.md:94-128

### Step 2 — Plan-eng-review (engineering plan)

Invoke `/li:plan-eng-review` skill (or inline equivalent).

Output: task list with for each task:
- Task ID
- Title (verb + object)
- Target file path(s)
- Dependency on prior tasks
- Acceptance criteria (test or verify command)
- Estimated tokens + minutes
- Complexity (mechanical / multi-file / architecture)
- Recommended subagent (per discover-report's mapping)

Rule (from superpowers): each task should be 2-5 minutes of implementer time. Bigger = decompose.

### Step 3 — Plan-design-review (if frontend in scope)

If design doc indicates UI/frontend work, invoke `/li:plan-design-review`:
- Design system implications
- Accessibility considerations
- Visual sketch (if needed) via `/li:design-html` or `/li:design-review`

Add design tasks to plan.

### Step 4 — Plan-devex-review (always)

Invoke `/li:plan-devex-review`:
- Operator-DX implications (will this be painful to use later?)
- Documentation needed
- Telemetry hooks needed
- Test coverage gaps

Add DX-improving tasks to plan.



## PLAN — skills/plan/SKILL.md:224-240

### Step 9 — Adversarial two-stage review (adopted from superpowers)

Dispatch CodeReviewer subagent (or general-purpose) with plan.md path:

**Stage 1 — Spec compliance review:**
"Does plan.md match design doc requirements exactly? Coverage gaps? Tasks not traceable to design?"

If Stage 1 finds issues: fix (Edit tool), re-dispatch. Max 3 iterations.

**Stage 2 — Quality review (only after Stage 1 PASS):**
"Are tasks well-decomposed? Deps correct? Costs realistic? Test coverage adequate? Edge cases addressed?"

If Stage 2 finds issues: fix, re-dispatch. Max 3 iterations.

Convergence guard: if same issues persist across 3 iterations, surface as "Reviewer Concerns" in plan.md and proceed.

If subagent unavailable: skip review, note in plan.md "Adversarial review unavailable — plan unreviewed."


## PLAN — skills/plan/SKILL.md:285-287

**Depth-parametric rendering (design §3.3).** Read `depth_schema` from `scope.md` (emitted by the SCOPE phase) and render the `plan.template.md` section that matches. The 2-5 min granularity rule applies to the **leaf** (task at flat/phased, subtask at tree) — hierarchy adds milestones, it does not weaken the leaf check. `plan-eng-review` Step 0's BLOCKING per-leaf check stays.

- **`flat`** (XS/S — today's shape): one task table, IDs `T1, T2, …`.


## PLAN — skills/plan/SKILL.md:354-358

**prompt.md** (canonical, `.claude/plans/<slug>/prompt.md`) — from `prompt.template.md` — **v3.8 Feature 2.2: born in PLAN, not CAPTURE.**

It is a SELF-CONTAINED prompt: a fresh AI session reading only this prompt + the linked spec.md + plan.md can re-execute or extend the work without prior context. See `prompt.template.md` for the full skeleton (Context / Constraints / Acceptance criteria / Deliverables / How to re-execute / What you DON'T need to know).

The trio (plan.md + spec.md + prompt.md) is the cold-executor handoff contract. Born together in PLAN — from the versioned templates above — so standalone planner-module invocations (`/li:plan <design.md>` without a surrounding cycle) produce a complete handoff. CAPTURE re-affirms the trio (verifies presence, updates with final-build evidence) but no longer generates prompt.md.


## REVIEW — skills/review/SKILL.md:103-134

### Step 2 — Stage 1: Spec compliance review

Dispatch CodeReviewer agent (or general-purpose):

Prompt:
"Review the diff against plan.md. For each task in plan.md, verify the implementation matches requirements EXACTLY. Be strict. 'Close enough' is not acceptable. Output:
- Per-task: PASS or list deviations with file:line + suggested fix
- Aggregate: total tasks PASS / total deviations / spec-compliance score
Be terse. Don't praise."

If Stage 1 FAILS:
- Surface per-task deviations
- AskUserQuestion: fix now (loop back to BUILD with fix-list) / defer with ADR / accept-risk
- Most cases: fix loop. Re-dispatch Stage 1 review. Max 3 iterations.

### Step 3 — Stage 2: Code quality review (ONLY after Stage 1 PASS)

Dispatch CodeReviewer agent:

Prompt:
"Review the diff for quality. Dimensions:
- Correctness (logic, edge cases, error handling)
- Security (injection, secrets, auth, OWASP)
- Performance (N+1, hot paths, memory)
- Code style (naming, structure, DRY)
- Test coverage (happy path, edge cases, regression)

For each finding: P1 (block ship) / P2 (must fix) / P3 (nit). Include file:line + concrete fix. Confidence per finding. Be terse."

If Stage 2 FAILS:
- P1 findings BLOCK — fix loop required
- P2 findings: AskUserQuestion fix now / defer


## CAPTURE — skills/capture/SKILL.md:89-103

### Step 2 — Lessons capture (filtered)

Invoke `/li:learn` (or inline):

For each correction operator made during the cycle:
- Was this correction GENERAL (would apply to future work) or SPECIFIC (one-time)?
- If GENERAL: candidate for `.claude/memory/lessons.md`
- If SPECIFIC: keep in this cycle's notes only

Examples of LESSON-worthy:
- "Don't mock the vendor SDK in tests — last 3 cycles' tests passed but prod failed because mocks diverged from real API"
- "Always map the codebase first when planning infra work — saved 90 min on this engagement"

Examples NOT lesson-worthy:
- "Use specific port 8443 in this customer's deployment" — too specific


## CAPTURE — skills/capture/SKILL.md:140-155


### Step 4 — ADR draft (if non-trivial decision)

Scan cycle history for non-trivial decisions:
- Architectural picks (alternative A vs B chosen)
- Pattern adoptions (new pattern introduced)
- Trade-off decisions (accepted P3 finding, deferred P2)
- Scope changes (descoped feature, added scope)

For each candidate, AskUserQuestion: "Draft ADR for this decision?"

If yes: invoke `/li:adr-new "<decision title>"`:
- Reads `.claude/decisions/TEMPLATE.md`
- Auto-numbers (NNNN)
- Substitutes title + date + status (Proposed)
- Operator fills Context / Decision / Consequences / Alternatives during draft


## CAPTURE — skills/capture/SKILL.md:183-197

**`spec.md` reaffirm** (born in PLAN):
- Verify spec.md still matches actual implementation
- Update interfaces/contracts that drifted during BUILD (annotated as post-build-evidence)
- Status: APPROVED (from PLAN) — unchanged unless drift detected

**`plan.md` reaffirm** (born in PLAN):
- Annotate plan.md tasks with actual STATUS (DONE/SKIPPED/DEFERRED) from build-log
- Acceptance criteria post-verification (which actually passed)

**`prompt.md` reaffirm** (born in PLAN, v3.8 Feature 2.2 moved birth to PLAN):
- Verify prompt.md still describes the work accurately
- Add any "What you DON'T need to know" entries discovered during BUILD
- Path: `.claude/plans/<slug>/prompt.md` (born by PLAN, lives there)

**Why moved to PLAN:** standalone `/li:plan <design.md>` (workflow_root post-v3.8) needs to produce the complete trio at PLAN-time. CAPTURE-only generation broke that — operator running PLAN solo got 2/3 of a handoff. Trio born together fixes this.


## CAPTURE — skills/capture/SKILL.md:233-234

Never claim independent review when the same identity implemented and reviewed a lane. Honest
degradation is part of the durable outcome, not a concern to hide.
