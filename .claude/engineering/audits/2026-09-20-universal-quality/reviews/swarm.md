# Unmerged swarm delta review

Preserve and integrate this feature after repairing its contract boundaries and reconciling it with main's accepted hybrid execution model. The branch contains useful engineering and operational knowledge: it should be enriched, not discarded to reduce the catalogue. Every recommendation below preserves the swarm capability, relevant use cases and discoverable entry points.

## Baseline and decision

Reviewed branch **codex/swarming-work at 275a35447c4ad271e05816ade43ac48f1acec24f**, against merge base **e9911fcd448dc632bf2752c69304d2be80b7aa65**. Main audit baseline is **28061e434be455ca02f135b73244eaf4f73f3a69**. Read-only Git checks confirmed **10 commits behind / 7 ahead**, with **76 changed files, +5,391 / -236** relative to the merge base.

This is a separate delta review. Findings do not describe missing later enterprise fixes as current-main defects. Branch citations below are paths and one-based lines **at 275a354**, unless explicitly marked main.

**Severity: P0 0 · P1 1 · P2 5 · P3 0.** Recommendation: retain the architecture and implementation, repair the six findings, then integrate through the current main package workflow and rerun independent review. Existing branch reports are useful historical evidence; they are not proof that the reconciled implementation has passed.

## Foundations to preserve

- **One authoritative work map and task source.** Optional swarm pointers preserve old maps; topology does not duplicate task descriptions, dependencies or acceptance. The distinction between candidate waves and authoritative prerequisites is explicitly documented.
- **One coordinator and attributable lanes.** Workers, reviewers, shared ledgers and integration have distinct ownership. Separate worktrees/patches/scoped sandboxes are required for concurrent writers, and a shared-tree union diff is correctly rejected as attribution.
- **A real read-only implementation.** The standard-library helper does not execute artifact text, spawn agents, merge or mutate shared state. It rejects unsafe paths, duplicate JSON keys, malformed evidence and same-wave scope overlaps; normalized path identities cover in-repository aliases.
- **Honest recovery and host degradation.** Lost runtime state is not completion; incomplete work is preserved. Native, sequenced and no-subagent hosts share durable artifacts, with no fabricated independence or hook translation.
- **Independent lane and integrated review.** Lane reports do not replace final review of the reconciled branch. Keep this distinction while adopting main's package review unit.
- **Meaningful focused tests.** The unit suite exercises actual parser/scope/state behavior, beyond keyword checks. Adapter tests also verify missing dependencies fail before target writes and source/runtime roots remain distinct.
- **Improved activation honesty.** Brief Forge documentation correctly moves from imagined universal callbacks to explicit invocation and tests nested policy resolution and unknown evaluators.

## Findings

### SW-01 — P1: Reject report/review paths that alias coordinator-owned authority

**Problem.** Lane artifact paths are checked for duplicates against other lane artifacts, but not against the work map, mapped specification/plan/tasks/prompt, charter or coordination document. Topology protects those paths only against `write_scope`. Scope checking then gives an exact `own_report` path an exception. A lane can consequently declare the authoritative plan as its report, validate successfully, and receive permission to overwrite that plan. A reviewer artifact can likewise point at `work.json`.

**Evidence.** `lib/swarm_contract.py:327` builds the artifact ownership set; `lib/swarm_contract.py:450` constructs protected paths only for scope overlap; `lib/swarm_contract.py:532` checks universal coordinator paths, followed by the own-report exception at `lib/swarm_contract.py:536`. The declared ownership promise is in `.claude/plans/swarming-work/spec.md:31`.

**Verification.** Executed the actual branch library against an entirely in-memory fixture. Ordinary fixture validation passed. Setting the lane report to the mapped plan still returned `ok=true`; `check_lane_scope(..., changed_paths=[mapped_plan])` also returned `ok=true`. Setting the review path to the work map validated successfully. No real file was modified.

**Impact.** The fail-before-dispatch ownership gate can authorize mutation of the source that governs the lane. This is a concrete authority violation, not merely incomplete evidence.

**Repair.** Validate all artifact ownership classes together using the existing normalized identity logic. Report/review paths must not equal or overlap coordinator artifacts, other owned artifacts or reserved roots; reject directory/ancestor collisions as applicable. Then make worker/reviewer scope checks derive from that validated ownership map. Add exact-path and symlink-alias negative cases. **Confidence: high.**

### SW-02 — P2: Reconcile swarm lanes with accepted hybrid packages and preserve leaf coverage

