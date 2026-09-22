# Pack inheritance: whole-block replacement

**Last updated:** 2026-09-20

A pack can declare one `extends:` parent. The resolver follows root to leaf,
rejecting missing parents, cycles and more than ten parent links. Each manifest
needs its own matching name and semantic version. Policy blocks can be inherited.
Identity-only and extension packs use the same rule.

## Precedence without hybrid blocks

Each child top-level key replaces the parent's **entire** value:

```yaml
# example-base/pack.yaml
name: example-base
version: 1.0.0
voice: {default_tier: mixed, gates_active: [voice-check]}
compliance: {mode: hard, hooks: [evidence-check]}
navigation: {default_workflow: controlled}
```

```yaml
# example-team/pack.yaml
name: example-team
version: 1.0.0
extends: example-base
voice: {default_tier: internal}
```

The team inherits the base compliance and navigation blocks. Its voice block does
**not** retain `voice-check`. The omitted `voice.gates_active` instead uses the
neutral `[]` field default, identified as neutral fallback in provenance.
Required fields validate in the effective ancestry before those neutral defaults
are considered; an explicit `compliance: {hooks: []}` is invalid, not repaired by
adding a neutral `compliance.mode`.

The same applies to `brief_forge_handoffs`. Declaring that block replaces every
parent handoff setting. Lists are not concatenated or deduplicated. A child adding
an evaluator must restate all settings/evaluators it intends to retain.

Explicit `null`, `false`, `""`, `[]` and quoted scalar types survive. An explicit
null block stays null rather than being recursively repopulated from defaults.
A missing field absent from both effective and neutral data returns empty through
the legacy shell accessor. Typed accessors distinguish missing from explicit null.

## Ancestry is not neutral fallback

`_default` is not an implicit parent. A pack can explicitly extend it, but ordinary
neutral missing-field fallback is separate from declared ancestry. For a three-level
chain, `_resolve_extends_chain example-team` returns its actual root-to-leaf names.
`profile_field_provenance compliance.mode` identifies the exact owning manifest,
version, SHA-256 and whether the field came from neutral fallback.

One structured representation handles merge, values, provenance, compatibility and
context identity. The shell API is an adapter; consumers must not merge text or parse
`PACK_CACHE_FILE`. See [pack resolution](pack-resolver.md) for the stable reference.

## Invalid or changed parents

`validate_pack <name>` rejects an invalid chain without activating anything.
A failed required selection never becomes neutral/advisory success. Only an
initial **optional legacy preference** may use diagnostic neutral fallback.
Neutral first use without a requested profile remains valid.

Every bound read verifies each ancestor's content, independent of timestamps.
A deleted parent, a same-mtime edit, or a source/selection change blocks with
`PROFILE_DRIFT`. Explicit rebind validates a new generation and retains the old
one for evidence; dependent work must be replanned/reviewed. This replaces the
historical cache deletion/pointer-ignore behavior under ADR-0029.

Compatibility also belongs to each manifest: a child cannot overwrite an
incompatible parent's product or capability requirement. Pack release versions,
schema versions and installed product versions are different axes.

## Verification and limits

`tests/unit/pack-inheritance-depth-3.sh` covers depth, whole-block replacement,
neutral provenance and cycles. `tests/unit/enterprise-pack-resolution.sh` adds
quoted/null/list semantics and malformed input. The Universal profile integration
test covers deleted and same-mtime-edited parents across fresh processes.

Inheritance is for shared identity/policy blocks, not an implicit per-task override
or multi-parent composition. Workflow flags select workflows; they do not rewrite
the bound corporate policy. To change one team, change its declared block rather
than silently changing a shared parent's meaning for every sibling.
