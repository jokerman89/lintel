# Planner-as-module — plan is a callable sub-workflow

**Last updated:** 2026-05-29 (v3.8 Feature 2 implementation)
**Status:** Concept doc — referenced by skills/plan/SKILL.md, skills/plan-eng-review/SKILL.md, skills/capture/SKILL.md, skills/cycle/SKILL.md

> Before v3.8, `plan` was Phase 4 of `cycle`. The cold-executor trio (plan.md + spec.md + prompt.md) was split — plan/spec born in PLAN, prompt born in CAPTURE. Standalone `/li:plan` invocations got 2/3 of a handoff. This concept doc captures v3.8 Feature 2's four sharpenings that make `plan` industry-best AND module-callable from other workflows.

## The four sharpenings

### 2.1 — `workflow_root: true` on plan's frontmatter

One-line frontmatter change in `skills/plan/SKILL.md`. Effect: PLAN becomes a first-class job when invoked standalone via the jobs system (Feature 1) — its own job folder, its own state, its own resumability.

```yaml
---
name: plan
layer: foundation
workflow_root: true              # ← new
description: ...
---
```

When operator runs `/li:plan <design.md>` outside a cycle, `job-begin` hook fires, spawns `~/.lintel/jobs/plan-<stamp>-<hash>/`, PLAN proceeds with full job tracking.

When PLAN runs INSIDE `/li:cycle` (Phase 4), the caller passes `--no-job` (or `NO_JOB=1`) so the hook short-circuits and no nested job is spawned.

### 2.2 — Move `prompt.md` generation from CAPTURE to PLAN

Before:

| Artifact | Where born | Where finalized |
|---|---|---|
| spec.md | PLAN (draft) | CAPTURE (finalize) |
| plan.md | PLAN | PLAN |
| **prompt.md** | **CAPTURE** | **CAPTURE** |

After (v3.8):

| Artifact | Where born | Where reaffirmed |
|---|---|---|
| spec.md | PLAN | CAPTURE (against build evidence) |
| plan.md | PLAN | CAPTURE (against build evidence) |
| **prompt.md** | **PLAN** | **CAPTURE** (annotate, not regenerate) |

**Why the move:**

1. **Architect-blueprint discipline.** The trio is the cold-executor handoff. It must be born together to be useful — a fresh AI session reading only the trio should be able to re-execute. If `prompt.md` is born in CAPTURE, a standalone `/li:plan` produces only 2/3 of the handoff.
2. **Module-callable contract.** Other workflows (Azure-e2e recipe, safe-install, future automation flows) want to call PLAN as a module and receive the complete trio. With Feature 2.2, that's the deterministic output contract.
3. **L-001 alignment.** PLAN is the layer where intent becomes executable spec. The prompt.md is THE handoff prose — it belongs in PLAN, not after the fact.

CAPTURE's new job for the trio: REAFFIRM. Verify spec.md still matches implementation. Annotate plan.md tasks with actual STATUS from build-log. Add post-build "What you DON'T need to know" entries to prompt.md. CAPTURE doesn't regenerate; it witnesses.

### 2.3 — Granularity hard check (LOCKED at 2–5 min per cold-subagent task)

The magic sauce in gstack, superpowers, Architect, and Lovable is not plan depth — it's task size. Small tasks = clean handoff = fewer errors. Operator-locked rule: **2–5 minutes per cold-subagent task, decompose otherwise.**

Implementation: `plan-eng-review` Step 0 (which is BLOCKING — already part of the plan-review flow) extended with a per-task time estimate + AskUserQuestion gate.

For each task in plan.md:
- Estimate cold-subagent implementation time (assuming subagent reads only the task spec + spec.md + prompt.md, no prior conversation).
- If estimate ≤5 min → PASS.
- If estimate >5 min → AskUserQuestion with two options:
  - **A) Decompose now** (preferred) — split into 2-N smaller tasks ≤5 min each.
  - **B) Accept with concern** — keep task; log concern in plan.md "Reviewer Concerns" section.

No batching. Per task. Mechanical.

