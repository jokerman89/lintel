# Legacy cleanup integration state

**Status:** implementation in progress; not reviewed or released.
**Updated:** 2026-09-25.
**Host/routing session:** e9c20b62-f877-4242-82cd-b5002d452da8.
**Workspace project-session identifier:** e9d7470d-278c-4d7a-8a73-e1fd7a108ece.

## Authority and current barrier

The selected map is [work.json](work.json); [plan.md](plan.md) owns original leaf IDs.
The operator released implementation at 09:08 CEST. Parent coordination and upstream
ownership remain as recorded in spec.md and swarm/charter.md.

Initial clean HEAD was `d285a33283ec90341b79f3d093d1e9ca6a1504ce`. Topology was committed
as `6b75a43463c4b4d78df4fd8e9a130bbe0cc4d39a`, then corrected for the generated showcase
exclusion, W2's actual underscore-named behavioral test, and distinct actor namespaces.
Validators passed before dispatch and after corrections.

PR #93 moved to `b7b245fac0c84fb86d9558c4f523d6a6218640c4` but was still open/draft with
hosted checks running at the last observation. This is not an ownership thaw.
Do not integrate worker commits, edit frozen paths or regenerate outputs until the
parent relays verified merged main. Then explicitly rebase this isolated branch onto
that main before serial fan-in. Preserve the worker branches and worktrees.

## Attributable implementation lanes

| Lane | App routing session | Branch | State |
|---|---|---|---|
| W1 | 7a4e21ae-488c-456a-a2e3-350459607d36 | jokerman-microsoft-native-planning-consolidation | Coordinator-preserved commit `556e4ea18968028daf413e5c435ee74a88a854fe`; acceptance pending |
| W2 | 10c8fef1-69f2-497a-9f07-f4dc60965172 | jokerman-microsoft-native-quality-workflows | Coordinator-preserved commit `2af909a802533ed93fdb0c64224994ae6c74d4ae`; acceptance pending |
| W3 | 750acb1b-2dff-4a5d-b4cb-d48fbc7903eb | jokerman-microsoft-continuity-workflow-consolidation | Implementing owned scope |
| W4 | 76bdc4fe-168f-4544-8364-754356d820a6 | jokerman-microsoft-browser-design-consolidation | Coordinator-preserved commit `da4a3d160de1a300e51e777710e19d8eb6ba1515`; acceptance pending |
| W5 | b8d0a9b2-2c45-4662-ac0f-df0cf8d7fe20 | jokerman-microsoft-native-installation-guards | Implementing owned scope; narrowed alias edit accepted |
| W6 | ddc03556-684b-4165-9fa9-939fb8043dea | jokerman-microsoft-native-documentation-migration | Original source scope finished; report/snapshot in progress; no extra audit ownership |

W1's exact 21 paths and W4's exact 44 precommit paths passed coordinator scope checks;
both indexes were empty and their base HEADs matched before preservation. W4's report
bytes matched its reported SHA-256. No worker report is promoted to independent clearance.
Git detects four W4 moves, so its preservation commit reports 40 changed paths, not a
loss of the separately checked 44-path precommit add/delete inventory.
W2's 28 precommit paths and report hash passed scope/attribution checks. Git detects
two moves, so its preserved commit lists 26 changes. All 69 useful agent roles remain.

First independent reviewer: `1742f900-1de4-4a59-beee-95c3a907a063`, Cleanup capability
review. It reads preserved W1/W2/W4 commits plus coordinator `4deae9c8` as a preliminary
specification/capability comparison only. No fan-in, frozen edits or final clearance.
Reuse it for the actual reconciled spec review; the separate quality reviewer has not
started. Presentation reservation authority and historical-record classification
corrections were supplied as explicit later overlays, not silently changed inputs.

## Coordinator changes and observations

Implemented current cycle ranges, explicit confirmation/owned recovery, native review
walkthrough, help-to-catalog filters, audience-to-role mode and historical identity
migration guidance. Retained old checkpoint preferences while using neutral commit
metadata and pause/resume routes. Joined inspect in the native reader, removing only
external automatic import; old native audit/history bytes stay readable. Updated
catalog categories, event producer, current emitted commands and named integration
test consumers. Twenty ordinary audit narratives now carry explicit historical
terminology banners; raw bound evidence/provenance subtrees were not rewritten.

Actual local observations, not full acceptance:

- `python -I -B tests/unit/native-route-consolidation.py`: 7/7 source checks passed.
- Stock `tests/shape/build-workflow-contract.sh`: all structural checks passed.
- Stock `tests/unit/cycle-skills-present.sh`: nine phases, remaining fix entry and
  all three cycle compositions passed.
- Thirteen changed Python sources parsed without importing product code.
- `node --check` passed for both changed browser integration JavaScript sources.
- `git diff --check` and the explicit frozen-path diff check passed.
- Repository-local profile bootstrap, before the later launcher restriction, observed
  `_default` 1.0.0 generation 1 under the actual host session. The whole-cycle estimator
  returned 120000, uncalibrated, zero samples. Neither grants release permission.

## Permission and evidence boundaries

W1's private/session-environment launcher was refused before execution. No copy, move,
inline recreation, tool switch or borrowed launcher may reproduce that action.
W2/W4/W5 reported separately permitted pre-update documentary red observations; W3's
pre-update interpreter-selection error ran no test. Keep those outcomes distinct.
Dynamic tests requiring the refused setup remain NOT RUN. Direct source-only checks
and the original read-only swarm metadata commands do not grant runtime QA.
Final ordinary repository CI on clean hosted checkouts remains required.

W5's delete/recreate of the alias registry was refused without deleting it. Parent
clarified only surgical in-place retirement of identified expired records, preserving
the registry/path/schema/unrelated data. The host accepted those limited edits.
No replay of the refused deletion is authorized.

The parent clarified that presentation paths are its scoped reservation, not a claim
that the operator enumerated those exact paths. The provisional residual register
also separates original observations/citations from actually manifest-bound evidence;
not every narrative review file is inherently immutable. Record both attribution and
classification rules in the lesson store after its freeze lifts.

## Next integration actions

1. Preserve remaining quiescent lanes after their actual path/scope checks.
2. On verified upstream merge, rebase this branch, then fan in lanes serially.
3. Join frozen resource inventories and capabilities. Add the actual freeze helper;
   point browser tests/PDF writer/install closure to canonical web-session resources.
   Fold make-pdf print options into generate-pdf, retaining writer/prepare helpers and
   never restoring the removed reader. Remove bridge-only old browser resources only
   after all real consumers are joined.
4. Finish raw-history residual register by exact path and immutable field/category;
   no blanket evidence-directory exemption and no repository-wide zero-token claim.
5. Regenerate catalogs/wiki/adapters, reconcile actual final-main version, and record
   metadata/compatibility/migration evidence. Do not edit presentation publication.
6. Obtain two separate review sessions on the integrated candidate, specification/
   capability first then quality/verification. Bind actual P05 v2 QA/review and host
   corroboration; fix substantive findings and preserve later-rejection semantics.
7. Open one aggregate PR against main through the supported tool. Require normal
   green hosted checks and review before merge, then verify remote main inclusion.
