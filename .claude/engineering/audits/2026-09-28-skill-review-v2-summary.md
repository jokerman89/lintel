# Skill and agent review summary

Original review: 2026-09-28. Post-native delta assessment: 2026-09-29.

**Advisory assessment, updated against the landed native skills and agents delivery.**
That delivery is a separate implementation, not execution of this review's portfolio
recommendations. This summary approves no removals, policy changes or release and
claims no competitive superiority.

## Revisions and method

| Evidence | Revision or scope |
|---|---|
| Original review baseline | [`49f2d15260f096213086f02dfeb1fae6cbe62d45`](https://github.com/jokerman89/lintel/tree/49f2d15260f096213086f02dfeb1fae6cbe62d45) |
| Post-native source pin | [`394ed0b801f2665cb299fb19a6d4597d20ab7c1d`](https://github.com/jokerman89/lintel/tree/394ed0b801f2665cb299fb19a6d4597d20ab7c1d), version 0.13.0; tree `10d2c47c180befb97ebefb7cdfa939bdd67b3307` |
| Comparison | [Original baseline through the post-native pin](https://github.com/jokerman89/lintel/compare/49f2d15260f096213086f02dfeb1fae6cbe62d45...394ed0b801f2665cb299fb19a6d4597d20ab7c1d), including intervening main changes, not only the native feature branch |
| Canonical coverage at that baseline | 96 skills and 69 agents |
| Canonical inventory at the post-native pin | The same 96 skills and 69 agents; all 165 canonical bodies are unchanged after frontmatter, comparing Git content |
| Native Copilot surface | 15 skill wrappers and three profiles at the original baseline; 96 complete native skill files and 72 profiles at the post-native pin |
| Landing | Authorized ordinary fast-forward to main; there is no native-delivery pull request number |
| Hook delivery | Deferred to a separate delivery; the post-native pin still installs no Copilot hook adapter or repository hook registration |

The comparison includes the intervening presentation merges #110, #111 and #112
through `1cf7d0997594a9963f413adef5ee2bb59068677d`. They are not evidence of native
skill acceptance. This summary is pinned to `394ed0b8`, not to a moving claim about
all subsequent main changes.

The assessment read every canonical skill and agent, followed selected references,
helpers and tests, compared current primary-source methods, and subjected the
synthesis to a separate challenge. It distinguishes source review, mechanical
checks and observed model behavior.

The original review checked coverage, source citation locations and the generated
catalog. This delta assessment compared committed files, inventory mappings and
existing acceptance records. It did not rerun a generator, product test suite,
host session or model benchmark.

### Evidence levels for the native delivery

**Source and generator contract.** Every canonical skill has its corresponding
`.github/skills/li-<name>/SKILL.md`; all 69 canonical agents have generated profiles,
plus the three orchestration profiles. There is no missing canonical-to-native
path in this pin. The generator iterates the canonical inventory rather than using
96 as a permanent limit. Canonical methods remain single-source; the generated
files add a host preamble and transform invocation, tool spelling and links.
The [landed Copilot contract](https://github.com/jokerman89/lintel/blob/394ed0b801f2665cb299fb19a6d4597d20ab7c1d/shims/copilot/COPILOT.md)
defines skill-relative reference paths, the source-root runner and dropped metadata.

**Recorded CLI observations.** The
[committed acceptance record](https://github.com/jokerman89/lintel/blob/394ed0b801f2665cb299fb19a6d4597d20ab7c1d/.claude/plans/native-client-parity/evidence/copilot-acceptance.md)
reports Windows 11, `gpt-5-mini`, and two routes: `--plugin-dir` and a vendored kit.
CLI 1.0.89-5 discovered all 96 skills, including `li-pause`, and delivered the complete
generated `li-cycle` body at `fd15197974908c457a495c98aeae53bdb7937c32`.
CLI 1.0.90-0 listed all 72 generated agent types on both routes at
`f6009076648ae7f5bd275f0868eedc74d2ca6696`. One plugin agent, `li:CodeReviewer`,
was selected with its declared tools; kit-route agent selection was not exercised.

The generated skill and agent files are byte-identical between those observation
revisions and the post-native pin. This delta assessment also recomputed the
committed plugin `li-cycle` body: 26,770 bytes after the recorded frontmatter
envelope removal, matching the acceptance record's corrected hash. It did not
replay or newly inspect the private host events.

**Existing hosted verification.** The landing confirmation reports
[CI run 36516745619](https://github.com/jokerman89/lintel/actions/runs/36516745619):
23 of 23 jobs successful, 489 strict test-file invocations, and no failures, skips
or partial results. These are the reported native-delivery results, not tests run
by this documentation change. Candidate-era pending statements in the build/review
records are historical; they were not relabeled as results from this assessment.

**Unobserved scope.** Whole-body equality was observed for `li-cycle`, not for every
skill; inventory discovery is not execution coverage. Installed-plugin/marketplace
installation, Copilot App, IDE and cloud acceptance remain unobserved for this
delivery. Selecting a declared tool subset is not a test of read-only enforcement.
The original file-reader size problem does not establish a hard 20 KB native
skill-body limit.

## Review findings and delta status

**Fixed** below closes only the named delivery or documentation gap at the pinned
revision. **Still valid** means the relevant source or evidence gap remains.
**Deferred** names an unimplemented capability or unobserved acceptance layer;
it is not a waiver or a passed control.

| Finding or recommendation | Baseline evidence | Current disposition |
|---|---|---|
| Pointer-based loading requires a second read of the canonical workflow | Original Copilot wrappers | **Fixed at the delivery layer:** all native bodies are generated completely; recorded full-body CLI delivery covers `li-cycle` on both routes, not all workflow behavior |
| Native entry points expose only a subset of the canonical inventory | Original 15 wrappers and three profiles | **Fixed for source mapping and recorded CLI discovery:** 96 skills and 72 profiles; `fix`, `verify`, `diagnose` and `pause` all have native files |
| Wrapper/canonical routing guidance is stale | Original adapter and handoff template | **Fixed for the inspected Copilot contract:** native invocation, source-relative references and regeneration are documented; other-client parity is not inferred |
| Canonical agent tools are not exposed as native profiles | Original three orchestration profiles | **Fixed for canonical declarations:** all 69 tool lists are preserved. The three orchestration profiles still declare no subset; enforcement acceptance is **deferred** |
| Copilot lifecycle-hook delivery and activation need separate evidence | Landed adapter, migration guide and `hooks_installed: false` | **Deferred:** no Copilot hook adapter or repository registration in this delivery |
| Generic generation, persona and internal-primitive front doors obscure the core workflow | All-item source review; canonical bodies unchanged | **Still valid as a recommendation:** no portfolio reduction or extraction was implemented |
| Task-duration and full-code planning prescriptions need reassessment | PLAN lines 32, 134 and 641-645; unchanged canonical body | **Still valid as a recommendation:** accepted rules remain in force, with no behavioral rewrite |
| Package/ad-hoc review wording diverges from the shared method | BUILD, REVIEW, cross-check and code-review methods; unchanged bodies | **Still valid:** no adaptive-review implementation is credited to this pin |
| REVIEW/SHIP helper-source fallbacks conflict with the trusted-source boundary | REVIEW lines 290 and 406; SHIP lines 115, 143, 282 and 393 | **Still valid and open:** generation preserves the canonical snippets; the supplied runner does not remove the fallback paths |
| Lessons and reusable guidance need demonstrated downstream benefit | Baseline lesson/memory methods and staged evaluation direction | **Still valid:** no later reuse implementation or outcome evidence is assumed |
| A matched task comparison has not established superior outcomes or lower overhead | Existing evaluation direction and limited pilots | **Still valid:** source size, discovery, successful CI and delivery fidelity do not establish a productivity gain |

## Proposed direction (not approved)

The assessment recommends preserving project intent, observable acceptance, scoped
execution, independent review, delivery authority and reliable cross-session
recovery, with organization policy and task-relevant knowledge in governed packs.
Correct native delivery is a prerequisite for evaluating those methods fairly.

The proposed simplification targets redundant public entry points, not useful contracts:

- Merge generic wrappers into their existing owners while preserving their callers,
  outputs and authorization boundaries.
- Move specialized document, design, customer and regulatory methods out of the
  neutral default only where an owned, usable replacement exists.
- Preserve real provider checks, independent critics and domain-specific failure
  reasoning. A short primitive can be valuable without a separate public skill.
- Keep read-only observation, diagnosis, authorized repair and publication distinct,
  even if they share a command family.

The original dispositions were proposals, not deletion quotas:

| Surface | Keep | Tighten | Merge | Extract | Retire |
|---|---:|---:|---:|---:|---:|
| Skills | 7 | 43 | 28 | 12 | 6 |
| Agents | 10 | 24 | 22 | 13 | 0 |

These counts describe the original baseline only. They do not imply that the
proposed target catalog exists or that all reviewers agreed on every placement.
The per-item inventory is not part of this summary; these aggregate counts are not
a publicly auditable list of removal instructions. Reviewers disagreed on retaining
`Planner`, `DocWriter` and `ChangelogMaintainer` as named agents versus transferring
their methods into existing workflows. Independent reviewers also split on `Explorer` and
`ReadOnly`. Independent `CodeReviewer` capability is retained in the recommendation.
Any retirement requires preserved behavior and an explicit caller migration.

## Decisions not implemented by this summary

1. Select a compact default surface and owned destinations for consolidated methods.
   No mass deletion or new pack is authorized by this document.
2. Decide whether to replace the hard task-duration rule with outcome, interface,
   authority and rollback boundaries. Existing accepted decisions must be amended
   explicitly if that direction is adopted.
3. Use the existing question catalog and Review Method for adaptive depth. Required
   controls cannot disappear through risk scoring; optional unexamined questions
   must not be presented as passes.
4. Test the cost and benefit of evidence bindings themselves. Prefer verified native
   platform evidence where it provides equivalent guarantees, without assuming it
   covers local uncommitted work, policy drift or cross-host recovery.
5. Run a small matched comparison before a large rewrite: native agent plus project
   intent, Spec Kit and Lintel, with equal task/model/tool/policy conditions. Measure
   accepted outcomes, defects, false positives, recovery, operator effort and actual
   resource use rather than document count or source length.

## Sources and preservation

The existing accepted architecture is the constraint until deliberately changed:
[work packages](https://github.com/jokerman89/lintel/blob/49f2d15260f096213086f02dfeb1fae6cbe62d45/.claude/decisions/0026-hybrid-work-packages.md),
[operation and evidence contract](https://github.com/jokerman89/lintel/blob/49f2d15260f096213086f02dfeb1fae6cbe62d45/.claude/decisions/0028-universal-operation-and-evidence-contract.md),
[required profile context](https://github.com/jokerman89/lintel/blob/49f2d15260f096213086f02dfeb1fae6cbe62d45/.claude/decisions/0029-required-profile-context.md),
and [shared Review Method](https://github.com/jokerman89/lintel/blob/49f2d15260f096213086f02dfeb1fae6cbe62d45/.claude/decisions/0036-mars-multi-model-review.md).

For the supported integration, the assessment considered
[Spec Kit at c00dc055](https://github.com/github/spec-kit/tree/c00dc0551583428a10a94443c58c6a41e5e0138c).
That comparison informs hypotheses, not proof of Lintel's relative performance.
Other comparative research is outside this summary. Required attribution remains
intact. Agent metadata and same-filename comparisons do not establish complete
authorship or license provenance.

## Delta-check and publication boundary

The source comparison preserved the original 165-item review inventory and found
no canonical body changes. Checks covered native path completeness, tool-declaration
mapping, observation-to-landed native-file equality, the recorded `li-cycle` hash,
the 0.13.0 manifests and absence of the deferred hook adapter/registration.
The summary's counts, pinned repository links, formatting and selected privacy
patterns are checked separately from product acceptance.

This report is the only proposed file change. Original private reports remain
unchanged. It contains no private paths, session correspondence, raw host logs or
unpublished branch evidence. It neither repairs findings nor clears publication
of any other artifact. Final document review and publication belong to the normal
integration process; no independent approval of this updated summary is claimed here.
