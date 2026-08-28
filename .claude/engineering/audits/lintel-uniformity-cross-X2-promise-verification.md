# Cross-cutting pass X2 — promise verification

**Pass:** X2 of 5 (per `.claude/engineering/audits/lintel-uniformity-audit-prompt.md` §"Cross-component checks")
**Date:** 2026-05-29
**Branch:** v4.0-phase1-meta-infra-spine (mid v4.0 reframe, Phase 1 of 3)
**Method:** for each architectural promise the framework makes, cross-reference all 8 cohort findings + design doc + AGENT-INSTRUCTIONS + direct file checks. Verdict per promise: UPHELD / PARTIALLY-UPHELD / BROKEN / DESIGNED-NOT-BUILT.
**Inputs:** cohorts 1-8 findings files; `.claude/engineering/design-archive/lintel-v4.0-reframe-design.md`; `AGENT-INSTRUCTIONS.md`; spot-checks of `skills/plan/SKILL.md`, `tests/shape/workflow-root-has-navigation.sh`, `lib/pack-resolver.sh`.

A promise is a claim the framework makes about itself — in design docs, in CLAUDE.md, in the motto (*kraftfullt från start, ständigt evolverande, lär sig och växer ihop med operatören och repot*). X2 asks the single question: **is the promise upheld by every component that should uphold it?** Not "does the mechanism exist" but "does it fire everywhere it claims to."

Verdict vocabulary:
- **UPHELD** — mechanism exists and every component that should uphold it does.
- **PARTIALLY-UPHELD** — mechanism exists and fires in some places it should, but not all (uneven adoption).
- **BROKEN** — mechanism exists (built) but the promise it makes is contradicted in practice (e.g. a producer/consumer contract that does not match; a built interface with zero consumers; a claim that is false).
- **DESIGNED-NOT-BUILT** — the promise is in the design but the mechanism does not yet exist; correct for the current phase, tracked, not a regression.

---

## Promise scorecard

| # | Promise | Verdict | Should-uphold count | Actually-upholds |
|---|---------|---------|--------------------|------------------|
| 1 | Cross-session memory via lessons (written AND consulted) | **PARTIALLY-UPHELD** | write-side + read-side across all phases/agents | write-side strong; read-side ~3 of ~30 sites |
| 2 | Pack-driven behavior (active pack changes behavior) | **BROKEN** | resolver + ~30 declared consumers | 0 consumers (resolver has zero callers) |
| 3 | Jobs visibility (every workflow_root participates; /li:status sees in-flight) | **PARTIALLY-UPHELD** | 8 phase skills + composites | 2 declare workflow_root (cycle, plan) |
| 4 | Brief Forge at hand-offs | **DESIGNED-NOT-BUILT** | all moments 1/2/4/5 (~25+ hand-offs) | 0 (lib/brief-forge unbuilt) |
| 5 | Knowledge tag-funnel (knowhow consulted) | **DESIGNED-NOT-BUILT** | DISCOVER/DEFINE/PLAN/REVIEW | 0 (no helper, no schema, no reader) |
| 6 | 500k handoff cap (enforced at plan/build handoffs) | **PARTIALLY-UPHELD** | every cold-executor hand-off | cap logic exists in context-budget; not called at handoffs |
| 7 | Mandatory pause at PLAN approval (founder gate) | **UPHELD** | PLAN (+ its callers) | PLAN built, gate MANDATORY, BLOCKED-on-3x-reject |
| 8 | Navigation mandatory on workflow_root (v4.0) | **DESIGNED-NOT-BUILT** | every workflow_root skill (cycle, plan) | 0 declare navigation; shape test is Phase-1 WARN-only |
| 9 | Override-with-audit (every gate has --override + audit; audit consumed) | **PARTIALLY-UPHELD** | all gates/hooks | override+audit present; two divergent writers; highest-stakes overrides bypass unified trail; some audits write-only |
| 10 | First-party-first (no gstack/3P binary on execution path) | **BROKEN** | all execution-path skills | 4+ planner skills + design-review call `~/.claude/skills/gstack/bin/*` on the path |

