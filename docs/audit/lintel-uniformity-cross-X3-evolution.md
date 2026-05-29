# X3 — operator-relation vs repo-relation evolution

**Cross-cutting pass:** X3 of 5
**Date:** 2026-05-29
**Branch:** v4.0-phase1-meta-infra-spine
**Inputs:** audit prompt §X3 + all 8 cohort findings files (cohort1-phase-core, cohort2-planner, cohort3-handoff, cohort4-agents, cohort5-hooks, cohort6-eng-domains, cohort7-packs-roles, cohort8-cross-cutting)
**Method:** synthesis only — no new file reads. Every mechanism is traced to a cohort finding with a file:line nano where the cohort recorded one.

---

## The motto under test

> *lär sig och växer ihop med operatören OCH repot* — the system must learn and grow in **both** threads.

- **OPERATOR-relation:** lessons accumulate + are consulted; voice calibrates; packs/profile/preferences compound across sessions.
- **REPO-relation:** ADRs accumulate + are consulted; knowhow grows; packaged lessons ship; envelopes/provenance compound across the repo's life.

X3 verifies **bidirectionality**: data must flow *both* written **and** consulted. A mechanism that only captures (write-only) does not make the system *grow with* its partner — it grows a landfill. The audit-wide pattern, found independently by six cohorts, is that **capture is strong and consultation is weak**. X3 makes that precise.

A mechanism is judged:

- **CLOSED-LOOP** — written by some component AND consulted/read back by some component (the loop returns).
- **WRITE-ONLY** — data is captured/persisted but no component reads it back to change behavior.
- **READ-ONLY** — consulted but never written by the system (e.g. operator-authored static input).
- **ABSENT** — designed-not-built; neither side exists yet.

---

## Headline mechanism table

| # | mechanism | thread | writes? | consulted? | verdict |
|---|-----------|--------|---------|------------|---------|
| 1 | lessons.md (CAPTURE → execution phases) | operator | yes — CAPTURE Steps 2-3 write + global-promote (cohort1 capture D10) | **partial** — SENSE Step 0a + DISCOVER Step 3 read; PLAN/BUILD/REVIEW/SHIP do **not** (cohort1 build/review/ship D10 = absent) | **write-only (mostly)** |
| 2 | lessons.md (planner sub-chain) | operator | (shared store) | **no** — office-hours, ceo, eng, design, devex, autoplan: 0/6 consult (cohort2 top-finding 3) | **write-only** |
| 3 | lessons.md (domain agents) | operator/repo | (shared store) | **partial** — only Architect + CodeReviewer read recent ADRs; majority of 83 agents don't (cohort4 D10) | **write-only (mostly)** |
| 4 | role-update → role-activate (role learnings) | operator | yes — role-update captures engagement learnings into role file (cohort7 role-update D10) | **no** — role-activate never surfaces role-tagged lessons (cohort7 role-activate D10) | **write-only** |
| 5 | voice calibration corpus (TRAILBLAZER-CALIBRATION) | operator | yes — corpus authored; staleness tracked | yes — no-trailblazer-without-corpus, no-en-vocab, stale-calibration-warn all read it (cohort5 D7 table) | **closed-loop** (but hardcoded path, not pack-driven) |
| 6 | question-preferences (plan-tune) | operator | yes — tombstone audit + questions.jsonl telemetry (cohort2 plan-tune D3/D10) | **no --suggest path** — telemetry written, never consulted back as a tuning suggestion (cohort2 plan-tune D10) | **write-only** |
| 7 | skill-router usage telemetry | operator | **partial** — reads ~/.lintel/telemetry/ frequency but logs nothing itself (cohort3 skill-router D13 absent) | reads on rank; writes nothing | **read-only / broken** |
| 8 | operator-profile.jsonl + cycle-completion.jsonl (CAPTURE) | operator | yes — richest observability in cohort1 (capture D13) | **no** — no component reads operator-profile back to adapt (no consumer found across cohorts) | **write-only** |
| 9 | WorkProfile / packs runtime resolution | operator/repo | declared in pack.yaml + resolver (cohort7) | **no consumers** — pack-resolver.sh has **zero callers**; 12 skills grep legacy profile.yaml instead (cohort7 C7-PACK-RESOLVER-ZERO-CONSUMERS) | **write-only at the pack layer / parallel old path** |
| 10 | ADRs (docs/adr) | repo | yes — adr-new / capture write (cohort4 ADRDrafter) | **partial** — context-warm-adrs, DISCOVER, Architect, CodeReviewer read; PLAN reads only if DISCOVER ran (cohort1 plan D10; cohort3 context-warm-adrs D10) | **closed-loop (narrow)** |
| 11 | knowhow tag-funnel (pack.knowhow) | repo | **no** — field declared `source: null`; no writer, no schema, no helper (cohort8 L2) | **no** — 0/8 phase skills read it (cohort8 L2 footnote 2) | **absent (designed-not-built)** |
| 12 | provenance store (~/.lintel/provenance) | repo | yes — REVIEW (conditional) + SHIP (gate) write (cohort8 L5) | yes — SHIP source-chain auto-detect reads adjacent entries; ProvenanceVerifier consumes (cohort8 L5) | **closed-loop (origin hole)** — BUILD writes nothing, so chain has a hole at source |
| 13 | payload envelope (lib/envelope-schema.yaml) | repo | **no** — file absent; handoffs are ad-hoc report files (cohort8 L4) | **no** — 0/8 consume (cohort8 L4) | **absent (designed-not-built)** |
| 14 | wiki generator (bin/li-wiki-gen) | repo | **no** — not built (cohort8 L3) | n/a — generator, not consumed | **absent (designed-not-built)** |
| 15 | jobs system (job.yaml / _active.md) | repo | yes — cycle + plan write; job-begin/end hooks (cohort8 L1) | yes — /li:jobs, /li:status, job-stale-warn read (cohort8 L1) | **closed-loop** (but only 2 of 8 phases participate) |
| 16 | bin/_audit.sh unified writer | repo | yes — built v4.0 Phase 1 | **partial** — meta-infra-overrides + pack-resolver.jsonl documented-consumed; brief-forge-override.jsonl write-only; **0 phase skills route through it** (cohort8 L6; cohort5 D13) | **write-only (mostly)** |
| 17 | hooks.jsonl / jobs.jsonl | repo | yes — 17/19 hooks write via inline printf (cohort5 D13) | yes — /li:hooks-status reads; surfaces trigger-counts + dead hooks (cohort5 D13) | **closed-loop** (the one clean repo loop) |
| 18 | context-save → context-dump/warm-sessions checkpoints | repo | yes — context-save writes (cohort3 CF-1) | **broken** — consumers read a different root/filename than producer writes (cohort3 CF-2) | **write-only (live breakage)** |
| 19 | context-ignore.md (context-cool IGNORE list) | repo | yes — context-cool writes coordination signal (cohort3 context-cool D3) | **no** — no skill/agent documented as reading it (cohort3 context-cool D3) | **write-only (orphan contract)** |
| 20 | Brief Forge envelopes at hand-offs | operator/repo | **no** — designed-not-built; 0/144 skills declare brief_forge_handoffs (cohort3 CF-3) | **no** | **absent (designed-not-built)** |

