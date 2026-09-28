# Agent report: PACK

Actor `copilot-session:5108bc3b-635d-4499-9601-d4680e0df88a` wrote this report. The identity and
result are copied from the consolidation snapshot at frozen head
`ebd087eca0358acde8e3cfc47703e220ec5c30f3` (`snapshot_file_sha256`
`45a42d4916159ae68c888a2bbaf6f6f37432d2f0cb7eddfb6f63bfbcafa11d99`). That snapshot is file-mode evidence of current content, not
Git attribution. Intended publication path: `.claude/plans/reusable-patterns/swarm/reports/PACK.md`.

**Rebind only.** This supersedes attempt `reusable-patterns-PACK-consolidation-fdb9f27b-1`,
whose report (SHA-256 `d8dc094b89339be2fcc39a1de1ec26752ed0ba0890367a11b34e1254973b26a9`) is kept
unchanged as history for fdb.
- The accepted plan wording changed between the two heads (`plan.md` 5.2.a PENDING text and `build-log.md`), so only `attempt_id` and `acceptance_digest` differ.
- Product bytes, the result object, `result_digest` and every check are unchanged.
- The checks cite test runs at `fdb9f27b65359d64b343aac5b0aa0e78dc73b536`; nothing was rerun at `ebd087ec`.

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
  "attempt_id": "reusable-patterns-PACK-consolidation-ebd087ec-1",
  "acceptance_digest": "9abd9e74a0f955b2191ee4b134b8f92fd9eed256af035f857c1c40c71d60dbf4",
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
        "name": "V02/V12 lane portion: pattern-launcher-roots.sh RootTests (5), HardeningTests (4), RunIdTests (1), AnchorTests (2) at fdb",
        "status": "PASS",
        "evidence": "bash tests/unit/pattern-launcher-roots.sh at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536: Ran 13 tests, OK, rc 0"
      },
      {
        "name": "V14 paths: bash tests/shape/claude-home-paths.sh at fdb",
        "status": "PASS",
        "evidence": "rc 0, 19 PASS lines, 0 FAIL"
      }
    ],
    "2.1.b": [
      {
        "name": "V05: pattern-pack-origins.sh OriginTests.test_inherited_parent_origin_and_same_snapshot_ancestry, test_child_block_and_explicit_null_replace_the_parent and DriftTests (4) at fdb",
        "status": "PASS",
        "evidence": "bash tests/unit/pattern-pack-origins.sh at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536: Ran 13 tests, OK, rc 0"
      },
      {
        "name": "V14 existing accessors: bash tests/unit/enterprise-pack-resolution.sh at fdb",
        "status": "PASS",
        "evidence": "rc 0, 39 PASS lines, 0 FAIL"
      },
      {
        "name": "V14 existing fallbacks: bash tests/unit/pack-resolver-fallbacks.sh at fdb",
        "status": "PASS",
        "evidence": "rc 0, All 9 pack-resolver-fallbacks scenarios PASSED"
      }
    ],
    "2.1.c": [
      {
        "name": "V05: pattern-pack-origins.sh OriginTests neutral/legacy, FailureTests.test_declared_missing_catalog_is_unavailable, DriftTests.test_adding_the_neutral_field_invalidates_stored_contexts, ScopeTests.test_repository_include_of_any_ancestry_catalog_stays_pack_scope at fdb",
        "status": "PASS",
        "evidence": "bash tests/unit/pattern-pack-origins.sh at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536: Ran 13 tests, OK, rc 0"
      },
      {
        "name": "JSON bridge with spaces/quoting: pattern-launcher-roots.sh RootTests.test_git_top_level_from_a_subdirectory_with_awkward_paths and HardeningTests.test_posix_spellings_of_awkward_input_paths_reach_the_core at fdb",
        "status": "PASS",
        "evidence": "bash tests/unit/pattern-launcher-roots.sh at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536: Ran 13 tests, OK, rc 0"
      },
      {
        "name": "source/target separation: bash tests/integration/pack-source-target-resolution.sh at fdb",
        "status": "PASS",
        "evidence": "rc 0, 4 PASS lines, 0 FAIL"
      }
    ],
    "2.1.d": [
      {
        "name": "V05: pattern-pack-origins.sh FailureTests required/fallback and ScopeTests.test_personal_patterns_are_never_activated_by_a_pack at fdb",
        "status": "PASS",
        "evidence": "bash tests/unit/pattern-pack-origins.sh at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536: Ran 13 tests, OK, rc 0"
      },
      {
        "name": "V12 lane portion: pattern-launcher-roots.sh NeutralTests.test_unconfigured_roots_create_nothing_and_prompt_nothing, RootTests outside-Git/explicit-repo and HardeningTests.test_outside_git_home_is_the_profile_context_not_a_repository at fdb",
        "status": "PASS",
        "evidence": "bash tests/unit/pattern-launcher-roots.sh at git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536: Ran 13 tests, OK, rc 0"
      },
      {
        "name": "V14 memory: bash tests/unit/memory-v2.sh at fdb",
        "status": "PASS",
        "evidence": "rc 0, 16 PASS lines, 0 FAIL"
      }
    ]
  },
  "checks": [
    {
      "name": "file-mode snapshot readback: SHA-256 of the 10 write_scope files in git-archive export of fdb9f27b65359d64b343aac5b0aa0e78dc73b536 equals snapshot.result.files digests",
      "status": "PASS",
      "evidence": "10/10 match"
    },
    {
      "name": "bash tests/unit/pattern-pack-origins.sh at fdb export",
      "status": "PASS",
      "evidence": "Ran 13 tests, OK, rc 0"
    },
    {
      "name": "bash tests/unit/pattern-launcher-roots.sh at fdb export",
      "status": "PASS",
      "evidence": "Ran 13 tests, OK, rc 0"
    },
    {
      "name": "existing V14 regressions at fdb export: claude-home-paths.sh, memory-v2.sh, pack-resolver-fallbacks.sh, enterprise-pack-resolution.sh, pack-source-target-resolution.sh",
      "status": "PASS",
      "evidence": "all rc 0, 0 FAIL"
    }
  ],
  "limitations": [
    "Evidence level is a file-mode snapshot of current content at fdb9f27b; it is not Git attribution of a worker diff. Git mode refuses the historical lane ranges because bin/li-pattern changed after the lane head.",
    "bin/li-pattern at fdb includes CORE/INT commit ef12c29e (missing runtime exits 5, contract R12). This actor did not write that change. The fdb reruns exercise the file, but no PACK test covers the missing-runtime path.",
    "The snapshot records bin/li-pattern as mode 100644, although the index mode at fdb is 100755 (core.filemode=false clone; swarm helper limitation, not fixed here).",
    "Host: Windows, Git for Windows bash/MSYS, Python 3.11, jq 1.8.2 (process-local PATH). This actor ran no POSIX or macOS launcher.",
    "Not run at fdb: the full suite, strict run-all --require-all, the kit, and core tests (patterns.sh). At 44c6b176, tests/shape/native-command-surface.sh returned rc 1; it was not rerun and its generated inventories belong to CORE/INT.",
    "V09, V11, V12 portability integration, P6, installation generation, the shared P05 v2 review, independent review and final release are separate and not claimed here.",
    "L-P2: the old invoking-environment failure could not be reproduced on this host because a shared MSYS /tmp mount is pinned by an unrelated process.",
    "Host load stretched test durations (1294 s and 965 s). After the run, three partly cleaned harness temp directories created by this run in the invoking TEMP were removed.",
    "The tests ran in a git archive export of fdb inside this session's files, not in the shared clone. db7f6df1 was a review-only object and was never promoted.",
    "Metadata-only rebind from attempt reusable-patterns-PACK-consolidation-fdb9f27b-1 (acceptance 5f5a8514...5113; report sha256 d8dc094b..., kept byte-identical as fdb history) to this attempt at ebd087eca0358acde8e3cfc47703e220ec5c30f3. git diff fdb9f27b..ebd087ec changes only .claude/plans/reusable-patterns/plan.md (5.2.a PENDING wording, 1 line) and build-log.md; card lines 2.1.a-d and all 10 write_scope files are byte-identical, and the result object and result_digest da046bc6... are equal to the fdb snapshot. The listed checks are the existing fdb9f27b runs; they are not new runs at ebd087ec and no test was rerun for this rebind."
  ]
}
-->

