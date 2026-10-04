# Optional engineering preference metadata

The modules' retained `domain.preferences_root: engineering.<domain>.*` strings
are legacy discovery hints, **not a validated pack interface**. They are not fields
declared by `lib/pack-schema.yaml`, wildcard resolver queries, required defaults or
proof that preference data exists. Module names and this metadata stay compatible;
no new manifest/schema keys or policy mechanism are introduced.

Use actual optional preference data only when explicitly supplied or read from the
selected verified profile with an exact supported accessor path. Record its source
and meaning as advice unless a real applicable policy separately makes a requirement
mandatory. A successful profile load does not type-validate these undeclared
engineering preferences. Missing advice remains missing; do not read a personal
profile or manufacture a default.

The existing resolver preserves optional manifest data and whole-block inheritance:
when a child supplies a top-level block, it replaces that parent block rather than
deep-merging nested preferences. Do not reinterpret the legacy hint as permission
to add defaults or alter that behavior.

The optional DA/SC warning hooks read the distinct exact legacy fields
`data_architecture.migration_glob` and `security_compliance.auth_flow_glob`.
Those are optional comma-separated filename pattern data, not typed engineering
policy fields or aliases for `engineering.*`. Their heuristic warnings never
satisfy required migration/auth review or required-profile validation.
