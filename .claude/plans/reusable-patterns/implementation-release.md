# Reusable patterns implementation release

Authority: operator instruction of 2026-09-24 22:38 +02 authorizes implementation
after the legacy audit, nested Opus 5.5 long-context High swarming, a feature PR,
and landing this batch after passing CI and required reviews. The 2026-09-25
14:06 instruction also asks for existing PR delivery. Existing owners retain
their work; this feature must not contact, mutate or take over unrelated sessions.

## Verified prerequisite and baseline

PR #104 is MERGED at 2026-09-27T21:07:41Z, merge commit
`224135581d4dd71f18d39efe5c0882b7e65ec76d`, reviewed head
`22d502be6251033f81eccd1b1fa69dc3bf3ec947`. All 24 hosted check-rollup
entries completed successfully. Its PR body records independent specification
and quality reviews on that head. Main was fetched and this coordinator's clean
isolated worktree fast-forwarded to the merge. The prerequisite is satisfied.

The five original planning artifacts are inputs, not executable authority or
evidence of a build. Their DRAFT/no-publication wording describes the earlier
planning-only delivery and is superseded for this feature by the authorization
above. Preserve R01-R16 and all 48 leaf IDs during reconciliation. No production,
credential, real-home installation, private pack or cloud-tenant mutation is granted.

## Required reconciliation with landed architecture

1. ADR-0029 and `lib/profile_context.py` now own pack parsing, provenance,
   required-policy failure, stable contexts and explicit rebind. Reuse those
   typed records and their shell adapters. The old proposed origin/snapshot
   accessor is an output requirement, not permission for a second parser or
   a competing cache. Pointer drift must follow the current fail-closed contract.
2. ADR-0028 and current shared v2 review/QA/lifecycle contracts remain the only
   release-clearance authority. Pattern clause coverage is supplemental content
   evidence consumed by them, never a parallel PASS that clears stale/missing
   independent review or a later rejection. Preserve work/task/profile binding.
3. ADR-0034 retained the nine cycle phases, engineering modules and specialist
   style capture, but consolidated some planned callers. Wire their current
   owners rather than recreating retired skills. In particular, mockup output
   belongs to `generate-web --mode mockup`; built-UI review belongs to
   `frontend-design-review`. Use `verify`, `inspect`, `cross-check`, `pause`
   and current `resume` where applicable. Consult the current migration document.
4. ADR-0033 removed the PDF reader. Retain current PDF writer/print and workbook,
   Word, slide and other provider capabilities. Do not label working providers
   as template slots because the old plan did. Do not add a PDF reader, pypdf or
   a third-party dependency. Distinguish helper tests from actual format/host
   acceptance and report unavailable observations honestly.
5. ADR-0027's swarm topology and current source/target-aware installation,
   discovery and generated-adapter inventories are already implemented.
   Extend their real dependency closure, not a new installation registry.
   Bare installation must not gain a Python prerequisite; runtime pattern
   operations may require the existing optional Python toolchain explicitly.
6. Main may advance with the separately owned client/docs batch. Integrate
   settled changes with ordinary merges, never reset/amend/rebase/force-push.
   Do not edit their worktrees or rewrite their historical evidence. Allocate a
   new unused ADR number at implementation time, avoiding the reserved client
   ADR-0035 and existing MARS/CI decisions.

## Execution ownership and handoff

The parent coordinates app-native nested worktrees. One integration child owns
the promoted work map, contract, core runtime/lifecycle and aggregate feature PR.
Its first release is P0 plus P1, including the public typed interfaces and runnable
core tests. It reports a frozen contract and commit before dependent lanes launch.
The parent then assigns disjoint pack/installation and workflow/visual integration
lanes against that contract. Shared generators and final plan/evidence reduction
stay with the integration owner. No lane changes another lane's files.

Use `claude-opus-5.5`, `context_tier: long_context`, `reasoning_effort: high`
for each requested nested session (the host exposes long_context, not a numeric
context-size guarantee). Independent review is a separate actor from implementers.
Use ordinary bounded sessions, not a factory. Record exact baselines, change sets,
commands, outcomes and limitations. Use the installed Lintel work-map/swarm and
shared acceptance contracts proportionately; never fabricate host receipts.

P0 must promote and reconcile the planning bundle in the feature checkout and
produce the actual dependency graph/topology. The parent may approve a documented
safe reordering to enable independent lanes; leaf acceptance cannot be dropped.
For now, do not dispatch dependent implementation before P1's contract is frozen.
No feature PR before aggregate implementation, regression/full-suite evidence
and independent review. The integration owner creates the PR with the host tool.
The parent verifies hosted CI/reviews and the exact merged main result.
