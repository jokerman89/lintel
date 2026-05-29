# /autoplan review — Lintel uniformity remediation plan

**Reviewed:** 2026-05-29 · branch `v4.0-phase1-meta-infra-spine` · `[subagent-only]` (codex unavailable)
**Plan:** [lintel-uniformity-REMEDIATION-PLAN.md](lintel-uniformity-REMEDIATION-PLAN.md) · restore: `docs/audit/.restore-remediation-20260529-191518.md`
**Pipeline:** CEO → (Design skipped, no UI) → Eng → DX.

> Verdict: the plan is directionally right (leverage-first, no-removal, shape-tested) but has **one critical architecture flaw** and **repeats the exact anti-pattern it was written to cure**. Both are fixable without changing the goal. The Eng voice caught the flaw; all three converged on the restructure.

---

## Consensus table

| Dimension | CEO | Eng | DX | Consensus |
|---|---|---|---|---|
| W1 "replace profile.yaml grep with pack-resolver" sound? | premise-risky | **NO — category error** | undercount 25≠16 | **DISAGREE w/ plan — split W1** |
| Does the plan repeat contract-before-consumer? | YES (W4-inert, W6-DA) | — | — | **CONFIRMED — defer those** |
| 6 meta-infra PRs proportionate? | NO (stalls) | over-heavy for W2/W5 | **NO — collapse to 3** | **CONFIRMED — 3 themed PRs** |
| Promote de-gstack (first-party) to first PR? | YES (credibility bug) | — | — | **CONFIRMED** |
| "Default A on 15 votes" good? | NO (hides 5 strategic) | — | NO (hides 3) | **DISAGREE — split 3 explicit + 12 confirm** |
| W5 bugs first? | yes, but W1 behind it | — | yes + front-load save→dump | **CONFIRMED w/ TTHW reorder** |

No cross-phase contradiction. Single-model (codex down) so these are strong recommendations, not formal dual-model User Challenges — but the operator's stated plan-shape is challenged on 4 points, surfaced at the gate.

---

## Critical finding (Eng) — W1 is a category error

`lib/pack-resolver.sh` resolves **pack-identity config** (voice tier, compliance mode, navigation). But ~25 files (plan said 16 — a 56% undercount) grep `profile.yaml` mostly for **operator runtime state**: `role_active`, `default_mode`, `azure_focus`, `workprofile`, `proactive` (see `skills/sense/SKILL.md` Step 1). The resolver has **no concept of those fields**, and its cache is cycle-immutable while operator state is session-mutable. Replacing those reads with `resolve_pack_field` is wrong; the proposed `no-hardcoded-profile-grep.sh` test would force removal of reads that have nowhere to go, then be weakened to theater.

**Fix (auto-applied to plan v2):** split W1 →
- **W1a** — genuine pack-config reads → `resolve_pack_field`.
- **W1b** — operator runtime state → a second helper `resolve_profile_field` (define-once-import-both, same discipline).
- Ship a **state-ownership table** (which field is pack-sourced vs profile-sourced) as the *first artifact*, before any swap. Every downstream workstream depends on it.

