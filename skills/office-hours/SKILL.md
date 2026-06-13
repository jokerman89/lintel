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

The design-doc generator. Takes an unstructured problem statement and produces a structured design document with: context, goals, premises, decisions, risks, scope, and a forcing-question section. Output lands at `~/.lintel/projects/<slug>/<user>-<branch>-design-<datetime>.md` and is the input to `/plan-ceo-review` and `/plan-eng-review`.

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

## Workflow

1. **Locate or create project dir.** `~/.lintel/projects/<slug>/` based on repo name + branch. Create if absent.
2. **Read context.** Project CLAUDE.md, any `--reference` files, recent commits for repo state.
3. **Structured intake.** Via AskUserQuestion, gather:
   - One-line goal
   - Primary user task affected
   - Constraints (technical, business, voice, compliance)
   - Three plausible directions (operator names them, skill expands)
4. **Generate sections:**
   - **Context** — current state, what's broken, what's working
   - **Goals** — outcome statements, measurable where possible
   - **Premises** — explicit assumptions, called out so they can be challenged
   - **Decisions Pending** — numbered D1, D2... with three alternatives each
   - **Out-of-Scope** — explicit list of what's excluded and why
   - **Risks** — known unknowns, dependencies, single-points-of-failure
   - **Forcing Questions** — 3-5 questions that, if not answered, block implementation
5. **Write doc.** Atomic write to `~/.lintel/projects/<slug>/<user>-<branch>-design-<datetime>.md`.
6. **Set status.** Doc header includes `Status: DRAFT`. Operator marks `APPROVED` after addressing forcing questions.
7. **Report path + next step.**

## Output structure

```markdown
---
title: <one-line>
status: DRAFT
created: 2026-05-27T17:42:00Z
user: jokerman
branch: main
slug: jokerman-lintel
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
- Doc lives at `~/.lintel/projects/` (local). Optional sync to brain repo if configured.
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
[Intake interview, 4 questions]
✓ Doc: ~/.lintel/projects/.../jokerman-main-design-20260527-174200.md
  Status: DRAFT (operator marks APPROVED after addressing forcing questions)
  Next: /plan-ceo-review on this doc.
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

- `/plan-ceo-review` — next step in the plan chain
- `/plan-eng-review` — required review gate, appends the REVIEW REPORT
- `/autoplan` — orchestrates this skill + reviews in one chain
- `/design-consultation` — exploratory discussion before committing to a design doc
