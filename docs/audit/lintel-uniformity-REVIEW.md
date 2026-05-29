# /autoplan review — Lintel uniformity audit methodology

**Reviewed:** 2026-05-29 · branch `v4.0-phase1-meta-infra-spine`
**Plan under review:** [lintel-uniformity-audit-prompt.md](lintel-uniformity-audit-prompt.md)
**Pipeline:** CEO → (Design skipped, no UI scope) → Eng → DX. Voices: Claude subagent only (`codex` unavailable on this host → `[subagent-only]`).
**Restore point:** `docs/audit/.restore-v4.0-phase1-meta-infra-spine-20260529-183430.md`

> One-line verdict: the audit asks the right questions but ships the wrong artifact. All three independent voices, with no shared context, converged on the same reframe — make uniformity a **machine-checked contract**, not a one-time hand-written register. The 14 dimensions and the no-cut motto survive intact; only the deliverable changes.

---

## Consensus table (CEO / Eng / DX)

| Dimension | CEO | Eng | DX | Consensus |
|---|---|---|---|---|
| Is a one-time findings register the right deliverable? | NO | NO | NO | **DISAGREE w/ plan — unanimous** |
| Should D1–D14 become a frontmatter contract + shape-test? | YES | YES | YES | **CONFIRMED** |
| Audit unbuilt features (D7/D9/envelope/wiki) per-component? | NO (noise) | NO (noise) | NO (noise) | **CONFIRMED — audit the contract, track adoption %** |
| "Strongest peer sets the bar" as written? | needs per-kind target | per-kind **floor**, not max | keep no-cut, floor not max | **DISAGREE w/ plan — use per-kind floor** |
| Cohort axis = component-type? | dimension is the better axis | matrices first, then gaps | filter by domain/dim | **DISAGREE w/ plan — invert** |
| 240×14 hand-authored YAML records? | over-scoped | write-only, can't diff | ~23k lines, nobody reads | **CONFIRMED — generate, don't hand-write** |

No cross-phase disagreement. This is the strongest possible signal: three blind reviewers, one conclusion.

---

## USER CHALLENGE (never auto-decided — your call)

**What you said:** Run an 8-cohort manual audit producing ~3360 per-component YAML finding records across 14 dimensions, plus a hand-curated top-20 and a markdown vote register.

**What all models recommend:** Keep the 14 dimensions and the *kraftfullt-från-start-ständigt-evolverande* motto. Replace the static register with a **uniformity-as-contract** pipeline:

```
 frontmatter `uniformity:` block            ← each component DECLARES its D-fields
 (per-kind: skill=all 14, read-only hook=D1/D3/D12/D13, agent=D1/D2/D3/D10/D11, …)
        │
        ▼
 tests/shape/uniformity-coverage.sh         ← Gate-M3 shape-test #9 (the 9th sibling
 (mechanical: presence + per-kind floor)      of the 8 that already exist)
        │  exits ≠0 only when a component is BELOW its kind-floor
        ▼
 docs/audit/uniformity-matrix.md            ← regenerated + idempotent like CATALOG.md;
 (X1 + X4 auto-generated, adoption% over time)  unbuilt-feature adoption ratchets 0→N
        │
        ▼
 HUMAN AUDIT runs ONLY on flagged below-floor cells   ← senior judgment spent where
        │                                               it's irreducible, not on 26k cells
        ▼
 /li:uniformity vote flow (AskUserQuestion, ranked batches of 3–5) → backlog
```

**Why (the models' reasoning):**
- The repo *already* enforces shape at SHIP via meta-infra **Gate M3**, *already* lints per-kind frontmatter (`tests/shape/frontmatter-lint-all.sh`), *already* regenerates idempotent catalogs (`CATALOG.md` + CI), and *already* has a grep/jq audit writer (`bin/_audit.sh`). The manual register reinvents all of it as dead text.
- The manual audit and the shape-test produce the **same X1 matrix** — one is computed every PR and blocks regression, the other is typed once and rots. *Ständigt evolverande* literally means the former.
- Components already self-document most dimensions as named sections today (e.g. `skills/migrations/SKILL.md` has Inputs=D1, Status protocol=D2, Failure recovery=D6, Integration Reads/Writes=D13). The dimensions are latent frontmatter waiting to be declared.

**What we might be missing (blind spots):** A one-time narrative audit has real value the contract doesn't capture — it reads *bodies* and catches *qualitative* drift (a recovery path that exists but is wrong; a failure mode that's inconsistent in spirit, not in field-presence). The contract checks presence + floor; it does not check whether the declared value is *good*. If your real goal was the qualitative read, the contract is necessary-but-not-sufficient.

**If we're wrong, the cost is:** You skip a deep one-pass narrative review and a latent qualitative defect ships because the shape-test only saw a present field, not a bad one. Mitigation: the human-audit step still runs — only scoped to flagged cells instead of all 240, so the qualitative read survives where it adds value.

