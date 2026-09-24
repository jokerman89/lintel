---
name: analyze
layer: foundation
description: Use to check that PLAN and BUILD still match the approved DEFINE design — run when a plan was revised or a build deviated, to catch drift between what was approved and what shipped. Checks the DEFINE-PLAN-BUILD legs and authority alignment, writes a severity-classified report, and is re-runnable read-only at any cycle point.
color: red
tools: Read, Bash, Grep, Glob, Write
voice: internal
cli_support: [claude-code, codex, copilot]
necessity: RECOMMENDED
gap_if_skipped: "Plan revisions and BUILD deviations go unreconciled against the design doc — drift between what was approved and what shipped is detected only by accident (the spec-kit /analyze hole, Convergent #6)."
---

# /analyze

Cross-artifact consistency check across the cycle's contract chain: the APPROVED design doc
(DEFINE) ↔ the cold-executor trio (PLAN) ↔ the build-log + tree (BUILD), plus alignment with
authority docs (ADRs, CLAUDE.md constraints). Read-only on the repo; writes exactly one
report at the selected cycle's explicit runtime path (for example
`.claude/runtime/state/<cycle-id>-analyze-report.md`). Retain prior-cycle reports;
the old `analyze-report.md` path is readable history, not automatic current evidence.

## When to use

- After any plan revision (re-run; the report supersedes the prior one)
- After BUILD completes or deviates (the PLAN↔BUILD leg — BUILD's final pass calls this)
- Before SHIP, when the operator wants a consistency verdict alongside the review gates
- Standalone, any time: "does what we have still match what we approved?"

## When NOT to use

- As a substitute for `/li:plan-eng-review` (that is quality judgment; this is coverage mechanics)
- Mid-task inside BUILD (per-task review is 3b-guard + two-stage review territory)
- When no design doc or plan exists yet — there is nothing to cross-check; run the cycle phases first

## Inputs (read-only)

Use the [shared work-map contract](../spec-kit/references/work-map.md) and
`bin/li-work-artifacts.py --repo <target> --map <selected> --view context`.
Verify the saved profile through `workflow_resume` before consuming its requirements.
ANALYZE uses the same explicit selection as PLAN/BUILD/CAPTURE; it never selects
the newest design, report or sibling file.

If a required artifact/evidence source is missing, mark the affected leg INCOMPLETE
with its path and reason. Do not convert a skipped/missing leg into GREEN. A leg can
be not-applicable only with a grounded phase/scope reason (e.g. BUILD has not started
at plan-time). This does not stop independent read-only analysis of available inputs.

| Artifact | Source |
|---|---|
| Requirements/design | Mapped `spec`/`plan` and explicitly linked approved design |
| Tasks and handoff | Mapped `tasks`/`prompt`; original IDs and task source, not a presumed plan.md checklist |
| Discover report | Exact report linked by the selected cycle's DISCOVER entry or mapped handoff |
| Build evidence | Selected cycle/package/leaf build-log entries and actual selected tracked/dirty/new-file evidence |
| Authority docs | Mapped constitution, relevant repository instructions and ADRs selected with P03's actual Markdown/YAML metadata reader |

## The three legs

**Leg 1 — DEFINE↔PLAN** (plan-time; what PLAN Step 8 delegates here):
- Every selected requirement maps to at least one original mapped task (coverage)
- Every design decision is tasked or explicitly deferred — including decisions not phrased as
  requirements (the old Step 8 "design decisions not yet tasked" check)
- No original task lacks a traceable requirement (no untasked scope creep into the plan)
- Design decisions marked LOCKED are not contradicted by any task
- Mapped task dependencies are consistent with the linked discover-report ADR constraints

**Leg 2 — PLAN↔BUILD** (post-build):
- Every mapped leaf has attributable build evidence/status (DONE / DONE_WITH_CONCERNS /
  BLOCKED); BLOCKED is unresolved work, not accepted completion
- No commits in the cycle's range fall outside any task's scope (untasked work shipped)
- Deviations (BLOCKED tasks, DONE_WITH_CONCERNS) are reflected back: design doc amended, plan
  annotated, or an explicit operator gap-acceptance recorded

**Leg 3 — Authority alignment** (both times):
- Nothing in the mapped design/tasks or built tree contradicts an Accepted ADR;
  unknown metadata remains visible rather than silently removing the document
- CLAUDE.md frozen zones (pack contract, frontmatter contracts, AGENT-INSTRUCTIONS) untouched
  unless the plan explicitly declared a meta-infra change with its M1 artifact

## Report format (persisted)

Write the selected report path and link it from this cycle's ledger/handoff. Do not
overwrite another initiative's report or carry its accepted findings into this one:

Record `analyze_report_path` through `state_append ANALYZE <actual-status>` after
the report is persisted. After `workflow_resume`, the consumer reads that exact
`state_cycle_field analyze_report_path` and checks the report's map/profile/package/
leaf identity. Missing or mismatching evidence remains INCOMPLETE, not a stale
global GREEN. ANALYZE is a utility entry and does not move the canonical phase.

```
# analyze-report
ts: <timestamp>
trigger: standalone | plan-step8 | build-final
work_map: <exact original work.json>
artifacts: <original spec/plan/tasks/prompt paths>
package_id: <selected package>
leaf_ids: [<original IDs>]
profile: <actually verified P07 reference>
required_policy: <unchanged P05 bridge>
legs_checked: [define-plan, plan-build, authority]
legs_incomplete: [<missing required evidence and reason>]
verdict: GREEN | YELLOW | RED | INCOMPLETE

| # | Severity | Leg | Finding | Artifact:line | Suggested action |
|---|----------|-----|---------|---------------|------------------|
```

Severity rubric: **P1** = a contradiction (task vs LOCKED decision, ADR violation, untasked
shipped work) → verdict RED. **P2** = a coverage gap (requirement with no task, task with no
terminal status) → YELLOW unless operator-accepted. **P3** = traceability nits → GREEN-with-notes.

**Supersede rule:** a re-run explicitly supersedes the same work/phase report, but operator-accepted findings carry forward
(re-emit them marked `accepted <date>`, excluded from the verdict) — an acceptance recorded at
plan-step8 must survive the build-final re-run, or accepted gaps re-flag forever.

Verdict is **advisory**: RED does not hard-block — surface it and let the operator decide
(defer to backlog / amend plan / accept gap), exactly like PLAN Step 8's existing protocol.
A pack may wire a hard gate via `compliance.hooks`; the neutral `_default` pack does not.

## Anti-patterns

- Do NOT fix anything found — this skill reports; the operator or the owning phase acts.
- Do NOT re-litigate design quality — wrong-shaped-but-consistent is GREEN here (quality is
  plan-eng-review's lens).
- Do NOT hide missing required artifacts as skipped success. Preserve a partial report
  with INCOMPLETE legs and the exact missing sources; it is not clearance.
- Do NOT compute a separate acceptance hash. When binding evidence, use P05 `bind_work`
  and the shared review/QA contract, including immutable obligations.

## Cycle-position footer

Close your report with the shared position footer. Outside an active cycle it renders the thin
ambient line; inside one it shows the operator's position + next step:

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/lib/cycle-footer.sh"
render_cycle_footer                               # auto: thin when no cycle, full/--compact when in one
```

See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
