# Master prompt — Lintel system-wide uniformity audit

**Purpose:** Run a deep, structured audit of every Lintel component (skills, agents, workflows, phases, hooks, packs) against a single uniform standard. Find where depth is uneven, where the framework breaks its own promises, and where one concept lives in one section but not in another. Produce a findings register and a prioritized recommendation set the operator can vote on, compare, and integrate.

**Critical operator directive — read first:**
- **Never remove functionality** as a recommendation. The motto is *kraftfullt från start och ständigt evolverande*. If a component is thin, recommend *raising it to the same depth as the strongest peer*, not cutting it.
- **Every component must reach the same depth on the same dimensions.** Front-end design skills, planning, discovery, testing, ship — all must answer the same uniformity questions. Different depths in different places is a finding.
- **Findings must be traceable at three levels:** *nano* (specific file:line or frontmatter field), *macro* (workflow/phase flow it belongs to), *high* (which architectural promise it upholds or breaks).
- **The work is in cohorts, not in one pass.** Token budget is finite; complete one cohort, checkpoint, then the next.
- **Justify every proposed change.** Every recommendation must answer: *what are we trying to achieve, is there a more elegant way, does someone else do this better, why this specifically.*

---

## The uniformity dimensions (this is the standard)

Every component — skill, agent, workflow, phase, hook, pack — must be evaluated on **all** of these dimensions. A finding is any place a dimension is missing, inconsistent with peers, or implemented at a different depth than another component of the same kohort.

**D1 — Head / entry.** What signals the start of this component running? Is it explicit (declared invocation, hook fire) or implicit (assumed convention)? What inputs does it require, and are they validated at head?

**D2 — Tail / exit.** What signals the component is done? Is it explicit (status protocol DONE/BLOCKED/etc, declared exit) or implicit? What outputs does it produce, and are they validated at tail?

**D3 — Expected objects (in / out contract).** What shape of input does it expect (file paths, envelope, declared types, free text)? What shape of output does it produce? Are these contracts written down, or inferred?

**D4 — Entry-points.** Which entry-points can reach this component? Is each entry-point covered? Are there entry-points where this component should fire but doesn't? Are there entry-points where this component fires but shouldn't?

**D5 — Checkpoints.** Does the component write checkpoints during execution (00-state, planner-checkpoint, envelope log)? At what granularity? Is the checkpoint readable by resume / replay mechanisms?

**D6 — Recovery points.** If this component fails or is interrupted, where can recovery resume from? Is there a stub-doc-and-continue path, a retry path, an operator-choice point?

**D7 — Pack / WorkProfile influence.** Does the active pack actually change this component's behavior? Should it? If yes, where is that influence declared (frontmatter, runtime resolve, hardcoded fallback)? Does WorkProfile on/off measurably differ?

**D8 — Frontmatter completeness.** Does this component declare cli_support, voice, layer, color, necessity, navigation (if workflow_root), brief_forge_handoffs, expected_inputs/outputs? Which are missing?

**D9 — Brief Forge integration.** At hand-off into or out of this component, does Brief Forge fire? If yes, with which evaluators? If not, why not? (Brief Forge is a designed feature — flag where it *should* fire even if not implemented yet.)

**D10 — Knowledge / lessons integration.** Does this component consult lessons.md or the knowhow tag-funnel at relevant moments? Should it? Is consultation declared in frontmatter or implicit?

**D11 — Subagent / context delegation.** Does this component spawn subagents to keep main context free? Should it (by the dedicated-vs-inline rule)? If it spawns, is the spawned subagent given a curated brief (Architect-style) or raw context?

**D12 — Failure mode.** What happens when this component encounters something unexpected? Crash, halt pipeline, stub-and-continue, retry, ask operator? Is the failure mode consistent with peers?

**D13 — Observability.** Does this component write to the usage log / envelope log / hooks.jsonl? Can the operator see it ran, what it did, what it cost? Is observability uniform with peers?

**D14 — Necessity declaration.** Is this component REQUIRED / STRONGLY RECOMMENDED / OPTIONAL within its workflow? Is the "gap if skipped" written down?

---

## The audit protocol (kohort by kohort)

You will work in **eight cohorts**, in this order. After each cohort, checkpoint findings to `.claude/engineering/audits/lintel-uniformity-findings-<cohort>.md`, then move to the next.

**Cohort 1 — Phase-core skills.** The 8 phase skills (sense, define, discover, plan, build, review, ship, capture) plus their composites (cycle, fix, research, plan-and-build, review-and-ship).

**Cohort 2 — Planner sub-chain.** office-hours, plan-ceo-review, plan-eng-review, plan-design-review, plan-devex-review, autoplan.

**Cohort 3 — Brief Forge / hand-off / envelope candidates.** Every skill currently doing hand-off-like work informally (pair-agent, codex, all context-warm-* skills, all context-save/restore/snapshot/dump/cool skills). This is where you find the most fragmentation.

**Cohort 4 — Domain-specialist agents in cycle phases.** The 73 agents. Map each agent to which phase(s) call it. Find agents that should be called but aren't, and the inverse.

**Cohort 5 — Hooks (15) + override mechanics.** Each hook against D1-D14. Pay special attention to D7 (do packs/WorkProfile change which hooks activate?) and D13 (override audit log existence vs consumption).

**Cohort 6 — Engineering domain skills.** Technical Architecture, Data Architecture, Security & Compliance, DevOps & Hosting, Testing & QA. The operator has explicitly flagged depth inconsistency here. Map every skill and agent in each domain against the uniformity dimensions. Data Architecture is likely the thinnest — note where its skills should reach the depth of Security & Compliance (the strongest).

