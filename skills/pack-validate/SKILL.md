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
activation. Report what passed, what failed, and which compatibility checks remain
manual. A child can inherit required policy blocks; an explicitly declared child
block replaces its parent's whole block.

## Workflow

### 1. Validate the effective manifest

```bash
source "$REPO_ROOT/lib/pack-resolver.sh"
target="${1:-$(get_active_pack_name)}"
verdict=PASS
if validate_pack "$target"; then
  echo "PASS: manifest identity, required effective fields, extension fields and inheritance"
else
  verdict=FAIL
  audit_log pack-lifecycle pack_validated "name=$target" "verdict=$verdict"
  echo "FAIL: pack cannot be activated; correct the diagnostic above."
  exit 1
fi
```

Runtime validation covers nonempty name/version in each manifest, effective
`voice.default_tier`, `compliance.mode`, `navigation.default_workflow`, required
extension fields, missing parents, cycles and the ten-parent limit. It preserves
legacy packs without `schema_version` or `requires_lintel`.

The shared parser supports indented and flow mappings, plain or quoted scalar
values, and scalar lists in block or flow form. Mapping keys must be unquoted
identifiers (`[A-Za-z_][A-Za-z_0-9-]*`); root mappings start in column one.
Anchors, tags, multiline scalars and
complex list items are unsupported. These are runtime contract checks, not a
general YAML-schema certification.
Double-quoted escapes supported by the parser are `\\`, `\"`, `\n`, `\r`, and
`\t`; use literal Unicode characters instead of Unicode escape sequences.

### 2. Report schema and version compatibility

```bash
pack_dir=$(_pack_dir "$target")
schema=$(_pack_yaml_field "$pack_dir/pack.yaml" schema_version) || schema=""
requires=$(_pack_yaml_field "$pack_dir/pack.yaml" requires_lintel) || requires=""
echo "Declared schema: ${schema:-not declared (legacy)}"
echo "Required Lintel: ${requires:-not declared (legacy)}"
echo "Compatibility: NOT VERIFIED by runtime validation."
verdict=PASS_WITH_WARN
```

Read `lib/pack-schema.yaml` for the intended field contract and the installed
plugin manifest for its actual version. If the pack declares a version range or
schema unsupported by that installation, explain the mismatch before activation.
Do not claim compatibility from a hardcoded version or a matching major-version
prefix. This skill does not introduce a new version-enforcement policy.

### 3. Audit and return the result

```bash
audit_log pack-lifecycle pack_validated "name=$target" "verdict=$verdict"
echo "$verdict: runtime contract passed; review compatibility before activation."
```

Use `FAIL` for runtime rejection and `PASS_WITH_WARN` while compatibility is
unverified. Record any completed manual compatibility review and its evidence.
Never report an unexecuted gate as passing or activate a pack as a side effect.

## Integration

Reads `lib/pack-resolver.sh`, `lib/pack-schema.yaml`, and the target ancestry.
Writes the verdict to stdout and the operator's pack lifecycle audit log.
