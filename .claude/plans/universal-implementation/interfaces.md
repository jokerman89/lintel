# Shared implementation interfaces

Coordinator-owned agreements for dependent packages. These signatures are proposals
accepted for implementation; code and contract tests at exact package revisions establish
their final availability. No second task/status ledger is introduced here.

## Shared Markdown source boundaries

Approved contract/ownership: `packages/P05-P06-markdown-boundary.md` at `7a892b4`.
Current provider checkpoint: `74259605c1a172a444d1d4d2e838aea2b120ef92`, owned by P06.
The earlier `09148b7` is rejected history: it falsely identified an ordered-2 paragraph
continuation as an item and lost multiline inline-code precedence.
`lib/markdown_source.py` implements the exact immutable types and stateless
`classify_markdown(str)` API. Independent complete provider/adapter spec and first
whole bounded quality passed in `1067da29`; integrated as `36593cd`. P05 and final
joined consumers remain separate gates.

P05 is authorized to import only the exact helper bytes as an explicitly attributed
dependency-only commit, not to edit or fork the helper. It then owns its selected-leaf,
single ASCII progress-character/excerpt consumer and actual clearance regressions.
Classify full supplied text; use original Unicode codepoint spans. A prose item describes
its start context, not permission over later literal spans. The actual checkbox location
must be eligible; quote/literal/opaque/unknown content remains identity-bearing.

No shared semantic task schema, normalization, I/O, policy or clearance belongs in this
provider. Missing installed helper must fail before writes, not fall back to a second
parser or a target-supplied module. Both independent consumer gates and final fan-in remain.

Exact 742 provider: Git blob `0b3da55046358864fcd3075ba5bfb6c2348b1fec`, 19,988 bytes,
SHA-256 `331c1c62e932b5555089336d1fdcc7031f545780508f1d0f2e11bd9f2a7a8ebf`.
P05 dependency-only import is `bd96a477`; its owned consumer `fd63e690` and report-only
snapshot `9c8ef727` were rejected by independent `0cdbf596` for Q01 excerpt-context
identity. All 81 actual evidence methods passed on that paired source; those fixtures
did not cover the new transition. P05 now owns the approved selection-relative context
binding repair in the shared-boundary card. No provider/API change is authorized.
The accepted consumer is `b023e8c` with report-only snapshot `ec90b609`, independently
approved by `33eac071` and integrated as `c5c8f86`. Its mapped-task excerpt digest uses domain-separated
canonical JSON of normalized text, sorted eligible codepoint spans relative to the
selection, and exclusive end-marker eligibility (pair or null). Old byte-only
mapped-excerpt receipts remain history, not clearance; fresh preparation/review/QA
is required. Other hash domains and public field/version shapes are unchanged.
Read the exact accepted evidence reference before implementing dependent consumers.
Downstream readers must use the shared implementation, not accept both hash domains
or invent an automatic receipt upgrade. Final integrated/client acceptance remains separate.

## P05 review and controls

**Coordinated format revision:** the affected bound review/context/QA contract moves
to v2 for required immutable `qa_requirements`. Profile references remain v1; work-map,
host registry and Swarming versions are independent. Do not silently reinterpret durable
v1 records or auto-upgrade them to clearance. Preserve history and reprepare/review.
An older obsolete/invalid record may be superseded by a newer valid applicable bound
decision; a later malformed/rejecting relevant or uncorrelatable decision still revokes.

Each QA requirement binds id, kind, requirement, applicability and policy using the
shared control definitions. IDs are unique and mandatory QA IDs belong to required
controls; typed review and QA declarations cannot contradict the approved inventory.
QA observations cannot omit, retype, downgrade or reclassify an obligation. Genuine
docs-only scopes declare their actual documentation checks and grounded test N/A, not
a fictitious universal test requirement.

Accepted producer seam: prepare's input retains its old fields plus `qa_requirements`
(no input version flag). It emits context version 2; the decision and QA receipt also
use version 2. A mandatory QA ID such as `tests` must appear in `required_controls`,
the review's typed controls, and each selected leaf's coverage. The typed obligation
is not reconstructed from observed results. Profile references, work maps, corroboration
and the standalone control-outcome envelope retain version 1.