**Cohort 7 — Pack lifecycle skills + role/profile mechanics.** All /li-pack-* skills (planned and existing), all role-* skills (8 today for 3 roles), WorkProfile-related logic. Audit whether pack-resolver pattern is consistent across consumers.

**Cohort 8 — Cross-cutting infrastructure.** The jobs system, knowledge base (tag-funnel), wiki generator, payload envelope, provenance. Audit whether each cross-cutting layer is consumed consistently by all phase-core skills.

---

## For each component within each cohort

Produce a finding record in this exact shape (so the operator can grep, vote, prioritize):

```yaml
component: <path/to/component>
kind: skill | agent | hook | workflow | pack | phase
cohort: <cohort number>
dimensions:
  D1_head:
    state: present | absent | partial | implicit
    nano: <file:line or "frontmatter:field" or "not declared">
    macro: <which workflow/phase this affects>
    high: <which architectural promise is at stake>
    finding: <one-sentence concrete problem, or "uniform with cohort">
    proposed: <what to add/normalize, never remove>
    why: <what we're trying to achieve, is there a more elegant way, does X do it better>
  D2_tail: { ...same shape... }
  D3_objects: { ... }
  ... through D14 ...
peer_comparison:
  strongest_peer_in_cohort: <which component sets the bar>
  this_component_depth: <relative: at-bar | below-bar | above-bar>
  uplift_needed: <what would bring this to bar, never down to bar>
operator_decision_required: yes | no
priority: high | medium | low
```

---

## Required questioning for every recommendation

Before writing a `proposed` field, you must internally answer all of:

1. **What are we trying to achieve here?** State the architectural goal in one sentence.
2. **Is there a more elegant way?** Consider at least one alternative to the obvious fix.
3. **Does someone else do this better?** Reference gstack, superpowers, speckit, ECC, Architect-bilden — does any of them have a pattern we should steal?
4. **Why this specifically?** Justify the chosen approach over the alternative.

If you cannot answer all four, the recommendation is not ready. Mark it `needs-more-thought` and move on.

---

## Cross-component checks (run after all cohorts complete)

After cohorts 1-8 are done, run these cross-cutting passes:

**X1 — Concept consistency.** For each concept (head, tail, checkpoint, recovery, pack-influence, etc.), produce a single table: rows = components, columns = whether the concept is present and at what depth. Cells should be sortable so the operator can see fragmentation at a glance.

**X2 — Promise verification.** For each architectural promise the framework makes (cross-session memory via lessons, pack-driven behavior, jobs visibility, Brief Forge at hand-offs, knowledge tag-funnel, 500k handoff cap, mandatory pause at PLAN approval), produce a verification: is the promise upheld by every component that should uphold it?

**X3 — Operator-relation vs repo-relation evolution.** The motto says the system learns and grows in both the operator-relation (lessons accumulate, voice calibrates, packs evolve) and the repo-relation (ADRs accumulate, knowhow grows, packaged lessons ship). Verify both threads are *active* — that data flows in both directions and is consulted, not just written.

**X4 — Entry-point coverage matrix.** Build a matrix: rows = every documented entry-point (/li-cycle, /li-fix, /li-research, /li-resume, /li-<phase>, /li-pack-new, etc.), columns = every cross-cutting layer (jobs, brief forge, knowledge, hooks, packs, voice, provenance). Cell = "fires", "skipped", "should-fire-doesn't", "fires-shouldn't". Anywhere "should-fire-doesn't" appears is a finding.

**X5 — Necessity + gap-if-skipped coverage.** Architect declares per-section. We don't yet. List every component where a `necessity` and `gap_if_skipped` field would be load-bearing if added.

---

## Output format

**Per-cohort:** `.claude/engineering/audits/lintel-uniformity-findings-<cohort-name>.md` with one finding record per component plus a cohort summary.

**Cross-cutting:** `.claude/engineering/audits/lintel-uniformity-cross-<X-number>.md` for X1 through X5.

**Master summary:** `.claude/engineering/audits/lintel-uniformity-MASTER.md` — top 20 highest-leverage findings, ranked. Each entry: which dimension, which components affected, proposed uplift, why this specifically, estimated effort, dependencies on other findings.

**Voting register:** `.claude/engineering/audits/lintel-uniformity-VOTE.md` — every finding marked `operator_decision_required: yes`, listed for operator to vote on. Format: finding ID, one-line summary, three proposed approaches (chosen + two alternatives), recommendation. Operator votes by marking choice.

---

## Token budget and checkpoint protocol

- After each cohort, write its findings file, commit, and stop. Do not chain into the next cohort without explicit operator continue.
- If a cohort risks exceeding 30k tokens of analysis, break it further and produce a partial findings file with `status: incomplete` and notes on what remains.
- Use subagents aggressively — spawn fresh agents per cohort with curated briefs, not one main agent carrying all 8 cohorts. (This is the dedicated-vs-inline rule applied to your own audit.)
- Read the actual files. Do not summarize from frontmatter alone — open bodies, check claims against implementation.

---

## What this audit produces

A complete picture of where Lintel keeps its promises and where it doesn't. A prioritized list of uplifts that raise weak components to the depth of strong peers. A vote register for the operator to choose direction. The findings become the next backlog cycle.

**This audit removes nothing. It surfaces what needs to grow.**

That is the motto: *kraftfullt från start, ständigt evolverande, lär sig och växer ihop med operatören och repot.* This audit makes the motto operational.
