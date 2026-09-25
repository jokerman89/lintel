# P04 final bounded component recheck

## Decision and scope

**Reviewed product: `aa736513ffebf469cd2df355bbce5e139b03e206`.**
**Specification: PASS. Quality: PASS. Bounded P04 component: ACCEPT.**
F04 and F05 are closed; the earlier F01-F03 closures remain valid. New or regressed
in-scope findings: **P0: 0, P1: 0, P2: 0, P3: 0**.

This is the requested same-reviewer repair closure, not another broad audit.
Specification rechecks and preservation checks passed before the affected quality
stage. The full bounded component decision combines the full-delta review recorded
in `3b2ab1237a3ae37b63fe63d729b38795fbd056c1` with inspection and independent
verification of the six-path repair. I did not implement any product change.

**A22.7 remains OPEN.** This acceptance does not close final Swarming, Universal,
shared-contract integration, independent actor corroboration or unrun client
behavior. Historical merge acceptance remains separate and unchanged.

## Exact references

| Role | Exact reference |
|---|---|
| Product under review | `aa736513ffebf469cd2df355bbce5e139b03e206` |
| Immediate parent / repair base | `28fc0dfcc5fd703237e944369951b41b2d90c183` |
| Previous product with F04/F05 | `dca635df2b3e3ddb89e29a8c73a7d04d52f5a632` |
| Previous independent recheck | `3b2ab1237a3ae37b63fe63d729b38795fbd056c1` |
| First component rejection | `6bf86c3c77d6e61701aa710d421324a7618fcc11` |
| Accepted historical merge | `e74849db6b33c7b93baadb86206009cb9f9eb6d5` |
| Historical merge review | `4bf5315d4636206f1df6a5f0c7a68a52e9341cae` |
| Later builder evidence-only child | `39ebc2689ee5c92fa804da72b4bad4b95d8f2bf5` |

The last ref changes only `reports/P04.md`, with the reviewed product as its
parent. I read that evidence-only diff without checking it out or substituting it
for the product. Its ten postcommit checks are builder evidence, not my runs.
The eventual commit containing this review is also not the reviewed product.

The cumulative component range is `e74849d..aa736513`: the same 30 bounded paths
enumerated in the previous review. The immediate repair changes exactly:

```text
.claude\plans\universal-implementation\reports\P04.md
docs\concepts\swarming-work.md
lib\swarm_contract.py
lib\swarm_snapshot.py
skills\swarm\SKILL.md
tests\unit\swarm-contract.py
```

No builder/master/source branch was reset or edited. Review took place in a new
clean detached snapshot pinned to the product; prior review worktrees and their
three report commits were preserved. The only authored repository artifact is
this report.

## Finding dispositions

| Finding | Disposition | Current code and evidence |
|---|---|---|
| F01, P1: hard-linked authority/ownership | CLOSED, retained | `lib/swarm_contract.py:129,158`. The current full Swarm suite reran actual hard-link cases for both actors, directory scopes, reducer descendants and cross-lane ownership. The previous independent red/green and same-file proofs remain recorded in `P04-recheck.md`; no claim that string aliases alone establish physical separation. |
| F02, P1: YAML constructor diagnostic leakage | CLOSED, retained | `lib/envelope_contract.py:80`. Current full Forge and non-quiet validator cases reject malformed bool/int/float/timestamp/empty scalars without the forbidden marker or traceback in output/audit. Default JSON works under `python -S`; unavailable optional YAML fails lazily and explicitly. The envelope implementation is unchanged by this repair. |
| F03, P2: discarded root package boundaries | CLOSED, retained | `lib/swarm_contract.py:421`. Current Swarm tests retain root-file, root-directory, quoted/new-path and explicit-boundary positives, unrelated-scope negatives and unknown/malformed-limit fail-closed behavior. |
| F04, P2: content-only result identity | CLOSED | `lib/swarm_snapshot.py:39,69,80,140,168,206,222`. Real Git index modes, filesystem type and exact link-target data now participate in capture and verification. Both original actual-CLI failures revoke completion; supported newly reviewed results remain usable. Details below. |
| F05, P2: completed unmapped package blocked | CLOSED | `lib/swarm_contract.py:582-590,1208-1250`. Both frontier and close resolve known unmapped packages from their original members and prerequisites. Mapped packages still require valid report/review state. Actual-CLI positive and negative controls pass. |

