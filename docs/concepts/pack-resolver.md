# Pack resolution and stable profile contexts

**Last updated:** 2026-09-20

`lib/pack-resolver.sh` preserves the shell accessor API over one structured
implementation, `lib/profile_context.py` (Python 3.9+, standard library only).
The same typed data supplies inheritance, validation, field provenance,
compatibility and SHA-256 identity. Configuration is never executable.
[ADR-0029](../../.claude/decisions/0029-required-profile-context.md) explicitly
replaces emergency-success and implicit mid-work refresh behavior.

## Selection and required policy

A repository can require a pack without trusting that pack to load first. Commit
this non-secret declaration as `.claude/profile-requirements.json`:

```json
{"schema_version": 1, "required_pack": "example-strict"}
```

The declaration has only these two keys; malformed or duplicate-key declarations
are unresolved requirements, not an absent policy. Selection precedence is:

1. Repository-required pack. A conflicting explicit selection is an error.
2. Explicit `LINTEL_PROFILE_PACK`. This is required, never an optional preference.
3. `LINTEL_ACTIVE_PACK_FILE`, normally `${LINTEL_PACKS_DIR}/active-pack`.
   This legacy pointer remains an **optional preference**.
4. No selection: validated neutral `_default`, without a global installation.

A missing, malformed or incompatible required pack returns nonzero without a
neutral value. An invalid optional preference can load validated `_default`,
but emits `OPTIONAL_PROFILE_FALLBACK` and records `selection.status: fallback`.
It is not successful activation of the requested company policy. An invalid
neutral baseline, missing parser or unreadable input is an actual error.
There are no hardcoded emergency policy values. `profile.yaml` continues to
hold mode/role preferences; its historical `active_pack` is not a selector.

For each named pack, directory precedence remains `${LINTEL_PACKS_DIR}/<name>`,
`${LINTEL_REPO_ROOT}/packs/<name>`, then `${LINTEL_SOURCE_ROOT}/packs/<name>`.
The source is the approved installed helper bundle; the target is the repository
whose requirements and runtime are being used. Explicit approved roots are honored.
Repository requirements constrain the selected name, not a second executable loader
or a hidden override of the explicitly configured pack store.

## Bootstrap, handoff and resume

For the portable Copilot kit, run the documented bootstrap in **each** fresh shell:

```bash
source .github/lintel/lib/copilot-env.sh
lintel_copilot_env "$PWD" || exit $?
source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"
profile_context_reference
```

When developing Lintel itself, source `lib/copilot-env.sh`. It defaults to a local
`.claude/runtime/lintel-home`, preserves explicitly configured roots and actually
binds/verifies the profile before returning. A bootstrap failure blocks dependent work.

An explicit optional second argument, `lintel_copilot_env "$PWD" work-42`, selects
a known stable work context. Otherwise the helper honors `LINTEL_PROFILE_CONTEXT`,
explicit `LINTEL_SESSION_ID`, a real `CLAUDE_SESSION_ID`, or an existing
`LINTEL_PROFILE_CONTEXT_FILE`. **No PID/PPID fallback exists.** With no supplied ID,
bootstrap atomically creates or verifies `.claude/runtime/profiles/selected.json`
and exports its durable context ID **and exact canonical `LINTEL_PROFILE_REFERENCE`**.
Two fresh shells therefore consume the same
selected work profile. This is repository work selection, not a claimed host session
identity; give separate concurrent initiatives explicit work IDs.

Bootstrap, bind, verify, rebind and the compatibility cache-clear operation use one
reference-publication helper. Successful selection always carries context, generation
and digest to subsequent calls and inherited processes. Repeating bootstrap or binding
the same ID does not discard an already expected generation. A caller cannot silently
adopt a child process's rebind; it must explicitly verify that approved new reference.
Even an invocation-scoped `LINTEL_PROFILE_PACK=strict lintel_copilot_env "$PWD"` retains
the required profile afterward. The internal bootstrap CLI also returns the complete
reference, not an ID-only continuation token.

