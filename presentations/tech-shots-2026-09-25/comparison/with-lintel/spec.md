# Dashboard specification

Status: authorized local implementation, grounded in stakeholder-answers.md.

- Default Northwind; customer always selected (Northwind / Contoso). Clear retains customer.
- Status All/New/Investigating/Resolved; severity All/Critical/High/Normal; case-insensitive ID/subject search; inclusive UTC creation dates; blank dates unbounded.
- A single filtered set supplies all numbers, daily creation counts, status counts, results and CSV. Active = New + Investigating. No fabricated trend points. Resolved-only active = 0.
- Export id, customer, subject, status, severity, createdAt in that order; preserve source timestamps; quote commas/quotes/newlines and prefix spreadsheet formulas with an apostrophe, including whitespace-prefixed formulas.
- Treat all ticket fields as untrusted text. Keep window.TICKETS unchanged. Opening index.html directly must work without dependencies or network.
- Clear empty state with zero metrics. Invalid/reversed ranges show a meaningful error and no misleading results.
- Native labelled controls, visible keyboard focus, readable date/count and status/count chart text. Usable at 390px and 1440px.
- UI and handoff explicitly state synthetic browser data is not tenant security; production needs server-side authorization and data isolation.
- Preserve starter fixtures, requirements, browser tests and CI. Run verify.mjs locally; remote CI is not run.

Implementation choices: newest-created-first table and matching CSV order; UTC dates labelled throughout; all three statuses remain in breakdown at zero; an empty CSV contains the header. Source-data errors fail closed with visible feedback. No persistence required.
