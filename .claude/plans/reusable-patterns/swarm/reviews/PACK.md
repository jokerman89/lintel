# Lane review: PACK (integrated head 2ce4cfcc)

Actor `copilot-session:24bf5df0-f0f7-432b-9321-3e8283e78e9e` wrote this independent local lane review. It is the original
PACK reviewer role, reused. It covers the PACK worker report whose SHA-256 is
`ca6263d71f7bca6eb31bdc485159cd32eaefb8e7dcdeb740f592cf8c000adeda` (UTF-8, LF), written by a different actor,
`copilot-session:5108bc3b-635d-4499-9601-d4680e0df88a`. The frozen integrated head is
`2ce4cfcc062e6806e0b3349d5e49a443097d4737` (tree `52900c7d562dcb5aa6a6701446e98a44645e2c0d`).

- **Intended publication path:** `.claude/plans/reusable-patterns/swarm/reviews/PACK.md`.
- **Binding source:** the binding is copied from the CORE-prepared structural input
  `PACK-2ce4cfcc.review-input.scratch.json` (SHA-256 `98e20bd1c0e7588c3aa12385d5a824727a9279ee133adb75d48da1c7513f6389`).
  That file is CORE's trusted `li-swarm review-input` output: rc 0, `ok: true`, `diagnostics: []`, with the binding under
  `review_input.binding`. It proves structural admission only. Exporting the binding is not review.
- **What I recomputed independently:**
  - `acceptance_digest` and `result_digest` with the unchanged `lib/swarm_contract.py`, read-only, against the actual CORE
    Windows worktree (`jokerman-microsoft-upgraded-doodle`). Both match; see the checks.
  - The report digest from the report's own bytes.

This record is a local observation only. It is not the P05 v2 decision, QA, corroboration, the integrated review or release
clearance. My earlier PACK review at `ebd087ec` (`reviews\PACK-ebd087ec.md`, SHA-256
`174bc85ad8cddfc65e17245b1136047198aec36bf9941e467ec831c29485fc50`) and every earlier PACK or remedial record stay
byte-identical as history. That earlier PASS is not transferred here; this verdict rests on the current acceptance and
evidence below.

