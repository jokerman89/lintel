---
name: plan-eng-review
layer: foundation
description: Use to review a plan or change for engineering soundness before it ships — covers architecture, code quality, test coverage, and performance. The required gate before SHIP; reach for it when a design or implementation needs a rigorous technical pass.
color: red
tools: Read, Bash, Grep, Glob, Edit
voice: internal
cli_support: [claude-code, codex, copilot]
hop_in: no
---

# /plan-eng-review

Engineering planning review: architecture, code quality, test coverage and
performance. Keep the structured report and actual evidence, not a legacy dashboard
string. Apply [task-relevant intake](../define/references/intake.md) and
[P05 evidence](../review/references/evidence.md). A plan-quality pass alone does not
clear implementation, independent review or delivery.

The architecture-and-tests gate before build — the one review Lintel requires. On top of the architecture/quality/coverage/performance pass it also runs:
- `cli_support` frontmatter check on every skill/agent the plan adds
- Voice-tier check on every customer-facing skill the plan adds
- the active pack's compliance gates as a checklist inside Step 0 (`resolve_pack_field compliance.hooks`; none by default)

## When to use

- Before any non-trivial implementation begins
- Before ship — Dashboard verdict gate depends on this
- After any major plan revision (re-run, supersedes prior report)

## When NOT to use

- Trivial fix (typo, comment) — no plan involved
- Pure docs PR — `/review` is the lighter pre-landing alternative

## Inputs

- Explicit plan/design path or the same selected work map as PLAN/BUILD. No
  freshest-global-design or newest-directory discovery.
- Optional `--scope diff` — review the current branch's diff instead of a plan doc (degrades to `/review` semantics).

For mapped work, validate the explicitly selected work.json with `bin/li-work-artifacts.py`
and use the [shared work-map contract](../spec-kit/references/work-map.md). Read design from
`plan`, requirements from `spec` and leaf IDs/checkboxes from `tasks`. Package membership in
the design or linked handoff references those original IDs; do not generate a parallel task
list or require a Lintel approval heading inside Spec Kit's technical plan. Ungrouped tasks
use singleton packages. Honor the same selection as PLAN/BUILD, never the newest directory.

## Workflow

### Step 0: Scope Challenge (BLOCKING — no review-section work until this resolves)

1. **What existing code partially solves each sub-problem?** Map reusable patterns.
2. **Minimum set of changes?** Ruthless about scope creep.
3. **Complexity check:** plan touches 8+ files OR introduces 2+ new classes/services?
   - If yes: inspect the aggregate risk and simpler alternatives. Ask reduce-or-proceed
     only if scope is actually unresolved; retain an already approved large scope.
4. **Original task-source cross-reference:** any deferred items now blocking?
   Propose scope changes explicitly, without a second TODOS backlog.
5. **Completeness check:** does the plan deliver its requested outcome or leave an
   unacknowledged shortcut? Prefer complete acceptance without inventing productivity ratios.
6. **Distribution check:** new artifact type (binary, package, container)? CI/CD pipeline included or deferred?
7. **Granularity hard check (2–5 min per verifiable leaf):**
   For every leaf in plan.md, estimate implementation time from its specification and linked context:
   - **Target: 2–5 minutes per leaf**, described precisely enough to implement without prior conversation context.
   - **Any leaf estimated >5 min** → AskUserQuestion with two options:
     - A) **Decompose now** — split the task into 2-N smaller tasks ≤5 min each. Preferred.
     - B) **Accept with concern** — keep the task; log the concern in plan.md "Reviewer Concerns" section.
   - Tasks <2 min are fine (combinable if useful, but no hard rule).
   - Evaluate every leaf; grouping into a work package does not waive this check.

