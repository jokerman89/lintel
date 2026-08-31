# Lintel uniformity remediation plan

**Status:** DRAFT_FOR_REVIEW — produced from the system-wide uniformity audit (8 cohorts + X1–X5 + MASTER + VOTE in `.claude/engineering/audits/`).
**Branch target:** new work off `v4.0-phase1-meta-infra-spine`.
**Mode:** **meta-infra** — nearly every task touches `skills/`, `agents/`, `hooks/`, `bin/`, `lib/`. Ships under Gate M1–M4 (structure-impact, compatibility-audit, shape-tests, future-operator validation) per `.claude/engineering/design-archive/lintel-v4.0-reframe-design.md` Ch.4.
**Motto constraint:** *kraftfullt från start, ständigt evolverande* — this plan removes no functionality. Every task is wiring, consolidation, or uplift to the strongest peer's depth.

---

## Problem statement (what the audit found)

The audit surfaced three structural themes, not 44 scattered defects:

1. **Built-but-unwired cluster (the dominant theme).** Lintel's best machinery exists, is tested, and has zero consumers: `lib/pack-resolver.sh` (0 callers), `bin/_audit.sh` (0 phase callers), `lessons.md` (write-only). These broke or half-broke 4 architectural promises. The fix is wiring + subtraction — the cheapest, highest-leverage work in the repo.
2. **A handful of real correctness bugs** hiding under uniformity gaps: producer/consumer path mismatches where a named consumer cannot read its named producer (`context-save`→`context-dump`/`warm-sessions`; planner chain reads `~/.gstack` while office-hours writes `~/.lintel`).
3. **First-party-first broken in Lintel's own planner chain** — it calls gstack binaries on the execution path, the exact rule Lintel ships a hook to enforce on others.

Plus: uniform weaknesses (necessity declarations absent on ~148 components; frontmatter drift on 33 agents; counts stale in README), and designed-not-built layers (envelope, Brief Forge, knowhow, wiki, engineering-domain modules) that are on-schedule, not regressions.

## Goal

Close every BROKEN/PARTIAL promise, fix the correctness bugs, normalize the contract substrate, and leave the designed-not-built work on its v4.0 schedule — in a leverage-first order where each sprint is independently shippable and verified by a shape-test so the fixes can't silently regress.

## What already exists (leverage map — do not rebuild)

| Need | Existing asset | Action |
|---|---|---|
| Pack state resolution | `lib/pack-resolver.sh` (built, tested) | Wire consumers; delete duplicate grep |
| Unified audit | `bin/_audit.sh` (built) | Route writers through it; add reader |
| Cross-session memory | `lessons.md` + `lessons-promote` | Add read-side at PLAN/BUILD/REVIEW |
| Shape enforcement | `tests/shape/` (8 tests) + Gate M3 | Add tests that lock each fix |
| Migration discipline | `docs/migrations/_INDEX.md` + `/li:migrations` | One entry per breaking change |
| Audit trail writer | `bin/_audit.sh` | Reuse for override consumption |

## NOT in scope (deferred, with rationale)

- **Building the engineering-domain modules** (TA/DA/SC/DH/TQ as full v4.0 `domain:` modules) — scheduled v4.1–v4.5; this plan only ships DA's enforcement *hooks* as the highest-risk slice (W6).
- **Brief Forge runtime + envelope runtime + wiki-gen** — designed for Phase 2/3 of the v4.0 reframe; this plan only adds their *inert frontmatter contracts* (W4) so declarations stop drifting before the runtime lands.
- **The "uniformity-as-contract" reframe** (the parked /autoplan recommendation) — revisit after W4 establishes the substrate; not committed here.
- **Multi-pack stacking, pack marketplace** — out of v4.0 scope entirely.

---

## Workstreams (leverage-first, each independently shippable)

### W1 — Wiring sprint: pack-resolver adoption (finding #1, #12, #15; DEC-1, DEC-11)

**What:** Make `pack-resolver` the single state-resolution interface. Replace ~16 hardcoded `grep ~/.lintel/profile.yaml` sites with `source lib/pack-resolver.sh` + `resolve_pack_field`. Single-source WorkProfile via `compliance.workprofile_default`. Point the 8 role skills at `pack.roles.source`/`default_role`.

**Files:** `skills/sense/SKILL.md`, `skills/compliance-gate/SKILL.md`, `skills/context-warm-from-url/SKILL.md`, all 8 `skills/role-*`/`roles-list`, plus any other `profile.yaml`-grep site (enumerate via `grep -rln "profile.yaml" skills/`).

**Tasks (≤5 min cold-executor each):**
- W1.1 Enumerate every `profile.yaml` grep site → checklist.
- W1.2 Add `resolve_pack_field` calls per consumer, one skill per task.
- W1.3 Delete the duplicate grep after each swap.
- W1.4 Migrate WorkProfile reads to the pack field; add `/li:migrations` entry + grace window.
- W1.5 Wire role skills to pack `roles.source`.