<!-- lintel-swarm-evidence:v2
{
  "schema_version": 2,
  "artifact_kind": "swarm-review",
  "initiative": "reusable-patterns",
  "task_id": "PACK",
  "status": "complete",
  "reviewer": "PACK lane independent integration reviewer (read-only GitHub Copilot app session 24bf5df0)",
  "actor_ref": "copilot-session:24bf5df0-f0f7-432b-9321-3e8283e78e9e",
  "mode": "independent",
  "changed_paths": [".claude/plans/reusable-patterns/swarm/reviews/PACK.md"],
  "binding": {
    "work_map": ".claude/plans/reusable-patterns/work.json",
    "package_id": "PACK",
    "leaf_ids": ["2.1.a", "2.1.b", "2.1.c", "2.1.d"],
    "attempt_id": "reusable-patterns-PACK-integration-2ce4cfcc-1",
    "acceptance_digest": "69da45d80b8dd3cf3ee969bf29f8cbbb548d80c373c56dfc2886da88ec002608",
    "result_digest": "da046bc69bedfe18706fe1c02951fa94906319c3c7b4d51fcabbc401c012bb20",
    "report_digest": "ca6263d71f7bca6eb31bdc485159cd32eaefb8e7dcdeb740f592cf8c000adeda"
  },
  "verdict": "PASS",
  "stages": {
    "spec": "PASS",
    "quality": "PASS"
  },
  "checks": [
    {
      "name": "binding: CORE structural review-input wrapper (review_input.binding) versus the report marker, plus independent recomputation against the actual CORE Windows worktree at 2ce4cfcc",
      "status": "PASS",
      "evidence": "wrapper sha256 98e20bd1... rc 0, ok true, diagnostics []; swarm_contract.acceptance_digest(CORE worktree, coordination.json, PACK lane) = 69da45d8...2608; verify_result(CORE worktree, write_scope, report.result) ok; value_digest(result) = da046bc6...bb20; report bytes sha256 = ca6263d7...deda. acceptance_digest on the reviewer's own LF worktree at 2ce4cfcc is also 69da45d8...2608"
    },
    {
      "name": "scope content identity: 10 write_scope blobs at 2ce4cfcc versus the CORE working files, the reviewer worktree and the report result digests",
      "status": "PASS",
      "evidence": "10/10 git-show blob sha256 equals the CORE working file sha256 and result.files digests; 10/10 byte-equal to the reviewer worktree; all 10 are LF (bin/li-pattern and lib/paths.sh: i/lf w/lf attr text eol=lf); tree mode bin/li-pattern 100755 versus snapshot 100644"
    },
    {
      "name": "scope and attribution: git diff over the 10 PACK paths from 4c6ce841, ebd087ec and fdb9f27b to 2ce4cfcc; 118e3037..2ce4cfcc; log of bin/li-pattern",
      "status": "PASS",
      "evidence": "4c6ce841, ebd087ec and fdb9f27b to 2ce4cfcc: empty; 118e3037..2ce4cfcc: only bin/li-pattern +2/-1; git log 118e3037..2ce4cfcc -- bin/li-pattern: ef12c29e (CORE/INT, missing runtime exits 5) and the joins 69f208c6, 075a797d; 118e3037 and 4c6ce841 are ancestors of 2ce4cfcc"
    },
    {
      "name": "acceptance source unchanged ebd087ec..2ce4cfcc: plan 2.1.a-d card lines, spec.md, contract.md, work.json, coordination.json",
      "status": "PASS",
      "evidence": "plan 2.1.a-d: 4 lines, identical hash at ebd and 2ce, all [x]; spec, contract, work.json and coordination.json have no diff; plan.md changes are 6.2.b and other non-PACK annotations; reconciliation adds RN-14 to RN-16 plus clarifications, none amending R02, R03, R15 or 2.1.x"
    },
    {
      "name": "owner-observed PACK suites at 4c6ce841 in the actual CORE worktree (not executed by this reviewer): log hash and result lines",
      "status": "PASS",
      "evidence": "native-join/t/j-pack-origins.log sha256 5a9746f6...1297: ISOLATED head=4c6ce841 cwd=CORE worktree, Ran 13 tests, OK; native-join/t/j-launcher-roots.log sha256 97b4cb1a...ca95: ISOLATED head=4c6ce841 cwd=CORE worktree, Ran 13 tests, OK. Whole-repo git diff 4c6ce841..2ce4cfcc is 4 files (two build logs, tests/integration/pattern-portability.py, tests/unit/wiki-gen-idempotency.sh), none an input of either suite, so reuse at 2ce4cfcc is by byte identity"
    },
    {
      "name": "reviewer rerun of V14 regressions at 2ce4cfcc (reviewer worktree, plain hermetic environment rebuilt from scratch)",
      "status": "PASS",
      "evidence": "claude-home-paths.sh rc 0 (0 FAIL); memory-v2.sh rc 0 (0 FAIL); pack-resolver-fallbacks.sh rc 0, 'All 9 pack-resolver-fallbacks scenarios PASSED'; enterprise-pack-resolution.sh rc 0, 39 PASS, 0 FAIL; pack-source-target-resolution.sh rc 0, 4 PASS, 0 FAIL. Resolves the uncertainty that .claude-plugin/plugin.json (0.12.0 to 0.13.1, read by lib/profile_context.py) changed since the author's fdb9f27b runs"
    },
    {
      "name": "native integration consumption of PACK scope (source read only)",
      "status": "PASS",
      "evidence": "bin/li-copilot.py trusted source lists name lib/pack-resolver.sh, lib/paths.sh, bin/li-pattern and bin/li-pattern.py (lines 180-181 and 209-216); no change to these entries fdb9f27b..2ce4cfcc. The CORE R12 loader consumes PACK origins through patterns.build_envelope(repo, home, pack_context_from_profile(record)); design_contract, pattern_visual, patterns, li-pattern and profile_context are byte-identical d4acf3e7..2ce4cfcc, where the reviewer observed design-contract 29/0/0/0 including the real-pack compound tests (plugin.json differs, so that run is cited as supporting context, not a 2ce4cfcc run)"
    }
  ],
  "limitations": [
    "File-mode snapshot review only: the binding proves the current content of the 10 write_scope files at 2ce4cfcc, not Git attribution of one worker diff. No reviewer Git base/head was invented; this review's own path is its only changed path.",
    "The snapshot records bin/li-pattern as mode 100644; the Git tree mode at 2ce4cfcc is 100755. This is a swarm helper limitation on a core.filemode=false clone, consistent between capture and verify, and not fixed here.",
    "The PACK suites (13 origins and 13 roots) at 4c6ce841 are owner-observed by CORE/INT copilot-session:11d27634, not rerun by this reviewer. I verified the log hashes, the head and cwd lines, the result lines and whole-repo byte identity 4c6ce841..2ce4cfcc. My own earlier runs of the same suites (ebd087ec 13/13 and 13/13, awkward environment) are history.",
    "The author's fdb9f27b V14 runs are historical reuse. This reviewer reran the five V14 scripts at 2ce4cfcc in its own worktree, a separate observation whose PACK scope is byte-equal to the CORE worktree. The CORE Windows worktree itself was not used as a test root and was not written.",
    "EOL decision (a): the CORE worktree keeps CRLF working bytes for older selected history/source files (for example spec.md, prompt.md and the swarm reviews). None of the 10 PACK scope files is among them, and acceptance_digest is identical on the CORE worktree and the reviewer's LF worktree. No normalization, checkout target change or profile rebind was performed by this reviewer.",
    "ef12c29e (missing runtime exits 5, contract R12) in bin/li-pattern is CORE/INT-authored; I reviewed it at INT. It is attributed here as a post-join write in PACK scope, not PACK authorship. No PACK-owned test covers the missing-runtime path.",
    "Not run by this reviewer: pattern-pack-origins and pattern-launcher-roots at 2ce4cfcc, tests/integration/pattern-portability.py, native-command-surface, the full suite, strict run-all --require-all, kit generation or installation, and POSIX/macOS launchers. Host: Windows, Git for Windows bash/MSYS, Python 3.11.9.",
    "This local PASS covers leaves 2.1.a-d only. V09, V11, V12 portability integration, WF 4.3.c and 5.2.a closure, 6.2.a/b/c, the native grant, the shared P05 v2 context, QA, corroboration, the integrated review and release clearance remain separate gates. A later rejection overrides this record."
  ]
}
-->

