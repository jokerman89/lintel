---
name: jstack-eval-suite-gen
description: Generate an evaluation suite skeleton for an AI feature — golden set, adversarial set, rubric.
color: green
tools: Read, Write, Bash, Glob, Grep
voice: internal
cli_support: [claude-code, codex]
---

# /eval-suite-gen

Generates the skeleton of an evaluation suite for an AI feature: golden-set (known-good fixtures), adversarial-set (known-failure fixtures), rubric (what the eval scores), and runner config. Operator fills the fixtures + tunes the rubric; this skill produces the structure.

Critical for AI features: without an eval suite, drift and regression are invisible. With one: every change is measurable.

## When to use

- New AI feature design — generate eval suite before model integration
- Existing AI feature without eval coverage — retroactive eval suite creation
- Before model upgrade — eval suite must be in place to detect regression
- Customer-facing AI — eval suite is a launch prerequisite

## When NOT to use

- Non-AI features (use `/qa` and standard test suites)
- Eval suite already exists + maintained — use `/qa-only` against it instead
- Pure deterministic AI (rules engine, regex) — standard tests suffice

## Inputs

- Required `--feature <name>` — short name for the AI feature
- Optional `--source <path>` — code or design doc
- Optional `--rai-assessment <path>` — output from `/rai-impact-assessment` (seeds rubric dimensions)
- Optional `--sensitive-use-report <path>` — output from `/sensitive-use-report` (seeds adversarial-set categories)
- Optional `--target-dir <path>` — where suite lands (default: `eval/<feature>/`)

## Workflow

1. **Read context.** RAI assessment + sensitive-use report (if present) — these tell us what to evaluate FOR and what to evaluate AGAINST.
2. **Generate eval suite structure:**
   ```
   eval/<feature>/
     README.md                  # suite methodology, how to run, how to interpret
     rubric.yaml                # scoring rubric (dimensions × scale × pass-threshold)
     golden/
       README.md                # what known-good means here
       fixture-001.yaml         # input + expected output + rationale (operator fills)
       fixture-002.yaml         # (stub created, operator fills)
       ... 8 stubs
     adversarial/
       README.md                # what known-bad means here
       fixture-001.yaml         # input + expected failure mode (operator fills)
       ... 8 stubs
     runs/.gitkeep
     runner.yaml                # config for the eval runner (model, params, output dir)
   ```
3. **Rubric scaffolding.** Dimensions seeded from inputs:
   - From RAI assessment: Fairness, Reliability, Inclusiveness, Transparency
   - From sensitive-use: per-triggered-category dimension
   - Plus baseline: Correctness, Format-compliance, No-hallucination
4. **Golden / adversarial seeds.** 8 + 8 stubs with template content:
   - `golden/fixture-001.yaml`: high-confidence happy-path scenario
   - `golden/fixture-002.yaml`: edge case (long input, ambiguous input)
   - `adversarial/fixture-001.yaml`: jailbreak attempt
   - `adversarial/fixture-002.yaml`: out-of-scope use
   - Etc.
5. **Runner config.** `runner.yaml` declares the model, hyperparameters, output format, results location.
6. **README + methodology.** `eval/<feature>/README.md` explains:
   - How to add fixtures
   - How to interpret pass/fail per dimension
   - When to update the rubric (model change, scope change, new failure mode discovered)
7. **Cross-link.** Reference in `compliance/rai-impact-DRAFT.md` (under Reliability + Fairness) that eval suite lives at `eval/<feature>/`.
8. **Report.**

## Report format

```
Eval suite: feature=case-analysis-ai

Target dir: eval/case-analysis-ai/

## Created
- README.md (methodology + runner instructions)
- rubric.yaml (8 dimensions × 1-10 scale × per-dimension pass threshold)
- golden/ — 8 fixture stubs (operator fills)
- adversarial/ — 8 fixture stubs (operator fills)
- runs/.gitkeep
- runner.yaml (model: gpt-4o, fallback: gemini-1.5-pro; output: runs/<ts>.jsonl)

## Rubric dimensions
1. Correctness (baseline)
2. Format-compliance (baseline)
3. No-hallucination (baseline)
4. Fairness (from RAI assessment — per-segment accuracy)
5. Reliability (from RAI assessment — failure-mode coverage)
6. Inclusiveness (from RAI assessment — non-English / accessibility)
7. Transparency (from RAI assessment — AI-disclosure surfaced in output)
8. Sensitive-use respect (from sensitive-use report — refuses out-of-scope queries)

## Next steps
1. Fill golden/ fixtures (8 stubs, ~30 min each)
2. Fill adversarial/ fixtures (8 stubs, ~20 min each)
3. Calibrate rubric thresholds via dry-run on 2-3 fixtures
4. First full run: ~/.claude/skills/jstack/bin/run-eval eval/case-analysis-ai/
5. Iterate model / prompts / fixtures until baseline ≥ 7/10 per dimension
6. Pre-launch: ≥ 8/10 per dimension on golden, ≥ 6/10 on adversarial

Estimated operator time to operational eval suite: 8-12 hours.
```

## Compliance integration

- Eval suite IS a Layer 2 launch prerequisite for customer-facing AI per RAI Reliability principle.
- Cross-references seeded from `/rai-impact-assessment` and `/sensitive-use-report`.
- Runner output to `runs/<ts>.jsonl` — append-only, audit-friendly.

## Voice tier note

`voice: internal`. Eval suite is engineering-internal infrastructure.

## Failure modes

- **Target dir exists + non-empty:** ask whether to merge or pick new path. Do not auto-overwrite.
- **No RAI / sensitive-use inputs:** generate with baseline-only rubric, surface that adding those skills' output will enrich.
- **Source has no AI signal (no model call, no prompt):** WARN — is this really an AI feature? Confirm.
- **Runner config can't reference a configured model:** stub with TODO, surface install / config step.

## Examples

**Standard AI eval suite:**
```
> /eval-suite-gen --feature case-analysis-ai --rai-assessment compliance/rai-impact-DRAFT.md --sensitive-use-report compliance/sensitive-use-DRAFT.md
[Generates suite with 8-dimension rubric seeded from inputs]
✓ Suite at eval/case-analysis-ai/. Fill fixtures next.
```

**Baseline-only:**
```
> /eval-suite-gen --feature smart-reply
[3-dimension baseline rubric, generic stubs]
✓ Suite generated. Recommend running /rai-impact-assessment to enrich.
```

## See also

- `/rai-impact-assessment` — feeds dimension scaffolding
- `/sensitive-use-report` — feeds adversarial categories
- `/onerai-prep` — eval suite is a One RAI mitigation deliverable
- `/qa-only` — runs against the eval suite once it has fixtures
- `/jstack-eval` (Phase 8) — orchestrator for running this suite + reporting
