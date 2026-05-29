# Cohort 8 findings — cross-cutting infrastructure

**Auditor:** uniformity auditor (cohort 8 of 8)
**Date:** 2026-05-29
**Scope:** 6 cross-cutting layers × 8 phase-core skills. NO-CUT. BUILT vs DESIGNED-NOT-BUILT marked per layer.
**Branch:** v4.0-phase1-meta-infra-spine (mid v4.0 reframe; Phase 1 of 3)
**Verified scale:** 144 skills, 83 agents, 19 hooks (18 in `hooks/shared/*/run.sh` + `hooks/entropy-secret-check.sh`).

The unit of audit in this cohort is the **layer**, not the skill. Each layer is evaluated for whether it is consumed *uniformly* across the 8 phase-core skills (sense, define, discover, plan, build, review, ship, capture). The headline deliverable is the 8×6 consumption matrix.

---

## Layer status summary

| # | Layer | Status | Built artifacts | Consumers (of 8 phase skills) |
|---|-------|--------|-----------------|-------------------------------|
| 1 | Jobs system | **BUILT** (v3.8) | `bin/_jobs.sh`, `hooks/shared/job-{begin,end,stale-warn}/run.sh`, `skills/jobs`, `skills/status`, `docs/concepts/jobs-system.md` | 2 declare `workflow_root` (cycle, plan); 0 of 8 phase skills declare it directly |
| 2 | Knowledge base / knowhow (tag-funnel) | **DESIGNED-NOT-BUILT** | `pack.yaml` `knowhow:` block only (`source: null`) | 0 |
| 3 | Wiki generator (`bin/li-wiki-gen`) | **DESIGNED-NOT-BUILT** (v4.0 Ch.2 FR-C, Phase 3) | none — verified absent in `bin/` | 0 (n/a — generates, not consumed by phases) |
| 4 | Payload envelope (`lib/envelope-schema.yaml`) | **DESIGNED-NOT-BUILT** (v4.0 Ch.2 FR-B, Phase 2) | none — verified absent in `lib/` (only `pack-resolver.sh`); forward-defensive test exists | 0 |
| 5 | Provenance | **BUILT (partial)** | `skills/provenance-track`, `agents/ms-specific/ProvenanceVerifier.md`, `~/.lintel/provenance/` store | 2 invoke it (review conditional, ship) |
| 6 | Audit writer (`bin/_audit.sh`) | **BUILT** (v4.0 Phase 1) | `bin/_audit.sh`, `bin/_jobs.sh` (own writer) | writers fragmented; see matrix |

---

## The 8×6 consumption matrix

Cell legend: `fires` = layer is invoked/written by this skill in its body; `n/a` = layer correctly does not apply; `should` = should-fire-doesn't (a finding); `--` = not applicable because layer is unbuilt and skill is not a designed consumer.

Rows = phase-core skills. Columns = layers.

| skill | L1 jobs | L2 knowhow | L3 wiki | L4 envelope | L5 provenance | L6 audit writer |
|-------|---------|-----------|---------|-------------|---------------|-----------------|
| sense    | should¹ | should²   | n/a | should³ | n/a       | should⁴ |
| define   | should  | should²   | n/a | should³ | n/a       | should⁴ |
| discover | should  | should²   | n/a | should³ | n/a       | should⁴ |
| plan     | **fires**⁵ | should² | n/a | should³ | n/a       | should⁴ |
| build    | should  | should²   | n/a | should³ | should⁶   | should⁴ |
| review   | should  | should²   | n/a | should³ | **fires**⁷ (conditional) | should⁴ |
| ship     | should  | should²   | n/a | should³ | **fires**⁸ | **fires**⁹ (hard-rule-stops.jsonl) |
| capture  | should  | should² (writes lessons, never reads knowhow) | n/a | should³ | n/a | should⁴ |

**Footnotes (file:line evidence):**

