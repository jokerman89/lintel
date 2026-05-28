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

## v3.5-close — Generate-pipeline Fas 2/3 + tag

**Status:** active

**What's pending:**
- Fas 2: refactor av legacy `generate-ppt/web/word` att stödja `--from-pipeline <dir>`-flag
- Fas 3: `generate-style-learn` skill (deferred)
- v3.5.0-dev tag efter Fas 2 dogfoodat

**Last touched:** 2026-05-28

---

## v3.6-cohorts — Backlog execution

**Status:** active (Cohort 1 in-flight)

**What's pending:**
- Cohort 1 (truth-fixes + frontmatter-lint + resume-integrity + shellcheck) — i PR-form
- Cohort 2 (observation spine + behavior-test pilot)
- Cohort 3 (design locks per default-recs)
- Cohort 5-partial (operator requests + second wave)
- Cohort 4a (alias-mekanism design pass)

**Last touched:** 2026-05-28

---

## reviewer-concerns — Open från tidigare PRs

**Status:** active

**What's pending:**
- PR #7 design doc reviewer concerns (4 öppna MAJORs — voice-gate terminology, 4-gate-home, --keep-runs YAGNI, voice-blocklist-customer-share-gate)
- PR #9 design doc reviewer concerns (7 captured) — adresseras under cohort-execution

**Last touched:** 2026-05-28