**Counts: UPHELD 1 · PARTIALLY-UPHELD 4 · BROKEN 2 · DESIGNED-NOT-BUILT 3.**

---

## Per-promise verification

### Promise 1 — Cross-session memory via lessons (written AND consulted)

**Verdict: PARTIALLY-UPHELD.**

**The claim.** The motto's operator-relation thread: lessons accumulate AND are consulted, growing the system with the operator (X3). CLAUDE.md self-improvement loop: "record the pattern in lessons.md … Review lessons.md at session start."

**Evidence — write side is strong.**
- CAPTURE writes lessons and promotes them globally — "BAR for lessons-WRITE side" (cohort 1, capture D10, finding line 221).
- `bin/li-lessons-promote` / `li-lessons-sync` exist (cohort 8 bin inventory).
- role-update writes role learnings back into the role file (cohort 7, role-update D10).

**Evidence — read side is the gap.**
- "Lessons are write-only across the execution phases. CAPTURE writes lessons … but PLAN, BUILD, REVIEW, SHIP never read them. The marquee example: a captured lesson like 'don't mock Azure SDK' never reaches the BUILD implementer subagent." (cohort 1 top finding 1; build D10 line 149; review D10 line 173; ship D10 line 197; plan D10 line 125). SENSE is the one phase that consults (Step 0a lessons-surface, line 53).
- Planner sub-chain: "NO component consults lessons.md/knowhow — including the three skills where memory would compound most (office-hours premises, ceo-review founder-signal synthesis, devex TTHW trend)." (cohort 2 top finding 3; office-hours D10 line 113).
- Agents: consultation "uneven … Architect and CodeReviewer read 'recent ADRs' … The majority of agents do NOT consult lessons.md" (cohort 4 D10 line 210).
- role-activate does not read the role lessons that role-update writes — "the write side exists, the read side doesn't close the loop" (cohort 7, role-activate D10 line 119).
- Hand-off cohort: context-save captures "failed attempts" inline but never promotes to lessons.md (cohort 3, context-save D10 line 209).

**Gap.** The producer half of the loop is built and exemplary; the consumer half fires at ~3 of ~30 relevant sites (SENSE, DISCOVER partial, role-update write-only). The promise is half a loop. **Uplift (per cohorts):** feed relevant lessons into BUILD's implementer brief, REVIEW Step 1, SHIP Step 2, PLAN's hotfix path, and the planner context-load steps.

---

### Promise 2 — Pack-driven behavior (active pack changes behavior)

**Verdict: BROKEN.**

**The claim.** v4.0 design's central thesis: "the pack is the single source of identity-bound state" (cohort 7 summary). `lib/pack-resolver.sh:2` documents itself as "a critical-path interface used by 30+ skills."

**Evidence — the interface is built and tested, with zero consumers.**
- "Grep of `skills/` for `pack-resolver`, `resolve_pack_field`, `pack_field_is_true`, `get_loaded_pack`, `get_active_pack_name`, `source.*pack-resolver`, `lib/pack-resolver` returns **zero matches**. Grep of `skills/` for `pack.yaml` or `active-pack` also returns **zero matches**." (cohort 7, C7-PACK-RESOLVER-ZERO-CONSUMERS, line 334-342). Confirmed by direct check: the resolver's only references are itself, its two test files, `bin/_audit.sh`, and design docs.
- The "30+ skills" header is "a forward-looking design assertion, not a description of today" (cohort 7 line 342).