1. ¹ SENSE is named in `docs/concepts/jobs-system.md:74` as a session-start trigger for `job-stale-warn`, but `skills/sense/SKILL.md` has no `workflow_root` flag and no `_jobs.sh` reference — it neither spawns nor surfaces jobs from its own body. Only the hook (if symlinked) does. Gap: SENSE is the canonical session entry yet doesn't itself read `_active.md`.
2. ² No phase-core skill references `knowhow` or the tag-funnel anywhere. The only `knowhow:` mention in the codebase outside design docs is `packs/_default/pack.yaml:41` (`source: null`) and `docs/concepts/pack-defaults.md`. DISCOVER (`skills/discover/SKILL.md:77`) reads `tasks/lessons.md` but never the pack knowhow base — the two knowledge channels are not unified.
3. ³ Envelope is DESIGNED mandatory-at-workflow_root (`docs/design/lintel-v4.0-reframe-design.md:206`), schema home `lib/envelope-schema.yaml` (line 208). File absent. All 8 phase skills hand off via ad-hoc report files (`discover-report.md`, `design.md`, the plan/spec/prompt trio) with no standardized HEAD/BODY/TAIL envelope. This is the largest designed-but-unadopted contract.
4. ⁴ `bin/_audit.sh` (v4.0 Phase 1) is the unified audit writer; its header (lines 6-10) names its intended callers — meta-infra, orientator, pack-resolver, Brief Forge, migration. **No phase-core skill sources `_audit.sh`.** Phase skills that do log write to bespoke files directly (cycle → `cycle-failures.jsonl`, ship → `hard-rule-stops.jsonl`) bypassing the unified writer.
5. ⁵ `skills/plan/SKILL.md:4` declares `workflow_root: true`; lines 374, 407-408 document the `job-begin` hook spawning `~/.lintel/jobs/plan-<stamp>-<hash>/`. This is the one phase-core skill that fully participates in jobs.
6. ⁶ BUILD produces the shippable artifact but never calls `provenance-track`; provenance is deferred to REVIEW/SHIP. For trailblazer-voice artifacts the source-chain auto-detect (`skills/provenance-track/SKILL.md:40-44`) relies on adjacent audit entries that BUILD never writes.
7. ⁷ `skills/review/SKILL.md:112-114` — `/li:provenance-track` fires only conditionally (`if WorkProfile=on AND artifact will ship`).
8. ⁸ `skills/ship/SKILL.md:100-102, 232, 250, 294` — provenance is a hard gate at SHIP for customer-facing artifacts (strongest consumer).
9. ⁹ `skills/ship/SKILL.md:81` writes `~/.lintel/audit/hard-rule-stops.jsonl` directly — observability exists but does NOT route through `bin/_audit.sh`.