## Severity counts

Critical 0 / High 0 / Medium 0 / Low 0 / Info 5.

## Specification review (2.1.a-d against the current acceptance)

The acceptance source is unchanged from `ebd087ec` to `2ce4cfcc`:
- the plan card lines 2.1.a-d are identical and all `[x]`;
- `spec.md`, `contract.md`, `work.json` and `coordination.json` have no diff;
- RN-14, RN-15 and RN-16 do not amend R02, R03, R15 or 2.1.x.

The new `acceptance_digest` comes from integration outside PACK. I recomputed it on the CORE worktree and got the bound value.

**No findings.** Per-leaf mapping, with attribution:

- **2.1.a Path helpers and roots envelope** (R02; V02, V12).
  - `lib/paths.sh` provides `lintel_patterns_dir`, `lintel_pattern_runtime_dir` and bounded, portable run IDs.
  - `bin/li-pattern` resolves the repository in the order `--repo`, then `LINTEL_REPO_ROOT`, then the Git top level, then none, with no fallback to the source bundle or `/`.
  - Outside Git, personal-only operations work and repository writes fail. The envelope crosses to Python as JSON on stdin, never through `eval`, and `CDPATH` is neutralized.
  - The report maps this to `pattern-launcher-roots` RootTests, HardeningTests, RunIdTests and AnchorTests. That suite is 13/13 OK at `4c6ce841`, owner-observed, and byte-identical to `2ce4cfcc`. The V14 path check `claude-home-paths` was rerun by me at `2ce4cfcc`: rc 0.
