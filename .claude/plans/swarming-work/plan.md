# Plan: first-class swarming work (size: XL · schema: tree)

**Status:** APPROVED — the operator explicitly requested delivery from vision through merge.
**Design:** [design.md](design.md)
**Discover:** [discover.md](discover.md)
**Spec:** [spec.md](spec.md)
**Prompt:** [prompt.md](prompt.md)
**Work map:** [work.json](work.json)

## Plan signals

- Build cards: 6; leaves: 98
- Phases: DEFINE, DISCOVER, PLAN, BUILD, REVIEW, SHIP, CAPTURE
- Size: XL
- Token estimate: 90k–180k, UNCALIBRATED planning range
- Execution: swarm; project cap 2 concurrent implementers; one coordinator
- Leaf budget: each numbered leaf targets 2–5 minutes of active work. BUILD must split and re-plan
  any leaf that proves larger before continuing it.

## Dependency graph

```text
BC1 → BC2 → BC3 → BC4 ─┐
                 └→ BC5 ├→ BC6
```

BC4 and BC5 may execute in parallel because their write scopes are disjoint. All other cards are
serialized by dependency or reducer ownership.

## Build cards

### BC1 — Lock architecture and execution contract (coordinator; R1–R3)

- [x] 1.1 Record the approved vision and problem statement in ADR-0026.
- [x] 1.2 Record the three alternatives and selected design in ADR-0026.
- [x] 1.3 Record invariants, non-goals, migration, and rollback in ADR-0026.
- [x] 1.4 Create the M1 header, affected paths, and structural delta.
- [x] 1.5 Complete M1 compatibility, verification plan, and rollback sections.
- [x] 1.6 Persist the cold-executor trio, work map, charter, and lane briefs.
- [x] 1.7 Parse both JSON files and run the existing work-map validator.
- [x] 1.8 Obtain an independent two-stage plan review with zero unresolved P1/P2 findings.
- [x] 1.9 Commit the reviewed planning baseline. BC2 is the bootstrap lane; the coordinator manually
      verifies its scope until BC2 builds the validator.

Acceptance: all planning artifacts are linked, authoritative roles are explicit, and the commit can
seed isolated implementation worktrees.

### BC2 — Build the swarm contract and deterministic gates (depends BC1; R2–R6)

- [x] 2.1 Define schema identity, required root keys, and version bounds.
- [x] 2.2 Define safe repository-relative path fields in the schema.
- [x] 2.3 Define lane, wave, isolation, report, and review fields in the schema.
- [x] 2.4 Add the stdlib coordination-file loader and structured diagnostics.
- [x] 2.5 Add repository-relative path validation without artifact execution.
- [x] 2.6 Add duplicate task/lane detection.
- [x] 2.7 Add same-wave write-scope overlap detection.
- [x] 2.8 Add parallel-writer isolation validation and sequenced fallback diagnostics.
- [x] 2.9 Expose the shared parser entry point that BC3 will call from the work-map validator.
- [x] 2.10 Add the CLI `validate` operation.
- [x] 2.11 Add the CLI `wave` ready-frontier operation.
- [x] 2.12 Add `check-scope` for one attributable patch/change set.
- [x] 2.13 Make `check-scope` allow only lane `write_scope + own report`.
- [x] 2.14 Add the CLI `status` operation.
- [x] 2.15 Add the CLI `verify` close-evidence operation.
- [x] 2.16 Add the charter template.
- [x] 2.17 Add the coordination JSON template.
- [x] 2.18 Add the worker brief template.
- [x] 2.19 Add the worker report template.
- [x] 2.20 Add the independent review template.
- [x] 2.21 Test invalid paths and duplicate lanes.
- [x] 2.22 Test overlap and missing isolation.
- [x] 2.23 Test per-patch scope plus own-report allowance and review-path rejection.
- [x] 2.24 Test incomplete evidence and old-map compatibility.

Acceptance: focused unit tests prove the validator fails closed and the current initiative's swarm
contract validates.

### BC3 — Integrate swarming into the Lintel workflow (depends BC2; R1, R3, R5–R9)

- [x] 3.1 Add `/li:swarm` frontmatter, purpose, and explicit opt-in rules.
- [x] 3.2 Document `init` artifact creation and authority boundaries.
- [x] 3.3 Document `run` readiness, Brief Forge dispatch, and coordinator ownership.
- [x] 3.4 Document `status` and `resume` output contracts.
- [x] 3.5 Document `verify` scope/evidence gates and serial integration.
- [x] 3.6 Add PLAN's independent-domain detection rule.
- [x] 3.7 Add PLAN's operator opt-in and additive work-map emission rule.
- [x] 3.8 Add BUILD's mapped-swarm entry condition.
- [x] 3.9 Add BUILD's evidence/topology candidate wave plus authoritative prerequisite gate.
- [x] 3.10 Add BUILD's worker startup, scope, acceptance, and report requirements.
- [x] 3.11 Add BUILD's per-lane spec and quality review requirements.
- [x] 3.12 Add REVIEW's integrated-tree close gate.
- [x] 3.13 Add RESUME's frontier and lost-attempt recovery rules.
- [x] 3.14 Add CAPTURE's durable evidence and M4 rules.
- [x] 3.15 Link the profile from CYCLE without adding a phase.
- [x] 3.16 Route full-engineering-pass DA/SC work through the host-aware profile.
- [x] 3.17 Document additive fields in the canonical work-map reference.
- [x] 3.18 Wire swarm validation into `li-work-artifacts.py`.
- [x] 3.19 Add shape assertions for workflow links and unique task authority.
- [x] 3.20 Add the integration fixture for safe wave and close evidence.
- [x] 3.21 Add a discovered `tests/integration/swarm-workflow.sh` wrapper.
- [x] 3.22 Run focused swarm tests and legacy BUILD/work-map fixtures.

