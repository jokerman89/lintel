# Lintel — five-lens remediation plan (engineering-reviewed)

**Companion to:** [lintel-five-lens-audit.md](lintel-five-lens-audit.md) (the findings).
**Review:** `/plan-eng-review` — Step 0 scope challenge + Architecture / Code-Quality / Test / Performance, four operator decisions resolved.
**Disciplines carried from the audit:** never remove capability (raise weak to strongest peer) · evidence-cited · the four resolved decisions all chose the complete, capability-preserving option.
**Scope decision:** reviewed as one program (all four phases together), per operator.

---

## Four decisions resolved at review

| # | Decision | Chosen | Consequence |
|---|---|---|---|
| D1 | How do the 7 `PreCommit` module hooks fire? | **Remap to `PreToolUse` matching git-commit** | stays in the one Claude Code hook system; fires on the agent's commits (raw-terminal commits not caught — accepted) |
| D2 | Identity drift: sweep once or guard it? | **Single canonical source + sync test** | a shape test fails CI if any manifest disagrees — can't silently re-drift |
| D3 | Dead `deploy` branch: add capability or remove pretense? | **Make `deploy` a distinct intent** | `classify_intent` emits `deploy` separately; SCOPE override becomes reachable; routing regression test required |
| D4 | Stop Swedish creeping back? | **Add a tripwire CI guard** | permanent CI test blocks Swedish in skills/agents/hooks; small allowlist for legit non-ASCII |

---

## What already exists (reuse, do not rebuild)

- [bin/li-wiki-gen](../../bin/li-wiki-gen) — regenerates showcase + wiki counts. The count-drift fix is *run it*, not *build it*.
- [context-budget/SKILL.md:49-76](../../skills/context-budget/SKILL.md) — the 500k cap logic already exists. Wiring = calling it at a handoff.
- [bin/_audit.sh](../../bin/_audit.sh) — the source-guard + idempotent idiom. The hook stdin shim and `_patterns.sh` copy it; they do not invent a new style.
- `subagent_spawn` convention — orphan-agent wiring is dispatch lines, not machinery.
- [.claude/engineering/audits/lintel-uniformity-REMEDIATION-REVIEW.md](lintel-uniformity-REMEDIATION-REVIEW.md) — precedent already ruled: leverage-first, themed PRs, no contract-before-consumer. This plan inherits it.

## NOT in scope (considered, deferred)

- **Contract-before-consumer work** — Brief Forge / DA-module enforcement contracts ahead of their runtimes. Same rule the prior remediation set; deferred until the consumer exists.
- **pack-resolver adoption (pack-config reads)** — depends on a second pack actually existing; only `_default` does. Out of scope until packs are real.
- **Design-doc Swedish** (`.claude/engineering/design-archive/*`, `.claude/engineering/audits/*`) — lower portability priority than the shipped surface. The tripwire (T2) scopes to skills/agents/hooks first; design docs are a follow-up so the guard doesn't block on a verbatim operator quote.
- **Deeper review-family unification** beyond rubric alignment — the two `*-review` families converge on the 6-dim rubric (T19); a full merge is later.

---

## Implementation tasks

> **Reconciled 2026-06-10 (v4.11):** all 19 tasks shipped in the v4.9 remediation (CHANGELOG 4.9.0)
> but the boxes were never ticked — the exact written-but-never-read drift this plan was about
> (backlog P1-6). Each box below was verified against the tree before ticking: T2/T3/T9/T12/T14
> test files exist, T8 `hooks/shared/_input.sh` + T18 `_patterns.sh` exist, T10 zero `PreCommit`
> events remain, T13 `deploy` intent in `lib/orientator-routing.sh:29`, T16 `$LINTEL_REPO_ROOT`
> in `capture/SKILL.md:64`, T17 `/li:lessons-surface` call in `sense/SKILL.md:47`, T4 zero
> `"operator":"jokerman"` in HOOK.md, T6 SUPERSEDED banner on `session-harness.md`, T7
> li-forge-stats de-claimed, T11 complexity-gated review in `build/SKILL.md` 3c, T5 wiki
> regenerated (again in v4.11). T19's final residual (the budgetwatch fold) completed 2026-06-10.

Synthesized from the review. P1 blocks ship, P2 same-branch, P3 follow-up. Effort as human / CC.

### Phase 1 — hygiene + identity contract

