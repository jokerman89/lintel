# Shared implementation interfaces

Coordinator-owned agreements for dependent packages. These signatures are proposals
accepted for implementation; code and contract tests at exact package revisions establish
their final availability. No second task/status ledger is introduced here.

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

Candidate producer seam: prepare's input retains its old fields plus `qa_requirements`
(no input version flag). It emits context version 2; the decision and QA receipt also
use version 2. A mandatory QA ID such as `tests` must appear in `required_controls`,
the review's typed controls, and each selected leaf's coverage. The typed obligation
is not reconstructed from observed results. Profile references, work maps, corroboration
and the standalone control-outcome envelope retain version 1.

`CONTRACT_VERSION=2` is scoped to the bound review/context/QA contract.
`validate_decision(record, history=...)` preserves strict historical-v1 inspection, not
clearance. `select_latest` keeps its existing keyword arguments and accepts decoded
mappings or ordered `ContractError` candidates; an invalid latest applicable candidate
cannot be discarded into an older PASS. The final source-owned example is
`skills/review/references/evidence.md` at the forthcoming immutable P05 repair.

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

The existing Python 3.9+ product floor remains. P05's temporary 3.10 prerequisite was
rejected as an unnecessary support regression; the worker is correcting annotations,
preflight and documentation rather than silently changing compatibility.

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
P07's implemented Python names (candidate verification still in progress) are
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

P06's current candidate Python interface is `load_registry`, `surface_id`, `describe`
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
`lib/envelope_contract.py` and `bin/li-envelope-validate`. P06 owns consumer preflight.
Default generated envelopes and the canonical envelope-schema file use stdlib-readable
JSON (also valid YAML). Legacy YAML parsing is optional/lazy with declared PyYAML
dependency and missing-parser refusal before output/audit. The unified audit writer
remains the writer; mandatory callers verify persisted receipt instead of trusting
its advisory failure behavior. No automatic handoff/hook activation follows.
