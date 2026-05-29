# Lintel uniformity audit — MASTER (top-20 ranked)

**Completed:** 2026-05-29 · branch `v4.0-phase1-meta-infra-spine`
**Inputs:** 8 cohort findings files + 5 cross-cut files (X1–X5) in `docs/audit/`. Scale audited: 144 skills, 83 agents, 19 hooks, 1 pack, 6 cross-cutting layers.
**Method note:** removes nothing — every recommendation is an uplift to the strongest peer's depth, per the operator motto *kraftfullt från start, ständigt evolverande*.

---

## The one theme that explains half the findings

**Lintel's best machinery is built, tested, and unwired.** Three of the highest-leverage findings are the same shape: a correct, tested mechanism with **zero consumers**.

- `lib/pack-resolver.sh` — built, tested, self-described as a "30+ skill" interface → **0 callers** (every skill greps `profile.yaml` instead).
- `bin/_audit.sh` — the v4.0 unified audit writer → **0 phase callers** (3 divergent bespoke writers coexist instead).
- `lessons.md` — written by CAPTURE, promoted globally → read by **almost nothing** (PLAN/BUILD/REVIEW/SHIP + planner chain + ~80/83 agents never consult it).

These are not authoring tasks. They are **wiring + subtraction** — the cheapest possible fixes, and they convert *ständigt evolverande* from aspiration to mechanism. This cluster is the build-order headline: do it first.

The second theme: **a handful of real correctness bugs** (producer/consumer path mismatches) hiding under the uniformity gaps. Those are bugs, not taste — fix regardless of the broader reframe.

The third theme: **first-party-first is broken in Lintel's own planner chain** (it calls gstack binaries on the execution path) — the exact rule Lintel ships a hook to enforce on others.

---

## Top 20 findings (ranked by leverage = impact ÷ cost)

| # | Dim | Finding | Components affected | Proposed uplift (never cut) | Why this specifically | Effort | Depends on |
|---|---|---|---|---|---|---|---|
| 1 | D7 | **pack-resolver has zero consumers** — pack-driven behavior is BROKEN; 16/18 entry-points hardcode `profile.yaml` grep against a different file than canonical `pack.yaml` | all phase skills, 8 role skills, sense, compliance-gate, context-warm-from-url | One `source lib/pack-resolver.sh` + `resolve_pack_field` at each skill head; delete duplicate grep sites | The whole v4.0 reframe rests on packs; the engine exists and is tested — this is the single change that makes "swap pack = swap behavior" true | S–M | — |
| 2 | D10 | **lessons.md write-only** — cross-session memory broken; captured rule never reaches the BUILD implementer | plan, build, review, ship, all 6 planner skills, ~80 agents | Add a lessons-consult step at PLAN/BUILD/REVIEW head; SENSE already proves the pattern | Compounding edge is the motto's core; capture without consult is theatre | S | — |
| 3 | D13 | **`_audit.sh` zero phase callers + 3 divergent audit writers**; block-overrides (secret, customer-data) bypass the unified trail | all phases, 17 logging hooks, cycle, ship | Route all audit writes through `_audit.sh`; migrate bespoke jsonl; add a reader | Override-with-audit is only real if the audit is unified and consumed | M | — |
| 4 | D3 | **Storage-root schism + 2 live producer/consumer breakages** — `context-save`→`context-dump`/`warm-sessions` can't find files; planner chain reads `~/.gstack` but office-hours writes `~/.lintel` | context-save/dump/warm-sessions, office-hours, all 5 plan-* reviews | Pick one canonical root; fix the two broken read paths | These are correctness BUGS, not style — features silently no-op today | S | DEC-4 |
| 5 | promise | **First-party-first BROKEN in own planner chain** — reviews + codex + design-review call gstack-plugin binaries on the execution path | plan-ceo/eng/design/devex-review, codex | Replace gstack binary calls with first-party/in-repo equivalents | Lintel ships `non-first-party-warn` to enforce this on others; it violates it itself | M | — |
| 6 | D4 | **DISCOVER dynamic dispatch omits `frontend` category** (1-word fix) + 11 orphan agents never invoked | discover, 5 frontend agents + 11 orphans | Make the scan directory-derived (`for cat in agents/*/`); wire Explorer→DISCOVER, ResearchSynthesizer→/research | 5 agents permanently unreachable via the dynamic path; one-line fix kills the whole drift class | XS–S | — |
| 7 | depth | **Data Architecture is the thinnest engineering domain** — 2 agents, 0 skills/hooks/audit/gate, vs Security-Compliance's full block-on-ship stack | DA domain | Build DA enforcement layer copying SC's proven stack (3 designed hooks + module verdict) | A destructive migration / untagged-PII schema reaches main with zero DA gate today | L | v4.1 module work |
| 8 | D14 | **necessity + gap_if_skipped absent on ~148 components** — skipping a step silently degrades the result with no signal | all skills, agents, hooks | Make `necessity` + `gap_if_skipped` required frontmatter; backfill top-20 first | Architect declares it per-section; Lintel asserts "ship-ready" without saying what was skipped | M | DEC-8 |
| 9 | D5/D1 | **Jobs participation ambiguous** — only cycle + plan are `workflow_root`; `/li:sense`/`/li:build` run invisibly to `/li:status` | 8 phase skills, jobs, status | Document the participation model; decide per-skill workflow_root | Jobs-visibility promise is half-kept; solo phase runs vanish from the one status surface | S–M | DEC-9 |
| 10 | D7 | **Hooks not pack-driven** — 9/19 inline Swedish PII / EN-vocab / first-party data; no pack swap | customer-data trio, voice trio, non-first-party-warn | Drive activation + patterns from `pack.compliance.hooks`; `no-production-mutation`'s `.txt` is the prototype | A non-MS pack still gets MS-specific blocks with only crude off-switches | M | DEC-1, DEC-10 |
| 11 | D3 | **Envelope absence** — 8 phase hand-offs are ad-hoc report files, no HEAD/BODY/TAIL contract | all phase transitions | Ship `lib/envelope-schema.yaml` (v4.0 Ch.2 FR-B); a shape-test already expects it | Hand-off uniformity is impossible without the contract; highest *architectural* leverage | M | designed (Phase 2) |
| 12 | D7 | **WorkProfile dual-location** — value migrated to pack but 12 consumers still read legacy `profile.yaml:workprofile` | sense, compliance-gate, 10 others | Single-source via pack-resolver; deprecate legacy field with migration note | Shared-schema discipline violated; two truths for one toggle | S | DEC-1 |
| 13 | D9 | **Brief Forge should-fire densest at cohort-3 hand-offs** (designed-not-built) — pair-agent/codex/context-* already carry proto-evaluators reinvented ad-hoc | 18 handoff skills | Formalize existing PII/allowlist scans as named Brief Forge evaluators when Phase 3 ships | Don't let each skill reinvent the gate; the evaluators already exist informally | M | designed (Phase 3) |
| 14 | D8 | **Agent frontmatter drift** — 9 use structured `cli_support`, 74 compact; 24 missing `tier` | 33 agents | Normalize all 83 up to structured form; backfill tier | Frontmatter is the contract; drift breaks any future shape-test | S | — |
| 15 | D10 | **Role skills pack-blind** — all 8 ignore `pack.roles.source`/`default_role` | 8 role skills | Resolve role library via pack-resolver | A pack-scoped role library has no effect today | S | DEC-1 |
| 16 | D3 | **Config-file drift** — `profile.yaml` vs `config.yaml` vs `context-state.json` vs `00-state.md` (5-way) | context-* cohort | Unify on one config + one state file; document the split | Five homes for overlapping state guarantees divergence | M | DEC-4, DEC-15 |
| 17 | D13 | **Counts drift / stale docs** — README says "14 hooks" (actual 19), "81 skills"/"78 agents" (actual 144/83) | README, CLAUDE.md, design docs | Regenerate counts; tie to a count-check (L-003 made mechanical) | The repo's own L-003 lesson; a generated wiki/CATALOG closes it | S | — |
| 18 | D3 | **`cycle` promises `tokens_est_typical`** no phase frontmatter declares — broken reference | cycle + 8 phases | Add the field to phase frontmatter, or stop promising it | Dry-run/progress output references a field that doesn't exist | XS | — |
| 19 | D2/D13 | **Observability non-uniform across phases** — composites indistinguishable from raw `/li:cycle` in logs; SENSE/DISCOVER/SHIP lack peers' analytics | 8 phases + 4 composites | Uniform analytics line per phase + composite tag | Can't measure what you can't see; composites vanish in telemetry | S | DEC-3 |
| 20 | D6/D12 | **plan-design-review is the weakest planner** — gstack path bug, no checkpoint, claude-only cli_support, depends on external gstack binary | plan-design-review | Raise to plan-eng-review's bar (BLOCKING gate, checkpoint, in-repo) | Strongest peer (plan-eng-review) sets a clear bar; this one is below on 5 dims | M | DEC-5 |