**Evidence — consumers use the OLD path instead, against a DIFFERENT file.**
- WorkProfile lives in two schemas: NEW `packs/_default/pack.yaml:23 compliance.workprofile_default` and OLD `~/.lintel/profile.yaml workprofile:`. "No skill reads `compliance.workprofile_default`." All 12 WorkProfile consumers grep profile.yaml directly (cohort 7, C7-WORKPROFILE-DUAL-LOCATION, line 360-373; sense:122, context-warm-from-url:43, compliance-gate:155).
- All 8 role skills hardcode the role-path triple and ignore pack `roles.source`/`roles.default_role` (cohort 7, C7-ROLE-PACK-BLINDNESS, line 417).
- Hooks: "ZERO hooks reference any of `pack`, `compliance.hooks`, `pack-resolver`, `WorkProfile`. No hook resolves an active pack." 9/19 hooks inline MS/Sweden/Trailblazer data that the pack model says belongs in `pack.compliance.*`/`pack.voice.*` (cohort 5 D7 verdict, line 59).
- Agents: "the active pack does NOT bias which agents are recommended. An ms-specific pack and a generic-OSS pack get the same agent recommendations." (cohort 4 D7 line 150).
- Phase skills: "No phase reads a pack manifest. SENSE Step 0c hardcodes meta-infra detection rather than resolving a pack." (cohort 1 designed-not-built note line 19).

**Why BROKEN, not DESIGNED-NOT-BUILT.** The resolver IS built and tested. The promise it embodies ("active pack changes behavior") is contradicted in practice: the canonical value was migrated into the pack + resolver but never propagated to consumers, and there are two parallel state-resolution patterns resolving different files for the same logical value. A built, well-tested, zero-consumer critical-path interface is a broken promise, not an unbuilt one. Working precedents exist that should anchor the wiring: WorkProfile-branching in REVIEW/SHIP Stage-3 gates, cycle's mode-presets (proto-packs), context-warm-customer's WorkProfile sensitivity gate (cohort 1 line 377; cohort 3 line 524).

---

### Promise 3 — Jobs visibility (every workflow_root participates; /li:status sees in-flight work)

**Verdict: PARTIALLY-UPHELD.**

**The claim.** `docs/concepts/jobs-system.md`: jobs are "the single source of truth for flows in flight"; `/li:status` shows "what's open right now."

**Evidence — built and works for the 2 root flows.**
- Jobs system is BUILT (v3.8): `bin/_jobs.sh`, 3 job-* hooks, `skills/jobs`, `skills/status`, concept doc (cohort 8 L1, line 61-74).
- PLAN is "the one phase-core skill that fully participates in jobs" — declares `workflow_root: true`, job-begin spawns `~/.lintel/jobs/plan-<stamp>-<hash>/` (cohort 8 footnote 5, plan/SKILL.md:4).

**Evidence — adoption is concentrated, not cross-cutting.**
- "Only 2 skills (cycle, plan) declare workflow_root. The 8 phase-core skills do NOT individually participate; a solo /li:sense or /li:build leaves no job trace." (cohort 8 L1 D4 line 76-81).
- "SENSE is the canonical session entry yet doesn't itself read `_active.md`" (cohort 8 footnote 1).
- The 4 composite entry-points (fix, research, plan-and-build, review-and-ship) lack workflow_root — "operator can't distinguish /li:fix invocation from /li:cycle --mode hotfix in logs" (cohort 1, fix D8 line 273, composites note line 259).
- job-begin "fires PreToolUse but is opt-in via manual symlink … so default installs get zero job tracking" (cohort 8 L1 line 81).
- `blocked_until` is sold as "a mechanical gate. BUILD literally cannot start" but `_jobs.sh job_update` does not evaluate it — advisory only (cohort 8 L1 D5 line 84-89).

**Gap.** The participation model is "neither (a) nested-only nor (b) per-skill — ambiguous" (cohort 8 L1 proposed). A solo `/li:sense` or `/li:build` is invisible to `/li:status`. The promise holds for cycle/plan flows; it does not hold for solo phase invocations or composites. **Operator decision needed:** nested-only vs per-skill job-touch (cohort 8 decision table).

---

### Promise 4 — Brief Forge at hand-offs

**Verdict: DESIGNED-NOT-BUILT.**

**The claim.** Every hand-off (skill→subagent, phase→phase, workflow→cold-executor, operator→skill) goes through Brief Forge curate→evaluate→envelope; design doc acceptance: "Every hand-off in cycle/plan/build/ship/capture runs through Brief Forge" (design line 914). Canonical field `brief_forge_handoffs:` asserted by `tests/shape/brief-forge-handoffs-canonical.sh`.

