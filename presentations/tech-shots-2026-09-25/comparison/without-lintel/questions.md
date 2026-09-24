# Questions and answers

The stakeholder was unavailable. The answers below are from stakeholder-answers.md, not an invented conversation.

| Question | Answer and source |
|---|---|
| Who is the audience and default customer? | Support leads; Northwind by default, with Contoso as the other customer. Stakeholder: Who and why / Filters and data contract. |
| What is active? | New plus Investigating; Resolved is excluded, even with a Resolved-only filter. Stakeholder: What does active mean? |
| Which outputs do filters affect? | Every KPI, chart, result count and CSV uses the exact same filtered set. Stakeholder: Filters and data contract. |
| What date boundary applies? | Inclusive UTC creation dates, including offset timestamps; blanks are unbounded. Stakeholder: Filters and data contract. |
| How should search behave? | Case-insensitive matching on ticket ID and subject. Stakeholder: Filters and data contract. |
| What belongs in CSV? | id, customer, subject, status, severity, createdAt, preserving original timestamps with correct quoting and formula neutralization. Stakeholder: Export and suspicious data. |
| Does customer selection enforce access? | No; both customers' synthetic data are in the browser. Production requires server-side authorization and data isolation. Stakeholder: Scope and trust boundary. |
| What happens when clearing? | Preserve the selected customer and clear other filters. Stakeholder: Interaction. |

## Implementation assumptions
- Show tickets in stable fixture order; no sort control is requested.
- Trim outer search whitespace for convenient pasted queries.
- Invalid or reversed date ranges show a corrective message, zero results and disable export until corrected, avoiding an apparently valid report.
- A valid empty result can export a CSV containing only the column headings.
- Show all three status categories, including zero counts; show only actual matching UTC days in the trend.
- Keep selections in memory for this page session only. No persistence or backend is needed.
- Reject malformed fixture data with a visible error instead of silently omitting records.

No unresolved stakeholder decision blocks this local pilot.
