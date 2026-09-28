# Reviews: native client parity

## DEFINE design review

- **Reviewer:** `ca6119f3` (rubber-duck, separate context, read-only). Inputs were the design, the
  evolution entry, ADR-0008/0024/0035, lessons L-016/L-020/L-030/L-053/L-054/L-055/L-060, and the
  generator and hook sources.
- **R1 (2026-09-28):** 1 Critical, 5 High, 4 Medium. All ten were verified against the code by the
  coordinator and accepted. Resolutions are in the design's "Design review R1 resolution" table.
- **R2 (2026-09-28):** no new Critical.
  - Resolved: 1, 2, 3, 5, 6.
  - Partial:
    - 4: PowerShell `$env:` overrides are not executed at `preToolUse` time.
    - 7: first-time insertion across batched messages; duplicate keys; control-character escaping.
    - 8 and a new High: a first-runner dedupe lets lower-trust repository hooks suppress the plugin.
    - 9: ADR timing in AC7; exact manifest list; a fresh version-collision check.
    - 10: no cap on discovery overhead; bundle size only reported.
- **R2 remedies applied as recommended:**
  - the adapter normalizes a leading `$env:` override sequence into the canonical hook environment;
  - once-per-batch injection, duplicate-key rejection and full control-character escaping;
  - cross-origin dedupe removed (both routes run, and repository hooks never suppress the plugin);
  - ADR-0038 accepted before BUILD, exact manifest paths listed, and a pre-merge version check;
  - a 48 KB discovery-metadata cap and a 2 MB bundle-growth gate.
- **Status:** DEFINE is DONE_WITH_CONCERNS. The R2 remedies had no third design pass, so PLAN
  Stage 1 review re-verifies design coverage together with the plan.

## PLAN review (inspect engineering + devex lenses, Stage 1 coverage, Stage 2 quality)

- **Reviewer:** `ca6119f3` (the same independent rubber-duck context, read-only). Design lens: not
  applicable (no rendered UI), and the reviewer agreed.
- **Iteration 1:** Critical 1, High 7, Medium 3. Engineering lens RED, DevEx YELLOW, Stage 1 RED.
  - The Critical: the `swarm_contract` parser derived 74 singleton packages, because of the header
    names, leaf ranges and non-literal boundaries.
  - Also found: coarse leaves, an inline P4 review, missing M2, the R2 no-dedupe rule not encoded, a
    weakened gate, increment 2 skipping DEFINE, untraced leaves, and a status overclaim.
- **Iteration 2:** Stage 1 RED, with 4 High and 2 Medium.
  - Stale design text in D5 and row 8.
  - The prompt listed only R1-R20.
  - The identity check came after the push.
  - AC8 had no leaf.
  - Recorded fixtures were not planned, and 2.5.a was untraced.
  - The privacy check was invalid.
- **Iteration 3:** Stage 1 RED, 1 High: the camelCase `preToolUse` payload was contract-derived and
  mislabeled as recorded. It was resolved by observation, with probe 3 recording live `create`,
  `edit` and `powershell` payloads. Camel-case `bash` is labeled contract-derived and `conditional`.
- **Iteration 4:** Stage 1 **GREEN**. Stage 2 RED, with 1 High (P6 spanned BUILD, REVIEW and SHIP)
  and 2 Medium (stale `main` refs, coarse leaves). P6 now ends at evidence, the gates are REVIEW and
  SHIP controls, and fetch-first checks and further leaf splits were added.
- **Iteration 5:** Stage 2 **YELLOW**, with 4 Medium:
  - the audit path in P6;
  - the version loop-back;
  - stale prompt IDs;
  - M4 not operationalized.

  All four were fixed as recommended, and CAPTURE controls were added. After three unchanged-verdict
  iterations were avoided, the mechanical fixes were not re-reviewed.
- **Mechanical checks:** `li-work-artifacts --view context` derives 6 packages and 104 leaves with the
  planned dependencies. Every leaf traces to R1-R23, and every traced ID exists.
- **Evidence form:** a narrative record attributable to reviewer `ca6119f3`. It is not a bound v2
  decision, because the rubber-duck reviewer is read-only. Bound v2 evidence is produced for the
  implementation packages and the final review consumed at SHIP.
- **Status:** PLAN is DONE_WITH_CONCERNS. The concerns are the narrative plan-review evidence and the
  unreviewed iteration-5 mechanical fixes.