**Tests:** extend `tests/unit/pack-resolver-fallbacks.sh` (per v4.0 FR-A.7); new `tests/shape/no-hardcoded-profile-grep.sh` asserting no execution-path `grep profile.yaml` remains.
**Verification:** `/li:pack-switch _default` vs (future) `caip-se` measurably changes behavior; promise X2#2 flips BROKEN→UPHELD.
**Risk:** silent regression if a swap leaves a hardcoded reference. Mitigation: the test harness ships *before* the swaps (FR-A.7 discipline).

### W2 — Wiring sprint: lessons read-side (finding #2; DEC-2)

**What:** Add a lessons-consult step at the head of PLAN, BUILD, REVIEW (SENSE already does it). The captured rule reaches the implementer.

**Files:** `skills/plan/SKILL.md`, `skills/build/SKILL.md`, `skills/review/SKILL.md` (+ planner chain if DEC-2 lands on option C).

**Tasks:** W2.1 define the consult contract (which lessons, keyword-scoped vs recent-N); W2.2 add the step per skill; W2.3 declare consultation in frontmatter (`reads: lessons.md`).
**Tests:** `tests/shape/lessons-consulted-by-exec-phases.sh` — asserts the three exec phases declare the lessons read.
**Verification:** X3 lessons mechanism flips write-only→closed-loop; promise X2#1 PARTIAL→UPHELD.

### W3 — Wiring sprint: unified audit (finding #3, #20; DEC-3)

**What:** Route all audit writes through `bin/_audit.sh`. Migrate the 3 bespoke writers (`jobs.jsonl` direct, `cycle-failures.jsonl`, `hard-rule-stops.jsonl`) and the two block-override paths (secret, customer-data) onto it. Add a reader (extend `/li:hooks-status` or a new `/li:audit`). Uniform per-phase analytics line; composite tag so composites are distinguishable in logs.

**Files:** `bin/_jobs.sh`, `hooks/shared/{secret-scan-block,customer-data-block}/run.sh`, `skills/cycle/SKILL.md`, `skills/ship/SKILL.md`, 17 logging hooks, `skills/hooks-status` (or new `skills/audit`).
**Tasks:** W3.1 define the unified record schema (shared-schema discipline); W3.2 migrate each writer; W3.3 add the reader; W3.4 per-phase analytics + composite tag.
**Tests:** `tests/shape/audit-writes-via-helper.sh` — no inline `printf >> *.jsonl` on the audit path.
**Verification:** override-with-audit promise PARTIAL→UPHELD; X4 audit-log column closes.

### W4 — Contract substrate sprint (finding #8, #13, #14, #17, #18; DEC-8, DEC-12, DEC-13)

**What:** Normalize the frontmatter contract so a future uniformity shape-test has something to check. Add `necessity` + `gap_if_skipped` as required fields (backfill top-20 first). Normalize all 83 agents to structured `cli_support` + backfill `tier`. Add inert `brief_forge_handoffs:` declarations to handoff skills. Add `tokens_est_typical` to phase frontmatter (or stop `cycle` promising it). Regenerate stale counts in README/CLAUDE.md and add a count-check (L-003 made mechanical).

**Files:** all skills (frontmatter), all 83 agents, `README.md`, `CLAUDE.md`, `skills/cycle/SKILL.md` + 8 phases.
**Tasks:** W4.1 schema definition; W4.2 backfill top-20 necessity; W4.3 agent frontmatter normalization (scriptable); W4.4 inert brief_forge fields; W4.5 tokens_est_typical; W4.6 counts regen + `tests/shape/counts-match-reality.sh`.
**Tests:** extend `tests/shape/frontmatter-lint-all.sh` with the new required fields per-kind.
**Verification:** D8/D14 fragmentation closes; substrate ready for the parked reframe.

### W5 — Correctness bugs + first-party-first (finding #4, #5, #16; DEC-4, DEC-5, DEC-15)

**What:** Fix the live producer/consumer breakages and de-gstack the planner chain. Canonicalize storage on `~/.lintel/`; fix `context-save`→`dump`/`warm-sessions` paths and planner-chain `~/.gstack`→`~/.lintel`. Replace gstack-binary calls in plan-*-review/codex with in-repo equivalents. Unify config (`profile.yaml` canonical; fold `config.yaml`).

**Files:** `skills/context-{save,dump,warm-sessions}/SKILL.md`, `skills/office-hours/SKILL.md`, `skills/plan-{ceo,eng,design,devex}-review/SKILL.md`, `skills/codex/SKILL.md`.
**Tasks:** W5.1 canonical-root decision applied; W5.2 fix two broken read paths; W5.3 planner-chain path fix; W5.4 first-party log/tooling swap; W5.5 config unification + migration entry.
**Tests:** `tests/shape/no-gstack-binary-on-exec-path.sh`; a round-trip test for save→dump.
**Verification:** first-party-first BROKEN→UPHELD; the two named consumers find their producer's output.

