# Agent report: PACK

Actor `copilot-session:5108bc3b-635d-4499-9601-d4680e0df88a` wrote this report for attempt
`reusable-patterns-PACK-integration-2ce4cfcc-1`. The identity and result are copied from the current input export at frozen
head `2ce4cfcc062e6806e0b3349d5e49a443097d4737` (tree `52900c7d562dcb5aa6a6701446e98a44645e2c0d`):

- `PACK.json` SHA-256 `239d82ea70cfffa557fe4d1b46f660213b11604ee0864e8d9ee6a2ee0f46d7c9`
- `PACK.file-snapshot.json` SHA-256 `ccc00142c0f88bab3b2dd358bbb8b7ad448692cf17ba881b8861bedef09253b7`
- `evidence-inventory.json` SHA-256 `2f8491b96847ad6e34fd60bc29ed62a8d46d44c4f69aa9033b4632512270896b`

That snapshot is file-mode evidence of current content, not Git attribution. Intended publication
path: `.claude/plans/reusable-patterns/swarm/reports/PACK.md`.

**New attempt, no new product work.**
- Supersedes `reusable-patterns-PACK-consolidation-ebd087ec-1` (report SHA-256 `9b36a78fb41188bded9ad73181fb86c124c0dcd0a27a59092f7416482dfb490b`) and, before it, the fdb attempt (report SHA-256 `d8dc094b89339be2fcc39a1de1ec26752ed0ba0890367a11b34e1254973b26a9`). Both are kept byte-identical as history.
- `scope_changes_since_ebd087ec` is empty. The result object and `result_digest` are equal to ebd; only `attempt_id` and `acceptance_digest` differ.
- The acceptance change comes from integration outside PACK scope (including P07 product version 0.13.1), not from the PACK runtime.
- Checks are either this actor's historical fdb9f27b runs, reused, or owner-observed CORE/INT runs at `4c6ce841781bd4467a2f75d3853170cadf782549`. This actor ran no test for this attempt.