**Problem.** Both main and this branch claim ADR-0026 for different decisions. Branch swarm lanes bind one `task_id` to a card and require independent two-stage review for every lane. Main already accepted short leaves grouped into bounded execution/review packages, with aggregate complexity determining review depth and mechanical packages eligible for coordinator review. Main's package table and numeric leaf IDs are not understood by the branch parser.

**Evidence.** Branch `.claude/decisions/0026-first-class-swarming.md:1`; `skills/swarm/SKILL.md:94` and `skills/swarm/SKILL.md:123`; `lib/swarm_contract.py:33` requires an alphabetic first character, and `lib/swarm_contract.py:364` recognizes only headings and checkbox-list task definitions. Main `.claude/decisions/0026-hybrid-work-packages.md:17` establishes the package model; main `scaffolding/01-foundation/templates/plan/plan.template.md:60` uses a package table and line 100 permits `1.1.a` leaves.

**Impact.** A textually clean merge can restore per-leaf setup/review overhead, fail on valid current plans, lose the required package-to-leaf acceptance mapping, or leave two incompatible ADR-0026 references throughout code and docs. This is an integration incompatibility, not a claim that the branch should have implemented later main work when it was written.

**Repair.** Preserve main ADR-0026 and assign a new unused ADR identifier to the reconciled swarm decision. Make a lane reference a bounded package from the authoritative plan, with unchanged member leaf IDs and acceptance evidence. Legacy ungrouped tasks become singleton packages. Preserve disjoint package ownership, derive package readiness from existing leaf dependencies, and keep final integrated review. Decide explicitly how main's mechanical inline-review allowance applies to serial/mechanical lanes; substantive packages must retain independent review. Include valid main flat/phased/tree and Spec Kit plans in compatibility fixtures. **Confidence: high.**

### SW-03 — P2: Bind completion and review evidence to the work actually reviewed

**Problem.** Reports identify initiative/task/worker, path names and PASS checks; reviews identify another name and PASS stages. Neither required contract identifies the source acceptance revision, attempt, attributable base/head or patch digest, reviewed report version, or actual result snapshot. The helper can retain `complete` after the mapped task's acceptance changes. A path string under scope is called a product change even if it was never created.

**Evidence.** `scaffolding/01-foundation/templates/swarm/agent-report.template.md:5`; `scaffolding/01-foundation/templates/swarm/agent-review.template.md:5`; `lib/swarm_contract.py:625`, especially the name-only product-change test at line 651; completion at `lib/swarm_contract.py:697`; close at `lib/swarm_contract.py:774`. The actual BC2 review describes “a real product change” at `.claude/plans/swarming-work/swarm/reviews/BC2.md:88`, stronger than the implemented check.

**Verification.** In-memory branch execution accepted complete report/review evidence naming a nonexistent product path. Changing the authoritative task's acceptance while retaining its ID still produced `verify_close.ok=true`. This verifies a structural limitation; it does not show that any real lane fabricated its work.

**Impact.** A fresh coordinator cannot reliably distinguish a previously reviewed attempt from changed acceptance, later rework or a different isolated change set using the committed evidence contract alone. Manual Git inspection remains essential but lacks a required link to the recorded PASS.

**Repair.** Preserve readable Markdown and the structural gate, adding compact provenance references: package/leaf source revision or digest, attempt identity, isolation handle, attributable base/result or patch digest, and the exact report/result reviewed. Verify observable facts from the supplied snapshot where possible; invalidate stale review after material source or implementation changes. Keep declared evidence, independently observed evidence and integrated evidence distinct. Do not invent product edits for verification-only work: support an explicit no-change result with appropriate acceptance evidence. **Confidence: high about the gap; no claim of actual fraudulent evidence.**

### SW-04 — P2: Encode project-specific coordinator reducers in the scope contract

**Problem.** The contract declares reducers “coordinator-only”, but the executable protected set consists of three universal paths plus mapped artifacts and lane handoff files. It has no machine-readable set of generated reducers or other project-specific coordinator-owned outputs. A lane may therefore own `skills/CATALOG.md` and pass validation, despite the explicit policy that workers edit canonical sources and the coordinator regenerates catalog outputs.

**Evidence.** `lib/swarm_contract.py:27` and line 32; `lib/swarm_contract.py:450`; `lib/swarm-schema.json:42`; `.claude/plans/swarming-work/spec.md:42`; `docs/concepts/swarming-work.md:65`.

