# Independent synthesis review

2026-09-20. Main baseline: `28061e434be455ca02f135b73244eaf4f73f3a69`.
Reviewed audit: `.claude/engineering/audits/2026-09-20-universal-quality/`.
Reviewer: a separately delegated, read-only synthesis reviewer. The coordinator made all corrections; the reviewer changed only this report.

## Decision

**GO to deliver the audit and proposed action list.** No unresolved finding remains in this bounded counterreview. This is not approval of implementation, a source merge, feature removal, production action, or a claim that the proposed Universal integration already works.

Initial findings: **P0 0, P1 0, P2 2, P3 2**. After coordinator corrections and source reread: **P0 0, P1 0, P2 0, P3 0 open**. These counts concern the audit delivery, not the underlying product defects.

The final synthesis preserves useful capabilities, the accepted ADR-0026 hybrid model, and independent substantive review. The host model distinguishes vendor capability, shipped integration and observed execution. Proposed architectural changes remain proposals with explicit decision requirements. The swarm work is treated as a desired capability with practical alternatives when native parallel execution is unavailable.

## Findings and verified resolution

### SYN-01 — P2: Promote the distinct runtime trust and private-sync risks into actionable results

The initial `action-plan.md:57–67` grouped runtime findings under small executable errors without identifying two P1 boundaries: target-project resolver execution and private sync using an obsolete destination. This obscured materially different acceptance requirements in an otherwise prioritized action list.

Primary evidence: `hooks/shared/ta-contract-collision-warn/run.sh:20–23` sources target-repository code; `bin/li-vault-init:43–48` prefers the same source. `bin/li-roles-sync:66–86` updates the configured URL without changing an existing origin, `:101` pushes that origin, and `:122` only removes the config on forget. `bin/li-lessons-sync:69–104` and `:124` repeat the destination problem.

**Resolved:** final `action-plan.md:68–90` gives RU-02 and RU-03 their own P1 cards A25/A26, exact preservation boundaries and discriminating acceptance cases. `report.md:65–70` now surfaces both risks. The optional-hook qualification remains explicit, and no default exploit is claimed.

### SYN-02 — P3: Distinguish static runtime evidence from executed reproductions

The initial `verification.md:62–63` called the runtime lane's evidence safe reproductions. In contrast, `reviews/runtime.json:711–714` says the lane was static and its proposed fixtures had not run. Static control-flow evidence can establish the reported defects, but should not be described as execution evidence.

**Resolved:** reread `verification.md:62–63`; it now states static source/control-flow evidence and proposed future reproduction fixtures. The separately executed coordinator probes and swarm in-memory checks remain distinguished.

### SYN-03 — P3: Describe the design scoring defect precisely

The initial `report.md:54–56` described design averaging. The cited `DesignSystemAuditor` actually uses per-dimension thresholds and explicitly rejects averaging away an accessibility failure (`agents/frontend/DesignSystemAuditor.md:156–164,181`). Its real defect is additive scoring within accessibility: normal-text contrast contributes only 20 points, while the stated penalty starts below 3:1 (`:109,119`), allowing the cited 100 minus 20 equals 80/GREEN counterexample.

**Resolved:** `report.md:55` now says score thresholds. The supported false-clearance finding and A02 acceptance case are preserved rather than withdrawn.

### SYN-04 — P2: Make the new preservation lessons visible to the existing reader

The new continuity entries initially used `### L-031` and `### L-032` at `.claude/memory/lessons.md:676,682`. The actual reader only recognizes `^## L-[0-9]+` (`lib/memory.sh:46,99`), so the user's preservation corrections would not be separate retrievable lessons.

**Resolved:** a final read confirms both entries use `## L-NNN`. This was a delivery-artifact correction; the reviewer did not change the shared lesson file. Literal patch-prefix characters observed in the report were also removed and checked.

## Representative primary-source verification