**Evidence — unbuilt, correctly phased.**
- `lib/brief-forge/` ships Phase 3 (design line 836-840, 979). Not built today.
- "None of the 18 [hand-off skills] fire Brief Forge — it is designed-not-built … Every save and every restore in this cohort is an un-gated cold-executor hand-off. That is the central finding of the cohort." (cohort 3 scope, line 30-34).
- "Zero of the 18 declare [`brief_forge_handoffs:`]." (cohort 3 CF-3, line 90).
- "No agent fires Brief Forge at its boundaries." (cohort 4 D9 line 190). "Brief Forge fires in no engineering domain" (cohort 6 C6-F4).
- Appears in ZERO phase skills (cohort 1 line 20); pack.yaml declares `brief_forge on_subagent_spawn enabled` (cohort 7, role-activate D9 line 116) but nothing invokes it.

**Why DESIGNED-NOT-BUILT, not BROKEN.** It is on-schedule Phase-3 work; the contract (field name, the five hand-off moments, the curate/evaluate/envelope mechanic) is coherent and ahead of implementation. **Readiness signal (per cohorts):** the highest-value first call sites are pair-agent + codex (moment 1, most-built proto-gates — cohort 3 line 752, 798), autoplan's step-8 aggregation (cohort 2 "#1 Brief Forge integration point"), context-save/restore (moment 4), and BUILD's implementer-brief (the de-facto Brief-Forge payload — cohort 1 line 148). Several proto-evaluators already exist (customer-PII scans, domain allowlists, context-ignore lists) that should be formalized as named evaluators rather than reinvented (cohort 3 line 882).

---

### Promise 5 — Knowledge tag-funnel (knowhow consulted)

**Verdict: DESIGNED-NOT-BUILT.**

**The claim.** The repo-relation thread: knowhow grows and is consulted (X3). Pack declares a `knowhow:` block.

**Evidence — least-specified of all cross-cutting layers.**
- "DESIGNED-NOT-BUILT … contract is a single nullable pack field (`packs/_default/pack.yaml:41 source: null`). No entry schema, no tag taxonomy, no lookup helper … knowhow is the least-specified of all 6 layers." (cohort 8 L2, line 104-118).
- "No phase-core skill references `knowhow` or the tag-funnel anywhere." (cohort 8 footnote 2). "0/8 phase skills."
- DISCOVER reads `tasks/lessons.md` but never the pack knowhow base — "the two knowledge channels are not unified" (cohort 8 footnote 2; line 124).

**Why DESIGNED-NOT-BUILT.** Unlike pack-resolver (Promise 2), nothing is built here at all — no helper, no schema, no reader. It is below even the floor of an unbuilt-but-contracted layer. **Uplift (per cohort 8):** write a `bin/_knowhow.sh` lookup helper + entry schema mirroring `_jobs.sh`, then wire DISCOVER as first consumer, unifying it with the lessons channel. This sits structurally adjacent to Promise 1's read-side gap — both are the "consulted, not just written" half of the motto's two learning threads.

---

### Promise 6 — 500k handoff cap (enforced at plan/build handoffs)

**Verdict: PARTIALLY-UPHELD.**

**The claim.** Cold-executor hand-offs are size-capped (500k soft / 750k hard for customer-engagement; 600k/900k recommended for meta-infra — design line 896, C4-D1). The cap protects the cold-executor from oversized briefs.

