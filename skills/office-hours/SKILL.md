---
name: office-hours
layer: foundation
description: Use to turn a rough problem statement into a structured, decision-gated design doc ready for engineering review. Reach for it when you have a problem to think through but no plan yet, and want the design pinned down before committing to architecture.
color: purple
tools: Read, Write, Bash, Glob, Grep
voice: internal
cli_support: [claude-code, codex]
---

# /office-hours

An exploratory intake entry into DEFINE/PLAN. Preserve structured context, goals,
premises, alternatives, risks and genuinely unresolved questions. Apply
[task-relevant intake](../define/references/intake.md) and the
[selected work-map contract](../spec-kit/references/work-map.md). Output is the
same explicit repository-local design path DEFINE uses, not a global project store.
Engineering review remains available; venture strategy review is opt-in.

## When to use

- New feature, big idea, or non-trivial change with multiple plausible directions
- Before any implementation, want to lock scope + decision rationale in writing
- Initial step of `/autoplan` chain
- Greenfield project setup — first design doc establishes the foundation

## When NOT to use

- Trivial fix or small change — `/plan-eng-review` against the diff is enough
- Plan already exists — skip to the review skills
- Brainstorming only, no commitment intended — use `/design-consultation` instead

## Inputs

- Required: the problem statement (inline prose or path to a draft markdown)
- Optional `--scope <area>` — narrow the design to a specific surface (e.g. "billing", "portal-auth")
- Optional `--reference <files>` — additional context files to read in (existing ADRs, codebase docs, prior designs)
- Optional `--mode <full|minimal>` — `full` (default) runs all sections; `minimal` skips Risks + Forcing Questions for small designs
- Optional `--map <work.json>` / `--lens venture` — retain existing work or select
  the venture lens explicitly; neither changes authority or auto-approves a draft

## Workflow

1. **Select the initiative.** Use `bin/li-work-artifacts.py --view context` for an
   existing map, or choose the same `.claude/plans/<initiative>/design.md` used by
   DEFINE for new work. Never choose by basename, branch freshness or modification time.
2. **Read context.** Project CLAUDE.md, any `--reference` files, recent commits for repo state.
3. **Structured intake.** Read existing evidence/answers first; ask only missing
   material decisions through the actual host channel. Useful inputs are:
   - One-line goal
   - Primary user task affected
   - Constraints (technical, business, voice, compliance)
   - Viable alternatives and their trade-offs (derive from evidence; do not require
     the operator to invent three alternatives as an interview step)
4. **Generate sections:**
   - **Context** — current state, what's broken, what's working
   - **Goals** — outcome statements, measurable where possible
   - **Premises** — explicit assumptions, called out so they can be challenged
   - **Decisions Pending** — numbered D1, D2... with three alternatives each
   - **Out-of-Scope** — explicit list of what's excluded and why
   - **Risks** — known unknowns, dependencies, single-points-of-failure
   - **Forcing Questions** — 3-5 questions that, if not answered, block implementation
5. **Write doc.** Use the selected DEFINE design path. Preserve its existing content,
   mapped task ownership and answered decisions.
6. **Set status.** A new exploratory design is DRAFT, not automatically APPROVED.
   Existing scoped approval survives unchanged input; material revisions identify
   exactly which approval needs renewal.
7. **Report path + next step.** Canonical DEFINE approval and PLAN produce/reconcile
   the original spec/plan/tasks/prompt/work.json. Office-hours does not create a
   parallel implementation backlog or another readiness verdict.

## Output structure

```markdown
---
title: <one-line>
status: DRAFT
created: 2026-05-27T17:42:00Z
user: <operator>
branch: <current branch>
slug: <selected initiative>
---

# <One-line goal>

## Context
...

## Goals
- G1: ...
- G2: ...

## Premises
- P1: ...
- P2: ...

## Decisions Pending

### D1: <one-line decision>
A) <option> — trade-off
B) <option> — trade-off
C) <option> — trade-off
Recommendation: A

### D2: <one-line decision>
...

## Out of Scope
- ...

## Risks
- R1: ...

## Forcing Questions
1. ...
2. ...

## REVIEW REPORT
[appended by /plan-eng-review — must be the LAST h2]
```

## Compliance integration

- Doc body sanity-scanned for Layer 2 patterns (secrets, customer-data, PII). BLOCK on hit.
- The design stays in the selected repository. External export/sync requires its
  own configured destination and authorization; none is activated here.
- Per Premise of repo policy: no customer data in design docs ever.

## Voice tier note

`voice: internal`. Design docs are engineering-internal. If the design covers a customer-facing surface, copy decisions reference the active pack's voice grid as a standard — but the design prose itself is internal.

## Failure modes

- **Problem statement too vague:** intake interview surfaces the gaps. If 3 rounds of clarifying questions don't produce enough signal: report STUCK + ask operator to draft a paragraph manually first.
- **No git repo detected:** doc still generated, slug derived from cwd. Report this clearly.
- **Doc already exists at target path:** ask whether to append, replace, or open new variant (`<ts>-v2.md`).
- **Forcing questions can't be generated honestly:** name that — sometimes the design is clear enough that no question is genuinely forcing.
- **Compliance scan hits on intake prose:** STOP, request sanitized restatement.

## Examples

**Standard:**
```
> /office-hours "new pricing page with tiered display"
[Only unresolved decisions are asked]
✓ Doc: .claude/plans/pricing-page/design.md
  Status: DRAFT (operator marks APPROVED after addressing forcing questions)
  Next: canonical DEFINE approval, then PLAN; strategy lens only if selected.
```

**With references:**
```
> /office-hours "billing refund flow rewrite" --reference docs/billing-adr.md docs/payment-provider.md
[Reads references, intake interview]
✓ Doc generated with references embedded.
```

**Minimal:**
```
> /office-hours "rename internal helper from getCwd to getCurrentWorkingDirectory" --mode minimal
[Skips Risks + Forcing Questions]
✓ Lightweight doc generated. Ready for /plan-eng-review.
```

## See also

- `/plan-ceo-review` — optional venture/strategy lens
- `/plan-eng-review` — required review gate, appends the REVIEW REPORT
- `/autoplan` — orchestrates this skill + reviews in one chain
- `/design-consultation` — exploratory discussion before committing to a design doc