Acceptance: one fixture traverses plan map → safe wave → reports/reviews → integrated close gate;
legacy BUILD fixtures remain green.

### BC4 — Propagate the contract through scaffolding and adapters (depends BC3; R5, R6, R8, R10)

- [x] 4.1 Add coordinator/single-writer rules to the canonical session protocol.
- [x] 4.2 Add attributable isolation and sequenced fallback to the protocol.
- [x] 4.3 Add swarm recovery and honest review-degradation rules to the protocol.
- [x] 4.4 Correct the repository subagent guide's discovery and ownership wording.
- [x] 4.5 Correct the scaffolded subagent guide to match the canonical contract.
- [x] 4.6 Teach the scaffold factory to install swarm templates.
- [x] 4.7 Add `swarm` to the Copilot workflow selection list.
- [x] 4.8 Add the canonical swarm skill/templates to Copilot resources.
- [x] 4.9 Extend the Copilot integration test with swarm workflow/resource assertions.
- [x] 4.10 Run the focused scaffold and Copilot generator tests.
- [x] 4.11 Hand canonical-source changes to the coordinator for protocol synchronization.
- [x] 4.12 Let the coordinator regenerate and check Copilot managed outputs.
- [x] 4.13 Let the coordinator verify a temporary consumer checkout after fan-in.

Acceptance: protocol parity, scaffold checks, Copilot init/check, and generated drift tests pass.

### BC5 — Make swarming understandable from every public angle (depends BC3; R1–R10)

- [x] 5.1 Add the concept guide's decision and non-goal sections.
- [x] 5.2 Add the concept guide's artifact tree and authority table.
- [x] 5.3 Add the concept guide's lifecycle and recovery sections.
- [x] 5.4 Add the concept guide's cross-CLI degradation and examples.
- [x] 5.5 Link the guide from the documentation index.
- [x] 5.6 Add the execution profile to architecture and cycle documentation.
- [x] 5.7 Add native/sequenced/none behavior to multi-CLI documentation.
- [x] 5.8 Add operator decision/recovery answers to the FAQ.
- [x] 5.9 Add swarm terminology to the glossary.
- [x] 5.10 Add concise capability entry points to the root README.
- [x] 5.11 Correct Brief Forge automatic-hook claims to match verified runtime reality.
- [x] 5.12 Hand catalog/wiki reducer work to the coordinator after documentation fan-in.

Acceptance: a new operator can decide when to swarm, inspect ownership, recover a run, and
understand host limitations without reading implementation code.

### BC6 — Review, release, merge, and capture (depends BC4 and BC5; R4, R7, R10)

- [ ] 6.1 Dispatch the independent specification review on the integrated tree.
- [ ] 6.2 Resolve each accepted specification-review P1/P2 finding.
- [ ] 6.3 Dispatch independent quality/security review on the corrected tree.
- [ ] 6.4 Resolve each accepted quality/security P1/P2 finding.
- [ ] 6.5 Run M2 compatibility audit by itself.
- [ ] 6.6 Run M3 shape and focused generated checks.
- [ ] 6.7 Run the full suite once on the stable reconciled commit.
- [ ] 6.8 Fetch `origin/main` and choose an unused patch version.
- [ ] 6.9 Apply the same version to every distribution manifest.
- [ ] 6.10 Update the changelog and rerun manifest identity checks.
- [ ] 6.11 Record M4 outcome and exact local evidence.
- [ ] 6.12 Update working state, plan review, and any durable lesson.
- [ ] 6.13 Commit the release/capture reducer changes atomically.
- [ ] 6.14 Push the feature branch.
- [ ] 6.15 Open the pull request against `main`.
- [ ] 6.16 Inspect required CI and address in-scope failures.
- [ ] 6.17 Merge the reviewed pull request under the current authorization.
- [ ] 6.18 Verify `origin/main` contains the merged feature.

Acceptance: the merged `main` ref contains the feature, remote required checks are green, and the
completion record states unverified host behavior honestly.

## Review

Planning gate passed after three independent review rounds. The first two rounds exposed four
contract issues and four execution-quality issues; all were corrected. The final two-stage review
reported P0/P1/P2/P3 = 0/0/0/0. Evidence: [swarm/reviews/plan.md](swarm/reviews/plan.md).

Implementation review remains pending. Reviewers must verify the integrated feature branch, not
isolated lane outputs, and must report exact checks and limitations.