`CONTRACT_VERSION=2` is scoped to the bound review/context/QA contract.
`validate_decision(record, history=...)` preserves strict historical-v1 inspection, not
clearance. `select_latest` keeps its existing keyword arguments and accepts decoded
mappings or ordered `ContractError` candidates; an invalid latest applicable candidate
cannot be discarded into an older PASS. The frozen source-owned example is
`skills/review/references/evidence.md` at P05's accepted `b023e8c` / `ec90b609` checkpoint.

`lib/review_contract.py` (stdlib): `ContractError`, `load_json(text)`,
`validate_control(control)`, `evaluate_controls(controls, required_policy=...)`,
`snapshot(repo, base=..., selection=..., record_path=...)`,
`bind_work(repo, work_map=..., package_id=..., leaf_ids=..., acceptance_paths=...)`,
`validate_review(record)`,
`select_latest(records, skill=..., work_map=..., package_id=...)`,
`verify_review(repo, record, expected=..., corroboration=...)`.

CLI: snapshot, controls, prepare, validate, verify, ship. Existing shell writer/reader
names remain. Exact status parsing, selection identity and later-negative revocation are
mandatory. Host/human corroboration is separately supplied and bound to decision/attempt/
actors/result; a checksum does not authenticate an actor. Relevant unchanged inputs may
reuse evidence; arbitrary new files, acceptance changes and dirty content cannot hide.

Required-policy bridge: `required` boolean, status loaded/unverified/error/not_required,
`source` and `version` string or null, applicability applicable/not_applicable/unknown.
`reason` is optional nonblank text. Required loaded policy needs nonblank source/version
and known applicability; unresolved data does not pass. Optional neutral context is
no-applicable-controls, not verified enterprise compliance. P05 owns this schema;
P07 must not declare a second interpretation. Every selected leaf covers every declared
required control, including both spec and quality where those are mandatory.

The Python 3.9+ product floor remains. P05's temporary 3.10 prerequisite was rejected
and corrected in annotations, preflight and documentation. Actual 3.9 execution remains
separate from grammar checks; no minimum-runtime pass is inferred.

Concrete P05 candidate CLI: `prepare --repo --request` emits immutable context;
`validate --record` is structural only; `li-review-log --file` records the decision;
`li-review-read --skill --expected --corroboration --gate-json` selects latest applicable
clearance. Standalone `verify --repo --record --expected --corroboration` cannot establish
latest-log status. `qa --repo --expected --input` validates recorded checks, without
running/repairing code. `ship --repo --skill --expected --corroboration --qa` invokes
the actual shared reader and same-context QA, never publication/deployment.

## P07 profile context

`lib/profile_context.py` is the shared stdlib parser/resolver/validator/digester.
`lib/profile-context-schema.json` describes v1 data/reference.
Target `.claude/profile-requirements.json` may declare
`{"schema_version":1,"required_pack":"synthetic-name"}` independently of the manifest.

Selection: repository requirement (conflicting invocation errors), explicit
`LINTEL_PROFILE_PACK` (required), legacy active pointer (optional with diagnostics),
neutral first use. Configured pack store/target/source lookup and whole-block inheritance
remain. Reference: schema_version, context_id, generation, `sha256:` digest, name, version.

Shell accessors: `bind_profile_context`, `verify_profile_context`,
`profile_context_reference`, `resolve_pack_field_json`, `profile_field_provenance`,
`rebind_profile_context`; legacy accessors retained. No PID-derived stable identity.
The documented lifecycle bootstrap must actually bind stable work/session context across
fresh shells or clearly fail required lifecycle use. Drift and required-load errors do
not silently downgrade policy. P05/P08/P04 carry digest/context/generation, not name alone.

