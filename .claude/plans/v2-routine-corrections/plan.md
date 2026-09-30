# V2 routine correction plan

Status: APPROVED within the eleven original scopes and the separately released
original DEFINE item 6 on 2026-09-30.
Base: `dcccf5f20a24f883d9e65e6c072a8ee11dd75083`.
One isolated writer; no new reviewer/agent dispatch. Parent findings stay open
outside their named subordinate scope.

## Packages

| Package ID | Outcome | Leaf IDs | Owner / edit boundary | Dependencies | Review |
|---|---|---|---|---|---|
| VAULT | Optional dependency correctness | lane-A-06.vault | routine owner; skills/capture/SKILL.md, tests/unit/continuity-consolidation.py, tests/unit/universal-trusted-tools.py | none | substantive |
| STATUS | Accurate observation authority | lane-B-02.status | routine owner; skills/status/SKILL.md, skills/jobs/SKILL.md, docs/concepts/jobs-system.md, tests/unit/continuity-consolidation.py, tests/unit/catalog-metadata.py | none | substantive |
| CONTINUITY | Existing recovery contracts agree | lane-B-09.continuity | routine owner; skills/pause/SKILL.md, skills/resume/SKILL.md, tests/unit/continuity-consolidation.py | none | substantive |
| ROLES | Available role and independence handling | lane-E-07.roles | routine owner; skills/cycle/SKILL.md, skills/discover/SKILL.md, skills/review/SKILL.md, tests/unit/planning-consolidation.py, tests/unit/quality-consolidation.py, tests/unit/native-command-surface.py | none | substantive |
| COMPLIANCE | Truthful discovery metadata | C-10.compliance | routine owner; skills/compliance-gate/SKILL.md, tests/unit/quality-consolidation.py, tests/unit/catalog-metadata.py | none | substantive |
| PERF | Sample-aware report | C-10.perfbench | routine owner; skills/perfbench/SKILL.md, tests/unit/native-route-consolidation.py | none | substantive |
| OBSERVATION | Actual reader routes | lane-B-10.observation | routine owner; skills/maintenance/SKILL.md, skills/usage-log/SKILL.md, skills/hooks-status/SKILL.md, tests/unit/observation-spine-skills-present.sh, tests/shape/observation-consumer-wording.sh, tests/integration/observation-learning.py | none | substantive |
| FRONTEND | Retained control/path contracts | lane-d-04.frontend | routine owner; skills/frontend-motion/SKILL.md, skills/frontend-typography/SKILL.md, skills/frontend-shader/SKILL.md, skills/frontend-design/SKILL.md, tests/unit/frontend-skills-present.sh, tests/integration/pattern-workflows.py | none | substantive |
| REPORTS | Method-consistent artifacts | lane-E-08.reports | routine owner; agents/engineering/Architect.md, agents/engineering/CapacityPlanner.md, agents/engineering/ObservabilityArchitect.md, agents/engineering/SystemArchitect.md, agents/engineering/DataPipelineDesigner.md, tests/behavior/agent_contract_scenarios.py | none | substantive |
| RESEARCH | Honest external handoff | lane-E-09.research | routine owner; agents/engineering/ResearchSynthesizer.md, tests/behavior/agent_contract_scenarios.py, tests/unit/native-command-surface.py | none | substantive |
| DEPENDENCY | Evidence-based consequence | F-03.dependencies | routine owner; skills/review/SKILL.md, agents/security/DependencyAuditor.md, agents/security/SBOMAuditor.md, agents/security/OAuthFlowReviewer.md, tests/unit/adaptive_review.py, tests/unit/review_method.py, tests/behavior/agent_contract_scenarios.py | ROLES | substantive |
| DEFINE-006 | Pivotal premise output | item-006.define-premises | routine owner; skills/define/SKILL.md, tests/unit/planning-consolidation.py | none | substantive |

Shared test files have one writer. Discovery-string expectations may use the two
narrow allowances in spec.md; no reducer or reserved header-test changes.

## Original-ID tasks

### lane-A-06.vault
- [ ] Verify and correct only optional-vault fresh-shell roots/writer dependency.
Dependencies: none
Acceptance: spec.md vault row. Verify actual recipe with enabled relative, disabled
and missing-path synthetic cases; preserve files outside the selected sink.

