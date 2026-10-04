# Built UI review

Review the actual built surface with `/frontend-design-review --url <url>`.
Use the same six canonical advisory dimensions in JSON and the human report.
Retain visual polish, copy and layout/density questions as findings, not a
second rubric or score-based release gate.

## Review ownership and reuse

Choose one post-generation review owner in the existing task brief/handoff.
An enclosing `frontend-design` run owns that review; for a standalone renderer
request, its current workflow caller owns it. Renderers return the actual
artifact paths, source/profile identity, build/inspection observations and
remaining required controls to that owner. Missing final review does not require
regenerating an otherwise valid artifact.

The owner invokes `frontend-design-review` once for the current output.
`WebExperienceCritic` can supply early design advice or the post-generation
method; `DesignSystemAuditor` can supply the latter. Their post-generation
coverage overlaps. The retained `design_pass_hook` names and `--review` request
are routes to this owner, not reasons to run both reviewers by default.
Pre-generation advice is not evidence about a rendered artifact.

Reuse an existing result only through the current P05 reader/QA contract:
source/design/artifact bytes, profile, routes/viewports, requested dimensions,
required controls and independent reviewer provenance must still apply.
An advisory `design-review.json` or implementer self-check cannot supply missing
independent evidence. Changed inputs or missing controls require the affected
review/observations; do not silently drop them or borrow another path's result.
Additional reviewers need a distinct requested purpose or uncovered obligation,
not merely another alias for the same artifact and rubric.

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
4. Critique observed behavior through the existing canonical dimensions. These
   questions preserve the broad UX coverage without a second set of ratings:

   | Canonical dimension | Questions |
   |---|---|
   | `typography_hierarchy` | Hierarchy, alignment, spacing, reading density, fallback and task/copy clarity |
   | `motion_coherence` | Observed reduced-motion fallback, interaction states and consistent motion language |
   | `shader_perf_budget` | Actual compatible device/workload measurements and observed GPU fallbacks; null without measurement |
   | `accessibility_wcag` | Normal text >=4.5:1, large text >=3:1, semantics, real focus order, keyboard access and labels |
   | `brand_conformance` | Selected tokens/profile, type, marks, configured voice, accuracy and spelling |
   | `responsive_fidelity` | Layout/density, mobile use, images, placeholders, clipping, overflow and touch targets |

   FPS, FOIT and scroll-jank need compatible performance measurements; source,
   DOM and screenshots do not provide them. Follow the
   [shared observation boundary](../../design-dna/references/design-contract.md#review-and-domain-handoff).
   Keep absent timing unverified and required observations blocked independently.
   Optional copy critique remains controlled by `--include-copy-pillar`; that
   retained input name does not create another scored output dimension.

5. Record each finding with P1/P2/P3 severity, route, viewport, actionable
   correction, file:line where attributable and screenshot/DOM anchors. Do not
   invent a source location for a remote-only observation. A screenshot alone
   cannot prove interactive behavior; absent performance evidence remains unverified.
6. Emit the existing `design-review.json` using `normalize_dimensions` and
   `validate_review`. Keep only its six canonical keys in both outputs. Put copy
   findings under the relevant dimension and report capture/measurement coverage.
   All selected routes must be accounted for; partial capture is not full review.
7. Use the same external P05 context/QA and current P07 reference as ordinary
   frontend review. Recheck current source/design/artifact bytes and actual
   required observations. Required failure/error/unverified blocks regardless
   of an advisory score/color or selected dimension subset.
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