**Evidence — the cap logic exists but is not wired to the hand-off points.**
- `context-budget` "already implements the handoff-size logic Brief Forge envelopes need … it ENFORCES the 500k soft / 750k hard handoff cap (context-budget:49-76)." (cohort 3, context-budget D9 line 644-649).
- But it is a manual/on-demand skill — nothing calls it at the actual hand-off boundaries (PLAN→BUILD trio emission, context-save, the envelope emit). "Brief Forge calls context-budget's cap logic at every envelope emit; don't duplicate the cap math" is the proposed wiring (cohort 3 line 649) — i.e. it is not wired today.
- The envelope (the standardized payload the cap should gate) is itself DESIGNED-NOT-BUILT (cohort 8 L4) — so there is no single hand-off object to cap at workflow_root. PLAN→BUILD is the plan/spec/prompt trio (file-path convention), not a size-checked envelope (cohort 1 line 20; cohort 8 footnote 3).
- `context-budgetwatch` provides GREEN/YELLOW/RED + CI exit codes (cohort 3 line 669) but watches the live session budget, not hand-off payload size; possible duplication with the `li-token-watcher` hook (cohort 3 D4 line 676).

**Gap.** The cap is implemented (the math exists in context-budget) but enforced only when an operator manually runs the skill — not mechanically at plan/build hand-offs. It becomes a real enforcement point only when (a) the envelope lands (Phase 2) and (b) Brief Forge calls the existing cap logic at emit (Phase 3). Today the promise is "capable but not wired." Marked PARTIALLY-UPHELD because the enforcement primitive genuinely exists and is correct; the binding to hand-off sites is missing.

---

### Promise 7 — Mandatory pause at PLAN approval (founder approval gate)

**Verdict: UPHELD.**

**The claim.** AGENT-INSTRUCTIONS line 185: "Founder approval gate at end of PLAN (MANDATORY pause)." CLAUDE.md (global): "Mandatory pause at PLAN approval." Personal protocol: "I am sole decision-maker on strategic matters."

**Evidence — built, mandatory, with a bounded reject path.**
- `skills/plan/SKILL.md:159` Step 10 "Founder approval gate (MANDATORY PAUSE)"; `:288` Pause-points (MANDATORY); `:294` "After full plan + reviews → AskUserQuestion founder approval gate"; frontmatter description names it (`:5`).
- The gate is enforced as a failure mode: "Plan finalized without founder gate — gate is MANDATORY per Architect image pattern" (plan:344); and bounded: "Operator rejects 3x at founder gate: status BLOCKED, save state … don't loop indefinitely" (plan:351).
- Cohort 1 ranks PLAN as the strongest peer with "two MANDATORY gates" (cost-estimate + founder approval) (line 29, plan D2 line 117).
- The pause offers explicit options including "C) PAUSE — save state for later" (plan:165) — operator-choice, not auto-proceed.

**Why UPHELD.** This is the one promise where the mechanism exists AND every component that should uphold it does. PLAN is the only component that owns this gate, it is built, mandatory, and consistently enforced including the standalone-module invocation path. The single minor caveat is that PLAN lacks a declared `necessity:` field (implicit in prose — cohort 1 D14 line 129), which is a frontmatter-uniformity nit (X5), not a hole in the gate itself.

---

### Promise 8 — Navigation mandatory on workflow_root (v4.0)

**Verdict: DESIGNED-NOT-BUILT.**

**The claim.** Design doc, repeated: "Mandatory `navigation:` block on every `workflow_root: true` skill" (line 121); "A `workflow_root: true` skill without `navigation:` block is rejected at load. The architectural guarantee holds." (line 913); "Navigation and brief_forge_handoffs are mandatory, not optional" (line 1002).

**Evidence — unbuilt; enforcement is deferred and currently WARN-only.**
- Direct check: grep `navigation:` across `skills/` returns **zero files**. Neither workflow_root skill (cycle, plan) declares it. Confirmed `skills/plan/SKILL.md` has no `navigation:` block.
- The shape test exists but is deliberately non-blocking in Phase 1: "Phase 1 enforcement is documentation-only … For Phase 1 we surface MISSING navigation as WARNING, not FAIL … Phase 2 spine-load enforcement will reject these." (`tests/shape/workflow-root-has-navigation.sh:28-44`).
- Cohort 1 flags it: plan D8 "declares workflow_root but NOT … navigation … master prompt D8 says workflow_root must declare navigation" (line 123); cycle "no necessity/navigation" (line 245).
- Schedule: navigation ships Phase 3 with Brief Forge + wiki (design line 836).

