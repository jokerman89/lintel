# Three Values — Kind, Daring, Deep

The three brand-value words that anchor Microsoft "Our Voice". Operationalized for CAIP-SE customer-bound output.

## The values

### Kind — the Human in our brand

**Microsoft's definition:**
> The humanity in our brand shows up as kindness in our voice. Consider how the choices you make with language can impart a sense of warmth and compassion.

**Operational signals (present):**
- "We" / "you" / "your" / "us" — first + second person
- Acknowledgment of audience state (frustrated, time-pressed, vulnerable)
- "We're here to help" without performative service-speak
- Warmth without sentimentality

**Operational signals (absent / violated):**
- Distancing third-person ("Microsoft will deliver")
- Patronizing ("rest assured", "don't worry your head about it")
- Performative empathy without follow-through ("we understand your pain")
- Cold transactional ("Please find attached the requested document")

**Example present:**
> We're always here to help, too, so do reach out with any questions.

**Example absent:**
> Microsoft is committed to providing world-class support across the entire customer journey.

### Daring — the Vibrant in our brand

**Microsoft's definition:**
> The vibrancy in our brand shows up as daring in our voice. Be bold and courageous with your words and constructs. Write with energy and passion. Be innovative and unexpected! Avoid the generic.

**Operational signals (present):**
- Specific concrete language (not generic abstractions)
- Bold opening lines, polarizing value statements
- Antonym constructions that surprise
- Personal stake / point of view
- Energy in word choice (not hedge phrases)

**Operational signals (absent / violated):**
- "Robust", "comprehensive", "best-in-class" (Tier 1 generic vocab)
- "In today's rapidly evolving landscape..."
- "We aspire to deliver value..."
- "It goes without saying..." (then why say it?)
- Avoiding stakes, hedging every claim

**Example present:**
> 48 hours isn't a lot of time. Some people start complaining. Others just start coding.

**Example absent:**
> In today's competitive landscape, organizations must embrace comprehensive innovation to remain relevant.

### Deep — the Dimensional in our brand

**Microsoft's definition:**
> The dimension in our brand shows up as depth in our voice. Look at things from different perspectives. Think about your audience and what it takes to truly engage them in our content.

**Operational signals (present):**
- Specific concrete details (numbers, sources, names of techniques)
- Multiple perspectives surfaced
- Audience-awareness (different angle for different reader)
- Naming the non-obvious
- Earned conclusions (not asserted)

**Operational signals (absent / violated):**
- Vague generalities
- Single perspective without acknowledging others
- Asserted conclusions without grounding
- One-size-fits-all phrasing
- Surface-level observations only

**Example present:**
> Ten years ago, we had four datacenters. Today, we have more than 60 regions in over 140 countries, and a fiber network long enough to wrap the Earth twice. We built it one cable at a time. And honestly? We still can't quite believe it's real.

**Example absent:**
> We've experienced significant growth and now operate at unprecedented scale, serving customers around the globe.

## All three must be present in aggregate

A common authoring trap: nail one value, lose the others.

- **Kind alone:** comes across as soft / hedging / lacking stakes. Misses Daring.
- **Daring alone:** comes across as arrogant / aggressive / preachy. Misses Kind.
- **Deep alone:** comes across as cold / technical / detached. Misses Kind.

The three should be detectable in aggregate over a paragraph or short section. They don't need to be in EVERY SENTENCE — that would be exhausting.

## Diagnostic: "does this aggregate the three?"

Read a paragraph, then ask:
1. Could I underline a phrase showing Kindness?
2. Could I underline a phrase showing Daring?
3. Could I underline a phrase showing Depth?

If yes to all three: the paragraph aggregates correctly.

If one is missing: rewrite. Most common gap is Kind (especially in Provoke-mode paragraphs).

## In practice: paragraph rewrite example

**Original (Daring + Deep, no Kind):**
> Cloud-first doesn't mean cloud-only. Most enterprises have a hybrid reality they refuse to acknowledge. The honest path is to make hybrid a feature, not a confession.

This is sharp and grounded. But it's pointing fingers. Where's the warmth toward the audience?

**Rewrite (Daring + Deep + Kind):**
> Cloud-first doesn't mean cloud-only. Half the customers we meet have a hybrid reality they can't talk about because someone in their org declared cloud-first three years ago. Our job is to make hybrid a feature, not a confession.

The "we meet" and "our job" pull the writer alongside the reader. Still daring. Still deep. Now also kind.

## In practice: failure mode — Provoke without Kind

**Provoke unintended-arrogance:**
> Other vendors claim "enterprise AI" but their solutions are fragmented, expensive, and lack the deep integration real enterprises need. They sell duct tape and call it architecture.

This is Provoke (P2 Skewer attempt) without Kind. It punches DOWN at competitors. It also implicitly says the reader was foolish to consider them. Violation.

**Rewrite — keep Provoke, add Kind:**
> "Enterprise-grade AI" gets used a lot. Most of the time it means a bundle of features that almost-but-not-quite hold together. We've watched this play out — and we've made our own mistakes along the way. The bar we've set for ourselves is integration that earns its name, not labels it.

Now Provoke (skewers the term "enterprise-grade") is paired with Kind (acknowledges shared experience including OUR mistakes).

## Anti-pattern: forced Kind

Conversely, don't overcorrect by stuffing Kind everywhere:

**Overcorrected:**
> We deeply value your time and want to express our heartfelt gratitude for your continued partnership.

This is performative. Real Kind is observed in behavior + word choice, not announced in adjectives.

## See also

- [OurVoice.md](OurVoice.md) — voice framework summary
- [OurVoice-examples.md](OurVoice-examples.md) — per-technique examples
- [OurVoice-corpus.md](OurVoice-corpus.md) — calibration anchor
- `TrailblazerVoiceCritic` agent — per-paragraph rubric application includes the three-value check
