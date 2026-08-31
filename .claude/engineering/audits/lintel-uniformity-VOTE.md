# Lintel uniformity audit — VOTE register

**For:** operator. Mark your choice by putting `[x]` on one approach per decision (or write your own under "operator note").
**Consolidation:** the 8 cohorts flagged ~44 `operator_decision_required: yes` records. Most collapse — e.g. all 7 role-skill flags are the *same* "wire to pack-resolver?" decision. They're consolidated into the 15 distinct decisions below, leverage-ranked. Each links to its source cohort/cross-cut file.
**Rule:** no option removes functionality. Every approach is an uplift or a wiring/consolidation choice.

---

## DEC-1 — pack-resolver: adopt the built engine, or keep profile.yaml grep?
*Source: cohort7, X2, X4 · finding #1 · the highest-leverage decision in the audit.*
`lib/pack-resolver.sh` is built + tested with zero consumers; ~16 entry-points hardcode `grep profile.yaml`.

- [ ] **A (recommended)** — Wire `pack-resolver` as the single state interface at every consumer head; delete duplicate grep sites. Makes pack-swap real; subtracts code.
- [ ] **B** — Keep profile.yaml grep; demote pack-resolver to a thin wrapper over profile.yaml. Less churn, but pack-driven behavior stays broken.
- [ ] **C** — Hybrid: pack-resolver reads, profile.yaml remains the write target for now; migrate writes later.

**Recommendation: A** — the engine exists; this is the change that makes the whole v4.0 pack reframe true. *Operator note:* ____

---

## DEC-2 — lessons read-side: which phases must consult lessons.md?
*Source: cohort1, X3, X4 · finding #2.* Captured lessons reach almost nothing today.

- [ ] **A (recommended)** — PLAN + BUILD + REVIEW consult lessons at head (SENSE already does). Closes the compounding loop where it pays most.
- [ ] **B** — Only BUILD consults (the implementer is where a lesson like "don't mock the Azure SDK" lands).
- [ ] **C** — All phases + planner chain consult. Most complete, highest token cost per phase.

**Recommendation: A.** *Operator note:* ____

---

## DEC-3 — unified audit: migrate to `_audit.sh`, or keep bespoke writers?
*Source: cohort5, cohort8, X4 · finding #3.* 3 divergent writers; block-overrides bypass the unified trail; `_audit.sh` has 0 callers.

- [ ] **A (recommended)** — Route all audit writes through `_audit.sh`; add a reader (extend `/li:hooks-status`); migrate bespoke jsonl. One trail, consumed.
- [ ] **B** — Keep per-domain jsonl but standardize the field schema across writers (shared-schema, no central writer).
- [ ] **C** — Minimal: only route the two block-override paths (secret, customer-data) through `_audit.sh`; leave the rest.

**Recommendation: A.** *Operator note:* ____

---

## DEC-4 — canonical storage root (fixes live producer/consumer bugs)
*Source: cohort2, cohort3, X1 · finding #4.* Data lives across `~/.gstack/`, `~/.lintel/sessions/`, in-repo `.lintel/state/`, `~/.lintel/audit/`. Two named consumers can't read their named producer.

- [ ] **A (recommended)** — Canonicalize on `~/.lintel/`; fix `context-save`→`dump`/`warm-sessions` paths + planner chain `~/.gstack`→`~/.lintel`. Lintel-native, first-party.
- [ ] **B** — Canonicalize on `~/.gstack/` (matches gstack tooling the operator also runs). Conflicts with first-party-first.
- [ ] **C** — Per-job dirs only (`~/.lintel/jobs/<id>/`) for all transient state; deprecate loose roots.

**Recommendation: A** (with C as the longer-term shape). These are correctness bugs — fix regardless of which root. *Operator note:* ____

---

## DEC-5 — first-party-first: de-gstack the planner chain?
*Source: cohort2, X2 · finding #5.* plan-*-review + codex + design-review call gstack-plugin binaries on the execution path.

- [ ] **A (recommended)** — Replace gstack binary calls with in-repo/first-party equivalents (review-log, design tooling). Honors the rule Lintel enforces on others.
- [ ] **B** — Keep gstack calls but guard behind a capability check + document the dependency. Pragmatic, but the violation stands.
- [ ] **C** — Make the planner reviews pack-policy-gated: caip-se pack forbids 3P binaries, _default allows. Ties to DEC-1.

**Recommendation: A.** *Operator note:* ____

---

## DEC-6 — DISCOVER dispatch + orphan agents
*Source: cohort4 · finding #6.* Dynamic scan omits `frontend`; 11 agents never invoked.

- [ ] **A (recommended)** — Directory-derive the scan (`for cat in agents/*/`) + wire the high-value orphans (Explorer→DISCOVER, ResearchSynthesizer→/research, CloudTestSuiteAuthor→BUILD). Kills the drift class.
- [ ] **B** — Just fix the frontend omission (1 word); leave orphans for later.
- [ ] **C** — A + audit all 83 agent descriptions so the dynamic keyword-score actually reaches them.

**Recommendation: A.** *Operator note:* ____

---

## DEC-7 — Data Architecture: build the enforcement layer now?
*Source: cohort6 · finding #7.* DA is the thinnest domain (2 agents, no gate); SC is the bar.

