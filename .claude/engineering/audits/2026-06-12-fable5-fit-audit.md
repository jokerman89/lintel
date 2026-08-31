# Lintel × Claude Code (Fable 5) — end-to-end fit audit

> Research-dive 2026-06-12, operator-requested ("ax till limpa"). Three tracks: mechanical
> health pass · skill-surface elegance metrics · wired-vs-shipped reality. Plus a first-person
> assessment by the agent operating inside the harness. Assessment only — no fixes applied.

## Verdict in one paragraph

The code that exists works (suite 74/74, helpers green, repo migrated, doctor clean) and the
*disciplines* genuinely run — but they run because the model reads prose and complies on
substance, not because the machinery fires. Measured against "is Lintel doing what it was
designed to do": **roughly 3 of ~14 mechanism families actually execute in real sessions**
(the 4 safety hooks, the pack-resolver fallback, the new vault sink). The cycle state machine,
jobs system, session digest, brief-forge envelopes, granularity calibration and memory-budget
hook have never fired on this machine — same root cause five ways: activation is a manual step
nobody took (or a wrong path), and the tests assert that prose exists rather than that
behavior happened. Separately, ~30-38% of the 27k-line skill surface is per-skill template
ceremony; the same capability fits in ~60% of the current size.

## Track 1 — mechanical health (PASS)

- Suite 74/74, rc=0 on the committed tree.
- lib/paths.sh · lib/memory.sh · bin/_context.sh self-tests green; lessons surfacing returns
  relevant results against the real corpus.
- li-doctor: repo scaffolded, v5 layout, auto-memory converged.
- The 4 safety hooks are registered and have real BLOCK records — genuinely live.

## Track 2 — surface elegance (metrics)

166 skills / 27,061 lines (median 134, max 483 = plan); 70 agents / 7,235 lines (uniform, slim).

| Finding | Size |
|---|---|
| Per-skill protocol ceremony (status enums, hop-in, voice, pause-points…) restated 110-166× | ~5.4-8.2k lines (20-30%) |
| 35 engineering sub-skills with exactly ONE caller each (their module) | ~4,400 lines (16%) |
| Skills with ≤1 inbound command reference | 27 (16%) — incl. gbrain-setup/sync at 0 |
| Agent fleet wired | 69/70 (orphan: WorkshopFacilitator) |
| Spine (top-20 central skills) | only 19-20% of lines — healthy concentration |

Scores: pack system **5/5** (define-once, ~30 consumers) · cycle spine **4/5** (version-history
prose accreted into instructions) · generate **4/5** (honest stubs) · context **3/5** ·
frontend **3/5** · engineering modules **2.5/5** (5×8 symmetry is for show — nobody
solo-invokes the sub-skills) · role system **2/5** (7 slash commands for CRUD).

## Track 3 — wired vs shipped (the uncomfortable one)

| Mechanism | Fires in real sessions? | Why not |
|---|---|---|
| 4 safety hooks | **YES** | registered in ~/.claude/settings.json |
| Pack resolver | **YES** (fallback) | but profile.yaml + ~/.lintel/packs MISSING — every session has silently run `_default` |
| Capture vault sink | **YES** | new; but unit tests had polluted the prod audit file |
| session-digest (ADR-0002) | never | no SessionStart registration; merge snippet has a WRONG path (missing `shared/`); plugin ships no hooks auto-registration |
| Cycle state machine (00-state, build-log, review-reports) | **never — zero files on the whole machine** | prose obligation, nothing enforces it; the v5 cycle shipped 3 ADRs without writing one state entry |
| Jobs system + registry | never | workflow_root spawning never executed |
| Brief forge envelopes | never | shape test greps for the WORD "envelope" → green forever |
| Granularity calibration | never | CAPTURE never wrote a record; estimator always on default prior |
| memory-budget-warn | never | not even installed to ~/.lintel/hooks |
| 20+ module warn-hooks | never | installed, registered nowhere |
| Per-CLI shims | broken-by-staleness | still point at tasks/* post-v5 (stubs, not content) |

Other findings: plugin.json still says 4.9.0; ~/.lintel/sessions contains only pack caches.

## The big miss

**Lintel has no closed loop between shipped and used.** Nothing measures whether a mechanism
fires, nothing prunes what nothing references, the activation step is manual and silently
skippable, and the tests verify documentation instead of behavior. The factory applies
verification discipline to every product EXCEPT itself-as-runtime. Everything above is one
instance of this single gap.

## First-person: the agent's reality (Fable 5)

What genuinely helps: lessons.md (changed concrete behavior multiple times in one session),
the independent-review mandate (caught P1s in all three v5 phases), shape tests as tripwires,
operator gates at real decision points, deterministic bash helpers. What is noise: 60+ lines
of ceremony per skill that the model never needs, state-write obligations with no in-session
reader, single-caller sub-skill files instead of dispatch tables, orchestrator prose that
restates default behavior. The harness's value concentrates precisely where it is mechanical
or knowledge-bearing; it thins where it is ceremonial.

## Recommended order (sky-is-the-limit, but start grounded)

1. **P0 — activation pass:** ship hook auto-registration with the plugin (hooks.json) so
   digest + safety + budget hooks wire on install; fix the snippet path; install
   memory-budget-warn; regenerate stale shims; bump plugin version; seed profile.yaml/packs
   at install; hermetic-guard the audit files against test pollution.
2. **P0 — behavior over prose:** convert the key shape tests into behavior tests (hermetic
   sandbox session must leave digest/state/audit traces); add a one-command `state_append`
   helper so the per-phase state write costs one line — or delete the obligation honestly.
3. **P1 — subtraction release:** protocol ceremony → frontmatter fields + ONE canonical
   protocol doc (-5-8k lines); engineering sub-skills → per-module dispatch tables (-4.4k);
   prune 0-ref skills; role family 7→3. Target: same capability at ~60% size.
4. **P2 — compounding upgrades:** `memory: project` on reviewer agents (reviewers that
   remember per-repo findings); usage-report → quarterly subtraction ritual; BUILD fan-out via
   parallel subagents; wire CAPTURE's granularity record so the estimator finally calibrates;
   a small eval set (same task with/without harness pieces) so tuning gets evidence.
