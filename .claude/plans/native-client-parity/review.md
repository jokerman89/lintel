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
  - ADR-0039 accepted before BUILD, exact manifest paths listed, and a pre-merge version check;
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

## BUILD reviews and final PR-1a candidate source review

- **Reviewer:** `e3fe3231` (lintel-reviewer, separate context).
  - After a cleanup incident (the L-049 amendment), it ran response-only: view, grep and glob on
    named pins and evidence, with no shell, writes or deletions. Its tool receipts were checked for
    every turn.
  - Verbatim records are kept in the coordinator's evidence folder.
- **P1, stage 1 and 2** (pin `4bfc4e73`): Critical 0, High 0, Medium 2 (M1, M2), Low 8.
- **P1 deltas:**
  - `4c2d1569`: CHANGES-REQUIRED (N1 Medium, N2 Low).
  - `68262ccd`: SOURCE-ACCEPTED-PENDING-HOSTED.
  - Tree `8f995fc5`: SOURCE-ACCEPTED-PENDING-HOSTED. N6 and N7 are advisory.
- **Decision B mapping** (`5957a7ea`): VERIFIED from the Git receipts; the trees are identical.
- **Final PR-1a candidate:**
  - `78e2e046`: CHANGES-REQUIRED (F1-F3 Medium); M2 disposition ACCEPTED.
  - `40724cb2`: F2 and F3 resolved; R1 Medium.
  - `9ab895c6`, tree `e6d5f441`: **SOURCE-ACCEPTED-PENDING-HOSTED**. R1 and A1 closed, 5.3.b met,
    no regression.
- **Evidence form:** narrative records attributable to a read-only reviewer. None of them is the
  bound v2 decision that the REVIEW phase's final independent review requires; that review stays
  pending. No record here is an overall PASS.
- **Hosted gates** are listed in `build-log.md` under "PR-1a verification candidate".

## Final review and delivery: PR-1a (2026-09-29)

This is the primary record of PR-1a's hosted gates, bound final review and landing. It covers PR-1a
only. PR-1b, the shared leaves (5.5.a-c, 6.3.a-b) and the whole-increment final review stay open.

- **Candidate:** `394ed0b8` (tree `10d2c47c`), which is `06e69eb6` plus the oracle fix `1b019341`
  and its build-log note.
- **Hosted CI:** run `36516745619` on that exact head passed all 23 jobs.
  - Under `--require-all`, 489 test files passed, with 0 failed, 0 skipped and 0 partial.
  - The 46 not-applicable results are Windows-only assertions on Ubuntu and macOS.
  - The strict shape tier ran with `jq` on all three systems.
  - `copilot-kit.sh` and `universal-adapters.sh` each ran once per system. Under MasterCoordinator's
    evidence-layer decision, these whole-file runs are the execution evidence for the complete
    suites. Their 52 and 17 test methods are counted from the source.
  - Run `36505644531` on `06e69eb6` stays a failure and is not relabeled.
- **6.1.a:** the literal regeneration proof on `06e69eb6` (receipt `e44a72a6`) applies at the head.
  Only the oracle test and the build log changed since.
- **Reviewer:** the existing independent app session `c3015de8`, chosen by MasterCoordinator.
  - The subagent reviewer `e3fe3231` had been lost at a host idle stop. Its lookup returned
    `{"message":"Agent not found","code":"failure"}`; see the L-043 amendment.
  - The judgment is new. The `e3fe3231` records above are supporting history.
- **Judgment:** PASS on spec, quality and tests for P1, P4, P5 and P6, with no blocking finding.
  - Each review is bound to one context per original package with only that package's PR-1a
    leaves, attempt `native-client-parity-pr1a-394ed0b8` and profile generation 2.
  - Advisory ADV-1 (Low, not fixed): `bin/li-run` (lines 47-49, 76-78) leaves its standard-input
    step file behind when the runner itself is killed by a signal.
- **Recording:** the coordinator serialized the judgment unchanged into v2 decisions, and the
  reviewer confirmed each as faithful before logging.
  - Host corroboration binds both exchanges from the two sessions' event logs. It is
    recorder-extracted, not authenticated.
  - The audit log, the latest-decision reader, QA from run `36516745619` and the SHIP gate returned
    ok for every package.
  - Record digests: P1 `849410b0`, P4 `2d75e4d6`, P5 `4b3f0d4d` and P6 `509a061c`.
  - Private receipts: `p05-final-receipt-394ed0b8.json` (`fc09fbb1`) and MasterCoordinator's landing
    receipt (`f935dec6`).
- **Landing:** MasterCoordinator fast-forwarded `main` from `1cf7d099` to `394ed0b8`, under its
  recorded direct-main fallback. There was no new commit, pull request, tag or release.
  `fd151979` and `f6009076` remain ancestors of `main`.