- **2.1.b Same-snapshot origin and ancestry transport** (R02, R03; V05, V14).
  - Origins come from the one existing ADR-0029 profile record. `lib/pack-resolver.sh` and `lib/profile_context.py` have no PACK change.
  - Inherited, child-null, own-block and fallback origins are covered, as is drift on a pointer change or a missing cached origin. The report maps this to `pattern-pack-origins` OriginTests and DriftTests: 13/13 OK, owner-observed.
  - The existing accessors are unchanged: `enterprise-pack-resolution` 39 PASS and `pack-resolver-fallbacks` 9/9, both rerun by me at `2ce4cfcc`.
- **2.1.c Neutral `patterns.source: null`, source-aware registry and JSON bridge** (R02, R03; V05).
  - The field is present in `packs/_default/pack.yaml` and documented in `lib/pack-schema.yaml`.
  - A declared but missing catalog is unavailable, and an ancestry catalog included by the repository stays at PACK scope.
  - Awkward and POSIX-spelled paths reach the core intact.
  - The mapped tests are FailureTests, DriftTests, ScopeTests and HardeningTests, all owner-observed OK. `pack-source-target-resolution` passes 4/0, rerun by me at `2ce4cfcc`.
- **2.1.d Unconfigured neutrality and visible fallback** (R02, R15; V05, V12, V14).
  - Unconfigured roots create nothing and prompt nothing. Required-policy failure and optional fallback stay visible and block dependent use, and a pack never activates personal patterns.
  - The mapped tests are NeutralTests and the outside-Git tests, owner-observed OK. `memory-v2` passes with rc 0, rerun by me at `2ce4cfcc`.

**Integration compatibility.**
- The native kit still lists the PACK runtime files as trusted sources; those entries are unchanged since `fdb9f27b`.
- The later CORE R12 loader consumes PACK origins only through the existing core `build_envelope` and `pack_context_from_profile`.
- The files on that path are byte-identical from `d4acf3e7` to `2ce4cfcc`. At `d4acf3e7` I observed the real-pack compound tests pass.
- I found no PACK-side incompatibility with the joined integration.

## Quality review

**No findings.** The PACK surface is unchanged since my earlier accepted review: one launcher, no second parser, cache or origin registry, per-call MSYS conversion suppression and structured errors. The earlier findings F4-F7, L-P1 and L-P2 remain closed.

Info:

1. **Report's V14 input statement is incomplete.** The report's limitation says the broad input directories of the V14 regressions changed only in `lib/cli-tiers.yaml` and `lib/pattern_visual.py`. That is accurate for the directories it named. It omits `.claude-plugin/plugin.json` (0.12.0 to 0.13.1), which is read by `lib/profile_context.py:478` and is therefore a transitive input to `pack-source-target-resolution`. `bin/li-run` and `bin/li-copilot.py` also changed, though they are not V14 inputs. My reruns at `2ce4cfcc` resolve this; the report is not wrong in substance.
2. **ef12c29e attribution.** The report attributes the only post-lane-head change in PACK scope to CORE/INT, correctly. Git log confirms it.
3. **File-mode quirk.** The snapshot records `100644` against a tree mode of `100755` for `bin/li-pattern`. This is retained and is not a PACK defect.
4. **EOL.** The CRLF working bytes kept under decision (a) are outside PACK scope. The PACK binding is EOL-invariant here: the same acceptance and result on both worktrees.
5. **Evidence labels.** The owner-observed, historical and readback labels in the report are honest and consistent with the logs I checked. The report also states that the author ran no test for this attempt.

## Verification and limitations

My evidence is under my session files, `swarm-consolidation\`:
- `checks-2ce\` holds `summary.log` and the five V14 logs.
- The binding recomputation was read-only against the CORE worktree, and I made no writes there.

My worktree was switched to `2ce4cfcc` with an ordinary detached switch and is clean. My scratch environment root has been removed.

I wrote nothing to source, branches, the CORE worktree, shared clones, P05, audit or the ledger. I contacted no other session except the parent.

The limitations are listed in full in the marker. The canonical shared decision will be the lane's P05 v2 JSON, prepared later by the coordinator with genuine current context, QA and corroboration; it binds this raw record without self-hashing. The WF lane, the host gates and the global close remain separately gated.