### 2.4 — Module-callable from other workflows

With 2.1 + 2.2 + 2.3, PLAN becomes a callable sub-workflow:

#### Inside cycle (Phase 4)
```
/li:cycle → SENSE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE
                                          ▲
                                  reads DEFINE + DISCOVER from job dir
                                  --no-job to avoid nested job
```

#### Standalone
```
/li:plan <design.md>
   ↓
   workflow_root: true → job-begin → ~/.lintel/jobs/plan-<stamp>-<hash>/
   produces: plan.md + spec.md + prompt.md (the trio)
   handoff-size-check against 500k cap
   founder approval gate
   → DONE, ready for cold-executor handoff
```

#### Sub-module called by another workflow_root skill
```
/li:cycle-azure-e2e           OR    /li:safe-install
  ↓ discovery                        ↓ pre-flight
  CALL /li:plan --from <design>      CALL /li:plan --from <change-spec>
  ↓ receives trio                    ↓ receives trio
  proceed to BUILD with trio         proceed to execute with trio
```

#### Caller contract

The calling workflow passes:
- `--from <path>` — design doc or change-spec
- `--called-by <skill-name>` — sets `CALLED_BY` env so job.yaml records caller
- `--no-job` (recommended for nested calls) — short-circuits `job-begin` to avoid nested jobs

#### Output contract (deterministic for callers)

PLAN always emits at `<run-dir>/`:
- `plan.md` — task breakdown
- `spec.md` — engineering master spec
- `prompt.md` — cold-executor handoff prose

Callers can rely on these paths existing post-DONE. CAPTURE re-affirms but doesn't (re)generate.

## What this closes

| Operator goal | Solved by |
|---|---|
| "The magic sauce: a planner that breaks things down right" | 2.3 granularity hard check |
| "Clear hand-off between when plans are written and what is expected" | 2.2 trio born together |
| "Plan phase as a module, usable by the whole workflow or parts of it" | 2.4 module-callable |
| "Our planner phase with everything it entails — industry best" | 2.1 + 2.2 + 2.3 + 2.4 together |

## What this explicitly does NOT do

- Does not add new agents; reuses existing CodeReviewer / Architect / ReadOnly.
- Does not change cycle's overall flow — only re-points where prompt.md is born.
- Does not invent new gate types; granularity check piggybacks plan-eng-review Step 0.
- Does not auto-decompose; operator decides at each >5min task.

## Operator validation criteria

Once both features ship, success looks like:

1. `/li:status` at any moment shows exactly what curated flows are open.
2. An abandoned flow surfaces at next session-start.
3. `/li:plan <design.md>` standalone produces all three artifacts (spec, plan, prompt).
4. A future Azure-e2e recipe can call `/li:plan` as a sub-workflow without re-implementing planning.
5. No plan ships with a task estimated >5 min without operator explicitly accepting the concern.

## L-001 / L-002 / L-003 / L-004 application

- **L-001:** PLAN body is contract. Specific tasks decomposed at invocation. Don't pre-bake "what 5 min looks like" for every domain — the estimate is per-task at invocation time.
- **L-002:** before adding the granularity check, plan-eng-review's existing Step 0 was already BLOCKING with complexity check + completeness check. Granularity check is an additive rule, not a parallel system.
- **L-003:** when caller says "this task is 4 min," verify by sample sizing for the first 2-3 tasks. Operator estimates may be optimistic.
- **L-004:** PLAN is decision-layer (what tasks, what order, what spec). BUILD is execution-layer (writing the code). The trio is the contract between them — this is L-004 in action at the within-cycle level.

## See also

- `skills/plan/SKILL.md` — primary
- `skills/plan-eng-review/SKILL.md` — Step 0 granularity check
- `skills/capture/SKILL.md` — trio reaffirm (not regenerate) post-v3.8
- `skills/cycle/SKILL.md` — caller passes --no-job for Phase 4 invocation
- `docs/concepts/jobs-system.md` — the first half of this feature pair (Feature 1)
- `tasks/lessons.md` L-004 — separate decisions from execution
