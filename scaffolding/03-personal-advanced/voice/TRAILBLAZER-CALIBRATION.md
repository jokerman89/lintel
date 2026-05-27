# Trailblazer voice eval calibration results

Per-cell accuracy of `TRAILBLAZER-TEST.md` against `TRAILBLAZER-CORPUS.md`.

Operator fills this iteratively while running the eval. Each row records one calibration pass per cell. The bottom-most rows are the most recent passes.

**Status:** PENDING (T0 voice corpus + eval not yet run; structure below is the template)

---

## Calibration target

**v1.0.0 ships when:** every cell achieves ≥90% accuracy on known-good AND ≥90% accuracy on known-bad in the same pass.

A cell that fails calibration after 3 prompt-refinement iterations falls back to one of:
- **Option A:** Drop that cell from v1.0.0 scope. JStack's Trailblazer surface narrows by 1 cell. Document the drop in this file.
- **Option B:** Gather 4+ more corpus paragraphs for that cell. Re-run after corpus expansion. May delay v1.0.0 ship.

Operator decides per cell.

---

## Calibration log

Each pass records: timestamp, prompt version, per-cell accuracy.

### Pass 0 (TEMPLATE — replace when first pass runs)

- **Date:** YYYY-MM-DD
- **TEST.md commit:** `<git rev-parse HEAD>`
- **CORPUS.md commit:** `<git rev-parse HEAD>`

| Cell | Known-good total | Known-good PASS | Known-good accuracy | Known-bad total | Known-bad FAIL | Known-bad accuracy | Status |
|---|---|---|---|---|---|---|---|
| R1 REVEAL/Understatement | TODO | TODO | TODO | TODO | TODO | TODO | PENDING |
| R2 REVEAL/Leave unanswered | TODO | TODO | TODO | TODO | TODO | TODO | PENDING |
| R3 REVEAL/Draw back curtain | TODO | TODO | TODO | TODO | TODO | TODO | PENDING |
| R4 REVEAL/Dream high | TODO | TODO | TODO | TODO | TODO | TODO | PENDING |
| I1 INSPIRE/Opposites attractive | TODO | TODO | TODO | TODO | TODO | TODO | PENDING |
| I2 INSPIRE/Language spectacular | TODO | TODO | TODO | TODO | TODO | TODO | PENDING |
| I3 INSPIRE/Marvel simple truth | TODO | TODO | TODO | TODO | TODO | TODO | PENDING |
| P1 PROVOKE/Skewer sacred | TODO | TODO | TODO | TODO | TODO | TODO | PENDING |
| P2 PROVOKE/Exception rules | TODO | TODO | TODO | TODO | TODO | TODO | PENDING |
| P3 PROVOKE/All or nothing | TODO | TODO | TODO | TODO | TODO | TODO | PENDING |
| P4 PROVOKE/Unflinching | TODO | TODO | TODO | TODO | TODO | TODO | PENDING |
| P5 PROVOKE/Vulnerability strength | TODO | TODO | TODO | TODO | TODO | TODO | PENDING |

**Status values:** PENDING (no data yet) | PASS (both ≥90%) | PARTIAL (one ≥90%, other below) | FAIL (both below 90%)

**Pass 0 verdict:** PENDING / PASS / PARTIAL / FAIL

**Action taken:** (what changed in TEST.md or CORPUS.md after this pass, if anything)

---

## Per-cell failure analysis (template — fill if a cell fails)

When a cell's accuracy is below 90% on either axis, write a short analysis:

### Cell <ID>: <STATUS>

- **Known-good failures (eval said FAIL but corpus said good):**
  - Paragraph PARAGRAPH-NNN: <why eval marked it FAIL — quote the specific eval verdict line>
  - Paragraph PARAGRAPH-NNN: <same>
- **Known-bad failures (eval said PASS but corpus said bad):**
  - Paragraph PARAGRAPH-NNN: <why eval marked it PASS — what voice attribute did it score too high on>
- **Refinement attempted in TEST.md:**
  - <what the prompt change was, and why>
- **Result after refinement:**
  - <new accuracy, or "still fails — proceeding to Option A drop or Option B expand">

---

## v1.0.0 ship gate

This file's status table determines T0 unblock:

- All 12 cells at PASS status → T0 cleared → Phase 1 begins
- Any cell at PENDING or FAIL → T0 still blocking
- Cells dropped via Option A → recorded with rationale, not counted toward T0 gate (but Trailblazer surface in v1 narrows accordingly)

Operator updates this file after each calibration pass. CC can assist with the per-paragraph eval execution + result tabulation, but the corpus content (the actual paragraphs) is operator-gathered + sanitized.