## Changed files

Nine owned paths were changed in PACK commits by this actor. `lib/pack-resolver.sh` is in scope
but unchanged; no adapter was needed. `lib/profile_context.py` was not touched.

- `lib/paths.sh`: adds `lintel_patterns_dir` and `lintel_pattern_runtime_dir`, with portable run-ID rules (F7).
- `bin/li-pattern`: the Bash launcher, covering the roots envelope, logical-path `CDPATH= cd --` (F4), known-option native path conversion (F5), per-call MSYS conversion suppression (L-P1) and the F6 profile context comments. At fdb this file also contains CORE/INT commit `ef12c29e`; see below.
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
"pattern check unavailable". This actor did not author it. The other 8 owned paths at fdb have the
same blobs as at lane head `118e3037`.

## Checks

These are the existing fdb9f27b runs, reused unchanged because product bytes are identical at ebd087ec. All checks were run by this actor in a synthetic environment, on a `git archive` export of `fdb9f27b65359d64b343aac5b0aa0e78dc73b536`
placed in this session's files. The SHA-256 of all 10 scoped files matched the snapshot digests.

- `bash tests/unit/pattern-pack-origins.sh`: PASS, Ran 13 tests, OK, rc 0.
- `bash tests/unit/pattern-launcher-roots.sh`: PASS, Ran 13 tests, OK, rc 0.
- `bash tests/shape/claude-home-paths.sh`: PASS, rc 0, 19 PASS lines.
- `bash tests/unit/memory-v2.sh`: PASS, rc 0, 16 PASS lines.
- `bash tests/unit/pack-resolver-fallbacks.sh`: PASS, all 9 scenarios.
- `bash tests/unit/enterprise-pack-resolution.sh`: PASS, rc 0, 39 PASS lines.
- `bash tests/integration/pack-source-target-resolution.sh`: PASS, rc 0, 4 PASS lines.
- The mapping from leaves to test classes is under `leaf_results`.

