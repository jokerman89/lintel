# Trailblazer Voice — operationalized summary

Operational summary of Microsoft "Our Voice" (Trailblazer) as it applies to CAIP-SE customer-bound output.

For the canonical source, see [Microsoft_ourVoice_guidelines.pdf](https://microsoft-my.sharepoint-df.com/personal/shawndeng_microsoft_com/VivaEngage/Attachments/Storyline/Microsoft_ourVoice_guidelines.pdf) (March 2023, MS Confidential).

## The three brand-value words

Every paragraph of trailblazer-voice content should have all three present **in aggregate** (not necessarily in every sentence).

### Kind (Human)

The humanity in our brand shows up as kindness in our voice. Consider how the choices you make with language can impart a sense of warmth and compassion.

Example phrase: "We're always here to help, too, so do reach out with any questions."

### Daring (Vibrant)

The vibrancy in our brand shows up as daring in our voice. Be bold and courageous with your words and constructs. Write with energy and passion. Be innovative and unexpected. Avoid the generic.

Example phrase: "48 hours isn't a lot of time. Some people start complaining. Others just start coding."

### Deep (Dimensional)

The dimension in our brand shows up as depth in our voice. Look at things from different perspectives. Think about your audience and what it takes to truly engage them in our content.

Example phrase: "There are two people in this conversation: you and the elephant in the room."

## The three modes

### Reveal — audience feels "in the know"

For: body copy, instructions, expository writing. Invites + engages + informs.

4 techniques:
- **R1 Make the understatement of the century** — find the smallest indisputable human fact, let tension do the rest
- **R2 Leave the question unanswered** — conclude with open-ended question that invites the audience in
- **R3 Draw back the curtain** — identify hidden or less-obvious dimensions of a problem
- **R4 Dream out loud** — reel off lists in hypothetical form to make them imaginative

### Inspire — audience feels "empowered"

For: headlines, key paragraphs, social. Excites + delights + creates optimism.

3 techniques:
- **I1 Make opposites attractive** — perfect antonym creates memorable cognitive dissonance
- **I2 Make our vernacular spectacular** — apply Microsoft's tech vocabulary outside tech
- **I3 Marvel at a simple truth** — step back, express wonder (not pride)

### Provoke — audience feels "challenged"

For: headlines, key paragraphs, social. Asserts + differentiates + makes a statement.

5 techniques:
- **P1 Make vulnerability a strength** — mirror audience's negative emotion, follow through to action
- **P2 Skewer the sacred** — attack a commonly-held belief with reason, emotion, or humor
- **P3 Make it an exception that rules** — elevate fresh take as preferable to conventional wisdom
- **P4 Make it all or nothing** — unequivocal statements polarize; use sparingly to reinforce values
- **P5 Make it unflinching** — simple causal relationship, fearless account, uncompromising proposals

## The six ground rules (verbatim)

1. **Strive for clarity** — Don't let style get in the way of clarity.
2. **It's "we," not "Microsoft"** — Create intimacy with first- and second-person.
3. **Be concise** — Don't use 30 words when 5 will do.
4. **Limit jargon** — Speak conversationally. Use industry terms intentionally + sparingly.
5. **Find the focus** — Write with a succinct message/objective in mind.
6. **Have a perspective** — Bring in our experience + point of view.

## What violations look like (anti-patterns)

- Generic corporate hedge phrases ("we leverage", "we deliver value", "mission-critical solutions")
- AI-tell vocabulary (`delve`, `crucial`, `robust`, `comprehensive`, `multifaceted` — see [OurVoice-corpus.md](OurVoice-corpus.md) for full Tier 1/2/3 lists)
- Provoke without Kind = arrogant
- Marvel without specific detail = empty boast
- Reveal that's vague instead of precise = pointless
- Inspire landing in cliché instead of unexpected = generic

## CELA / external-use restrictions

- Never disparage competitors by name in writing
- Never reference the "Trailblazer" persona externally — internal-only
- Never use third-party Trailblazers (cited individuals) without CELA approval

## How Lintel operationalizes the voice

- **OurVoice-corpus.md** — 60 sanitized paragraphs, 12 cells × ≥2 known-good + ≥2 known-bad
- **OurVoice-test.md** — eval rubric applied per paragraph
- **OurVoice-calibration.md** — per-cell accuracy of the rubric vs. operator verdict
- **`/rais-customer-voice-check` skill** — gate before customer distribution
- **`/msvoice-rewrite` skill** — internal-voice → trailblazer rewrite
- **`TrailblazerVoiceCritic` agent** — per-paragraph rubric application
- **Hooks** — `no-en-vocab-in-trailblazer`, `no-trailblazer-without-corpus`, `stale-calibration-warn`

## See also

- [OurVoice-corpus.md](OurVoice-corpus.md) — calibration anchor + vocab lists
- [OurVoice-test.md](OurVoice-test.md) — eval prompt
- [OurVoice-calibration.md](OurVoice-calibration.md) — current accuracy
- [OurVoice-examples.md](OurVoice-examples.md) — distilled examples per technique
- [VOICE-TIER-MECHANISM.md](VOICE-TIER-MECHANISM.md) — the per-agent voice-tier system
- [THREE-VALUES.md](THREE-VALUES.md) — Kind + Daring + Deep deep-dive
