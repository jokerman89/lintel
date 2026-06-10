# Todo — v4.11: launch-polish remainder + cycle-discipline backlog

**Initiative:** Operator-approved 2026-06-10 ("Both, punch-list first"). Close what actually remains
of the State-of-the-Harness §18 punch-list (most was already closed by the launch-readiness work),
then roll into the parked cycle-discipline backlog from the 2026-06-09 audit without re-asking.

**Mode:** `meta-infra` (touches test runner semantics, removes a skill, edits phase-skill spine).
Gates M1–M4 active.

**Verified state on main @ 98999ba (re-checked, audit claims were stale):**
- ✅ already closed upstream: getting-started.md neutral · @microsoft.com purged + tripwire scans
  README/SECURITY · manifests de-branded · 8 customer agents tracked · li-forge-stats honestly
  labeled "(planned — not yet shipped)" in all 3 concept docs.
- ❌ still open: hollow e2e (empty dir, CI job vacuously green) · context-budgetwatch residual skill ·
  hooks/shared/README.md says "29 hooks: 27 warn-only" (real: 30 dirs) · scale-estimator.sh comment
  lag · "8-phase" branding vs the P2-A standard "9-step (8 core + SCOPE)" in CLAUDE.md/README/
  AGENT-INSTRUCTIONS · orphaned hooks/entropy-secret-check.sh (P1-7) · P1-8 broken links (verify count).

## Phase A — launch polish (PR 1, branch feat/v4.11-launch-polish)

- [x] A1a `tests/runner/run-all.sh`: any scope that discovers ZERO tests exits 1 (fail-closed) —
      simplest rule, covers explicit scopes and a hypothetically empty tree alike. Verified rc=1.
- [x] A1b `tests/e2e/harness-critical-path.sh` (tagged `claude-code-only`): sandbox install.sh →
      pack-resolver REAL parse (asserts `voice.enforce`, outside the hardcoded fallback list) →
      footer from fixture state. 7 assertions green; tag-filtered run green.
- [x] A2 `skills/context-budgetwatch/` removed; alias in `config/aliases.yaml` (grace to 2026-09-10,
      `match`→`skill-router` pattern); verify.sh probe dropped; context-budget/HOOK.md/
      CONTEXT-ENGINE.md updated; M1 entry `2026-06-10-v4.11-launch-polish.md`. Shape suite green.
- [x] A3 Doc sweep: hooks README "29/27" → real tally (30: 23 warn + 2 block + 2 surface +
      2 lifecycle + 1 inject) · scale-estimator comment un-lagged (tree L/XL shipped) · 8 broken
      links fixed (CHANGELOG×5, v2-design×2, v3-plan×1; audit's "10" was stale) · "8-phase" →
      "9-step (8 core + SCOPE)" across README/CLAUDE/AGENTS/GEMINI/AGENT-INSTRUCTIONS/SHIP-GATE/
      getting-started/engineering-modules/CLAUDE.md.template (historical design docs left as-is) ·
      README count 169 → 168 skills.
- [ ] A4 M2 compat audit + M3 full suite green → push → PR 1.

## Phase B — cycle discipline (PR 2)

- [ ] B1 Convergent #5: BUILD two-stage review fails CLOSED on a no-op tree (no diff → review
      verdict cannot be SHIP). skills/build/SKILL.md + shape test.
- [ ] B2 Convergent #2: `/li:lessons-surface` mandatory+automatic at SENSE (written-but-never-read
      loop closed). skills/sense/SKILL.md + shape test.
- [ ] B3 Small P1s: remove orphaned `hooks/entropy-secret-check.sh` (M1) · P1-1 frontmatter-contract
      drift in CLAUDE.md · P1-6 stale five-lens checklist reconcile (verify still stale first).
- [ ] B4 M2 + M3 green → push → PR 2.

## Phase C — consistency gate (PR 3, own ADR)

- [ ] C1 Convergent #6: `/analyze`-style DEFINE↔PLAN↔BUILD consistency gate (spec-kit's biggest
      steal). Design first: ADR + where it hooks (pre-BUILD gate vs standalone skill). Largest item;
      design doc → implement → shape test.

## Parked (explicitly not this initiative)
- context-* naming drift + the two divergent review-rubric families (§17) — deliberate design calls,
  operator hasn't decided.
- P1-2 cli_support 131-flat/38-structured split — meta-infra contract change, needs its own design.
- Remaining ~25 official skills adopting the cycle footer — incremental adoption.

## Review
_(to be filled at task end)_
