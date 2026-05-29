# Cross-cutting pass X1 — concept consistency

**Pass:** X1 of X1–X5 (concept consistency)
**Standard:** `docs/audit/lintel-uniformity-audit-prompt.md` (14 dimensions D1–D14)
**Inputs:** all 8 cohort findings files (`lintel-uniformity-findings-cohort{1-8}-*.md`)
**Date:** 2026-05-29
**Branch:** v4.0-phase1-meta-infra-spine

## What this pass does

For each of the 14 dimensions, this table shows — per cohort — whether the
concept is implemented, at what depth, and which members deviate from their
cohort norm. The point is to make **fragmentation across peer cohorts visible at
a glance**: where a dimension is present in one cohort but absent in a sibling
that should also carry it.

It does **not** reproduce all ~240 components row-by-row. Each cohort gets one
**norm row** per dimension-block, plus named **deviators** (members that sit
above or below their cohort norm).

### Cell legend

| Cell | Meaning |
|---|---|
| `present` | dimension implemented at/above the cohort's strongest-peer depth |
| `partial` | implemented but below the strongest peer, or prose-only / undeclared |
| `split` | cohort is internally divided — some members present, some absent |
| `absent` | dimension missing where the floor expects it |
| `n/a-kind` | correctly does not apply to this kind (e.g. D9 on a hook) |
| `n/a-arch` | designed-not-built at architecture level; tracked, not a per-component gap |

### The three designed-not-built dimensions (recorded once, per master directive)

- **D7 (runtime pack/WorkProfile resolver):** the *resolver* is built (`lib/pack-resolver.sh`) but has **zero consumers**; WorkProfile *branching* exists in a few skills/hooks but reads legacy `profile.yaml`, not the canonical pack field. So D7 is marked `n/a-arch` where unbuilt, but its **consumer-layer fragmentation is real and scored** (cohorts 5, 7).
- **D9 (Brief Forge):** unbuilt everywhere. Marked `n/a-arch`. The *should-fire density* is the finding, concentrated in cohort 3.
- **Envelope / wiki / knowhow:** unbuilt (cohort 8 layers L2/L3/L4). `n/a-arch`.

---

## The X1 concept-consistency table

Each row = one cohort's **norm** for that dimension; deviators named inline.

### D1 — Head / entry

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | present | `plan` above (3 invocation modes + job spawn); `fix` strongest composite head |
| 2 planner | present | `plan-eng-review` above (BLOCKING Step 0); `office-hours` above (richest Inputs) |
| 3 handoff | present | `context-budget`/`context-cool` partial (implicit head, no Inputs §) |
| 4 agents | **partial** | prose `When to invoke`, no validated input contract; `ShaderEngineer` above (declared flag-inputs) |
| 5 hooks | present | `stale-calibration-warn` **bug** (frontmatter claims content-gate run.sh lacks) |
| 6 eng-domains | split | SC deep (`/onecs-check` validated); TA/DA **thin** (agent-spawn only, no `/li:` entry) |
| 7 packs/roles | present | uniform — all 8 role skills explicit slash + $1 input |
| 8 cross-cutting | partial | no envelope ⇒ no uniform head validation across the 8 phase handoffs (L4) |

### D2 — Tail / exit

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | present | `cycle` above (only ABORTED state); 4 composites **partial** (status "inherits") |
| 2 planner | present | `plan-eng-review` above (BLOCKING exit gate); design/devex **partial** (score-delta, no CLEARED token) |
| 3 handoff | **split** | lintel-dialect (DONE/BLOCKED) vs gstack-dialect (✓ only, no token) — ~7 below floor; `skill-router` absent |
| 4 agents | partial | every agent has Report format but status vocab inconsistent (DONE vs free-text Verdict) |
| 5 hooks | present | `job-end` above (DONE/ABORTED/FAILED protocol) |
| 6 eng-domains | split | SC deep (PASS/NEEDS_ACTION blocks downstream); TA/DA thin (agent report, no verdict) |
| 7 packs/roles | present | `role-deactivate` above (honest DONE_WITH_CONCERNS) |
| 8 cross-cutting | partial | no envelope TAIL contract across phases |

