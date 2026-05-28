---
name: jstack-rais-customer-voice-check
layer: ms-team
v1_alias: [jstack-customer-voice-check]
description: Gate customer-facing artifacts through 12-cell Trailblazer eval before distribution.
color: red
tools: Read, Bash, Glob
voice: mixed
cli_support: [claude-code, codex]
license_note: depends on OurVoice-corpus.md calibration (T0)
---

# /rais-customer-voice-check

The voice gate. Every customer-bound artifact (PDF, customer-guide, release note, demo script, email draft) MUST pass this check before it leaves the building. Applies the 12-cell Trailblazer rubric from OurVoice-test.md per paragraph and surfaces violations.

T0 calibration must be complete (`OurVoice-calibration.md` ≥90% per cell × ≥10 cells) for this check to be trusted. Pre-calibration runs WARN-only with explicit "uncalibrated" stamp.

## When to use

- Customer-guide draft from `/document-generate --voice trailblazer` ready for distribution
- Release note draft from `/landing-report --voice trailblazer`
- Customer demo deliverable from `/demo-deliverable-gen`
- Any artifact about to be shared OUTSIDE the engineering team
- Pre-deck-review on a customer-facing pitch slide

## When NOT to use

- Engineering-internal doc — voice doesn't matter, skip
- Already passed within the last 24h and content hasn't changed — re-running burns calibration evidence without value
- T0 corpus empty / not calibrated — surfaces nothing useful; run calibration first

## Inputs

- Required `--input <path>` — file or directory to check
- Optional `--per-paragraph` — emit per-paragraph verdict (default: aggregate summary + violations only)
- Optional `--threshold <score>` — minimum overall pass score 0-100 (default: 85)
- Optional `--out <path>` — write report to file (default: stdout)

## Workflow

1. **Preflight.** Verify OurVoice-corpus.md exists + OurVoice-calibration.md shows ≥90% per cell × ≥10 cells. If not: surface UNCALIBRATED warning, proceed with WARN-only mode.
2. **Parse input.** Split into paragraphs. Skip code blocks, frontmatter, YAML, tables.
3. **Per-paragraph eval:**
   - Identify mode_attempted (Reveal / Inspire / Provoke / Neutral)
   - If non-Neutral: identify technique (one of 12 cells)
   - Score against rubric: kind_score, daring_score, deep_score (each 1-10), ground_rules_passed (list), ground_rules_violated (list), anti_ai_vocab_detected (list)
   - Verdict: PASS / FAIL with reason
4. **Aggregate.** Overall score = paragraph average. Violations list.
5. **Compare to threshold.** PASS if overall ≥ threshold AND zero P1 violations (P1 = AI-tell Tier 1 vocab detected, OR CELA-restricted phrasing like competitor name disparagement).
6. **Report.**

## Report format

```
Customer Voice Check: docs/guides/billing.md

Calibration status: CALIBRATED (OurVoice-calibration.md ≥90% per cell × 11 cells)
Threshold: 85

## Aggregate
Overall score: 88/100  ✓ PASS
P1 violations: 0
P2 violations: 1
P3 violations: 3

## Per-paragraph (--per-paragraph not enabled — see summary only)

## Violations

[P1] none

[P2] paragraph 4
   Mode attempted: Provoke / Skewer
   Issue: punching down — names competitor implicitly ("the other major cloud provider")
   Rule: CELA / external-use — never disparage competitors by reference, even oblique
   Fix: rewrite without competitor reference

[P3] paragraph 7
   Mode attempted: Inspire / Marvel
   Issue: AI-tell Tier 2 vocab ("leverage") in customer-facing paragraph
   Fix: use "use"

[P3] paragraph 9
   Mode attempted: Reveal / Curtain
   Issue: marvel without specific detail — "thousands of customers" is too vague
   Fix: substitute concrete number or specific anecdote

[P3] paragraph 11
   Mode attempted: Reveal / Understatement
   Issue: hedge phrase "we believe" — see OurVoice-corpus.md Tier 3 traps
   Fix: show, don't say

## Verdict
✓ PASS (score 88/100, no P1, threshold 85)
Recommendation: fix P2 + P3 before final distribution.
```

## Compliance integration

- This skill IS a Layer 2 gate at distribution time. The 5 always-on rules ALSO apply (sanity-scan, customer-data, production-mutation auth, MS SSO, first-party-first).
- A FAIL verdict from this skill BLOCKS downstream `/release-ev2` for the customer-bound artifact.
- An UNCALIBRATED stamp surfaces in any downstream reference — `/release-ev2` will refuse to land artifacts gated by an UNCALIBRATED check.

## Voice tier note

`voice: mixed`. The skill ITSELF is internal-voice (the report is engineering-internal). Its JOB is to evaluate trailblazer-voice output. It produces no trailblazer voice; it judges it.

## Failure modes

- **Corpus or calibration missing:** UNCALIBRATED stamp + WARN mode. Skill still produces a report but cannot certify PASS.
- **Input not parseable (binary, image):** report unsupported format + exit. Do not silently degrade.
- **All paragraphs verdict Neutral:** ask whether the input is actually customer-facing or just neutral prose. Neutral text doesn't need this skill.
- **Threshold met but P1 violations present:** STILL FAIL. P1 overrides aggregate. AI-tell vocab + CELA violations are non-negotiable.
- **Eval crashes on a paragraph (rare):** mark paragraph as NOT_EVALUATED, continue, surface in report.

## Examples

**Standard guide check:**
```
> /rais-customer-voice-check --input docs/guides/billing.md
Score 88/100, 0 P1, 1 P2, 3 P3. ✓ PASS (fix P2+P3 recommended).
```

**Per-paragraph deep:**
```
> /rais-customer-voice-check --input release-notes-draft.md --per-paragraph --out check-report.md
12 paragraphs evaluated, report at check-report.md.
```

**Strict threshold:**
```
> /rais-customer-voice-check --input pitch-deck.md --threshold 95
Score 88/100 — below threshold (95). ✗ FAIL. Fix violations + retry.
```

## See also

- OurVoice-test.md — the eval prompt this skill applies
- OurVoice-corpus.md — the calibration anchor
- OurVoice-calibration.md — current per-cell accuracy
- `/msvoice-rewrite` — rewrite an internal-voice draft to trailblazer
- `/release-ev2` — reads this skill's verdict as a gate
- `/jstack-eval` (Phase 8) — runs this against OurVoice-corpus.md to maintain calibration
