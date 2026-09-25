# ADR-0033: Remove the blocked document-format acceptance and the PDF reader

- **Status:** Accepted, 2026-09-25
- **Date:** 2026-09-25
- **Deciders:** the operator ("Ta bort detta ur Lintel"), executed by coordinator88 (P15 final
  delivery)
- **Supersedes:** —
- **Superseded by:** —

## Context

PR #93 carried two blockers that only the operator could resolve:

- **The PDF reader.** `skills/generate-pdf/scripts/check_pdf.py` read produced PDFs through an
  existing `pypdf` installation. The repository never declared `pypdf`, and the operator refused
  to add it (L-054). `tests/integration/document-pdf.sh` therefore failed in integration shard 3
  on every CI system, and A23.4's strict CI could not pass.
- **A15.1–A15.4, verifiable document formats (P12).** Their acceptance needed rendering and
  editability evidence through Word, Excel and PDF-raster application routes, and P12
  structured-record persistence. The operator denied all of these, and Visio has no writer.
  The four items stayed open and blocked the initiative's count at 108 of 113.

On 2026-09-25 the operator answered both with one instruction: remove them from Lintel.

## Decision

- **Remove the PDF reader.** Delete `check_pdf.py` and its tests: the reader, physical-geometry
  and native-print classes of `document-pdf`. Also remove the reader from `ADAPTER_RESOURCES`,
  from the `document-pdf` capability selection and from the documentation.
  - Lintel then has no PDF reader and depends on no PDF library. `generate-pdf` keeps its
    writer: HTML preparation (`prepare_html.py`) and the accepted browser print
    (`print_pdf.mjs`), with their tests.
  - The produced PDF's text, pages and visual rendering are explicitly unverified.
- **Remove A15.1–A15.4 from the Universal initiative's scope.** They were never accepted, and
  removal is not a waiver. The integrated document skills (Word, PowerPoint, workbook, PDF and
  the Visio template slot) stay as staged capabilities with their existing unverified
  boundaries and passing tests. No acceptance is claimed for them.
- The initiative's count becomes 109 items, and A23.4 closes on the strict CI run of the
  resulting head.
- **Scope reading.** "Remove this from Lintel" is read as removing the blockers: the unverifiable
  requirements and the undeclared dependency, not the document skills. This is the coordinator's
  interpretation of the instruction, and the operator may extend it to the skills themselves.

## Alternatives considered

- **Declare and install `pypdf` for CI.** Rejected by the operator (L-054).
- **Keep `check_pdf.py` and drop only its tests.** Rejected: that would ship untested code with
  an undeclared dependency.
- **Remove the whole document-format skill family.** Rejected. It would discard working, reviewed
  capabilities that existed before the initiative (L-031), and it collides with the separate
  initiative "Removing legacy skills and agents", which preserves the PDF writer and XLSX
  contracts.

## Consequences

- **Positive:** the strict suite no longer needs an undeclared package, and the initiative can
  close without claiming unverified document-format acceptance.
- **Negative:** `generate-pdf` loses automated checks of text retention, page size and text
  positions. A separately authorized reader or viewer must supply those observations.
- **Neutral:**
  - P11's opt-in `--pdf-reader pypdf` option in `tests/integration/design-browser-pipeline.py`
    stays. CI does not run it, and it reproduces accepted A16 print evidence.
  - The historical P12 reports and reviews, and the P13 preservation map, keep describing the
    reader as it was when they were written.

## References

- L-054 (no undeclared third-party packages), L-031 (preserve value when consolidating).
- `.claude/plans/universal-implementation/reports/final.md` ("Delivery CI").
- ADR-0032 (the sharded strict CI suite and its first hosted run).
