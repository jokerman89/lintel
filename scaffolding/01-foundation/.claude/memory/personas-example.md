# Persona: Example Operator

This is a reference example for the persona format used in `.claude/memory/personas.md`. Adapt the structure — every field is optional, but the more you fill in, the more useful the persona is at session start.

This persona is anonymized. Do not put real customer names, internal MS account names, or PII in a persona file that lives in a shared repo.

---

## Role

Senior Engineer, hybrid IC + tech-lead responsibilities. Owns a specific subsystem end-to-end (design → build → operate). Reports into an EM but operates with high autonomy.

## Background

- 10+ years engineering, mixed languages (Python, Go, TypeScript). Recent tilt toward distributed-systems + platform work.
- Comfortable on the command line. Treats the terminal as the primary workspace.
- New-ish to AI-assisted development (under one year). Treats AI as a tool, not an oracle — wants citations and verification, not confident assertions.

## What this person owns

- Architecture decisions in their subsystem.
- On-call rotation for the same subsystem.
- Mentoring two ICs on the same team.

## Communication preferences

- **Direct.** Bottom-line up front, supporting detail after. No throat-clearing.
- **Concrete.** File paths, function names, exact commands — not "the auth module" or "run the tests".
- **Honest about uncertainty.** When the assistant does not know, it should say so and propose how to find out. Confident hedging is worse than admitting ignorance.
- **No corporate vocabulary.** "Comprehensive", "robust", "leverage" — avoid.
- **Swedish or English** depending on the conversation. The assistant should match the language the operator opens with.

## What this person cares about

- **Subtraction bias.** A change that removes code is usually better than a change that adds code.
- **Verification before done.** Tests, behavior diffs, actual side-effects observed. Green tests are a floor, not a ceiling.
- **Documenting non-obvious decisions.** ADRs for anything that will be re-litigated.
- **Long-term repo health** over short-term sprint velocity.

## What this person avoids

- Speculative abstractions ("we might need this later").
- Defensive code for impossible conditions.
- Comments that restate what the code does.
- Multi-file PRs that bundle unrelated changes.

## How the assistant should work with this person

- Plan first for any non-trivial task (3+ steps or architectural decision). Stop and re-plan if the plan goes wrong mid-execution.
- Use subagents to keep main context clean.
- Mark TODOs complete as they finish — not in a batch at the end.
- For UI/frontend work, drive a real browser to verify; do not claim "looks good" without screenshots.
- Capture a one-line lesson in `.claude/memory/lessons.md` after any correction.

## What this person will NOT delegate

- Strategic scope decisions (what to build).
- Architecture decisions that touch ownership boundaries between teams.
- Customer-facing copy beyond a starting draft.

## Notes

- Edits to this file are versioned. When the role or preferences shift, do not delete the old text — date it and supersede.