### lane-B-02.status
- [ ] Align metadata and job documentation with the actual read/mutation scopes.
Dependencies: none
Acceptance: spec.md status row. Verify mapped-only work, no job registry and emitted
descriptions without creating or reconciling state.

### lane-B-09.continuity
- [ ] Resolve watcher/age/ledger contradictions while retaining data formats.
Dependencies: none
Acceptance: spec.md continuity row (also lane-B-08). Verify actual recovery
selection/refusal cases and bounded source contracts.

### lane-E-07.roles
- [ ] Correct previews, stale totals and named-role versus independence fallback.
Dependencies: none
Acceptance: spec.md role row (also lane-A-06). Exercise empty/available binding and
missing independent-evidence cases; no actor launch.

### C-10.compliance
- [ ] Make discovery describe the current per-control model.
Dependencies: none
Acceptance: spec.md compliance row. Verify rendered metadata and existing
mandatory/advisory/unknown outcome cases.

### C-10.perfbench
- [ ] Keep empirical values distinct from population guarantees in output.
Dependencies: none
Acceptance: spec.md performance row. Instantiate a five-sample report retaining
failures and uncertainty without inventing a statistical floor.

### lane-B-10.observation
- [ ] Repair only stale cross-routes and retain manual observation semantics.
Dependencies: none
Acceptance: spec.md observation row (also C-04). Exercise existing reader fixtures;
do not equate missing records or CLI flags with nonexistent manual capability.

### lane-d-04.frontend
- [ ] Align declared controls and owned-path language in retained frontend methods.
Dependencies: none
Acceptance: spec.md frontend row (also lane-d-05). Exercise existing pattern/workflow
fixtures and unavailable-control cases; no publication or provider activation.

### lane-E-08.reports
- [ ] Make actual report templates express the methods' existing invariants.
Dependencies: none
Acceptance: spec.md report row (also lane-E-11). Render discriminating role-output
fixtures, not only a keyword-presence list.

### lane-E-09.research
- [ ] Replace the unowned external flag with the actual caller capability boundary.
Dependencies: none
Acceptance: spec.md research row. Verify unsupported and supplied-source handoffs
without expanding the role's tools.

### F-03.dependencies
- [ ] Preserve applicability, evidence and mandatory policy in dependency handoffs.
Dependencies: lane-E-07.roles
Acceptance: spec.md dependency row. Exercise existing method/control fixtures;
preserve reserved header classes and distinct specialist roles.

### item-006.define-premises
- [ ] Persist the released conditional premise/falsifier/check/consequence row inside the selected design.
Dependencies: none
Original item: `all-items.json` index 6, `skills/define/SKILL.md`.
Execution order: started only after F1/F2 corrections and their affected checks passed.
Acceptance: spec.md DEFINE row. Render source-linked positive and missing-falsifier/
unchecked-premise cases; retain source-contract zero-question approved T014 and
compatibility-only migration checks. Shared intake and SCOPE are unchanged.

## Verification and review

Use the smallest affected selectors, combining shared suites once. Record actual
RED/GREEN commands, exits and log hashes in own runtime evidence. All original
checkboxes remain open until the separately assigned reviewer completes acceptance.
Generated reducers/version/joined CI belong to Master. A blocked leaf does not
stop independent ready packages.

Own target-local profile and exact required-policy bridge are verified before
dependent work; no borrowed reference or global activation.

Implementation: the original eleven scopes and the separately released original
DEFINE item are implemented. The first independent SPEC review was blocked by
F1/F2; QUALITY was not performed. Repairs await that same SPEC recheck and first
QUALITY stage. Original checkboxes remain open, not inferred from test exit codes.

## Implementer evidence

The final scoped batch is retained in own runtime
`routine-tests/logs/final-scoped-batch.json`, with exact argv, timestamps, exits,
log hashes and matching before/after source/index identity.
This is the preserved initial-candidate batch, not post-repair acceptance.