- [x] **T1 (P1, human ~4h / CC ~30min)** — i18n — English sweep of the v3.5–v3.7 cohort
  - Surfaced by: DevEx / hygiene manifest — ~27 skills + 5 frontend agents + `frontend-design-surface` hook + `entropy-secret-check.sh` + `catalog.yml`/`ci.yml` + `.codex-plugin` prompts + `install.sh`. Target dialect = the v4.x modules.
  - Fixing skill `description:` auto-clears `CATALOG.md` Swedish + the `:94` mojibake.
  - Verify: T2 passes; `grep` of the Swedish stopword list across skills/agents/hooks returns zero.
- [x] **T2 (P1, human ~1h / CC ~15min)** — ci — Swedish tripwire CI guard [D4]
  - New `tests/shape/no-swedish.sh`: block `å ä ö` + a Swedish-stopword list across `skills/ agents/ hooks/`; allowlist legit cases. Wire into `ci.yml` + a `verify.sh` subcommand.
  - Verify: passes after T1; fails on a planted Swedish line.
- [x] **T3 (P2, human ~2h / CC ~20min)** — release — identity single-source + sync test [D2]
  - Canonical slug/version/email in one place; `tests/shape/manifest-identity.sh` asserts all 8 manifests + `install.sh` + `.opencode/INSTALL.md` agree. Rename `bin/li-adr-new` `jstack-*`→`li-*`.
  - Verify: shape test green; `grep -r jstack- bin/` returns zero.
- [x] **T4 (P2, human ~1h / CC ~10min)** — docs — parameterize hard-coded paths + operator examples
  - `CLAUDE.md:164`, `README.md:88`, `bin/li-lessons-promote:10`, design doc → `$HOME`/placeholder; `"operator":"jokerman"` in 17 HOOK.md → `"<operator>"`.

### Phase 2 — regenerate the self-description (runs after T1)

- [x] **T5 (P1, human ~30min / CC ~5min)** — wiki — regenerate counts + showcase
  - Run `bin/li-wiki-gen`. **Depends on T1** (CATALOG inherits skill `description:`). Verify: `verify.sh --counts` green; showcase shows 168/65/1, not 192/92/3.
- [x] **T6 (P2, human ~2h / CC ~20min)** — docs — reconcile the fossils
  - README v4.7 vs CHANGELOG v4.6; `session-harness.md` → SUPERSEDED banner (LAYERS.md model) or rewrite; `AGENT-INSTRUCTIONS.md` cycle → add SCOPE + mark pack-modes.
- [x] **T7 (P2, human ~1h / CC ~10min)** — docs — fix doc-vs-code contracts
  - Module-hook names unprefixed→`ta-`/`tq-`/etc. in concept docs; `li-forge-stats` ship-or-de-claim.

### Phase 3 — wire the built-but-unwired

- [x] **T8 (P1, human ~3h / CC ~25min)** — hooks — shared stdin adapter [A1, dual-mode]
  - New `hooks/shared/_input.sh`: read tool payload from **stdin JSON** if present, else fall back to `$1` (keeps manual testing + shape tests working). Source-guard idiom like `_audit.sh`. Update all 30 hooks to source it. Log when extraction fails (no silent null).
  - Verify: T9.
- [x] **T9 (P1 CRITICAL regression, human ~1h / CC ~15min)** — hooks — adapter shape test
  - stdin JSON → correct field extracted; empty stdin → `$1` fallback; malformed JSON → graceful, no crash.
- [x] **T10 (P1, human ~1h / CC ~15min)** — hooks — PreCommit remap [D1]
  - 7 module `HOOK.md` `event: PreCommit` → `PreToolUse` matching Bash + `git commit`. Verify: hooks fire on a simulated git-commit tool call.
- [x] **T11 (P1, human ~2h / CC ~20min)** — cost — wire the 500k cap + gate BUILD review
  - PLAN/CAPTURE invoke the existing `context-budget` check at trio-emit. Gate BUILD's two-stage review by task complexity (mechanical/Haiku leaves → inline, per dispatch rule c). Off-switch already exists. Verify: T12.
- [x] **T12 (P2, human ~45min / CC ~10min)** — cost — cap-fires test
  - trio + warming context > 500k → cap fires at the handoff.
- [x] **T13 (P1, human ~1h / CC ~15min)** — routing — `deploy` as a distinct intent [D3]
  - `lib/orientator-routing.sh:28` emits `deploy` separately, ship arm retained; `scope/SKILL.md:102` branch now reachable. Verify: T14.
- [x] **T14 (P1 CRITICAL regression, human ~45min / CC ~10min)** — routing — intent regression test
  - `"deploy X"`→`deploy`; `"ship X"`→`ship`; smoking-gun `"deploy a website to azure"` still escalates.