<!-- lintel-swarm-evidence:v2
{
  "schema_version": 2,
  "artifact_kind": "swarm-report",
  "initiative": "reusable-patterns",
  "task_id": "PACK",
  "status": "complete",
  "worker": "PACK lane builder (lintel-builder custom agent, GitHub Copilot app session)",
  "actor_ref": "copilot-session:5108bc3b-635d-4499-9601-d4680e0df88a",
  "isolation_ref": "git-worktree:jokerman-microsoft-stunning-tribble branch jokerman-microsoft-patterns-pack-integration at lane head 118e303770cb215761918ea165a7b998091bb8ff",
  "work_map": ".claude/plans/reusable-patterns/work.json",
  "package_id": "PACK",
  "leaf_ids": [
    "2.1.a",
    "2.1.b",
    "2.1.c",
    "2.1.d"
  ],
  "attempt_id": "reusable-patterns-PACK-integration-2ce4cfcc-1",
  "acceptance_digest": "69da45d80b8dd3cf3ee969bf29f8cbbb548d80c373c56dfc2886da88ec002608",
  "result": {
    "base": null,
    "files": {
      "bin/li-pattern": {
        "digest": "e268f86bbda9648f6974dd29621d1ddc856ac2f6d95a2bc5a2ab5ae6234eeda7",
        "mode": "100644",
        "type": "file"
      },
      "lib/pack-resolver.sh": {
        "digest": "f7ebcf76b21330c3533224f51f1f8ebf7037761fd54fa528f104c2d501d7df53",
        "mode": "100644",
        "type": "file"
      },
      "lib/pack-schema.yaml": {
        "digest": "e7281fa94f4baac257811f59a68465ad10a4a5aa9e71b2ccd33364e1688862f1",
        "mode": "100644",
        "type": "file"
      },
      "lib/paths.sh": {
        "digest": "7e28ceecc10cea55871821780eb287378749c0d0b29cc192549f1577563b4f9c",
        "mode": "100644",
        "type": "file"
      },
      "packs/_default/pack.yaml": {
        "digest": "c78bc86931c63c4d4ba2b48c24e7eb6463b537b55ab4c9a5ee345205bcd2ec97",
        "mode": "100644",
        "type": "file"
      },
      "tests/unit/pattern-launcher-roots.py": {
        "digest": "2902850d44f154a2f077bd31f520b06bdd4ba66c36ffd525c84e353624a74cd5",
        "mode": "100644",
        "type": "file"
      },
      "tests/unit/pattern-launcher-roots.sh": {
        "digest": "3deb022df46a9731a224ee8b731a3d54d52fc31a0c9e21ea665b62e3190bdca0",
        "mode": "100644",
        "type": "file"
      },
      "tests/unit/pattern-pack-origins.py": {
        "digest": "be7df9aedac5e5a363a5c3642f975dacfda3c29ae12d99795afeb69cb4b0bb90",
        "mode": "100644",
        "type": "file"
      },
      "tests/unit/pattern-pack-origins.sh": {
        "digest": "999ecd88bd83f4cbd359336338120e49cf977eea7dfc4c3180fb6051758a1ffb",
        "mode": "100644",
        "type": "file"
      },
      "tests/unit/pattern_pack_harness.py": {
        "digest": "b760b8e2832f0758de0a93194334016e04ac4df8f1050157dfe3e03777a1cd23",
        "mode": "100644",
        "type": "file"
      }
    },
    "head": null,
    "kind": "files"
  },
  "result_digest": "da046bc69bedfe18706fe1c02951fa94906319c3c7b4d51fcabbc401c012bb20",
  "changed_paths": [
    "bin/li-pattern",
    "lib/paths.sh",
    "packs/_default/pack.yaml",
    "lib/pack-schema.yaml",
    "tests/unit/pattern-pack-origins.sh",
    "tests/unit/pattern-pack-origins.py",
    "tests/unit/pattern-launcher-roots.sh",
    "tests/unit/pattern-launcher-roots.py",
    "tests/unit/pattern_pack_harness.py",
    ".claude/plans/reusable-patterns/swarm/reports/PACK.md"
  ],
  "leaf_results": {
    "2.1.a": [
      {
        "name": "V02/V12 lane portion: pattern-launcher-roots RootTests (5), HardeningTests (4), RunIdTests (1), AnchorTests (2) at 4c6ce841, owner-observed",
        "status": "PASS",
        "evidence": "owner-observed (CORE/INT integration owner copilot-session:11d27634-94dc-4a1a-8453-602cd1dbf84b, not this actor): bash tests/unit/pattern-launcher-roots.sh at 4c6ce841781bd4467a2f75d3853170cadf782549, log native-join/t/j-launcher-roots.log sha256 97b4cb1a355c6b27e5dcb003d6659f15554642e356d7e2f7b60b53998915ca95: Ran 13 tests, OK, rc 0. PACK scope and pattern runtime have zero Git delta 4c6ce841..2ce4cfcc; this is reuse by byte identity, not a rerun at 2ce4cfcc"
      },
      {
        "name": "same tests at fdb9f27b, reused historical run by this actor",
        "status": "PASS",
        "evidence": "historical run by this actor, reused: bash tests/unit/pattern-launcher-roots.sh at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536 (log swarm-consolidation-fdb.log in this actor's session files): Ran 13 tests, OK, rc 0. Not rerun for this attempt"
      },
      {
        "name": "V14 paths: tests/shape/claude-home-paths.sh at fdb9f27b, reused historical run by this actor",
        "status": "PASS",
        "evidence": "historical run by this actor, reused: bash tests/shape/claude-home-paths.sh at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536 (log swarm-consolidation-fdb.log in this actor's session files): rc 0, 19 PASS lines, 0 FAIL. Not rerun for this attempt"
      }
    ],
    "2.1.b": [
      {
        "name": "V05: pattern-pack-origins OriginTests.test_inherited_parent_origin_and_same_snapshot_ancestry, test_child_block_and_explicit_null_replace_the_parent and DriftTests (4) at 4c6ce841, owner-observed",
        "status": "PASS",
        "evidence": "owner-observed (CORE/INT integration owner copilot-session:11d27634-94dc-4a1a-8453-602cd1dbf84b, not this actor): bash tests/unit/pattern-pack-origins.sh at 4c6ce841781bd4467a2f75d3853170cadf782549, log native-join/t/j-pack-origins.log sha256 5a9746f651a950f6423be8ebcacae7e12df2caf084c3e998b8b402a3192e1297: Ran 13 tests, OK, rc 0. PACK scope and pattern runtime have zero Git delta 4c6ce841..2ce4cfcc; this is reuse by byte identity, not a rerun at 2ce4cfcc"
      },
      {
        "name": "same tests at fdb9f27b, reused historical run by this actor",
        "status": "PASS",
        "evidence": "historical run by this actor, reused: bash tests/unit/pattern-pack-origins.sh at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536 (log swarm-consolidation-fdb.log in this actor's session files): Ran 13 tests, OK, rc 0. Not rerun for this attempt"
      },
      {
        "name": "V14 existing accessors and fallbacks: enterprise-pack-resolution.sh and pack-resolver-fallbacks.sh at fdb9f27b, reused historical runs by this actor",
        "status": "PASS",
        "evidence": "historical run by this actor, reused: bash tests/unit/enterprise-pack-resolution.sh; bash tests/unit/pack-resolver-fallbacks.sh at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536 (log swarm-consolidation-fdb.log in this actor's session files): rc 0, 39 PASS lines, 0 FAIL; all 9 scenarios PASSED. Not rerun for this attempt"
      }
    ],
    "2.1.c": [
      {
        "name": "V05: pattern-pack-origins OriginTests neutral/legacy, FailureTests.test_declared_missing_catalog_is_unavailable, DriftTests.test_adding_the_neutral_field_invalidates_stored_contexts, ScopeTests.test_repository_include_of_any_ancestry_catalog_stays_pack_scope at 4c6ce841, owner-observed",
        "status": "PASS",
        "evidence": "owner-observed (CORE/INT integration owner copilot-session:11d27634-94dc-4a1a-8453-602cd1dbf84b, not this actor): bash tests/unit/pattern-pack-origins.sh at 4c6ce841781bd4467a2f75d3853170cadf782549, log native-join/t/j-pack-origins.log sha256 5a9746f651a950f6423be8ebcacae7e12df2caf084c3e998b8b402a3192e1297: Ran 13 tests, OK, rc 0. PACK scope and pattern runtime have zero Git delta 4c6ce841..2ce4cfcc; this is reuse by byte identity, not a rerun at 2ce4cfcc"
      },
      {
        "name": "JSON bridge with spaces/quoting: pattern-launcher-roots RootTests.test_git_top_level_from_a_subdirectory_with_awkward_paths and HardeningTests.test_posix_spellings_of_awkward_input_paths_reach_the_core at 4c6ce841, owner-observed",
        "status": "PASS",
        "evidence": "owner-observed (CORE/INT integration owner copilot-session:11d27634-94dc-4a1a-8453-602cd1dbf84b, not this actor): bash tests/unit/pattern-launcher-roots.sh at 4c6ce841781bd4467a2f75d3853170cadf782549, log native-join/t/j-launcher-roots.log sha256 97b4cb1a355c6b27e5dcb003d6659f15554642e356d7e2f7b60b53998915ca95: Ran 13 tests, OK, rc 0. PACK scope and pattern runtime have zero Git delta 4c6ce841..2ce4cfcc; this is reuse by byte identity, not a rerun at 2ce4cfcc"
      },
      {
        "name": "same tests at fdb9f27b plus source/target separation, reused historical runs by this actor",
        "status": "PASS",
        "evidence": "historical run by this actor, reused: bash tests/unit/pattern-pack-origins.sh; bash tests/unit/pattern-launcher-roots.sh; bash tests/integration/pack-source-target-resolution.sh at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536 (log swarm-consolidation-fdb.log in this actor's session files): 13 OK; 13 OK; rc 0, 4 PASS lines, 0 FAIL. Not rerun for this attempt"
      }
    ],
    "2.1.d": [
      {
        "name": "V05: pattern-pack-origins FailureTests required/fallback and ScopeTests.test_personal_patterns_are_never_activated_by_a_pack at 4c6ce841, owner-observed",
        "status": "PASS",
        "evidence": "owner-observed (CORE/INT integration owner copilot-session:11d27634-94dc-4a1a-8453-602cd1dbf84b, not this actor): bash tests/unit/pattern-pack-origins.sh at 4c6ce841781bd4467a2f75d3853170cadf782549, log native-join/t/j-pack-origins.log sha256 5a9746f651a950f6423be8ebcacae7e12df2caf084c3e998b8b402a3192e1297: Ran 13 tests, OK, rc 0. PACK scope and pattern runtime have zero Git delta 4c6ce841..2ce4cfcc; this is reuse by byte identity, not a rerun at 2ce4cfcc"
      },
      {
        "name": "V12 lane portion: pattern-launcher-roots NeutralTests.test_unconfigured_roots_create_nothing_and_prompt_nothing, RootTests outside-Git/explicit-repo and HardeningTests.test_outside_git_home_is_the_profile_context_not_a_repository at 4c6ce841, owner-observed",
        "status": "PASS",
        "evidence": "owner-observed (CORE/INT integration owner copilot-session:11d27634-94dc-4a1a-8453-602cd1dbf84b, not this actor): bash tests/unit/pattern-launcher-roots.sh at 4c6ce841781bd4467a2f75d3853170cadf782549, log native-join/t/j-launcher-roots.log sha256 97b4cb1a355c6b27e5dcb003d6659f15554642e356d7e2f7b60b53998915ca95: Ran 13 tests, OK, rc 0. PACK scope and pattern runtime have zero Git delta 4c6ce841..2ce4cfcc; this is reuse by byte identity, not a rerun at 2ce4cfcc"
      },
      {
        "name": "same tests at fdb9f27b plus V14 memory, reused historical runs by this actor",
        "status": "PASS",
        "evidence": "historical run by this actor, reused: bash tests/unit/pattern-pack-origins.sh; bash tests/unit/pattern-launcher-roots.sh; bash tests/unit/memory-v2.sh at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536 (log swarm-consolidation-fdb.log in this actor's session files): 13 OK; 13 OK; rc 0, 16 PASS lines, 0 FAIL. Not rerun for this attempt"
      }
    ]
  },
  "checks": [
    {
      "name": "file-mode readback by this actor for this attempt (read-only, not a test): SHA-256 of the 10 write_scope blobs at 2ce4cfcc062e6806e0b3349d5e49a443097d4737 (git show from the read-only integrated worktree) equals snapshot.result.files digests",
      "status": "PASS",
      "evidence": "10/10 match; git diff 4c6ce841..2ce4cfcc, ebd087ec..2ce4cfcc and fdb9f27b..2ce4cfcc over the 10 paths are empty; worktree HEAD 2ce4cfcc tree 52900c7d, porcelain status empty"
    },
    {
      "name": "bash tests/unit/pattern-pack-origins.sh at 4c6ce841, owner-observed",
      "status": "PASS",
      "evidence": "owner-observed (CORE/INT integration owner copilot-session:11d27634-94dc-4a1a-8453-602cd1dbf84b, not this actor): bash tests/unit/pattern-pack-origins.sh at 4c6ce841781bd4467a2f75d3853170cadf782549, log native-join/t/j-pack-origins.log sha256 5a9746f651a950f6423be8ebcacae7e12df2caf084c3e998b8b402a3192e1297: Ran 13 tests, OK, rc 0. PACK scope and pattern runtime have zero Git delta 4c6ce841..2ce4cfcc; this is reuse by byte identity, not a rerun at 2ce4cfcc"
    },
    {
      "name": "bash tests/unit/pattern-launcher-roots.sh at 4c6ce841, owner-observed",
      "status": "PASS",
      "evidence": "owner-observed (CORE/INT integration owner copilot-session:11d27634-94dc-4a1a-8453-602cd1dbf84b, not this actor): bash tests/unit/pattern-launcher-roots.sh at 4c6ce841781bd4467a2f75d3853170cadf782549, log native-join/t/j-launcher-roots.log sha256 97b4cb1a355c6b27e5dcb003d6659f15554642e356d7e2f7b60b53998915ca95: Ran 13 tests, OK, rc 0. PACK scope and pattern runtime have zero Git delta 4c6ce841..2ce4cfcc; this is reuse by byte identity, not a rerun at 2ce4cfcc"
    },
    {
      "name": "bash tests/unit/pattern-pack-origins.sh and pattern-launcher-roots.sh at fdb9f27b export, reused historical runs by this actor",
      "status": "PASS",
      "evidence": "historical run by this actor, reused: both launchers at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536 (log swarm-consolidation-fdb.log in this actor's session files): 13 OK each, rc 0. Not rerun for this attempt"
    },
    {
      "name": "existing V14 regressions at fdb9f27b export (claude-home-paths.sh, memory-v2.sh, pack-resolver-fallbacks.sh, enterprise-pack-resolution.sh, pack-source-target-resolution.sh), reused historical runs by this actor",
      "status": "PASS",
      "evidence": "historical run by this actor, reused: the five V14 scripts at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536 (log swarm-consolidation-fdb.log in this actor's session files): all rc 0, 0 FAIL. Not rerun for this attempt. fdb9f27b..2ce4cfcc changes lib/cli-tiers.yaml and lib/pattern_visual.py among lib/, packs/, bin/_context.sh and these test files; none of them references either file directly"
    }
  ],
  "limitations": [
    "Evidence level is a file-mode snapshot of current content at 2ce4cfcc062e6806e0b3349d5e49a443097d4737 (tree 52900c7d562dcb5aa6a6701446e98a44645e2c0d); it is not Git attribution of a worker diff and not a new authorship claim. No new product work was performed for this attempt.",
    "This actor ran no test for this attempt. Owner-observed checks were executed by the CORE/INT integration owner at 4c6ce841, not by this actor; this actor verified only the log SHA-256 values against evidence-inventory.json and the 13/13 OK lines. Byte identity of PACK scope and pattern runtime 4c6ce841..2ce4cfcc supports reuse; it is not a rerun at 2ce4cfcc.",
    "The fdb9f27b checks are this actor's historical runs, reused without rerun. The V14 regressions were not observed at 4c6ce841 or 2ce4cfcc by anyone in this evidence set; their broad input directories changed only in lib/cli-tiers.yaml and lib/pattern_visual.py since fdb9f27b, with no direct reference found.",
    "bin/li-pattern includes CORE/INT commit ef12c29e89f2c59da56306d28b729a442a6d8c16 (missing runtime exits 5, contract R12). This actor did not write that change, and no PACK test covers the missing-runtime path.",
    "The snapshot records bin/li-pattern as mode 100644, although the Git tree mode at 2ce4cfcc is 100755 (core.filemode=false clone; swarm helper limitation, not fixed here).",
    "Host of this actor's historical runs: Windows, Git for Windows bash/MSYS, Python 3.11, jq 1.8.2 (process-local PATH). The owner logs name the same host toolchain. This actor ran no POSIX or macOS launcher.",
    "Not run by this actor: the full suite, strict run-all --require-all, the kit, core tests and hosted CI. native-command-surface.sh returned rc 1 at 44c6b176 in this actor's lane; evidence-inventory.json reports 0 findings at 2ce4cfcc from the owner's preparation turn, which this actor did not observe.",
    "V09, V11, V12 portability integration, P6, installation generation, the shared P05 v2 review, independent review, the aggregate/final matrix and release are separate and not claimed. Source-only acceptance is not SHIP and this report carries no release clearance.",
    "L-P2: the old invoking-environment failure could not be reproduced on this host because a shared MSYS /tmp mount is pinned by an unrelated process.",
    "db7f6df1 was a review-only object and was never promoted.",
    "Rebind chain: reusable-patterns-PACK-consolidation-fdb9f27b-1 (report sha256 d8dc094b...) and reusable-patterns-PACK-consolidation-ebd087ec-1 (report sha256 9b36a78f...) are kept byte-identical as history. This attempt differs in attempt_id and acceptance_digest only; scope_changes_since_ebd087ec is empty and result/result_digest da046bc6... are equal. The acceptance change comes from integration changes outside PACK scope, including P07 product version 0.13.1, not from the PACK runtime.",
    "The version-only named profile rebind (gen2/c50efdbe..., neutral not_required) was performed by the parent coordinator. This actor did no bootstrap, rebind, profile activation or real-home access, and ran no li-swarm helper validation for this report; the marker was checked structurally only."
  ]
}
-->