Earlier evidence at lane heads (session files `head-44c6.log`, `lp1.log`, `lp2.log`, `lp3.log`, `pack-lane-report.md`) is historical and is not rebound here.

## Findings

- None open in PACK scope. Review findings F4-F7, L-P1 and L-P2 were closed by independent review `24bf5df0`. F1-F3 were closed on the CORE side.

## Limitations

- Evidence level is a file-mode snapshot of current content at fdb9f27b; it is not Git attribution of a worker diff. Git mode refuses the historical lane ranges because bin/li-pattern changed after the lane head.
- bin/li-pattern at fdb includes CORE/INT commit ef12c29e (missing runtime exits 5, contract R12). This actor did not write that change. The fdb reruns exercise the file, but no PACK test covers the missing-runtime path.
- The snapshot records bin/li-pattern as mode 100644, although the index mode at fdb is 100755 (core.filemode=false clone; swarm helper limitation, not fixed here).
- Host: Windows, Git for Windows bash/MSYS, Python 3.11, jq 1.8.2 (process-local PATH). This actor ran no POSIX or macOS launcher.
- Not run at fdb: the full suite, strict run-all --require-all, the kit, and core tests (patterns.sh). At 44c6b176, tests/shape/native-command-surface.sh returned rc 1; it was not rerun and its generated inventories belong to CORE/INT.
- V09, V11, V12 portability integration, P6, installation generation, the shared P05 v2 review, independent review and final release are separate and not claimed here.
- L-P2: the old invoking-environment failure could not be reproduced on this host because a shared MSYS /tmp mount is pinned by an unrelated process.
- Host load stretched test durations (1294 s and 965 s). After the run, three partly cleaned harness temp directories created by this run in the invoking TEMP were removed.
- The tests ran in a git archive export of fdb inside this session's files, not in the shared clone. db7f6df1 was a review-only object and was never promoted.

## Downstream notes

- File snapshots prove current content and existence, not a Git diff or actor identity.
- This v2 record is a local observation, not the P05 v2 review. Closing the lane needs an independent reviewer, whose actor_ref must differ from this report's, plus CORE/INT's shared context, QA and live verification.
- The upgrade that adds neutral `patterns.source: null` changes the manifest digest. Stored contexts fail closed until an explicit, reasoned rebind.