| Claim sampled | Original evidence checked | Result |
|---|---|---|
| Copilot-first entry framing | `README.md:3–13`; `docs/getting-started.md:3–9`; ADR-0024:16–22 | Supported. Additive adapter authority does not require a vendor-first product identity. |
| Mandatory compliance failure can be only a warning | `skills/compliance-gate/SKILL.md:73–104`; `skills/ship/SKILL.md:64–80` | Supported. The per-control policy/evidence recommendation addresses the actual ambiguity. |
| Review may omit requested working-tree changes | `skills/code-review/SKILL.md:38–49`; `skills/review/SKILL.md:65–68`; `skills/ship/SKILL.md:44–49` | Supported. Commit ranges and a PASS document do not bind all selected uncommitted content. |
| Old clearance can survive a later rejection | `bin/li-review-read:162–193` | Supported by control-flow trace: negative statuses are filtered before final selection; an empty commit also passes the implemented condition. |
| Host-specific question hard stop | `skills/define/SKILL.md:333–337`; `lib/cli-tiers.yaml:8–75` | Supported. Adapter/capability handling is preferable to declaring an otherwise usable host incapable. |
| Unsafe context and snapshot recipes | `skills/context-warm/SKILL.md:38–46`; `skills/safe-install/SKILL.md:98–115` | Supported by shell semantics. No dangerous input, deletion or restore was executed. |
| Pack/session behavior versus accepted contract | `lib/pack-resolver.sh:39–45,409–469`; `docs/concepts/pack-resolver.md:64–81,104–106` | Supported. The audit correctly identifies caller obligations and labels stricter fallback behavior a deliberate contract change. |
| Cycle marker/order mismatch | `skills/cycle/SKILL.md:178–218,234–266`; `lib/state.sh:83–99` | Supported as an instruction/state-contract inconsistency. No full model-run failure is implied. |
| Design score/schema defects | `agents/frontend/DesignSystemAuditor.md:106–120,156–189`; `skills/frontend-design-review/SKILL.md:147–179` | Supported, subject to the corrected score-threshold wording above. |
| Preservation of hybrid execution | ADR-0026:17–30; final `report.md:126–130`; `action-plan.md:3–13` | Short leaves, coherent packages, aggregate review depth and independent substantive review remain intact. |

The available official-source spot checks support the selected client claims: [Cursor subagents](https://prod.cursor.com/docs/subagents), [GitHub Copilot app](https://docs.github.com/en/copilot/concepts/agents/github-copilot-app), and [Factory custom droids](https://docs.factory.ai/harness/subagents). These checks establish documented vendor capabilities, not successful Lintel installation or execution.

## Preservation and swarm assessment

Reviewed the full final `swarm-preservation.md` and the expanded A22 at `action-plan.md:326–343`. The document inventories all 76 branch-delta paths without pretending every line was deeply reviewed. Its requirements explicitly preserve implementation, knowledge, tests, briefs, reports, history and useful entry points; generated surfaces may be regenerated while retaining discoverability.

The capability matrix at `swarm-preservation.md:28–35` supplies native isolated execution, sequential delegated execution and coordinator-assisted external/manual handoff. It keeps substantive independent review open when no real reviewer is available. A22 requires a traceable destination for valuable branch changes and an explicit decision for unavoidable loss. This satisfies the requested preservation intent at audit/action-list scope; it does not defer the whole feature merely because one host lacks concurrency. Actual integration and per-change preservation evidence remain implementation work.

The general inventory recommendations also retain source-grounded specialist methods and useful aliases. Staged PDF/XLSX/Visio work is not counted as working delivery; perf-mode and the historical migration entry require useful replacement and retained access before changing ownership. Optional packaging is conditioned on retained value, not a file-count reduction target.

## Review scope and limits

- Read the synthesis, action list, verification, client sources and both item inventories; inspected detailed workflow/capability/agent/runtime evidence, upstream comparison and the separate swarm report. Read relevant authority, accepted ADRs and the primary-source slices listed above. This was a bounded counterreview, not a second complete semantic read of all 195 instructions.
- Independently checked the critical mechanisms through static source/control-flow analysis. Did not rerun coordinator probes, the swarm fixture execution, installers, sync, dangerous recipes, the full suite, or paid model evaluations. Existing test source is not claimed as freshly passing evidence.
- Did not reconstruct historic imports or independently verify every external legal/library claim. The audit's careful limits on upstream comparison, temporal client information and staged capabilities are appropriate.
- The final tracked diff check showed only audit continuity files; no product change was made by this reviewer. Final artifact-link validation, plan/working-state closeout and any authorized audit-branch delivery remain coordinator responsibilities.

The corrected audit is suitable for operator review and prioritization. Its product findings remain open until implemented and verified through a separately authorized plan.
