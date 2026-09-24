# Handoff

## Delivered and how to run

Open index.html directly in a modern browser. No server, installation, account or network is needed. index.html, styles.css and app.js are the implementation; tickets.js remains the supplied synthetic source. The dashboard provides customer selection, intersecting filters, total/active/critical/resolved counts, daily arrivals, status breakdown, searchable ticket results and CSV download. Mobile ticket cards preserve long and multiline subjects.

## Data definitions

- Default customer: Northwind. Selecting Contoso retains the other filters. Clear filters preserves the current customer.
- Active means New + Investigating. Every metric, graph, result count and CSV comes from the same filtered rows. Critical priority includes any Critical ticket in the view, regardless of status.
- ID and subject search is case insensitive; surrounding query whitespace is trimmed. Status, severity, search and inclusive date filters intersect. Blank dates are unbounded.
- Dates and daily groups use the UTC date of createdAt. Days without matching tickets are omitted. All three statuses remain visible at zero when appropriate.
- Tickets and CSV use newest creation time first, then ID. CSV columns are id, customer, subject, status, severity, createdAt. The original timestamp is retained. Quoting preserves commas, quotes and newlines; a leading apostrophe neutralizes formula prefixes, including prefixes after whitespace.
- Empty results have zero metrics, explicit feedback and a header-only CSV. Invalid date ranges or invalid source data show an error, zero results and disable export. Clear recovers from an invalid range; source corruption requires restoring tickets.js and reloading.

## Actual verification

Both suites ran locally in headless Chromium using the preinstalled Playwright runtime, directly from file URLs.

1. Supplied verify.mjs: 14/14 PASS, no browser errors, on 2026-09-20. Covers offline launch, customer totals, resolved-only active count, both timezone-offset boundaries, combined filters, empty states, chart reconciliation, exact CSV data/escaping, formula defense, literal markup, labelled controls, responsive widths, clear behavior and production disclosure. Evidence: common-verification.json.
2. Added verify-extra.mjs: 7/7 PASS, on 2026-09-20. Covers reversed-range recovery, each open date boundary, customer switching with filters, filtered chart reconciliation, actual header-only CSV download, keyboard skip link/focus, 1024px reflow, no HTTP(S) requests, and corrupt-source handling. Evidence: additional-verification.json.
3. Visually inspected common-1440.png and common-390.png. Controls, counts, graph labels, long literal subjects, mobile ticket cards and the production-boundary footer are visible, without clipping or page overflow. The screenshot tool initially hit a host filesystem helper error; reading the generated screenshots through the authorized local-file workaround allowed inspection. This was not an application failure.
4. Inline specification and quality self-review completed in review.md. No independent reviewer was available in this lane. Supplied tests and CI were preserved unchanged. No failing application check or corrective test rewrite occurred.

To reproduce with Node and Playwright already installed: run `node verify.mjs` and `node verify-extra.mjs` in this directory. On the recording host the Node executable is `node`; both runners contain the supplied host Playwright fallback. Do not install dependencies or access the network under this task's authorization.

Suggested manual demo: open index.html; confirm Northwind total 8 / active 5; choose Resolved and confirm active 0; clear; set both dates to 2026-09-19 and confirm three tickets; switch customers; try a search and CSV; narrow to 390px and read the ticket cards.

## Trust boundary and limitations

Both customers' synthetic data are in the browser. The customer selector is not security or tenant isolation. Production requires server-side authorization and data isolation. Authentication, a backend, live synchronization, persistence, pagination and production data handling are outside this pilot. It is intentionally sized for these fixtures.

Remote CI was not executed. Firefox, Safari, physical mobile devices, screen-reader output, and spreadsheet-application behavior were not exercised. Native table semantics, control labels and keyboard focus are present; this is not a full accessibility audit. Automated CSV assertions verify neutralized content and escaping, rather than certifying every spreadsheet application's import behavior. No source control or deployment was operated.

## Next engineer

Read spec.md, plan.md, questions.md and decision-log.md. prompt.md provides fresh-session instructions. All tasks are complete; no build blocker remains. Sensible next steps are stakeholder demo feedback, cross-browser/assistive-technology checks, and a separately authorized server-side design before considering real customer data. Do not infer production readiness from these local checks.
