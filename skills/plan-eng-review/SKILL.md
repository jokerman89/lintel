---
name: plan-eng-review
layer: foundation
description: Architecture + tests review. The required gate before /release-ev2. Covers arch, code quality, test coverage, performance.
color: red
tools: Read, Bash, Grep, Glob, Edit
voice: internal
cli_support: [claude-code, codex]
---

# /plan-eng-review

The **required** review per Lintel's Review Readiness Dashboard. Scope: architecture, code quality, test coverage, performance. Outputs a structured plan-file review report + persists via first-party `bin/li-review-log` so `/release-ev2` can read it.

Inspired-by gstack's equivalent. Lintel version adds:
- `cli_support` frontmatter check on every skill/agent the plan adds
- Voice-tier check on every customer-facing skill the plan adds
- 5-always-on compliance checklist gate inside Step 0

## When to use

- Before any non-trivial implementation begins
- Before `/release-ev2` — Dashboard verdict gate depends on this
- After any major plan revision (re-run, supersedes prior report)

## When NOT to use

- Trivial fix (typo, comment) — no plan involved
- Pure docs PR — `/review` is the lighter pre-landing alternative

## Inputs

- Optional path to a plan/design doc. Auto-discovers from `~/.gstack/projects/<slug>/*-design-*.md` if not provided.
- Optional `--scope diff` — review the current branch's diff instead of a plan doc (degrades to `/review` semantics).

## Workflow

### Step 0: Scope Challenge (BLOCKING — no review-section work until this resolves)

1. **What existing code partially solves each sub-problem?** Map reusable patterns.
2. **Minimum set of changes?** Ruthless about scope creep.
3. **Complexity check:** plan touches 8+ files OR introduces 2+ new classes/services?
   - If yes: AskUserQuestion proposing minimal version, ask reduce-or-proceed.
   - **STOP** until resolved.
4. **TODOS.md cross-reference:** any deferred items now blocking? Any items the plan SHOULD subsume?
5. **Completeness check:** is plan doing the complete version or a shortcut? With AI-assisted coding, completeness cost is 10-100x cheaper than human-team — recommend the lake, not the puddle.
6. **Distribution check:** new artifact type (binary, package, container)? CI/CD pipeline included or deferred?
7. **Granularity hard check (v3.8 Feature 2.3, LOCKED at 2–5 min per cold-subagent task):**
   For each task in plan.md, estimate cold-subagent implementation time. Apply the superpowers rule:
   - **Target: 2–5 minutes per task**, implementable by a single cold-subagent reading only the task spec + the spec.md + the prompt.md (no prior conversation context).
   - **Any task estimated >5 min** → AskUserQuestion with two options:
     - A) **Decompose now** — split the task into 2-N smaller tasks ≤5 min each. Preferred.
     - B) **Accept with concern** — keep the task; log the concern in plan.md "Reviewer Concerns" section.
   - Tasks <2 min are fine (combinable if useful, but no hard rule).
   - **This is mechanical — apply per task, no batching.**

   Rationale: small tasks = clean handoff = fewer errors. Source: superpowers SDD pattern + Architect-blueprint discipline. The cold-executor trio (plan.md + spec.md + prompt.md) lives or dies on per-task granularity.

### Sections 1-4 (after scope agreed)

Each section: ONE AskUserQuestion per issue. Never batch. Each option labeled by issue NUMBER + option LETTER.

1. **Architecture** — system design, dependency graph, data flow, scaling, security boundaries, ASCII diagrams worth embedding in code comments.
2. **Code quality** — DRY (aggressively flag), error handling, technical debt, over/under-engineering.
3. **Tests** — coverage diagram per Step 3 below; 100% coverage is the goal. Test plan artifact written.
4. **Performance** — N+1 queries, memory, caching opportunities, slow paths.

### Test Step 3 — coverage diagram (mandatory)

