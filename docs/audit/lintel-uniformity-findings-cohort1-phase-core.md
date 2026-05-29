# Cohort 1 — phase-core skills uniformity findings

**Cohort:** 1 (phase-core)
**Standard:** `docs/audit/lintel-uniformity-audit-prompt.md` (14 dimensions D1-D14)
**Components audited:** 13 — 8 phase skills (sense, define, discover, plan, build, review, ship, capture) + 5 composites (cycle, fix, research, plan-and-build, review-and-ship)
**Bar discipline:** per-kind FLOOR, no-cut (every `proposed` raises to strongest peer; never remove)
**Date:** 2026-05-29

Two sub-kinds within this cohort have different floors:
- **phase skill** (sense…capture) + **orchestrator** (cycle) — full-body floor
- **composite delegator** (fix, research, plan-and-build, review-and-ship) — thin-by-design, but must still own the dims they delegate-leak

---

## Designed-not-built note (architecture-level, recorded ONCE)

Per the master prompt, the following dimensions are DESIGNED-NOT-BUILT mid-v4.0. They are NOT spammed as per-component "absent" findings — they are tracked here at the architectural level, and each component cell below is marked `n/a — unbuilt, tracked at arch level`.

- **D7 pack-influence (runtime).** WorkProfile *is* wired (it gates compliance depth in define/build/review/ship — real, present). But **pack/WorkProfile as a runtime resolver that changes phase behavior** (D7's stronger reading: "does the active pack measurably change this component?") is unbuilt. No phase reads a pack manifest. SENSE Step 0c hardcodes meta-infra detection rather than resolving a pack. Arch decision needed: pack-resolver pattern (cohort 7) must land before phases can consume it.
- **D9 Brief Forge.** Appears in ZERO phase skills. Hand-offs between phases are file-path conventions (00-state.md + design doc + plan.md trio), not Brief-Forge envelopes with evaluators. The trio (PLAN→BUILD→CAPTURE) is the *de facto* hand-off and is the natural Brief-Forge insertion point. Arch decision needed before any phase declares `brief_forge_handoffs:`.
- **Envelope / wiki.** No phase writes a payload envelope or wiki node. Observability today = scattered per-skill `~/.lintel/analytics/*.jsonl` (real, present in most phase skills) — NOT a unified envelope log. Arch-level.

**Count of designed-not-built dims: 3** (D7-runtime, D9, envelope/wiki). These dominate the cohort's missing-cells but are correctly arch-level, not per-component findings.

---

## Peer ranking

- **Strongest peer (full-body floor):** `plan` — only component with a *written deterministic output contract* (the trio + "callers can rely on these paths"), explicit job integration, module-callable §, dependency-graph step, two MANDATORY gates, nested-job anti-pattern, and an analytics jsonl. `cycle` is a close second (richest orchestration + failure-recovery protocol + telemetry).
- **Strongest composite:** `fix` — has a real pre-flight gate + post-fix soft-prompt that the other three composites lack depth on.
- **Weakest overall:** `review-and-ship` — pure delegator, `status protocol: "inherits"`, no own 00-state write, no observability jsonl, no frontmatter `workflow_root`/necessity, no failure-recovery of its own. `plan-and-build` is nearly as thin.

---

## Per-component finding records

### Phase skills (full-body floor)

```yaml
component: skills/sense/SKILL.md
kind: skill
cohort: 1
dimensions:
  D1_head: { state: present, nano: "body §'You are the SENSE skill — Phase 1'", macro: cycle-entry, high: explicit-invocation-promise, finding: "uniform with cohort", proposed: "-", why: "-" }
  D2_tail: { state: present, nano: "Status protocol DONE/BLOCKED/NEEDS_CONTEXT", macro: cycle, high: status-protocol-promise, finding: "uniform with cohort", proposed: "-", why: "-" }
  D3_objects: { state: partial, nano: "Integration §Reads/Writes", macro: cycle, high: in/out-contract, finding: "Reads/Writes listed but no DETERMINISTIC output contract like plan's 'callers can rely on these paths'", proposed: "add explicit output-contract block (00-state SENSE entry shape is the contract)", why: "achieve caller-relyability; plan does it better — steal its pattern" }
  D4_entrypoints: { state: present, nano: "When to use / Hop-in support", macro: cycle+standalone, high: entrypoint-coverage, finding: "uniform with cohort", proposed: "-", why: "-" }
  D5_checkpoints: { state: present, nano: "Step 7 writes 00-state.md", macro: resume, high: resumability, finding: "uniform with cohort", proposed: "-", why: "-" }
  D6_recovery: { state: present, nano: "Failure recovery § (profile malformed / state unreadable / perms)", macro: resume, high: recovery-promise, finding: "strongest recovery § in cohort — names tmp-fallback path", proposed: "-", why: "-" }
  D7_packinfluence: { state: n-a, nano: "tracked at arch level", macro: cohort7, high: pack-driven-behavior, finding: "n/a — unbuilt, tracked at arch level (SENSE Step 0c hardcodes meta-infra detect rather than resolving a pack)", proposed: "arch-level", why: "arch-level" }
  D8_frontmatter: { state: partial, nano: "frontmatter: lacks necessity, expected_inputs/outputs, tokens_est_typical", macro: cycle, high: frontmatter-completeness, finding: "cycle references phase frontmatter tokens_est_typical but SENSE doesn't declare it; no necessity field", proposed: "add necessity: REQUIRED, gap_if_skipped, tokens_est_typical to frontmatter", why: "cycle's progress-output PROMISES tokens_est_typical — it's a broken reference today" }
  D9_briefforge: { state: n-a, nano: "tracked at arch level", macro: handoff, high: brief-forge-at-handoff, finding: "n/a — unbuilt", proposed: "arch-level", why: "arch-level" }
  D10_lessons: { state: present, nano: "Step 0a invokes /li:lessons-surface; Step 5 light-scan", macro: cross-session-memory, high: lessons-consulted-not-just-written, finding: "BEST lessons integration in cohort — actively surfaces, closes L-001/L-002 loop", proposed: "-", why: "-" }
  D11_subagent: { state: n-a, nano: "Anti-patterns: 'no expensive grep'", macro: context-budget, high: dedicated-vs-inline, finding: "n/a-for-kind — SENSE is deliberately read-only/light, subagent spawn would violate its lightness contract", proposed: "-", why: "-" }
  D12_failure: { state: present, nano: "Failure recovery § warn-but-continue", macro: cycle, high: failure-mode-consistency, finding: "uniform with cohort", proposed: "-", why: "-" }
  D13_observability: { state: partial, nano: "writes 00-state but NO analytics jsonl (define/plan/build/review have one)", macro: observability, high: operator-can-see-it-ran, finding: "SENSE writes no ~/.lintel/analytics/*.jsonl — inconsistent with peers", proposed: "add sense-metrics.jsonl (intent_detected, mode_recommended, context_budget)", why: "uniform observability; cheap; SENSE's intent-detection accuracy is worth tracking" }
  D14_necessity: { state: implicit, nano: "Anti-patterns: 'always first in cycle'", macro: cycle, high: necessity-declaration, finding: "necessity stated in prose ('always first') not in a declared field", proposed: "add necessity: REQUIRED + gap_if_skipped", why: "Architect declares per-section; we don't yet (X5)" }
peer_comparison: { strongest_peer_in_cohort: plan, this_component_depth: at-bar, uplift_needed: "output-contract block + analytics jsonl + necessity/tokens_est frontmatter" }
operator_decision_required: no
priority: medium
```

```yaml
component: skills/define/SKILL.md
kind: skill
cohort: 1
dimensions:
  D1_head: { state: present, nano: "body §; hard-gate line 17", macro: cycle, high: explicit-invocation, finding: "uniform with cohort", proposed: "-", why: "-" }
  D2_tail: { state: present, nano: "Status protocol + Step 12 approval gate", macro: cycle, high: status-protocol, finding: "uniform; richest exit (4 status states incl DONE_WITH_CONCERNS)", proposed: "-", why: "-" }
  D3_objects: { state: partial, nano: "Integration Reads/Writes", macro: cycle, high: in/out-contract, finding: "output (design doc) path well-specified but not framed as deterministic contract for PLAN to rely on", proposed: "add output-contract block naming design-doc path PLAN consumes", why: "plan→build trio is contractual; DEFINE→PLAN should be too" }
  D4_entrypoints: { state: present, nano: "Hop-in support § (4 entry paths + skip-conditions)", macro: cycle, high: entrypoint-coverage, finding: "BEST entrypoint doc in cohort — explicit skip-conditions", proposed: "-", why: "-" }
  D5_checkpoints: { state: present, nano: "writes 00-state DEFINE entry", macro: resume, high: resumability, finding: "uniform", proposed: "-", why: "-" }
  D6_recovery: { state: present, nano: "Failure recovery § (AskUserQuestion unavailable → BLOCKED)", macro: cycle, high: recovery, finding: "uniform", proposed: "-", why: "-" }
  D7_packinfluence: { state: n-a, nano: arch-level, macro: cohort7, high: pack-driven, finding: "n/a — unbuilt. Role-lens overlay (Step 8) is the closest analog and IS built", proposed: "arch-level", why: "arch-level" }
  D8_frontmatter: { state: partial, nano: "frontmatter lacks necessity/tokens_est/brief_forge_handoffs", macro: cycle, high: frontmatter-completeness, finding: "same gap as cohort", proposed: "add necessity, gap_if_skipped, tokens_est_typical", why: "X5" }
  D9_briefforge: { state: n-a, nano: arch-level, macro: handoff, high: brief-forge, finding: "n/a. DEFINE→PLAN handoff is prime Brief-Forge candidate", proposed: "arch-level", why: "arch-level" }
  D10_lessons: { state: present, nano: "Integration Reads tasks/lessons.md, tasks/memory.md", macro: memory, high: lessons-consulted, finding: "reads lessons but no active surface-step like SENSE Step 0a", proposed: "add lessons-surface call at context-gather (Step 1)", why: "SENSE does it better — mirror its pattern" }
  D11_subagent: { state: present, nano: "Step 7 codex/subagent; Step 11 CodeReviewer spec-review", macro: context-budget, high: dedicated-vs-inline, finding: "strong — adversarial spec review via dispatched subagent", proposed: "-", why: "-" }
  D12_failure: { state: present, nano: "Failure recovery § (4 cases)", macro: cycle, high: failure-mode, finding: "uniform", proposed: "-", why: "-" }
  D13_observability: { state: present, nano: "Step 11 writes spec-review.jsonl", macro: observability, high: operator-visibility, finding: "uniform (has analytics jsonl)", proposed: "-", why: "-" }
  D14_necessity: { state: implicit, nano: "When NOT to use lists skip-conditions", macro: cycle, high: necessity, finding: "skip-conditions stated; necessity not a field", proposed: "add necessity: STRONGLY_RECOMMENDED (REQUIRED unless hotfix/ship-only)", why: "X5" }
peer_comparison: { strongest_peer_in_cohort: plan, this_component_depth: at-bar, uplift_needed: "output-contract block + active lessons-surface + necessity field" }
operator_decision_required: no
priority: low
```

```yaml
component: skills/discover/SKILL.md
kind: skill
cohort: 1
dimensions:
  D1_head: { state: present, nano: "body §; 'principle: don't reinvent'", macro: cycle, high: explicit-invocation, finding: "uniform", proposed: "-", why: "-" }
  D2_tail: { state: present, nano: "Status protocol; Step 8 writes discover-report", macro: cycle, high: status-protocol, finding: "uniform", proposed: "-", why: "-" }
  D3_objects: { state: present, nano: "Step 8 discover-report.md YAML schema is FULLY specified", macro: cycle, high: in/out-contract, finding: "strongest output-shape in cohort after plan — full report template", proposed: "-", why: "-" }
  D4_entrypoints: { state: present, nano: "Hop-in + skip-conditions", macro: cycle, high: entrypoint-coverage, finding: "uniform", proposed: "-", why: "-" }
  D5_checkpoints: { state: present, nano: "Step 9 00-state append", macro: resume, high: resumability, finding: "uniform", proposed: "-", why: "-" }
  D6_recovery: { state: present, nano: "Failure recovery § (scope too large / no ADRs)", macro: cycle, high: recovery, finding: "uniform", proposed: "-", why: "-" }
  D7_packinfluence: { state: n-a, nano: arch-level, macro: cohort7, high: pack-driven, finding: "n/a — unbuilt", proposed: "arch-level", why: "arch-level" }
  D8_frontmatter: { state: partial, nano: "lacks necessity/tokens_est", macro: cycle, high: frontmatter, finding: "cohort gap", proposed: "add necessity, tokens_est_typical", why: "X5" }
  D9_briefforge: { state: n-a, nano: arch-level, macro: handoff, high: brief-forge, finding: "n/a", proposed: "arch-level", why: "arch-level" }
  D10_lessons: { state: present, nano: "Step 3 lessons scan filtered-by-relevance + invokes /li:lessons", macro: memory, high: lessons-consulted, finding: "good — filters lessons to wedge", proposed: "-", why: "-" }
  D11_subagent: { state: partial, nano: "Steps 5-6 recommend agents for PLAN but DISCOVER itself doesn't spawn", macro: context-budget, high: dedicated-vs-inline, finding: "DISCOVER does heavy grep/glob inline; could delegate codebase-map to a subagent to keep main context clean", proposed: "optionally spawn a map subagent for large wedges (>200 files)", why: "keeps DISCOVER's own context lean; ReadOnly-style agent fits" }
  D13_observability: { state: partial, nano: "no analytics jsonl", macro: observability, high: visibility, finding: "writes 00-state + report but no discover-metrics.jsonl", proposed: "add discover-metrics.jsonl (files_mapped, adrs_found, agents_recommended)", why: "uniform observability" }
  D12_failure: { state: present, nano: "Failure recovery §", macro: cycle, high: failure-mode, finding: "uniform", proposed: "-", why: "-" }
  D14_necessity: { state: implicit, nano: "skip-conditions in body", macro: cycle, high: necessity, finding: "implicit", proposed: "add necessity: STRONGLY_RECOMMENDED + gap_if_skipped (PLAN flies blind on prior decisions)", why: "X5" }
peer_comparison: { strongest_peer_in_cohort: plan, this_component_depth: at-bar, uplift_needed: "analytics jsonl + necessity field + optional map-subagent for large wedges" }
operator_decision_required: no
priority: low
```

```yaml
component: skills/plan/SKILL.md
kind: skill
cohort: 1
dimensions:
  D1_head: { state: present, nano: "frontmatter workflow_root: true; body §; job-begin on workflow_root", macro: cycle+standalone+sub-module, high: explicit-invocation, finding: "STRONGEST head — 3 invocation modes + job spawn declared", proposed: "-", why: "-" }
  D2_tail: { state: present, nano: "Status protocol; Step 10 founder gate; output contract §", macro: cycle, high: status-protocol, finding: "strongest tail — deterministic output contract", proposed: "-", why: "-" }
  D3_objects: { state: present, nano: "Output contract § ('callers can rely on these paths existing post-DONE')", macro: cold-executor-handoff, high: in/out-contract, finding: "THE BAR — only component with explicit caller-relyable contract", proposed: "-", why: "-" }
  D4_entrypoints: { state: present, nano: "Module-callable § (3 modes) + --called-by/--no-job flags", macro: cross-workflow, high: entrypoint-coverage, finding: "BAR — handles nested-job anti-pattern explicitly", proposed: "-", why: "-" }
  D5_checkpoints: { state: present, nano: "Step 11 .planner-checkpoint.md + 00-state", macro: resume, high: resumability, finding: "BAR — dedicated checkpoint file for /li:resume", proposed: "-", why: "-" }
  D6_recovery: { state: present, nano: "Failure recovery § (cost-exceeds / reviewer-unavailable / gap / 3x-reject)", macro: cycle, high: recovery, finding: "BAR", proposed: "-", why: "-" }
  D7_packinfluence: { state: n-a, nano: arch-level, macro: cohort7, high: pack-driven, finding: "n/a — unbuilt. Reads HARD-RULES if WorkProfile=on (that part IS built)", proposed: "arch-level", why: "arch-level" }
  D8_frontmatter: { state: partial, nano: "declares workflow_root but NOT necessity/tokens_est/brief_forge_handoffs/navigation", macro: cycle, high: frontmatter, finding: "even the bar lacks necessity + nav fields", proposed: "add necessity, tokens_est_typical, navigation (it's a workflow_root)", why: "master prompt D8 says workflow_root must declare navigation" }
  D9_briefforge: { state: n-a, nano: arch-level, macro: handoff, high: brief-forge, finding: "n/a — but the trio output IS the natural Brief-Forge payload", proposed: "arch-level", why: "arch-level" }
  D10_lessons: { state: absent, nano: "Integration Reads has no lessons.md", macro: memory, high: lessons-consulted, finding: "PLAN reads design+discover+ADRs+principles but NOT lessons.md directly (relies on DISCOVER having surfaced them)", proposed: "add lessons consult at Step 1 OR explicitly document 'lessons inherited via discover-report'", why: "if DISCOVER skipped (hotfix path into PLAN), lessons never reach PLAN — gap" }
  D11_subagent: { state: present, nano: "Step 9 two-stage CodeReviewer; recommended-agents §", macro: context-budget, high: dedicated-vs-inline, finding: "BAR", proposed: "-", why: "-" }
  D12_failure: { state: present, nano: "Failure recovery §", macro: cycle, high: failure-mode, finding: "BAR", proposed: "-", why: "-" }
  D13_observability: { state: present, nano: "Writes plan-metrics.jsonl", macro: observability, high: visibility, finding: "uniform", proposed: "-", why: "-" }
  D14_necessity: { state: implicit, nano: "skip-conditions in body", macro: cycle, high: necessity, finding: "implicit even at the bar", proposed: "add necessity: REQUIRED (unless hotfix/trivial) + gap_if_skipped", why: "X5" }
peer_comparison: { strongest_peer_in_cohort: plan, this_component_depth: at-bar, uplift_needed: "necessity + navigation + tokens_est frontmatter; lessons-consult path for hotfix-into-PLAN" }
operator_decision_required: yes
priority: high
```

```yaml
component: skills/build/SKILL.md
kind: skill
cohort: 1
dimensions:
  D1_head: { state: present, nano: "body §; Step 1 pre-flight checks", macro: cycle, high: explicit-invocation, finding: "strong head — pre-flight validates branch/hooks/plan-status", proposed: "-", why: "-" }
  D2_tail: { state: present, nano: "Status protocol; Step 7 00-state", macro: cycle, high: status-protocol, finding: "uniform", proposed: "-", why: "-" }
  D3_objects: { state: partial, nano: "Integration Reads plan.md MANDATORY; Writes source+build-log", macro: cycle, high: in/out-contract, finding: "input contract clear (plan.md), output is code+build-log — not framed as deterministic contract REVIEW relies on", proposed: "add output-contract block (build-log shape + diff-range REVIEW consumes)", why: "REVIEW reads build-log — make it contractual" }
  D4_entrypoints: { state: present, nano: "Hop-in + skip-conditions", macro: cycle, high: entrypoint-coverage, finding: "uniform", proposed: "-", why: "-" }
  D5_checkpoints: { state: present, nano: "Step 4 continuous-checkpoint WIP commits + Step 5 build-log per task", macro: resume, high: resumability, finding: "BEST checkpoint granularity — per-task WIP commits, /li:context-restore resumable", proposed: "-", why: "-" }
  D6_recovery: { state: present, nano: "Failure recovery § (implementer BLOCKED root-cause matrix)", macro: cycle, high: recovery, finding: "BAR-level recovery — root-cause classification", proposed: "-", why: "-" }
  D7_packinfluence: { state: n-a, nano: arch-level, macro: cohort7, high: pack-driven, finding: "n/a — unbuilt. HARD-RULE hooks fire if WorkProfile=on (built)", proposed: "arch-level", why: "arch-level" }
  D8_frontmatter: { state: partial, nano: "lacks necessity/tokens_est", macro: cycle, high: frontmatter, finding: "cohort gap", proposed: "add necessity, tokens_est_typical", why: "X5" }
  D9_briefforge: { state: n-a, nano: arch-level, macro: handoff, high: brief-forge, finding: "n/a — note: BUILD ALREADY does Brief-Forge-like work informally (Step 3a gives implementer 'full task text + scene-setting context' = a curated brief). This is the de-facto pattern Brief Forge should formalize.", proposed: "arch-level (flag as exemplar)", why: "BUILD's implementer-brief is what Brief Forge should standardize" }
  D10_lessons: { state: absent, nano: "Integration Reads: no lessons.md", macro: memory, high: lessons-consulted, finding: "BUILD doesn't consult lessons during execution (e.g., 'don't mock Azure SDK' lesson never reaches implementer subagent)", proposed: "pass relevant lessons into implementer subagent brief at Step 3a", why: "CAPTURE writes lessons but BUILD never reads them = write-only memory (the L-001/L-002 anti-pattern SENSE fixed for itself)" }
  D11_subagent: { state: present, nano: "Step 3a fresh implementer per task + two-stage reviewer; sequential-not-parallel rule", macro: context-budget, high: dedicated-vs-inline, finding: "BAR — best subagent discipline (curated brief, model selection, sequential)", proposed: "-", why: "-" }
  D12_failure: { state: present, nano: "Failure recovery § (5 cases incl hard-rule-repeat)", macro: cycle, high: failure-mode, finding: "BAR", proposed: "-", why: "-" }
  D13_observability: { state: present, nano: "build-log.md + build-metrics.jsonl", macro: observability, high: visibility, finding: "uniform", proposed: "-", why: "-" }
  D14_necessity: { state: implicit, nano: "skip-conditions", macro: cycle, high: necessity, finding: "implicit", proposed: "add necessity: REQUIRED + gap_if_skipped", why: "X5" }
peer_comparison: { strongest_peer_in_cohort: plan, this_component_depth: at-bar, uplift_needed: "lessons-into-implementer-brief (load-bearing) + output-contract block + necessity field" }
operator_decision_required: yes
priority: high
```

```yaml
component: skills/review/SKILL.md
kind: skill
cohort: 1
dimensions:
  D1_head: { state: present, nano: "body §; Step 1 load context + scope detect", macro: cycle, high: explicit-invocation, finding: "uniform", proposed: "-", why: "-" }
  D2_tail: { state: present, nano: "Status protocol; verdict block in review-report", macro: cycle, high: status-protocol, finding: "strong tail — explicit ship-ready verdict + loop-back recommendation", proposed: "-", why: "-" }
  D3_objects: { state: present, nano: "Step 7 review-report.md + compliance-report.md schemas fully specified", macro: cycle, high: in/out-contract, finding: "strong — two report shapes specified", proposed: "-", why: "-" }
  D4_entrypoints: { state: present, nano: "Hop-in (--diff, --pr) + skip-conditions", macro: cycle, high: entrypoint-coverage, finding: "good — concrete CLI flags", proposed: "-", why: "-" }
  D5_checkpoints: { state: present, nano: "Step 8 00-state append", macro: resume, high: resumability, finding: "uniform", proposed: "-", why: "-" }
  D6_recovery: { state: present, nano: "Failure recovery § (subagent 529, voice persistent-fail, hard-rule)", macro: cycle, high: recovery, finding: "BAR — names primary-reviewer-unavailable → BLOCKED", proposed: "-", why: "-" }
  D7_packinfluence: { state: partial, nano: "Stage 3 gates fire per WorkProfile + voice_tier + audience", macro: cohort7, high: pack-driven, finding: "CLOSEST to real pack-influence in cohort — WorkProfile genuinely changes which Stage-3 gates fire. The runtime-pack-resolver layer is still arch-level, but WorkProfile-branching IS built here", proposed: "arch-level for pack; document WorkProfile-branching as the working precedent", why: "REVIEW is the exemplar for how pack-influence should look once built" }
  D8_frontmatter: { state: partial, nano: "lacks necessity/tokens_est", macro: cycle, high: frontmatter, finding: "cohort gap", proposed: "add necessity, tokens_est_typical", why: "X5" }
  D9_briefforge: { state: n-a, nano: arch-level, macro: handoff, high: brief-forge, finding: "n/a", proposed: "arch-level", why: "arch-level" }
  D10_lessons: { state: absent, nano: "Integration Reads: no lessons.md", macro: memory, high: lessons-consulted, finding: "REVIEW doesn't check lessons (past review findings / recurring bug patterns) before reviewing", proposed: "consult lessons for known-recurring findings at Step 1", why: "same write-only-memory gap as BUILD" }
  D11_subagent: { state: present, nano: "3-stage dispatched subagents + concentrated agent pool §", macro: context-budget, high: dedicated-vs-inline, finding: "BAR — separate dispatch per stage", proposed: "-", why: "-" }
  D12_failure: { state: present, nano: "Failure recovery §", macro: cycle, high: failure-mode, finding: "BAR", proposed: "-", why: "-" }
  D13_observability: { state: present, nano: "review-metrics.jsonl", macro: observability, high: visibility, finding: "uniform", proposed: "-", why: "-" }
  D14_necessity: { state: implicit, nano: "skip-conditions", macro: cycle, high: necessity, finding: "implicit", proposed: "add necessity: REQUIRED (gate before SHIP) + gap_if_skipped", why: "X5" }
peer_comparison: { strongest_peer_in_cohort: plan, this_component_depth: at-bar, uplift_needed: "lessons-consult at Step 1 + necessity field" }
operator_decision_required: no
priority: medium
```

```yaml
component: skills/ship/SKILL.md
kind: skill
cohort: 1
dimensions:
  D1_head: { state: present, nano: "body §; Step 1 pre-flight MANDATORY", macro: cycle, high: explicit-invocation, finding: "strong — pre-flight ship-readiness", proposed: "-", why: "-" }
  D2_tail: { state: present, nano: "Status protocol; Step 11 00-state", macro: cycle, high: status-protocol, finding: "uniform", proposed: "-", why: "-" }
  D3_objects: { state: partial, nano: "Integration Reads/Writes (PR, release-notes, deliverables)", macro: cycle, high: in/out-contract, finding: "many outputs listed; no single deterministic contract for CAPTURE", proposed: "add output-contract block (PR url + commit range CAPTURE consumes)", why: "CAPTURE reads SHIP outputs — make contractual" }
  D4_entrypoints: { state: present, nano: "Hop-in + ship-path § (pr/direct_main/demo)", macro: cycle, high: entrypoint-coverage, finding: "good — 3 ship paths", proposed: "-", why: "-" }
  D5_checkpoints: { state: present, nano: "Step 11 00-state; hard-rule-stops.jsonl", macro: resume, high: resumability, finding: "uniform", proposed: "-", why: "-" }
  D6_recovery: { state: present, nano: "Failure recovery § (6 cases incl gh-unavailable, EV2-fail, customer-delay)", macro: cycle, high: recovery, finding: "BAR — most recovery cases in cohort (6)", proposed: "-", why: "-" }
  D7_packinfluence: { state: partial, nano: "gates fire per WorkProfile + audience + voice_tier", macro: cohort7, high: pack-driven, finding: "like REVIEW — WorkProfile genuinely branches behavior; runtime-pack-resolver still arch-level", proposed: "arch-level", why: "arch-level" }
  D8_frontmatter: { state: partial, nano: "voice: mixed; lacks necessity/tokens_est", macro: cycle, high: frontmatter, finding: "cohort gap", proposed: "add necessity, tokens_est_typical", why: "X5" }
  D9_briefforge: { state: n-a, nano: arch-level, macro: handoff, high: brief-forge, finding: "n/a", proposed: "arch-level", why: "arch-level" }
  D10_lessons: { state: absent, nano: "Integration Reads: no lessons.md", macro: memory, high: lessons-consulted, finding: "SHIP doesn't consult ship-related lessons (e.g., 'this customer needs transparency note')", proposed: "consult lessons for ship-gotchas at Step 2", why: "write-only-memory gap" }
  D11_subagent: { state: present, nano: "recommended-agents §; 4-gate pipeline dispatches", macro: context-budget, high: dedicated-vs-inline, finding: "good", proposed: "-", why: "-" }
  D12_failure: { state: present, nano: "Failure recovery §", macro: cycle, high: failure-mode, finding: "BAR", proposed: "-", why: "-" }
  D13_observability: { state: partial, nano: "provenance-log + hard-rule-stops.jsonl but NO ship-metrics.jsonl", macro: observability, high: visibility, finding: "has audit logs but no ship-metrics analytics jsonl like peers", proposed: "add ship-metrics.jsonl (ship_path, gates_passed, pr_url)", why: "uniform observability" }
  D14_necessity: { state: implicit, nano: "skip-conditions", macro: cycle, high: necessity, finding: "implicit", proposed: "add necessity + gap_if_skipped", why: "X5" }
peer_comparison: { strongest_peer_in_cohort: plan, this_component_depth: at-bar, uplift_needed: "lessons-consult + ship-metrics jsonl + output-contract + necessity field" }
operator_decision_required: no
priority: medium
```

```yaml
component: skills/capture/SKILL.md
kind: skill
cohort: 1
dimensions:
  D1_head: { state: present, nano: "body §; Step 1 cycle-history aggregation", macro: cycle, high: explicit-invocation, finding: "uniform", proposed: "-", why: "-" }
  D2_tail: { state: present, nano: "Status protocol; Step 11 closing message", macro: cycle, high: status-protocol, finding: "strong tail — explicit cycle-complete closing", proposed: "-", why: "-" }
  D3_objects: { state: present, nano: "Step 10 00-state final + artifacts list; reaffirms trio contract", macro: cold-executor, high: in/out-contract, finding: "strong — consumes plan's trio contract, reaffirms it", proposed: "-", why: "-" }
  D4_entrypoints: { state: present, nano: "Hop-in (standalone reflection)", macro: cycle, high: entrypoint-coverage, finding: "uniform", proposed: "-", why: "-" }
  D5_checkpoints: { state: present, nano: "Step 10 00-state final entry", macro: resume, high: resumability, finding: "uniform", proposed: "-", why: "-" }
  D6_recovery: { state: present, nano: "Failure recovery § (lessons.md/template missing)", macro: cycle, high: recovery, finding: "uniform", proposed: "-", why: "-" }
  D7_packinfluence: { state: n-a, nano: arch-level, macro: cohort7, high: pack-driven, finding: "n/a — unbuilt", proposed: "arch-level", why: "arch-level" }
  D8_frontmatter: { state: partial, nano: "lacks necessity/tokens_est", macro: cycle, high: frontmatter, finding: "cohort gap", proposed: "add necessity, tokens_est_typical", why: "X5" }
  D9_briefforge: { state: n-a, nano: arch-level, macro: handoff, high: brief-forge, finding: "n/a — trio-reaffirm IS the handoff-production step; Brief-Forge insertion point", proposed: "arch-level", why: "arch-level" }
  D10_lessons: { state: present, nano: "Steps 2-3 lessons capture + promote (WRITES lessons + global promote)", macro: memory, high: lessons-flow, finding: "BAR for lessons-WRITE side. But it's write-only — CAPTURE is the producer; SENSE is the only consumer. The operator-relation thread (X3) is half-built here.", proposed: "-", why: "this is the write half of the loop; the read half is missing in BUILD/REVIEW/SHIP/PLAN" }
  D11_subagent: { state: present, nano: "Step 6 dogfood-trio subagent; recommended-agents §", macro: context-budget, high: dedicated-vs-inline, finding: "good", proposed: "-", why: "-" }
  D12_failure: { state: present, nano: "Failure recovery §", macro: cycle, high: failure-mode, finding: "uniform", proposed: "-", why: "-" }
  D13_observability: { state: present, nano: "operator-profile.jsonl + cycle-completion.jsonl + retros", macro: observability, high: visibility, finding: "BAR — richest observability (profile + completion + retro)", proposed: "-", why: "-" }
  D14_necessity: { state: implicit, nano: "When NOT to use", macro: cycle, high: necessity, finding: "implicit", proposed: "add necessity: STRONGLY_RECOMMENDED + gap_if_skipped (cross-session memory lost)", why: "X5" }
peer_comparison: { strongest_peer_in_cohort: plan, this_component_depth: at-bar, uplift_needed: "necessity field; (cohort-level: close the lessons read-loop so CAPTURE's writes get consumed beyond SENSE)" }
operator_decision_required: no
priority: medium
```

### Orchestrator

```yaml
component: skills/cycle/SKILL.md
kind: skill (orchestrator, workflow_root)
cohort: 1
dimensions:
  D1_head: { state: present, nano: "frontmatter workflow_root; Step 0 dry-run; Step 1 parse + Step 2 SENSE-always", macro: top-level-entry, high: explicit-invocation, finding: "BAR for orchestration head — dry-run + flag-parse", proposed: "-", why: "-" }
  D2_tail: { state: present, nano: "Status protocol (DONE/CONCERNS/BLOCKED/ABORTED); Step 8 complete", macro: top-level, high: status-protocol, finding: "BAR — only component with ABORTED state", proposed: "-", why: "-" }
  D3_objects: { state: present, nano: "Step 4 propagates phase-output→next-input", macro: cross-phase, high: in/out-contract, finding: "good — declares inter-phase propagation", proposed: "-", why: "-" }
  D4_entrypoints: { state: present, nano: "Hop-in --from + dependency verification", macro: top-level, high: entrypoint-coverage, finding: "BAR — verifies phase deps on hop-in", proposed: "-", why: "-" }
  D5_checkpoints: { state: present, nano: "Step 4 00-state per phase; cycle_paused flag", macro: resume, high: resumability, finding: "BAR — pause/resume orchestration", proposed: "-", why: "-" }
  D6_recovery: { state: present, nano: "Step 7 + Failure recovery § (Architect FAILURE RECOVERY PROTOCOL)", macro: top-level, high: recovery, finding: "BAR — retry/skip/loop-back/abort + cycle-failures.jsonl", proposed: "-", why: "-" }
  D7_packinfluence: { state: partial, nano: "mode-presets set compliance level; meta-infra gates M1-M4", macro: cohort7, high: pack-driven, finding: "mode-presets are the closest thing to packs that EXISTS — they branch phases/compliance/voice. Runtime pack-resolver still arch-level, but presets are the working precedent.", proposed: "arch-level; document mode-presets as proto-packs", why: "presets ARE the pack-influence pattern, just hardcoded not resolved" }
  D8_frontmatter: { state: partial, nano: "workflow_root declared; references tokens_est_typical that phases don't declare; no necessity/navigation", macro: top-level, high: frontmatter, finding: "cycle's Step-4 progress output reads phase frontmatter tokens_est_typical — but NO phase declares it (broken reference)", proposed: "add tokens_est_typical to all 8 phases + navigation to cycle", why: "load-bearing: cycle PROMISES per-phase token estimates it can't read today" }
  D9_briefforge: { state: n-a, nano: arch-level, macro: handoff, high: brief-forge, finding: "n/a — cycle is where inter-phase Brief-Forge would orchestrate", proposed: "arch-level", why: "arch-level" }
  D10_lessons: { state: absent, nano: "Integration Reads: profile + 00-state, no lessons", macro: memory, high: lessons-consulted, finding: "orchestrator doesn't surface lessons (delegates to SENSE which does)", proposed: "document that lessons-surface is SENSE's job, not duplicate", why: "elegance: don't double-surface; SENSE owns it" }
  D11_subagent: { state: n-a, nano: "orchestrator delegates to phase-skills not subagents", macro: context-budget, high: dedicated-vs-inline, finding: "n/a-for-kind — cycle chains skills; phases spawn subagents", proposed: "-", why: "-" }
  D12_failure: { state: present, nano: "Failure recovery § (Architect protocol)", macro: top-level, high: failure-mode, finding: "BAR", proposed: "-", why: "-" }
  D13_observability: { state: present, nano: "cycle-runs.jsonl + cycle-failures.jsonl", macro: observability, high: visibility, finding: "BAR", proposed: "-", why: "-" }
  D14_necessity: { state: implicit, nano: "When NOT to use", macro: top-level, high: necessity, finding: "implicit", proposed: "add necessity field", why: "X5" }
peer_comparison: { strongest_peer_in_cohort: plan, this_component_depth: at-bar, uplift_needed: "fix the tokens_est_typical broken reference (add field to phases); navigation frontmatter" }
operator_decision_required: yes
priority: high
```

### Composites (thin-delegator floor)

The four composites are intentionally thin (they delegate to `/li:cycle --mode/--from/--to`). The thin-delegator FLOOR is: own pre-flight, own post-output summary, declare delegation, declare anti-patterns. Where they fall below floor: **status protocol "inherits" with no own exit semantics**, **no own 00-state/observability**, **no `workflow_root` despite being operator entry-points**, **no necessity/gap field**. `fix` is the strongest composite (real pre-flight gate + post-fix soft-prompt); `review-and-ship` and `plan-and-build` are weakest.

```yaml
component: skills/fix/SKILL.md
kind: skill (composite-delegator)
cohort: 1
dimensions:
  D1_head: { state: present, nano: "Step 1 pre-flight AskUserQuestion (hotfix-appropriate?)", macro: hotfix-entry, high: explicit-invocation, finding: "STRONGEST composite head — real gate", proposed: "-", why: "-" }
  D2_tail: { state: partial, nano: "'Status protocol: Inherits from /li:cycle'", macro: hotfix, high: status-protocol, finding: "no own exit semantics — pure inherit", proposed: "add own DONE/BLOCKED reflecting composite-level outcome (e.g. 'hotfix shipped' vs 'underlying cycle BLOCKED')", why: "operator invoking /li:fix should see fix-level status, not cycle internals" }
  D3_objects: { state: partial, nano: "Integration: 'Delegates, no new behavior'", macro: hotfix, high: in/out-contract, finding: "no in/out contract of its own", proposed: "declare: in=bug-description, out=PR/commit", why: "floor: composite should state its own contract" }
  D4_entrypoints: { state: present, nano: "Hop-in: 'No — itself a hop-in shortcut'", macro: hotfix, high: entrypoint-coverage, finding: "uniform with composites", proposed: "-", why: "-" }
  D5_checkpoints: { state: absent, nano: "no own 00-state write", macro: resume, high: resumability, finding: "delegates checkpointing to phases (acceptable for delegator)", proposed: "document 'checkpoints owned by delegated phases'", why: "make the delegation explicit rather than silent" }
  D6_recovery: { state: partial, nano: "Step 1 suggests /li:investigate if hesitant", macro: hotfix, high: recovery, finding: "light recovery (pre-flight redirect only)", proposed: "document 'recovery inherited from cycle'", why: "floor: state where recovery lives" }
  D7_packinfluence: { state: n-a, nano: arch-level, macro: cohort7, high: pack-driven, finding: "n/a — but DOES set compliance=minimal via preset", proposed: "arch-level", why: "arch-level" }
  D8_frontmatter: { state: partial, nano: "no workflow_root despite being an operator entry-point; no necessity", macro: hotfix, high: frontmatter, finding: "composites are entry-points but lack workflow_root (so no job spawns on /li:fix)", proposed: "decide: should composites spawn jobs? if yes add workflow_root", why: "operator-decision — /li:fix is a real entry-point; should it appear in jobs?" }
  D9_briefforge: { state: n-a, nano: arch-level, macro: handoff, high: brief-forge, finding: "n/a", proposed: "arch-level", why: "arch-level" }
  D10_lessons: { state: implicit, nano: "Step 3 soft-prompts lessons-promote post-fix", macro: memory, high: lessons-flow, finding: "good — reminds operator to capture fix-pattern", proposed: "-", why: "-" }
  D11_subagent: { state: n-a, nano: "delegator", macro: context-budget, high: dedicated-vs-inline, finding: "n/a-for-kind", proposed: "-", why: "-" }
  D12_failure: { state: partial, nano: "inherits cycle failure", macro: hotfix, high: failure-mode, finding: "no own failure mode", proposed: "document inherited failure path", why: "floor" }
  D13_observability: { state: absent, nano: "no own jsonl; cycle logs cycle-runs", macro: observability, high: visibility, finding: "operator can't distinguish /li:fix invocation from /li:cycle --mode hotfix in logs", proposed: "tag cycle-runs.jsonl with invoked_via: fix", why: "uniform observability — know which shortcut was used" }
  D14_necessity: { state: implicit, nano: "When NOT to use", macro: hotfix, high: necessity, finding: "implicit", proposed: "add necessity: OPTIONAL (convenience shortcut)", why: "X5" }
peer_comparison: { strongest_peer_in_cohort: plan, strongest_composite: fix, this_component_depth: at-composite-bar, uplift_needed: "own status semantics + in/out contract + invoked_via log tag + workflow_root decision" }
operator_decision_required: yes
priority: medium
```

```yaml
component: skills/research/SKILL.md
kind: skill (composite-delegator)
cohort: 1
dimensions:
  D1_head: { state: present, nano: "Step 1 pre-flight AskUserQuestion", macro: research-entry, high: explicit-invocation, finding: "uniform with composites", proposed: "-", why: "-" }
  D2_tail: { state: partial, nano: "'Inherits from /li:cycle'", macro: research, high: status-protocol, finding: "no own exit semantics", proposed: "add own status (research-complete vs blocked-on-scope)", why: "same as fix" }
  D3_objects: { state: present, nano: "Step 3 lists output artifacts (design doc + discover-report)", macro: research, high: in/out-contract, finding: "BETTER than fix — names concrete outputs", proposed: "-", why: "-" }
  D4_entrypoints: { state: present, nano: "Hop-in n/a", macro: research, high: entrypoint-coverage, finding: "uniform", proposed: "-", why: "-" }
  D5_checkpoints: { state: absent, nano: "no own 00-state", macro: resume, high: resumability, finding: "delegates", proposed: "document delegation", why: "floor" }
  D6_recovery: { state: absent, nano: "no own recovery", macro: research, high: recovery, finding: "inherits", proposed: "document inherited", why: "floor" }
  D7_packinfluence: { state: n-a, nano: arch-level, macro: cohort7, high: pack-driven, finding: "n/a (sets compliance=none)", proposed: "arch-level", why: "arch-level" }
  D8_frontmatter: { state: partial, nano: "no workflow_root/necessity", macro: research, high: frontmatter, finding: "same composite gap", proposed: "workflow_root decision + necessity", why: "operator-decision" }
  D9_briefforge: { state: n-a, nano: arch-level, macro: handoff, high: brief-forge, finding: "n/a", proposed: "arch-level", why: "arch-level" }
  D10_lessons: { state: n-a, nano: "delegates to DEFINE/DISCOVER which consult", macro: memory, high: lessons-flow, finding: "n/a-for-kind (delegated phases consult)", proposed: "-", why: "-" }
  D11_subagent: { state: n-a, nano: "delegator", macro: context-budget, high: dedicated-vs-inline, finding: "n/a-for-kind", proposed: "-", why: "-" }
  D12_failure: { state: partial, nano: "inherits", macro: research, high: failure-mode, finding: "no own", proposed: "document inherited", why: "floor" }
  D13_observability: { state: absent, nano: "no invoked_via tag", macro: observability, high: visibility, finding: "same as fix", proposed: "tag cycle-runs.jsonl invoked_via: research", why: "uniform" }
  D14_necessity: { state: implicit, nano: "When NOT to use", macro: research, high: necessity, finding: "implicit", proposed: "necessity: OPTIONAL", why: "X5" }
peer_comparison: { strongest_peer_in_cohort: plan, strongest_composite: fix, this_component_depth: at-composite-bar, uplift_needed: "own status semantics + invoked_via tag + delegation-documentation for checkpoint/recovery" }
operator_decision_required: yes
priority: low
```

```yaml
component: skills/plan-and-build/SKILL.md
kind: skill (composite-delegator)
cohort: 1
dimensions:
  D1_head: { state: present, nano: "Step 1 pre-flight (verify APPROVED design doc)", macro: plan-build-entry, high: explicit-invocation, finding: "good — verifies precondition", proposed: "-", why: "-" }
  D2_tail: { state: partial, nano: "'Inherits from /li:cycle'", macro: plan-build, high: status-protocol, finding: "no own exit", proposed: "own status", why: "same as fix" }
  D3_objects: { state: partial, nano: "Step 3 lists artifacts but input-contract loose", macro: plan-build, high: in/out-contract, finding: "below fix — assumes design-doc exists without contract", proposed: "declare in=APPROVED-design-doc-path, out=plan.md+code+build-log", why: "floor" }
  D4_entrypoints: { state: present, nano: "Hop-in n/a", macro: plan-build, high: entrypoint-coverage, finding: "uniform", proposed: "-", why: "-" }
  D5_checkpoints: { state: absent, nano: "no own 00-state", macro: resume, high: resumability, finding: "delegates", proposed: "document", why: "floor" }
  D6_recovery: { state: absent, nano: "no own recovery", macro: plan-build, high: recovery, finding: "inherits; Step 1 suggests /li:define if missing design", proposed: "document inherited", why: "floor" }
  D7_packinfluence: { state: n-a, nano: arch-level, macro: cohort7, high: pack-driven, finding: "n/a", proposed: "arch-level", why: "arch-level" }
  D8_frontmatter: { state: partial, nano: "no workflow_root/necessity", macro: plan-build, high: frontmatter, finding: "composite gap", proposed: "workflow_root decision + necessity", why: "operator-decision" }
  D9_briefforge: { state: n-a, nano: arch-level, macro: handoff, high: brief-forge, finding: "n/a", proposed: "arch-level", why: "arch-level" }
  D10_lessons: { state: n-a, nano: "delegated phases consult", macro: memory, high: lessons-flow, finding: "n/a-for-kind (but inherits BUILD's lessons-gap — see BUILD D10)", proposed: "-", why: "-" }
  D11_subagent: { state: n-a, nano: "delegator", macro: context-budget, high: dedicated-vs-inline, finding: "n/a-for-kind", proposed: "-", why: "-" }
  D12_failure: { state: partial, nano: "inherits", macro: plan-build, high: failure-mode, finding: "no own", proposed: "document", why: "floor" }
  D13_observability: { state: absent, nano: "no invoked_via tag", macro: observability, high: visibility, finding: "same gap", proposed: "tag invoked_via: plan-and-build", why: "uniform" }
  D14_necessity: { state: implicit, nano: "When NOT to use", macro: plan-build, high: necessity, finding: "implicit", proposed: "necessity: OPTIONAL", why: "X5" }
peer_comparison: { strongest_peer_in_cohort: plan, strongest_composite: fix, this_component_depth: below-composite-bar, uplift_needed: "in/out contract (loose today) + own status + invoked_via tag — raise to fix's depth" }
operator_decision_required: yes
priority: medium
```

```yaml
component: skills/review-and-ship/SKILL.md
kind: skill (composite-delegator)
cohort: 1
dimensions:
  D1_head: { state: present, nano: "Step 1 pre-flight (verify BUILD output exists)", macro: review-ship-entry, high: explicit-invocation, finding: "good precondition check", proposed: "-", why: "-" }
  D2_tail: { state: partial, nano: "'Inherits' (but DOES enumerate BLOCKED-at-REVIEW vs BLOCKED-at-SHIP)", macro: review-ship, high: status-protocol, finding: "slightly better than fix on outcome enumeration but still no own protocol", proposed: "promote the BLOCKED-at-X enumeration into a real status protocol", why: "it's half-there — finish it" }
  D3_objects: { state: partial, nano: "Step 1 verifies inputs; outputs delegated", macro: review-ship, high: in/out-contract, finding: "input checks present, output contract absent", proposed: "declare out=PR+reports+captured-artifacts", why: "floor" }
  D4_entrypoints: { state: present, nano: "Hop-in n/a", macro: review-ship, high: entrypoint-coverage, finding: "uniform", proposed: "-", why: "-" }
  D5_checkpoints: { state: absent, nano: "no own 00-state", macro: resume, high: resumability, finding: "delegates", proposed: "document", why: "floor" }
  D6_recovery: { state: absent, nano: "no own recovery", macro: review-ship, high: recovery, finding: "inherits", proposed: "document inherited", why: "floor" }
  D7_packinfluence: { state: n-a, nano: arch-level, macro: cohort7, high: pack-driven, finding: "n/a", proposed: "arch-level", why: "arch-level" }
  D8_frontmatter: { state: partial, nano: "voice: mixed; no workflow_root/necessity", macro: review-ship, high: frontmatter, finding: "composite gap", proposed: "workflow_root decision + necessity", why: "operator-decision" }
  D9_briefforge: { state: n-a, nano: arch-level, macro: handoff, high: brief-forge, finding: "n/a", proposed: "arch-level", why: "arch-level" }
  D10_lessons: { state: n-a, nano: "delegated phases (but inherits REVIEW+SHIP lessons-gap)", macro: memory, high: lessons-flow, finding: "n/a-for-kind (inherits D10 gap of REVIEW/SHIP)", proposed: "-", why: "-" }
  D11_subagent: { state: n-a, nano: "delegator", macro: context-budget, high: dedicated-vs-inline, finding: "n/a-for-kind", proposed: "-", why: "-" }
  D12_failure: { state: partial, nano: "inherits", macro: review-ship, high: failure-mode, finding: "no own", proposed: "document", why: "floor" }
  D13_observability: { state: absent, nano: "no invoked_via tag", macro: observability, high: visibility, finding: "weakest observability in cohort", proposed: "tag invoked_via: review-and-ship", why: "uniform" }
  D14_necessity: { state: implicit, nano: "When NOT to use", macro: review-ship, high: necessity, finding: "implicit", proposed: "necessity: OPTIONAL", why: "X5" }
peer_comparison: { strongest_peer_in_cohort: plan, strongest_composite: fix, this_component_depth: below-composite-bar, uplift_needed: "finish the half-built status protocol + out-contract + invoked_via tag — raise to fix's depth (it is the weakest overall)" }
operator_decision_required: yes
priority: medium
```

---

## Cohort summary

**Components covered (13):** sense, define, discover, plan, build, review, ship, capture (8 phase) + cycle, fix, research, plan-and-build, review-and-ship (5 composite).

**Strongest peer:** `plan` (full-body) — the only component with a written, caller-relyable output contract, job integration, module-callable §, and explicit nested-job anti-pattern. `cycle` ties on orchestration depth. **Strongest composite:** `fix`.

**Weakest peer:** `review-and-ship` (pure delegator, status "inherits", no own contract/observability/necessity). `plan-and-build` close behind (loose in/out contract).

### Top findings (ranked)

1. **[HIGH] Lessons are write-only across the execution phases.** CAPTURE writes lessons (and promotes them), SENSE surfaces them — but **PLAN, BUILD, REVIEW, SHIP never read them**. The marquee example: a captured lesson like "don't mock Azure SDK" never reaches the BUILD implementer subagent. SENSE already solved this for itself (Step 0a lessons-surface, closing L-001/L-002). Uplift: feed relevant lessons into BUILD's implementer brief (D10), REVIEW's Step 1, SHIP's Step 2, and give PLAN a lessons-consult path for the hotfix-into-PLAN case. This is the X3 operator-relation thread being only half-active.

2. **[HIGH] `cycle` promises per-phase `tokens_est_typical` that no phase declares.** cycle Step 4 progress-output and Step 0 dry-run both read phase frontmatter `tokens_est_typical:` — but zero of the 8 phases declare it. Broken reference today. Uplift: add `tokens_est_typical` to all 8 phase frontmatters.

3. **[MEDIUM] Observability is non-uniform: SENSE, DISCOVER, SHIP, and all 4 composites lack an analytics jsonl** that define/plan/build/review/capture/cycle have. Composites additionally can't be distinguished from raw `/li:cycle` in logs (no `invoked_via` tag). Uplift: add the missing `*-metrics.jsonl` writes + tag cycle-runs.jsonl with `invoked_via`.

### Designed-not-built note (one architecture-level entry, per directive)

**D7-runtime (pack resolver), D9 (Brief Forge), envelope/wiki are unbuilt.** Each component above is marked `n/a — tracked at arch level` rather than spammed as "absent". Important nuance surfaced: three working *precedents* already exist for these unbuilt features and should anchor their design — (a) **WorkProfile-branching in REVIEW/SHIP Stage-3 gates** is the working precedent for pack-influence; (b) **cycle's mode-presets** are proto-packs (they branch phases/compliance/voice, just hardcoded not resolved); (c) **BUILD's implementer-brief (Step 3a: full task text + scene-setting)** is the de-facto Brief-Forge payload. When these features land (cohorts 7-8), they should generalize these precedents, not invent fresh patterns.

### Cross-cohort field gaps (feed X5)

Every component lacks a declared `necessity` + `gap_if_skipped` field (all currently implicit in prose). No `workflow_root` on the 4 composite entry-points (operator-decision: should `/li:fix` etc. spawn jobs?). No `navigation` on the two `workflow_root` skills (plan, cycle).

### Operator-decision-required count: **6**

- `plan` (high) — necessity/navigation frontmatter + lessons-consult path for hotfix-into-PLAN
- `build` (high) — lessons-into-implementer-brief (load-bearing memory fix)
- `cycle` (high) — fix tokens_est_typical broken reference (touches all 8 phases)
- `fix`, `research`, `plan-and-build`, `review-and-ship` — **shared decision:** should composite entry-points carry `workflow_root` (spawn jobs) + own status/observability? (counted as the 4th operator item — one decision spanning all four composites)

(7 components carry `operator_decision_required: yes` individually; they collapse to **6 distinct operator decisions** because the four composites share one workflow_root/observability decision... counted conservatively as 6 decision-threads, 7 yes-flags.)
