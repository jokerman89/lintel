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

## v5.0-claude-home — three stacked PRs OPEN 2026-06-12

**Status:** active — awaiting PR merges

**What shipped (one session, full cycle SENSE→CAPTURE):**
- **D1–D4 locked** by operator: knowledge committed/runtime ignored · everything Lintel-owned → `.claude/` · native auto-memory converged · 4 Obsidian patterns
- **PR #62** vault sink (rebased clean; neutral-pack default OFF after review)
- **PR #63** v5 `.claude/` home (ADR-0005): lib/paths.sh, scope-routed audit/jobs + cross-repo registry, li-migrate-claude-home, ~210-file sweep, dogfooded on this repo
- **PR #64** memory v2 (ADR-0006): lib/memory.sh + bin/_context.sh + memory-budget-warn hook, update-phase + supersede convention, context family 8→3 (aliases), AGENTS.md + rules emission, subtractions (operator-profile, gbrain over-claims)
- **PR #65** Obsidian patterns (ADR-0007): locked schema, sessions.base + li-vault-init, hub/predecessor wikilinks, 00-index
- All three phases passed independent L-007 review (SHIP-WITH-FIXES; every P1/P2 acted on)

**What's pending:**
- ALSO open: **PR #66** (activation pass, ADR-0008) — stacked on #65. Fit audit
  (docs/audit/2026-06-12-fable5-fit-audit.md) found ~3/14 mechanisms firing; #66 ships plugin
  hook auto-registration + state ledger (lib/state.sh) + behavior tests + the exit-2 fix for
  the block hooks (they never actually blocked). After merge: verify li-doctor proof-of-life
  on first fresh session (digest audit record must appear).
- Merge chain: #62 → #63 (re-target to main) → #64 → #65
- Operator: run `li-migrate-claude-home` on other Lintel-connected repos (grace to 2026-09-12)
- Operator: re-enable vault sink in a personal pack override (~/.lintel/packs/_default) — the shipped neutral default is now OFF
- Follow-ups parked: marker-parse consolidation (5 copies → paths.sh), basic-memory-style index if grep ever scales out

**Last touched:** 2026-06-12

---

## v4.0-reframe — design doc DRAFT_FOR_REVIEW 2026-05-29

**Status:** design phase — awaiting operator pass

**Scope:** Master design consolidating 3 operator-supplied FRs + 1 text-form engineering-depth request + 1 meta-process note into 5-chapter reframe of what Lintel IS. Becomes v4.0.

**5 chapters in one architecture:**
1. **Spine + Packs + Navigation** — generic spine, pack-loaded identity, mandatory navigation declarations, orientator at SENSE (honors `lintel-feature-spine-packs-navigation.md`)
2. **Brief Forge + Envelope + Wiki** — universal hand-off gate, standardized payload, generated 1:1 documentation (honors `lintel-feature-brief-forge.md`)
3. **Engineering Depth** — 5 domain modules (tech-architecture · data-architecture · security-compliance · devops-hosting · testing-qa) with full/loop/single granularities, per-module checkpoints + recovery + iteration loops (NEW — interprets operator text-form FR)
4. **Meta-infra Discipline** — `meta-infra` mode envelope + 4 mandatory gates (structure-impact, compatibility-audit, regression-shape-tests, future-operator validation) for harness-on-harness work (NEW — interprets operator meta-process note)
5. **Composition** — ship sequencing, cross-chapter deps, risks, operator validation criteria

**Estimates:** ~17-27 CC-days for v4.0 ship (alpha/beta/rc), ~10-15 CC-days for engineering-depth rollout (v4.1-4.5).

**Open decisions:** 14 numbered (C1-D1 through C5-D2). All recommendations included; operator confirms or vetoes per-line.

**Files:**
- `docs/design/lintel-v4.0-reframe-design.md` (master doc)
- `docs/feature-requests/lintel-feature-spine-packs-navigation.md` (canonical reference)
- `docs/feature-requests/lintel-feature-brief-forge.md` (canonical reference)

