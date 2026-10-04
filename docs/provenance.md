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
retired or renamed entrypoints, including several whose names came from an earlier external
harness (see [ADR-0011](../.claude/decisions/0011-native-workflow-ownership.md) and
[ADR-0034](../.claude/decisions/0034-native-workflow-consolidation.md)). It changed only design-dna's
routing text in `SKILL.md`; the attributed corpus, scripts, profile, attribution and license files
are unchanged and stay with the component. Removing an
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

The original 2026-09-28 review's G-01/G-11 comparison pointers are retained
separately under `method_comparison_addenda`, alongside (not replacing) those
older pins. The [review summary](../.claude/engineering/audits/2026-09-28-skill-review-v2-summary.md)
identifies that dated assessment; the registry records the pointers from the
original findings. No external fetch or new upstream study was performed when
recording this addendum.

Spec Kit `c00dc0551583428a10a94443c58c6a41e5e0138c` is the original comparison
pin, not proof of an installed local tool, enabled extension or host execution.
Its analysis/converge/workflow overlap is handled by the
[artifact bridge](spec-kit.md#select-reports-and-resolve-overlapping-checks).
Native plan-mode coverage still needs actual supplied/inspected host observations,
not a presumed capability or a fabricated comparison revision.

The registry's current-facing GSD URL uses the original review's
`open-gsd/gsd-core` reference; its historical key, install path, verification date
and 2026-09-20 method pin remain. ECC's changing inventory counts are omitted,
not replaced with invented current numbers. The dated comparison and import
records, narrowed design-dna attribution and retained notices are unchanged.
Historical method observations are not current upstream support for a planning
prescription; Lintel's accepted planning rules retain their own authority.

Product version, pack schema and capability compatibility describe different contracts.
Their validation belongs to the corresponding profile/adapter interfaces; provenance
remains tied to exact source components and the delivered revision.
