---
name: pack-validate
layer: foundation
description: Validate a pack before activation or after editing its manifest. Checks effective required fields and inheritance with the shared resolver, then reports schema and version compatibility limits.
color: green
tools: Read, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

Validate the target pack with the same parser and effective-field rules used at
activation. Report what passed, what failed, and which host/policy checks remain
unverified. A child can inherit required policy blocks; an explicitly declared child
block replaces its parent's whole block.

## Workflow

### 1. Validate the effective manifest

```bash
pack_source_root="${LINTEL_SOURCE_ROOT:?approved installed Lintel source is required}"
source "$pack_source_root/lib/pack-resolver.sh" || exit $?
if [ -n "${1:-}" ]; then
  target="$1"
else
  target=$(get_active_pack_name) || exit $?
fi
verdict=PASS
if validate_pack "$target"; then
  echo "PASS: manifest, inheritance and declared schema/product/feature compatibility"
else
  verdict=FAIL
  audit_log pack-lifecycle pack_validated "name=$target" "verdict=$verdict"
  echo "FAIL: pack cannot be activated; correct the diagnostic above."
  exit 1
fi
```

Runtime validation covers a matching directory/name and semantic pack version in each manifest, effective
`voice.default_tier`, `compliance.mode`, `navigation.default_workflow`, required
extension fields, control-list types, missing parents, cycles and the ten-parent limit.
It preserves legacy packs without `schema_version` and recognizes exact historical
`requires_lintel: ">=4.0.0"` as a pack-v1 marker, not a public product constraint.

The shared parser supports indented and flow mappings, plain or quoted scalar
values, and scalar lists in block or flow form. Mapping keys must be unquoted
identifiers (`[A-Za-z_][A-Za-z_0-9-]*`); root mappings start in column one.
Anchors, tags, multiline scalars and
complex list items, multiple documents and duplicate keys are rejected. These are runtime contract checks, not a
general YAML-schema certification.
Double-quoted escapes supported by the parser are `\\`, `\"`, `\n`, `\r`, and
`\t`; use literal Unicode characters instead of Unicode escape sequences.

### 2. Report schema and version compatibility

```bash
pack_compatibility "$target" || exit $?
```

This uses the same structured implementation as activation. `schema_version`
selects manifest syntax; `version` belongs to the pack; `requires_lintel_product`
checks the installed source's `.claude-plugin/plugin.json`; `requires_capabilities`
checks feature contract versions in `lib/pack-schema.yaml`. Every ancestor's
requirements are checked, so child replacement cannot erase an incompatible parent.
Absent constraints mean not requested, not an executed compatibility check.
Unknown product metadata cannot satisfy a declared product constraint.

Ranges support full semver with `=`, `==`, `<`, `<=`, `>`, `>=` and space/comma
conjunctions. Other range syntax is rejected. Other historical `requires_lintel`
values require explicit migration rather than comparison to public 0.x versions.
See [ADR-0029](../../.claude/decisions/0029-required-profile-context.md).

For an already selected profile, `profile_field_provenance <dotted.path>` and
`profile_context_reference` report verified origins and bound identity. They are
not a reason to activate a different target as part of validation. Repo-required
policy is declared outside its manifest; a failed required load remains an error.

### 3. Audit and return the result

```bash
audit_log pack-lifecycle pack_validated "name=$target" "verdict=$verdict"
echo "$verdict: declared runtime contracts passed; live host/company controls remain unverified."
```

Use `FAIL` for runtime rejection. A structural `PASS` is neither successful
activation nor proof that a company control, extension plugin, independent review
or host enforcement mechanism ran. Record those acceptance boundaries separately.
Never report an unexecuted gate as passing or activate a pack as a side effect.

## Integration

Reads `lib/pack-resolver.sh`, `lib/pack-schema.yaml`, and the target ancestry.
Writes the verdict to stdout and the operator's pack lifecycle audit log.