### F04 independent replay

The previous-product red control again accepted staged/committed index-only
`100644 -> 100755` and replacement of a regular file by a real same-content
`os.symlink("copy.py", ...)`: public `verify` returned exit 0. The repaired product
returns exit 1 for both, with stale result evidence rather than an unrelated
invalid fixture accounting for the rejection.

On the repaired product I also verified:

- An unchanged result, restored original mode/type, and a newly captured/reviewed
  `100755` result pass. A stale declared head cannot capture the changed mode.
- Newly reviewed native file-only links and actual committed Git `120000` objects
  pass. The record contains `type`, `mode`, an exact target-byte SHA-256 and target
  text, not the target file's content digest.
- Replacing a Git link by an ordinary file fails with `core.symlinks=true`.
  With `core.symlinks=false`, a file containing the exact target text preserves
  the reviewed Git link object. Changing `copy.py` to `./copy.py` fails even
  though both resolve to the same destination; restoring the exact text passes.
- A real Windows directory link is one data entry. A read guard on its target
  subtree proves that capture does not read target contents. Target-body text is
  absent from the snapshot.
- Outside-root targets and staged or recorded Git `160000` entries fail.
  Removing the unsupported entry restores valid evidence. This is an explicit
  unsupported boundary, not fabricated submodule support.
- Unrelated commits and UTF-8 LF/CRLF equivalents do not invalidate the unchanged
  scoped result.

The final consolidated independent replay completed with exit 0. Earlier
reviewer-harness attempts needed Windows fixture corrections: avoid doubled CRLF,
compare regular-file hashes after the documented normalization, and construct
native directory-link targets with Windows separators. Those harness failures
were not product findings; the corrected controls were rerun successfully.

Old content-only evidence cannot silently acquire missing type/mode metadata.
It requires recapture and review; historical reports remain unmodified history.

### F05 independent replay

The previous product reproduced the exact asymmetry: checked-complete unmapped
P0 blocked P1's `wave` and `verify`, while the equivalent original T0 dependency
passed. At the repaired ref both package and leaf forms pass.

Twelve independently constructed current-product cases exercised the public
`validate`, `wave` and `verify` boundaries. They cover both equivalent positive
forms; an incomplete second member; unknown direct and package prerequisites;
a cycle between checked unmapped packages; complete and incomplete transitive
prerequisites; mapped but unreviewed, validly reviewed and failed-review
prerequisites; and an unresolved original-leaf prerequisite hidden behind a
checked status. Every negative blocks dispatch and close with the relevant
prerequisite diagnostic. Merely checking a mapped package's leaves does not
replace its report/review.

This is derived readiness over original authoritative leaves and dependencies,
not a new package-status store, replacement backlog or dispatcher.

## Quality stage

The affected quality review passes. I inspected the complete typed snapshot
implementation, package aggregation and recursive dependency resolution, actual
capture/report/review/frontier/close consumers, new tests and the two approved
documentation paragraphs against the earlier full component review.

File classification precedes content reads; link identity is target data rather
than dereferenced content. Committed and working Git results share the same
type/mode/target representation, with the Windows index-mode and link-file
semantics explicit. Unsupported entries fail rather than inheriting clearance.
Cycle detection and unknown prerequisites fail closed, and both readiness
consumers reuse the same dependency logic.