- [x] **T15 (P2, human ~3h / CC ~25min)** — dispatch — wire the orphans
  - 6 agents (CustomerEmpathyCheck, PostDemoFollowup, SlideNarrationCritic, DevOpsToolchain, ReadOnly, ResearchSynthesizer) → natural callers; `instruction-parity-check`→CI; `handoff-size-check`→PLAN/CAPTURE.
- [x] **T16 (P2 regression, human ~30min / CC ~5min)** — capture — fix `_audit.sh` source path [Q4]
  - `capture/SKILL.md:61` `$(dirname "$0")`→`$LINTEL_REPO_ROOT`. Verify: calibration write actually lands (it silently no-ops today).
- [x] **T17 (P2, human ~1h / CC ~10min)** — skills — fix lessons-surface invocation + root guard
  - `~/.claude/skills/...` path → `/li:lessons-surface` (multi-CLI); add `LINTEL_REPO_ROOT` fallback guard (peer pattern at `lib/brief-forge.sh:25`).

### Phase 4 — design consolidation (preserve capability)

- [x] **T18 (P2, human ~2h / CC ~20min)** — hooks — extract `_patterns.sh`
  - Dedupe secret + customer-data regexes across 6 hooks into `hooks/shared/_patterns.sh` (source-guard idiom). Keep warn-vs-block tiers; lift the strongest pattern set.
- [x] **T19 (P3, human ~3h / CC ~30min)** — cleanup — the rest of the consolidations
  - One lessons-surface helper (plan/build/review); fold `context-budgetwatch`→`context-budget --watch` (keep alias); align the two `*-review` families to the 6-dim rubric; normalize 4 agents' `cli_support`; `context-warm-*` shared fragment.

---

## Failure modes (per new codepath)

| Codepath | Realistic failure | Test? | Error handling? | Visible? |
|---|---|---|---|---|
| T8 stdin adapter | wrong JSON field path → hooks read null, no-op (same as today, silently) | T9 | **add: log on extraction failure** | currently silent → make it loud |
| T13 routing | `deploy` emitted but nothing downstream routes it → worse than the dead branch | T14 + downstream route check | route table must handle `deploy` | would be silent mis-route |
| T11 cap | counts warming context it shouldn't → fires on legit handoffs (false positive) | T12 | off-switch exists; tune threshold | operator sees a spurious block |
| T16 capture | path fixed but `_audit.sh` contract changed → still no-ops | T16 regression | match peer signature exactly | silent until tested |

**Critical-gap rule:** any failure mode with no test AND no error handling AND silent is a blocker. T8's silent-null is the one that qualifies today → T8 adds a log line, T9 tests it.

## Worktree parallelization

| Lane | Tasks | Modules | Notes |
|---|---|---|---|
| **A — hygiene** | T1 → T2, then T3, T4 | `skills/ agents/ hooks/ install/ tests/shape/` | T2 needs T1 done; T3/T4 independent of T1 |
| **B — hooks** | T8 → T9 → T10 → T18 | `hooks/` | all touch `hooks/` — **sequential within the lane** |
| **C — routing** | T13 → T14 | `lib/ skills/scope/` | self-contained |
| **D — cost/dispatch** | T11 → T12, T15, T16, T17 | `skills/{plan,build,capture}/ lib/` | mostly independent |
| **Post-A** | T5 → T6, T7 | `docs/ showcase` | **T5 depends on T1** (CATALOG regen) |

**Conflict flags:** Lane A and Lane B both touch `hooks/` (A edits hook *text* for Swedish, B edits hook *plumbing*) — run A's hook-text sweep before B's plumbing, or coordinate. Lane A (T1) and Post-A (T5) are ordered: never regen counts before the sweep.

**Launch:** A + C + D in parallel worktrees. B after A's hook-text edits land. Post-A regen last.

---

## Completion summary

- Step 0 scope challenge — reviewed as one program (operator choice); complexity gate fired and was answered
- Architecture review — 5 findings (2 → decisions D1/D2, 3 folded)
- Code quality review — 4 findings (1 → decision D3, 3 mandated/folded)
- Test review — coverage diagram produced, 11 gaps, **4 CRITICAL regression tests** mandated (T9, T14, T16, + T2 tripwire)
- Performance review — no issues (markdown/bash harness; cost axis covered in the audit)
- NOT in scope — written (4 items)
- What already exists — written (5 reuse points)
- Failure modes — 4 mapped, 1 critical-gap closed by T8+T9
- Parallelization — 5 lanes, 3 parallel + 2 ordered
- Decisions resolved — 4/4, all chose the complete capability-preserving option

**Verdict:** plan is engineering-sound with the four decisions applied. 19 tasks, 4 CRITICAL regression tests, no capability removed. Ready to implement when the operator chooses to pick up a lane.