---

## Two-thread synthesis

### OPERATOR-relation thread (mechanisms 1-9)

The thread the operator experiences as *"it learns my taste."* **Capture is excellent; consultation is the floor.**

- **Strong write side, weak read side.** lessons.md is written and *globally promoted* by CAPTURE (the strongest write mechanism in the whole audit), but only 2 of the 8 phase skills (SENSE, DISCOVER) read it back. The four execution phases (PLAN, BUILD, REVIEW, SHIP) and the entire 6-skill planner sub-chain consult **nothing** — the marquee failure is a captured lesson like *"don't mock the Azure SDK"* that never reaches the BUILD implementer subagent (cohort1 build D10).
- **SENSE is the proof the loop CAN close.** SENSE Step 0a already surfaces lessons and closes its own L-001/L-002 loop — it is the working precedent every other phase should copy. The gap is non-adoption, not impossibility.
- **The one genuinely closed operator loop is voice calibration** (mechanism 5): the corpus is written, and three hooks read it back to gate Trailblazer output. But even this is hardcoded, not pack-driven (cohort5 D7), so it doesn't *grow* with new packs.
- **Profile/preferences compound into a landfill, not a feedback loop.** plan-tune writes preference telemetry but offers no `--suggest` consult-back (mechanism 6); CAPTURE writes operator-profile.jsonl that nothing reads (mechanism 8); skill-router reads usage frequency but records nothing, so its own routing can't learn (mechanism 7). Packs — the designed vehicle for operator-relation evolution — have a fully-built resolver with **zero consumers** (mechanism 9, the cohort-7 headline).

**Operator-thread verdict: ACTIVE on write, INERT on read.** The system records the operator faithfully and consults that record in exactly two places (SENSE lessons-surface, voice-calibration hooks). It does not yet *grow with* the operator everywhere it captures them.

### REPO-relation thread (mechanisms 10-20)

The thread the operator experiences as *"it knows this repo's history."* **Mixed: the built infrastructure loops close, the v4.0 knowledge layer is unbuilt, and several built loops are broken at the seam.**