The documentation describes the supported links and excluded submodules rather
than removing links to cure stale type evidence. No product regression, scope
expansion or false final-acceptance claim was found in this bounded repair.
`reports/P04.md` still records the prior rejection and pending reviewer decision;
this report supplies that new decision without rewriting the earlier outcomes.

## Audit and leaf results

SW-01/04/06 ownership, coordinator/reducer protection and reviewer-only changes
remain accepted locally. SW-02 package parsing and readiness now pass together.
SW-05 and A21 retain the real rich-brief/strict-envelope/validation/evaluation/
audit-before-output path. SW-03's local result identity is repaired, but its
shared trust and actor-corroboration part remains open under A22.7.

| Leaf | Spec | Quality | Evidence and boundary |
|---|---|---|---|
| A22.1.a | PASS | PASS | Exact recorded merge parents and required ancestries retained |
| A22.1.b | PASS | PASS | Accepted hybrid/session source and current coordinator authority preserved |
| A22.1.c | PASS, preservation | PASS, preservation | Enterprise/helper sources unchanged; prior actual Universal map/consumer evidence retained; no new client matrix claimed |
| A22.1.d | PASS | PASS | All 76 inventory destinations/modes retained; historical artifacts unchanged |
| A22.2 | PASS | PASS | Main ADR0026 preserved, original Swarming body retained in ADR0027, 27 unique ADR numbers |
| A22.3.a | PASS | PASS | Direct/ancestor/alias/physical-hard-link ownership cases retained |
| A22.3.b | PASS | PASS | Both actors, reducers, cross-lane negatives and actual Git reviewer-diff gates |
| A22.4.a | PASS | PASS | Flat/phased/tree/numeric/Spec Kit and legacy singleton tests |
| A22.4.b | PASS | PASS | Membership/order/scope/review-depth checks plus F05 original-member/prerequisite closure |
| A21.1 | PASS | PASS | Explicit opt-in call path remains; no automatic dispatcher or hook activation |
| A21.2 | PASS | PASS | Invalid/forbidden payload and YAML constructor failures block before payload release/audit |
| A21.3 | PASS | PASS | Actual Swarm CLI producer preserves rich Markdown and structured handoff fields |
| A21.4 | PASS | PASS | Earlier accessor/evaluator/error/source-root checks retained; current missing-parser and audit-error/fail-open-receipt checks pass |
| A22.5 | PASS | PASS | Existing attempt/acceptance/report/no-change cases plus F04 actual type/mode/link identity |
| A22.6 | PASS, component | PASS, component | Genuine Git isolation/fan-in/conflict/interruption and declared serial/manual paths; former F04/F05 blockers removed |
| A22.7 | OPEN / excluded | OPEN / excluded | Shared P05-v2/P07/P08/P09 binding and independent integrated verification still required |

## Checks actually executed at this product

Tests ran sequentially with synthetic temporary repositories, homes, state and
audit directories, bytecode disabled, user/system Git configuration excluded and
fixture hooks disabled. No network, dependency installation, private configuration,
global activation or nested agents were used. Existing Python 3.11, Git/Git Bash
and optional PyYAML were used. The specifically approved jq 1.8.2 executable's
SHA-256 was rechecked; only the test process PATH was extended.

| Independent reviewer execution | Actual result |
|---|---|
| `python -B -S tests\unit\swarm-contract.py` | 56 tests PASS, no unittest skips; 83.160 s |
| Consolidated independent F04 real-Git/public-CLI probe | PASS, including newly reviewed modes/links, exact-target identity, no-dereference witness and unsupported-boundary controls |
| Independent F05 old/new public-CLI probe | Old package/leaf asymmetry reproduced; all twelve repaired-product cases PASS |
| `python -B -S tests\integration\swarm-workflow.py` | Both mapped/legacy and genuine Git worktree/fan-in/recovery scenarios PASS; 22.000 s |
| Five selected `brief-forge-boundary.py` cases below | 5 tests PASS, no skips; 62.268 s |
| Git-object ancestry/inventory/full unchanged-tree comparisons | PASS; details below |
| Repair-range and `e74849d..aa736513` `git diff --check` | PASS |
| Post-test exact HEAD and worktree status | Exact reviewed product, clean before writing this report |

