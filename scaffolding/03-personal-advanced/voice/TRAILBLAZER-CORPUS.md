# Trailblazer voice eval corpus

Sanitized customer-engagement paragraphs labeled per cell. Used to calibrate `TRAILBLAZER-TEST.md`.

**Sanitization rules** (load-bearing, no exceptions):

1. Real customer names → placeholders (`Acme Corp`, `Bravo Industries`, `Customer A`)
2. Real project names → placeholders (`Project Falcon`, `Initiative Beta`)
3. Real internal MS employee names → placeholders (`SE engineer`, `Field CTO`, `Account team`)
4. Real numeric data points (revenue, deal size, employee count) → rounded category (`mid-market customer`, `Fortune 500`, `5-15 employee team`)
5. Real product code names → placeholders (`<MS-product>`, `<Azure-service>`)
6. Real geo locations beyond country level → category (`Nordic region`, `EU public sector`, `Asia-Pacific manufacturing`)

If a paragraph cannot be sanitized while preserving the voice signal, **drop it** — pick another. Do not commit un-sanitizable content to this file.

---

## Corpus structure

48 numbered slots: 12 cells × 4 paragraphs each (2 known-good + 2 known-bad). The design doc target is 30 paragraphs minimum; this template carries 48 slots so the operator can over-collect and prune.

Operator fills slots iteratively. Each entry has:

```yaml
- id: PARAGRAPH-NNN
  cell: <MODE>/<TECHNIQUE>
  verdict_label: known-good | known-bad
  source: <one-line anonymized source description, e.g. "email to mid-market customer about Azure migration timeline">
  rationale: <one-line why this is known-good or known-bad for this cell>
  text: |
    <sanitized paragraph text>
```

---

## Reveal cells (4 cells × 4 slots = 16 paragraphs)

### Cell R1: REVEAL / Understatement of the century

#### Known-good
```yaml
- id: PARAGRAPH-001
  cell: REVEAL/Understatement
  verdict_label: known-good
  source: TODO
  rationale: TODO
  text: |
    TODO

- id: PARAGRAPH-002
  cell: REVEAL/Understatement
  verdict_label: known-good
  source: TODO
  rationale: TODO
  text: |
    TODO
```

#### Known-bad
```yaml
- id: PARAGRAPH-003
  cell: REVEAL/Understatement
  verdict_label: known-bad
  source: TODO
  rationale: TODO  # e.g. "overstates the problem instead of finding the smallest indisputable truth"
  text: |
    TODO

- id: PARAGRAPH-004
  cell: REVEAL/Understatement
  verdict_label: known-bad
  source: TODO
  rationale: TODO
  text: |
    TODO
```

### Cell R2: REVEAL / Leave the question unanswered
(4 slots, 2 known-good + 2 known-bad — same template)

### Cell R3: REVEAL / Draw back the curtain
(4 slots)

### Cell R4: REVEAL / Dream high
(4 slots)

---

## Inspire cells (3 cells × 4 slots = 12 paragraphs)

### Cell I1: INSPIRE / Make opposites attractive
(4 slots)

### Cell I2: INSPIRE / Make our language spectacular
(4 slots)

### Cell I3: INSPIRE / Marvel at simple truth
(4 slots)

---

## Provoke cells (5 cells × 4 slots = 20 paragraphs)

### Cell P1: PROVOKE / Skewer the sacred
(4 slots)

### Cell P2: PROVOKE / Make it an exception that rules
(4 slots)

### Cell P3: PROVOKE / Make it all or nothing
(4 slots)

### Cell P4: PROVOKE / Make it unflinching
(4 slots)

### Cell P5: PROVOKE / Make vulnerability a strength
(4 slots)

---

## Operator workflow

1. **Gather raw paragraphs** (operator-local, NOT this file). Recent CAIP-SE customer emails, decks, demo scripts, internal wiki contributions. Aim for ~60 raw paragraphs across 12 cells.

2. **Label each raw paragraph** by mode + technique cell + verdict (known-good / known-bad). For paragraphs that don't fit any cell cleanly, skip — they're not useful for eval.

3. **Sanitize per the rules above.** If a paragraph can't be sanitized while preserving voice signal, drop it.

4. **Land sanitized paragraphs in this file** at the appropriate cell + verdict slot. Replace TODOs.

5. **Run TRAILBLAZER-TEST.md against each paragraph.** Compare eval verdict to your verdict_label.

6. **Record results in TRAILBLAZER-CALIBRATION.md.** Per-cell accuracy.

7. **Iterate** the TEST prompt OR drop cells from v1 scope until ≥90% accuracy on known-good AND ≥90% on known-bad per cell.

**Estimated operator time:** 4-8 hours for the full 48-slot corpus + 2-3 hours for calibration iteration = 6-11 hours total over ~7 days.

**Minimum viable v1 corpus:** ≥2 known-good + ≥2 known-bad per cell × 12 cells = 48 paragraphs. The design doc said 30 — that floor still ships v1 if the operator covers all 12 cells with at least 1 of each verdict (24 paragraphs) plus 6 cells doubled (30 total). But the calibration is stronger with 4 per cell.

---

## Privacy + compliance notes

- This file lives in-repo. It WILL be reviewed by anyone with repo access (CAIP SE team + future contributors).
- Every paragraph here has been sanitized per the rules above. NO real customer names, project names, or identifiable engagement specifics.
- If you ever spot a paragraph in this file that wasn't fully sanitized: open an issue + delete the paragraph immediately. Re-collect from sanitized source.
- This file does NOT count as "customer data in the repo" per Premise: the content has been transformed to preserve voice signal while removing customer-identifying data.
