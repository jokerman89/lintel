# Pack lifecycle

This is the shared procedure for the retained `pack-list`, `pack-validate`,
`pack-create` and `pack-switch` entrypoints, owned by `pack-switch`. There is no
new public `pack` command or second policy/parser implementation.

| Entry | Existing helper operation | Authority |
|---|---|---|
| `pack-list [--validate]` | `pack-list` | Read-only inventory; `--validate` requests per-row detail, not a helper flag |
| `pack-validate [name]` | `pack-validate [name]` | Read-only effective fields and compatibility |
| `pack-create` | `pack-create <name> --scope repo\|home [--extends <parent> \| --from <pack>]` | Explicit destination and reviewed manifest publication |
| `pack-switch <name>` | `pack-switch <name> --reason <text>` | Explicit policy-context/pointer change and generation rebind |

Use only the source-owned `bin/li-lifecycle` / `bin/li-lifecycle.py`. Root flags
precede the subcommand. Required policy and carried-reference errors stay errors;
no read binds or silently replaces a profile. Extension declarations are not
host discovery, permissions, model selection or hook activation.

## Switch

Change policy context only for the selected working repository and configured operator
store. Follow [lifecycle paths](../../../docs/lifecycle.md); a bare install, source bundle,
working target and profile pointer are different things.

## Workflow

1. Read the current `profile-status`, then `pack-validate <target>` through the source-owned
   helper. Show the current and requested effective voice, compliance, navigation, persona,
   role and extension fields. A changed policy can invalidate the current plan and review.
2. Establish authorization for this target and reason. An explicit operator switch is
   already authorization; ask only for a missing decision. Never replace a repository's
   required pack or silently remove `LINTEL_PROFILE_PACK` to make the switch succeed.
3. Run the actual helper and retain its exit status:

   ```bash
   bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
     --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" \
     pack-switch "$target" --reason "$reason"
   ```

4. Report `changed`, the effective pack, actual configured pointer and full returned
   reference: schema_version, context_id, generation, digest, name and version. A repeated
   switch to the already effective target is a verified no-op, not a new activation.
5. Carry the returned reference into subsequent work only as part of this explicit switch.
   Older handoffs must fail their reference check; replan affected work and obtain fresh
   review. Ordinary bootstrap verifies a pin and never silently adopts the new generation.

The helper consumes `LINTEL_PACKS_DIR` and `LINTEL_ACTIVE_PACK_FILE`, validates before
writing, atomically writes the configured pointer and invokes the accepted structured
rebind API. Profile history retains the previous generation and reason. Do not maintain
another parser, raw cache, home pointer or independent hand-written audit receipt.

## Drift and interrupted switching

`PROFILE_DRIFT`, missing history, invalid required packs and incompatible schema/product/
capability constraints are unresolved errors, never neutral success. A failed binding
after the pointer write is `PROFILE_SWITCH_INCOMPLETE`, not "active next session".
Preserve both pointer and history, inspect the error, then use an explicitly reasoned
rebind through the same helper:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" \
  profile-rebind --pack "$target" --reason "$recovery_reason"
```

Do not automatically roll back, delete a context, forge a reference or retry against a
different target. The legacy `clear_pack_cache` accessor remains an explicit reasoned
rebind compatibility path, not a way to discard history.

## Extension and host boundary

An extension pack still contributes its declared namespace, workflow and specialist
methods. Show those from the validated target values, including which surfaces it
declares. Identity selection does **not** install/discover plugins, register hooks, grant
permissions, copy private packs or switch models. Use the actual host-supported extension
operation separately with its own authorization and observed discovery evidence.

## List

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" pack-list
```

Render the actual configured-store, target-repository and trusted-source rows. Keep
all duplicate names visible as selected versus shadowed origins; configured store
precedes target, then source. Show name, origin/path, validity/diagnostics, effective
pack and pack release. The retained skill `--validate` asks for the helper's existing
validation/compatibility details; do not pass that flag to `pack-list`.

Schema, pack release, product and feature compatibility are different facts. A
`reference: null` is an unbound read, not a stable handoff. Optional fallback diagnostics
differ from valid neutral first use. A broken required pack or profile drift blocks
the read. Only `_default` ships here; list other configured packs without inventing
or hiding them. Listing changes no pointer/context, installs nothing and reads no
private role bodies.

## Validate

Validate after a manifest edit or before an authorized switch. With no name, the
helper uses the actual effective profile, not a guessed personal-home pointer:

```bash
validation_args=(pack-validate)
[ -z "${target:-}" ] || validation_args+=("$target")
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" "${validation_args[@]}"
```

