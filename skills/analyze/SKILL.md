---
name: analyze
layer: foundation
description: Cross-artifact consistency gate (ADR-0004, adopted from spec-kit /analyze) — checks DEFINE↔PLAN↔BUILD legs + authority alignment, persists a severity-classified report to .lintel/state/analyze-report.md. Read-only on the tree; re-runnable at any cycle point. Delegated to by PLAN Step 8 and BUILD's final pass.
color: red
tools: Read, Bash, Grep, Glob, Write
voice: internal
cli_support: [claude-code, codex]
necessity: RECOMMENDED
gap_if_skipped: "Plan revisions and BUILD deviations go unreconciled against the design doc — drift between what was approved and what shipped is detected only by accident (the spec-kit /analyze hole, Convergent #6)."
---

# /analyze

Cross-artifact consistency check across the cycle's contract chain: the APPROVED design doc
(DEFINE) ↔ the cold-executor trio (PLAN) ↔ the build-log + tree (BUILD), plus alignment with
authority docs (ADRs, CLAUDE.md constraints). Read-only on the repo; writes exactly one
artifact: `.lintel/state/analyze-report.md`.

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

Resolve each; if one is absent, mark its legs SKIPPED in the report (never fail on a missing
artifact — report honestly what could not be checked):

| Artifact | Source |
|---|---|
| Design doc | newest `docs/design/*-design-*.md` or the doc named in `00-state.md` DEFINE entry |
| Cold-executor trio | `plan.md` + `spec.md` + `prompt.md` (paths from `00-state.md` PLAN entry) |
| Discover report | `discover-report.md` (ADR constraints list) |
| Build evidence | build-log entries + `00-state.md` BUILD entry + `git log`/`git diff` over the cycle's commits |
| Authority docs | `docs/adr/*.md` (Accepted), CLAUDE.md frozen zones |

## The three legs

**Leg 1 — DEFINE↔PLAN** (plan-time; what PLAN Step 8 delegates here):
- Every design-doc requirement maps to ≥1 plan.md task (coverage)
- No plan task lacks a traceable design requirement (no untasked scope creep into the plan)
- Design decisions marked LOCKED are not contradicted by any task
- plan.md dependencies consistent with discover-report ADR constraints

**Leg 2 — PLAN↔BUILD** (post-build):
- Every plan.md task has a terminal build-log status (DONE / DONE_WITH_CONCERNS / BLOCKED — none missing)
- No commits in the cycle's range fall outside any task's scope (untasked work shipped)
- Deviations (BLOCKED tasks, DONE_WITH_CONCERNS) are reflected back: design doc amended, plan
  annotated, or an explicit operator gap-acceptance recorded

**Leg 3 — Authority alignment** (both times):
- Nothing in plan.md or the built tree contradicts an Accepted ADR
- CLAUDE.md frozen zones (pack contract, frontmatter contracts, AGENT-INSTRUCTIONS) untouched
  unless the plan explicitly declared a meta-infra change with its M1 artifact

## Report format (persisted)

Write `.lintel/state/analyze-report.md`:

```
# analyze-report
ts: <timestamp>
trigger: standalone | plan-step8 | build-final
legs_checked: [define-plan, plan-build, authority]   # SKIPPED legs listed with reason
verdict: GREEN | YELLOW | RED

| # | Severity | Leg | Finding | Artifact:line | Suggested action |
|---|----------|-----|---------|---------------|------------------|
```

Severity rubric: **P1** = a contradiction (task vs LOCKED decision, ADR violation, untasked
shipped work) → verdict RED. **P2** = a coverage gap (requirement with no task, task with no
terminal status) → YELLOW unless operator-accepted. **P3** = traceability nits → GREEN-with-notes.

Verdict is **advisory**: RED does not hard-block — surface it and let the operator decide
(defer to backlog / amend plan / accept gap), exactly like PLAN Step 8's existing protocol.
A pack may wire a hard gate via `compliance.hooks`; the neutral `_default` pack does not.

## Anti-patterns

- Do NOT fix anything found — this skill reports; the operator or the owning phase acts.
- Do NOT re-litigate design quality — wrong-shaped-but-consistent is GREEN here (quality is
  plan-eng-review's lens).
- Do NOT fail on missing artifacts — mark legs SKIPPED with the reason; a partial check
  honestly labeled beats a crash.

## Cycle-position footer

Close your report with the shared position footer. Outside an active cycle it renders the thin
ambient line; inside one it shows the operator's position + next step:

```bash
source "$LINTEL_REPO_ROOT/lib/cycle-footer.sh"   # fallback: "$(git rev-parse --show-toplevel)/lib/cycle-footer.sh"
render_cycle_footer                               # auto: thin when no cycle, full/--compact when in one
```

See [ADR-0003](../../docs/adr/0003-cycle-position-footer.md).