**Why DESIGNED-NOT-BUILT.** The guarantee is designed, the shape test scaffolding is in place, and the rejection-at-load enforcement is explicitly scheduled for Phase 2/3. It is on-schedule, not a regression. **Risk (per cohort 8 + design line 95):** "Without navigation, workflow_root declarations are advisory" — until enforcement fires, the navigation guarantee is documentation. The orientator agent that navigation depends on (design line 50) is likewise pending.

---

### Promise 9 — Override-with-audit (every gate has --override + audit; audit consumed)

**Verdict: PARTIALLY-UPHELD.**

**The claim.** Design Chapter 1.C: "Every gate ships with `--override` + audit … Defense through transparency, not blocking. Override-with-audit is the pattern. Trust the operator." (design line 85, 1000-1005). The audit must be CONSUMED, not just written.

**Evidence — override + audit present for hooks; consumption partly closed.**
- Both justified-block hooks have override env-var recovery paths (secret-scan-block: `LINTEL_OVERRIDE_SECRET=1`; customer-data-block: `LINTEL_OVERRIDE_CUSTOMER_DATA=1`) and log both block AND override events (cohort 5, secret-scan-block D6 line 98, D13 line 105).
- `hooks.jsonl` is CONSUMED by `/li:hooks-status` — "this loop is closed. Good." (cohort 5 D13 line 69). `jobs.jsonl` consumed by jobs skill + job-stale-warn.

**Evidence — the unified audit promise is contradicted.**
- "Two parallel, non-converging audit systems exist." `bin/_audit.sh` is the declared v4.0 unified writer, but "**NO hook calls `_audit.sh`.** Override events from the 2 justified-block hooks (the highest-stakes overrides in the whole system) are written by hand-rolled printf to `hooks.jsonl`, NOT through `_audit.sh`, and are therefore NOT in the unified override trail." (cohort 5 D13 line 67-77).
- Write-only category logs: "no skill grep-reads `meta-infra-overrides.jsonl` or `brief-forge-override.jsonl` — they are write-only today (write side exists, read side is design-doc-only)." (cohort 5 line 73).
- Phase skills bypass the unified writer too: ship writes `hard-rule-stops.jsonl` directly, cycle writes `cycle-failures.jsonl` directly — "THREE audit-writing conventions coexist … The unified writer has zero phase-skill callers despite being the v4.0 standard." (cohort 8 L6 D13 line 226).
- `context-bloat-warn` audits nothing at all (cohort 5 C5-D13a, line 78).
- The SENSE meta-infra-override prompt-after-3 (design line 786) depends on `meta-infra-overrides.jsonl` being consumed — which it is not.

**Gap.** The override+audit PATTERN holds (gates have overrides; most events are logged; `hooks-status` closes one loop). But the UNIFIED-audit promise is broken at the seams: three writers, two readers that never meet, the highest-stakes overrides bypassing the unified trail, and several category logs write-only. The "audit is consumed" half is upheld for `hooks.jsonl`/`jobs.jsonl` and broken for the `_audit.sh` category logs. **Cleanest win (per cohorts 5+8, no new design):** route every audit write through `bin/_audit.sh` and teach `hooks-status` its schema.

---

### Promise 10 — First-party-first (no gstack/3P binary on execution path)

**Verdict: BROKEN.**

**The claim.** CLAUDE.md (project): "Lintel claims first-party-first." The motto's MS-CAIP-SE framing prefers MS/first-party. A dedicated hook (`non-first-party-warn`) and skill (`first-party-check`) exist to enforce it. The promise: no external-plugin binary sits on Lintel's own execution path.

