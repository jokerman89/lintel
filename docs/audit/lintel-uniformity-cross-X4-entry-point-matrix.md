# Cross-cutting pass X4 — entry-point × cross-cutting-layer coverage matrix

**Pass:** X4 (entry-point coverage matrix)
**Date:** 2026-05-29
**Branch:** v4.0-phase1-meta-infra-spine (mid v4.0 reframe; Phase 1 of 3)
**Auditor:** uniformity auditor (X4 cross-cutting)
**Inputs:** audit prompt §X4 + all 8 cohort findings files. Extends Cohort 8's 8×6 consumption matrix and Cohort 5's hook-fire analysis across **every documented entry-point** and **every cross-cutting layer**.
**Motto:** kraftfullt från start, ständigt evolverande — NO-CUT. Every `should-fire-doesn't` is an uplift target, never a removal.

---

## Method and scope

**Rows (entry-points)** — every operator-reachable front door, verified by glob of `skills/`:
- 5 composites: `cycle`, `fix`, `research`, `plan-and-build`, `review-and-ship`
- 8 phase skills: `sense`, `define`, `discover`, `plan`, `build`, `review`, `ship`, `capture`
- Continuity / lifecycle: `resume`, `jobs`, `status`
- Role overlay entry: `role-activate` (representative of the 8-skill role lifecycle)
- Planner orchestrator: `autoplan` (representative of the planner sub-chain)
- DESIGNED-NOT-BUILT: `pack-*` lifecycle (8 skills — glob `skills/pack-*` returns nothing)

**Columns (cross-cutting layers)** — every layer a front door could consume:
1. **jobs** (BUILT v3.8 — `bin/_jobs.sh`, job-* hooks, `_active.md`)
2. **brief-forge** (DESIGNED-NOT-BUILT — `brief_forge_handoffs:` field, `pack.yaml:67`)
3. **knowledge / knowhow** (split: lessons.md BUILT + consumed unevenly; knowhow tag-funnel DESIGNED-NOT-BUILT)
4. **hooks** (BUILT — 19 hooks; pack-driving DESIGNED-NOT-BUILT)
5. **packs** (resolver `lib/pack-resolver.sh` BUILT-but-ZERO-CONSUMERS; pack-* skills DESIGNED-NOT-BUILT; WorkProfile branching BUILT in a few skills)
6. **voice** (BUILT — voice_tier gating + 3 trailblazer hooks)
7. **provenance** (BUILT-partial — `provenance-track`, fires at review/ship)
8. **audit-log** (BUILT — `bin/_audit.sh` unified writer, plus bespoke jsonl writers)

**Cell legend:**
- `fires` — layer is invoked / written / consumed by this entry-point in its body (verified).
- `skipped` — layer correctly does not apply to this entry-point (n/a-for-kind; NOT a finding).
- **`SHOULD`** — should-fire-doesn't: the layer is built (or designed-mandatory) and this entry-point should engage it but does not. **This is a finding.**
- `fires!?` — fires-shouldn't (over-fire). None found in this pass (noted in §Observations).
- `—` — not applicable because the layer is unbuilt **and** this entry-point is not a designed consumer of it.
- `DNB` — the entry-point ITSELF is designed-not-built (whole row hypothetical).

Designed-not-built columns are shaded by suffix: `SHOULD·dnb` = the entry-point is a designed consumer of a layer that is not built yet (the gap is "not built" not "built-but-unwired"); plain `SHOULD` = both layer and entry-point exist, so the gap is pure wiring.

---

## The matrix (15 built entry-points + 1 DNB row × 8 layers)

