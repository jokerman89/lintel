---
name: jstack-plan-design-review
description: UI/UX gaps review for plans with a frontend surface. Skip for backend/infra/CLI-only work.
color: orange
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code]
---

# /plan-design-review

Visual + interaction review of a plan that introduces or changes a UI surface. Optional — only fires when the plan touches frontend components, CSS, views, user-facing flows, or any rendered output.

JStack version inspired-by gstack's `/plan-design-review` but written fresh. Stays internal voice (design critique among builders).

## When to use

- Plan adds/changes user-facing UI (web, mobile, CLI prompts with rendering)
- Plan changes a customer-facing screen flow
- Existing design review predates significant frontend changes (staleness)

## When NOT to use

- Backend-only changes — no design surface
- Pure infra (Bicep, Terraform, GitHub Actions) — `/plan-eng-review` covers
- Prompt/LLM-only changes — `/customer-voice-check` is the relevant eval

## Inputs

- Optional path to a plan/design doc with UI scope. Auto-discovers from `~/.gstack/projects/<slug>/*-design-*.md` if not provided.

## Workflow

Score against **6 design pillars** (each 1-10):

1. **Information hierarchy** — what does the user see first/second/third? Does importance match visual weight?
2. **Interaction states** — loading, empty, error, success, partial, hover, disabled — all designed for?
3. **Edge case paranoia** — 47-char name, zero results, 10k results, network fail, slow connection, stale data, double-click, navigate-away-mid-op?
4. **Subtraction default** — Rams "as little design as possible." Every element earns its pixels?
5. **Trust** — every UI element builds or erodes trust. Where does trust break?
6. **Accessibility** — contrast, keyboard nav, screen reader, focus management, reduced motion?

Each pillar gets a score + 2-4 specific findings. Per finding: AskUserQuestion with options (recommended fix / alternative / defer-to-TODOS / no-action).

After scoring: **overall_score = average** of 6 pillars.

## Report format

```markdown
## Design Review — <plan title>

| Pillar | Initial | After fixes | Findings |
|---|---|---|---|
| Information hierarchy | 6/10 | 8/10 | 2 |
| Interaction states | 7/10 | 7/10 | 0 |
| Edge case paranoia | 5/10 | 7/10 | 3 |
| Subtraction default | 8/10 | 8/10 | 1 (deferred) |
| Trust | 7/10 | 8/10 | 1 |
| Accessibility | 4/10 | 7/10 | 4 |

**Overall:** 6.2/10 → 7.5/10 (after 11 decisions made)
**Critical gaps:** 0
**Unresolved:** 1 (subtraction-default — operator deferred to v1.1)
```

Persist:
```bash
~/.claude/skills/gstack/bin/gstack-review-log '{"skill":"plan-design-review","timestamp":"...","status":"...","initial_score":N,"overall_score":N,"unresolved":N,"decisions_made":N,"commit":"..."}'
```

## Visual sketch + outside voices (optional)

If the plan benefits from visual exploration: invoke `design` binary (if `~/.claude/skills/gstack/design/dist/design` exists) to generate ASCII / HTML wireframes for the proposed UI. Otherwise skip — `/plan-design-review` is primarily critique, not generation.

Outside voices (Codex + Claude subagent) can propose alternative design directions. Always informational — user decides.

## Compliance integration

- If the plan is customer-facing: design output must pass `/customer-voice-check` if any Trailblazer-tier copy is included.
- If the plan involves data display: confirm sensitivity labels carry through from source to UI.

## Voice tier note

`voice: internal` — review prose is builder-to-builder. But this skill OFTEN finds issues in `voice: trailblazer` output (e.g., a UI button using generic AI copy). When it does: cross-reference `/customer-voice-check` for the copy itself.

## Failure modes

- **No design doc:** offer `/office-hours` first.
- **Plan has no UI surface:** report "no UI scope detected, skipping. Use /plan-eng-review for non-UI plans."
- **Operator skips per-finding AskUserQuestion:** marks as unresolved decision, lists at end.

## Examples

**Backend plan invokes /plan-design-review by mistake:**
```
> /plan-design-review
✗ No UI scope detected in current plan.
  Backend-only or infra plans don't need /plan-design-review.
  Use /plan-eng-review (required) instead.
```

**UI plan, healthy review:**
```
> /plan-design-review
[6 pillars scored, 11 findings discussed]
✓ Overall: 6.2 → 7.5/10
  11 decisions, 1 deferred
  Dashboard updated
```

## See also

- `/plan-eng-review` — runs in parallel for arch + tests
- `/design-review` — diff-scoped lighter variant (when plan-design-review is overkill)
- `/design-consultation` — interactive design partner mode
- `/customer-voice-check` — eval UI copy when Trailblazer-tier
