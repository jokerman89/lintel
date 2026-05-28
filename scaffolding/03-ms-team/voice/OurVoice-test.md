# Trailblazer voice eval prompt

This is the eval prompt for `/rais-customer-voice-check`. Run it against any customer-facing or official-communication paragraph (input) to get a structured verdict against Microsoft Our Voice guidelines.

The 12-cell grid this evaluates against:

| Mode | Technique cells |
|---|---|
| **Reveal** (4 cells) | Understatement of the century / Leave the question unanswered / Draw back the curtain / Dream high |
| **Inspire** (3 cells) | Make opposites attractive / Make our language spectacular / Marvel at simple truth |
| **Provoke** (5 cells) | Skewer the sacred / Make it an exception that rules / Make it all or nothing / Make it unflinching / Make vulnerability a strength |

Total: 4 + 3 + 5 = **12 cells**. (Earlier office-hours discussion said "15 cells (3 modes × 5 techniques)" — that was wrong. Reveal and Inspire don't share Provoke's 5 techniques; each mode has its own technique set. The corpus targets 12 cells.)

---

## The prompt

Pass the paragraph in question to the agent as `<input>`. Agent applies this rubric:

```
You are a Microsoft Our Voice evaluator. Score this paragraph against the Trailblazer voice attributes + 6 ground rules. Output structured verdict.

INPUT:
<paragraph>

EVALUATION:

1. Identify the mode the paragraph is attempting (choose one):
   - REVEAL (informing, in-the-know audience — body copy, instructions)
   - INSPIRE (exciting, empowered audience — headlines, social, key copy)
   - PROVOKE (challenging, challenged audience — statements, customer pushback)

2. For the identified mode, identify the technique being used (must be one of the mode's specific techniques):
   - Reveal techniques: Understatement of the century | Leave the question unanswered | Draw back the curtain | Dream high
   - Inspire techniques: Make opposites attractive | Make our language spectacular | Marvel at simple truth
   - Provoke techniques: Skewer the sacred | Make it an exception that rules | Make it all or nothing | Make it unflinching | Make vulnerability a strength

3. Score the three Trailblazer attributes on 1-5 scale:
   - KIND (warmth, human, compassion in language): 1 (cold/corporate) → 5 (warm + direct)
   - DARING (bold, energetic, unexpected — avoiding generic): 1 (generic) → 5 (unmistakable)
   - DEEP (perspective, depth, engaging — not surface-level): 1 (surface) → 5 (compounds meaning)

4. Check the 6 ground rules (PASS or VIOLATION each):
   - Clarity first (style doesn't obscure message)
   - "We"/"You" not "Microsoft"/"Customers" (direct, 1st/2nd person)
   - Concise (not 30 words when 5 would do)
   - Limited jargon (sounds human, not slide deck)
   - Single focus (one clear takeaway)
   - Has an opinion (humble but expert — not "it depends")

5. Check anti-AI vocabulary blacklist (count occurrences):
   delve, crucial, robust, comprehensive, nuanced, multifaceted, furthermore, moreover, additionally, pivotal, landscape, tapestry, underscore, foster, showcase, intricate, vibrant, fundamental, significant

VERDICT:
- PASS: All three attributes ≥3 AND no ground-rule violations AND zero anti-AI vocabulary
- FAIL: Any attribute <3 OR any ground-rule violation OR anti-AI vocabulary detected

OUTPUT FORMAT (structured, machine-readable):

```yaml
mode_attempted: <REVEAL|INSPIRE|PROVOKE>
technique: <one of the technique names above, or "none-clear" if mode used without a specific technique>
kind_score: <1-5>
daring_score: <1-5>
deep_score: <1-5>
ground_rules_passed: [<list of rule names that passed>]
ground_rules_violated: [<list of rule names with one-sentence reason each>]
anti_ai_vocab_detected: [<list of words found, empty if clean>]
verdict: <PASS|FAIL>
suggestion: <one-sentence fix if FAIL, omit if PASS — must reference the specific failed dimension>
```

CALIBRATION NOTES (for operator running corpus tests):
- A "known-good" paragraph should output verdict: PASS
- A "known-bad" paragraph should output verdict: FAIL
- If a known-good outputs FAIL or known-bad outputs PASS, the eval is miscalibrated for that cell
- Target: ≥90% accuracy on known-good AND ≥90% accuracy on known-bad per cell
```

---

## How to run

```bash
# After install + Phase 1: /rais-customer-voice-check skill runs this eval against any provided paragraph
# Before install (operator-manual calibration):
#   1. Copy the prompt above into a Claude conversation
#   2. Paste a corpus paragraph as <input>
#   3. Compare verdict against the corpus's labeled verdict
#   4. Record result in OurVoice-calibration.md
```

---

## Calibration acceptance criteria

The eval is calibrated and ready for v1.0.0 ship when:

- Each of the 12 cells has ≥2 known-good + ≥2 known-bad corpus entries
- Per-cell accuracy on known-good ≥90%
- Per-cell accuracy on known-bad ≥90%
- No anti-AI vocabulary false positives (the blacklist is precise, not pattern-matched against word fragments)

If a cell fails calibration after 3 iterations of prompt refinement:
- Option A: drop that cell from v1.0.0 scope (narrows Lintel's Trailblazer surface but ships)
- Option B: gather more corpus paragraphs for that cell (delays v1.0.0)

Operator decides per cell.