## Changed files

Nine owned paths were changed in PACK commits by this actor. `lib/pack-resolver.sh` is in scope
but unchanged; no adapter was needed. `lib/profile_context.py` was not touched.

- `lib/paths.sh`: adds `lintel_patterns_dir` and `lintel_pattern_runtime_dir`, with portable run-ID rules (F7).
- `bin/li-pattern`: the Bash launcher, covering the roots envelope, logical-path `CDPATH= cd --` (F4), known-option native path conversion (F5), per-call MSYS conversion suppression (L-P1) and the F6 profile context comments. It also contains CORE/INT commit `ef12c29e`; see below.
- `packs/_default/pack.yaml`: optional neutral `patterns.source: null`.
- `lib/pack-schema.yaml`: documents the optional field.
- `tests/unit/pattern-pack-origins.{sh,py}`, `tests/unit/pattern-launcher-roots.{sh,py}` and `tests/unit/pattern_pack_harness.py`: new hermetic tests and harness.

Ordinary hook-aware commits by this actor on `jokerman-microsoft-patterns-pack-integration`:

- `7b0b246c94a6394a258cab5a0418dfca63a011d7`: from launch base `ae9d6df7aa4015661233d4b399eebbb5209b7831`; 9 files, +1015/-4.
- `d15d8664a62a94321cf9825b59edbd28e58ad71c`: authorized ordinary merge of approved CORE R7 `2fd07f003439632aa3c297a3825e5f12c712459d`. This updated the dependency baseline; it is not PACK content.
- `44c6b176ec9f834fb25499f233e380e7baa1f856`: anchor tests. `2fd07f00..44c6b176` is the same 9 files, +1058/-4.
- `5e2ba1442b5c452d9f552f4c7c8c97bd0903b4ef` (L-P1): 3 files, +52/-9.
- `660d7a32bf25f3645673b1c00d758ae401948a3d` then `118e303770cb215761918ea165a7b998091bb8ff` (L-P2): test-only.