**Verification.** The in-memory fixture accepted `write_scope=["skills/CATALOG.md"]` with `ok=true`.

**Impact.** The deterministic ownership gate does not enforce a central swarm invariant, and overlapping generated/source changes can enter fan-in despite valid topology.

**Repair.** Add coordinator-owned/generated path references from an existing project inventory where possible, or a small explicit topology ownership list. Apply alias-aware overlap checks to scopes and handoff paths. Keep task authority in the original plan: ownership metadata is not a second backlog. Test generated outputs and shared schema/reducer cases, including renamed or aliased paths. **Confidence: high.**

### SW-05 — P2: Adapt Markdown lane briefs to Brief Forge's structured payload

**Problem.** The new explicit swarm call sends its Markdown brief file as content type `brief`. The existing helper simply indents file contents beneath YAML `body.content`; it does not extract the schema's `task`, `constraints` and `acceptance` fields. The template supplies Markdown headings instead. The default subagent policy runs security/stale, so the structured completeness mismatch is not necessarily surfaced.

**Evidence.** `skills/swarm/SKILL.md:110`; `scaffolding/01-foundation/templates/swarm/agent-brief.template.md:10`; `skills/brief-forge/SKILL.md:197`; `lib/brief-forge.sh:66` and line 82; `lib/envelope-schema.yaml:64`; `lib/brief-forge-evaluators.sh:106`; branch default policy is documented at `skills/brief-forge/SKILL.md:26`.

**Verification.** Built the exact body indentation in memory using the committed BC2 brief. None of the three required structured fields were present. A YAML parser was unavailable in this runtime, so no parser-failure claim is made. The structural mismatch is independent of whether some Markdown happens to parse as a scalar.

**Impact.** The mandatory new handoff boundary can produce a payload that does not satisfy its declared schema while being described as forged. The focused new tests exercise policy resolution and evaluator lookup, not this actual caller-to-body interface.

**Repair.** Preserve the rich human-readable brief. Add an explicit structured envelope adapter carrying authoritative task/package references, scope, acceptance and context pointers, with the complete original brief preserved as data. Validate the envelope before dispatch and test the real committed template through the real helper and consumer. Also propagate the resolved trusted source root into this transitive call: the swarm setup supports `CLAUDE_PLUGIN_ROOT`, while the callee's literal source commands still use `LINTEL_SOURCE_ROOT` or `LINTEL_REPO_ROOT`. **Confidence: high.**

### SW-06 — P2: Scope-check the reviewer's attributable changes as well as the worker's

**Problem.** The ownership model gives reviewers exactly their own review path, but `check-scope` only exposes worker scope. The workflow checks the worker's changed paths before dispatching review, then relies on prose for reviewer write ownership. Review completion verifies evidence fields and a distinct identity, but not the reviewer's changed path set.

**Evidence.** `bin/li-swarm.py:73` exposes the worker task-based scope command; `lib/swarm_contract.py:499` derives `write_scope + own_report`; `skills/swarm/SKILL.md:120` performs scope checking before reviewer dispatch at line 123; `.claude/plans/swarming-work/spec.md:31` promises reviewer scope is exactly the review artifact and that the validator checks both extensions.

**Impact.** A reviewer can accidentally modify implementation or another artifact without a corresponding post-review scope gate, weakening the separation that makes lane review independent. A prompt restriction remains useful but is not equivalent to the promised mechanical validation.

**Repair.** Add an explicit reviewer ownership check or actor mode using the same validated ownership map. Capture the reviewer's actual attributable changes and run the check after review, before accepting PASS or integrating. Preserve host-enforced read-only/review-artifact permissions where available and report when enforcement is procedural. Add reviewer-only positive and implementation/coordinator/other-review negative fixtures. **Confidence: high.**

## Integration recommendation

Keep the existing feature and build a coherent red thread:

1. **Authority:** approved requirements → short leaf IDs/acceptance → bounded package mapping in the existing plan.
2. **Topology:** optional swarm pointer → lanes referencing those packages → declared worker/reviewer/coordinator ownership and actual host capacity.
3. **Dispatch:** current authoritative prerequisites → verified isolated assignment → a schema-valid handoff containing the whole brief and its provenance.
4. **Evidence:** attributable result and per-leaf acceptance → actor-specific scope checks → appropriate package spec/quality review bound to that result.
5. **Integration and recovery:** deterministic coordinator fan-in → regenerate shared outputs → integration checks → final REVIEW → durable completion/handoff. Lost attempts never erase preserved work.

