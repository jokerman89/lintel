# Planner-as-module — plan is a callable sub-workflow

**Last updated:** 2026-09-08 (short leaves, bounded work packages)
**Status:** Concept doc — referenced by skills/plan/SKILL.md, skills/plan-eng-review/SKILL.md, skills/capture/SKILL.md, skills/cycle/SKILL.md

PLAN is callable on its own or within a cycle. It produces the complete cold-executor trio
(plan.md + spec.md + prompt.md), preserves short, verifiable leaves and groups connected work
into bounded packages for execution and review.

## The four sharpenings

### 2.1 — `workflow_root: true` on plan's frontmatter

The frontmatter in `skills/plan/SKILL.md` declares PLAN eligible to own a job when invoked
through the jobs system. It does not itself create a job or register a host hook.

```yaml
---
name: plan
layer: foundation
workflow_root: true              # ← new
description: ...
---
```

When invoked through an active jobs integration, standalone PLAN can use its own job folder
and tracking. Automatic job spawning remains opt-in under ADR-0008; do not claim a hook fired
merely because `workflow_root: true` is present.

Inside a cycle, reuse the caller's active job rather than creating a nested job. Existing
integrations may pass `--no-job` (or `NO_JOB=1`) for this purpose.

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

### 2.3 — Short, verifiable leaves

Each leaf remains targeted at **2–5 minutes of implementation**. At flat/phased depth a task
is a leaf; at tree depth a subtask is a leaf. Every leaf retains its ID, owner/edit boundary,
requirements, dependencies, observable acceptance, verification procedure and evidence.

`plan-eng-review` Step 0 evaluates every leaf. A leaf estimated above five minutes must be
decomposed or explicitly accepted with its concern recorded, using the existing gate.
This is an instruction-driven judgment, not a timed runtime validator. Grouping leaves does
not weaken the check. Time estimates appear in output only when requested.

### Work packages

The operator-selected hybrid model keeps leaves as the verification/progress unit and uses
packages (`P1`, `P2`, …) as the execution/review unit. A package has:

- One observable outcome, with acceptance evidence mapped to every included leaf.
- The same accountable write owner and permitted edit boundary across its leaves.
- Connected dependencies, with leaf IDs unchanged and internal execution in dependency order.

Split packages at different owners, security boundaries, irreversible decisions or independent
rollback boundaries. Choose boundaries from the work; no fixed count or duration makes a package
appropriate. A single leaf is a valid package. For existing plans with no grouping, treat each
leaf as a singleton package without rewriting IDs or creating a second task list.

The canonical plan template records package ID, outcome, leaf IDs, owner/edit boundary,
dependencies and acceptance evidence. Every leaf belongs to exactly one package. Derive package
dependencies from the leaf graph and check both for cycles or hidden later-package dependencies.
Packages execute sequentially; this grouping does not authorize concurrent editors.

BUILD performs one spec-compliance pass followed by one quality pass for the combined package;
review findings reference the affected leaf IDs. Judge complexity on the complete package,
not the apparent simplicity of each leaf. Recheck affected work after corrections. A package
cannot be DONE until every leaf's acceptance is verified with evidence and the package reviews
pass. Unverified or blocked leaves cannot disappear behind an aggregate success label.

This is a planning and dispatch instruction contract. The package table and optional package
annotation in build-log do not add a new job schema, automated dispatcher, approval gate or
replacement for existing leaf statuses/resume pointers. The implementation role and review
separation follow the host's actual capabilities and the BUILD skill.

### 2.4 — Module-callable from other workflows

With 2.1 + 2.2 + 2.3, PLAN becomes a callable sub-workflow:

#### Inside cycle (Phase 4)
```
/li:cycle → SENSE → SCOPE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE
                                          ▲
                                  reads DEFINE + DISCOVER from job dir
                                  --no-job to avoid nested job
```

#### Standalone
```
/li:plan <design.md>
   ↓
   workflow_root: true (job tracking only when invoked through an active integration)
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
- `plan.md` — short leaves, bounded package grouping, acceptance and evidence mapping
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
- Does not change the cycle's phase order or its approval gates.
- Does not invent new gate types; granularity check piggybacks plan-eng-review Step 0.
- Does not hide oversized leaves inside a package; the existing decomposition/concern gate applies.

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
- `.claude/memory/lessons.md` L-004 — separate decisions from execution