`db7f6df1` was a review snapshot only and was never promoted.

Joins were made by CORE/INT, not this actor: `075a797d` (44c6b176), `69f208c6` (5e2ba144) and
`ba494404` (118e3037). The only content change in PACK scope after `118e3037` is CORE/INT commit
`ef12c29e89f2c59da56306d28b729a442a6d8c16` in `bin/li-pattern`: a missing runtime now exits 5 with
"pattern check unavailable". This actor did not author it. `118e3037` is an ancestor of
`2ce4cfcc`, and `git log 118e3037..2ce4cfcc -- bin/li-pattern` lists only `ef12c29e` and the two joins.
The other 8 owned paths at `2ce4cfcc` have the same blobs as at lane head `118e3037`.

## Checks

Read-only readback by this actor for this attempt (not a test):
- The SHA-256 of the 10 scoped blobs at `2ce4cfcc` matched the snapshot digests: 10/10.
- The 10 scoped paths have empty diffs from `4c6ce841`, `ebd087ec` and `fdb9f27b` to `2ce4cfcc`.
- Card lines 2.1.a-d in `plan.md` are unchanged since `ebd087ec`.
- `agent-report.template.md` and `lib/swarm_contract.py` are unchanged since `fdb9f27b`.

Owner-observed by the CORE/INT integration owner at `4c6ce841781bd4467a2f75d3853170cadf782549`, not rerun by this actor:
- `bash tests/unit/pattern-pack-origins.sh`: Ran 13 tests, OK, rc 0. `j-pack-origins.log` SHA-256 `5a9746f651a950f6423be8ebcacae7e12df2caf084c3e998b8b402a3192e1297`, matching the inventory.
- `bash tests/unit/pattern-launcher-roots.sh`: Ran 13 tests, OK, rc 0. `j-launcher-roots.log` SHA-256 `97b4cb1a355c6b27e5dcb003d6659f15554642e356d7e2f7b60b53998915ca95`, matching the inventory.
- The inventory records the `4c6ce841..2ce4cfcc` delta as two build logs, `tests/integration/pattern-portability.py` and `tests/unit/wiki-gen-idempotency.sh`. None of them is PACK scope or pattern runtime.

