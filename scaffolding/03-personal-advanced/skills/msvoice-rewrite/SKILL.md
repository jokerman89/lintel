---
name: jstack-msvoice-rewrite
description: Rewrite internal-voice content into Microsoft Our Voice (Trailblazer) — 12-cell aware.
color: orange
tools: Read, Write, Edit, Bash
voice: trailblazer
cli_support: [claude-code, codex]
license_note: requires T0 corpus + calibration (TRAILBLAZER-CORPUS.md, TRAILBLAZER-CALIBRATION.md)
---

# /msvoice-rewrite

Takes internal-voice prose and rewrites it in Microsoft Our Voice (Trailblazer). Each rewritten paragraph is mode-tagged (Reveal / Inspire / Provoke) with a specific technique cell (one of 12).

Output is DRAFT by definition — requires `/customer-voice-check` before distribution.

T0 calibration must be complete for the rewrite to be trusted. Pre-calibration: skill produces output but surfaces UNCALIBRATED stamp; downstream gates refuse to land it.

## When to use

- Engineer drafted a release note in internal voice; needs a customer-facing version
- Internal pitch slide needs a customer-bearing rewrite
- Onboarding email to a customer drafted internally needs voice-treatment
- Customer-guide section from `/document-generate --target customer-guide --voice internal` needs trailblazer pass

## When NOT to use

- Already in trailblazer voice — skip
- Engineering-internal doc — no rewrite needed
- Content is too short to mode-tag (one-line tweet, button copy) — handwrite
- T0 not calibrated — rewrite produces unverified output; calibrate first

## Inputs

- Required `--input <path>` — internal-voice source
- Optional `--target-modes <list>` — restrict rewrite to specific modes (e.g. `reveal,inspire`)
- Optional `--target-cells <list>` — restrict to specific cell numbers (e.g. `R1,R3,I1,P3`)
- Optional `--preserve <pattern>` — paragraphs matching pattern stay verbatim (e.g. code blocks, legal text)
- Optional `--out <path>` — output path (default: `<input>-trailblazer.md`)

## Workflow

1. **Preflight.** TRAILBLAZER-CORPUS.md must exist; TRAILBLAZER-CALIBRATION.md ≥90%/cell × ≥10 cells for trusted output. Surface UNCALIBRATED stamp if not.
2. **Parse input.** Split into paragraphs. Mark code blocks, tables, YAML as PRESERVE.
3. **Per-paragraph plan.** For each non-PRESERVE paragraph: identify the topic + the right mode/cell for that topic. Heuristics:
   - Strong product claim → Reveal/Curtain or Reveal/Understatement
   - Feature catalog → Reveal/Dream
   - Brand assertion → Inspire/Marvel or Inspire/Opposites
   - Sacred-cow-challenging insight → Provoke/Skewer
   - Polarizing value statement → Provoke/All-or-nothing
   - Hard truth → Provoke/Unflinching
4. **Rewrite.** Apply the cell's technique. Honor:
   - Six ground rules (clarity, "we" not "Microsoft", concise, limit jargon, focus, perspective)
   - Three brand-value words (Kind + Daring + Deep — all present in aggregate)
   - AI-tell vocabulary blocklist (Tier 1 absolute, Tier 2 default-blocked, Tier 3 phrase-pattern trap)
   - CELA restrictions (no competitor disparagement, no Trailblazer-persona external reference)
5. **Annotate.** Each rewritten paragraph gets a cell tag in a margin comment (`<!-- cell: REVEAL/Curtain -->`).
6. **Compliance scan + self-check.** Run Tier 1 AI-tell scan on output. Run CELA pattern scan. Block on hit.
7. **Mark DRAFT.** Output frontmatter explicitly: `voice: trailblazer-draft`, `status: requires-customer-voice-check`.
8. **Write.** Atomic write to `--out`.
9. **Report.**

## Report format

```
MS Voice Rewrite: release-notes-internal.md → release-notes-trailblazer-DRAFT.md

Calibration: CALIBRATED (11 cells ≥90%)
Mode mix:
- Reveal: 6 paragraphs (3 Curtain, 2 Dream, 1 Understatement)
- Inspire: 3 paragraphs (2 Marvel, 1 Opposites)
- Provoke: 2 paragraphs (1 Skewer, 1 Exception)
- Preserved: 4 (code blocks + table)

## Voice self-check
✓ No Tier 1 AI-tell vocab
✓ No CELA-violating phrasing
✓ All three brand values present in aggregate
✓ Six ground rules check: clarity ✓ / we-not-MS ✓ / concise ✓ / jargon ✓ / focus ✓ / perspective ✓

## Status
DRAFT — requires /customer-voice-check before distribution.

## Cell distribution (chart)
R1 Understatement   ▌▌                  (1)
R3 Curtain          ▌▌▌▌▌▌              (3)
R4 Dream            ▌▌▌▌                (2)
I1 Opposites        ▌▌                  (1)
I3 Marvel           ▌▌▌▌                (2)
P2 Skewer           ▌▌                  (1)
P3 Exception        ▌▌                  (1)
```

## Compliance integration

- AI-tell vocab Tier 1 scan post-rewrite — BLOCKS write on hit.
- CELA pattern scan — competitor names, Trailblazer-persona external refs — BLOCKS.
- Output marked DRAFT, status `requires-customer-voice-check`. Downstream `/ship` refuses without that check.
- If `--input` had customer-data patterns: BLOCK before rewrite. Voice rewrite of customer-data is still customer-data.

## Voice tier note

`voice: trailblazer`. This skill is one of the few JStack skills that PRODUCES trailblazer-voice output. Its own report frontmatter is internal; the rewritten artifact is trailblazer-draft.

## Failure modes

- **Corpus missing / uncalibrated:** UNCALIBRATED stamp + still produce output. Downstream gates will refuse. Operator can override only with explicit reason logged.
- **Paragraph too short to mode-tag (<20 words):** PRESERVE verbatim, flag in report.
- **All paragraphs would land in one mode:** suspect topic too narrow for full trailblazer treatment. Surface + ask.
- **Tier 1 AI-tell detected in rewritten output:** REGENERATE that paragraph (up to 2 attempts). If 3rd attempt still hits: fail closed, surface, refuse write.
- **CELA pattern hit:** STOP. No retry — operator must restate the source content to remove the pattern.

## Examples

**Standard rewrite:**
```
> /msvoice-rewrite --input release-notes-internal.md
[Rewrites 11 paragraphs, preserves 4 code blocks]
✓ release-notes-internal-trailblazer.md DRAFT generated.
  Next: /customer-voice-check before distribution.
```

**Restricted modes:**
```
> /msvoice-rewrite --input pitch.md --target-modes inspire,reveal
[Skips Provoke — no polarizing statements for this audience]
✓ pitch-trailblazer.md DRAFT (Inspire 60% / Reveal 40%).
```

**With preservation:**
```
> /msvoice-rewrite --input doc.md --preserve "^```" --preserve "^\| "
[Preserves code blocks and tables verbatim]
```

## See also

- TRAILBLAZER-CORPUS.md — calibration source
- `/customer-voice-check` — required gate AFTER this skill
- `/document-generate --voice trailblazer` — generate trailblazer directly (vs rewrite)
- `/ship` — reads downstream check verdict
