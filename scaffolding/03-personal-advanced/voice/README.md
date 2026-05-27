# Trailblazer voice — the wedge proof point

This folder holds the Trailblazer voice eval infrastructure. Per JStack v1 design doc:

> Until calibration passes ≥90% known-good AND ≥90% known-bad across 12 cells, do not write any other JStack content. Without it, customer-facing skills ship generic-AI prose under a Microsoft brand — a values failure, not just a quality failure.

## Three files, one purpose

| File | What it is | Who fills it |
|---|---|---|
| `TRAILBLAZER-TEST.md` | The eval prompt — takes a paragraph as input, outputs structured verdict against MS Our Voice attributes + 3 modes + 12 technique cells + 6 ground rules + anti-AI vocab blacklist | Skeleton complete (CC); operator iterates if cells fail calibration |
| `TRAILBLAZER-CORPUS.md` | 48-slot template: 12 cells × 4 paragraphs each (2 known-good + 2 known-bad). Sanitized customer-engagement examples | Operator gathers + sanitizes + lands |
| `TRAILBLAZER-CALIBRATION.md` | Per-cell accuracy results after running TEST against CORPUS | Operator updates after each calibration pass |

## Workflow

1. **Read `TRAILBLAZER-CORPUS.md`** for the sanitization rules + corpus structure.
2. **Gather raw paragraphs locally** (not in this repo — operator-local until sanitized).
3. **Sanitize** per the explicit rules. Drop any paragraph that can't be sanitized while preserving voice signal.
4. **Land sanitized paragraphs** in the corpus file at the appropriate cell + verdict slot. Replace TODOs.
5. **Run `TRAILBLAZER-TEST.md` against each paragraph.** Compare eval verdict against your `verdict_label`.
6. **Record per-cell accuracy** in `TRAILBLAZER-CALIBRATION.md`.
7. **Iterate** TEST or drop cells until calibration passes for all included cells.

## What CC can help with vs what operator must do

**CC can:**
- Help refine the TEST prompt when a cell fails calibration (suggest specific changes based on which dimension is misfiring)
- Run the eval against each corpus paragraph and tabulate results
- Help sanitize raw paragraphs by suggesting placeholder replacements
- Detect anti-AI vocabulary occurrences in corpus paragraphs

**Operator must:**
- Identify which raw paragraphs from real CAIP-SE work are good/bad examples per cell
- Decide if a paragraph is sanitizable (some content can't be — voice signal is too entangled with customer specifics)
- Make Option A vs Option B calls when a cell fails calibration after 3 iterations
- Final sign-off on `TRAILBLAZER-CALIBRATION.md` status before T0 unblock

## Cell count correction

Earlier office-hours discussion said "15 cells (3 modes × 5 techniques)." That was wrong:

- **REVEAL** has 4 techniques (Understatement / Leave unanswered / Draw back curtain / Dream high)
- **INSPIRE** has 3 techniques (Opposites attractive / Language spectacular / Marvel simple truth)
- **PROVOKE** has 5 techniques (Skewer sacred / Exception rules / All or nothing / Unflinching / Vulnerability strength)

Total: 4 + 3 + 5 = **12 cells**, not 15. The corpus template targets 12 cells × 4 paragraphs = 48 slots. Design doc's "30 paragraphs minimum" still works as a floor (covers 12 cells with 1+1+0.5 average), but the template carries 48 for clearer per-cell ≥2+2 calibration.

## When T0 unblocks

Phase 1 of JStack v1 begins when `TRAILBLAZER-CALIBRATION.md`'s status table shows PASS for all cells the operator chose to include in v1 scope. Cells dropped via Option A reduce the v1 Trailblazer surface but don't block T0.

Eng review session 2 verdict line is the ship gate:
> "ENG CLEARED — ready to begin Phase 1 implementation, BLOCKED by T0 voice corpus assignment."

Get this folder green, and Phase 1 starts.