Plus two Eng sub-fixes auto-applied: (1) pack-resolver cache key is `PPID`-based → mid-cycle `/li:pack-switch` won't be seen; **pin to cycle/job id** (`LINTEL_CYCLE_ID` already exists). (2) W3's real work is "make `_jobs.sh` source `_audit.sh` + delete its 3 inline `printf` records" (and pack-resolver's `_resolver_audit` is a 4th inline writer the plan missed) — not "define a schema" (the schema already is `audit_log`).

## High finding (CEO) — the plan repeats contract-before-consumer

The audit's whole thesis: building ahead of consumers (pack-resolver, `_audit.sh`, lessons) is the repo's central sin. **W4's inert `brief_forge_handoffs:` + `tokens_est_typical`** and **W6's DA hooks** commit that sin again — adding contracts/gates for runtimes (Brief Forge) and modules (DA, scheduled v4.1) that don't exist yet. In 6 months either the runtime shipped (and the guessed fields were wrong) or it didn't (dead frontmatter drifts — the L-003 disease).

**Fix (auto-applied):** W4 keeps `necessity` + `gap_if_skipped` (consumer-independent documentation, useful now) and the counts-regen. **Defer** `brief_forge_handoffs` and `tokens_est_typical` until their consumer is built. **Defer** W6's DA *hooks* to the v4.1 DA module; W6 keeps only the cheap, owed dispatch fixes (directory-derive DISCOVER scan + orphan wiring).

## High finding (DX) — collapse 6 PRs → 3 themed PRs

Gate ceremony is flat (every PR carries M1 structure-impact + M4 future-operator validation) but the work isn't (W2 = 3 one-line edits; W4 = touches 83 agents). 6× M1/M4 for ~2x real structural change stalls a single-operator harness. **Fix (auto-applied):** PR-A = W5+W1, PR-B = W2+W3, PR-C = W4+W6. Shape-tests still ship per-fix → identical regression protection, 3 fewer M1 docs + M4 reviews. Reserve full M1–M4 for the structural workstreams; W2 + the W5 path-bug fixes run internal-tool mode + a shape-test.

## Auto-decided (mechanical, logged)

| # | Phase | Decision | Principle |
|---|---|---|---|
| 1 | CEO | Skip Design (no UI scope) | — |
| 2 | all | Dual voices → subagent-only (codex down) | P6 |
| 3 | Eng | Split W1→W1a/W1b + state-ownership table first | P5 explicit (correctness) |
| 4 | Eng | Pin resolver cache to cycle id, not PPID | P5 (bug) |
| 5 | Eng | W3 = source _audit.sh + delete 4 inline writers | P4 DRY |
| 6 | Eng | Fix dep graph: W6 depends on W1a AND W3; W1 not independent | P3 |
| 7 | CEO | Defer W4-inert (brief_forge/tokens_est) + W6-DA-hooks to their consumers | P4 (don't dup the sin) |
| 8 | DX | Collapse 6 PRs → 3 themed PRs | P3 pragmatic |
| 9 | CEO | Promote de-gstack to first PR headline | P6 (credibility) |
| 10 | DX | Front-load context-save→dump round-trip = first visible win | P6 bias-to-action |
| 11 | DX/CEO | Split VOTE: 3 explicit (DEC-1/4/5) + 12 confirm-at-gate | P5 |

## Taste decisions (surfaced at gate)

- **T1 — Defer-vs-build the contract-before-consumer work.** Auto-decided: **defer** (P4). But if the operator confirms Brief Forge + DA land *this* v4.0 cycle, building the contracts now is defensible. → folded into the premise question below.
- **T2 — 3 themed PRs vs 6 granular PRs.** Auto-decided: **3** (P3). Operator may prefer 6 for finer rollback granularity.

---

## The premise the whole plan hangs on (CEO — your call)

Two premises, both unanswerable by the models, both reshaping the plan:

1. **Is a second pack (`caip-se`) actually imminent?** If yes → W1a (pack-resolver adoption) is owed now. If packs stay notional (only `_default` exists) → W1a wires an engine for a hypothetical consumer, and should wait. The audit's #1 finding assumes packs are real.
2. **Will Brief Forge + envelope + the DA module land in *this* v4.0 cycle?** If yes → W4-inert + W6-DA contracts are justified ahead of runtime. If no/later → defer them (auto-decided default).

Your answer sets the plan's shape. Everything else is the recommended uplift.

---

## Recommended plan v2 (shape, pending your premise answer)

- **PR-A (meta-infra):** state-ownership table → W5 bugs (**de-gstack headline + save→dump round-trip first**) → W1a pack-config adoption → W1b profile helper. Verifies: first-party-first + 2 broken read-paths fixed; pack/profile state cleanly split.
- **PR-B (mixed):** W2 lessons read-side (internal-tool) + W3 unified audit (meta-infra). Verifies: lessons + override-audit promises flip.
- **PR-C (meta-infra):** W4 substrate (necessity + counts only; brief_forge/tokens_est deferred) + W6 dispatch fixes (DISCOVER directory-scan + orphan wiring; DA hooks deferred to v4.1).
- **Deferred to their consumers:** brief_forge_handoffs frontmatter, tokens_est_typical, DA enforcement hooks, hooks pack-drive (rides W1a).

3 explicit votes remain: **DEC-1** (adopt pack-resolver for pack fields — yes if packs real), **DEC-4** (canonical root `~/.lintel/`), **DEC-5** (de-gstack). The other 12 are confirm-at-gate uplifts.