### D3 — Expected objects (in/out contract)

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | **partial** | only `plan` has a deterministic caller-relyable contract; `discover` close (full report schema) |
| 2 planner | partial + **BROKEN** | `office-hours` writes `~/.lintel/projects/`; ceo/eng/design/autoplan read `~/.gstack/projects/` — path break; `plan-tune` correct |
| 3 handoff | **broken** | storage-root schism (4 roots); `context-save`→`context-dump` & →`context-warm-sessions` **live contract breaks**; `context-warm`/`codex` set the bar |
| 4 agents | partial | prose in/out; structured emitters cite consuming SKILL.md (good); text-report agents have no out-schema |
| 5 hooks | present | `no-merge-without-review` above (consults review-log); `no-customer-data-in-screenshot` partial (implicit dom.html) |
| 6 eng-domains | split | SC deep (per-artifact + cross-artifact); DA mid (agent report only) |
| 7 packs/roles | present | `role-frame` above (richest findings block); `role-new` template = schema source |
| 8 cross-cutting | absent | **the single most fragmented contract** — 8/8 phase handoffs ad-hoc, no HEAD/BODY/TAIL (L4 unbuilt) |

### D4 — Entry-points

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | present | `plan`/`cycle` above (module-callable, dep-verify); composites uniform |
| 2 planner | present | uniform; `plan-eng-review` above (also consumed by release-ev2) |
| 3 handoff | present | `codex` above (names 3 callers); `skill-router` partial (body `/match` name drift) |
| 4 agents | **broken** | DISCOVER Step 6 scan **omits `frontend` category** (5 agents dynamic-unreachable); **11 orphans** named by no skill |
| 5 hooks | present | uniform — correct event matchers |
| 6 eng-domains | split | SC deep (session-start auto + on-demand + pre-ship gate); DA thin/absent (Task-spawn only) |
| 7 packs/roles | present | `roles-list` is keystone (4 skills' recovery falls back to it) |
| 8 cross-cutting | partial | jobs: only cycle+plan declare `workflow_root`; solo phase invocations leave no trace (L1) |

### D5 — Checkpoints

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | present | `build` above (per-task WIP commits); `plan` above (`.planner-checkpoint`); composites **absent** (delegate) |
| 2 planner | **absent** | no mid-flight checkpoint; only `autoplan` (idempotency) + `eng-review` (exit gate) have any resume discipline |
| 3 handoff | split | lintel-family append 00-state; `pair-agent` **absent** (multi-turn, no resume); `context-warmup` different model |
| 4 agents | **absent** | agents write no own checkpoint (acceptable for review agents; gap for long BUILD implementers) |
| 5 hooks | n/a-kind | `job-begin`/`job-end` present (only hooks that manage state); warn hooks n/a |
| 6 eng-domains | split | designed-not-built for TA/DA/SC modules; `safe-deploy-ring`/`qa` have per-iteration |
| 7 packs/roles | present | **strongest cohort** — all 8 role skills append typed 00-state events |
| 8 cross-cutting | present | jobs checkpoint mechanical (cycle/plan); `blocked_until` advisory-only (not enforced) |

### D6 — Recovery points

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | present | `ship` above (6 cases); `sense`/`build`/`review` strong; composites partial (inherit) |
| 2 planner | present | `autoplan` above (per-step pause + idempotent re-run); `office-hours` above (5 modes) |
| 3 handoff | split | `pair-agent`/`context-warm` set bar; `context-snapshot`/`-budget`/`-cool` **absent** (no failure-modes §) |
| 4 agents | partial | all have `Edge cases`; recovery **vocabulary inconsistent** (STOP vs degrade vs NEEDS_CONTEXT) |
| 5 hooks | present | block-tier override = recovery (required, present); `job-stale-warn` above (actionable recovery) |
| 6 eng-domains | split | SC deep (CRITICAL-raise, attestation path); TA/DA thin (agent edge-cases) |
| 7 packs/roles | present | **strongest cohort** — 3 named recovery branches per skill, the model others should copy |
| 8 cross-cutting | n/a | (layer-level) |

### D7 — Pack / WorkProfile influence

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | n/a-arch | `review`/`ship` partial (WorkProfile branches Stage-3 gates — working precedent); `cycle` mode-presets = proto-packs |
| 2 planner | n/a-arch | none consume a pack; designed knobs noted |
| 3 handoff | split | `context-warm-customer`/`-from-url` **present** (WorkProfile changes behavior — D7 exemplars); rest absent |
| 4 agents | **absent** | all 83 — no `packs:` affinity; DISCOVER scan pack-blind |
| 5 hooks | **absent** | all 19 — **9 inline MS/Sweden/Trailblazer data** (PII regex, EN-vocab array, first-party map) with no pack switch |
| 6 eng-domains | split | SC mid (ms-team gates fire by profile); TA/DA absent |
| 7 packs/roles | **absent (the center)** | resolver built+tested, **zero consumers**; all hardcode role-path triple + grep `profile.yaml`; WorkProfile in 2 schemas |
| 8 cross-cutting | partial | provenance responds to WorkProfile (good) but predicate duplicated inline in review+ship |

### D8 — Frontmatter completeness

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | partial | all lack `necessity`/`tokens_est_typical`; `plan`/`cycle` lack `navigation` despite `workflow_root` |
| 2 planner | partial | `plan-design-review`/`plan-tune`/`autoplan` cli_support claude-only (inversion); none declare necessity/io |
| 3 handoff | partial | **zero declare `brief_forge_handoffs:`** (canonical field); `context-warmup` best cli_support |
| 4 agents | partial | **2 cli_support dialects** (74 compact vs 9 structured); `tier:` missing on 24 (mostly engineering) |
| 5 hooks | present | mostly complete; `secret-scan-block` fullest; necessity stamp the main gap |
| 6 eng-domains | split | SC deep (layer/v1_alias + agent tier); DA/TA mid |
| 7 packs/roles | partial | cli_support form-drift (short-list vs object); no necessity/io/brief_forge_handoffs |
| 8 cross-cutting | n/a | (layer-level) |

### D9 — Brief Forge integration

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | n/a-arch | exemplar precedent: `build` Step 3a implementer-brief = de-facto Brief-Forge payload |
| 2 planner | n/a-arch | `autoplan` step-8 aggregation = **#1 should-fire site in cohort** |
| 3 handoff | **n/a-arch (densest should-fire)** | moments 1/2/4/5 all present & un-gated; `pair-agent`/`codex` most-built proto-gates |
| 4 agents | n/a-arch | agent-spawn IS a hand-off; curated-brief rule already mandated but not wired |
| 5 hooks | n/a-kind | hooks are not hand-off points |
| 6 eng-domains | n/a-arch | designed in every §3.x (evaluators), built nowhere |
| 7 packs/roles | n/a-arch | `role-activate` injects role brief subagents inherit — should-fire (pack.yaml declares on_subagent_spawn) |
| 8 cross-cutting | n/a-arch | envelope = the Brief-Forge transport (L4 unbuilt) |

### D10 — Knowledge / lessons integration

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | **split** | `sense`/`define`/`discover`/`capture` present; **`plan`/`build`/`review`/`ship`/`cycle` ABSENT** (write-only memory) |
| 2 planner | **absent** | none consult lessons — even where memory compounds most (ceo founder-signal, devex trend) |
| 3 handoff | absent | mostly absent; `context-warm-adrs` partial (reads ADRs, not lessons); `skill-router` reads telemetry only |
| 4 agents | partial | `Architect`/`CodeReviewer` read ADRs; majority absent even where relevant (DebugForensics, RegressionDetective) |
| 5 hooks | absent | could pull tells from corpus/lessons; none do |
| 6 eng-domains | thin | SC mid (reads RAI/ON-DEMAND rules); TA/DA thin (read existing schema/ADRs) |
| 7 packs/roles | **half-built** | `role-update` WRITES role learnings; `role-activate` never READS them — loop open |
| 8 cross-cutting | absent | knowhow tag-funnel write-never-read; DISCOVER reads lessons.md but not pack knowhow (unmerged channels) |

### D11 — Subagent / context delegation

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | present | `build`/`review` set bar (curated brief, sequential); `sense`/`cycle` n/a-kind |
| 2 planner | split | `plan-eng-review` present (outside-voice subagent); office-hours/design/devex **absent** (inline bulk gen) |
| 3 handoff | split | **`pair-agent` is the only true delegator** (sets bar); rest n/a-kind or absent |
| 4 agents | n/a-kind | agents are leaves — correct; uniform |
| 5 hooks | n/a-kind | hooks run inline by design |
| 6 eng-domains | present | SC/TA deep (agents are the curated delegation target); DA mid (2 agents) |
| 7 packs/roles | present | correctly inline; `role-frame`/`role-new` could delegate large reads |
| 8 cross-cutting | n/a | (layer-level) |

### D12 — Failure mode

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | present | uniform; composites partial (inherit, no own mode) |
| 2 planner | present | uniform/strong; `eng-review` degrades gracefully (jq-missing) |
| 3 handoff | present | `pair-agent`/`codex` set bar; `context-snapshot`/`-cool` partial (no failure branches) |
| 4 agents | partial | same vocab inconsistency as D6; `ShaderEngineer` above (Anti-patterns + Failure recovery) |
| 5 hooks | present | uniform (block vs warn); fail-open infra hooks |
| 6 eng-domains | present | SC/DH/TQ deep (explicit `## Failure modes`); TA/DA thin |
| 7 packs/roles | present | uniform ask-operator/list-alternatives; `role-update` above (post-write integrity check) |
| 8 cross-cutting | n/a | (layer-level) |

### D13 — Observability

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | **split** | define/plan/build/review/capture/cycle have `*-metrics.jsonl`; **sense/discover/ship + all 4 composites absent**; composites can't be distinguished from raw cycle (no `invoked_via`) |
| 2 planner | split | review skills log (via **gstack-bin path** — first-party violation); `office-hours`/`autoplan` emit NO log |
| 3 handoff | split | `context-warm-customer` bar (durable audit); `skill-router` **absent** (invisible runs) |
| 4 agents | **absent** | all 83 — no per-agent usage/envelope/cost trail |
| 5 hooks | present | 17/19 write hooks.jsonl (consumed by hooks-status ✓); **but bypass `_audit.sh`**; `context-bloat-warn` zero audit |
| 6 eng-domains | split | SC deep (pervasive append-only jsonl); **TA + DA write NONE** |
| 7 packs/roles | partial | `role-deep-dive` above (cost note); pack-resolver writes jsonl, role skills don't match |
| 8 cross-cutting | **fragmented** | THREE writers (`_audit.sh` unified-but-unused, `_jobs.sh` own, phase-skill inline) with inconsistent field sets |

### D14 — Necessity declaration

| Cohort | norm | deviators |
|---|---|---|
| 1 phase-core | **implicit** | all in prose (`When NOT to use`); no declared `necessity`/`gap_if_skipped` field anywhere |
| 2 planner | partial | prose-only (`plan-eng-review` says "required" in prose, not field) |
| 3 handoff | **absent** | all 18 — no REQUIRED/RECOMMENDED/OPTIONAL stamp |
| 4 agents | **absent** | all 83 |
| 5 hooks | mostly absent | only 4 newest (job×3, frontend-surface) carry de-facto necessity framing |
| 6 eng-domains | absent | SC has implicit REQUIRED via downstream-block; declared field nowhere |
| 7 packs/roles | absent | implicitly OPTIONAL, never stated |
| 8 cross-cutting | n/a | (layer-level) |

---

## Dimension health summary (one line per D1–D14)

For each dimension: which cohorts implement it well, which don't, and the single
worst fragmentation.

- **D1 head** — well: hooks(5), packs/roles(7), planner(2). Weak: agents(4, prose-only). Worst frag: SC has a validated `/li:` entry, peer DA has no entry at all (agent-spawn only).
- **D2 tail** — well: phase-core(1), packs/roles(7), eng-SC. Weak: handoff(3, dialect split). Worst frag: lintel DONE/BLOCKED dialect vs gstack `✓`-only dialect coexist in cohort 3 — a resume engine can machine-detect half the cohort, not the other half.
- **D3 in/out contract** — well: hooks(5), packs/roles(7). Weak/broken: planner(2 path bug), handoff(3 schism), cross-cutting(4 no envelope). **Worst frag: live producer/consumer breaks** — `context-save`→`context-dump` and the planner `~/.gstack/` vs `~/.lintel/` path split (a consumer literally cannot read its named producer).
- **D4 entry-points** — well: phase-core(1), planner(2), packs/roles(7), hooks(5). **Worst frag: agents(4)** — DISCOVER dynamic scan omits the entire `frontend` category + 11 orphan agents reachable by no skill, vs ms-specific/security/compliance fully wired.
- **D5 checkpoints** — well: **packs/roles(7, strongest)**, phase-core(1). Weak/absent: planner(2), agents(4). Worst frag: every role skill appends a typed 00-state event, but no planner review skill checkpoints mid-flight — peer cohorts on opposite extremes.
- **D6 recovery** — well: **packs/roles(7)**, phase-core(1), planner(2). Weak: handoff(3 split), agents(4 vocab). Worst frag: within cohort 3, `pair-agent` has the best failure enumeration while `context-snapshot`/`-budget`/`-cool` have no failure-modes section at all.
- **D7 pack-influence** — well: **nowhere at the consumer layer** (resolver built, unused). Partial precedents: review/ship WorkProfile-branching, context-warm-customer. **Worst frag: packs/roles(7)** — a fully-built, fully-tested resolver with literally zero callers while 12+ skills hardcode `profile.yaml` grep; *and* hooks(5) inline Swedish PII/EN-vocab with no pack switch.
- **D8 frontmatter** — well: hooks(5), eng-SC. Weak: everyone lacks `necessity`; **agents(4) carry 2 incompatible cli_support dialects + 24 missing `tier:`**; cohort 3 has zero `brief_forge_handoffs:`. Worst frag: two parseable cli_support shapes across the agent layer (74 vs 9).
- **D9 Brief Forge** — uniformly `n/a-arch` (unbuilt). Best should-fire density: handoff(3). Worst frag: not present anywhere, so no consumer fragmentation — but cohort 3 has 4 hand-off moments un-gated vs cohorts that have only 1.
- **D10 lessons/knowledge** — well: half of phase-core(1) (sense/define/discover/capture). **Worst frag: write-only memory** — CAPTURE *writes* lessons and `role-update` *writes* role learnings, but PLAN/BUILD/REVIEW/SHIP and `role-activate` never *read* them; planner(2) and most agents consult nothing. The learning loop is open in 5 of 8 cohorts.
- **D11 subagent delegation** — well: phase-core(1, build/review), eng-domains(6). Correct n/a: agents(4), hooks(5). Worst frag: cohort 3 has exactly one true delegator (`pair-agent`) while peers in cohort 2 (office-hours, devex) run bulk generation inline.
- **D12 failure mode** — well: phase-core(1), planner(2), hooks(5), packs/roles(7), eng-SC/DH/TQ. Weak: agents(4 vocab), eng-TA/DA(thin). Worst frag: SC/DH/TQ have explicit `## Failure modes`; peers TA/DA have only agent edge-cases.
- **D13 observability** — well: hooks(5, consumed loop ✓), eng-SC. **Worst frag: agents(4)** all 83 emit no trail at all, *and* eng-domains where SC writes pervasive jsonl but peer DA/TA write none; compounded by THREE divergent writers (`_audit.sh`/`_jobs.sh`/inline) in cross-cutting(8).
- **D14 necessity** — **uniformly weak**: no cohort declares `necessity`/`gap_if_skipped` as a field; best is prose (`plan-eng-review`, hooks' 4 newest). No real fragmentation — it is uniformly absent, an X5 framework decision.

---

## The fragmentation verdict

Three structural patterns recur across the table:

1. **Storage / path / writer fragmentation (D3, D13)** — the same logical data
   lands in 4–5 different roots; the unified audit writer has no callers; named
   producer/consumer pairs are broken. *Pure consolidation of built parts.*
2. **Write-only learning (D10)** — lessons and role-learnings are written but
   never read back by the components that would benefit. *The operator-relation
   loop is open in 5 of 8 cohorts.*
3. **Built-but-unwired (D7)** — `pack-resolver.sh` is the framework's
   best-engineered artifact with zero consumers; the pack promise is 100%
   declared and ~0% upheld at the consumer layer.

D8/D14 (necessity, frontmatter schema) are **uniformly** weak rather than
fragmented — they fold into the X5 framework-schema decision, not X1.
