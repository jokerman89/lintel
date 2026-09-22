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

Apply a selected voice rubric to known-good and known-bad corpus paragraphs, compare
observed verdicts to each `verdict_label`, and report separate per-cell accuracy.
Preserve the useful calibration method without claiming an automatic evaluation service.

This is a workflow, not proof that a model runner, gateway, audit writer or ship gate
exists. Use actual permitted evaluation or explicitly attributed manual/recorded verdicts.
No corpus is configured in the neutral pack. Applicable project/pack policy may require
evaluation; this skill neither invents that requirement nor clears policy or review gates.

## When to use

- Voice corpus is populated, ready to calibrate
- Corpus, rubric, evaluator or settings changed — re-evaluate the affected scope
- The applicable project/pack policy requests calibration evidence
- TEST rubric was tuned — re-eval to measure if accuracy improved
- After cell-coverage expansion (added more paragraphs to a cell)

## When NOT to use

- Corpus is empty or absent — report insufficient input, not a passing empty run
- Rubric or permitted evaluator is missing — retain NOT_EVALUATED, not fabricated verdicts
- Single-paragraph spot-check — apply the rubric directly

## Inputs

- `--corpus <path>` — explicitly selected corpus, or its path from the existing verified
  profile's `voice.corpus`. Read only authorized inputs; do not scan private packs.
- `--test <path>` — explicit rubric and its version/content identity; no guessed sibling filename
- `--cells <list>` — optional exact cell IDs, not globs or code; default all declared cells
- `--out <path>` — explicitly owned target report such as `reports/voice/CALIBRATION.md`;
  otherwise report in the response only. Never default to writing beside a private corpus.
- `--threshold <pct>` — per-class accuracy threshold, default 90 as an advisory comparison
  when policy has not specified one. Reject nonnumeric/nonfinite values or values outside
  0..100. Do not relax a policy requirement to make the report pass.
- Evaluation evidence — actual authorized tool/actor and settings, or explicitly supplied
  recorded/manual verdicts bound to these inputs. No undeclared `--cli` dispatcher is implied.

## Workflow

1. **Bind the scope.** Record corpus/rubric paths and content identities, declared cells,
   selected IDs, threshold and actual evaluator/settings. Keep those fixed for a run.
   Reject unknown/repeated cell IDs, duplicate paragraph IDs, empty/malformed inputs and
   labels other than the declared known-good/known-bad ground truth. Structured YAML/JSON
   can use the existing `lib/envelope_contract.py` `load_text` reader through a permitted
   Python operation from the trusted source. Report parser/dependency errors; do not
   build a second corpus parser or use this reader to reinterpret profile policy.
2. **Apply the actual rubric.** For each selected paragraph, obtain an observed verdict
   through an available permitted operation, or document the manual/recorded evidence.
   Keep expected labels separate from evaluation input where possible; copying ground
   truth into the observed column is not evaluation. Preserve the rubric's real detail
   (for example technique, kind/daring/deep scores and rule violations) without inventing
   fields the rubric does not define.
3. **Compare per paragraph.** Retain paragraph ID, expected label, observed verdict,
   evidence reference and discrepancy. Ambiguous, missing or malformed verdicts are
   NOT_EVALUATED until resolved, not silent correct answers or discarded rows.
4. **Compare per cell.** Known-good accuracy is correct known-good verdicts divided by
   all expected known-good paragraphs; known-bad accuracy uses its own denominator.
   Show both fractions, evaluated/expected counts and the threshold. Never merge the
   classes so abundant good examples can hide failure on bad examples.
   A cell with fewer than two paragraphs of either class is INSUFFICIENT; do not divide
   by zero. Any unevaluated paragraph prevents PASS. With sufficient complete evidence,
   PASS requires both accuracies to meet the selected threshold; otherwise FAIL.
5. **Aggregate without promoting scope.** List every declared cell as selected/evaluated,
   failed, insufficient or not evaluated. Any subset run is PARTIAL_SCOPE, even if every
   selected cell passes. An empty corpus has no passing aggregate. ALL_CELLS_PASS applies
   only to a nonempty full-corpus run with sufficient complete evidence and every cell
   passing; it means comparison success, not release clearance or automatic certification.
