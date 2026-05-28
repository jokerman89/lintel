---
name: li-demo-deliverable-gen
layer: ms-team
description: Generate customer-facing demo deliverables — script, handout, follow-up email — trailblazer-voiced.
color: orange
tools: Read, Write, Bash, Glob
voice: trailblazer
cli_support: [claude-code, codex]
license_note: depends on TRAILBLAZER-CORPUS calibration (T0)
---

# /demo-deliverable-gen

Produces a coordinated set of customer-bound demo deliverables: presentation script (with mode-tagged paragraphs), 1-page handout, and post-demo follow-up email. All trailblazer-voiced, all gated by `/rais-customer-voice-check` before distribution.

Typically run inside a `/scaffold-engagement-demo` repo, but also works on a standalone deliverable request.

## When to use

- New customer demo prep — generate the full deliverable bundle in one pass
- Existing demo needs refreshed deliverables (audience changed, new product to highlight)
- Internal deck → customer-bound rewrite

## When NOT to use

- One-piece content (just script, just handout) — use `/document-generate --target customer-guide` for finer control
- Pre-demo discovery (not yet locked) — content will churn; wait
- Internal-team-only demos — internal voice is fine, skip this skill

## Inputs

- Required `--demo-name <slug>` — short demo name
- Required `--audience <text>` — primary audience description
- Required `--key-message <text>` — one-sentence what-you-want-them-to-remember
- Optional `--source-deck <path>` — existing internal deck to seed from
- Optional `--duration <minutes>` — demo duration target (default: 30)
- Optional `--out-dir <path>` — output directory (default: `deliverables/` if in scaffold repo, else `~/.lintel/demo-deliverables/<demo-name>/`)
- Optional `--include-handout` / `--include-follow-up` — toggle each piece (default: all three)

## Workflow

1. **Preflight.** TRAILBLAZER-CORPUS + CALIBRATION must be present + ≥90%/cell. UNCALIBRATED stamp if not.
2. **Read inputs.** Source deck (if provided), audience, key message.
3. **Generate script (`script-DRAFT.md`):**
   - Opening hook (Provoke / Skewer or Reveal / Curtain — pick what fits the audience)
   - 3-5 substantive sections, each mode-tagged (one cell per section, mix of modes)
   - Call-to-action close (Inspire / Marvel or Provoke / Exception)
   - Duration-balanced (script word count ≈ duration × 130 words/min)
   - Stage directions in `[brackets]` for the presenter
4. **Generate handout (`handout-DRAFT.md`):**
   - 1-page rendered length (target: ≤400 words)
   - Headline (trailblazer-mode-tagged)
   - 3 bullets of "what this changes" (each cell-tagged)
   - Call-to-action (one concrete next step)
5. **Generate follow-up email (`follow-up-email-DRAFT.md`):**
   - Subject line (trailblazer-mode-tagged, ≤8 words)
   - Body 80-150 words
   - One soft ask (meeting, link click, content read)
6. **Cross-link to provenance.** Each output frontmatter includes generator info that `/provenance-track` will pick up.
7. **Mark ALL outputs DRAFT.** Status: `requires-customer-voice-check`.
8. **AI-tell vocab scan + CELA scan.** Block on Tier 1 hit. Regenerate paragraph if hit (up to 2 retries).
9. **Report.**

## Report format

```
Demo deliverable: azure-arc-hybrid-demo

Audience: mid-market public sector IT leadership
Key message: "Manage your on-prem servers the same way you manage Azure — one policy, one view."
Duration target: 30 min
Calibration: CALIBRATED

## Generated artifacts (DRAFT)

1. deliverables/script-DRAFT.md (4.2 KB)
   Word count: 3,950 (matches 30-min target)
   Mode mix: Reveal 50% / Inspire 25% / Provoke 25%
   Cell coverage: R1 R3 R4 I1 I3 P2 P3 (7 of 12 cells)

2. deliverables/handout-DRAFT.md (1.1 KB)
   Word count: 380 (≤400 target)
   Mode mix: Reveal headline + Provoke bullets + Inspire CTA

3. deliverables/follow-up-email-DRAFT.md (0.7 KB)
   Subject: "About the boring slide that mattered" (Reveal/Understatement)
   Body word count: 124

## Voice self-check
✓ Tier 1 AI-tell vocab: clean (0 hits across all 3 artifacts)
✓ CELA pattern scan: clean (no competitor mentions, no Trailblazer-persona external ref)
✓ Brand-value words present in aggregate (Kind ✓, Daring ✓, Deep ✓)

## Status
ALL THREE FILES: DRAFT — require /rais-customer-voice-check before delivery.

## Next steps
1. /rais-customer-voice-check --input deliverables/ (or per-file)
2. /provenance-track each artifact
3. /onecs-check before customer delivery
4. After delivery: archive or move to deliverables/sent/
```

## Compliance integration

- All outputs DRAFT, status `requires-customer-voice-check`.
- Tier 1 AI-tell vocab + CELA pattern scan BLOCKS write on hit (with regen retries).
- Customer-data patterns in inputs (source deck, audience description) BLOCK — sanitize first.
- Provenance pre-seeded for `/provenance-track` to pick up.
- Downstream `/release-ev2` for customer-bearing deliverables refuses without passed voice-check + provenance record.

## Voice tier note

`voice: trailblazer`. This skill PRODUCES trailblazer-voice. Output is DRAFT and gated.

## Failure modes

- **Uncalibrated:** generate with UNCALIBRATED stamp. Downstream refuses distribution.
- **Source deck contains Tier 1 AI-tell vocab:** generation may inherit — WARN, recommend `/msvoice-rewrite` on source first.
- **Audience description vague:** ask for specifics. "Public sector" is too broad; "Nordic mid-market public sector IT leadership" is workable.
- **Duration target unrealistic (e.g. 5 min for AI-feature deep dive):** WARN — content density will hurt; suggest a different duration or scope.
- **All three artifacts requested but `/rais-customer-voice-check` would fail at high threshold:** generate anyway with each artifact's score noted; operator iterates.

## Examples

**Full demo pack:**
```
> /demo-deliverable-gen --demo-name azure-arc-hybrid-demo --audience "mid-market public sector IT leadership" --key-message "manage on-prem like Azure"
[Generates script + handout + follow-up email, all DRAFT]
✓ 3 deliverables generated. Next: /rais-customer-voice-check.
```

**Just script:**
```
> /demo-deliverable-gen --demo-name copilot-for-legal --include-handout=false --include-follow-up=false --audience "legal-tech CIOs"
[Script only]
✓ deliverables/script-DRAFT.md generated.
```

**From existing deck:**
```
> /demo-deliverable-gen --demo-name security-arc --source-deck internal/decks/security-pitch.pptx --audience "CISO + SecOps lead"
[Reads source deck for substance, applies trailblazer voice]
✓ 3 deliverables generated, source deck cross-referenced.
```

## See also

- `/scaffold-engagement-demo` — provides the repo this skill typically runs in
- `/rais-customer-voice-check` — REQUIRED gate after this skill
- `/provenance-track` — required record before distribution
- `/msvoice-rewrite` — for individual paragraph-level rewrites
- OurVoice-corpus.md — calibration source