| Package | Evidence in that batch |
|---|---|
| VAULT | `continuity`: real selected-profile fresh-shell relative, disabled and missing destination cases, including an actual advisory audit record |
| STATUS | `metadata`: actual catalog/native description rendering; `continuity`: mapped work without job registry or mutation |
| CONTINUITY | `continuity`: existing checkpoint behavior, seven-day wording and actual age-only versus branch-drift recipe behavior |
| ROLES | `routes`: instantiated dry-run with unselected/declared bindings; `quality` source boundary; `independence` actual stale/missing evidence refusal |
| COMPLIANCE | `metadata` and `controls`: actual rendered discovery and mandatory/advisory/grounded-N/A/unverified outcomes |
| PERF | `routes`: actual report template instantiated with five synthetic samples, empirical tail uncertainty and retained failures; no benchmark was run |
| OBSERVATION | `observation`: actual reader rows/manual totals/missing-file result; two observation guards |
| FRONTEND | `quality`, `controls`, `patterns`, `frontend-shape`: declared interfaces, selected assets, unmet required control despite pattern pass, existing consumer/mandatory-clause behavior |
| REPORTS | `roles`: instantiated actual Markdown/YAML example mappings for alternatives, capacity, SLI, system and pipeline invariants |
| RESEARCH | `roles`: unavailable versus caller-supplied external evidence in the retained report template |
| DEPENDENCY | `controls`: raw rank cannot override applicability or mandatory outcome; specialist-source boundaries retained |

Final observation: 33 unittest methods and three scoped shell guard files passed;
all twelve commands returned zero with no outer fail/skip markers. Shell printed
PASS counts remain distinct from method or total assertion counts. No full suite,
model, live-client, scanner, benchmark or network observation is claimed.

RED logs and intermediate failures remain intact. Test-only corrections addressed
an omitted import, the existing mapping parser's single-item-list example boundary,
the actual control status vocabulary and owned Windows fixture cleanup. An age-only
confirmation contradiction was found by executing the original resume recipe and
corrected without relaxing branch/content/profile checks. No prior failed root,
shared temporary output or mounted parent directory was cleaned.

Own profile context `v2-routine-corrections`, generation 1, `_default` 1.0.0,
digest `sha256:499138ecd6fde1133ed673f13653b88e9334c0431d6c751d78ce0363ff912c95`.
Actual required policy is `required: false`, `status: not_required`,
`source: bundled-neutral`, `version: 1.0.0`, `applicability: not_applicable`.
This is a target-local reference, not another owner's permission or acceptance.

The initial candidate retained role declarations. The later repair clarifies only
ResearchSynthesizer's description; names, tools and optional model/memory remain.
The reserved header fixtures, held scopes, schemas, protocols,
versions and reducers remain unchanged. CAPTURE edits are confined to Step 7b.
Generator-description overrides were unnecessary: an actual owned-fixture render
already consumes the corrected canonical descriptions. Generated native/catalog/wiki
outputs are intentionally not updated in this tree; Master owns final regeneration
and integration. This handoff is source/fixture evidence, not P05/SHIP clearance.

## Source review repairs and explicit DEFINE addition

The original review and failed candidate remain unchanged in private evidence.
F1's existing cohort-5 guard was run read-only and failed before restoring the
active pack's `compliance.hooks` source in the body; the truthful description and
old guard remain. F2's exact prose trend-consumer claim was removed, and the
negative fixture now catches both the prose and flag forms.

Selected provisional notes were addressed without expanding assurance:
- The performance report retains raw sample/reference and estimator fields; regression
  rows refer to the selected result scenarios rather than unrelated fixed examples.
- The cross-repository job registry is described as still synchronized but
  supplementary/non-authoritative. The job-list bullet matches the real read-only reader.
- Supplied web material remains a legitimate research input. Discovery now distinguishes
  it from new authorized retrieval; tools were not expanded.
- SLI tests now inspect the actual template and reject omitted fields/healthy no-data
  mutations. Local arithmetic was not evidence of a shipped SLI calculator.
- F-03 report fixtures carry contrary exposure/applicability, source-only inventory
  mismatch and missing token/provider evidence; missing coverage fields are rejected.
- Vault warnings consistently use stderr; missing/disabled cases remain nonblocking
  with the original scoped audit behavior.

`repair1-scoped-batch.json` records the repaired checks: the old guard and 19 scoped
methods passed with unchanged source during the run. The separately released
`item-006.define-premises` was implemented only afterwards. Its source/report
fixtures passed (including missing-falsifier/unchecked-premise mutations), together
with existing intake, approved-work and Spec Kit authority checks. No source test
claims a live model interview, a performed experiment or human-grant authentication.

The DEFINE clause writes only a conditional table within the selected design;
settled facts/approved T014 require no extra question or proof exercise. Missing
compatibility facts do not select strategy. Shared intake, SCOPE, schemas and
policy floors remain unchanged.