Direct accessor calls without bootstrap/ID still support one-shot neutral or pack
reads, but cannot emit a pinned reference. Lifecycle producers must bootstrap or
call `bind_profile_context <stable-context-id>`; a reference records:

```json
{
  "schema_version": 1,
  "context_id": "work-42",
  "generation": 1,
  "digest": "sha256:<64 lowercase hexadecimal characters>",
  "name": "example-strict",
  "version": "1.2.3"
}
```

Pass this JSON as data with a delegated or cold-executor handoff, retaining the
approved source/target/home roots. In a fresh process:

```bash
source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"
verify_profile_context "$handoff_reference_file" || exit $?
profile_required_policy || exit $?
resolve_pack_field compliance.mode || exit $?
```

Verification does not create a missing context or replace an expected generation.
On success, the shell helper exports the exact verified JSON as
`LINTEL_PROFILE_REFERENCE`. Subsequent accessors, a re-sourced resolver and newly
spawned child processes verify that same context, generation and digest. The shared
parser consumes this transport; callers must not reinterpret or manually edit it.
Call `verify_profile_context` directly in the shell that will perform the work,
not inside command substitution or a pipeline whose exports cannot reach its parent.
Redirecting its output to a file does not prevent propagation.

The explicit reference selects its work identity over a new ambient host session.
A contradictory explicit `LINTEL_PROFILE_CONTEXT` remains an error. An original
explicit pack request is retained in the binding when a fresh consumer does not
repeat it. Failed verification does not replace an already verified selection.
A later generation or lost pin blocks subsequent accessors instead of resolving
neutral data. A lost/malformed required reference is unresolved policy, not evidence
that the policy was optional. Valid neutral/advisory profiles retain their ordinary
non-required control status.

A reference does not grant permission to change target repositories, activate hooks
or claim independent review. Approved policy source/target roots must still match;
an isolated worktree is not automatic cross-target profile transfer.

## Drift and rebind

Runtime records live at `${LINTEL_HOME}/sessions/profiles/<context-key>/current-profile.json`
or an explicitly selected context file within that home or target `.claude/runtime/`.
`profile-context-schema.json` defines the record/reference/requirements shapes.
Records contain typed values, exact per-field manifest provenance, source/target
roots, root-to-leaf ancestry, compatibility results and input content hashes.

Each bound read rechecks **bytes**, not modification times. Pointer changes,
same-mtime manifest/parent edits, deletion, required-declaration changes, a newly
higher-precedence source and compatibility metadata drift return `PROFILE_DRIFT`.
Even a now-invalid optional pack cannot silently replace a previously bound profile.

After an authorized profile change, explicitly run:

```bash
rebind_profile_context "approved policy update; replan affected work"
```

The new generation is validated first. Every published record, including the initial
and current generations, is retained immutably in `history/` using the same record
schema. A missing current record is not evidence of first use: `create=True` refuses
to recreate it when history or the selected reference shows prior binding. A current
record replaced by an older or conflicting retained generation also fails.

The old record is retained in `history/`,
old references stop matching, and the repository selected reference is updated
only if it names this context. Replan/review dependent work against the new reference.
Rebind holds the repository selection lock before the context lock and publishes
both records before releasing the transaction. Concurrent successful rebinds cannot
leave `selected.json` behind the current generation. An explicit rebind can repair
a stale same-context selection only when its reference is corroborated by retained
history; it neither fabricates history nor takes another context's selection.
An interrupted write that did not return success remains an explicit recovery case.

For a missing current record, a reason-bearing `rebind_profile_context` can recover
from the unambiguous latest retained record and publish the **next** generation.
It preserves that record's required invocation selection and never restarts at
generation 1. A supplied expected reference must match the retained generation.
Missing, incomplete, conflicting or corrupt history is not sufficient recovery
evidence; preserve it and restore a verified record rather than fabricating one.
A genuinely unused explicit work ID can still be bound normally. This is new work,
not permission to reset or silently replace a lost existing context.

