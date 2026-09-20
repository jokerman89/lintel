# Shared implementation interfaces

Coordinator-owned agreements for dependent packages. These signatures are proposals
accepted for implementation; code and contract tests at exact package revisions establish
their final availability. No second task/status ledger is introduced here.

## P05 review and controls

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
source, version and applicability. Required unknown/failure blocks. Optional neutral
context is no-applicable-controls, not verified enterprise compliance.

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