The five current Brief Forge selectors were:

```text
BriefForgeBoundaryTests.test_actual_swarm_cli_brief_reaches_the_shared_handoff_boundary
BriefForgeBoundaryTests.test_yaml_scalar_constructor_failures_are_sanitized_at_public_boundaries
BriefForgeBoundaryTests.test_standard_library_default_and_missing_optional_yaml_parser
BriefForgeBoundaryTests.test_audit_failure_has_no_success_shaped_output
BriefForgeBoundaryTests.test_fail_open_audit_return_without_persistence_cannot_release
```

The previous independent review at `dca635d` executed all 15 Brief Forge cases,
both six-scenario retained shell suites, three shape checks, actual Universal
work-map validation and the full bounded quality inspection. Those are retained
prior evidence, not relabeled as new runs. Unchanged sources and the current
affected-consumer tests support continuity. The builder's 56/15 and postcommit
ten-case reports are likewise separate from the reviewer executions above.

## Preservation

The historical merge still has exactly these parents:
`21261f1ff76be994246060a7817924f2893f2454` and
`275a35447c4ad271e05816ade43ac48f1acec24f`.
Main `28061e434be455ca02f135b73244eaf4f73f3a69`, original Swarming, the merge,
`8ea0fc4`, `02be6cb`, `dca635d` and the exact repair parent remain ancestors.
The original Swarming branch still resolves to its recorded head.

The 76 inventory rows exactly match the original
`e9911fcd448dc632bf2752c69304d2be80b7aa65..275a354` source-delta path set.
Every destination exists with its retained file kind/mode, including the ADR
rename. All 23 historical Swarming plan/brief/report/review paths are exact
blob/mode matches to the accepted merge. Main ADR0026 is byte-identical, and the
original Swarming ADR body from `## Context` is retained in ADR0027. The tree has
27 unique ADR numbers.

For the reported 39-path shared-authority/source preservation claim, I used a
stronger whole-tree check rather than guessing an unpublished 39-row membership:
**all 821 pre-existing paths outside the exact 30-path owned component delta are
byte/mode-identical to `e74849d`**. This includes the 32 existing memory,
Universal-audit and Universal-plan authority paths enumerated in the prior
review and the unchanged enterprise/helper/hybrid/generated sources. The number
39 is not presented as a separately enumerated reviewer manifest.

No historical outcome was fabricated, no old report was amended to certify this
attempt, and no shared plan/memory/reducer was changed. The three earlier reviewer
worktrees remained clean at their original report commits.

## Remaining limits and final seam

This is Windows execution. Real native symlinks and actual Git index-mode changes
ran; the conditional POSIX filesystem-chmod branch did not run. The absence of
unittest skips does not establish POSIX validation. Submodule snapshots remain
unsupported by explicit contract.

The genuine Git integration uses real commits, isolated worktrees, actor-change
diffs, interrupted review, scoped untracked-addition rejection, conflict recovery
and ancestry-preserving fan-in. Its worker/reviewer identities are synthetic
declarations, not independently corroborated agents or humans. Native/sequenced/
manual capability flags are caller declarations, not host capability probes.
File-only snapshots do not prove a Git base diff or native isolation.

A22.7 must still bind the final P05-v2 review/control/QA contract, P07 effective
profile reference, P08 selected-work/operation identity and P09 domain-result
envelope, with separate host/human corroboration and final integrated review.
Combined-tree regeneration, joined enterprise/hybrid/swarm checks, strict full
suite and fresh/client behavior validation remain coordinator-owned gates.
No final Swarming or Universal acceptance, publication or remote action is implied.