---

## Cross-cut scorecard (from X1–X5)

- **X1 most-fragmented dimensions:** D7 (pack-influence, ~0% upheld at consumer layer), D3 (in/out contract, broken in planner + context cohorts), D10 (lessons, write-only in 5/8 cohorts).
- **X2 promises:** 1 UPHELD (founder PLAN pause) · 4 PARTIAL (lessons, jobs-visibility, 500k-cap, override-audit) · 2 BROKEN (pack-driven, first-party-first) · 3 DESIGNED-NOT-BUILT (Brief Forge, knowhow, navigation).
- **X3 evolution:** 5 closed-loop vs 11 write-only mechanisms. Capture is best-in-class; consultation is the systematic gap. Motto ~⅓ operational.
- **X4 entry-points:** 57 should-fire-doesn't of 144 cells; zero over-fire. The system under-wires uniformly. Top gap: packs → 16/18 entry-points.
- **X5 necessity:** ~148 components lack `necessity`; most dangerous absences = plan, review, customer-data-block.

---

## Recommended build order (leverage-first)

1. **Wiring sprint (findings #1, #2, #3, #6, #12, #15):** pack-resolver adoption + lessons read-side + unified audit + DISCOVER frontend fix. All cheap; converts 4 broken/partial promises to upheld. *This is itself a meta-infra change — ships under Gate M1–M4.*
2. **Correctness bugs (#4, #18):** storage-root + broken read paths + tokens_est reference. Fix regardless.
3. **First-party-first (#5):** de-gstack the planner chain.
4. **Contract sprint (#8, #14, #17):** necessity field + agent frontmatter normalization + counts regen — the substrate a continuous uniformity shape-test would later check (the parked reframe).
5. **Designed-not-built, on-schedule (#11, #13):** envelope (Phase 2), Brief Forge (Phase 3) per existing v4.0 plan.
6. **Domain depth (#7):** build DA first using SC as template (v4.1).

See `lintel-uniformity-VOTE.md` for the consolidated operator decisions (44 per-component yes-flags collapse to ~15 distinct decisions).
