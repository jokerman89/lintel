# Pack resolution — one accessor and explicit failure behavior

**Last updated:** 2026-09-08

Thirty-plus skills consume voice, compliance, navigation and hand-off settings.
`lib/pack-resolver.sh` provides a shared parser and accessor so consumers agree
on those values. It validates and caches the effective manifest, then extracts
requested fields from that cache. Subsequent reads check manifest freshness;
this is not a parse-once performance guarantee.

## Source, target and profile roots

`LINTEL_SOURCE_ROOT` identifies the installed Lintel bundle containing helpers
and neutral defaults. `LINTEL_REPO_ROOT` identifies the repository being worked
on. The Copilot adapter sets these separately; a consumer does not need top-level
copies of Lintel's `lib/` or `packs/_default/`.

For a named pack, lookup checks these directories in order:

1. `${LINTEL_PACKS_DIR}/<name>` (normally `${LINTEL_HOME}/packs/<name>`).
2. `${LINTEL_REPO_ROOT}/packs/<name>`.
3. `${LINTEL_SOURCE_ROOT}/packs/<name>`.

The active pointer is `LINTEL_ACTIVE_PACK_FILE`, defaulting to
`${LINTEL_PACKS_DIR}/active-pack`. `profile.yaml` carries mode and role
preferences; its legacy `active_pack` field is not the selector.
`get_loaded_pack` reports the effective cached identity, including fallback.
A shared operator home implies shared selection across repositories. Repository
adapters can set separate roots; inspect resolved paths before switching.

## Inheritance and validation

A pack can declare one `extends:` parent. Each manifest needs its own name and
version; policy blocks can be inherited. Validation checks the effective
`voice.default_tier`, `compliance.mode` and `navigation.default_workflow`.
Compliance mode must be `hard`, `advisory` or `off`; enabled extension packs
must declare a namespace and workflow.

The chain is merged root to leaf. Every child top-level block replaces that
parent block wholesale. This includes `brief_forge_handoffs`: evaluator lists
are not concatenated or deduplicated. See [pack inheritance](pack-inheritance.md).

Missing parents, cycles, ancestry exceeding ten parent links, missing required
effective fields and unsupported manifest syntax reject activation.
`lib/pack-schema.yaml` is an authoring reference; runtime does not interpret it
as a complete executable schema. Optional field types and schema/semver
compatibility are not fully verified. [Pack validation](../../skills/pack-validate/SKILL.md)
reports that limitation instead of claiming an unexecuted check passed.

## Field representation and fallback

`resolve_pack_field <dotted.path>` reads nested scalar values and scalar lists.
Block and inline lists return the same `[a, b]` representation, including
three-level hand-off evaluator lists. Quoted scalar values preserve spaces and
literal hash characters. Mapping keys are plain identifiers; supported syntax
and escape limits are documented in the validation skill.

Resolution follows these rules:

1. Return a field explicitly present in the effective session manifest.
   Explicit `null`, `false`, empty strings and `[]` remain explicit.
2. For an absent field, read its neutral `_default` value. A field absent from
   both manifests returns empty.
3. If cache priming itself fails, emit diagnostics and return an emergency
   neutral value for the known critical fields below; other paths return empty.

| Emergency field | Value |
|---|---|
| `voice.default_tier` | `internal` |
| `compliance.mode` | `advisory` |
| `compliance.workprofile_default` | `off` |
| `navigation.default_workflow` | `cycle` |
| `navigation.orientator_budget_tokens` | `2000` |
| `navigation.orientator_max_output_tokens` | `200` |
| `navigation.escalation_threshold` | `medium` |
| `brief_forge_handoffs.budget_tokens` | `5000` |

Required policy fields must validate before activation. Field fallback does not
make an incomplete policy block valid. An invalid active pack follows the
existing documented behavior: warn, audit and load `_default`. Enterprise
callers must surface that fallback; it is not successful enterprise activation.

## Workflow defaults

Generic build and unclear requests use `navigation.default_workflow`. A bare
workflow in an extension pack is qualified with `extension.namespace`; a fully
qualified `/namespace:workflow` stays unchanged. Explicit review, research, fix,
ship and resume requests retain their dedicated routes. To select the neutral
cycle from an extension pack, declare `/li:cycle` explicitly.

High-risk rules can name a bare workflow ID (matching all namespaces) or a
qualified command (matching that namespace only). Configured high-risk membership
wins over lower-risk heuristics. Routing recommends a command; it does not install
the extension plugin, prove host discovery or execute the workflow.

## Session cache and audit

The cache lives at `${LINTEL_HOME}/sessions/<session-id>-pack-cache.yaml`.
Changing only the active pointer preserves the current session cache. A newer
manifest or invalid edited ancestry invalidates the corresponding cached pack.
Deleting a cached pack directory leaves its cache available for the current
session. `clear_pack_cache` explicitly forces resolution again.

A new session ID gets its own cache. The ID precedence is explicit
`LINTEL_SESSION_ID`, then `CLAUDE_SESSION_ID`, then a process-derived fallback.
Hosts without a stable session ID should supply one.

The shared audit writer records cache priming, invalidation and fallback events
in `${LINTEL_HOME}/audit/pack-resolver.jsonl`, or an explicitly configured
`LINTEL_AUDIT_DIR`. These are local diagnostic records, not tamper-resistant
enterprise audit storage.

## Public functions and verification

- `get_active_pack_name`: selected pointer value, or `_default`.
- `get_loaded_pack`: effective cached identity.
- `validate_pack <name>`: runtime contract checks without activation.
- `resolve_pack_field <path>`: field value or empty.
- `pack_field_is_true <path>`: success for `true`, `yes` or `on`.
- `pack_is_extension`, `pack_namespace`, `pack_workflow`: extension awareness.
- `clear_pack_cache`: explicit session-cache invalidation.

The isolated fallback and inheritance unit tests cover neutral loading, malformed
packs, missing fields, cycles, repeated reads, pointer switching and cached pack
deletion. `tests/unit/enterprise-pack-resolution.sh` adds list/quoted-value
parsing, inheritance boundaries and malformed-input regressions.
`tests/integration/enterprise-pack-impact.sh` verifies values reaching gate-list
consumers, routing and the session digest. Host discovery and live execution of
pack-provided gates need separate acceptance evidence.
