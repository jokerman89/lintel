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

## v3.8-jobs-and-planner — Curated-flow tracking + planner-as-module SHIPPED 2026-05-29

**Status:** ready for merge (PR open)

**What shipped:**
- **Feature 1 (jobs system):** ~/.lintel/jobs/_active.md as single source of truth. 3 hooks (job-begin, job-end, job-stale-warn). 2 skills (`/li:jobs`, `/li:status`). `workflow_root: true` frontmatter flag on cycle + plan. Helper bin/_jobs.sh.
- **Feature 2.1:** plan declares workflow_root: true (spawns its own job when invoked standalone).
- **Feature 2.2:** prompt.md generation moved from CAPTURE to PLAN. Trio (plan.md + spec.md + prompt.md) born together. CAPTURE now reaffirms (annotates with build evidence), doesn't regenerate.
- **Feature 2.3:** granularity hard check in plan-eng-review Step 0 — per-task ≤5min (operator-LOCKED). Tasks >5min trigger decompose-or-accept AskUserQuestion.
- **Feature 2.4:** plan/SKILL.md documents Module-callable section. Three invocation modes documented (inside cycle, standalone, sub-module called by another workflow_root skill). --no-job flag for nested calls.

**Concept docs:** docs/concepts/jobs-system.md + docs/concepts/planner-as-module.md.

**Tests:** tests/unit/jobs-system-present.sh + tests/unit/workflow-root-and-trio.sh. 20/20 PASS local. Behavior smoke: job_create → job_update → job_archive end-to-end verified with audit-log writes.

**Last touched:** 2026-05-29

---

## v3.7-close — Frontend-design family COMPLETE

**Status:** completed

**What's pending:**
- ~~Fas A1: foundation core~~ ✅ SHIPPED (PR #22)
- ~~Fas A2: extension + canonical pattern~~ ✅ SHIPPED (PR #23)
- ~~Fas B: generate-web --from-frontend-design + new generate-app skill (M-2)~~ ✅ SHIPPED (PR #24)
- ~~Fas C: frontend-design-surface hook + vault loop closure~~ ✅ SHIPPED (PR #25)
- v3.7.0-dev tag ✅ pushed 2026-05-29
- **Fas D** (operator-only) — real-engagement dogfood + L-004 canonical-pattern re-evaluation pending

**Stats:** 9 net-new skills + 5 new agents (78→83) + 1 hook + canonical pattern + L-004 lesson durable. M-1/M-2/M-3/M-4/M-5/M-6 + m-1/m-3 all resolved. 17/17 tests pass.

**Last touched:** 2026-05-29 (v3.7.0-dev milestone)

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

### PR #21 (lintel-v3.7-frontend-design-system) — 7 of 9 concerns RESOLVED via implementation

Eng-review run 2026-05-28. v3.7 Fas A1+A2+B+C shipped i PR #22-#25, all merged 2026-05-29. Status update för 9 concerns:

**MAJORs — alla 6 RESOLVED:**
1. ~~M-1 design-spec.json schema collision~~ ✅ RESOLVED i PR #21 (filename → `frontend-design-spec.json`) + PR #24 (generate-web reader)
2. ~~M-2 frontend-app-scaffold boundary violation~~ ✅ RESOLVED i PR #21 (renamed till generate-app) + PR #24 (skill shipped i generate-* family)
3. ~~M-3 Fas A monolithic-PR risk~~ ✅ RESOLVED i PR #21 (split till A1 + A2)
4. ~~M-4 sequential sub-skill chain 3× latency~~ ✅ RESOLVED i PR #22 (orchestrator Workflow Step 2-4 parallel-dispatch documented)
5. ~~M-5 schema-versioning missing~~ ✅ RESOLVED i PR #22/#23 (`schema_version: 1` på alla contract JSON)
6. ~~M-6 roundtrip integration test deferred~~ ✅ RESOLVED i PR #22 (`tests/integration/frontend-design-roundtrip.sh`)

**MINORs — 2 of 3 RESOLVED, 1 deferred:**
7. ~~m-1 FrontendArchitect ↔ FrontendBuilder non-overlap~~ ✅ RESOLVED i PR #22 (explicit non-overlap section)
8. **m-2 SKILL.md DRY pattern** — ⏳ DEFERRED. 9 frontend-* + generate-* skills now exist; pattern-anatomy doc not yet authored. Low-priority — drift signal-to-noise är låg så länge antalet är manageable. Address when next family adds.
9. ~~m-3 --overwrite flag inheritance~~ ✅ RESOLVED i PR #23 (frontend-style-extract documents flag)

**Additional concern surfaced post-shipment (#7 perf-budget):** vault-lookup latency budget documented i PR #25 frontend-design-surface hook (<200ms MVP target for vault of 1-3 patterns, scaling-index deferred till vault > 10).

**Status:** PR #21 reviewer-concerns 7-of-9 closed via implementation. Remaining m-2 carries over till next family-design occasion. Entry can close after m-2 addressed or operator dismisses som YAGNI.

**Last touched:** 2026-05-29 (v3.7.0-dev milestone)

---

## operator-only-remaining — Items som kräver operator beyond AI-execution

**Status:** active

**What's pending:**

1. ~~**WS-4a + WS-4b naming-sessions**~~ ✅ AUTO-EXECUTED with operator-veto path 2026-05-29. WS-4a: NO renames (prefix-only disambiguation principle adopted). WS-4b: 4 renames (match→skill-router, setup-brain→gbrain-setup, sync-brain→gbrain-sync, agt-tier-stamp→agent-tier-stamp). Alias-mekanism + bin/_aliases.sh + tests shipped. Operator vetoes any line if disagreement.
2. **6.7 internal-voice consistency check** decision (D-5a: intended gap or drift?)
3. **6.8 3-role validation** before more role-tooling (D-5b)
4. **T0 voice corpus calibration** ($1.80-6 × 3-5 rundor)
5. **Real-work `/li:cycle` dogfood** på faktisk Azure-engagement
6. **Marketplace submission** (post MS legal review)
7. **PR #14 merge** efter WS-4a/b + alias-implementation

**Last touched:** 2026-05-28
