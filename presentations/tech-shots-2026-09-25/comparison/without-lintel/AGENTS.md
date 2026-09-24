# Project engineering instructions

Build the support dashboard described in implementation-prompt.md. stakeholder-answers.md is authoritative project knowledge. Read it before implementing; distinguish stated facts from assumptions. Keep all work in this project.

## Engineering standard
Use a competent, maintainable implementation. Plan the work before editing, identify consequential ambiguity, and document decisions. Derive displayed metrics, graphs and exports from a coherent data/filter contract. Validate inputs and handle empty/error states. Treat fixture text as untrusted. Use accessible native controls, visible focus and responsive layouts. Avoid unnecessary dependencies or abstractions. This is a local synthetic pilot; do not imply production authentication or data isolation.

## Quality and execution
The shared browser tests in verify.mjs and the CI definition are part of this starter. Run the checks locally, inspect failures and fix the root cause, then re-run. You may add meaningful checks. Do not weaken or rewrite the supplied tests to make them pass. Keep the original input files unchanged. Document actual tests and any unverified areas. Do not fabricate independent review. No network or deployment is authorized for this local build.

## Stable browser testing contract
This contract specifies test selectors, not the app architecture or visual design:
- Native select IDs: customer, status, severity. Options have visible customer names, status names and severity names from stakeholder-answers.md.
- Search input ID: search. Date input IDs: start and end.
- Button IDs: clear and export.
- Metric IDs: total-count and active-count, containing numeric values.
- Ticket result container ID: ticket-rows. One visible element per ticket has data-ticket-id="<id>".
- Daily graph container ID: trend. One count element per actual matching UTC day has data-date="YYYY-MM-DD" and data-count="<integer>". Display readable date/count text.
- Status graph container ID: breakdown. One count element per status has data-status="<status>" and data-count="<integer>". Display readable status/count text.
- Keep window.TICKETS as the supplied fixtures. Export should use a Blob download (normal browser CSV behavior).
- Opening index.html from disk must work without a server or network. verify.mjs uses the installed Playwright runtime; a package fallback path is supplied for this recording host.

## Completion
Supply plan.md, questions.md, decision-log.md and handoff.md. State what is delivered, how to run it, what was tested, limitations and sensible next steps. You may add useful artifacts. Source control and remote CI are not operated during this recording.
