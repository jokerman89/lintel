# Lintel whole-system enterprise value review

Date: 2026-09-08. Baseline: `6b10a84`. Independent branch: `codex/enterprise-value-review`.
This review excludes the concurrent Copilot session's uncommitted changes from its baseline.
Findings below cite baseline locations; fixes are assessed through this branch's diff and tests.

## Assessment

Lintel has a useful architectural separation: a neutral workflow spine, company packs,
canonical state/path helpers, specialist modules and selected executable controls. Its main
enterprise weakness is the incomplete connection between a declared requirement, a capability
installed on the actual host, its execution and evidence that the result satisfied it.

More skills, prompts or gates alone do not close that gap. Prioritize correct profile
resolution, explicit requirement coverage, coherent work packages and realistic evaluations.
This branch improves those paths. It is not a claim that Lintel is ready to serve as a mandatory
enterprise enforcement layer; two pre-existing P1 Git collection defects remain open.

## Coverage and limits

| Area | Review performed | Evidence limit |
|---|---|---|
| SENSE through CAPTURE | Phase contracts, routing/sizing, plan/template, BUILD/review, gate and handoff links | Selected executable snippets and helpers; no autonomous nine-phase host run |
| Profiles and packs | Activation, inheritance, scalar/list reads, validation, consumers, digest | Synthetic enterprise/default comparisons; no private company pack or user profile changed |
| Runtime continuity | State, jobs, checkpoints, resume path, registry | Static review plus existing tests; no cross-process registry stress test |
| Safety controls | Hook registration, Git collection, scanner failure paths | One failure probe and static history analysis; no live protected push |
| Installation and host differences | Bare installers, plugin activation, source/target assumptions | Baseline source review; concurrent Copilot fixes are separate |
| Engineering modules | TA → DA/SC → DH → TQ composition and module/test contracts | System-level inspection, not exhaustive validation of every specialist's reasoning |
| Content workflows | Shared generate pipeline, format slots, brand/voice inputs | Contract spot checks; no document rendered or output-quality evaluation |
| Knowledge and efficiency | Memory authority/continuity, calibration provenance, recurring dispatch cost | No measured enterprise productivity pilot |
| Verification | Existing shape/unit/integration design, staged eval architecture | Shape presence does not prove agent behavior; independent scenario review recorded below |

Three initial reviewers used repository Planner, SystemArchitect and CodeReviewer roles in
separate contexts. Implementers did not close their own review findings; an independent code
review and fresh-context scenario assessment follow implementation. This is broad system review,
not an assertion that every line of every skill and host adapter has been tested.

## Findings

Initial severity count: **P0 0, P1 7, P2 15**. P1 means material correctness/enforcement impact;
P2 means bounded correctness or adoption gap. Status distinguishes this branch from other work.

