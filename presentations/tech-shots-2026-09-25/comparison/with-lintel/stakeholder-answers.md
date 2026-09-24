# Stakeholder answers — available equally to both builders
These are prepared answers, not a transcript. Read whichever sections help resolve your questions.

## Who and why
The audience is a support lead comparing a synthetic customer-support pilot. Northwind and Contoso are the two customers. A useful first result is a trustworthy view of the selected customer's backlog and filtered tickets, rather than a decorative executive dashboard.

## What does active mean?
Active means New plus Investigating. Resolved tickets are not active. There should also be a total-ticket count and a status breakdown so that the count can be reconciled.

## Filters and data contract
A customer must always be selected; default to Northwind. No cross-customer "All" view is required. Offer status (All/New/Investigating/Resolved), severity (All/Critical/High/Normal), free-text search, and inclusive start/end date filters. Dates are UTC dates of createdAt, including records near midnight with timezone offsets. Search should match ticket ID and subject without case sensitivity. Blank dates mean unbounded.

Every KPI, graph, result count and CSV export must be derived from the exact same filtered set. Active on a Resolved-only filter is zero. Show a clear message and zero metrics when no tickets match. The daily trend is created-ticket count, with no invented data points. Counts by day must use UTC, just like the date filter.

## Export and suspicious data
CSV includes id, customer, subject, status, severity and createdAt, in a stable order. Export only the filtered rows; retain the original timestamp. Correctly quote commas, double quotes and newlines. Text could include HTML-looking content or spreadsheet formula prefixes. Display it as text, and neutralize formula-like CSV cells (leading =, +, -, @, including after whitespace) so spreadsheet apps do not execute them. These intentionally suspicious fixtures are synthetic test inputs.

## Interaction
Use native labelled controls, visible keyboard focus and readable chart labels or an equivalent text summary. The layout must remain usable at 390px and 1440px widths. When a customer/filter changes, all output should update together. Clearing filters preserves the selected customer.

## Scope and trust boundary
This is a frontend-only local pilot. Both customers' synthetic data are in the browser. A customer selector is NOT authorization, tenant isolation or production security. The UI and handoff must explicitly say that production needs server-side authorization and data isolation. Do not build authentication or claim that this pilot enforces tenant security.

## Delivery
No specific visual style or implementation architecture is mandated. Use your engineering judgment. Meaningful automated checks, a documented smoke test, or both are welcome. Record the actual verification you ran, including failures or limitations. The next engineer should understand how to run it, its definitions and what is not production-ready.
