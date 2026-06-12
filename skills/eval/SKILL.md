---
name: eval
layer: foundation
description: Run the active pack's voice TEST against its voice CORPUS — per-cell accuracy → CALIBRATION.md.
color: orange
tools: Read, Write, Bash
voice: internal
cli_support: [claude-code, codex]
---

# /li:eval

The voice calibration runner. Applies the pack's voice test rubric to every paragraph in the pack's voice corpus (`resolve_pack_field voice.corpus`; none by default), compares the eval verdict to the `verdict_label` ground truth, computes per-cell accuracy, writes results to a calibration file.

This skill moves a voice corpus from POPULATED → CALIBRATED. Calibration is a ship prerequisite for any voice-bearing surface.

## When to use

- Voice corpus is populated, ready to calibrate
- Calibration is stale (>30 days) — refresh
- Pre-ship of a customer-bearing AI feature using the pack's voice tier
- TEST rubric was tuned — re-eval to measure if accuracy improved
- After cell-coverage expansion (added more paragraphs to a cell)

## When NOT to use

- Corpus is empty — populate first, or the active pack defines no voice corpus
- TEST rubric file missing — needed to compute verdicts
- Single-paragraph spot-check — apply the rubric directly

## Inputs

- Optional `--corpus <path>` — path to corpus (default: the active pack's voice corpus, `resolve_pack_field voice.corpus`)
- Optional `--test <path>` — path to test rubric (default: same dir as the corpus, test variant)
- Optional `--cells <list>` — evaluate only specific cells (e.g. `R1,R3,P2`)
- Optional `--out <path>` — calibration output (default: same dir as the corpus, calibration variant)
- Optional `--threshold <pct>` — pass threshold per cell (default: 90)

## Workflow

1. **Read corpus.** Parse YAML entries per cell. Filter by `--cells` if specified.
2. **Read test rubric.** Load the test rubric prompt template.
3. **Per paragraph:**
   - Apply the TEST rubric prompt (this means an LLM call — Claude or Codex per `--cli`)
   - Extract YAML verdict from response (mode_attempted, technique, kind/daring/deep scores, ground_rules_passed/violated, anti_ai_vocab_detected, verdict)
   - Compare verdict to `verdict_label` (known-good / known-bad)
4. **Per cell, compute:**
   - Known-good accuracy: (known-good correctly classified) / (total known-good)
   - Known-bad accuracy: (known-bad correctly classified) / (total known-bad)
   - PASS if BOTH ≥ threshold
5. **Aggregate:**
   - Cells PASS / FAIL
   - Overall calibration status (CALIBRATED if ≥10 cells PASS)
6. **Write the calibration file** with timestamp, per-cell results, aggregate verdict.
7. **Report.**

## Report format

```
Lintel Voice Eval

Corpus: 60 paragraphs (33 known-good + 27 known-bad)
Test rubric: voice-test.md v2.0
Eval LLM: Claude Opus 4.7
Threshold: 90%

## Per-cell results

| Cell                              | Good  | Bad   | Status |
|-----------------------------------|-------|-------|--------|
| R1 Understatement                 | 3/3   | 2/2   | PASS   |
| R2 Question unanswered            | 2/2   | 2/2   | PASS   |
| R3 Draw back the curtain          | 2/2   | 2/2   | PASS   |
| R4 Dream out loud                 | 2/2   | 1/2   | PARTIAL|
| I1 Opposites attractive           | 2/2   | 2/2   | PASS   |
| I2 Vernacular spectacular         | 2/2   | 2/2   | PASS   |
| I3 Marvel simple truth            | 2/2   | 2/2   | PASS   |
| P1 Vulnerability as strength      | 2/2   | 2/2   | PASS   |
| P2 Skewer the sacred              | 2/2   | 1/2   | PARTIAL|
| P3 Exception that rules           | 2/2   | 2/2   | PASS   |
| P4 All or nothing                 | 2/2   | 2/2   | PASS   |
| P5 Unflinching                    | 2/2   | 2/2   | PASS   |

## Aggregate
- Cells PASS: 10/12
- Cells PARTIAL: 2 (R4, P2)
- Overall: CALIBRATED (10/12 ≥ threshold)

## Failures
[R4-BAD-002] "Imagine a world where your organization..."
   Expected: known-bad (FAIL on dream-out-loud technique, lands in cliché)
   Got: AMBIGUOUS verdict (the "imagine" pattern fooled the rubric into thinking it was attempt)
   Recommendation: refine R4 rubric to specifically flag "imagine" as a tell

[P2-BAD-001] "Other vendors claim..."
   Expected: known-bad (punching down, Provoke without Kind)
   Got: PASS (rubric missed the Kind violation)
   Recommendation: strengthen P2 rubric's Kind check

## Status
CALIBRATED — 10/12 cells PASS at ≥90%.
Voice ship prerequisite: met.

Drop the 2 PARTIAL cells from scope OR iterate rubric and re-run.

Written to: voice-calibration.md
```

## Compliance integration

- LLM eval calls run against Claude Opus (or Codex if `--cli codex`). The active pack may route calls via a configured gateway.
- Audit-logged each run: `.claude/runtime/audit/eval-runs.jsonl`.
- Calibration snapshot stamped with run-id; downstream consumers reference snapshots for stability.

## Voice tier note

`voice: internal`. Eval report is engineering-internal; the SUBJECT is the pack's voice tier.

## Failure modes

- **Corpus YAML parse error:** report the offending entry, exit. Operator fixes.
- **TEST rubric prompt template malformed:** report + bail.
- **LLM API failure:** retry once per paragraph, mark NOT_EVALUATED if persistent.
- **Cell has <2 known-good or <2 known-bad:** skip cell (insufficient data), surface in report. Operator adds more.
- **Overall calibration < 10 cells PASS:** UNCALIBRATED stamp, downstream voice gates refuse to certify. Operator iterates.

## Examples

**Full eval:**
```
> /li:eval
[60 LLM calls + comparison]
10/12 cells PASS. CALIBRATED. Voice ship prerequisite met.
```

**Cell-scoped re-eval:**
```
> /li:eval --cells R4,P2
[Re-evaluates the 2 PARTIAL cells]
2/2 PASS now after rubric refinement. Overall calibration: 12/12.
```

**Stricter threshold:**
```
> /li:eval --threshold 95
[Same corpus, higher bar]
8/12 cells PASS at 95% — operator decides whether to relax or iterate further.
```

## See also

- the pack's voice corpus — the input (`resolve_pack_field voice.corpus`)
- the pack's voice test rubric — the rubric
- the calibration file — the output
- the active pack's voice gate — reads calibration to decide whether to certify
- `SHIP-GATE.md` — ship prerequisites