**Evidence — the planner sub-chain depends on gstack binaries on the path.**
- "the 4 reviews call `~/.claude/skills/gstack/bin/gstack-review-log` — an external gstack-plugin binary path, violating first-party-first." (cohort 2 top finding 2, line 718; plan-ceo-review D13 line 230 "a gstack-plugin binary path, not a Lintel-owned one. Brand + dependency fragmentation"; plan-eng-review D13 line 322; plan-design-review D13 line 411; plan-devex-review D13 line 500).
- plan-design-review also "depends on an external gstack design binary" `~/.claude/skills/gstack/design/dist/design` (cohort 2 line 712; D11 line 399).
- codex persists via `gstack-review-log` (cohort 3, codex D3 line 780, D5 line 791) — "persist via the canonical envelope/jobs log, not gstack-review-log (CF-1 sibling)."
- Storage-root schism reinforces the coupling: context-save/restore write/read `~/.gstack/projects/<slug>/checkpoints/` (cohort 3 CF-1, line 50-60); the planner chain's projects-dir is split `~/.lintel/projects/` (producer) vs `~/.gstack/projects/` (consumers) — "the chain hand-off is literally broken at the directory level" (cohort 2 top finding 1, line 716).

**Why BROKEN, not a nit.** Lintel ships a hook and a skill to enforce first-party-first against the *target repo*, while its own review/observability execution path calls a gstack-plugin binary at a `~/.claude` path. "Depending on a gstack bin at a ~/.claude path couples the chain to an external plugin install" (cohort 2 line 237). The framework breaks the exact rule it enforces on others — and worse, the dependency is load-bearing (review-log write+verify-read is the observability spine of the planner chain, cohort 2 line 326). The audit-prompt explicitly cites this as a known break ("cohort 2 found reviews call a gstack binary = first-party-first broken"). **Uplift (per cohort 2):** route through a Lintel-owned `li-review-log`; alias the gstack path for back-compat (NO-CUT).

---

## Cross-promise observations

- **Two clusters of brokenness share one root: built-but-unwired.** Promise 2 (pack-resolver, zero consumers), Promise 6 (cap logic not called at hand-offs), and Promise 9's unified-audit seam (`_audit.sh`, zero phase-skill callers) are all the same failure shape — a correct, tested mechanism with no one calling it. These are the cheapest fixes because the authoring is done; the work is wiring + deleting duplicate call sites (subtraction). Cohorts 7 and 8 both name this as their highest-leverage finding.
- **The motto's two learning threads are both half-active.** Promise 1 (operator-relation: lessons) and Promise 5 (repo-relation: knowhow) are both "written, not consulted." X3 will find the same pattern; X2 confirms it at the promise level: data flows in, almost nothing flows back out as consultation.
- **The three DESIGNED-NOT-BUILT promises (4, 5, 8) are on-schedule and interlocked.** Navigation (Phase 3), Brief Forge (Phase 3), envelope (Phase 2) and knowhow are sequenced; the design correctly orders envelope before wiki and Brief Forge after pack+envelope. The risk is slip, not direction.
- **Only Promise 7 is cleanly UPHELD.** The founder approval gate is the framework's most disciplined promise — built, mandatory, bounded, operator-choice. It is the model: a gate that exists, fires every time, and is enforced as a failure mode.

---

## RETURN summary

**Counts: UPHELD 1 · PARTIALLY-UPHELD 4 · BROKEN 2 · DESIGNED-NOT-BUILT 3.**

**3 most-broken promises:**
1. **Pack-driven behavior (BROKEN)** — `lib/pack-resolver.sh` is built, tested, self-described as a 30+-skill critical-path interface, and has ZERO consumers; every skill grep-reads legacy `profile.yaml` against a different file than the canonical `pack.yaml`.
2. **First-party-first (BROKEN)** — Lintel's own planner reviews + codex + design-review call gstack-plugin binaries (`~/.claude/skills/gstack/bin/gstack-review-log`, gstack design binary) on the execution path, violating the rule Lintel ships a hook to enforce on others.
3. **Cross-session memory via lessons (PARTIALLY-UPHELD, write-only)** — CAPTURE/role-update write lessons but PLAN, BUILD, REVIEW, SHIP, the entire planner chain, and ~80 of 83 agents never read them; the marquee miss is "don't mock Azure SDK" never reaching the BUILD implementer.
