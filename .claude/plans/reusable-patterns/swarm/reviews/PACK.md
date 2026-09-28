# Lane review: PACK

Actor `copilot-session:24bf5df0-f0f7-432b-9321-3e8283e78e9e` wrote this independent local lane review. It covers the PACK
worker report whose SHA-256 is `9b36a78fb41188bded9ad73181fb86c124c0dcd0a27a59092f7416482dfb490b`, at frozen head
`ebd087eca0358acde8e3cfc47703e220ec5c30f3` (tree `831bfe8157f599ca127b853284d29084c0e52d7f`). Intended publication path:
`.claude/plans/reusable-patterns/swarm/reviews/PACK.md`.

This record is a local observation only. It is not the P05 v2 decision, QA, corroboration or the integrated review. The
binding below was derived with native `li-swarm.py review-input` in my own scratch export, with the report placed at its
intended path. It returned `ok: true` with 0 diagnostics. Exporting input is not review; the review content follows.

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
    "attempt_id": "reusable-patterns-PACK-consolidation-ebd087ec-1",
    "acceptance_digest": "9abd9e74a0f955b2191ee4b134b8f92fd9eed256af035f857c1c40c71d60dbf4",
    "result_digest": "da046bc69bedfe18706fe1c02951fa94906319c3c7b4d51fcabbc401c012bb20",
    "report_digest": "9b36a78fb41188bded9ad73181fb86c124c0dcd0a27a59092f7416482dfb490b"
  },
  "verdict": "PASS",
  "stages": {
    "spec": "PASS",
    "quality": "PASS"
  },
  "checks": [
    {
      "name": "native review-input binding in reviewer-owned scratch git-archive export of ebd087ec with the report at its intended path",
      "status": "PASS",
      "evidence": "LINTEL_SOURCE_ROOT=<scratch> python -I -B bin/li-swarm.py review-input --repo . --coord .claude/plans/reusable-patterns/swarm/coordination.json --task PACK: rc 0, ok true, 0 diagnostics; binding equals the supplied attempt, acceptance, result and report digests"
    },
    {
      "name": "result readback: SHA-256 of git cat-file blob ebd087ec:<path> for all 10 write_scope files equals result.files digests",
      "status": "PASS",
      "evidence": "10/10 match"
    },
    {
      "name": "scope and attribution: git diff 118e3037..ebd087ec over the 10 PACK scope paths; fdb9f27b..ebd087ec overall",
      "status": "PASS",
      "evidence": "PACK scope differs from lane head 118e3037 only in bin/li-pattern (+2/-1), from CORE/INT commit ef12c29e (missing-runtime exit 5); fdb..ebd changes only plan.md (1 line) and build-log.md; PACK scope is byte-identical from b8312bb7 to ebd087ec"
    },
    {
      "name": "bash tests/unit/pattern-pack-origins.sh at ebd087ec (reviewer hermetic environment with awkward TEMP/HOME)",
      "status": "PASS",
      "evidence": "Ran 13 tests, OK, rc 0 (339 s)"
    },
    {
      "name": "bash tests/unit/pattern-launcher-roots.sh at ebd087ec (reviewer hermetic environment with awkward TEMP/HOME)",
      "status": "PASS",
      "evidence": "Ran 13 tests, OK, rc 0 (363 s), including real junction, CDPATH/dash, POSIX spelling, plain-root opaque value, run-ID and outside-Git profile-context cases"
    },
    {
      "name": "bash tests/shape/claude-home-paths.sh at ebd087ec (awkward environment)",
      "status": "PASS",
      "evidence": "rc 0, 0 FAIL"
    },
    {
      "name": "existing V14 regressions at ebd087ec in a plain-path reviewer hermetic environment: memory-v2.sh, pack-resolver-fallbacks.sh, enterprise-pack-resolution.sh, pack-source-target-resolution.sh",
      "status": "PASS",
      "evidence": "all rc 0; enterprise 39 PASS / 0 FAIL; all 9 pack-resolver-fallbacks scenarios passed; source-target 4 PASS / 0 FAIL; memory-v2 0 FAIL"
    },
    {
      "name": "post-join CORE/INT launcher missing-runtime change (ef12c29e) as consumed by PACK scope: reviewer INT probes f/h at fdb9f27b (same bin/li-pattern bytes as ebd)",
      "status": "PASS",
      "evidence": "probes_int.py 8/8 OK at fdb; Python below 3.10 and a missing runtime with a lock both exit 5 with empty stdout and 'pattern check unavailable', never 'no patterns'; attributed to CORE/INT, not PACK"
    }
  ],
  "limitations": [
    "File-mode snapshot/review only: the binding proves current content of the 10 write_scope files at ebd087ec, not Git attribution of one worker diff. Git mode refuses the historical lane ranges because bin/li-pattern later received CORE/INT commit ef12c29e. No reviewer Git base/head was invented.",
    "The snapshot records bin/li-pattern as mode 100644, but the index mode at ebd087ec is 100755 (swarm helper limitation on a core.filemode=false clone; consistent between capture and verify; not fixed by this review).",
    "Substantive review history is my earlier separate records: db7f6df1 (F1-F7), 44c6b176 closure, 5e2ba144 L-P1, 118e3037 L-P2, INT b8312bb7 and INT closure fdb9f27b. They are cited, not rehashed. db7f6df1 was a review-only object and was never promoted.",
    "ef12c29e (missing runtime exits 5, contract R12, L-N1) is CORE/INT-authored. I reviewed it at INT; it is attributed here only as a post-join write in PACK scope, not PACK authorship. No PACK-owned test covers it; the portability integration test and my INT probes do.",
    "In my awkward-path environment (TEMP/HOME containing sp'a$c(e)&), memory-v2, pack-resolver-fallbacks, enterprise-pack-resolution and pack-source-target-resolution fail. The same four fail with the same signatures at launch base ae9d6df7 (before any PACK change). This is a pre-existing old-caller limitation outside PACK scope, not repaired and not a PACK regression; the plain-path reruns pass.",
    "Host: Windows only, Git for Windows bash/MSYS, Python 3.11.9, LongPathsEnabled=0. No POSIX or macOS launcher observed by this reviewer.",
    "Not run: full suite, strict run-all --require-all, the full kit, and core patterns.sh. Those, WF's 4.3.c/5.2.a host cells, V17, P05 shared context/QA/corroboration, the integrated review and release clearance remain separate gates. This local PASS does not clear them."
  ]
}
-->

