# T0 Calibration Workflow

Operator-driven workflow for moving the Trailblazer (Our Voice) corpus from POPULATED → CALIBRATED. Required gate for v2.0 customer-bound doc-gen output.

Phase D of v2 build. NOTE: Calibration requires actual LLM-eval calls — this is operator-driven, not automated in a single Claude session.

---

## Pre-flight smoke test (P2 fix T9 from eng-review)

Before committing to full calibration ordering, verify `/jstack-eval` actually produces parseable verdicts.

### Recipe

1. **Pick 2-3 paragraphs from `scaffolding/03-personal-advanced/voice/OurVoice-corpus.md`** — one known-good, one known-bad, one CAIP-SE-specific. Suggested test set:
   - `R1-GOOD-001` (Azure AI Search filing-cabinet)
   - `R1-BAD-001` (Revolutionary new platform)
   - `CAIP-GOOD-001` (Nordic public sector Arc migration)

2. **Invoke `/jstack-eval --cells R1,CAIP --paragraphs R1-GOOD-001,R1-BAD-001,CAIP-GOOD-001 --dry-run`**.

3. **Verify output:**
   - Each paragraph evaluated produces a YAML verdict block
   - Verdict contains all required fields: mode_attempted, technique_cell, kind/daring/deep scores, ground_rules_passed/violated, anti_ai_vocab_detected, verdict (PASS/FAIL)
   - Verdict matches the `verdict_label` field for ≥2 of the 3 test paragraphs (raw rubric accuracy at corpus-construction time)

4. **Log smoke result to `~/.jstack/audit/eval-smoke-<ts>.md`**:
   ```markdown
   # /jstack-eval smoke test — <timestamp>
   Test set: R1-GOOD-001, R1-BAD-001, CAIP-GOOD-001
   Output parseable: yes/no
   Verdict accuracy: 2/3 or 3/3
   Recommend Phase D ordering: as-planned / fix-eval-first
   ```

5. **Phase D ordering decision:**
   - 3/3 accurate or 2/3 with clear failure-mode → proceed with planned Phase D
   - <2/3 OR output unparseable → Phase D adds "fix eval skill" as task 0 BEFORE iteration begins

---

## Full calibration workflow

After smoke test passes, execute the full calibration. Estimated time: 2-4 hours operator + 30-60 min CC per eval round (typically 1-3 rounds needed).

### Round 1: First full eval

```
/jstack-eval --corpus scaffolding/03-personal-advanced/voice/OurVoice-corpus.md \
             --test scaffolding/03-personal-advanced/voice/OurVoice-test.md \
             --out scaffolding/03-personal-advanced/voice/OurVoice-calibration.md
```

Output: per-cell accuracy table + failure list for paragraphs where verdict ≠ verdict_label.

### Decision point per cell

After Round 1, for each cell:
- ≥90% known-good AND ≥90% known-bad → cell PASS
- One side <90% → review the failure paragraphs, decide:
  - Rubric tells need sharpening → iterate rubric in OurVoice-test.md, re-eval (Round 2)
  - Cell is genuinely difficult (R4 Dream, P1 Vulnerability are known) → consider dropping from v1 scope
- Both sides <90% → either iterate rubric OR drop cell

### Round 2-3: Iterate rubric

For each cell scoring <90%:
1. Read failure paragraphs + their YAML verdicts
2. Identify the rubric's misclassification pattern (e.g. "fails to detect P2 punching-down because Kind-score heuristic too lenient")
3. Edit `OurVoice-test.md` rubric for that cell — add explicit fail-mode tells, adjust scoring weights
4. Re-run eval scoped to changed cells: `/jstack-eval --cells <changed>`
5. Compare new accuracy to baseline

### Round N: Cell-drop decision

If cell persists below 90% after 3 rubric iterations:
- Operator decides to DROP from v1 scope OR push for full 12/12
- Drop is acceptable for the 2 known-difficult cells (R4 Dream, P1 Vulnerability)
- Document drop reason in OurVoice-calibration.md

### Landing CALIBRATED status

When ≥10 of 12 cells PASS at ≥90% per side:
1. Write CALIBRATED stamp to OurVoice-calibration.md frontmatter:
   ```yaml
   ---
   status: CALIBRATED
   calibrated_at: 2026-MM-DDTHH:MM:SSZ
   per_cell_accuracy:
     R1: {good: 0.92, bad: 0.91}
     R2: {good: 0.94, bad: 0.93}
     ... (etc)
   dropped_cells: []  # or [R4, P1] if dropped
   total_cells_pass: 10  # or 12
   ---
   ```
2. Downstream `/rais-customer-voice-check` reads CALIBRATED state. UNCALIBRATED stamp drops from all skills.
3. Phase F doc-gen can now produce customer-bound output that passes voice gate.

---

## Operator checklist

- [ ] Smoke test 3 paragraphs (Round 0)
- [ ] Confirm `/jstack-eval` produces parseable verdicts
- [ ] Run Round 1 full eval
- [ ] Review per-cell accuracy
- [ ] Iterate rubric for sub-90% cells (Rounds 2-3 as needed)
- [ ] Decide cell drops (max 2) if iteration plateaus
- [ ] Land CALIBRATED status in OurVoice-calibration.md
- [ ] Verify `/rais-customer-voice-check` reads CALIBRATED correctly
- [ ] Run one customer-voice-check on a known sample to confirm gate behavior

Estimated total: 6-12 hours operator work (heavily LLM-call-dependent).

---

## What can go wrong + mitigations

| Issue | Mitigation |
|-------|------------|
| Smoke test fails — output unparseable | Fix `/jstack-eval` skill before continuing. Likely YAML escape issue or rubric ambiguity. |
| LLM eval calls time out at scale (60 paragraphs) | Run in batches of 12-15 (per-cell). Each cell's eval is independent. |
| Rubric iteration produces oscillation (cell PASS → FAIL → PASS) | Operator stops iterating. Accept current state OR accept "best of last 3" verdict. |
| Costs spiral (eval = ~60 LLM calls × $0.03-0.10 = $1.80-6.00 per full round) | Use cheaper model for initial rounds (gpt-4o-mini vs gpt-4o). Promote to better model for final calibration. |
| CAIP-SE-specific cells consistently fail | Likely indicates need for more CAIP-specific corpus paragraphs. Operator adds 2-3 more per cell, re-runs eval. |

---

## Cross-references

- `OurVoice-corpus.md` — input corpus
- `OurVoice-test.md` — rubric being calibrated
- `OurVoice-calibration.md` — output state file
- `/jstack-eval` skill — eval orchestrator
- `/rais-customer-voice-check` — downstream consumer of CALIBRATED status
- `SHIP-GATE.md` Gate 3 — requires CALIBRATED status for v2.0.0 tag
