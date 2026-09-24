# Implementation plan

Authority: implementation-prompt.md authorizes this local build; stakeholder-answers.md defines behavior. Starter files are preserved. No customer data, credentials or production mutations are involved.

## Acceptance contract

See spec.md. Run the supplied verify.mjs unchanged, then focused edge-case checks and visual inspection of desktop/mobile captures. Document observed results and limitations; do not claim independent review.

| ID | Task and files | Depends | Acceptance | Heuristic effort | Complexity / role | Status |
|---|---|---|---|---|---|---|
| T1 | Resolve scope and record spec, questions, decisions and handoff prompt in scope.md, spec.md, questions.md, decision-log.md, prompt.md | — | All stakeholder requirements mapped; assumptions explicit | 2 min | Mechanical; local implementer | DONE |
| T2 | Build accessible responsive shell in index.html and styles.css | T1 | Native labels, focus, 390/1440 layout, clear production boundary | 2–3 min | Multi-file; local implementer | DONE |
| T3 | Implement coherent filtering, charts, table, validation and safe export in app.js | T2 | UTC/intersection behavior, plain text, formula-safe CSV, empty/error states | 2–3 min | Multi-file; local implementer | DONE |
| T4 | Run shared/extra checks, inspect captures, self-review and write handoff.md / review.md | T3 | Passing checks, actual evidence, fresh-session instructions and remaining limits | 2–3 min | Review; same implementer | DONE |

These are unmeasured planning heuristics.

## Inline plan review

Spec self-review: PASS. Customer scope, active definition, status/severity/search/date intersection, UTC aggregation, safe export, text rendering, empty states and responsive accessibility are covered.
Quality self-review: PASS. One derived set removes drift across outputs. Dependencies are local scripts only. Date-range and malformed-data failures need visible feedback. Chart count text is available without graphics. Keep the scope bounded.
Design self-review: readable light workspace, clear hierarchy, restrained violet accent, labelled charts, visible focus, mobile ticket cards.
Developer experience self-review: opening index.html must work; document definitions and commands, preserve tests, no telemetry needed for this offline synthetic pilot.
Adversarial review unavailable — plan unreviewed by an independent identity. The inline checks above are self-reviews only, as required by the local workflow adaptation.

## Final review

Complete. Shared browser suite: 14/14 PASS; supplemental suite: 7/7 PASS. Both viewport captures visually inspected. See common-verification.json, additional-verification.json, review.md and handoff.md. No open implementation blocker. Remote CI, cross-browser and full assistive-technology verification remain outside observed evidence.