## Severity counts

Critical 0 / High 0 / Medium 0 / Low 0 / Info 5.

## Specification review

No findings. The four leaves are covered on the actual combined code at `ebd087ec`.

- **2.1.a** Path helpers and roots envelope (R02; V02, V12).
  - `lib/paths.sh` adds `lintel_patterns_dir` and `lintel_pattern_runtime_dir`, with portable, bounded run IDs. Device names, a trailing dot, a leading dash and more than 128 characters are refused with a one-line error that does not echo the input (closed F7).
  - `bin/li-pattern` resolves the repository in the order `--repo`, then `LINTEL_REPO_ROOT`, then the Git top level, then none. There is no source-bundle fallback.
    - Outside Git, personal-only operations work and repository writes fail.
    - Linked repository and home anchors are refused with `invalid_roots` (exit 2).
    - `CDPATH='' cd --` is used, and native paths are converted only for known path options.
    - All covered by `pattern-launcher-roots` 13/13 at ebd.
- **2.1.b** Same-snapshot origin and ancestry transport (R02, R03; V05, V14).
  - Origins come from the single existing ADR-0029 profile record. `lib/pack-resolver.sh` and `lib/profile_context.py` are unchanged.
  - Inherited, child-null, own-block and fallback origins are covered, as are drift on a pointer change and drift on a missing cached origin. Covered by `pattern-pack-origins` 13/13.
  - Existing accessors are unchanged: `enterprise-pack-resolution` 39 PASS and `pack-resolver-fallbacks` 9/9 in the plain-path environment.
- **2.1.c** Neutral `patterns.source: null` and the JSON bridge (R02, R03; V05).
  - Present in `packs/_default/pack.yaml` and documented in `lib/pack-schema.yaml`.
  - A declared but missing catalog is unavailable, not empty success.
  - An ancestry catalog included explicitly by a repository stays at PACK scope.
  - Awkward and POSIX-spelled paths reach the core intact.
  - The public upgrade notice is in `docs/concepts/patterns.md:80-83`: every bound profile drifts until an explicit, reason-bearing rebind, and there is no automatic rebind (F3 disclosure, INT).
- **2.1.d** Unconfigured neutrality and visible fallback (R02, R15; V05, V12, V14).
  - Unconfigured roots create no files, prompts or runtime churn. Required-policy failures and optional fallback stay visible and block dependent patterns.
  - A pack never activates personal patterns.
  - Outside Git, `LINTEL_HOME` is the P07 profile context and `repository` is null (F6).
  - Memory and path regressions pass.

## Quality review

No findings. The code is simple and bounded: one launcher, no second parser, cache or origin registry, per-call MSYS conversion suppression and structured errors. My earlier Low findings (L-P1, L-P2) are closed.

Info:

1. **ef12c29e attribution.** The only in-scope change after lane head `118e3037` is `ef12c29e`, authored by CORE/INT. The worker report attributes it correctly and discloses that no PACK test covers it.
2. **File mode.** The snapshot records mode `100644` against index mode `100755` for `bin/li-pattern`. This is a tool limitation and consistent between capture and verify.
3. **Guard status.** The report says `native-command-surface.sh` returned rc 1 at `44c6b176`. At `fdb9f27b` I observed rc 0 with 0 findings, now that WF has joined. This is not rerun at ebd, but the relevant bytes are identical.
4. **Old-caller path limitation.** The old callers fail with an awkward TEMP/HOME, and do so identically at base `ae9d6df7`. This is pre-existing and outside PACK scope. PACK's own suites pass in that same awkward environment.
5. **PASS-line counts.** Line counts differ slightly by counting method: `claude-home-paths` shows 20 lines for me against 19 reported, and `memory-v2` 17 against 16. Both show 0 FAIL and rc 0, so there is no substantive difference.

## Verification and limitations

- My evidence (all outside the repository and read-only for source) is under my session files `swarm-consolidation\`:
  - `checks\` (awkward environment, ebd): `summary.log`, `pattern-pack-origins.log`, `pattern-launcher-roots.log`, `claude-home-paths.log`, and the four awkward-environment regression logs.
  - `checks-plain\` (plain environment, ebd).
  - `checks-ae9-awkward\` (baseline at ae9).
  - `review-input-PACK.json` and `scratch-ebd\` (own scratch export).
- The reviewer's worktree was switched to `ebd087ec` with an ordinary detached switch and stayed clean.
- I made no source, branch, shared-clone or P05 JSON writes. I did not contact other sessions beyond the parent.

This Markdown record is a local observation. The canonical shared decision is the lane's P05 v2 JSON under `.claude/runtime/reviews/`, which the coordinator will prepare with genuine lane context, QA and corroboration. It must bind this raw record without self-hashing. Later rejection overrides this local PASS. The final P08 join, the WF/host gates and the global close remain separately gated.