| entry-point | jobs | brief-forge | knowledge | hooks | packs | voice | provenance | audit-log |
|---|---|---|---|---|---|---|---|---|
| **cycle** (composite, workflow_root) | **fires**¹ | SHOULD·dnb | SHOULD² | **fires**³ | SHOULD⁴ | **fires**⁵ | skipped⁶ | **fires**⁷ |
| **fix** (composite) | SHOULD⁸ | SHOULD·dnb | fires⁹ | **fires**³ | SHOULD⁴ | skipped¹⁰ | skipped | SHOULD¹¹ |
| **research** (composite) | SHOULD⁸ | SHOULD·dnb | SHOULD¹² | **fires**³ | SHOULD⁴ | skipped¹⁰ | skipped | SHOULD¹¹ |
| **plan-and-build** (composite) | SHOULD⁸ | SHOULD·dnb | SHOULD¹² | **fires**³ | SHOULD⁴ | skipped¹⁰ | skipped | SHOULD¹¹ |
| **review-and-ship** (composite) | SHOULD⁸ | SHOULD·dnb | SHOULD¹² | **fires**³ | SHOULD⁴ | **fires**⁵ | **fires**¹³ | SHOULD¹¹ |
| **sense** (phase) | SHOULD¹⁴ | SHOULD·dnb | **fires**¹⁵ | **fires**³ | SHOULD¹⁶ | skipped¹⁰ | skipped | SHOULD¹⁷ |
| **define** (phase) | SHOULD¹⁴ | SHOULD·dnb | fires¹⁸ | **fires**³ | SHOULD¹⁶ | **fires**¹⁹ | skipped | fires²⁰ |
| **discover** (phase) | SHOULD¹⁴ | SHOULD·dnb | fires²¹ | **fires**³ | SHOULD¹⁶ | skipped¹⁰ | skipped | SHOULD¹⁷ |
| **plan** (phase, workflow_root) | **fires**²² | SHOULD·dnb | SHOULD²³ | **fires**³ | SHOULD¹⁶ | skipped¹⁰ | skipped | fires²⁰ |
| **build** (phase) | SHOULD¹⁴ | SHOULD·dnb | SHOULD²⁴ | **fires**³ | SHOULD¹⁶ | skipped¹⁰ | SHOULD²⁵ | fires²⁰ |
| **review** (phase) | SHOULD¹⁴ | SHOULD·dnb | SHOULD²⁶ | **fires**³ | **fires**²⁷ | **fires**¹⁹ | **fires**²⁸ | fires²⁰ |
| **ship** (phase) | SHOULD¹⁴ | SHOULD·dnb | SHOULD²⁶ | **fires**³ | **fires**²⁷ | **fires**¹⁹ | **fires**²⁹ | **fires**³⁰ |
| **capture** (phase) | SHOULD¹⁴ | SHOULD·dnb | **fires**³¹ (write-only) | **fires**³ | SHOULD¹⁶ | skipped¹⁰ | skipped | fires²⁰ |
| **resume** (continuity) | SHOULD³² | SHOULD·dnb | skipped³³ | **fires**³ | SHOULD¹⁶ | skipped¹⁰ | skipped | SHOULD¹⁷ |
| **jobs** (lifecycle controller) | **fires**³⁴ | skipped | skipped | **fires**³⁵ | SHOULD¹⁶ | skipped¹⁰ | skipped | **fires**³⁶ |
| **status** (read alias) | **fires**³⁷ | skipped | skipped | skipped | skipped | skipped | skipped | skipped³⁸ |
| **role-activate** (overlay) | skipped³⁹ | SHOULD·dnb⁴⁰ | SHOULD⁴¹ | **fires**³ | SHOULD⁴² | **fires**⁴³ | skipped | SHOULD⁴⁴ |
| **autoplan** (planner orch.) | SHOULD⁸ | SHOULD·dnb⁴⁵ | SHOULD⁴⁶ | **fires**³ | SHOULD⁴ | skipped¹⁰ | skipped | SHOULD⁴⁷ |
| **pack-*** (lifecycle) `DNB` | DNB | DNB | DNB | DNB | DNB | DNB | DNB | DNB |

---

## Footnotes (file:line evidence)