Report the exit code, effective values and each ancestor's checked compatibility.
Nonzero is failure even when a manifest file exists. The shared profile implementation
checks matching directory/name, semantic pack versions, effective `voice.default_tier`,
`compliance.mode`, `navigation.default_workflow`, extension fields/control-list types,
missing parents, cycles and the ten-parent limit. Child blocks replace whole parent
blocks; required fields may be inherited. Do not run another parser.

Retain the existing syntax and compatibility limits:

- Legacy manifests without `schema_version` remain accepted. Indented/flow mappings,
  plain/quoted scalars and scalar block/flow lists are supported. Keys are unquoted
  identifiers (`[A-Za-z_][A-Za-z_0-9-]*`); root mappings start in column one.
- Anchors, tags, multiline scalars, complex list items, multiple documents and duplicate
  keys are rejected. Double-quoted escapes are `\\`, `\"`, `\n`, `\r`, `\t`; use
  literal Unicode rather than Unicode escapes. This is not general YAML certification.
- `schema_version` selects syntax, `version` is the pack release,
  `requires_lintel_product` uses source `.claude-plugin/plugin.json`, and
  `requires_capabilities` uses `lib/pack-schema.yaml`. Every ancestor is checked;
  child block replacement cannot hide an incompatible parent.
- Full-semver ranges support `=`, `==`, `<`, `<=`, `>`, `>=` and space/comma
  conjunctions, not other range syntax. Exact historical `requires_lintel: ">=4.0.0"`
  is a pack-v1 marker, not a public-product constraint; other historical values need
  explicit migration. Absent constraints mean not requested; unknown product metadata
  cannot satisfy a declared constraint. See [ADR-0029](../../../.claude/decisions/0029-required-profile-context.md).

For an already selected profile, the existing `profile_field_provenance` and
`profile_context_reference` accessors report verified origins/identity. They do not
authorize selecting another pack. Repository-required policy lives outside the manifest.

If `patterns.source` is declared, use the [pattern workflow](../../pattern/SKILL.md)
for its separate `li-pattern check` against the effective profile. Never switch a
candidate merely to perform that check. Report a candidate's unrun resource check
explicitly. Missing `root: pattern` assets are unavailable; missing Python is an
unavailable pattern check, not PASS. Report manifest and pattern results separately.

A structural PASS is not activation, a running company control, an installed plugin,
independent review or host enforcement. Validation writes no audit receipt or preference.

## Create

Use the existing pack rather than creating another for a one-off field change. For
a real new pack, gather only missing name, destination scope and mode decisions.
Never invent company identity, policy or a compliance posture.

- **Blank:** start with the neutral `_default` manifest.
- **Inherited:** declare identity and `extends`, plus only intentional overrides.
- **Cloned:** copy a chosen manifest as an editable starting point.

Select `--scope repo|home` explicitly. `repo` means the working repository's `packs/`;
`home` means the configured `LINTEL_PACKS_DIR`, not an assumed personal path. Keep
private identity out of repository/public output unless that transfer is authorized.

```bash
create_args=("$name" --scope "$scope")
[ -z "${parent:-}" ] || create_args+=(--extends "$parent")
[ -z "${template_pack:-}" ] || create_args+=(--from "$template_pack")
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" \
  pack-create "${create_args[@]}"
```

`parent` and `template_pack` are mutually exclusive. The helper stages/validates
ancestry with the same profile API, refuses an existing name in any resolution root,
and publishes one verified file. An inherited child does not copy neutral blocks
over company policy. A clone copies the **manifest only**, not private corpora,
credentials, executable extensions or hook settings. Inspect/configure referenced
resources before claiming they are usable.

Optional `patterns: { source: patterns/catalog.json }` is pack-relative; neutral is
`source: null`, and the entire block replaces an inherited block. Keep source-local
`.gitattributes` with `* -text` beside the catalog for exact asset bytes. Author
patterns only from confirmed expectations via the existing pattern workflow; ship
all declared assets and pinned `root: pattern` sources.

Run the validation procedure above and report the actual destination, effective
inherited values, checked compatibility and unresolved resource/host boundaries.
Creation neither activates nor privately synchronizes. Explicit switch is separate.
For an extension skeleton, retain `bin/li-pack-scaffold` with its explicit namespace,
workflow and destination; a skeleton is source, not a running plugin.

If scope is ambiguous, ask for `repo` or `home`. On failure preserve the diagnostic,
do not overwrite an existing manifest, invent a usable pack, or activate it anyway.
