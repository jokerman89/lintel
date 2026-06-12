# ADR-NNNN: <Short decision title>

- **Status:** Proposed
- **Date:** YYYY-MM-DD
- **Deciders:** <names or roles>
- **Supersedes:** —
- **Superseded by:** —

## Context

What is the situation? What forces are at play (technical, organizational, regulatory)? What constraints are non-negotiable? Cite sources when constraints are contested.

Keep this section concrete. "We need to store user data" is not context. "We need to store EU user data under GDPR, and our current vendor is US-only" is.

## Decision

What did we decide. State it in one or two sentences. Past tense once accepted ("We chose Postgres on managed AWS RDS").

## Alternatives considered

The serious options that were on the table. For each, one or two sentences on why it was not chosen. Do not list strawmen — only options a reasonable person could have picked.

- **Option A**: <one-line summary>. Rejected because <reason>.
- **Option B**: <one-line summary>. Rejected because <reason>.

## Consequences

What this decision commits us to. Both directions:

- **Positive**: <what becomes easier or possible>
- **Negative**: <what becomes harder or impossible; what we have to pay for>
- **Neutral**: <what changes that is not strictly good or bad>

## Implementation notes (optional)

If the decision implies non-obvious migration steps, sequencing, or feature-flag work, sketch it here. Keep brief — full plans go in `.claude/plans/todo.md` while the work is active.

## References

- Linked ADRs, RFCs, design docs, vendor docs.
- Tickets that capture the original ask.
