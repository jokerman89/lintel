# Provenance and reuse

Lintel contains author-written integration and explicitly attributed adaptations.
It does not automatically download the external projects listed in
[the source registry](../install/upstream-sources.yaml). Not downloading during
installation is different from claiming that no third-party material is distributed.

## Existing distributed material

The [design-dna attribution](../skills/design-dna/ATTRIBUTION.md) records the consumed
UI/UX Pro Max corpus/search components and Anthropic example-profile/doctrine material,
local modifications and notices. The corresponding
[MIT notice](../skills/design-dna/LICENSES/MIT-next-level-builder.txt) and
[Apache-2.0 license](../skills/design-dna/LICENSES/Apache-2.0-anthropic.txt) remain with
the component. Descriptive origin names do not imply endorsement.

The recorded UI/UX Pro Max release is v2.5.0. Exact historical import commit IDs were
not captured in the existing attribution and remain explicitly unknown. Do not replace
that gap with a current upstream head or the revision inspected in a later comparison.
An update should pin the actual reviewed source revision and retain applicable notices.

## Workflow consolidation

The 2026-09-25 [native workflow migration](migrations/2026-09-25-native-workflows.md)
retired or renamed entrypoints, including several whose names came from the reference-only
harness Lintel grew out of (see the registry and
[ADR-0011](../.claude/decisions/0011-gstack-de-heritage.md)). It did not change the
design-dna component, and its attribution and license files above stay with it. Removing an
entrypoint does not remove a notice owed by retained content; if a retained file still carries
adapted material, its notice stays with that file.

## Adding or adapting material

Record the source URL, exact revision and component path, whether material was copied,
adapted or consulted as a method reference, local destinations and modifications, license
and notice locations, and the verification date. Keep those records with the distributed
component and ensure optional bundles carry their required notices too.

Review the terms of the exact component and intended use. A top-level repository license,
a permissive label, public visibility or a language rewrite is not a substitute for that
review. An unresolved rights question needs qualified review before reuse; do not invent
a blanket "safe to install" or "safe to redistribute" assurance.

Do not use similarity thresholds, synonym substitution or section reordering as a rights
or quality test. The archived proposal for that approach is superseded, not a release
requirement. Useful borrowed methods should improve observable decisions, negative-case
handling and preserved functionality; an independently passing behavior test still does
not waive applicable attribution.

## Comparison evidence versus import evidence

The 2026-09-20 comparison inspected selected method-source revisions. Their exact
identities and revisions are recorded separately under `method_comparisons` in the
registry. They establish which material informed that comparison, not what Lintel once
imported, whether an upstream workflow ran successfully, or a measured performance gain.

Product version, pack schema and capability compatibility describe different contracts.
Their validation belongs to the corresponding profile/adapter interfaces; provenance
remains tied to exact source components and the delivered revision.
