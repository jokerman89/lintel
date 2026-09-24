# Handoff

## Delivered
A finished frontend-only support dashboard in index.html, styles.css and app.js, using the unchanged synthetic tickets.js fixture. It includes a selected-customer view, total/active/resolved metrics, a daily created-ticket chart, status breakdown, intersecting filters, ticket results, responsive layout and filtered CSV download.

## Run
Open index.html directly in a current browser. No server, package installation, network connection or external assets are required. Choose Northwind or Contoso, filter by status/severity, search by ID/subject, and optionally supply inclusive UTC dates. Clear filters preserves the customer. Export CSV downloads only the visible matching set, in stable fixture order.

Active means New plus Investigating. All outputs use the same filtered set. Dates and daily grouping use UTC; CSV retains original timestamps. Blank date bounds are unrestricted. Formula-like export cells are prefixed with an apostrophe; quotes, commas and newlines are escaped. Source fixtures remain untouched.

## Verification
Completed locally on 2026-09-20 using installed Node and Playwright Chromium:

- `verify.mjs`: **14/14 PASS**, no browser errors. Covers launch, customer/default counts, active definition, UTC offset boundaries, combined filters, empty states, charts, CSV rows/escaping/formula protection, text-only rendering, labelled controls, responsive overflow, clearing and pilot boundary.
- `verify-extra.mjs`: **6/6 check groups PASS**, including all 32 customer/status/severity combinations, reversed-date recovery, empty header-only downloads, one-sided inclusive dates, trimmed search, visible keyboard focus, unchanged in-memory fixture content and malformed-source error handling.
- Visually inspected `common-1440.png` and `common-390.png`: clear hierarchy, readable count/date labels, no overlapping controls, wrapped fixture subjects and mobile ticket cards. Rounded status percentages initially summed to 101%; changed to one decimal place and re-ran both browser suites successfully. No browser-test failures occurred.
- Compared starter file SHA-256 hashes before/after: AGENTS.md, implementation-prompt.md, stakeholder-answers.md, tickets.js and verify.mjs all unchanged. See starter-hashes.json and starter-integrity.json. The supplied CI configuration was also left unchanged.

Evidence: common-verification.json, extra-verification.json, common-1440.png and common-390.png. Re-run with `node verify.mjs` and `node verify-extra.mjs` where the installed Playwright runtime is available; both scripts include the recording host's existing runtime fallback. No packages were installed.

The host's standard image-view helper failed before reading the screenshots; a permitted local file read displayed those same generated images for visual review. This did not affect the app or browser tests. Remote CI, Firefox/WebKit, screen-reader behavior and opening CSV in spreadsheet applications were not tested. No independent review is claimed.

## Limitations and production boundary
This is a local synthetic pilot. Both customers' data are present in the browser; customer selection is not a security boundary. Production requires server-side authorization and data isolation. There is no login, backend, persistence, real customer data, paging or live updates. Search trims outer whitespace. Invalid or reversed date ranges show zero outputs with an error and disable export. Empty valid results may export column headings only. Dates accept four-digit years.

## Next steps
Run assistive-technology checks and broader browser coverage before widening the pilot. Agree a backend/API contract and implement authenticated server-side authorization and data isolation before introducing real customer data. Decide whether persistence, sorting or pagination are needed using pilot feedback.