Successful shell bind/rebind updates `LINTEL_PROFILE_REFERENCE` in the caller;
already-running consumers retain their old generation and must explicitly verify
the newly approved reference before continuing. Do not silently clear a stale
expected reference to bypass review or policy drift.
`clear_pack_cache` is a compatibility spelling for this explicit rebind; it no
longer deletes evidence. Interrupted-writer locks fail visibly rather than being
stolen by guessing that a process is dead.

These local records are consistency evidence, not tamper-resistant audit storage.
Publish only approved non-secret reference/identity data, not entire runtime profiles.

## Inheritance, types and compatibility

Each manifest has its own matching directory/name and semantic `version`. A child
replaces every declared **top-level block wholesale**; lists are never concatenated.
Required effective voice/compliance/navigation fields validate before neutral
missing-field defaults. Explicit null, false, empty strings/lists and quoted string
types remain explicit. A null block is not recursively filled with neutral subfields.
See [inheritance](pack-inheritance.md) and [neutral defaults](pack-defaults.md).

Supported YAML is indented/flow mappings and scalar lists, with plain identifier
keys, root mappings in column one, and plain/single/double-quoted values. Duplicate
keys, anchors, aliases, tags, multiline scalars, complex list items and multiple
documents are errors. Double-quote escapes are `\\`, `\"`, `\n`, `\r`, `\t`.
Unquoted `true`/`false` and `null`/`~` are typed; quoted forms are strings.
Legacy boolean helper aliases `yes`/`on` remain supported.

Compatibility axes are independent and checked for **every ancestor**:

| Axis | Contract |
|---|---|
| Pack schema | `schema_version: "1"`; absent is legacy schema 1; unsupported explicit versions fail |
| Pack release | `version`, belonging to that pack, not the product |
| Public product | `requires_lintel_product`, compared to source `.claude-plugin/plugin.json` |
| Feature contracts | `requires_capabilities`, compared to `runtime_compatibility` in `lib/pack-schema.yaml` |
| Historical marker | Exact `requires_lintel: ">=4.0.0"` means legacy pack-v1, **not public v4+** |

Product and feature ranges support full semantic versions with `=`, `==`, `<`,
`<=`, `>`, `>=`, and space/comma-separated conjunctions. Unsupported syntax is an
error. Other historical `requires_lintel` ranges must be explicitly migrated.
Unknown product metadata cannot satisfy a declared product constraint. No product
constraint means it is not checked, not that the product was verified. Extension
capability declaration does not prove host discovery or control execution.

## Public accessors and control bridge

Existing functions remain: `get_active_pack_name`, `get_loaded_pack`,
`validate_pack <name>`, `resolve_pack_field <path>`, `pack_field_is_true <path>`,
`pack_is_extension`, `pack_namespace`, `pack_workflow`, `clear_pack_cache`.
Shell lists retain `[a, b]`; absent optional fields return empty. Errors return
nonzero without success-shaped values. Use `resolve_pack_field_json` when quoting
or null/string distinctions matter; its absent-field status is 1, explicit null is 0.

New functions include `pack_compatibility <name>`, `profile_field_provenance <path>`,
`profile_context_json`, `profile_context_reference`, `bind_profile_context`,
`verify_profile_context`, `rebind_profile_context`, and `profile_required_policy`.
`PACK_CACHE_FILE` is no longer a YAML document. Consumers must use shared accessors,
not parse cache storage. There is no second YAML parser in shell.

`profile_required_policy` emits exactly `{required,status,source,version,applicability}`.
Required load is `loaded`/`applicable`; optional/neutral is `not_required`/
`not_applicable`. Unresolved load/drift emits `error`/`unknown` **and exits nonzero**.
When a transported reference is lost or invalid, policy applicability is unknown
and `required` remains true; absence of the pin cannot erase a prior requirement.
This bridge is for P05's control result, not a claim that loaded controls passed.
Mandatory missing/error/unverified evidence still blocks in the consuming workflow.

`tests/integration/universal-profile-context.sh` exercises actual producer/fresh
process/handoff/resume, no-ID bootstrap, required failures, same-time drift,
provenance and independent compatibility. Existing pack, extension and source/target
tests preserve their useful cases. Joined work/review/host consumers and actual
company/renderer/model acceptance require their own integration evidence.