### W6 — Targeted depth + dispatch (finding #6, #7, #9, #10; DEC-6, DEC-7, DEC-9, DEC-10)

**What:** Kill the dispatch drift class and ship DA's enforcement slice. Directory-derive DISCOVER's agent scan (`for cat in agents/*/`); wire high-value orphans (Explorer→DISCOVER, ResearchSynthesizer→/research, CloudTestSuiteAuthor→BUILD). Ship DA's 3 designed hooks (schema-breaking-change-warn, pii-in-schema-warn, retention-policy-required-warn) copying SC's block-on-ship pattern. Document the jobs participation model + let phases opt into `workflow_root` solo. Make hooks pack-driven (activation + patterns from `pack.compliance.hooks`).

**Files:** `skills/discover/SKILL.md`, the 11 orphan agents (descriptions), 3 new `hooks/shared/*-warn/`, `docs/concepts/jobs-system.md`, 9 MS-specific hooks (pack-drive), `packs/_default/pack.yaml` (hooks block).
**Tasks:** W6.1 directory-derive scan; W6.2 wire orphans; W6.3 DA hooks (one per task); W6.4 jobs-participation doc; W6.5 hooks pack-drive (depends on W1).
**Tests:** `tests/shape/discover-scans-all-agent-categories.sh`; DA-hook fixtures.
**Verification:** all 10 agent categories reachable; DA gains an enforcement layer; hooks swap with pack.

---

## Sequencing + dependency graph

```
W1 (pack-resolver) ─────┬──► W6.5 (hooks pack-drive)
                        └──► W4 partial (pack fields)
W2 (lessons read) ── independent
W3 (unified audit) ── independent ──► W3.4 composite tag
W4 (contract substrate) ── independent (enables parked reframe later)
W5 (bugs + first-party) ── independent (ship early; they're bugs)
W6 (dispatch + DA + jobs) ── W6.5 depends on W1; rest independent
```

**Ship order:** W5 (bugs) + W1 (pack-resolver) first — bugs because they're bugs, W1 because it unblocks W6.5 and the most promises. Then W2, W3 (parallel-eligible). Then W4 (substrate). Then W6. Each workstream is one PR under meta-infra Gate M1–M4 with a `MIGRATION.md` entry where it breaks a shape.

**Estimate:** W1 ~M, W2 ~S, W3 ~M, W4 ~M-L, W5 ~M, W6 ~L (DA hooks dominate). Total ~human-weeks / CC-days range; each PR independently mergeable.

## Operator decisions folded in (defaults = audit recommendations)

This plan assumes option **A** for all 15 VOTE decisions (the recommended uplift). The load-bearing ones to confirm before W1/W5 start: **DEC-1** (adopt pack-resolver), **DEC-4** (canonical root = `~/.lintel/`), **DEC-5** (de-gstack planner). The rest are "obvious uplift" and can be confirmed at the gate. Full register: `.claude/engineering/audits/lintel-uniformity-VOTE.md`.

## Verification criteria (plan is "done" when)

1. X2 promises: pack-driven + first-party-first flip BROKEN→UPHELD; lessons + override-audit flip PARTIAL→UPHELD.
2. X4 matrix: the 30 pure-wiring should-fire-doesn't cells close (the 27 design-blocked remain, on schedule).
3. Every fix is locked by a `tests/shape/` test that fails if the wiring regresses.
4. `grep -rln "profile.yaml" skills/` returns no execution-path matches (pack-resolver is the interface).
5. Save→dump round-trips; DISCOVER reaches all 10 agent categories; DA can block a ship.
6. Each breaking change has a `docs/migrations/` entry + `/li:migrations` surfaces it.

## Risks

- **R1 — wiring sprint leaves a hardcoded reference behind.** Mitigation: ship the pack-resolver test harness before the swaps; final `grep -r` sweep as a PR artifact (W1).
- **R2 — meta-infra overhead on 6 PRs feels heavy.** Mitigation: Gate M2/M3 are mechanical (run automatically); only M1/M4 need thinking. The shape-tests are the payoff — they make these fixes un-regressable.
- **R3 — DA hooks over-block.** Mitigation: ship as `warn` first (like SC's progression), promote to block after a grace window.
- **R4 — counts/README regen drifts again.** Mitigation: `counts-match-reality.sh` shape-test makes it CI-enforced (closes the L-003 lesson mechanically).
- **R5 — config/root canonicalization breaks an operator script.** Mitigation: alias + grace window via `config/aliases.yaml` + `/li:migrations`.
