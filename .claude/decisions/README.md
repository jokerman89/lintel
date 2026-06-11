# Architecture Decision Records

This directory holds the architectural decisions that shape this project. Each ADR captures **one** decision — what we chose, why, and what we knowingly traded off.

## Why ADRs

Decisions get re-litigated when nobody remembers why they were made. ADRs are the canonical record so:

- A new contributor can understand the shape of the system without asking the original author.
- A future self can reconsider a decision with the original constraints visible.
- The assistant has a stable reference to cite ("this conflicts with ADR-0007") instead of restating policy from memory.

## When to write one

Write an ADR when:

- A choice is non-trivial to reverse (schema, persistence, framework, language, deploy target).
- A constraint or trade-off is non-obvious from reading the code.
- A decision will outlast the current task or sprint.
- A stakeholder asks "why did we do it that way" more than once.

Do **not** write an ADR for:

- A bug fix.
- A purely tactical refactor that does not change the contract.
- A reversible choice with no downstream consequences.

## How to write one

1. Copy [TEMPLATE.md](TEMPLATE.md) to `NNNN-short-kebab-title.md`. Use the next available number, zero-padded to four digits.
2. Fill in the sections — keep it short. An ADR longer than two screens is usually two ADRs.
3. Start at status `Proposed`. Move to `Accepted` when the decision is in effect.
4. When superseded, change status to `Superseded by ADR-NNNN` and link the new ADR. Do not delete superseded ADRs — they are the history of why the current decision exists.

## Numbering

Sequential, never reused. Gaps are fine (deleted drafts leave gaps). Filename pattern: `0001-database-choice.md`, `0002-auth-strategy.md`, etc.

## Status values

- `Proposed` — drafted, not yet in effect.
- `Accepted` — in effect.
- `Superseded by ADR-NNNN` — replaced. Link to the replacement.
- `Deprecated` — no longer applies but was not directly replaced (e.g., the subsystem was removed).

## Index

Maintain the index by running `ls docs/adr/*.md` — no separate file. Filenames carry both number and title.

## Convention notes

- Past tense in "Decision" once accepted ("We chose Postgres").
- Active voice. No editorial hedging — if the decision is made, state it.
- Quote constraints from real sources (Slack, Jira, customer email) when the constraint is contested.