1. `skills/cycle/SKILL.md:4` declares `workflow_root: true`; `job-begin` hook (`hooks/shared/job-begin/run.sh:23`) spawns `~/.lintel/jobs/<id>/`. One of only two skills that fully participate in jobs (Cohort 8 fn5, Cohort 1 cycle record).
2. cycle delegates lessons-surface to SENSE (Cohort 1 cycle D10: "orchestrator doesn't surface lessons (delegates to SENSE)"). Knowhow tag-funnel unbuilt — but cycle is the orchestration point where unified knowledge surfacing would belong; `SHOULD` because lessons (built) are not orchestrated, only delegated, and knowhow has no consumer anywhere.
3. Hooks fire by event-matcher (PreToolUse/PostToolUse/SessionStart), not by skill invocation — so any entry-point that edits/commits/pushes triggers the relevant hook. `fires` here means "hooks are reachable from this entry-point's activity," which is universal. **But hook activation is opt-in via manual symlink** (`hooks/shared/README.md:7`) so a default install fires zero hooks — the `fires` is conditional on installation, a Cohort-5-wide caveat.
4. Composites set compliance/voice via mode-presets (Cohort 1: "cycle's mode-presets are proto-packs") but never call `lib/pack-resolver.sh` (Cohort 7: zero consumers). `SHOULD` — presets hardcode what packs should resolve.
5. cycle + review-and-ship reach SHIP/REVIEW which gate on `voice_tier` (Cohort 1 review/ship D7); voice machinery engages for customer-facing artifacts.
6. cycle orchestrates the phases that fire provenance (review/ship); it does not itself call `provenance-track` — correct delegation, `skipped` not `SHOULD`.
7. cycle writes `cycle-runs.jsonl` + `cycle-failures.jsonl` (Cohort 1 cycle D13) — observability present, but **bespoke writer, not via `bin/_audit.sh`** (Cohort 8 L6). Counted `fires` for "writes an audit trail" but flagged in §audit-fragmentation.
8. The 4 composites + autoplan lack `workflow_root` (Cohort 1: "no workflow_root despite being operator entry-points"; Cohort 2 autoplan). A solo `/li:fix` or `/li:autoplan` spawns no job → invisible to `/li:status`. `SHOULD` (operator-decision in Cohort 1: should composites spawn jobs?).
9. `skills/fix/SKILL.md` Step 3 soft-prompts lessons-promote post-fix (Cohort 1 fix D10) — closes the operator-relation write loop. `fires` (light).
10. `voice: internal` entry-point producing operator-only output → voice machinery correctly does not apply. `skipped`, not a finding.
11. Composites have no own observability jsonl and no `invoked_via` tag (Cohort 1: "operator can't distinguish /li:fix from /li:cycle --mode hotfix in logs"). `SHOULD` — should tag `cycle-runs.jsonl` with `invoked_via`.
12. Composite delegates knowledge to phases, but inherits the phase gaps (research → define/discover which DO consult; plan-and-build → build/review which do NOT). `SHOULD` where the delegated phases don't consult.
13. review-and-ship reaches SHIP (provenance hard-gate) — provenance fires via delegation. `fires`.
14. The 8 phase skills do NOT declare `workflow_root`; a solo `/li:sense`/`/li:build` leaves no job trace (Cohort 8 fn1, L1; Cohort 8 footnote). The participation model (nested-only vs per-skill touch) is undocumented — `SHOULD`.
15. `skills/sense/SKILL.md` Step 0a invokes `/li:lessons-surface`; Step 5 light-scan (Cohort 1 sense D10: "BEST lessons integration in cohort"). `fires`.
16. No phase reads a pack manifest; SENSE Step 0c hardcodes meta-infra detection rather than resolving a pack (Cohort 1 D7-runtime arch note; Cohort 7 zero-consumers). `SHOULD` (pack-resolver is BUILT — pure wiring gap).
17. sense/discover/resume write `00-state` but **no `*-metrics.jsonl`** and do not route through `bin/_audit.sh` (Cohort 1 sense D13 "writes no analytics jsonl"; discover D13; Cohort 8 L6). `SHOULD`.
18. `skills/define/SKILL.md` Integration reads `tasks/lessons.md` + `tasks/memory.md` (Cohort 1 define D10) — reads but no active surface-step like SENSE. `fires` (read-side present).
19. define/review/ship are `voice: mixed` — voice_tier gating + trailblazer hooks engage for customer-facing artifacts (voice grep: define/review path; review/ship Cohort 1 D7). `fires`.
20. define/plan/build/review/ship/capture each write a `*-metrics.jsonl` (Cohort 1 D13: spec-review.jsonl / plan-metrics / build-metrics / review-metrics / cycle-completion). Observability present — `fires` — but **bespoke writers, not `bin/_audit.sh`** (Cohort 8 L6). See §audit-fragmentation.
21. `skills/discover/SKILL.md:77` Step 3 lessons scan filtered-by-relevance + invokes `/li:lessons` (Cohort 1 discover D10) — but reads lessons.md, **never the pack knowhow base** (Cohort 8 fn2). `fires` for lessons; the knowhow half is unbuilt.
22. `skills/plan/SKILL.md:4` `workflow_root: true`; lines 374/407-408 document `job-begin` spawning the job dir (Cohort 8 fn5). The strongest jobs consumer. `fires`.
23. PLAN reads design+discover+ADRs+principles but **NOT lessons.md directly** (Cohort 1 plan D10) — relies on DISCOVER having surfaced them; breaks on hotfix-into-PLAN. `SHOULD`.
24. BUILD does not consult lessons during execution — the "don't mock Azure SDK" lesson never reaches the implementer subagent (Cohort 1 build D10, the marquee write-only-memory finding). `SHOULD`.
25. BUILD generates the artifact but writes **no provenance breadcrumb**; SHIP's source-chain auto-detect then infers from 24h-adjacent audit entries that may not exist (Cohort 8 fn6, L5). `SHOULD`.
26. REVIEW/SHIP do not consult lessons for known-recurring findings / ship-gotchas (Cohort 1 review D10, ship D10). `SHOULD`.
27. review/ship Stage-3 gates fire per `WorkProfile` (Cohort 1 review D7 "CLOSEST to real pack-influence"; ship D7). WorkProfile branching is BUILT — `fires` — though it reads legacy `profile.yaml`, not `compliance.workprofile_default` (Cohort 7 dual-location). The richest real pack-ish influence in the system.
28. `skills/review/SKILL.md:112-114` — `/li:provenance-track` fires conditionally (WorkProfile=on AND will-ship) (Cohort 8 fn7). `fires` (conditional).
29. `skills/ship/SKILL.md:100-102,232,250,294` — provenance hard-gate for customer-facing artifacts; strongest consumer (Cohort 8 fn8). `fires`.
30. `skills/ship/SKILL.md:81` writes `~/.lintel/audit/hard-rule-stops.jsonl` + provenance-log (Cohort 8 fn9). `fires` — but again **bespoke, bypasses `bin/_audit.sh`**; no `ship-metrics.jsonl` (Cohort 1 ship D13).
31. `skills/capture/SKILL.md` Steps 2-3 WRITE lessons + global promote (Cohort 1 capture D10: "BAR for lessons-WRITE side. But it's write-only — CAPTURE is producer; SENSE is only consumer"). `fires` but write-only — the read-side loop is the system-wide gap.
32. RESUME reads `00-state.md` (and job dir via `/li:jobs continue`) but is not itself jobs-aware as a producer — it routes INTO phases that should (but don't) touch jobs. `SHOULD` (resume should reconcile job state, per jobs participation decision).
33. RESUME is a state-recovery mechanic; surfacing lessons/knowhow is SENSE's job. `skipped` (correct delegation) — though Cohort 3 (context family) notes restore/resume could warm lessons tagged to the restored task (deferred, low).
34. `skills/jobs/SKILL.md` — the jobs lifecycle controller itself: list/continue/replan/abort/branch, sources `bin/_jobs.sh`. `fires` (it IS the jobs layer's operator surface).
35. jobs notes `job-begin`/`job-end`/`job-stale-warn` fire around it (jobs SKILL "Hooks fire" section) — `fires`.
36. `skills/jobs/SKILL.md:111` Step 4 writes `~/.lintel/audit/jobs.jsonl` — `fires`, but via `_jobs.sh` printf, **not `bin/_audit.sh`** (Cohort 8 L6, Cohort 5 §D13: two divergent writers).
37. `skills/status/SKILL.md` reads `~/.lintel/jobs/_active.md` — pure read of the jobs layer. `fires` (read).
38. status writes nothing (`skills/status/SKILL.md:84` "Writes: nothing") — a pure read alias, no audit needed. `skipped`, not a finding.
39. role-activate runs nested inside a cycle/standalone; it is not a workflow_root job-spawner. `skipped` (correct for kind).
40. `skills/role-activate/SKILL.md` injects a role brief that subagents inherit; `pack.yaml:67` declares `brief_forge on_subagent_spawn enabled` — this IS the Brief-Forge subagent-spawn path but role-activate never invokes it (Cohort 7 D9). `SHOULD·dnb` (Brief Forge unbuilt, but role-activate is a designed should-fire).
41. role-update WRITES role learnings; role-activate does not surface lessons tagged with the role-id on activation (Cohort 7 D10: write side exists, read side doesn't close the loop). `SHOULD`.
42. all 8 role skills hardcode the role-path triple and ignore pack `roles.source`/`roles.default_role` (Cohort 7 C7-ROLE-PACK-BLINDNESS). `SHOULD` (resolver BUILT — wiring gap).
43. role-activate sets `voice_tier` per role file (roles/*.md declare `voice_tier`); reverting voice is role-deactivate's job. Voice machinery engages. `fires`.
44. role-activate writes a `00-state` event but **no usage-log line** like pack-resolver does (Cohort 7 D13: "operator can see role activated in 00-state but not in a queryable usage log"). `SHOULD`.
45. autoplan's step-8 aggregation ("read all review-log entries from this run") is the **#1 Brief Forge call site in the planner cohort** (Cohort 2 autoplan D9). `SHOULD·dnb`.
46. autoplan doesn't consult lessons to decide default chain composition (Cohort 2 autoplan D10). `SHOULD`.
47. autoplan READS member review-logs but emits **no own run-level record** — an autoplan run is invisible to its own aggregator (Cohort 2 autoplan D13); members route through a **gstack-owned bin** (`~/.claude/skills/gstack/bin/gstack-review-log`, not Lintel's) (Cohort 2 fn). `SHOULD`.

---

## Cell tally

| classification | count |
|---|---|
| total cells (15 built rows... counting cycle..autoplan = 18 built entry-points × 8 layers) | **144** |
| `fires` (verified consumption) | 28 |
| `skipped` (correct n/a-for-kind) | 23 |
| **`SHOULD` (should-fire-doesn't — findings)** | **57** |
| `—` / not-applicable-unbuilt | 0 (folded into SHOULD·dnb where a designed consumer exists) |
| `fires!?` (fires-shouldn't / over-fire) | 0 |
| `DNB` (pack-* row, whole entry-point unbuilt) | 8 |

Of the 57 `SHOULD` cells, **27 are `SHOULD·dnb`** (the brief-forge column alone contributes 14 — every built entry-point is a designed brief-forge hand-off and none fire because the layer is unbuilt) and **30 are plain `SHOULD`** (layer is built; the gap is pure wiring — these are the highest-leverage because they require no new design).

> **Counting note.** The headline `total cells` = 144 covers the 18 built entry-points (cycle, fix, research, plan-and-build, review-and-ship, sense, define, discover, plan, build, review, ship, capture, resume, jobs, status, role-activate, autoplan) × 8 layers. The 9th row (`pack-*`, all `DNB`) is excluded from the 144 because the entry-point itself does not exist yet; its 8 cells are reported separately.

---

## Layer-by-layer reading (extends Cohort 8 across all entry-points)

- **jobs (built):** fires for only 4 of 18 entry-points (cycle, plan, jobs, status). The 8 phase skills, 4 composites, autoplan, resume all `SHOULD` — the participation model (nested-only vs per-skill job-touch) is undocumented (Cohort 8 L1). A solo `/li:sense`, `/li:build`, `/li:fix`, or `/li:autoplan` is invisible to `/li:status`.
- **brief-forge (designed-not-built):** 14 `SHOULD·dnb` — every built entry-point is a designed hand-off boundary (Cohort 2 autoplan = #1 site; Cohort 3 pair-agent/codex/save/restore; Cohort 7 role-activate subagent-spawn; Cohort 1 PLAN→BUILD trio). Uniform absence; the largest single block of should-fire cells, all blocked on one unbuilt layer.
- **knowledge:** lessons.md fires at 6 entry-points (sense BEST, define, discover, fix, capture write-only, review-and-ship via delegation) and `SHOULD` at the execution phases (plan, build, review, ship) — the **write-only-memory** gap: CAPTURE writes, SENSE reads, but PLAN/BUILD/REVIEW/SHIP never read (Cohort 1 #1 finding). The knowhow tag-funnel half is unbuilt everywhere (Cohort 8 L2).
- **hooks (built):** the only near-universal `fires` column — because hooks fire by event-matcher, not by skill invocation. Two caveats: (a) activation is opt-in via manual symlink so default installs fire nothing (Cohort 5 README); (b) no hook is pack-driven — 9/19 inline MS/Sweden/Trailblazer data (Cohort 5 D7).
- **packs:** `fires` at only review + ship (WorkProfile Stage-3 branching, the one real pack-ish influence) — and even there it reads legacy `profile.yaml`, not `compliance.workprofile_default` (Cohort 7 dual-location). Every other entry-point `SHOULD` consume the BUILT-but-zero-consumer `pack-resolver.sh` (Cohort 7 center finding). Highest pure-wiring leverage in the matrix.
- **voice (built):** fires correctly only at the `voice: mixed` entry-points (define, review, ship, review-and-ship, cycle-via-ship, role-activate). `skipped` for `voice: internal` front doors — these are NOT findings (correct n/a-for-kind).
- **provenance (built-partial):** fires at review (conditional) + ship (hard-gate) + their composite. The one real `SHOULD` is **build** (origin hole — generates the artifact, writes no breadcrumb; Cohort 8 L5).
- **audit-log:** fires (writes SOME jsonl) at 9 entry-points but **almost none route through `bin/_audit.sh`** — cycle→cycle-runs.jsonl, ship→hard-rule-stops.jsonl, jobs→jobs.jsonl, phases→*-metrics.jsonl are all bespoke writers (Cohort 8 L6, Cohort 5 §D13). `SHOULD` at sense/discover/resume/composites/role-activate/autoplan which write no audit line at all. This is the cleanest consolidation win (no new design).

---

## Observations

- **No fires-shouldn't (over-fire) found.** Every layer that fires does so appropriately. The system's failure mode is uniformly *under*-wiring, never over-wiring — consistent with the audit's NO-CUT thesis (nothing to remove; everything to raise).
- **Adoption clusters in three skills** — cycle, plan, ship (and review) — exactly as Cohort 8 found, and the X4 expansion confirms it holds across the *full* entry-point set: continuity skills (resume), composites, autoplan, and role-activate are even thinner consumers than the phase skills.
- **Two distinct gap classes** the matrix separates cleanly:
  - **wiring gaps (30 plain SHOULD)** — built layer, unwired consumer. Fix = add a `source`/call line. (packs ×13, audit-log ×8, knowledge-lessons ×4, jobs ×varies, provenance ×1.)
  - **build gaps (27 SHOULD·dnb + 8 DNB)** — layer (brief-forge, knowhow) or entry-point (pack-*) not built. Fix = ship the designed layer first (Phase 2-3).

---

## Top should-fire-doesn't cells, ranked by leverage

Ranked by (leverage = breadth × build-readiness): pure-wiring gaps on built layers rank above design-blocked gaps.

| # | Cell(s) | Why it's the gap that matters | Built? | Source |
|---|---|---|---|---|
| **1** | **packs → all 16 non-review/ship entry-points** | `lib/pack-resolver.sh` is fully built and tested with **zero consumers**; every entry-point hardcodes `profile.yaml` grep instead. One `source` line per skill-head closes 13+ cells at once and *deletes* duplicate parse sites (subtraction). The pack-driven-behavior promise is 0% upheld at the consumer layer. | **YES** | Cohort 7 C7-PACK-RESOLVER-ZERO-CONSUMERS |
| **2** | **audit-log → all 9 bespoke-writer + 6 silent entry-points** | `bin/_audit.sh` is the v4.0 unified writer; cycle/ship/jobs/phases all write bespoke jsonl with inconsistent field sets, and sense/discover/resume/composites/autoplan write nothing. Pure consolidation of already-built parts → grep/jq/replay uniformity. | **YES** | Cohort 8 L6, Cohort 5 §D13 |
| **3** | **knowledge(lessons) → plan, build, review, ship** | Write-only memory: CAPTURE writes lessons, SENSE reads them, but the four execution phases never do — the "don't mock Azure SDK" lesson never reaches the BUILD implementer. SENSE already proves the fix (Step 0a lessons-surface). | **YES** | Cohort 1 #1 finding |

**Runners-up (build-blocked, highest architectural leverage once their layer ships):**
- **brief-forge → autoplan step-8 + PLAN→BUILD trio + pair-agent/codex** — the densest designed hand-off cluster; one envelope schema (`lib/envelope-schema.yaml`, Phase 2) closes D1/D2/D3 across all 8 phase handoffs simultaneously (Cohort 8 L4).
- **jobs → the 8 phase skills + composites + autoplan** — resolve the participation model so `/li:status` reflects all in-flight work (Cohort 8 L1; operator-decision).

---

## NO-CUT statement

This matrix removes nothing. Every `SHOULD` is an entry-point that should *grow* a connection to a layer that already exists or is on the Phase-2/3 roadmap. The two cleanest wins (packs-resolver wiring, audit-log consolidation) require **no new design** — only `source` lines added at each entry-point head and bespoke writers re-routed through `bin/_audit.sh`. That is Subtraction Bias in service of uniformity: fewer parse patterns, one audit format, one pack read-path — and three ranked gaps that, closed, would lift adoption from "clustered in cycle/plan/ship" to "cross-cutting in fact, not just in name."
