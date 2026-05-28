# Memory — Lintel working-state

Cross-session working state (ej durable rules — that's [[lessons.md]]; ej persona-frames — that's
[[personas.md]]). Surface at session-start so operatorn ser var arbetet pausade.

> Format per entry: short title, then `Status:`, then `What's pending:`. Update at session-end
> or at major checkpoints. Stale entries (>30 days) bör städas.

---

<!--
## entry-id — short title

**Status:** active / paused / blocked / completed

**What's pending:**
- <pending item 1>
- <pending item 2>

**Last touched:** YYYY-MM-DD
-->

## v3.5-close — Generate-pipeline COMPLETE

**Status:** completed

**What's pending:**
- ~~Fas 2: --from-pipeline support~~ ✅ SHIPPED (PR #17)
- ~~Fas 3: generate-style-learn skill~~ ✅ SHIPPED (PR #19)
- v3.6.0-dev + v3.6.1-dev tags pushed (signal milestone instead of v3.5.0-dev)

**Last touched:** 2026-05-28 (v3.5 doc-gen-pipeline COMPLETE)

---

## v3.6-cohorts — Backlog execution NEARLY COMPLETE

**Status:** active (Cohort 4 operator-only kvar)

**What's pending:**
- ~~Cohort 1 (truth-fixes + frontmatter-lint + resume-integrity + shellcheck)~~ ✅ MERGED PR #10
- ~~Cohort 2 (observation spine + behavior-test pilot)~~ ✅ MERGED PR #11
- ~~Cohort 3 (design locks per default-recs)~~ ✅ MERGED PR #16
- ~~Cohort 5-partial (operator requests + second wave)~~ ✅ MERGED PR #13
- ~~Cohort 5-expansion (profile-switch + maintenance + entropy)~~ ✅ MERGED PR #18
- ~~Cohort 6 (instruction-parity-check)~~ ✅ MERGED PR #19
- **Cohort 4a (alias-mekanism design pass)** — PR #14 OPEN (intentional, väntar WS-4a/b)
- **Cohort 4 implementation** — depends på operator working-sessions WS-4a (gstack-collisions) + WS-4b (orphan-names)

**Last touched:** 2026-05-28 (~95% v3.6 backlog completed)

---

## reviewer-concerns — Open från tidigare PRs (M-1 tracking per v3.6 backlog)

**Status:** active

**What's pending:**

### PR #7 (lintel-v3.5-doc-generation-plan) — 4 MAJORs öppna

1. **Voice-gate terminology mismatch** — designdoc nämner `TrailblazerVoiceCritic`, befintliga `/li:generate-*` använder `/li:rais-customer-voice-check` + "T0 CALIBRATED". `orchestrator-level voice-gate` landed med `/li:rais-customer-voice-check`-reference i Fas 1 PR #8. Adresseras: konsekvent terminologi vid Fas 2 dogfood.
2. **4-gate explicit home** — `voice_gate_owner: orchestrator` + `format_gate_owner: format-builder` i `skills/generate/agent-mapping.yaml` IS the spec. Validate vid Fas 2 dogfood.
3. **`--keep-runs <N>` YAGNI** — flag specced men inte implementerat. Defer om operator dogfood visar behov.
4. **Voice-blocklist-customer-share-gate** — interaction not explicitly specced. Falls under "address at invocation per L-001".

### PR #9 (lintel-v3.6-backlog-sequencing) — 7 concerns captured

Resterande 7 minor concerns i designdocets Reviewer Concerns-sektion. 4 MAJORs adresserade inline under cohort-execution. Minor concerns adresseras vid respective cohort-execution-time eller följdiget design-iteration.

**Tracking pattern:** open reviewer concerns lever här tills addressat ELLER PR om reviewer-concern-resolution öppnas. Entry kan slutas när alla 4+7=11 resolved.

**Last touched:** 2026-05-28 (v3.6.1-dev milestone)

---

## operator-only-remaining — Items som kräver operator beyond AI-execution

**Status:** active

**What's pending:**

1. **WS-4a + WS-4b naming-sessions** (2-3h operator) → unlocks Cohort 4 implementation + PR #14 alias-mekanism implementation
2. **6.7 internal-voice consistency check** decision (D-5a: intended gap or drift?)
3. **6.8 3-role validation** before more role-tooling (D-5b)
4. **T0 voice corpus calibration** ($1.80-6 × 3-5 rundor)
5. **Real-work `/li:cycle` dogfood** på faktisk Azure-engagement
6. **Marketplace submission** (post MS legal review)
7. **PR #14 merge** efter WS-4a/b + alias-implementation

**Last touched:** 2026-05-28