Consumers never parse PACK_CACHE_FILE directly. P04 replaces its raw YAML/awk snippet.
P07's accepted Python names (final workflow gates remain separate) are
`ProfileConfig`, `resolve_profile`, `load_profile_context`, `profile_reference`,
`validate_profile_reference`, `verify_profile_reference`, `bootstrap_profile_context`,
`rebind_profile_context` and `required_policy`. `profile_required_policy` emits an error
bridge with nonzero status on load/drift failure, not success-shaped field defaults.
The no-host-ID Copilot bootstrap uses a durable selected repository work context, explicitly
not an invented host-session identifier, and verifies it across fresh subprocesses.

Source bundles need the Python helper, profile schema and pack schema. Explicit product
constraints need actual source product metadata, not an invented version. Missing product
identity cannot satisfy such a constraint.

## P06 host operations

`lib/cli-tiers.yaml` stays the single capability source, moving to JSON-compatible YAML
schema v2 for stdlib readers; `lib/client_capabilities.py` validates/selects it.
Keep distinct surfaces and compatibility aliases. Per operation distinguish vendor
source evidence, delivered binding/fallback and actual observed result (default not_run).
Current-session bindings separately identify callable tool and permission.

No structured question tool may use conversation where the host permits; denied
permission stays blocked. Lack of safe attributable write isolation selects serial,
lack of delegation selects durable external/manual handoff. Independent review remains
outstanding until separately corroborated. Data selection never grants tool permission.

P06's accepted Python interface is `load_registry`, `surface_id`, `describe`
and `resolve`. CLI: `bin/li-client-capabilities.py` validate/list/show/resolve/field/
normalize/table. Session binding schema separates tool availability, permission and
attributable isolation; `work_map` and `profile_ref` pass through unchanged. Resolution
reports `executed:false`, `declared-session-bindings` and independent review outstanding.
`bin/li-adapter.py` is a thin entry into the existing Copilot engine, not a second installer.

## P04 swarm and envelopes

Local evidence uses package_id/leaf_ids, acceptance_digest, attempt_id, result_digest,
exact report_digest and attributable Git/snapshot information. Historical v1 reports
remain unchanged, not silently upgraded. Final A22.7 consumes P05/P07/P08 contracts.

New transitive source files include `lib/swarm_snapshot.py`,
`lib/envelope_contract.py` and `bin/li-envelope-validate`. Joined preflight is committed
as `98ad7ed`; P10 now owns only its approved transaction/CLI extension, not navigation
or provider changes.
Default generated envelopes and the canonical envelope-schema file use stdlib-readable
JSON (also valid YAML). Legacy YAML parsing is optional/lazy with declared PyYAML
dependency and missing-parser refusal before output/audit. The unified audit writer
remains the writer; mandatory callers verify persisted receipt instead of trusting
its advisory failure behavior. No automatic handoff/hook activation follows.

## P10 installation and runtime boundaries

ADR-0030 and packages/P10.md record the explicit no-Python bare-install decision and
approved native receipt/runtime transaction split. Native Bash/PowerShell installation
must not invoke the Python dispatcher or install an interpreter automatically.
Already Python-based consumers retain the existing adapter inventory and ownership
policy; the shared transaction primitive does not acquire ownership from a later scan.

P03 compatibility dependency `ca28074` postpones annotation evaluation without changing
function behavior or snapshot formats. Its 23 context plus 24 snapshot tests pass on
Python 3.11.9, with a 3.9 grammar/annotation check; an actual 3.9 runtime is unavailable.
Do not convert that syntax evidence into a minimum-runtime execution claim.

P10's reported observation seams are still unaccepted implementation data, not an
agreed replacement audit schema. Its helper currently reports operation profile
reference, required caller policy, unbound target profile/selection and transaction
identity/state/snapshot/change/store information. Native receipts use versioned
meta.tsv/plan.tsv, per-file phases and aggregate incomplete/complete/recovered state;
the native installer does not call Python or an audit writer. P08 must coordinate
the exact frozen shapes and real producer fixtures before its A13 integration, retain
the native no-Python boundary, and distinguish observations from independent verification.

P08 currently reports a new, uncommitted trusted `lib/workflow.sh` reference consumer.
Its final accepted source must join the explicit installed-resource preflight as well
as ordinary lib copying. Do not import this WIP or make its absent file a prerequisite
for P10's current freeze; the coordinator reconciles that dependency after acceptance.
