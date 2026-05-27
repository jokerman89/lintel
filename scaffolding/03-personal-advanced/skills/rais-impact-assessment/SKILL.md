---
name: jstack-rais-impact-assessment
v1_alias: [jstack-rai-impact-assessment]
description: Generate an RAI Impact Assessment — fairness, reliability, privacy, inclusiveness, transparency, accountability.
color: orange
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

# /rais-impact-assessment

Generates a Responsible AI Impact Assessment across the six MS RAI principles: Fairness, Reliability & Safety, Privacy & Security, Inclusiveness, Transparency, Accountability. Output is a structured assessment that informs design decisions + feeds the Sensitive Uses and One RAI review processes.

Distinct from `/rais-sensitive-use` (category classification) and `/onerai-submit-draft` (One RAI submission draft). Impact assessment is the BROADER design-time RAI lens.

## When to use

- Design-phase of an AI feature — apply RAI principles to shape the design
- Pre-launch verification — confirm each principle has been addressed
- Post-incident — re-assess where the existing assessment failed
- Periodic review — annual or on significant model/data change

## When NOT to use

- Non-AI features
- Internal-only AI with no end-user impact
- Already-thorough assessment with no material change

## Inputs

- Required `--feature <name>` — short name for the AI feature
- Optional `--source <path>` — design doc / spec for the feature
- Optional `--sensitive-use-report <path>` — output from `/rais-sensitive-use`
- Optional `--out <path>` — output report path (default: `~/.jstack/rai/<feature>-impact-assessment.md`)
- Optional `--depth <quick|thorough>` — quick = 1-2 lines per principle; thorough = structured per-principle questionnaire

## Workflow

1. **Read inputs.** Source + sensitive-use report if present.
2. **Per RAI principle, structured assessment:**

   **Fairness:**
   - What groups could be impacted differently?
   - What bias sources exist (training data, optimization target, deployment context)?
   - How is fairness measured? (named metric)
   - Mitigation strategy

   **Reliability & Safety:**
   - What failure modes are anticipated?
   - What's the worst-case impact of a confident-wrong output?
   - How are failures detected (monitoring, eval set, user feedback)?
   - Rollback / safe-state path

   **Privacy & Security:**
   - What personal data is processed?
   - Data minimization applied (collect / process only what's needed)?
   - Secure handling (encryption, access controls, audit)?
   - Cross-link to `/dpia-submit-draft` output if available

   **Inclusiveness:**
   - Accessibility: does the feature work for users with disabilities?
   - Language: how does it perform in languages other than English?
   - Cultural context: does it surface culturally-specific knowledge?
   - Underrepresented groups: are they served as well as majority?

   **Transparency:**
   - Are users aware they're interacting with AI?
   - Are capabilities + limitations communicated?
   - Is provenance traceable (where did the output come from)?
   - Disclosure mechanism (link to `/rais-transparency-note` output if available)

   **Accountability:**
   - Who is the responsible owner?
   - What's the escalation path on incident?
   - What audit trail exists?
   - How are user feedback / complaints handled?

3. **Build report.** Per principle: assessment + mitigation + open questions.
4. **Summary score.** Per principle: ADDRESSED / PARTIAL / GAP. Overall: ready-for-launch / needs-work.
5. **Output.**

## Report format

```
RAI Impact Assessment: feature=case-analysis-ai

Source: docs/design/case-analysis-ai.md
Sensitive-Use cross-ref: present (4 triggered categories)
Depth: thorough

## Principle assessments

### Fairness — PARTIAL
- Impacted groups: legal-system users across socio-economic spectrum, non-native language speakers
- Bias sources: training data may underrepresent informal-sector cases, dialectal Swedish
- Measurement: per-segment accuracy on labeled eval set (planned, not yet built)
- Mitigation: planned eval set construction Q3 2026; recommend launch gate

### Reliability & Safety — PARTIAL
- Failure modes: hallucinated legal claim, misclassified case type, missed deadline indication
- Worst-case: legally inaccurate advice acted upon by user
- Detection: human-in-loop required (designed in), output confidence threshold
- Rollback: feature flag, rollback to retrieval-only mode

### Privacy & Security — ADDRESSED
- Personal data: case description text (Sensitive class)
- Minimization: only fields necessary for analysis, no PII enrichment
- Security: TLS in transit, encryption at rest, audit per access
- DPIA: prep'd via /dpia-submit-draft, HIGH-RISK triggered (Article 35), Privacy consultation scheduled

### Inclusiveness — GAP
- Accessibility: not yet evaluated; UI assessment pending
- Language: Swedish only at launch; English Q4 2026; no plan for less-resourced languages
- Cultural: legal context is Swedish-specific; transfer to other jurisdictions out-of-scope
- Underrepresented: legal aid context underrepresented; eval set must include

### Transparency — PARTIAL
- AI-awareness: planned disclosure paragraph, exact wording TBD
- Capabilities + limitations: drafted in /rais-transparency-note output (DRAFT)
- Provenance: each output cites which legal sources informed it
- Disclosure: pending /rais-customer-voice-check on disclosure copy

### Accountability — ADDRESSED
- Owner: SE engineer + CAIP Field-CTO (joint)
- Escalation: Field-CTO 24h, then RAI team
- Audit trail: per-query log retained 90 days, then aggregate-only
- User feedback: feedback button + escalation form

## Summary
| Principle      | Status     |
|----------------|------------|
| Fairness       | PARTIAL    |
| Reliability    | PARTIAL    |
| Privacy        | ADDRESSED  |
| Inclusiveness  | GAP        |
| Transparency   | PARTIAL    |
| Accountability | ADDRESSED  |

Overall: NEEDS WORK before launch.

## Open questions
1. When will Fairness eval set be built? (blocks launch)
2. Is Swedish-only-at-launch acceptable per Inclusiveness, or must it ship multilingual? (operator + product decision)
3. Final transparency disclosure wording — needs /rais-customer-voice-check
```

## Compliance integration

- Implements design-time RAI review. Operator can run BEFORE `/rais-sensitive-use` or AFTER (best to iterate).
- A GAP on any principle for a customer-facing AI feature: BLOCKS launch (operator can override only with documented reason + RAI team co-sign).
- Output cross-linked by `/onerai-submit-draft` for One RAI submission.

## Voice tier note

`voice: internal`. RAI assessment is MS-internal.

## Failure modes

- **All principles ADDRESSED:** WARN — honest assessment usually surfaces ≥1 PARTIAL. Operator may be over-confident.
- **All principles GAP:** halt — feature is not ready for this level of review. Recommend deeper design work first.
- **Source unavailable + free-text only:** valid but assessment marked "self-reported, not source-verified".
- **Operator skips a principle:** that principle is GAP by default — refuse to mark ADDRESSED without justification.

## Examples

**Thorough design-time:**
```
> /rais-impact-assessment --feature case-analysis-ai --source docs/design/case-analysis.md --depth thorough
[Six-principle structured questionnaire]
✓ Report generated. Overall: NEEDS WORK (2 PARTIAL, 1 GAP). 3 open questions.
```

**Quick post-incident:**
```
> /rais-impact-assessment --feature billing-prediction --depth quick
[1-2 lines per principle]
✓ Quick assessment. Fairness GAP — re-eval after incident root cause.
```

## See also

- `/rais-sensitive-use` — category-specific triage (complementary)
- `/onerai-submit-draft` — consumes this output
- `/dpia-submit-draft` — Privacy & Security principle cross-link
- `/rais-transparency-note` — Transparency principle cross-link
- MS RAI principles canonical doc (Phase 6 reference)
