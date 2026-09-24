# Implementation plan

## Acceptance criteria
- Open index.html offline with no dependencies or browser errors.
- Default to Northwind; one selected customer, intersecting status, severity, case-insensitive ID/subject search and inclusive UTC creation dates.
- Derive counts, actual-day trend, status breakdown, ticket rows and CSV from one filtered set. Active = New + Investigating.
- Render fixture text literally; quote CSV values and neutralize spreadsheet formula prefixes.
- Provide labelled native controls, visible focus, meaningful empty/error states and usable 390px/1440px layouts.
- State the local synthetic pilot boundary in the UI and handoff.

## Build cards
- [x] Read authoritative brief, stakeholder answers, fixture and shared tests.
- [x] Record resolved questions and implementation decisions.
- [x] Build accessible responsive dashboard shell and styling.
- [x] Implement validation, shared filtering/rendering and CSV download.
- [x] Run supplied browser checks unchanged; inspect desktop/mobile screenshots.
- [x] Run additional checks for invalid ranges, empty export and filtered reconciliation.
- [x] Finish handoff with actual evidence, limitations and next steps.

## Verification
Run the supplied verify.mjs with the installed Node/Playwright runtime, retain its report and screenshots, and inspect any failures. Add bounded checks for behaviors not covered by the supplied suite. Preserve original starter files. No git, remote CI, installation, network or deployment.

## Review
Completed: all 14 unchanged shared browser checks and all 6 additional check groups passed in local Chromium with no browser errors. Additional coverage includes 32 filter combinations, date-error recovery, header-only downloads, single date bounds, keyboard focus, immutable fixtures and malformed-source handling. Desktop and mobile screenshots were visually inspected. Starter hashes match their initial values. Status percentages were refined to one decimal place after visual review; both suites passed afterward. No browser-test failures occurred. Remote CI, other browsers, screen readers and opening CSV in spreadsheet applications remain unverified. This is one implementer's work; no independent review is claimed.

