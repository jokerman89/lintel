# Plan: complete the original V2 findings

**Status:** APPROVED for the three-clause continuation's scope under existing
operator authority. The previously delivered scope and its approval remain
historical facts. BUILD still requires the current independent plan-review gate;
this approval is not a claim that review or implementation has passed.
**Spec:** [spec.md](spec.md).
**Work map:** [work.json](work.json).
**Base:** `f9796bb8b3fbcdab3e235f30401933ea1b2f3162`.
**Execution:** coordinator-owned, dependency-ordered packages; no automatic swarm.
**Continuation baseline:** `19fd4dccc44c1d7de37f5e89afca7e3c69361435` (0.13.8).

**Captured delivery:** the elaborated P1-P8 clauses and P9 source-delivery
obligation landed in 0.13.8 at `b2516af57244017160c499558f183f95e7a9fe5c`.
Checked boxes cover these bounded clauses, not all clauses of each original
finding. The original programme remains open; see
[verified delivery](#verified-delivery-2026-10-04).

The complete remaining inventory still contains ready implementation, not only
external blockers. Original `lane-A-07`, `lane-B-09` and `lane-B-11` are now
elaborated in P10. Their full claims were reread against 0.13.8. B-09/B-11 move
from P3 into P10 for their remaining clauses, without changing their IDs or
rewriting the prior P3 review. P9 is reopened for the next aggregate delivery.
The current map has 56 original task IDs across ten packages; every previous ID
is retained, with A-07 the only newly elaborated original finding.

## Outcome and signals

The final outcome is correction of the original findings, not the delivery of
another convenient subset. Preserve all 84 original IDs in the requirement
inventory. Split coherent packages at their actual ownership and compatibility
boundaries; a completed package leaves every other finding open.

Scope size is XL. Phases are PLAN, BUILD, REVIEW, VERIFY, SHIP and CAPTURE.
Runtime/token cost is unmeasured; no time, price or calibrated productivity claim
is supplied. The operator has authorized implementation. Resolve only genuine
new architecture or permission decisions.

## Original finding areas

| Area | Outcome | Original finding IDs | Edit boundary | Dependencies |
|---|---|---|---|---|
| Generation safety | Non-mutating QA, owned output, real share controls and measured contrast | lane-d-04, lane-d-05, lane-d-06, lane-d-10, lane-d-12 | Canonical generation/design methods, existing shared admission/checker helpers and focused tests | None |
| Generation fidelity | One retained source-fidelity/inspection method and truthful provider limits | lane-d-02, lane-d-03, lane-d-07, lane-d-08, lane-d-09, lane-d-11, F-02 | Generation/frontend owners, references, read-only checkers and direct tests | Specific retirement/ADR decisions before affected changes |
| Core planning | Observable decision boundaries without repeated permission questions | lane-A-01, lane-A-02, G-02, G-03, G-06, G-07, ENT-04, ENT-06 | Existing planning/intake/inspection methods and their tests | ADR-0026 decision for removing the fixed duration rule |
| External work authority | Reuse selected Spec Kit artifacts without inventing a parallel backlog | lane-A-05, G-01, G-11 | Spec Kit bridge, mapped readers and direct consumers/tests | Inspect the supported local interface before changing its schema |
| Coordination | One owner per routing/role/observation method, truthful built-in evaluator semantics | lane-B-04, lane-B-05, lane-B-06, lane-B-07, lane-B-09, lane-B-10, lane-B-11, lane-B-12, C-04, C-06, C-07, C-08, C-09 | Existing coordination methods/helpers and coupled checks | Keep source ownership and old saved-data contracts |
| Agent methods | Preserve differentiated reasoning and remove contradictory role/consumer contracts | lane-E-01, lane-E-01b, lane-E-02, lane-E-03, lane-E-04, lane-E-05, lane-E-06, lane-E-08, lane-E-09, lane-E-10, lane-E-11, lane-E-12, lane-E-13, lane-E-14, F-03, F-05, F-06 | Canonical roles, owning methods, native-role generator and direct tests | Specific preservation mapping before a wrapper retirement |
| Policy conformance | Explicit control ownership and failure behavior without invented enforcement | C-02, C-03, ENT-02, ENT-03 | Existing controls, documentation and synthetic conformance tests | Preserve pack inheritance; no native-hook hold workaround |
| Portfolio and evidence | Resolve actual default-surface and efficacy questions, not blanket administrative blockers | lane-d-01, F-01, F-04, C-05, G-04, G-05, G-08, G-09, G-10, G-12, G-13, ENT-01, ENT-05, ENT-07, ENT-08, lane-A-08 | Existing capability selections, source-backed docs and approved evidence interfaces | Explicit decisions where architecture or experiments change |
| Prior-delivery reconciliation | Retain complete fixes and identify residual clauses | lane-A-03, lane-A-04, lane-A-06, lane-A-07, lane-B-01, lane-B-02, lane-B-03, lane-B-08, C-01, C-10, lane-E-07 | Read existing source and original claims; reopen only real residuals | Do not rerun completed release acceptance |

## Work packages

These group the elaborated compatible task clauses, not all recommendations
listed above. The coordinator owns the integrated result and all shared files;
implementation delegates ran sequentially with attributable preimages.
Original finding cards are not represented as measured 2-5 minute work. Their
bounded source/test substeps and actual command evidence are retained per package.
The coordinator records that granularity concern explicitly instead of inventing
elapsed estimates or dropping the original finding IDs.

| Package ID | Outcome | Leaf IDs (dependency order) | Owner | Dependencies | Acceptance evidence |
|---|---|---|---|---|---|
| P1 | Artifact input/output and inspection safety | lane-d-10, lane-d-04, lane-d-05, lane-d-06, lane-d-12 | Coordinator | none | Original source/fixture and numerical contrast criteria |
| P2 | Evidence-correct agent methods and callers | lane-E-04, lane-E-08, lane-E-09, lane-E-11, lane-E-13, F-04, F-05 | Coordinator | none | Actual role/caller and preservation checks |
| P3 | Consistent coordination methods | lane-A-01, lane-A-02, lane-B-06, lane-B-08, lane-B-12, C-02, C-07, C-08, C-09 | Coordinator | P2 | Signal, lifecycle, warning and unchanged-control tests |
| P4 | Shared document/design fidelity | lane-d-03, lane-d-07, lane-d-08, lane-d-09, lane-d-11, lane-E-14, F-02 | Coordinator | P1 | Real checker/emitter negatives and source preservation |
| P5 | Shared discovery/lifecycle observations | lane-B-04, lane-B-05, lane-B-07, lane-B-10, C-04, C-06 | Coordinator | P3 | Real transport, reader and retained-interface tests |
| P6 | Preserved role/runtime capabilities | lane-E-01, lane-E-01b, lane-E-02, lane-E-03, lane-E-05, lane-E-06, lane-E-10, lane-E-12, F-06 | Coordinator | P2, P4, P5 | Actual configuration/helper tests and inventory parity |
| P7 | Original external authority and required controls | lane-A-05, G-01, G-11, ENT-02, ENT-03 | Coordinator | P6 | Real map/profile/evidence refusal and preservation tests |
| P8 | Conditional core methods and usable hot memory | lane-A-06, lane-d-02, ENT-05, F-01 | Coordinator | P3, P4, P5, P6, P7 | Full procedure/history equality and current caller checks |
| P10 | Complete original premise and recovery-method handoff | lane-A-07, lane-B-09, lane-B-11 | Coordinator | P3, P8 | Exact method preservation, real snippet regressions and native resource closure |
| P9 | Verified generated and delivered aggregate | V2-INTEGRATION | Coordinator | P1, P2, P3, P4, P5, P6, P7, P8, P10 | Current local/hosted verification, independent review and actual delivery |

## First ready leaf

- [x] lane-d-10 Make artifact QA report-only by default and repair only into a distinct authorized output.

**Files:** `skills/generate-qa/SKILL.md`, the direct `generate` caller if it
supplies a repair default, and the existing document-generation regression harness.
**Requirement:** OWNERSHIP; original lane-d-10 claim.
**Acceptance:** an inspection of a teammate's artifact does not edit it. `safe`
and `aggressive` need explicit selection and a distinct owned output; the report
path never stands in for the repaired artifact path. Preserve input bytes and
rerun affected checks on the copy. An unavailable output is an error, never
fallback to the source or current directory.
**Verification:** discriminating source/fixture checks plus the affected existing
document pipeline suite; source-contract checks are not model-efficacy proof.
**Evidence:** the source, independent review and actual delivery evidence are
recorded in the verified-delivery section below. Original acceptance is retained.

The coordinator reviewed this bounded leaf against the full original claim and
current QA/caller sources before implementation: changing the default and copy
destination preserves every check, mode and required-evidence gate. This is an
inline mechanical plan review, not independent or whole-programme clearance.
The package's final source and quality review remains required.

## Remaining leaf elaboration

- [x] lane-B-08 Correct the remaining checkpoint examples against the actual repository-key grammar.

The native pause entry and phantom-hook corrections already exist. The remaining
source examples must include the full repository key, identify any sample key
as synthetic, and direct readers to the actual reserved path. Preserve every
checkpoint filename/ownership rule; the helper and current resume behavior do
not change. Verify the real helper's key and every published example.

- [x] lane-B-10 Use the shared usage/audit reader with honest manual-report and coverage boundaries.

Coordinator owns this bounded residual: retain the manual writer and report
flags, route reads through the existing audit owner, and remove stale
single-log/task-authority claims. Verify `UsageReportContracts` including
actual event-reader preservation and the source-owner guard.

- [x] lane-d-04 Replace nonexistent generation share gates with actual named controls.
- [x] lane-d-05 Require explicit owned outputs instead of personal-home or current-directory fallbacks.
- [x] lane-d-06 Ship a read-only contrast measurement helper over actual observed colors.
- [x] lane-d-12 Make generation and design descriptions task-triggered and current.

**Generation safety owner:** one sequential implementation delegate for these
four leaves; the coordinator retains lane-d-10 and its caller changes.
**Files:** the generation and frontend canonical skills named by the original
findings, their actual shared references/helpers, `skills/design-dna/scripts/`
and focused generation/contrast/description tests. Do not edit `generate-qa`,
`generate`, shared reducers, version, pack/schema, ADR, memory or other packages.

**lane-d-04 acceptance:** every replaced flag/hook/role has a real operation or
an explicit model/manual/unavailable control. Licensing and brand obligations
remain mandatory when the actual brief/profile requires them; no made-up
`compliance-gate --check`, `brand-staleness-warn` or `li-doctor --brand-summary`
route is necessary. No new scanner, license verdict or hook is introduced.

**lane-d-05 acceptance:** source/brand directories are explicitly selected or
resolved through the verified profile. Output writes target an explicitly owned
destination. An unavailable destination produces a diagnostic and no fallback
write to HOME, current directory, another artifact or another run.

**lane-d-06 acceptance:** a small standard-library read-only helper computes
WCAG relative luminance and contrast from actual reported foreground/background
colors. Black/white is 21:1, equal colors 1:1, normal text requires 4.5:1 and large
text 3:1. Invalid, unresolved, translucent-without-known-compositing-background,
gradient/image and missing observations remain invalid/unverified, not white or
passing. The helper reports the ratio/text-size observation, never inventing
browser execution or a P05 clearance record. Wire it from the existing design
validation method and retain existing checks.

**lane-d-12 acceptance:** applicable canonical descriptions use concrete "Use
when/to" triggers, remove archaeology and universal proactive imperatives, and
remain faithful to implemented behavior. Preserve names, capability boundaries
and required attribution. Extend the existing description guard where possible.

**Verification:** source-specific negative cases for obsolete gates and implicit
outputs, numeric and invalid-input contrast tests against the shipped helper,
and the existing description/design tests. Record actual commands, counts and
limits. Report any dependency-closure additions to the coordinator rather than
editing shared generated files. Independent review follows the frozen result.

Coordinator follow-up to lane-d-04: remove the nonexistent Visio role while
preserving the current slot and actual writer requirement. That one reference is
an ordinary correction, not a user-imposed hold or permission to retire the skill.
The delegate's original report is preserved; its reservation was coordinator-owned.

- [x] lane-E-04 Route planning-only operations to planning-only capability.
- [x] lane-E-08 Make remaining role templates obey their own evidence rules.
- [x] lane-E-09 State actual tool/evidence handoffs instead of unavailable operations.
- [x] lane-E-11 Keep persistence ownership with the authorized caller.
- [x] lane-E-13 Derive release notes from delivered behavior rather than invented prefix mappings.
- [x] F-04 Require dated primary-source applicability and a responsible owner without fabricating legal currency.
- [x] F-05 Share actual voice/consent guards and remove false compliance-as-voice routing.

**Agent-correctness owner:** one sequential delegate, after generation safety
returns. Read each full original claim and check prior V2 repairs before editing.
**Files:** the canonical roles identified by these claims; direct DH/SC/review
callers only where routing changes; focused existing/new role-method tests.
No role retirement, tools expansion, generator, pack/schema, ADR, new provider,
active security scan, network, legal advice or shared memory/plan change.

**Acceptance:** DH/SC planning-only work no longer depends on an execution role;
execution/publication still requires actual authority. Remaining Planner and
PerfBudgetEnforcer templates carry viable choices and evidence-derived budgets,
not fixed preferred answers or thresholds. A role lacking a tool hands the exact
observation to an available authorized caller and states the limitation.
Read-only specialists return proposed content; only their caller chooses and
persists the mapped artifact, preserving migration-plan compatibility.
Changelog guidance distinguishes breaking changes, explicit deprecation, reverts,
release diffs and existing hand-authored entries without invented commit-prefix
semantics. Regulatory templates support overlapping obligations with explicit
source/version/date/owner and unverified currency, not an exclusive risk ladder.
Customer drafters use the actual `voice.gates_active` field and preserve consent,
proof and authority without claiming a compliance hook is a voice critic.

**Verification:** discriminating tests against actual source/templates and
existing role/domain routing contracts; mark documentary tests honestly.
Already corrected clauses need evidence and no gratuitous rewrite. Preserve
names and functional capabilities. Report separate consolidation proposals as
still open, never as a reason to omit these compatible corrections.

- [x] lane-A-01 Base sizing/ambiguity judgments on actual work, with lexical estimates as hints.
- [x] lane-A-02 Remove repeated approval and default complete-code prescriptions while retaining accepted leaf constraints.
- [x] lane-B-06 Describe built-in handoff checks and fixed accounting honestly.
- [ ] lane-B-09 Preserve corrected resume precedence and finish reference-owned job, tree, swarm and ledger recovery.
- [ ] lane-B-11 Preserve named contract owners and move Swarm's shared-evidence consumer into its reference.
- [x] lane-B-12 Render MARS offers from the observed roster, with host-specific mechanics in references.
- [x] C-02 Label optional domain-hook heuristics accurately and remove unsupported override advice.
- [x] C-07 Ask for observed lesson efficacy/recurrence instead of inventing reference frequency.
- [x] C-08 Remove unsupported engineering preference-contract claims.
- [x] C-09 Put scaffold-mode acceptance reasoning with the owning scaffold method.

**Coordination-method owner:** one sequential delegate. Scope includes the
canonical skills named by these ten claims, directly linked references,
`hooks/shared/da-migration-irreversible-warn/` and
`hooks/shared/sc-auth-bypass-warn/`, and focused existing/new tests.
No hook registration or native adapter work is included.

**Acceptance:** SCOPE/PLAN use actual requirements, owners, interfaces,
uncertainty and rollback boundaries to interpret their existing estimates.
The lexical helper remains a hint and cannot decide that an unrelated-domain
ambiguity is absent. Only unresolved decisions prompt; existing authorization
is retained, signals presented once and default plans specify interfaces and
acceptance instead of prewriting implementations. Keep ADR-0026's short leaves,
the nine phases, mandatory review/control and approval requirements unchanged;
the original proposal to repeal those rules remains a separate open clause.

Built-in Forge results distinguish binary/diagnostic results, missing-pointer
failure and fixed accounting from measured quality/token usage. Keep the existing
protocol and custom evaluator semantics. Resume has one clear precedence/decision
table, consistent seven-day warnings and a real selected baseline command or an
explicit unrun limitation, not a checkbox pass. Move job/tree/swarm details to
references only with complete caller/resource/test preservation.

Translate package identifiers to named source/evidence/profile contracts without
renaming their persisted IDs. MARS preserves live roster, accepted defaults and
consent; public examples do not select a hard-coded current model or imply a
particular host tool is available.

Existing optional DA/SC hooks remain advisory filename/regex heuristics, never
proof of reversibility or authorization. Remove unparsed override flags and dead
array-population code without changing activation or policy. Lesson capture
distinguishes observed downstream benefit, recurrence, and unknown; no counter
or automatic calibration is invented. Unsupported module `preferences_root`
metadata must not be presented as a typed pack contract; preserve actual optional
preference data and whole-block inheritance without adding schema keys.
Scaffold owns internal-tool/MVP acceptance/failure questions; retain existing
aliases/modes, output ownership and no-installs-without-authority behavior.

**Verification:** actual signal/helper or inert method fixtures for each changed
path, existing scope/plan/resume/MARS/Forge/domain-hook/scaffold checks as affected.
No full-suite rerun, model experiment, global profile mutation, private-data read,
generated reducer or ADR change by the delegate. Preserve preceding packages,
or document exact intentional overlaps before editing a shared caller.

- [x] lane-d-03 Ship the existing PPTX notes/retention inspection as a read-only checker.
- [x] lane-d-07 Use one shared frontend-fragment publication procedure without canned vendor choices.
- [x] lane-d-08 Keep one advisory review rubric and require observations for performance claims.
- [x] lane-d-09 Remove nonexistent generation-resume and obsolete acceptance promises.
- [x] lane-d-11 Correct unproven superiority and overbroad adaptation attribution claims.
- [x] lane-E-14 Give documentation fidelity one shared owner consumed by BUILD, SHIP and docs front doors.
- [x] F-02 Use one narrative structure and one axis publication owner without duplicate default contexts.

F-02's remaining compatible work keeps every named role. A shared narrative
reference supplies the common arc/genre/timing questions to slide and demo views;
the axis ownership reference separates a role's draft decision from the caller's
single publication. Preserve doctrine, schemas, notices and unique expertise;
no default second planner or unsupported licensing lookup is implied. Verify
both actual caller/reference links and retained fragment-emitter behavior.

**Fidelity owner:** one sequential delegate. Allowed canonical generation/
frontend methods, their existing shared helpers/references, the three directly
coupled doc/design reviewer roles, BUILD/SHIP/DocWriter/generate-docs caller
links, factual upstream-attribution records and focused tests. No public
entrypoint retirement, new renderer, pack extraction or schema rewrite.

**Acceptance:** promote the real OOXML notes-alias and source-retention checks
from test-only code into a standard-library read-only checker that callers can
invoke on explicit inputs. Keep archive/XML reads bounded and reject malformed,
external, missing or aliased notes references. Test actual notes relationships
and missing source detail; never claim native editability or rendered layout.

The three frontend partial producers use one existing-library publication owner
with the same profile/input/readback guarantees. Remove stock vendor/color
prescriptions from those decisions while retaining none/CSS/library/no-shader
branches and all legitimate licensed sources. The existing six canonical
advisory dimensions are the only output rubric; unmeasured FPS, FOIT and jank
stay unverified, never scored as observed from screenshots or simple DOM reads.

Generation no longer advertises an unimplemented `--resume` or retired
`A15.3.shared` acceptance. Continue a partial run through explicit source/current
input validation and actual supported stage/format methods; no new scheduler or
automatic cleanup. State the actual format-specific coverage, including absent
PDF inspection and Visio writer limits.

Narrow current provenance paths and unsupported benefit statements to facts.
A dated factual clarification of ADR-0017's comparative claim may correct the
evidence description without changing its chosen design direction or licenses;
no broader architecture decision is authorized. Retain all required notices.

BUILD owns one documentation-fidelity reference combining source inventory,
claim-to-source coverage, accepted-doc intent, removed-option migration,
frozen paths, changed-source refresh and unrun examples. SHIP, DocWriter and
generate-docs consume it without a circular delegation or new schema/role.
Preserve all useful docs targets and canonical role names.

**Verification:** run real read-only checker fixtures, missing/aliased notes
and retention negatives, shared-emitter preservation/refusal tests, existing
review/format/caller contracts and source-notice checks. Preserve preceding
package fixes and document every intentional overlapping file. Report exact
resource closures for central generation; independent review remains separate.

- [x] lane-B-04 Consolidate metadata-first discovery without invented routing success.
- [x] lane-B-05 Give role lifecycle one method owner while preserving existing entrypoints.
- [x] lane-B-07 Provide a concrete bounded single-hop transport for the existing URL policy.
- [x] C-04 Replace maintenance's duplicate or unsupported methods with actual owner routes.
- [x] C-06 Centralize profile/audit/doctor procedures without changing mutation authority.

**Discovery/lifecycle owner:** one sequential delegate; canonical discovery,
role/pack/audit/doctor/maintenance methods and direct references, the existing
`lib/url_policy.py` callback seam and a minimal standard-library transport,
plus focused existing/new tests. No public removal, new policy engine, host
setting, pack schema or native adapter change.

**Acceptance:** catalog owns metadata-based intent narrowing; retained routing
front doors delegate rather than claim measured success or another LLM
escalation. SENSE's real high-risk routing and native host authority remain.
Role create/update/list/activate methods share one reference, preserve explicit
private-role consent and failure-safe state, and keep every old flag/caller.
Profile CRUD, hook observations and installed checks use their existing actual
helpers; read-only and mutating cases stay distinguishable. Source-only
uniformity checks cannot pretend a consumer bundle contains contributor tests.

URL retrieval keeps `fetch_checked` and its response/allowlist contract.
A shipped transport exposes exactly one HTTP response, never follows redirects
automatically, caps reads before accumulation and uses a finite timeout.
`fetch_checked` validates every Location before another request. No credentials,
cookies, authentication bypass, certificate relaxation, automatic installation,
unapproved destination or prior-host-denial fallback is added.
Expose it through the existing URL method with explicit allowlist/operation
authorization. Test real transport behavior through an owned in-process
HTTP/response fixture or injected transport; no external network is required.
Preserve existing validation-only CLI behavior if adding an explicit fetch mode.

**Verification:** existing lifecycle/discovery/audit semantics plus wrong/missing
authority, unsupported helper, redirect-loop/disallowed-host/downgrade, response
size and timeout negatives. No real personal profile or private-role scan, no
remote request, no global state or activation. Keep source bytes from prior
packages outside exact documented overlaps.

- [x] lane-E-01 Configure the native reviewer profile's least-privilege tool declaration.
- [x] lane-E-01b Emit role-specific planner/builder/reviewer report contracts.
- [x] lane-E-02 Share distributed-boundary reasoning without duplicate default dispatch.
- [x] lane-E-03 Share data-design methods while preserving the migration planner/executor split.
- [x] lane-E-05 Turn redundant role procedures into compatible views of their existing owners.
- [x] lane-E-06 Extract the existing bisect and migration eligibility recipes into trusted helpers.
- [x] lane-E-10 Distinguish client/provenance metadata from observed support and license evidence.
- [x] lane-E-12 Share performance-evidence reasoning and avoid repeated profiling for report views.
- [x] F-06 Preserve actual host/attribution facts without documentary-as-runtime claims.
- [x] F-01 Replace arbitrary role-count floors with meaningful inventory/consumer parity.

**Role/runtime owner:** one sequential delegate. Scope includes relevant named
canonical roles and method references, the two extracted helpers and consumers,
native role-profile rendering in `bin/li-copilot.py`, exact related adapter docs
and focused tests. No central resource tuple/generator run, public name removal,
default-portfolio change, tool expansion or held ADR-drafting work.

**Acceptance:** the Copilot `lintel-reviewer` profile declares read/search tools,
not unrestricted edit/shell access. Reports return to the authorized coordinator;
unavailable prepared context or recording support stays explicit. Canonical
agent tool lists and planner/builder needs remain intact. Test the emitted
configuration and role-specific reports; separately identify live host
enforcement as unobserved unless genuinely exercised by an allowed operation.

Use existing architecture/data/performance owners as shared procedures, retain
legacy role names as compatible entrypoints and avoid spawning both aliases
for one outcome. Preserve all distinctive constraints, exact task/evidence
identity, and MigrationPlanner/Migrator's separate authority. ADRDrafter and
the held ADR helper are not changed.

Move the two tested shell recipes out of Markdown to explicitly trusted
standalone helpers with the same literal inputs, exit/error handling, trial
isolation and recovery predicates. Callers/tests consume the helpers, not a
second copied recipe. No real source checkout is bisected or restored.

Client hints are not host observations. Verify which historical metadata
complaints were already fixed; preserve native memory/model hints as such and
do not invent an upstream URL, verification date or license clearance.
Record the known derivative's already-retained attribution and clarify legacy
tier meaning centrally. Inventory tests require unique valid roles, referenced
members and native/catalog parity instead of a minimum of sixty or a fixed
neutral-domain count. Current names and capabilities remain.

**Verification:** generator source/config fixtures, actual extracted-helper
tests in newly owned synthetic Git repositories, migration eligibility
negatives, role/method preservation and relevant inventory/caller tests.
Normal local commits inside explicitly created synthetic test repositories are
allowed; source commits and changes to this worktree's hook configuration are
not. Targeted cleanup of a test-owned temporary child is allowed; no repository,
session, worktree or broad root deletion. No external network or model call.

- [x] lane-A-05 Preserve selected external analysis, convergence and bug/assessment authority.
- [x] G-01 Detect actual selected Spec Kit capability overlap without requiring extensions.
- [x] G-11 Correct current-facing upstream descriptions while retaining dated import/review pins.
- [x] ENT-02 Define concrete control ownership, negative checks and failure behavior without claiming enforcement.
- [x] ENT-03 Demonstrate that a loaded/pinned child pack cannot clear an omitted required control.

**External authority owner:** one sequential delegate. Scope is the Spec Kit
bridge and its direct ANALYZE/DEFINE/DIAGNOSE/FIX/REVIEW references, existing
work/evidence integration seams and focused tests, enterprise control guidance,
and exact current-facing upstream source descriptions. No competing task list,
new work-map schema, package installation, policy service or live control change.

**Acceptance:** selected `tasks.md`, including convergence-added task IDs,
remains the only task authority. Explicitly selected original analysis,
convergence, bug and assessment artifacts are bound through existing input/
acceptance selection, not recreated as Lintel records. Detect commands/workflow
gates/hooks only from actual supplied or inspected registration/configuration;
unsupported/unknown versions remain unknown. No Spec Kit extension is required,
installed, executed or assumed. Conflicting ownership is surfaced before a
dependent action, and an external assessment never grants publication authority.

Preserve the old method/import pins and dates. Add only source-grounded dated
comparison pointers and correct current-facing descriptions/URLs from retained
evidence; no fresh upstream review, imported revision or outcome superiority is
claimed. Native planning overlap does not remove existing evidence guarantees.

Enterprise guidance distinguishes model instruction, invoked helper validation
and actual host/CI enforcement. For each selected required control, identify its
responsible owner, actual mechanism, negative test, evidence and failure action.
No defaults pretending every organization configured those controls.
An actual synthetic parent/child whole-block replacement test must retain the
accepted resolver semantics, show the missing inherited control, and prove that
the existing immutable P05 requirement still blocks clearance. Loading, pinning
or selecting the pack is not source approval or a passed control.

**Verification:** real map/evidence/profile helpers over explicit synthetic
artifacts, task-ID/current-byte preservation and missing-control negatives.
Normal test-only Git/profile fixtures and targeted child cleanup are allowed;
no source commits, target-profile rebind, external network or policy change.
Keep earlier packages intact and report new resource dependencies centrally.

- [x] lane-A-06 Move optional delivery/capture and maintainer procedures behind their actual conditions.
- [x] lane-d-02 Remove false Visio completion/library promises while retaining the explicit unavailable-writer boundary.
- [x] ENT-05 Keep current working memory concise and historical detail cold without inventing learning efficacy.

**Core-boundary owner:** one sequential delegate. Scope is CYCLE/CAPTURE/SHIP
and new direct method references, the retained Visio compatibility entry and
its source tests, mutable memory/index and a byte-preserving history archive.
The earlier F-01 task additionally covers conditional customer routing and
removal of the hard-coded follow-up cadence, not default portfolio removal.

**Acceptance:** optional customer delivery/review/follow-up runs only for the
actual requested outcome, selected applicable profile and available authorized
capability. Use existing source selections as discovery, never as permission;
derive timing from the agreed plan rather than inventing immediate/48-hour/
weekly commitments. Core SHIP retains all required review, QA and publication
checks. Maintainer M1-M4 and optional CAPTURE report/vault procedures have one
linked owner and run only at their existing conditions; preserve complete
procedures and data/consent boundaries when moving text to references.

Visio remains explicitly without a bundled writer. Remove automatic library
suggestions/install implications, personal-home template defaults and
image-as-editable-format success. No output is DONE merely because a QA handoff
was made. Actual requested format, writer, editable reopen, connector/label and
required inspection evidence are necessary; absent tools keep that output
blocked. Tests must guard this truthful boundary, not insist the workflow stay
empty. Do not add a renderer/dependency or retire the public name.

Archive the previous committed-style working-state detail byte-for-byte at an
explicit internal history path; keep a short accurate current state with links.
Do not copy private runtime/session history. Reconcile stale hot-index claims
against existing delivery records, retaining uncertainty rather than declaring
unrelated programmes complete. This improves retrieval, not measured compounding.
Do not modify the protected shared todo or old review records.

**Verification:** original procedure/field preservation, false-DONE/no-writer
and cadence negatives, current caller/source tests and memory/history equality/
link checks. No live delivery, external export, user-home scan, unsupported
model benchmark, generated reducer or policy/architecture change.

Keep original finding IDs when detailing the next ready package. Read its full
claim and relevant current code before editing. Reconcile partial prior fixes;
do not label an entire finding fixed because one sentence or one branch changed.
Task counts and package coverage are checked against the complete original
inventory, not this first-leaf excerpt.

## Integration and review

- [ ] V2-INTEGRATION Verify the joined original-clause result, generated resources and actual delivery without closing unresolved original findings.

The completed source delivery changed 0.13.7 to 0.13.8. Its explicitly reasoned
target-local profile rebind preserves generation 1 as history and selects
generation 2 for that acceptance; the neutral pack and required policy do
not change. Old implementation observations are not rewritten as new-version
checks. Required aggregate QA includes affected local tests, generated/installed
consumer checks and complete hosted verification of the exact candidate.

Integrated review reopened the original **lane-B-02** prior-delivery residual
(`INT-SPEC-01`). Its correction is an integration obligation, not a new task ID
or replacement inventory: preserve the 55 mapped leaves and all 84 original IDs.
Repository job mutations must leave an unselected global registry/personal
profile untouched; an explicitly selected, authorized registry retains the
ADR-0005 pointer pattern, other scopes and legacy records. `list` remains
non-mutating, and whole replan preserves original map/IDs and provenance.
The owning changes are `bin/_jobs.sh`, `skills/jobs/SKILL.md`, the jobs-system
reference and the existing continuity regression suite. Verify preservation
after each mutation (not only after archive can restore a registry's bytes),
explicit selected synchronization and read-only listing. The same integrated
reviewer must reconcile this original claim before QUALITY and delivery.

Coordinator owns generated resources, final inventory/closure, version metadata,
ordinary commits, integration and delivery. Use existing generators and targeted
tests, then the required complete joined verification. New selected-input changes
invalidate affected evidence. A reviewer must not repair its own findings.

Do not edit the byte-bound shared `todo.md` or any earlier acceptance tree.
Link current progress from mutable working memory. No deletion of files or
worktrees is part of proving finding closure.

## Original method proposals continuation

- [ ] lane-A-07 Carry a material riskiest assumption and its falsifying observation into the native spec template.

**Authority and design:** the original A-07/B-09/B-11 claims and the existing
SOURCE, TRUTH, METHOD and ACCEPTANCE requirements. These are missing compatible
implementation clauses, not a new initiative or governance change. ADR-0026's
short leaves, ADR-0039's complete native artifacts and the shared profile/work/
review controls remain. No phase, public entrypoint, role, helper API or required
control is removed. There is no new runtime engine, schema or model benchmark.

**Owner and order:** the coordinator implements P10 sequentially, then P9's
generated/verified aggregate. The three original finding IDs remain the leaves;
the bounded edits below are their implementation steps, not a second task ledger.
The existing original-finding granularity concern remains explicit, without a
fabricated implementation-time claim. No swarm fields or new actors are selected.

**A-07 files and acceptance:** `scaffolding/01-foundation/templates/plan/spec.template.md`
and its existing planning/installed-template tests. Retain the six-column
requirements table, DRAFT-first status, original acceptance links and PLAN's
finalization ownership. Add one conditional riskiest-assumption row carrying
the existing premise/decision link, invalidating observation, evidence state and
original requirement/task link. If no material premise exists, state a reasoned
N/A rather than inventing an assumption, adding a question or re-interviewing
approved work. Missing evidence stays planned/unverified. Use an actual rendered
template fixture with a carried premise and with no material premise; neither is
model-efficacy evidence.

**B-09 files and acceptance:** `skills/resume/SKILL.md` and the new
`skills/resume/references/state-and-job-recovery.md`, with directly affected
continuity, coordination, enterprise-snippet and shape checks. Move the complete
swarm-aware resume, selected-ledger integrity and tree/job resume procedures into
the one reference. Keep the public headings, one map-first decision table, all
inputs/modes, checkpoint ownership, baseline selection, required preconditions,
seven-day warning and conditional questions in the main method. Each affected
step must require reading its exact reference section before proceeding.
Preserve actual Bash recipes and all branch/commit/age/blocked-leaf/flat-fallback
behavior; adapt tests to execute the real new owner, not a copied implementation.

**B-11 files and acceptance:** `skills/swarm/SKILL.md` and its existing
`references/evidence.md`. Move the complete shared-evidence consumer under the
already named contract table; leave run/verify and essential failure/permission
boundaries in the main method with an explicit required reference read. Remove
the obsolete back-link claiming the procedure lives in the main body. Replace
deictic references such as "arguments above" with the existing exact profile
arguments or an explicit caller link. Keep every work/profile/review/QA/domain
rule, version, later-rejection behavior and independence obligation. No helper
semantics change. Check the complete preserved procedure, not just its title.

**Coupled distribution and continuity:** include the new recovery reference in
the existing core capability closure and direct native-resource inventory where
needed. Regenerate wrappers rather than making pointer-only adapters or applying
a supposed hard 20 KB limit. Existing native bodies remain complete translations
of their canonical bodies, and required references must be available in installed
bundles. The observed stale "uncommitted 0.13.8" hot-index claim is removed in favor
of the existing working-state owner, avoiding two volatile delivery summaries.
Keep the protected shared todo and exact cold archive untouched.

**Verification:** start with discriminating new template/reference tests that
fail on the baseline. Run the affected existing planning, coordination and
continuity tests, actual enterprise workflow snippets and Swarm shape checks.
Use complete synthetic homes/temp/data/config roots; never run an updater or
mutate a personal profile. Preserve recipe/procedure preimages and compare them
to the new owners, allowing only documented heading/link-context changes.
Exercise the installed Copilot kit/resource closure and canonical/native/catalog/
wiki checks. Changing selections/resources requires both integration consumers,
`copilot-kit` and `catalog-installed`; do not repeat the earlier missed consumer.
Full current-head CI and independent source acceptance precede main delivery.

**P9 continuation:** the next source version is 0.13.9, with all existing version
manifests kept in sync. The new owned target has its own verified profile context;
it does not borrow the old target's reference. Rebind only if the declared source
version changes, with an explicit reason, retaining the old generation. Renew
current acceptance/QA as needed; never edit old 0.13.8 records. Update the original
84-clause dispositions only after actual independent source review. No forecast
of three closures is a result. Preserve all remaining architectural, empirical
and exact host-held work.

**Plan signals:** four currently open original tasks (P10's three source leaves
and the reopened integration task), PLAN -> BUILD -> REVIEW -> VERIFY -> SHIP ->
CAPTURE, one writer and one bounded independent reviewer. No rendered UI is
changed. The actual bound helper reports **12,000 tokens, uncalibrated, zero
samples**, once for this S-sized continuation; this is not measured usage or a
budget guarantee. No dollar, time or calibrated-benefit claim is supplied.
Independent plan review remains a separate mandatory entry gate before BUILD.

**Profile impact:** this new owned target has an independently bootstrapped and
verified `_default` 1.0.0 context. Actual required-policy is
`not_required / bundled-neutral / 1.0.0 / not_applicable`; no enterprise control,
private pack or old-target profile reference is imported. This produces no
additional product behavior. Profile presence is neither approval nor evidence
that a host hook fired.

The coordinating planner's non-clearing engineering/devex inspection and
standalone consistency analysis are retained at
`.claude/runtime/v2-method-proposals/plan-inspection.md` and
`.claude/runtime/v2-method-proposals/plan-analyze.md`. BUILD has not started;
proposed runtime tests are not observations. Those advisory reports do not
replace the actual independent staged plan decision.

## Verified delivery 2026-10-04

The compatible source batch was delivered by an authorized ordinary fast-forward
from `f9796bb8b3fbcdab3e235f30401933ea1b2f3162` to
`b2516af57244017160c499558f183f95e7a9fe5c`. GitHub main and the remote plugin
manifest were read back at **2026-10-04T08:17:28Z**, confirming **0.13.8**.
This records that source delivery, not a tag, deployment or whole-programme finish.

The source includes non-mutating artifact QA, explicit output ownership, actual
contrast and bounded PPTX checks, bounded URL transport, shared skill/role
methods and their consumers, source-owned bisect/migration helpers, explicit
global-registry selection, updater-root protection and regenerated native assets.
The 54 P1-P8 clauses plus the reopened jobs residual were reviewed in the full
integration; P9 records the verified source delivery rather than another finding.

### Review and verification

Independent source SPEC and QUALITY passed at tree
`ec32727a6c9be75b6d6080fe5e05c9b333fc85c2`, the exact b251 committed tree.
When the original ephemeral reviewer became unavailable, an existing independent
reviewer assessed current evidence applicability and authored the final eight
decisions. The earlier source judgments retain their actual author; the final
reviewer did not claim to repeat them. The author confirmed byte-exact copies,
actual native request/result events corroborated the invocation, and all eight
once-writer/latest-reader/QA-SHIP gates passed before the main update.

[Exact-source CI run 37181136525](https://github.com/jokerman89/lintel/actions/runs/37181136525)
passed **23 jobs, 27 strict invocations and 600 script executions**: 200 per OS,
with no required failures, skips or partial executions. This includes actual
Python 3.12 PPTX and the fixed-parent migration fixture. Platform N/A counts were
23 on Ubuntu, 23 on macOS and zero on Windows; they are not skipped scripts.
The selected local total is **136 retained cases plus 17 fresh source-bound
PPTX cases = 153**, not 170. The earlier unbound PPTX receipt remains history.
Four committed native/catalog/wiki/whitespace checks also passed.

Raw M2 remains **RED, 94 occurrences**, with explicit narrowly scoped acceptance
for the reviewed source and production guards. It was not retyped GREEN.
The final review's factual wording errata are retained alongside the original
report. Its evidence-array clarity recommendation does not affect the shared
consumer, which reads counts from the observation, not by summing evidence files.
No live rendering, every-client enforcement, legal currency or model efficacy is
inferred. The failed first CI and test-isolation incidents remain recorded;
unobserved personal/client state is not described as restored.

Private proof is retained under the coordinating session's owned runtime and
backups, not published as raw session history. Stable content references are:

| Evidence | SHA-256 |
|---|---|
| Hosted verified summary | `9085710c43e8d1e599f0f0d75bd6bb46399f230cba08247c23b3feaf1b74f97c` |
| Final reviewer manifest | `6cc92f1c1bdc168aa94450a738eba60beaac3a7c4eff38b6b214420e4b2f0774` |
| Author's faithful-copy confirmation | `5f604be50635aae94af3fb862de3200a22dd4799f8799c00f5a7c0e26849cb5c` |
| Native host observations | `036cb2f177965cf29e08bc8e1f4fe16a78627e68a8080fd32b0054d9978915de` |
| Actual source QA/SHIP receipt | `919047657d6ca152ab8869f2a636f4a31686eff4486fc2c12281ba5ecd0edb60` |
| Original-finding dispositions | `9daa8dfd3225c441ca5fb0dab89e7387c5c50d330641a179b5d2380d249eff66` |

### Original work still open

The independent disposition inventory still has **84 original findings**:
**36 source-complete/retained-guidance and 48 with explicit remaining clauses**.
The checked package clauses above do not replace that inventory. In particular,
not all remaining items are host blockers: some are unimplemented method/template
proposals; others require public-surface/architecture decisions, primary-source
verification, live-client evidence or separately authorized outcome experiments.

Keep the exact native-hook and ADR-drafting holds untouched. No retirement,
pack extraction, replacement of accepted planning rules or new benchmark is
authorized by this capture. The work map and specification remain APPROVED for
their stated compatible scope, not COMPLETE for the original programme.
Resume from the original unclosed clauses and their full evidence, not by
re-executing the delivered packages or reconstructing private inputs from this
summary. The private Impact report remains a separate completed private deliverable.
