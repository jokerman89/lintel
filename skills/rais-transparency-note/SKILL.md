---
name: jstack-rais-transparency-note
layer: ms-team
v1_alias: [jstack-transparency-doc-gen]
description: Generate transparency note for an AI feature — capabilities, limitations, data, disclosure.
color: yellow
tools: Read, Write, Bash
voice: mixed
cli_support: [claude-code, codex]
license_note: customer-bearing artifact; T0 calibration required for trailblazer sections
---

# /rais-transparency-note

Generates a customer-facing transparency note for an AI feature. Aligns with MS RAI transparency principle + the MS "transparency note" template format. Output is BOTH a machine-friendly internal record (engineering frontmatter) and a customer-friendly rendered document (trailblazer-voiced).

## When to use

- Customer-facing AI feature ready for launch — transparency note is REQUIRED
- Significant change to existing transparency note (model upgrade, capability change, new limitation discovered)
- Periodic review (typically aligned with model retraining or major release)
- Public-facing disclosure (web page, in-product modal, doc site)

## When NOT to use

- Internal-only AI (no customer surface)
- Feature without AI involvement
- Existing transparency note current + no material change

## Inputs

- Required `--feature <name>` — short name for the AI feature
- Optional `--source <path>` — code, design doc, RAI assessment
- Optional `--audience <consumer|business|developer>` — affects tone + technical depth (default: business)
- Optional `--rai-assessment <path>` — output from `/rais-impact-assessment` (auto-populates limitations + risk awareness)
- Optional `--onerai-draft <path>` — output from `/onerai-submit-draft` (cross-references)
- Optional `--out <path>` — output (default: `compliance/transparency-note-DRAFT.md` if in scaffold repo)

## Workflow

1. **Read inputs.** RAI assessment (if present) gives limitations + risk surface. One RAI draft gives intended uses.
2. **Structured intake for missing data:**
   - System purpose (one sentence)
   - Intended uses (3-5 named scenarios)
   - Out-of-scope / unsupported uses (explicit)
   - System capabilities (concrete list)
   - System limitations (concrete list — honest, not hedged)
   - Data the system uses (training source, runtime input)
   - Decisions the system makes / informs (what's automated vs. suggested vs. informational)
   - Human-in-the-loop mechanisms
   - Feedback + appeal mechanisms
   - Disclosure point (where + how is the user told this is AI?)
3. **Generate two parallel artifacts:**

   **Internal frontmatter record** (`compliance/transparency-internal.yaml`):
   ```yaml
   feature: <name>
   audience: <consumer|business|developer>
   capabilities: [...]
   limitations: [...]
   intended_uses: [...]
   out_of_scope: [...]
   data: { training_source, runtime_input, retention }
   human_in_loop: <description>
   rai_assessment: <path>
   onerai_draft: <path>
   ```

   **Customer-rendered document** (`compliance/transparency-note-DRAFT.md`):
   - Title: simple, no jargon
   - "What this is" (Reveal/Curtain — what's actually happening)
   - "What it can do" (factual capability list — no boasting)
   - "What it can't do" (factual limitation list — no hedging)
   - "How to know if it got something wrong" (Provoke/Unflinching — honest about failure modes)
   - "What we do with your data" (Reveal/Curtain — concrete, specific)
   - "How to give us feedback or appeal" (concrete, with links)
   - "When you're using this" (AI disclosure statement — required by RAI)

4. **Compliance scans:**
   - AI-tell vocab Tier 1 (BLOCK on hit, regen)
   - CELA pattern (BLOCK on hit)
   - Honest-limitations check: limitation count ≥ capability count - 2 (forces honest accounting)
5. **Mark DRAFT.** Frontmatter `voice: trailblazer-draft, status: requires-customer-voice-check`.
6. **Report.**

## Report format

```
Transparency doc: feature=case-analysis-ai (business audience)

Inputs: rai-impact-assessment present, onerai-DRAFT present
Capabilities listed: 6
Limitations listed: 7 (ratio 6/7 — balanced, good)

## Generated
1. compliance/transparency-internal.yaml — machine-readable record
2. compliance/transparency-note-DRAFT.md — customer-facing doc (4.1 KB, 850 words)

## Customer-doc structure
- "What this is" (Reveal/Curtain)
- "What it can do" — 6 concrete capabilities
- "What it can't do" — 7 concrete limitations
- "How to know if it got something wrong" (Provoke/Unflinching)
- "What we do with your data" (Reveal/Curtain)
- "How to give feedback or appeal" — feedback button + 24h escalation
- AI disclosure: "You're interacting with AI. Here's what that means: ..."

## Voice self-check
✓ Tier 1 AI-tell vocab: clean
✓ CELA scan: clean
✓ Honest-limitations: ratio 6/7 (passes)
✓ Brand values aggregate: Kind ✓ Daring ✓ Deep ✓

## Status
DRAFT — requires /rais-customer-voice-check before distribution.

## Next steps
1. /rais-customer-voice-check --input compliance/transparency-note-DRAFT.md
2. /provenance-track this artifact
3. Operator: place on customer-facing surface (website, in-product, doc site)
4. Set review schedule (typically annual or on model upgrade)
```

## Compliance integration

- Implements Item 7 of the 7 on-demand compliance items.
- Output marked DRAFT; downstream `/release-ev2` refuses without passed voice-check.
- Honest-limitations check enforces an honesty ratio (limitations ≥ capabilities − 2). Hides nothing.
- Cross-links provenance + One RAI + RAI assessment artifacts.

## Voice tier note

`voice: mixed`. Internal YAML record is internal voice. Customer-facing markdown is trailblazer-DRAFT.

## Failure modes

- **No RAI assessment present + customer-facing feature:** WARN — transparency without RAI input is shallow. Recommend running `/rais-impact-assessment` first.
- **Capabilities outnumber limitations by 3+:** REJECT — honest accounting requires more limitations. Force operator to add.
- **Tier 1 AI-tell vocab in generated text:** regenerate paragraph up to 2 attempts; fail closed if persistent.
- **"AI disclosure" section vague ("we use technology"):** REJECT — must explicitly name AI / model class. RAI principle.
- **Audience mismatch (e.g. consumer audience but text is full of MS-jargon):** WARN, regenerate.

## Examples

**Business-audience transparency note:**
```
> /rais-transparency-note --feature case-analysis-ai --audience business --rai-assessment compliance/rai-impact-DRAFT.md
[Reads RAI assessment, generates both artifacts]
✓ DRAFT generated. Next: /rais-customer-voice-check.
```

**Consumer audience (simpler language):**
```
> /rais-transparency-note --feature smart-summary --audience consumer
[Plain-language, no jargon, shorter sentences]
✓ DRAFT generated (consumer-tone). 6 cap / 5 lim.
```

**Developer audience (technical):**
```
> /rais-transparency-note --feature copilot-completions --audience developer
[Includes model type, context window, prompt strategy, eval methodology]
✓ DRAFT generated (technical depth).
```

## See also

- `/rais-impact-assessment` — feeds transparency note's limitations + risks
- `/onerai-submit-draft` — cross-referenced
- `/rais-customer-voice-check` — required gate
- `/onecs-check` Item 7 — surfaces transparency-note requirement
- MS Transparency Note template (Phase 6 reference)