Trace every codepath the plan introduces. Map user flows + interaction edge cases. ★★★/★★/★ rating per existing test. Mark [→E2E] vs [→EVAL] vs unit. Output ASCII diagram.

**REGRESSION RULE (mandatory, no AskUserQuestion):** If the diff modifies existing behavior + test suite doesn't cover the changed path → regression test added as CRITICAL task.

### Optional: Outside voice

After all 4 sections: offer codex (or Claude subagent if codex unavailable) for independent challenge. Cross-model tension surfaced per topic via AskUserQuestion. User decides per tension point — outside voice is INFORMATIONAL, not auto-applied.

## Report format — written to the plan/design doc

```markdown
## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| Eng Review | /plan-eng-review | Architecture & tests (required) | N | CLEAR (PLAN) | M issues, K critical gaps |

**UNRESOLVED:** count
**VERDICT:** ENG CLEARED — ready to implement | NOT CLEARED — <reason>
```

Persist via first-party `bin/li-review-log` (legacy alias: gstack-review-log):
```bash
bin/li-review-log '{"skill":"plan-eng-review","timestamp":"...","status":"...","unresolved":N,"critical_gaps":N,"issues_found":N,"mode":"FULL_REVIEW","commit":"..."}'
```

## Required outputs

- **NOT in scope** section — explicit deferrals with one-line rationale.
- **What already exists** — reuse map.
- **TODOS.md updates** — one AskUserQuestion per proposed TODO (never batch).
- **Failure modes** — per new codepath: realistic failure + test? + err handling? + silent vs visible. Critical gaps flagged.
- **Worktree parallelization** — dependency table + lanes + execution order + conflict flags.
- **Implementation Tasks** — flat list, each derived from a finding (no padding). JSONL artifact via `jq -nc` for /autoplan aggregation.
- **Completion Summary** — section-by-section issue counts + Lake Score (X/Y recommendations chose complete).

## Compliance integration

- The 5 always-on rules run at Step 0 (no customer data in plan prose, no secrets, no production mutations without auth, MS SSO+zero retention, first-party-first).
- Per Lintel v1: also verify every new skill/agent introduced declares `cli_support` in frontmatter (per C1) and `voice` tier (per A6).

## Exit Plan Mode Gate (BLOCKING)

Before `ExitPlanMode`:

1. Read the plan file. Confirm LAST `## ` heading is `## GSTACK REVIEW REPORT`.
2. Report contains: Runs/Status/Findings table + VERDICT line.
3. `bin/li-review-log` called + `bin/li-review-read` consumed at least once.

Failing this gate + calling `ExitPlanMode` = contract violation. User sees a plan with a missing/stale report + rejects it.

## Voice tier note

`voice: internal` — direct, builder-talking-to-builder. No Trailblazer overhead.

## Failure modes

- **No design doc:** offer `/office-hours` as prerequisite. If user skips, proceed with standard review against the diff.
- **Operator skips a per-issue AskUserQuestion:** mark as unresolved decision, list in "Unresolved decisions that may bite later" at end.
- **jq missing:** skip JSONL write, warn user — markdown task list still primary deliverable.

## Examples

**Healthy clear:**
```
> /plan-eng-review
[Step 0 + 4 sections, 6 issues resolved]
✓ ENG CLEARED — ready to implement
Tasks: 17 in markdown + JSONL
Dashboard updated
```

**Scope reduction:**
```
> /plan-eng-review
[Step 0 complexity check fired — 140-file scope]
AskUserQuestion: reduce-or-proceed?
Operator: proceed (Path C accepted)
[continue 4 sections]
```

## See also

- `/plan-ceo-review` — strategy review (runs before this)
- `/plan-design-review` — UI/UX review (parallel if there's a UI surface)
- `/review` — diff-scoped lighter variant (when plan-eng-review is overkill)
- `/release-ev2` — reads this skill's review-log output as ship-gate signal
- `/autoplan` — chains office-hours → ceo-review → eng-review → design-review