Historical runs by this actor, reused without rerun. They ran in a synthetic environment on a `git archive` export of `fdb9f27b65359d64b343aac5b0aa0e78dc73b536` in this session's files:
- `bash tests/unit/pattern-pack-origins.sh`: Ran 13 tests, OK, rc 0.
- `bash tests/unit/pattern-launcher-roots.sh`: Ran 13 tests, OK, rc 0.
- `bash tests/shape/claude-home-paths.sh`: rc 0, 19 PASS lines.
- `bash tests/unit/memory-v2.sh`: rc 0, 16 PASS lines.
- `bash tests/unit/pack-resolver-fallbacks.sh`: all 9 scenarios passed.
- `bash tests/unit/enterprise-pack-resolution.sh`: rc 0, 39 PASS lines.
- `bash tests/integration/pack-source-target-resolution.sh`: rc 0, 4 PASS lines.

The mapping from leaves to test classes is under `leaf_results`. Earlier lane-head evidence (`head-44c6.log`, `lp1.log`, `lp2.log`, `lp3.log`, `pack-lane-report.md`) is history and is not rebound here.

## Findings

- None open in PACK scope. Review findings F4-F7, L-P1 and L-P2 were closed by independent review `24bf5df0`. F1-F3 were closed on the CORE side.

## Limitations