- **The clean repo loops are the oldest infra.** hooks.jsonl → /li:hooks-status (mechanism 17) and jobs.yaml → /li:status (mechanism 15) are genuinely closed — write side and read side both exist and meet. These are v3.x mechanisms; maturity correlates with loop-closure.
- **ADRs are a narrow closed loop** (mechanism 10): written by adr-new, read by context-warm-adrs / DISCOVER / Architect. But the read is conditional — PLAN only sees ADRs if DISCOVER ran, so the hotfix-into-PLAN path flies blind (cohort1 plan D10).
- **Provenance closes but has an origin hole** (mechanism 12): REVIEW/SHIP write and SHIP reads back, but BUILD — which generates the artifact — writes no breadcrumb, so source-chain reconstruction infers from 24h-adjacent logs that may not exist (cohort8 L5).
- **The v4.0 repo-knowledge layer is entirely absent.** knowhow tag-funnel (11), payload envelope (13), wiki (14), and Brief Forge envelopes (20) are all designed-not-built. These are exactly the mechanisms meant to make *repo* knowhow grow and ship. Today knowhow is a single nullable pack field with no writer, no schema, no reader — the least-specified layer in the system (cohort8 L2).
- **bin/_audit.sh is a write-only standard** (mechanism 16): the v4.0 unified writer exists, but no phase skill routes through it and brief-forge-override.jsonl is write-side-design-only. The highest-stakes overrides (secret + customer-data blocks) bypass the unified trail entirely (cohort5 D13).
- **Two repo loops are live breakages, not just gaps.** context-save writes a root its named consumers (context-dump, context-warm-sessions) cannot read (mechanism 18, cohort3 CF-1/CF-2), and context-cool's IGNORE list has no documented consumer (mechanism 19). These are write-only by *defect*, not by design.

**Repo-thread verdict: PARTIALLY ACTIVE.** The mature infra loops (hooks, jobs, ADRs, provenance) close; the v4.0 knowledge-growth layer that the motto leans on (knowhow, envelope, wiki, Brief Forge) is unbuilt; and two built loops are broken at the producer/consumer seam.

---

## Tallies

Counting the 20 distinct mechanisms above:

- **CLOSED-LOOP: 5** — voice calibration (5), ADRs (10, narrow), provenance (12, origin hole), jobs (15, 2/8 participation), hooks.jsonl/hooks-status (17).
  *(All five carry a caveat — narrow, holed, or partial-participation — but the loop demonstrably returns.)*
- **WRITE-ONLY: 11** — lessons→execution (1), lessons→planner (2), lessons→agents (3), role-update→role-activate (4), plan-tune telemetry (6), operator-profile.jsonl (8), packs/resolver (9), _audit.sh unified (16), context-save→dump (18, broken), context-ignore.md (19), skill-router telemetry (7, write-side-missing / effectively non-learning).
- **ABSENT (designed-not-built): 4** — knowhow tag-funnel (11), payload envelope (13), wiki (14), Brief Forge (20).

So: **5 closed-loop, 11 write-only, 4 absent** (20 total).

If you collapse the three lessons.md rows (1-3) into one mechanism — which is fair, it is one store with three non-consuming reader populations — the count is **5 closed-loop, 9 write-only, 4 absent (18)**. Either way the headline holds: **write-only mechanisms outnumber closed-loop ones roughly 2:1.**

---

## Is the motto operational today?

**No — not yet. The system *learns* (captures) far better than it *grows* (consults).** Across six independent cohorts the same shape recurred: a strong, even best-in-class, write side paired with a weak or missing read side. CAPTURE promotes lessons globally but only SENSE and DISCOVER read them; role-update evolves role files but role-activate never surfaces them; plan-tune and CAPTURE write rich preference/profile telemetry that nothing consults; the pack-resolver is the best-engineered artifact in the repo with zero callers; and the v4.0 knowledge-growth layer (knowhow, envelope, wiki, Brief Forge) that the motto most depends on is still designed-not-built. The loops that *do* close are the oldest infrastructure (hooks→hooks-status, jobs→status) plus two narrow domain loops (ADRs, provenance) that themselves have caveats (conditional read; origin hole). The motto's first clause — *kraftfullt från start* — is upheld: the capture spine is powerful from day one. The second and load-bearing clause — *växer ihop med operatören och repot* — is only one-third realized, because growth requires the consultation half of each loop, and that half is the systematic gap. The good news embedded in the findings is that the fix is almost never new design: SENSE already proves the lessons loop can close, the pack-resolver is already built and only needs wiring, and the unified audit writer already exists and only needs callers. Operationalizing the motto is predominantly a *close-the-read-side* campaign, not a build-from-scratch one.

---

## RETURN summary

- **Closed-loop mechanisms: 5** (voice calibration, ADRs, provenance, jobs, hooks-status — each with a caveat).
- **Write-only mechanisms: 11** (9 if the three lessons reader-populations are collapsed to one).
- **Single biggest write-only gap:** **lessons.md is written and globally promoted by CAPTURE but consulted by almost nothing** — PLAN, BUILD, REVIEW, SHIP and the entire 6-skill planner sub-chain read zero lessons, so a captured rule like *"don't mock the Azure SDK"* never reaches the BUILD implementer. SENSE already closes this loop for itself; the gap is non-adoption everywhere else. This is the highest-leverage, lowest-cost fix in the operator-relation thread and the clearest single violation of *växer ihop med operatören*.