**Last touched:** 2026-05-29

---

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

### PR #7 (lintel-v3.5-doc-generation-plan) — ALL 4 MAJORs RESOLVED (2026-05-29 sweep)

1. ~~**Voice-gate terminology mismatch**~~ ✅ CLOSED. Audit confirmed generate-* family uses `/li:rais-customer-voice-check` consistently (no `TrailblazerVoiceCritic` references in skills/). Terminology unified — design doc had stale name.
2. ~~**4-gate explicit home**~~ ✅ CLOSED. `skills/generate/agent-mapping.yaml` has `voice_gate_owner: orchestrator` + `format_gate_owner: format-builder` explicit. Validated at v3.5 Fas 2 merge (PR #17).
3. ~~**`--keep-runs <N>` YAGNI**~~ ✅ CLOSED. Documented as YAGNI in `skills/generate/SKILL.md` "Deferred flags" section. Operator can request implementation when run-dir size becomes friction.
4. ~~**Voice-blocklist-customer-share-gate interaction**~~ ✅ CLOSED. Full interaction chain documented in `skills/generate/SKILL.md` "Voice-blocklist ↔ customer-share-gate interaction" section: --customer-share → voice-tier=trailblazer-draft → blocklist enforced via OurVoice corpus → rais-customer-voice-check verifies + compliance-gate aggregates.

### PR #9 (lintel-v3.6-backlog-sequencing) — 7 of 7 concerns RESOLVED (2026-05-29 sweep)

MAJORs (#1, #2): coverage matrix shipped inline; 4.1 alias-mekanism CLOSED via PR #14 (design) + PR #27 (implementation 2026-05-29).

MINORs (#3-#7): all CLOSED via cohort-execution paths:
- ~~#3 5.6 distribution targets~~ enumerated at Cohort 1 PR-open (truth-fixes + 6.3+6.4+6.6 went there)
- ~~#4 6.3 resume integrity spec~~ implemented in Cohort 1 PR #10 (resume Step 1.5)
- ~~#5 6.6 shellcheck estimate~~ shipped warn-only in Cohort 1 (PR #10) per recommendation
- ~~#6 L-002 grep-evidence for 4.3~~ context-family pair-by-pair verified in PR #27 WS-4a section (33 collisions enumerated)
- ~~#7 M-3 LAYERS.md pre-baking~~ link-not-content approach used: LAYERS.md got L-001/L-002/L-003 (Cohort 1) + L-004 (v3.7 closeout) as durable principles with reference to lessons.md for incident-driven rationale

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
2. ~~**6.7 internal-voice consistency check** (D-5a)~~ ✅ INVESTIGATED 2026-05-29 — verdict: INTENDED, not drift. 125 internal / 14 mixed / 2 trailblazer distribution coherent. See [decisions-67-68 doc](docs/design/lintel-v3.6-decisions-67-68.md). Operator vetoes by reply "drift" if disagree.
3. ~~**6.8 3-role validation** (D-5b)~~ ✅ INVESTIGATED 2026-05-29 — verdict: PATTERN VALIDATED. 3 role files structurally consistent (7/7 sections, 78-81 lines). Ready for role #4 — recommended `frontend-designer` to anchor v3.7 family. Operator vetoes by reply "not yet" or "go with X".
4. **T0 voice corpus calibration** ($1.80-6 × 3-5 rundor)
5. **Real-work `/li:cycle` dogfood** på faktisk Azure-engagement — synthetic pre-validation done 2026-05-29 (4 validations passed, 3 soft-findings logged). See [docs/design/lintel-v3.7-fas-d-dogfood-protocol.md](../docs/design/lintel-v3.7-fas-d-dogfood-protocol.md) for the 7-step operator checklist (15-30 min). Reduces operator-effort from multi-hour evaluation to focused validation.
6. **Marketplace submission** (post MS legal review)
7. **PR #14 merge** efter WS-4a/b + alias-implementation

**Last touched:** 2026-05-29
