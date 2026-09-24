# Questions and resolutions

Prepared source answers, not a stakeholder conversation.

| Question | Resolution | Basis |
|---|---|---|
| What does active mean? | New + Investigating | Stakeholder: What does active mean? |
| Can customers be combined? | Always one customer; Northwind default | Stakeholder: Filters and data contract |
| Which date/time and boundaries? | Inclusive UTC creation dates; blanks unbounded | Stakeholder: Filters and data contract |
| What updates with filters? | All metrics, graphs, result count and export use identical rows | Stakeholder: Filters and data contract |
| Which fields are searchable? | Ticket ID and subject, case insensitive | Stakeholder: Filters and data contract |
| How should suspicious content behave? | Literal text; CSV formulas neutralized, CSV syntax escaped | Stakeholder: Export and suspicious data |
| Does the selector provide tenant security? | No; production requires server-side authorization and data isolation | Stakeholder: Scope and trust boundary |
| Which result order? | Newest creation first, then ID; CSV follows table | Implementation assumption; reversible presentation choice |
| What if dates are reversed? | Explain error, show zero results until corrected or cleared | Implementation assumption; avoids misleading totals |
| What if no rows match? | Explain empty state; zeros; allow header-only CSV | Empty state explicit; export detail implementation assumption |
| Is persistence required? | No; refresh restores defaults | Implementation assumption; no requirement supplied |

No unresolved decision blocks this authorized local build.
