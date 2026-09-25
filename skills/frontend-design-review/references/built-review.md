# Built UI review

Review the actual built surface with `/frontend-design-review --url <url>`.
This supplements the six canonical JSON dimensions with the retained six-pillar
human critique; it creates no competing schema or score-based release gate.

## Inputs

- `--url <url>`: running application or authorized preview. A positional URL
  is equivalent; reject conflicting artifact/URL selections.
- `--routes <file>`: optional explicit route list; default the supplied URL.
  Read entries as data, resolve relative routes against that URL, and admit each
  destination and every redirect before following it. Do not crawl for routes.
- `--viewport <list>`: CSS-pixel sizes, default `1440x900,375x812`. Record actual
  requested/observed sizes and unsupported device emulation.
- `--baseline-ref <ref>`: optional local Git reference for changed-file context.
  This is distinct from the existing `--baseline <pattern>` design reference.
  Neither implies a checkout, fetch, baseline build or browser observation.
- `--include-copy-pillar[=true|false]`: copy critique; include by default for an
  explicitly customer-facing surface, otherwise opt in. A false value does not
  waive mandatory voice/content controls.
- Existing `--dimensions`, `--out`, `--customer-share` and
  `--include-screenshots` retain their meaning. Choose an owned run directory
  for captures; a remote URL has no writable artifact directory.

## Procedure

1. Verify the selected work/profile and actual browser operation, isolation and
   data permissions. Observe health for an owned preview server. Do not navigate
   an existing personal tab to discover whether the provider is safe.
2. For every route and viewport, use `web-session --mode browse` to open/read and
   capture requested screenshots/DOM. Request console capture only for sanitized
   pages when the provider supports it; no console access is not a clean console.
   Re-read after actual interactions. Keep route/viewport/artifact associations.
3. Run the existing mechanical validator against actual captured HTML using
   the resolved palette. Retain its hard errors and warnings as findings.
   Static validation does not replace required rendered measurements.
4. Critique the six pillars, retaining advisory 1-10 scores only where evidence
   supports a score:

   | Pillar | Questions and canonical dimension connection |
   |---|---|
   | Visual polish | Alignment, spacing, states, images, overflow and placeholders; typography and responsive findings |
   | Accessibility | Normal text >=4.5:1, large text >=3:1, semantics, real focus order, keyboard access and labels; accessibility findings |
   | Motion | Observed reduced-motion fallback, consistent timing, responsiveness; motion and shader-budget findings |
   | Copy | Accuracy, spelling, task clarity, length and configured voice; human critique and applicable content controls, not a new JSON dimension |
   | Layout/density | Information hierarchy, mobile use and clipping; responsive and typography findings |
   | Brand consistency | Selected token/profile, type and signature requirements; brand findings |

5. Record each finding with P1/P2/P3 severity, route, viewport, actionable
   correction, file:line where attributable and screenshot/DOM anchors. Do not
   invent a source location for a remote-only observation. A screenshot alone
   cannot prove interactive behavior, and an unmeasured pillar remains unscored.
6. Emit the existing `design-review.json` using `normalize_dimensions` and
   `validate_review`. Keep only its six canonical keys. Put the six-pillar table,
   cross-pillar copy critique and capture coverage in the human report.
   All selected routes must be accounted for; partial capture is not full review.
7. Use the same external P05 context/QA and current P07 reference as ordinary
   frontend review. Recheck current source/design/artifact bytes and actual
   required observations. Required failure/error/unverified blocks regardless
   of a pillar average, advisory color or selected dimension subset.
   Persist an independent review only through the accepted P05 writer and a
   real separate actor. Implementer feedback remains self-review.
   A standalone built surface need not have a design spec: use P05's existing
   snapshot/inspect route and verified project/profile inputs, never an invented
   design envelope. `validate_review` still validates the six advisory keys;
   the design-bound `review_result` is used only with an actual selected design.
8. Close only owned browser/server handles. Keep unfinished cleanup visible.
   Browser use, a source report and customer-share clearance are separate facts.

## Failures and data

An unreachable route, denied provider or missing required observation remains
failed/blocked/unverified with exact coverage. Continue independent source
inspection only as clearly labeled partial work; do not award a full score.
Missing explicitly selected baselines block that comparison rather than fall back.

If customer data appears, stop capture/sharing and follow the applicable owned
quarantine procedure. The optional screenshot hook is a DOM-pattern warning, not
OCR, automatic quarantine or universally installed enforcement. Do not claim
sanitization passed without its real result. Missing required voice guidance stays
unresolved; an optional copy critique can be deferred explicitly.
