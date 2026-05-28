---
name: li-rais-sensitive-use
layer: ms-team
v1_alias: [li-sensitive-use-report]
description: Classify an AI feature against MS Sensitive Uses categories — produces structured report.
color: red
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

# /rais-sensitive-use

Evaluates an AI feature against the MS Responsible AI Sensitive Uses categories — uses that warrant additional review because of the consequence of error. Output is a structured report consumed by `/onerai-submit-draft` and the Sensitive Uses review process.

The MS Sensitive Uses categories (illustrative — operator-extendable via `~/.lintel/sensitive-uses.yaml`):
- Decisions consequential for individuals (legal, financial, health, employment)
- Inferring emotional or psychological state
- Biometric identification / categorization
- Public safety / law enforcement
- Critical infrastructure
- Education access / outcomes
- Welfare benefits eligibility
- Migration / asylum / border processes
- AI used by or about minors
- AI in elections / democratic processes
- Generative content at scale without provenance

## When to use

- Before greenlighting an AI feature's design — early triage prevents late-stage rework
- Pre-`/onerai-submit-draft` — feeds risk register
- Periodic re-assessment when feature scope changes
- After incident / customer feedback that suggests previously-unflagged sensitive use

## When NOT to use

- AI for internal engineering productivity (no end-user impact)
- Already-classified feature with no scope change
- Non-AI features

## Inputs

- Required `--feature <name>` — short name for the AI feature
- Optional `--source <path>` — code or design doc
- Optional `--out <path>` — output report path (default: `~/.lintel/rai/<feature>-sensitive-use.md`)

## Workflow

1. **Structured intake via AskUserQuestion.** Per Sensitive Uses category, ask:
   - "Does this feature potentially fit this category? (yes / no / partial)"
   - For yes / partial: "Describe the fit in 1-2 sentences"
2. **Severity assessment.** For each YES / PARTIAL fit, ask:
   - Decision impact (informational / suggestive / consequential)
   - Reversibility (reversible / hard-to-reverse / irreversible)
   - Scale (1-10 users / 100-1000 / 10k+)
3. **Pattern matching.** Run regex/keyword scan over `--source` for sensitive-use signal phrases ("hire", "approve loan", "diagnose", "detect emotion", "identify face", "minor"). Surface matches even if operator didn't flag the category.
4. **Build report:**
   - **Feature one-liner**
   - **Categories assessed** (table: category × fit × severity × scale)
   - **Triggered categories** (any YES / PARTIAL)
   - **Source-scan matches** (signal phrases found)
   - **Recommendation:** None / Sensitive-Uses review recommended / Sensitive-Uses review REQUIRED
5. **Output.** Write report.
6. **Cross-link.** If recommendation ≠ None: emit cross-reference for `/onerai-submit-draft` to consume.

## Report format

```
Sensitive Use Report: case-analysis-ai

Feature one-liner: AI-assisted analysis of customer legal-case description, producing
                   structured legal-context summary + recommended next steps.

## Categories assessed
| Category                                            | Fit     | Severity | Scale  |
|-----------------------------------------------------|---------|----------|--------|
| Decisions consequential for individuals (legal)     | YES     | HIGH     | 10k+   |
| Decisions consequential for individuals (financial) | PARTIAL | MEDIUM   | 10k+   |
| Inferring emotional state                           | NO      | -        | -      |
| Biometric                                           | NO      | -        | -      |
| Public safety                                       | NO      | -        | -      |
| Critical infrastructure                             | NO      | -        | -      |
| Education access                                    | NO      | -        | -      |
| Welfare benefits                                    | NO      | -        | -      |
| Migration / asylum                                  | NO      | -        | -      |
| AI used by/about minors                             | PARTIAL | MEDIUM   | low    |
| AI in elections                                     | NO      | -        | -      |
| Generative content at scale                         | YES     | MEDIUM   | 10k+   |

## Triggered categories
- Legal decisions (HIGH)
- Financial decisions (MEDIUM, partial — when case involves money)
- Use by/about minors (MEDIUM, partial — guardian-on-behalf cases)
- Generative content at scale (MEDIUM — analysis output produced at scale)

## Source-scan matches
- "legal advice" — appears 8x in src/lib/case-analysis.ts
- "financial damages" — appears 3x
- "case involving minor" — appears 1x in tests/fixtures/

## Recommendation
Sensitive-Uses review REQUIRED before launch.
  - Legal-decisions category requires human-in-the-loop verification path
  - Generative content at scale requires provenance + disclosure mechanism
  - Minor-involvement requires guardian-consent flow

## Next steps
1. Run /onerai-submit-draft --feature case-analysis-ai --sensitive-use-report <this file>
2. Schedule Sensitive Uses review with MS RAI team
3. Implement mitigations before launch
```

## Compliance integration

- Implements Item 4 of the 7 on-demand compliance items.
- A TRIGGERED category with HIGH severity → REQUIRES Sensitive Uses review (operator cannot self-clear).
- Output cross-linked by `/onerai-submit-draft` for risk register seeding.
- Customer-data patterns in form body → BLOCK (placeholders only).

## Voice tier note

`voice: internal`. RAI assessment is MS-internal.

## Failure modes

- **Operator answers "no" to all categories despite source-scan matches:** WARN — likely missed category. Re-prompt with the source matches surfaced.
- **All categories triggered at HIGH:** WARN — likely over-classification. Operator should refine; not every feature is sensitive across all axes.
- **Operator unsure on a category:** PARTIAL is the right answer. Don't force yes/no.
- **Source not provided + free-text intake only:** valid, but report flagged "self-reported, not source-verified".

## Examples

**AI feature triage:**
```
> /rais-sensitive-use --feature case-analysis-ai --source src/lib/case-analysis.ts
[Intake interview + source scan]
✓ 4 categories triggered. Sensitive-Uses review REQUIRED.
  Next: /onerai-submit-draft --sensitive-use-report <this output>.
```

**Internal tool clear:**
```
> /rais-sensitive-use --feature engineering-velocity-dashboard
[All NO]
✓ No categories triggered. Recommendation: None.
```

## See also

- `/onerai-submit-draft` — consumes this output
- `/onecs-check` Item 4 — surfaces Sensitive-Uses requirement
- `/dpia-submit-draft` — complementary when personal data is involved
- `~/.lintel/sensitive-uses.yaml` — operator-extendable category list
- MS RAI Sensitive Uses internal portal