**Matrix headline:** of 48 cells, only **5 fire** (plan→jobs, review→provenance conditional, ship→provenance, ship→audit, and plan's job-spawn). **31 cells are should-fire-doesn't** for built/designed layers. Cross-cutting layers are built but **not cross-cut** — adoption is concentrated in cycle/plan/ship and absent from sense/define/discover/build/capture.

---

## Per-layer records

### Layer 1 — Jobs system — BUILT (v3.8)

```yaml
layer: jobs-system
kind: cross-cutting-infrastructure
status: BUILT
built_artifacts:
  - bin/_jobs.sh (job_create/job_update/job_archive/regenerate_active/stale_jobs/job_path)
  - hooks/shared/job-begin/run.sh
  - hooks/shared/job-end/run.sh
  - hooks/shared/job-stale-warn/run.sh
  - skills/jobs/SKILL.md (5-subcommand controller)
  - skills/status/SKILL.md (read alias)
  - docs/concepts/jobs-system.md
dimensions:
  D4_entrypoints:
    state: partial
    nano: "hooks/shared/job-begin/run.sh:23 (greps workflow_root: true); only skills/cycle/SKILL.md:4 + skills/plan/SKILL.md:4 declare it"
    macro: "every curated flow"
    high: "jobs visibility promise — 'see what's open right now'"
    finding: "Only 2 skills (cycle, plan) declare workflow_root. The 8 phase-core skills do NOT individually participate; a solo /li:sense or /li:build leaves no job trace. job-begin fires PreToolUse but is opt-in via manual symlink (hooks/shared/README.md:7) so default installs get zero job tracking."
    proposed: "Decide the participation model: either (a) phase skills run only nested inside cycle/plan jobs (then document this explicitly and add the NO_JOB guard to each), or (b) give each phase skill a lightweight job-touch so solo invocations are visible. Today it is neither — ambiguous."
    why: "Achieve uniform in-flight visibility. gstack's context-save/restore + GSD's .planning/ thread model both persist per-invocation state; Lintel persists only for the 2 root flows. Option (a) is more elegant (fewer parts) and matches the anti-pattern note in jobs-system.md:156 about nesting."
  D5_checkpoints:
    state: present
    nano: "bin/_jobs.sh:80-103 job_update writes current_step + last_touched; 00-state.md moved into job dir"
    finding: "Checkpointing is mechanical for cycle/plan but the per-step job.yaml steps[] contract (consumes/produces/blocked_until, jobs-system.md:113-137) is documented, not enforced by any built code — _jobs.sh job_update does not validate blocked_until."
    proposed: "Add blocked_until evaluation to job_update or a job_can_start helper; raise to the depth the concept doc promises."
    why: "The doc sells blocked_until as 'a mechanical gate. BUILD literally cannot start' (jobs-system.md:137) — currently advisory only. Promise verification gap."
  D13_observability:
    state: present
    nano: "bin/_jobs.sh:70-71,99-100,137-138 → ~/.lintel/audit/jobs.jsonl"
    finding: "Jobs write their OWN jobs.jsonl, not via bin/_audit.sh. Two audit-writing conventions coexist (see Layer 6)."
    proposed: "Refactor _jobs.sh audit writes to source _audit.sh / audit_log. Single writer."
    why: "One audit format → grep/jq/replay uniformity (the _audit.sh promise, lines 11-12)."
peer_comparison:
  strongest_consumer: plan (full workflow_root participation)
  weakest_consumer: sense/build (zero participation despite being session-relevant)
  uplift_needed: "phase-core skills reach plan's participation depth (declared model, not ambiguous)"
operator_decision_required: yes
priority: high
```

### Layer 2 — Knowledge base / knowhow (tag-funnel) — DESIGNED-NOT-BUILT

```yaml
layer: knowhow-tag-funnel
status: DESIGNED-NOT-BUILT
contract_location: "packs/_default/pack.yaml:40-43 (source: null, override_session_priors: false)"
also_referenced: "docs/feature-requests/lintel-feature-spine-packs-navigation.md, docs/feature-requests/lintel-feature-brief-forge.md, docs/concepts/pack-defaults.md"
adoption: 0/8 phase skills
dimensions:
  D3_objects:
    state: absent
    nano: "pack.yaml:41 declares the field; no schema for what a tag-indexed knowhow entry looks like; no reader"
    finding: "The contract is a single nullable pack field. No entry schema, no tag taxonomy, no lookup helper (compare bin/_jobs.sh which exists for jobs). knowhow is the least-specified of all 6 layers."
    proposed: "Before any consumer: write a knowhow entry schema (tags, body, provenance, scope) and a bin/_knowhow.sh lookup helper mirroring _jobs.sh. Then wire DISCOVER as first consumer."
    why: "DISCOVER already does knowledge surfacing from lessons.md (discover/SKILL.md:77-80) — it is the natural first consumer. superpowers/ECC tag-indexed retrieval is the reference pattern. Building the helper first (L-002 lift discipline) avoids 8 skills each reinventing lookup."
  D4_entrypoints:
    state: absent
    nano: "grep across skills/ for knowhow → 0 hits in phase skills"
    finding: "should-fire-doesn't at DISCOVER (context prep), DEFINE (prior-art), PLAN (reusable patterns), REVIEW (known pitfalls). 4 designed consumption points, 0 built."
    proposed: "DISCOVER reads pack.knowhow alongside lessons.md; unify the two knowledge channels into one surface."
    why: "Repo-relation evolution thread (motto): knowhow grows and must be consulted, not just declared. Today it's write-never-read at the structural level."
peer_comparison:
  strongest_analog: jobs-system (has helper + hooks + skills + concept doc)
  this_layer_depth: far-below-bar (field only, no helper, no concept doc, no consumer)
  uplift_needed: "raise to jobs-system depth: helper + schema + concept doc + ≥1 phase consumer"
operator_decision_required: yes
priority: medium
```

### Layer 3 — Wiki generator (`bin/li-wiki-gen`) — DESIGNED-NOT-BUILT

```yaml
layer: wiki-generator
status: DESIGNED-NOT-BUILT
contract_location: "docs/design/lintel-v4.0-reframe-design.md:212-226 (FR-C, Ch.2.C), schedule line 836-839 (Phase 3)"
verified_absent: "glob bin/** → no li-wiki-gen (bin has: li-adr-new, li-roles-sync, li-doctor, li-lessons-promote, li-lessons-sync, li-scaffold, li-update, li-compat-audit, _aliases.sh, _jobs.sh, _audit.sh, li-compat-audit/)"
adoption: n/a (generator, not consumed by phase skills)
dimensions:
  D3_objects:
    state: designed
    nano: "design.md:216 — two outputs from one generator: markdown wiki + showcase HTML regen from current sources"
    finding: "Contract is well-specified (idempotent, pre-commit + CI staleness check, regenerates docs/showcase/lintel-the-harness.html). Not built — correct for Phase 1 (it's Phase 3 work, design.md:836)."
    proposed: "No uplift now — on-schedule. When built: ensure it reads the SAME source-of-truth that the envelope schema and pack schema define, so wiki cannot fork reality (design.md:226 risk)."
    why: "The acceptance test (design.md:916) demands idempotence against 144 skills × 83 agents × 19 hooks. Worth confirming the count source is canonical (skills/CATALOG.md is auto-regenerated per commit 3584001) so wiki-gen and CATALOG don't drift."
peer_comparison:
  this_layer_depth: on-schedule-not-built
  uplift_needed: "none pre-Phase-3; flag the count-source-of-truth dependency"
operator_decision_required: no
priority: low
```

### Layer 4 — Payload envelope (`lib/envelope-schema.yaml`) — DESIGNED-NOT-BUILT

```yaml
layer: payload-envelope
status: DESIGNED-NOT-BUILT
contract_location: "docs/design/lintel-v4.0-reframe-design.md:204-210 (FR-B, Ch.2.B); schema home lib/envelope-schema.yaml:208; mandatory-at-workflow_root agreed:206"
verified_absent: "glob lib/** → only lib/pack-resolver.sh. envelope-schema.yaml absent."
forward_defensive_test: "tests/shape/schema-versioned-contracts.sh:32 lists lib/envelope-schema.yaml as a future contract; emits INFO 'not present yet (ships Phase 2-3)' rather than failing"
adoption: 0/8 (designed mandatory at workflow_root → minimum cycle + plan must adopt at ship-time)
dimensions:
  D3_objects:
    state: designed
    nano: "design.md:206 HEAD + BODY + TAIL standardized payload"
    finding: "Today every phase-to-phase handoff is ad-hoc: SENSE→DEFINE (free text), DEFINE→DISCOVER (design.md), DISCOVER→PLAN (discover-report.md, discover/SKILL.md:15), PLAN→BUILD (plan+spec+prompt trio). No HEAD/BODY/TAIL contract; no validation at head/tail (D1/D2 of the dimension standard). This is the single most fragmented contract in the framework."
    proposed: "Phase 2: build lib/envelope-schema.yaml with schema_version (test already expects it). Phase 2-3: make workflow_root skills (cycle, plan) emit + validate envelopes; phase skills consume them. Sequence envelope BEFORE wiki (wiki reads schemas)."
    why: "D3 'expected objects' is the core uniformity dimension and it is currently inferred everywhere. The envelope is the fix the design already chose. More elegant than per-skill contracts because one schema + one validator covers all 8 handoffs. speckit's contract-first plan artifacts are the reference."
  D1_head_D2_tail:
    state: absent
    finding: "Without the envelope, no phase skill validates inputs at head or outputs at tail in a uniform shape — each does ad-hoc checks. This is exactly the D1/D2 gap the master prompt targets."
    proposed: "Envelope adoption gives every workflow_root handoff a validated HEAD (inputs) + TAIL (outputs) for free."
    why: "Single mechanism closes D1+D2+D3 uniformity across all 8 skills at once."
peer_comparison:
  this_layer_depth: on-schedule-not-built (but highest-leverage when built)
  uplift_needed: "none pre-Phase-2; this is THE Phase-2 uniformity unlock"
operator_decision_required: no
priority: high
```

### Layer 5 — Provenance — BUILT (partial adoption)

```yaml
layer: provenance
status: BUILT
built_artifacts:
  - skills/provenance-track/SKILL.md
  - agents/ms-specific/ProvenanceVerifier.md
  - "~/.lintel/provenance/ store + index.jsonl (provenance-track/SKILL.md:72)"
adoption: 2/8 phase skills (review conditional, ship hard-gate); build should but doesn't
dimensions:
  D4_entrypoints:
    state: partial
    nano: "ship/SKILL.md:100-102 (hard gate); review/SKILL.md:112-114 (conditional WorkProfile=on AND will-ship)"
    finding: "Provenance fires at REVIEW (conditional) and SHIP (gate). It is BUILT and well-specified but adoption is back-loaded. BUILD — which actually generates the artifact and whose audit entries the source-chain auto-detect depends on (provenance-track/SKILL.md:40-44) — writes nothing, so source-chain reconstruction at SHIP relies on adjacent audit entries that may not exist."
    proposed: "Have BUILD write a lightweight provenance breadcrumb (skill, input, timestamp) when WorkProfile=on, so SHIP's auto-detect has a real chain instead of inferring from 24h-adjacent logs."
    why: "Provenance is sold as a complete source-chain (provenance-track/SKILL.md:54-65). If the generating step (BUILD) leaves no trace, the chain has a hole at its origin. Closing it at the source is more robust than inferring at the sink."
  D7_pack_influence:
    state: present
    nano: "review/SKILL.md:112 gates on WorkProfile=on; pack.yaml compliance.workprofile_default:24"
    finding: "Provenance correctly responds to WorkProfile — good D7. But the trigger is duplicated as inline conditionals in review + ship rather than read from one pack policy."
    proposed: "Centralize the 'provenance required when' predicate (mirror brief_forge_handoffs block in pack.yaml) so review/ship/build read one policy."
    why: "Shared-schema discipline: two skills reinterpreting the same gate condition is the duplication anti-pattern."
peer_comparison:
  strongest_consumer: ship (hard gate, ProvenanceVerifier agent, 4-gate fire)
  weakest_consumer: build (origin of artifact, zero provenance write)
  uplift_needed: "BUILD writes origin breadcrumb; gate-predicate centralized in pack"
operator_decision_required: yes
priority: medium
```

### Layer 6 — Audit writer (`bin/_audit.sh`) — BUILT (v4.0 Phase 1)

```yaml
layer: audit-writer
status: BUILT
built_artifacts:
  - bin/_audit.sh (audit_log / audit_count / audit_days_ago)
intended_callers: "_audit.sh:6-10 — meta-infra-mode-override, orientator-override, pack-resolver, brief-forge-override, migration"
dimensions:
  D13_observability:
    state: partial
    nano: "_audit.sh:35 audit_log writes ~/.lintel/audit/<category>.jsonl with ts/kind/operator/cycle_id"
    finding: "THREE audit-writing conventions coexist: (1) bin/_audit.sh (the unified writer, v4.0), (2) bin/_jobs.sh writes jobs.jsonl directly (lines 70-71,99-100,137-138), (3) phase skills write bespoke files inline (cycle→cycle-failures.jsonl cycle/SKILL.md:364; ship→hard-rule-stops.jsonl ship/SKILL.md:81; hooks→hooks.jsonl). The unified writer has zero phase-skill callers despite being the v4.0 standard."
    proposed: "Migrate _jobs.sh and phase-skill inline audit writes to source _audit.sh and call audit_log. One writer, consistent record shape (ts/kind/operator/cycle_id + kv)."
    why: "_audit.sh:11-12 promises 'grep-portable, jq-queryable, replay-able'. That promise breaks when jobs.jsonl and hard-rule-stops.jsonl use hand-rolled printf with different field sets (jobs records lack operator/cycle_id; _audit records have them). Uniform observability requires one writer. This is the clearest should-fire-doesn't of the cohort — the writer exists, the standard exists, nobody routes through it."
  D4_entrypoints:
    state: partial
    finding: "Of the 5 intended callers, none are phase-core skills — they are meta-infra/orientator/pack/brief-forge/migration. So _audit.sh observability never touches the sense→capture flow."
    proposed: "Add phase-transition audit events via _audit.sh (category=phase-transition) so the operator can see the cycle progress in one queryable log."
    why: "D13 observability uniformity: every phase should be visible in the same log format, not scattered across jobs.jsonl / cycle-failures.jsonl / hard-rule-stops.jsonl."
peer_comparison:
  strongest_consumer: (intended) meta-infra mode-override
  weakest_consumer: all 8 phase skills (zero route through it)
  uplift_needed: "phase skills + _jobs.sh adopt audit_log; single record shape"
operator_decision_required: yes
priority: high
```

---

## Should-fire-doesn't findings (consolidated)

Ranked by leverage:

1. **Audit writer bypass (L6).** `bin/_audit.sh` is the v4.0 unified writer; `_jobs.sh` and phase skills (cycle, ship) write bespoke JSONL inline, with inconsistent field sets. The standard exists and is unused by the flow it should cover. *Highest-leverage because it is pure consolidation of already-built parts.*
2. **Envelope absence (L4).** 8/8 phase handoffs are ad-hoc report files with no HEAD/BODY/TAIL contract; D1/D2/D3 uniformity cannot exist until `lib/envelope-schema.yaml` ships (Phase 2). *Highest architectural leverage — one schema closes three dimensions across all 8 skills.*
3. **Jobs participation ambiguity (L1).** Only cycle + plan declare `workflow_root`; the 8 phase skills neither spawn nor surface jobs solo, and the model (nested-only vs per-skill) is undocumented. A solo `/li:sense` or `/li:build` is invisible to `/li:status`.
4. **knowhow write-never-read (L2).** Pack declares a `knowhow:` field; no helper, no schema, no consumer. DISCOVER reads lessons.md but not knowhow — the two knowledge channels are unmerged.
5. **Provenance origin hole (L5).** BUILD generates the artifact but writes no provenance breadcrumb; SHIP's source-chain auto-detect infers from 24h-adjacent audit entries that may not exist.
6. **Jobs blocked_until advisory (L1, D5).** Concept doc sells `blocked_until` as a mechanical gate; `_jobs.sh job_update` does not evaluate it.

---

## operator_decision_required count: 4

| Layer | Decision |
|-------|----------|
| L1 jobs | Participation model: nested-only vs per-skill job-touch for the 8 phase skills |
| L2 knowhow | Build order: schema+helper first, then DISCOVER as first consumer — confirm priority vs other v4.0 work |
| L5 provenance | Add BUILD origin breadcrumb + centralize gate predicate in pack? |
| L6 audit | Migrate _jobs.sh + phase-skill inline writes to route through _audit.sh? |

(L3 wiki, L4 envelope = on-schedule design work, no decision needed now.)

---

## Cohort summary

The cross-cutting layers are mostly **built or credibly designed**, but they are **not cross-cutting in practice**. Adoption clusters in three skills — cycle, plan, ship — and is absent from sense, define, discover, build, capture. Of 48 matrix cells, 5 fire and 31 are should-fire-doesn't for layers that exist or are designed.

The two cleanest wins require **no new design**, only consolidation of already-built parts:
- Route all audit writes through `bin/_audit.sh` (L6).
- Resolve the jobs participation model so `/li:status` reflects all in-flight work (L1).

The highest **architectural** leverage is the Phase-2 envelope (L4): a single `lib/envelope-schema.yaml` + validator closes the D1 (head), D2 (tail), and D3 (objects) uniformity gaps across all 8 phase skills simultaneously. It is on-schedule — the risk is only that it slips and the ad-hoc-handoff debt compounds.

NO functionality recommended for removal. Every uplift raises a thin/absent layer toward the depth of the strongest peer (jobs-system sets the bar: helper + hooks + skills + concept doc + ≥1 real consumer).
