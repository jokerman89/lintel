# Preparatory integration of the reviewed pattern source

**Authority:** portfolio coordinator's bounded 2026-09-29 grant.
**Original adaptive source:** `c097360f7ad7e74c66a9435e1fcc622189457f47`,
tree `b42f0bae365d793d95b047ef0f7a67ca8d3c28e3`.
**Exact upstream:** `d89385f2567e490896e078de466ae3f1bedf98c4`,
tree `586905863c7c985343d9071a20be4c98d8ec24b4`.
**Status:** joined verification preparation, not main or release clearance.

## Integration decisions

One ordinary merge in the existing adaptive worktree joins the exact granted
upstream. No rebase, reset, amendment, force push, other-owner write or selection
of an unfrozen upstream head occurred. Git merged the shared BUILD, REVIEW, SC,
memory and wiki-index files without conflicts. Both the adaptive Review Method
and upstream Reusable patterns sections remain; there was no manual source
conflict resolution.

The adaptive helpers, 51-question catalog, c097 executable mode and portable
invalid-input oracle remain unchanged. The upstream `patterns.py`, profile and
review implementations and generator remain unchanged. No P05/P07 schema or
policy interpretation is replaced; a pattern review supplements the existing
latest applicable content-bound review.

The six declared plugin/marketplace manifest files stage **0.13.2**, with an
unreleased changelog entry. Local refs had no 0.13.2 collision; the publication
coordinator must perform the fresh authoritative remote collision check before
publication. Existing 0.13.0/0.13.1 history and ADR-0038/0039/0040 remain.

The actual merged generator regenerated the complete native kit, then the
canonical catalog and wiki generators ran on the merged sources. No generated
body was copied from an older checkout or manually edited. Hook installation
was not requested or enabled. The resulting kit reports 172 managed files;
file integrity is not live client discovery.

## Authorized P07 transition

The original target-local reference verified before the merge:
context `d9057650-8028-439a-85da-5849b5470136`, generation 1,
`sha256:394ea169a0b9e52eb72f79e9237e52e61547a9dd53aefeaadc27bf087fc3487c`,
neutral `_default` 1.0.0.

After the merge/version preparation, verification returned actual `PROFILE_DRIFT`.
The preserved raw before/after inputs show only:

- plugin product version 0.12.0 to staged 0.13.2;
- the optional `patterns` schema block and `source` field;
- neutral `patterns.source: null`.

All existing effective values, roots, selection, required policy, compliance and
voice were compared and remained unchanged. The existing resolver performed
**one** reason-bearing rebind, preserving generation 1 and its lineage:

```json
{
  "schema_version": 1,
  "context_id": "d9057650-8028-439a-85da-5849b5470136",
  "generation": 2,
  "digest": "sha256:2db4de55f7f9a0c4f5b950fd8faca8859b7f20ecbb1621506a8e335be0aa658f",
  "name": "_default",
  "version": "1.0.0"
}
```

Fresh verification passed. Required policy remains `required: false`,
`status: not_required`, `source: bundled-neutral`, `version: 1.0.0`,
`applicability: not_applicable`; compliance is advisory with no hooks. The
private `adaptive-join-d89385f2` receipt preserves complete raw diffs, old/new
records, reason and actual results. No other target's profile was borrowed.

Old generation-1 contexts and source reviews remain historical. This transition
requires current dependent review/QA; it does not transfer their clearance.

## T11/T12 verification obligations

Keep the original map and T1-T12 acceptance. This integration uses focused
checks for actual installed-provider projection/coverage, required question
inventory, method/depth/evaluation/MARS behavior, merged native kit and
instruction/catalog/wiki/ADR consistency. Prior standalone results, including
the 23/23 successful c097 CI run, are not joined acceptance.

The coordinator designated existing independent session
`c3015de8-134b-499b-bd3d-fa14d965701b` for current joined SPEC then QUALITY review.
It is not the lost 010f0e08 context and does not inherit that verdict or its
own earlier Patterns verdict.

Current P05 preparation keeps the original P4/T11/T12 identity, generation-2
profile, explicit selected source and required QA inventory. Focused observations
can pass only after they run. The **future full hosted joined matrix**, current
canonical decisions, QA and actual corroboration remain pending, not N/A or PASS.
No local full stress suite, new pilot, model/provider experiment or new actor is
part of this preparation.

Main order remains native1a, then patterns, then adaptive. Master alone publishes,
dispatches CI, creates the PR and merges main. A later upstream CI correction
requires ordinary reconciliation and rechecking affected inputs.