Do not replace the current package implementation with old branch copies. Reconcile the focused changes onto current main, retain the enterprise profile and source-root fixes already accepted there, and regenerate adapters/catalog/protocol consumers from their canonical sources. The ADR collision must be resolved before changing implementation annotations or presenting the new documentation as authoritative.

Preserve `/li:swarm init/run/status/resume/verify` and the helpful CLI operations. The helper deliberately is not a scheduler: authoritative dependency checking may remain coordinator-driven if the output continues to be named a candidate frontier and the handoff proves the actual prerequisites were checked. There is no need to introduce a daemon, database or universal spawning API.

For Universal positioning, describe the portable durable contract separately from each host's proven operations. The new source-root discipline and Copilot dependency preflight are useful. Native/sequenced/none metadata must be reconciled with actual callable tools and permissions at dispatch; a product label alone does not prove concurrency or isolation. A no-subagent host can still perform useful implementation and export the exact review package, while substantive independent review remains explicitly pending.

## Verification before integration

Retain the existing focused tests and add discriminating cases for:

- Every ownership-class collision, including report/review versus work map, task source, charter, coordinator reducers and symlink aliases.
- Current main package tables and numeric/tree leaf IDs, Spec Kit IDs, singleton compatibility, verification-only packages and all-leaf acceptance coverage.
- Evidence invalidation after changed acceptance, rework, a new attempt or changed result; proof that the reviewer inspected the exact accepted snapshot.
- Worker **and reviewer** path attribution, independent identity provenance, generated reducer fan-in, and a deliberate scope breach.
- A real Markdown lane brief through envelope conversion/evaluation/validation, including missing policy, unknown evaluator, unavailable evaluator, audit failure and trusted-source propagation.
- One temporary Git integration scenario with two disjoint isolated changes, sequential fan-in and recovery after interruption. The current integration fixture has no Git repository and therefore cannot prove isolation, merge attribution or integrated-tree membership.
- A small host matrix: native isolated lanes, serial fallback, no-subagent/manual independent review, clean consumer checkout and missing adapter dependencies. Distinguish unexercised authenticated client behavior from static packaging coverage.
- Only after the reconciled tree is stable: focused affected checks, generated drift/protocol/catalog checks, independent integrated review and the repository-required full suite. No such final verification was performed during this audit.

## Coverage and limitations

**Full branch files read:** `lib/swarm_contract.py` (783 lines), `lib/swarm-schema.json` (108), `bin/li-swarm.py` (104), `bin/li-swarm` (10), `skills/swarm/SKILL.md` (218), `skills/brief-forge/SKILL.md` (357), `docs/concepts/swarming-work.md` (195), the new swarm ADR (89), specification (48), design (108), plan (173), work map (12), coordination map (53), all four actual worker briefs, all five canonical swarm templates, `tests/unit/swarm-contract.py` (576), `tests/integration/swarm-workflow.py` (189), its shell wrapper (14), and `tests/shape/swarm-contract.sh` (102). Read the full BC2 worker report plus BC2 and BC4 review reports as representative committed evidence; those historical checks were not re-executed.

**Changed hunks read:** PLAN, BUILD, CYCLE, REVIEW, RESUME, CAPTURE, full-engineering-pass, Spec Kit work-map reference, work-map loader, Copilot generator, scaffold helper, Copilot integration tests, Brief Forge policy tests, canonical session protocol, subagent guide and multi-CLI documentation. Read the Brief Forge concept rewrite and the concrete unchanged envelope helper/schema/evaluator portions required to trace the new caller. Main's accepted hybrid ADR was read fully, with current package/leaf templates and dispatch rules inspected for compatibility.

**Not claimed:** a fresh whole-branch audit of all 76 files, execution of the branch's full tests, reconstruction of every historical lane's real isolation, or authenticated execution inside Claude/Codex/Copilot and other desktop clients. Generated inventories and marketing surfaces were inventoried but not all reread in full. Current vendor feature verification belongs to the parent Universal audit.

**Audit execution:** branch objects were read through Git without checkout, reset, merge or original-worktree changes. Actual branch Python was evaluated only with in-memory source/evidence fixtures; no probe artifacts were written. The only authored file for this task is this report. The unrelated working-state changes seen in the shared audit worktree were left untouched.

The feature's value is clear: explicit ownership, preserved context, truthful handoffs and recoverable parallel work. The work remaining is to make its boundaries and evidence as reliable as its stated operating model, while keeping main's short-leaf/package discipline intact.