| ID | Severity | Baseline evidence and consequence | Disposition |
|---|---|---|---|
| F01 | P1 | `lib/pack-resolver.sh:334–380` returns empty for block lists; `skills/compliance-gate/SKILL.md:60–65` treats empty requested gates as a no-op | Shared scalar/list extraction and consumer integration regression |
| F02 | P1 | `lib/orientator-routing.sh:76–78` compares CSV against raw YAML list syntax; a declared high-risk cycle can become low risk | Normalize list members before exact route matching |
| F03 | P1 | `lib/pack-resolver.sh:130–178` accepts empty required nested fields and missing/deep ancestry | Validate effective inherited requirements and every ancestry link; semver remains explicitly unverified |
| F04 | P1 | `skills/pack-create/SKILL.md:92–104` copies neutral blocks before adding `extends`, replacing parent company controls | Emit a minimal inherited child; execute the real creation snippet in integration test |
| F05 | P1 | `hooks/shared/_input.sh:113–114` scans net upstream diff or ten recent commits; add-then-remove secrets remain in outgoing history | **Open release blocker:** collect actual outgoing refs and inspect every introduced commit; cover non-HEAD and long-history cases |
| F06 | P1 | `hooks/shared/_input.sh:110–117` suppresses Git failures; real collector with a failing Git stub returned success and empty bytes | **Open release blocker:** separate collection failure from successful empty scan; block the matched mutation when inspection fails |
| F07 | P1 | `skills/scope/SKILL.md:104` treats a non-default branch as a deliverable; line 150 can emit `buildDEFINE` | Require identified artifact evidence and write one resolved intent; actual snippet regression |
| F08 | P2 | `hooks/shared/session-digest/run.sh:32` reads stale profile identity while `pack-switch` changes the pointer | Digest reports the actually loaded pack |
| F09 | P2 | `skills/pack-validate/SKILL.md:99–104` always exits failure in awk END; line 123 invents a current version | Delegate checks to the shared runtime validator; compatibility is reported as not verified |
| F10 | P2 | `lib/orientator-routing.sh:45–52` uses company default only for unclear intent and prefixes extension defaults with `/li:` | **Open:** define and verify extension workflow routing without duplicating host discovery |
| F11 | P2 | `docs/getting-started.md:157–166` implies repository-scoped profile switching, but the pointer is machine-global | New enterprise guide explains actual activation; reconcile older onboarding text with the concurrent adapter work |
| F12 | P2 | `lib/scale-estimator.sh:56,84,114–117`: `api` in “capital”, `all` in “small”; multi-tenant work undersized | Token boundaries and tenant size floor, with positive and negative cases |
| F13 | P2 | `skills/plan/SKILL.md:147` sums a whole-cycle calibrated prior over every leaf | Use one cycle estimate; emit basis and sample count while retaining numeric API |
| F14 | P2 | Canonical plan template invents dollar cost, defaults to APPROVED, shows always-on minutes and a 15-minute leaf | Draft template, honest optional estimates, leaf acceptance/ownership/evidence and package mapping |
| F15 | P2 | `skills/plan/SKILL.md:322–327` selects the newest directory and checks only nonempty trio files | **Open:** explicit work selection and semantic artifact validation; concurrent Copilot branch has separate work-map corrections |
| F16 | P2 | `skills/build/SKILL.md:112` rejects an explicitly planned verification-only task because it has no diff | Review its command/result evidence; retain the guard for change-producing leaves |
| F17 | P2 | `skills/build/SKILL.md:20,143` says pack hooks automatically run across hosts | Record requested controls, actual implementation and proof/missing capability |
| F18 | P2 | `install/install.sh:154–157`, `install/install.ps1:123–125`: installed default pointer has no installed default pack; E2E sources checkout and masks it | **Separate work:** observed fixes in concurrent checkout, not present or credited on this branch |
| F19 | P2 | `skills/resume/SKILL.md:189` reads scope from the jobs parent directory, inconsistent with its own line 310 | **Open:** consume an explicit authoritative scope/work path and test the actual resume chain |
| F20 | P2 | `bin/_context.sh:56–75` mixes same-branch legacy checkpoints from different repositories | **Open:** establish owning repository before automatic selection; include two-repository regression |
| F21 | P2 | `bin/_jobs.sh:389–420` reads/replaces the shared registry without serialization | **Open:** protect against lost updates or derive from separately owned records; authoritative job directories survive |
| F22 | P2 | `tests/behavior/build-pilot.sh` only greps prose, although behavior-tier documentation describes executable proof | **Open:** label the existing pilot truthfully; new branch integration cases provide actual helper/snippet evidence, not model evaluation |

## Planning decision and efficiency

The operator explicitly selected **hybrid** execution. ADR-0026 records the alternatives and
the decision: retain short leaves, execute a coherent package with one owner, review the
whole package for spec then quality, and retain evidence for every leaf. Legacy plans become
singleton packages. Packages with substantive integration still need independent review;
grouping small leaves does not downgrade the combined risk.

This removes a source of repeated setup without creating another scheduler or backlog.
It does not establish a numeric saving. Capture actual usage, intervention, rework and
defect rates in a representative pilot before choosing package-size budgets or claiming ROI.

## Company profile value

PLAN now carries the missing connection: loaded pack/source → applicable requirement →
existing leaf/package IDs → observable acceptance → evidence. Neutral tasks add no invented
company requirements. A team overlay retains the parent's required blocks. The enterprise
guide distinguishes executable helper behavior, agent-driven application and actual host
enforcement, and defines a before/after pilot.

Several fields remain availability declarations with no verified automatic consumer, including
parts of know-how/opinions/role defaults and data-residency metadata. Extension flags describe
available surface, not installation. Do not market those settings as controls merely because
they can be resolved. `brief_forge_handoffs` can now be read at nested paths, but automatic
envelope construction remains dormant under ADR-0008.

## Remaining architectural choices

- Invalid active packs currently fall back to `_default` by accepted architecture. A stricter
  enterprise activation mode would need an explicit decision and migration design; this branch
  does not silently replace that contract.
