---
name: jstack-dsb-submit-draft
layer: ms-team
v1_alias: [jstack-dsb-prep]
description: Prepare a Data Sharing Board submission draft — recipients, purpose, data class, retention.
color: orange
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

# /dsb-submit-draft

Drafts a Data Sharing Board (DSB) submission for sharing data outside its intended audience. Output is a structured form draft the operator refines + submits to the MS-internal DSB portal.

DSB is the body that approves data flows leaving their original collection context — sharing with a partner, exporting to a new region, exposing to a new audience class.

## When to use

- Planning to share data with a new third party (partner, vendor, customer)
- Exporting data to a different geography (e.g. EU → US)
- Exposing data to a new audience class (e.g. internal → public)
- Significantly changing scope of existing share (more data, more recipients, longer retention)

## When NOT to use

- Within-Microsoft same-audience data flow — no DSB needed
- One-time analytics aggregate (no individual-level data shared) — typically exempt
- Customer's own data being returned to them — that's not a "share"

## Inputs

- Required `--share-name <name>` — short name for the share
- Optional `--system <path>` — code or design doc for the system that will do the sharing
- Optional `--out <path>` — output draft path (default: `~/.jstack/dsb/<share>-dsb-DRAFT.md`)

## Workflow

1. **Structured intake via AskUserQuestion.** Gather:
   - What data is being shared (categories, classes, fields)
   - With whom (recipient organization, internal team, etc.)
   - For what purpose (specific, named — not generic "analytics")
   - Legal basis (consent, contract, legitimate interest, regulatory)
   - Retention duration at recipient
   - Deletion mechanism at recipient
   - Audit trail mechanism
2. **Data class assessment.** For each data category: assign MS Business Data class (Public / Non-business / Business / Sensitive / Highly Sensitive / Confidential). Flag any class ≥ Business as high-risk.
3. **Build draft sections:**
   - **Share overview** (one paragraph)
   - **Data inventory** (table: category, fields, class, volume estimate)
   - **Recipient profile** (org, region, regulatory regime)
   - **Purpose statement** (specific, scoped)
   - **Legal basis**
   - **Retention + deletion**
   - **Security controls** (encryption in transit + at rest, access controls)
   - **Audit + monitoring** (who reviews what, how often)
   - **Risk assessment** (3-5 named risks, severity, mitigation)
   - **Termination conditions** (when does the share end automatically?)
4. **Compliance scan.** Customer-data patterns in draft body BLOCKED (use placeholders).
5. **Mark DRAFT.**
6. **Report.**

## Report format

```
DSB prep: share-name=quarterly-usage-export-to-partner

Output: ~/.jstack/dsb/quarterly-usage-export-to-partner-dsb-DRAFT.md (3.2 KB)
Recipient: partner-org (Nordic region, GDPR regime)
Purpose: quarterly product-usage analytics for joint roadmap

## Data inventory
- Aggregated usage counts (Public class) — LOW risk
- Per-customer feature adoption flags (Business class) — MEDIUM risk
- Free-text feedback excerpts (Sensitive class) — HIGH risk — flag for additional review

## Class summary
- 1 Public
- 1 Business
- 1 Sensitive ⚠

## Risk highlights
1. Sensitive-class feedback excerpts — recommend redaction or aggregation before share
2. Recipient is in GDPR regime — Article 28 processor agreement required
3. Retention at recipient: 12 months — confirm with deletion attestation

## Next steps
1. Operator refines DRAFT (especially redaction strategy for Sensitive class)
2. Verify Article 28 agreement with recipient legal
3. Submit to DSB portal
4. After approval: implement deletion-attestation hook
```

## Compliance integration

- Implements Item 5 of the 7 on-demand compliance items.
- Sensitive / Confidential class data: BLOCKS the draft from finalizing without additional gates (operator may need separate Privacy review).
- DRAFT only. Submission to DSB portal is operator-driven.
- Customer-data patterns in form body → BLOCK (use placeholders + describe abstractly).

## Voice tier note

`voice: internal`. DSB submission is MS-internal review form.

## Failure modes

- **Data class can't be assigned (operator unsure):** ask for clarification on each field. Default to HIGHER class on ambiguity.
- **Recipient is outside MS + no contract referenced:** WARN — DSB will reject. Surface as blocker.
- **Retention "indefinite" or unbounded:** REJECT — DSB requires bounded retention. Refuse to finalize.
- **Purpose statement is generic ("analytics", "improvement"):** WARN — DSB reviewer will push back. Require specific named outcome.
- **Output path collides with active draft:** ask whether to update or new variant.

## Examples

**Partner share:**
```
> /dsb-submit-draft --share-name quarterly-usage-export-to-partner
[Intake interview, data class assignment]
✓ DRAFT at ~/.jstack/dsb/quarterly-usage-export-to-partner-dsb-DRAFT.md
  1 Sensitive class flagged — see report for redaction recommendation.
```

**With system reference:**
```
> /dsb-submit-draft --share-name internal-research-export --system src/analytics/research_export.py
[Reads system to infer data fields]
✓ DRAFT generated with fields auto-detected.
```

## See also

- `/onecs-check` Item 5 — surfaces DSB requirement
- `/dpia-submit-draft` — complementary for personal data
- `/onerai-submit-draft` — if AI is involved in the data processing
- MS-internal DSB portal — destination for DRAFT