8. **Work-package review:** apply the [shared package contract](../../docs/concepts/planner-as-module.md#work-packages).
   Verify one outcome, common write owner/edit boundary, connected dependencies and acceptance
   evidence for every unchanged leaf ID. Split across different owners, security boundaries,
   irreversible decisions or independent rollback boundaries. No arbitrary package size limit.
   Check aggregate complexity: a multi-file package cannot be classified mechanical solely
   because its leaves are small. Packages execute sequentially, their leaves in dependency order;
   one package spec review precedes one quality review, with findings mapped back to leaves.
   A package is incomplete while any leaf lacks verification. Older ungrouped plans use singleton
   packages. The plan table does not create new job state or claim automatic enforcement.

### Sections 1-4 (after scope agreed)

Use numbered findings and label decision options by issue NUMBER + option LETTER. Present
related findings together and request only unresolved decisions; retain each finding's affected
package/leaf IDs so a shared review cannot hide gaps.

1. **Architecture** — system design, dependency graph, data flow, scaling, security boundaries, ASCII diagrams worth embedding in code comments.
2. **Code quality** — DRY (aggressively flag), error handling, technical debt, over/under-engineering.
3. **Tests** — risk/acceptance coverage diagram per Step 3 below; distinguish covered,
   missing and unobservable behavior rather than imposing an unexplained percentage.
4. **Performance** — N+1 queries, memory, caching opportunities, slow paths.

### Test Step 3 — coverage diagram (mandatory)

Trace every codepath the plan introduces. Map user flows + interaction edge cases. ★★★/★★/★ rating per existing test. Mark [→E2E] vs [→EVAL] vs unit. Output ASCII diagram.

**REGRESSION RULE (mandatory, no AskUserQuestion):** If the diff modifies existing behavior + test suite doesn't cover the changed path → regression test added as CRITICAL task.

### Optional: Outside voice

Use an available, authorized independent host reviewer or an explicit external/manual
handoff. Keep the same original map, profile, scope and evidence. Do not require a
vendor/model name or invent a command. Surface actionable disagreement; ask only
unresolved material choices. The implementer cannot supply its own independence.

## Report format — written to the plan/design doc

```markdown
## REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| Eng Review | /plan-eng-review | Architecture & tests (required) | N | CLEAR (PLAN) | M issues, K critical gaps |

**UNRESOLVED:** count
**VERDICT:** ENG CLEARED — ready to implement | NOT CLEARED — <reason>
```

Persist via first-party `bin/li-review-log`:
```bash
review_source="${LINTEL_SOURCE_ROOT:?select trusted source}"
python="${LINTEL_PYTHON:-python3}"
"$python" "$review_source/bin/li-review-evidence.py" validate \
  --record "${review_record:?set actual v2 decision}" || exit $?
bash "$review_source/bin/li-review-log" --file "$review_record" || exit $?
bash "$review_source/bin/li-review-read" --skill plan-eng-review \
  --expected "${review_context:?set prepared context}" \
  --corroboration "${corroboration:?set actual independent receipt}" --gate-json
```

Run both helpers from the selected source bundle. `LINTEL_REPO_ROOT` selects the
working repository, not helper code. Prepare the context with the shared `prepare`
command **before** actual review, retaining immutable `qa_requirements`, original
leaf coverage and the verified P07 reference/required-policy bridge. Then author
the observed v2 decision; this persistence block is not a fabricated result template.
Use same-context QA/SHIP only after applicable review/acceptance is actually complete.

For a draft design or unmapped read-only pass, use P05 `snapshot` then `inspect`
with actual controls. It needs no duplicate backlog and returns
`release_clearance:false`. Old positive-string/empty-commit records remain history,
not approval. A standalone direct verify cannot establish latest-log clearance.

## Required outputs

- **NOT in scope** section — explicit deferrals with one-line rationale.
- **What already exists** — reuse map.
- **Original mapped task updates/proposals** — trace deferrals by existing ID and
  resolve any missing scope decision without duplicating the backlog.
- **Failure modes** — per new codepath: realistic failure + test? + err handling? + silent vs visible. Critical gaps flagged.
- **Worktree parallelization** — dependency table + lanes + execution order + conflict flags.
- **Implementation Tasks** — unchanged leaf IDs, each derived from a finding (no
  padding), grouped by bounded work package in the original plan/task artifact.
  Autoplan consumes canonical PLAN; no parallel JSONL task authority is produced.
- **Completion Summary** — section-by-section issue counts + Lake Score (X/Y recommendations chose complete).

## Compliance integration

- The active pack's compliance gates run at Step 0 (`resolve_pack_field compliance.hooks`; none by default). The advisory baseline still applies — no customer data in plan prose, no secrets, no production mutations without auth.
- Per Lintel v1: also verify every new skill/agent introduced declares `cli_support` in frontmatter (per C1) and `voice` tier (per A6).

## Report completion and host plan mode

Before reporting a planning review complete:

1. Read the selected plan and report. A native design can append `## REVIEW REPORT`
   when authorized; preserve external Spec Kit structure and use an explicitly linked
   report instead of forcing a last-heading convention into it.
2. Report contains: Runs/Status/Findings table + VERDICT line.
3. For bound review, the actual writer and latest applicable reader consume the
   prepared context. For inspection, report its limited non-clearance result.

Use native plan UI only when available and permitted. There is no Universal
`ExitPlanMode` requirement; its absence does not remove the artifact or review gates.

## Failure modes

- **No design doc:** offer `/office-hours` as prerequisite. If user skips, proceed with standard review against the diff.
- **Operator skips a per-issue AskUserQuestion:** mark as unresolved decision, list in "Unresolved decisions that may bite later" at end.
- **Required evidence persistence fails:** report the error and leave review open;
  never skip the write into an apparent clearance.

## Examples

**Healthy clear:**
```
> /plan-eng-review
[Step 0 + 4 sections, 6 issues resolved]
✓ ENG CLEARED — ready to implement
Tasks: 17 original IDs in the selected task artifact
Observed report and shared evidence linked; release clearance remains separate
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
- `/ship` — reads this skill's review-log output as ship-gate signal
- `/autoplan` — chains office-hours → ceo-review → eng-review → design-review
