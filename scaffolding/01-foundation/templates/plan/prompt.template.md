<!--
  Canonical prompt.md template — the cold-executor handoff prompt.
  Source of truth for PLAN's prompt.md (skills/plan/SKILL.md Step 11 references this file).
  Born in PLAN (v3.8 Feature 2.2), not CAPTURE. It is the IRREDUCIBLE handoff: a fresh
  AI session reading only this prompt + the linked spec.md + plan.md should be able to
  re-execute or extend the work without prior context.
  Design: .claude/engineering/design-archive/lintel-scope-and-scaled-planning-design.md §3.3
-->
# Cold-Executor Prompt — <wedge title>

This file is a SELF-CONTAINED prompt. A fresh AI session reading only this prompt + the linked spec.md + plan.md should be able to re-execute or extend this work without prior context.

## Context

<2-3 paragraphs: what this is, what it accomplishes, what business outcome it serves.>

## Constraints

- Must respect: <list constraints from the design doc>
- Must NOT: <list explicit anti-requirements>
- Compliance: <active pack's gates — resolve_pack_field compliance.hooks; none by default>
- Voice tier: <active pack's voice tier — resolve_pack_field voice.default_tier; default internal>

## Acceptance criteria (verify)

- [ ] <criterion 1 — concrete, testable>
- [ ] <criterion 2>

## Deliverables

- spec.md (this directory)
- plan.md (this directory)
- Code as per spec
- Tests with N% coverage
- Documentation per plan.md task X

## How to re-execute

1. Read spec.md fully
2. Read plan.md
3. Run /li:cycle --from BUILD (skip DEFINE/PLAN, they're done)
4. Apply two-stage review per task
5. Run /li:qa final
6. Ship per /li:ship

## What you DON'T need to know

- This cycle's specific operator preferences (in lessons.md)
- This cycle's prior failures (in build-log if needed)
- The full conversation history that produced this

This prompt is the IRREDUCIBLE handoff. Everything needed is here or in the linked files.
