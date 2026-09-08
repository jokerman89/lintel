# Plan: Copilot enterprise launch (size: XL · schema: tree)

**Status:** COMPLETE — all seven build cards delivered and merged through PR #83 on 2026-09-08.
**Spec:** [spec.md](spec.md)
**Prompt:** [prompt.md](prompt.md)
**Baseline:** 6b10a84; main was two commits ahead of origin/main. Branch: codex/copilot-enterprise-launch.

## Plan signals

Seven build cards, 31 leaves across DISCOVER, PLAN, BUILD, REVIEW, SHIP and CAPTURE.
Token estimate: approximately 80k–160k, UNCALIBRATED planning range, not a cost measurement.
No model-price assumptions or invented dollar estimate. Implementation authority is already given.

## Build cards

### BC1 — Establish evidence and contracts (root; R1, R9)

- [x] 1.1 Read canonical instructions, relevant lessons, architecture and staged ADRs.
- [x] 1.2 Create feature branch and record initial Git state.
- [x] 1.3 Delegate independent runtime, public-surface and release audits.
- [x] 1.4 Write spec, plan, handoff, ADR and structure-impact record.

Acceptance: artifacts exist and map all ten requirements to the cards below.

### BC2 — Deliver native Copilot onboarding (copilot_runtime; depends BC1; R2–R4)

- [x] 2.1 Define adapter inventory and safe init/check CLI.
- [x] 2.2 Generate portable skills, custom agents and instructions.
- [x] 2.3 Bundle runtime source in consumer repos; dogfood root source here.
- [x] 2.4 Integrate scaffold flag and plan templates; repair legacy shim.
- [x] 2.5 Test fresh clone, idempotence, drift, conflicts and unsafe paths.

Acceptance: new Copilot integration tests and check command pass against generated artifacts.

### BC3 — Align workflow and distribution contracts (root; depends BC1/BC2 interface; R2, R5, R6)

- [x] 3.1 Add explicit Copilot marketplace/plugin descriptors without Claude hook loading.
- [x] 3.2 Update host capabilities and canonical core skill declarations; fix host assumptions.
- [x] 3.3 Add Spec Kit execution bridge preserving artifact ownership and task traceability.
- [x] 3.4 Correct generated planning signals and plugin descriptions; regenerate catalogs/wiki.
- [x] 3.5 Resolve review findings: one committed work map for native/Spec Kit tasks, fresh-clone resume and source-only helper paths.

Acceptance: identity/capability/frontmatter/adapter checks and generated-artifact drift tests pass.

### BC4 — Make the public experience enterprise-ready (enterprise_docs; depends BC1/BC2 interface; R7)

- [x] 4.1 Rewrite README and getting-started around a working Copilot-first path.
- [x] 4.2 Document Copilot surfaces, enterprise rollout and Spec Kit interoperability.
- [x] 4.3 Audit current public docs for stale counts, claims, links and security guarantees.
- [x] 4.4 Update contribution/release notes and review public package descriptions.

Acceptance: a fresh evaluator can install, run a first task, understand trust boundaries and
find support/limitations without relying on unstated Claude knowledge.

### BC5 — Repair release verification and installers (release_quality; depends BC1; R3, R8)

- [x] 5.1 Run baseline and record actual failures/skips.
- [x] 5.2 Repair missing runtime resources and installer portability/failure behavior.
- [x] 5.3 Run all suite tiers in CI and pin downloaded tooling with verified hashes.
- [x] 5.4 Add focused installer/runner regression tests and verify clean install.

Acceptance: complete suite plus installer verification; no silent copy errors or false-green tests.

### BC6 — Review, integrate and capture (root + independent reviewers; depends BC2–BC5 and BC7; R8, R9)

- [x] 6.1 Cross-review each card for spec compliance then correctness/security; resolve findings.
- [x] 6.2 Run final full verification, compatibility audit and generated-artifact check.
- [x] 6.3 Commit atomic changes, integrate to main, push authorized main and inspect remote CI.
- [x] 6.4 Capture final evidence, actual launch limitations and future-operator instructions.

Acceptance: verified Git refs, green required checks and a self-contained completion record.

## Added scope: BC7 — Preserve the complete project startup protocol

**Operator steering:** 2026-09-08 — inspect the personal Boris Cherny-inspired CLAUDE.md,
repeat the startup discipline at repository/project level, reconcile duplication and lose nothing.
**Owner:** enterprise_docs, with copilot_runtime consumer integration; requirement R10.

- [x] 7.1 Read the complete personal protocol and map every section to a reusable or personal-only disposition.
- [x] 7.2 Establish one versioned neutral protocol source and identical inline blocks in repo start files.
- [x] 7.3 Include the complete protocol in both normal and Copilot consumer scaffolding; preserve team content.
- [x] 7.4 Add deterministic parity/coverage and clean-home regression checks, ADR and lesson.
- [x] 7.5 Review no-loss coverage and verify generated startup files before final integration.

Acceptance: a fresh project clone with an empty user home gets planning, subagents, learning,
verification, simplicity, authority, schema, communication and safety disciplines directly in
its project entry files. Personal machine state, private data and marketplace grants are not
promoted into reusable policy. This is deliberate source-generated repetition, not manual drift.

## Review

Independent spec review found and drove repairs to mapped Spec Kit BUILD approval/task sources, committed-work resume, missing ignore verification and CI adapter drift detection. Independent quality/security review passed after installer, consumer execution and compatibility-audit fixes. Final local aggregate passed: 101 tests, zero skips/failures/partial assertions. Hosted CI for `da938538972e49d214a7188e99cbc2c159bbefa5` passed the same complete suite on Ubuntu, macOS and Windows, plus native installation, syntax and generated-artifact checks. [PR #83](https://github.com/jokerman89/lintel/pull/83) merged to main as `52c7b3857f86fb7d118c9f2811cc914f667b1150`.

The [completion review](review.md) records exact hosted runs, resolved findings and acceptance
boundaries. Version 0.9.0 remains beta: authenticated model work, VS Code/cloud-agent behavior,
enterprise tenant controls and marketplace listing have no acceptance evidence from this batch.
This completed plan is a delivery record, not continuing permission for new main pushes,
publication or data transfer. New work requires a current operator request.