- [ ] **A (recommended)** — Build DA first among the v4.1 modules, copying SC's proven block-on-ship stack (3 designed hooks + module verdict).
- [ ] **B** — Defer all 5 engineering modules to their scheduled v4.1–v4.5 cadence; don't reorder for DA.
- [ ] **C** — Ship just the 3 DA hooks now (schema-breaking/pii-in-schema/retention) without the full module.

**Recommendation: A** (DA's gap is the most dangerous — destructive migrations reach main ungated). *Operator note:* ____

---

## DEC-8 — make `necessity` + `gap_if_skipped` required frontmatter?
*Source: X5, cohort1/2/5 · finding #8.* Absent on ~148 components.

- [ ] **A (recommended)** — Add both as required fields; backfill the top-20 highest-leverage components first; enforce via frontmatter-lint shape-test.
- [ ] **B** — Recommended (not required) field; backfill opportunistically.
- [ ] **C** — Only on `workflow_root` skills + block-hooks (where skipping is most dangerous).

**Recommendation: A** (this is the substrate the parked uniformity-as-contract reframe would later check). *Operator note:* ____

---

## DEC-9 — jobs participation model
*Source: cohort8, cohort1 · finding #9.* Only cycle + plan are `workflow_root`; solo phase runs are invisible to `/li:status`.

- [ ] **A (recommended)** — Document "nested-only" explicitly + let any phase opt into `workflow_root` when run solo. Clear model, no surprise.
- [ ] **B** — Make all 8 phases `workflow_root`. Maximum visibility, more job churn.
- [ ] **C** — Status surface also lists non-job phase runs from the analytics log. No frontmatter change.

**Recommendation: A.** *Operator note:* ____

---

## DEC-10 — hooks pack-drivability
*Source: cohort5 · finding #10.* 9/19 hooks inline MS/Sweden/Trailblazer data.

- [ ] **A (recommended)** — Drive hook activation + patterns from `pack.compliance.hooks` (the `no-production-mutation` `.txt` extensibility is the prototype). Depends on DEC-1.
- [ ] **B** — Keep inline patterns but extract them to per-pack data files the hooks read. Lighter than full pack-drive.
- [ ] **C** — Leave as-is; document that caip-se patterns are the default and other packs override via env/markers.

**Recommendation: A.** *Operator note:* ____

---

## DEC-11 — WorkProfile single source
*Source: cohort7 · finding #12.* 12 consumers read legacy `profile.yaml:workprofile`; value also lives in pack.

- [ ] **A (recommended)** — Single-source via pack (`compliance.workprofile_default`) through pack-resolver; deprecate legacy field with a `/li:migrations` entry. Depends on DEC-1.
- [ ] **B** — Keep `profile.yaml` as the source; pack field mirrors it.

**Recommendation: A.** *Operator note:* ____

---

## DEC-12 — agent frontmatter normalization
*Source: cohort4 · finding #14.* 9 structured vs 74 compact `cli_support`; 24 missing `tier`.

- [ ] **A (recommended)** — Normalize all 83 to structured `cli_support` (carries per-cli `level`); backfill `tier`. Enforce via shape-test.
- [ ] **B** — Normalize down to compact form (simpler, loses per-cli level granularity).

**Recommendation: A** (normalize up, never lose information). *Operator note:* ____

---

## DEC-13 — Brief Forge handoff field: adopt now or at Phase 3?
*Source: cohort3 · finding #13. Designed-not-built.*

- [ ] **A (recommended)** — Add `brief_forge_handoffs:` declaration to handoff skills NOW (inert until Phase 3) so the contract exists and proto-evaluators get named. No behavior change yet.
- [ ] **B** — Wait for Phase 3; don't add inert frontmatter.

**Recommendation: A** (cheap, and the existing proto-evaluators stop drifting). *Operator note:* ____

---

## DEC-14 — context skill consolidation (snapshot vs save)
*Source: cohort3 · finding #16.* Overlapping save/snapshot/dump semantics.

- [ ] **A (recommended)** — Keep all skills (no-cut) but declare one canonical (`context-save`) and document the others as thin specializations of it.
- [ ] **B** — Merge snapshot into save behind a `--named` flag; keep the alias.
- [ ] **C** — Leave separate; just fix the broken read paths (covered by DEC-4).

**Recommendation: A.** *Operator note:* ____

---

## DEC-15 — config file unification (profile.yaml vs config.yaml)
*Source: cohort3 · finding #16.*

- [ ] **A (recommended)** — One operator config (`~/.lintel/profile.yaml`); fold `config.yaml` knobs into it; document. Depends on DEC-4.
- [ ] **B** — Keep two files with a documented split (profile = identity/role, config = thresholds).

**Recommendation: A.** *Operator note:* ____

---

## Suggested voting order

Vote DEC-1 → DEC-2 → DEC-3 → DEC-4 → DEC-5 first (the leverage cluster + the bugs). Those five unblock most of the rest. The remaining ten are largely "yes, the obvious uplift" — skim and confirm.

When voted, these become the next backlog cycle. The parked reframe (uniformity-as-contract: frontmatter schema + Gate-M3 shape-test #9 + regenerable matrix) sits naturally on top of DEC-8 + DEC-12 + DEC-17-counts once the substrate exists — revisit after the wiring sprint surfaces what's real.