**Your original direction is the default.** It does not change unless you pick it below.

---

## Taste decisions (auto-decided per the 6 principles; override at the gate)

- **T1 — Per-kind floor vs global max as "the bar."** Auto-decided: **per-kind floor** (P5 explicit, and it resolves the conflict with the repo-wide Subtraction-Bias protocol — "always match the deepest peer" can ratchet every hook toward bloat). Above-floor depth stays allowed, never mandated.
- **T2 — Three-level trace (nano/macro/high) on every cell vs only on real findings.** Auto-decided: **only on flagged/votable findings** (P3 pragmatic — macro/high are derivable from cohort; full trace ×3360 is the single biggest bloat driver).
- **T3 — Cohort axis.** Auto-decided: keep cohorts as the *parallelization unit* (subagent-per-cohort is sound) but generate the dimension matrix *first* and run human judgment only on gaps it reveals (P1 completeness + P3 — inverts the plan's post-hoc X-checks into machine inputs).

## Auto-decided (mechanical, no disagreement)

| # | Phase | Decision | Principle | Rationale |
|---|---|---|---|---|
| 1 | CEO | Skip Design phase | — | No UI scope; audit reviews design *skills* but builds no UI |
| 2 | all | Run dual voices | P6 | Codex unavailable → `[subagent-only]`, proceeded |
| 3 | Eng | Don't hand-audit D8 (frontmatter) | P4 DRY | `frontmatter-lint-all.sh` already checks it mechanically |
| 4 | Eng | Unbuilt dims → 1 architecture-level finding + adoption counter, not 240 cells | P3 | 240 identical "absent" cells = noise, not signal |
| 5 | DX | Vote flow = AskUserQuestion batches, not flat .md | P5 | 330 markdown votes get abandoned ~15 in; ship after first batch |
| 6 | CEO | Never recommend removal | operator motto | Uplift-only honored throughout |

---

## Scores

- **CEO** (strategy/scope): premises P1/P3/P5 challenged as the load-bearing flaws; central contradiction = "ständigt evolverande" motto vs a point-in-time register. Scope ~26,000 cells hand-read, badly under the plan's own 30k-token/cohort cap.
- **Eng** (architecture): 6 findings; strongest = encode D1–D14 as per-kind contract + `uniformity-coverage.sh` (Gate M3 #9) + regenerated matrix. Grounded on real files (shape-tests, meta-infra-discipline, pack-resolver).
- **DX** (operator experience): central risk = ~23k lines of YAML is write-only; TTHW from "audit done" → "first uplift shipped" is days, gated on a voting marathon. Reframe = regenerable `/li:uniformity` dashboard surfacing only below-floor findings.
- **Cross-phase theme:** "the manual register decays; the repo already has the CI machinery to make uniformity continuous" — surfaced independently in all three phases. High-confidence signal.

---

## If you approve the reframe — concrete next deliverable (replaces 8 cohort files)

1. `docs/audit/uniformity-contract.md` — the per-(kind × dimension) target table + the `uniformity:` frontmatter schema (which of D1–D14 each kind must declare, which are N/A-with-reason).
2. `tests/shape/uniformity-coverage.sh` — Gate-M3 test #9: per-kind floor check, exits ≠0 only on below-floor.
3. `docs/audit/uniformity-matrix.md` — regenerated, idempotent (sibling of `catalog-regenerates-clean.sh`); component × dimension, adoption % per unbuilt feature.
4. `skills/uniformity/SKILL.md` (`/li:uniformity`) — runs the test, surfaces only below-floor findings, drives the ranked AskUserQuestion vote flow, writes decisions to `~/.lintel/audit/uniformity.jsonl` via `bin/_audit.sh`.
5. Human-audit pass scoped to flagged cells only → backlog. Two irreducibly-human inputs remain: (a) define the per-kind target depth, (b) rank the uplift backlog.

This is itself a **meta-infra** change (touches `tests/shape/`, adds a frontmatter contract across all skills/agents) → ships under Gate M1–M4 per the v4.0 discipline.

---

## Gate resolution (2026-05-29)

**Operator decision: keep the original direction — run the manual 8-cohort audit as specified.** User Challenge resolved in favor of the operator's stated spec. The model consensus (reframe to uniformity-as-contract) is recorded above as an advisory, not adopted. The operator holds context the models lack; the manual audit proceeds per the plan's own protocol.

The reframe is not discarded — it is parked as a candidate for *after* the manual pass surfaces real gaps (the contract can then encode what the audit found, turning the one-time register into the continuous check without guessing the schema up front). Logged here so it isn't re-litigated.

**Status:** Plan stands as written. Audit ready to execute cohort-by-cohort (Cohort 1 = phase-core skills), checkpoint + commit after each, per the plan's token-budget protocol.