- Pack schema prose promises special evaluator-list merging, while the implementation and
  architecture use top-level block replacement. Resolve that inconsistency explicitly before
  relying on inherited evaluator composition.
- Strict schema/semver enforcement is not implemented. The validator now states that limit
  instead of reporting a fabricated compatibility pass.
- The staged model eval harness (ADR-0021) remains the route to repeatable agent-quality evidence.
  A large new harness was not added as part of these corrections.

## Verification record

- PASS: aggregate runner, **93/93 test scripts** (49 unit, 6 integration, 36 shape,
  1 behavior, 1 e2e). This full run preceded the final parser/cache edge repairs;
  final focused regressions are recorded separately below.
- PASS: targeted scale-estimator/calibration, workflow-root-and-trio and edited-skill
  frontmatter checks. `git diff --check` is clean.
- PASS: final enterprise unit, all nine existing fallback scenarios, three-level
  inheritance and extension contract checks. Cases cover indentationless lists,
  quoted-key rejection, whitespace alignment and primed-cache invalidation.
- PASS: final actual SCOPE, pack-create and BUILD snippets, including BLOCKED
  returning to BUILD with a repair note and success returning to REVIEW. Synthetic
  enterprise impact exercises field/risk/digest consumers; it does not execute a
  private compliance hook or prove host enforcement.
- PASS: all five plugin/marketplace JSON files parsed with PowerShell and version
  parity at unreleased 0.10.0. Catalogue regenerated by the canonical workflow code.
- Bash syntax checks passed. `install/verify.sh --all` returned 0 and reported
  ALL CHECKS PASSED. Its upstream listing skipped because `yq` is absent; its
  unchanged legacy counter (`install/verify.sh:317,328`) emitted an integer warning
  because `grep -c ... || echo 0` produces two zeros on no matches. This diagnostic
  is an additional existing verifier issue, outside the initial 22-finding count;
  it is not counted as a clean verification of that legacy counter.
- The first aggregate unit run exposed one invalid capture fixture (`mode: none`,
  `default_route`). Corrected to existing schema values (`off`, `default_workflow`)
  without weakening its assertion. A continuity check required host write permission
  for this worktree's runtime directory and then passed; no personal profile changed.
- Runner reports zero whole-script skips, but several internal JSON assertions skip
  when `jq` is unavailable. Manifest JSON/parity was checked separately; jq-based
  hook-envelope extraction remains for CI. Generic skill-creator quick validation
  was unavailable because bundled Python lacks PyYAML; no dependency was installed.
- No real company profile, live hook registration, production action, measured
  productivity pilot or full model-level cycle was tested. The behavior-tier prose
  check is not reclassified as an executed agent scenario.

## Independent review of the changes

The fresh-context hybrid scenario used two packages and five leaves: one mechanical
documentation package and one substantive service package covering schema, handler,
integration and a verification-only access-denial check. Failed implementation keeps
the affected package open; completed independent work stays complete. Aggregate risk
requires independent spec then quality review, even when each leaf is small.

The reviewer initially found three P2 inconsistencies: assumed hook availability,
hardcoded models, and a BLOCKED ledger pointing to REVIEW. All were repaired by the
coordinator and independently closed. Final scenario review: **P0/P1/P2/P3 = 0**.

The independent pack implementation review found two P2 issues: quoted keys could
validate but disagree with inheritance merging, and rejected ancestry could be mistaken
for a fresh cache. Follow-up found a whitespace variant of the key issue. The coordinator
repaired them and added regressions. Final bounded code review: **P0/P1/P2/P3 = 0**.
Reviewers made no repairs to their own findings. These clean diff reviews do not close
the baseline findings explicitly left open in the whole-system table.

M2 remains **RED pending explicit operator override**. The generated report includes a
manual disposition of each affected contract; a clean test suite does not grant that override.

## Delivery and next action

The review and compatible improvements are verified on the isolated feature branch. Obtain
the explicit M2 disposition before publishing the prepared PR. Reconcile overlapping changes with the
Copilot branch before combining them. Address F05 and F06 before treating local Git hooks as
a reliable enterprise release control. Then run the measured pack pilot; evaluate further
complexity only against its results.

Implementation commits: `edcb2b8` (effective enterprise packs) and `8676097`
(hybrid planning and execution). Review evidence, onboarding guidance and unreleased
manifest/catalogue updates are in the following documentation commit. No remote branch,
PR, release, personal installation or production environment was changed.