- Evidence level is a file-mode snapshot of current content at 2ce4cfcc062e6806e0b3349d5e49a443097d4737 (tree 52900c7d562dcb5aa6a6701446e98a44645e2c0d); it is not Git attribution of a worker diff and not a new authorship claim. No new product work was performed for this attempt.
- This actor ran no test for this attempt. Owner-observed checks were executed by the CORE/INT integration owner at 4c6ce841, not by this actor; this actor verified only the log SHA-256 values against evidence-inventory.json and the 13/13 OK lines. Byte identity of PACK scope and pattern runtime 4c6ce841..2ce4cfcc supports reuse; it is not a rerun at 2ce4cfcc.
- The fdb9f27b checks are this actor's historical runs, reused without rerun. The V14 regressions were not observed at 4c6ce841 or 2ce4cfcc by anyone in this evidence set; their broad input directories changed only in lib/cli-tiers.yaml and lib/pattern_visual.py since fdb9f27b, with no direct reference found.
- bin/li-pattern includes CORE/INT commit ef12c29e89f2c59da56306d28b729a442a6d8c16 (missing runtime exits 5, contract R12). This actor did not write that change, and no PACK test covers the missing-runtime path.
- The snapshot records bin/li-pattern as mode 100644, although the Git tree mode at 2ce4cfcc is 100755 (core.filemode=false clone; swarm helper limitation, not fixed here).
- Host of this actor's historical runs: Windows, Git for Windows bash/MSYS, Python 3.11, jq 1.8.2 (process-local PATH). The owner logs name the same host toolchain. This actor ran no POSIX or macOS launcher.
- Not run by this actor: the full suite, strict run-all --require-all, the kit, core tests and hosted CI. native-command-surface.sh returned rc 1 at 44c6b176 in this actor's lane; evidence-inventory.json reports 0 findings at 2ce4cfcc from the owner's preparation turn, which this actor did not observe.
- V09, V11, V12 portability integration, P6, installation generation, the shared P05 v2 review, independent review, the aggregate/final matrix and release are separate and not claimed. Source-only acceptance is not SHIP and this report carries no release clearance.
- L-P2: the old invoking-environment failure could not be reproduced on this host because a shared MSYS /tmp mount is pinned by an unrelated process.
- db7f6df1 was a review-only object and was never promoted.
- Rebind chain: reusable-patterns-PACK-consolidation-fdb9f27b-1 (report sha256 d8dc094b...) and reusable-patterns-PACK-consolidation-ebd087ec-1 (report sha256 9b36a78f...) are kept byte-identical as history. This attempt differs in attempt_id and acceptance_digest only; scope_changes_since_ebd087ec is empty and result/result_digest da046bc6... are equal. The acceptance change comes from integration changes outside PACK scope, including P07 product version 0.13.1, not from the PACK runtime.
- The version-only named profile rebind (gen2/c50efdbe..., neutral not_required) was performed by the parent coordinator. This actor did no bootstrap, rebind, profile activation or real-home access, and ran no li-swarm helper validation for this report; the marker was checked structurally only.

## Downstream notes

- File snapshots prove current content and existence, not a Git diff or actor identity.
- This v2 record is a local observation, not the P05 v2 review and not release clearance. Closing the lane needs an independent reviewer, whose actor_ref must differ from this report's, plus CORE/INT's shared context, QA and live verification.
- The upgrade that adds neutral `patterns.source: null` changes the manifest digest. Stored contexts fail closed until an explicit, reasoned rebind.