6. **Persist only within authority.** Write the requested target report or return it in
   conversation. Preserve earlier evidence rather than overwriting a broader report with
   a subset. Record actual checks and limits; do not stamp a fictitious audit event or run.

## Report format

Include actual scope/input identities, actor/tool or manual evidence, evaluated/expected
counts, both per-class fractions, failures and the exact owned output (or response-only).
Label illustrations as illustrations. Do not name a model/version that was not actually used.

Synthetic worked comparison, **not a model run**, at threshold 90:

| Cell | Correct good / expected good | Correct bad / expected bad | Status |
|---|---|---|---|
| R1 | 2/2 | 2/2 | PASS |
| R2 | 1/2 | 2/2 | FAIL |
| R3 | 0/0 | 0/0 | INSUFFICIENT |

All eight populated paragraphs have recorded verdicts in this example. R2 good accuracy
is 50%, not rescued by its 100% bad accuracy. R3 is declared but empty; no division or
vacuous PASS is valid. Aggregate: one passing, one failed, one insufficient cell; full
corpus calibration is **not established**.

A useful failure entry preserves the ID and concrete error: `R2-GOOD-002`, expected
known-good, observed known-bad, with the actual rubric rationale/evidence. Revise the
rubric or examples only within scope, then rerun affected work under the new input
identity. Do not remove failed cells merely to obtain a passing report.

## Compliance integration

Apply actual P07 profile requirements and P05 control/review rules when they govern the
authorized work. A malformed required profile is not optional/neutral success. A profile
gateway declaration is not a callable tool or permission to transmit corpus data.

Inspect real evaluator tools before invoking them. Missing/denied execution retains the
manual or NOT_EVALUATED route without bypassing denial. No automatic audit logging,
snapshot stamping, independent actor or downstream enforcement is promised by this method.
An actual downstream consumer must validate its own applicable evidence; this report does
not alter ship controls. Do not launch a paid benchmark to demonstrate the example.

## Failure modes

- **Invalid corpus/rubric/selection:** report the offending input, stop that comparison and
  preserve a prior good report. Never replace it with empty success.
- **Missing corpus or insufficient class coverage:** list what is missing; no calibration claim.
- **Unavailable evaluator, permission denial or failed call:** preserve NOT_EVALUATED;
  retries require existing execution/cost authority and must not erase the original failure.
- **Partial rerun or changed inputs:** report only that evidence. Prior results may be
  referenced separately with their exact unchanged inputs/settings, not counted as executed
  in this run or silently promoted into a new whole-corpus result.
- **Unowned/existing output conflict:** return the result without clobbering the artifact;
  obtain specific revision authority before replacing it.

## Examples

**Full eval:**
```
> /li:eval --corpus fixtures/voice.yaml --test fixtures/rubric.md --out reports/voice/CALIBRATION.md
[Only after those inputs, output and an actual evaluation method are authorized]
Compare every declared cell, retain actual verdict evidence, then report real counts.
If no evaluator/recorded evidence is available: NOT_EVALUATED. No calls or readiness invented.
```

**Cell-scoped re-eval:**
```
> /li:eval --corpus fixtures/voice.yaml --test fixtures/rubric-v2.md --cells R2
Illustration: R2 now has 2/2 correct good and 2/2 correct bad.
Selected cell: PASS. Run: PARTIAL_SCOPE (1 of 3 declared cells).
R1 and R3 were not re-evaluated; no whole-corpus certification or ship clearance.
```

**Stricter threshold:**
```
> /li:eval --threshold 95
[With the same explicitly selected inputs and real evidence]
19/20 good and 20/20 bad meet 95%; 18/20 good does not.
Report the actual scope. A mandatory threshold cannot be relaxed by this skill.
```

## See also

- the pack's voice corpus — the input (`resolve_pack_field voice.corpus`)
- the pack's voice test rubric — the rubric
- the calibration file — the output
- the applicable verified profile and review/control contract — separate evidence obligations
- [ADR-0021](../../.claude/decisions/0021-eval-harness.md) — a staged general eval harness,
  not proof that this voice method already has an automated runner
