# Reusable patterns: cold handoff (2026-09-28)

**Status: local source candidate FROZEN pending the remaining gates; not released.** No release
clearance, native ADR-0028 v2 review, QA, corroboration or SHIP result exists. Nothing is pushed
and no pull request exists.

## Current frozen candidate (2026-09-28)

- Source head: `99de0741a2d338cec0a088fd35d6b5357ccfda7d`. Its runtime and test bytes are the
  ones reviewed at `d4acf3e7`.
- Reviewed head: `d4acf3e7e4557f7abd95611cff3e73c1a043dc17`.
- Reviewer 24bf5df0's `d1-m1-d4acf3e7.md` (sha256 `ecae2489…f0f1`, JSON `9b316e3b…1dd5`) found:
  - SPEC MET for A1-A7;
  - QUALITY acceptable, with no Medium or High;
  - D-1, M-1, L-1 to L-5 and I-2 closed.
- Parent Linux at `d4acf3e7`: design-contract 29/29 and document-pipeline-binding 36/36
  (`posix-d4acf3e7-d1-compound.log`, sha256 `f0308154…538f`).
- The closure commit after `d4acf3e7` is metadata only. It has no product, code or test change,
  and ticks 4.3.c and 5.2.a. It also appends the RN-16 L-6 clarification and refreshes this
  handoff and the working state.
- Open leaves: 6.2.a, 6.2.b and 6.2.c only.
- Non-blocking recorded limits:
  - I-4: the final `verify_lock` recheck is not isolated by a test.
  - I-5: the CLI edited-lock case asserts only exit code and empty stdout.
  - I-6: document-only stage checks are prose.
  - Standalone P05 is repository-only.
  - A spec that omits both `pattern_context` and the lock is undetectable by the loader.


## Historical baseline and evidence heads

This section and "Test evidence" below are historical. The current frozen, reviewed runtime is
`99de0741`, reviewed at `d4acf3e7` (see the top of this file). Later targeted tests ran on those
later heads. The records below are not rewritten.

- Branch `jokerman-microsoft-patterns-core-integration`; base (settled main) `49f2d15260f096213086f02dfeb1fae6cbe62d45`.
- Historical frozen product and docs head `fdb9f27b65359d64b343aac5b0aa0e78dc73b536`. The full
  suites and focused runs below ran on these product bytes.
- `ebd087eca0358acde8e3cfc47703e220ec5c30f3`: ledger/plan truth corrections only (plan.md 5.2.a
  wording, build-log). No product file changed from `fdb9f27b`.
- `9e56dc7944acb91fb4a1c44f81958e0348ad4953`: the six actor swarm records only. No product file
  changed from `fdb9f27b`.
- `64338b6c`: this handoff, the working-state entry and lesson L-062 (docs only).
- The RN-14 scope reconciliation commit follows `64338b6c` (docs, plan annotations and lesson
  L-063 only). Its plan annotations change the lane acceptance digests, so the `ebd087ec`-bound
  actor records are verbatim history for that acceptance and are not rebound.

## Swarm lane records (published in `9e56dc79`)

Each record is bound to the attempt `reusable-patterns-<lane>-consolidation-ebd087ec-1` and to
acceptance at `ebd087ec`. Raw digests are the actors' delivered bytes.

| Record | Actor | Raw sha256 | Committed bytes |
|---|---|---|---|
| `swarm/reports/CORE.md` | CORE owner, session 11d27634 | `190effc22bf64bc6d9e0b07018658c44d113aa6599fe2e089fad201ee2a01bd3` | identical (LF) |
| `swarm/reviews/CORE.md` | reviewer c3015de8, PASS | `81ac89fd4994258d08494a97d9eb72ac7a79f3a3bf9a5a2fb8a527d8172fc015` (CRLF) | LF-normalized, `e4d4dd5f5206d39044699e41eb59c494757e98944c54cde37af11a8d539da8ea` |
| `swarm/reports/PACK.md` | PACK owner, session 5108bc3b | `9b36a78fb41188bded9ad73181fb86c124c0dcd0a27a59092f7416482dfb490b` | identical (LF) |
| `swarm/reviews/PACK.md` | reviewer 24bf5df0, PASS | `174bc85ad8cddfc65e17245b1136047198aec36bf9941e467ec831c29485fc50` (CRLF) | LF-normalized, `385dcfcf31cac08607bfdfda79b73fd07a7b4066c7977e25b3d1f2aa2c0b3219` |
| `swarm/reports/WF.md` | WF owner, session a2f55ec5, **pending** | `4719be91a83fa8be21ae5081d9699b95d6ad37ad3079b2b7cab8c8afa7d61981` | identical (LF) |
| `swarm/reviews/WF.md` | reviewer 24bf5df0, **PENDING, non-clearing** | `cb6f1ccd3fbd27991d43be6ad15b0a585453365f84536b7f5eb3ec367a3e351b` (CRLF) | LF-normalized, `bb668e19b4b40a6fda4438db793d91a5a030a3187513de6fa94edd3a43568700` |

- The three reviews were uniformly CRLF. The repository's `*.md text eol=lf` policy stored them
  LF, so the committed review bytes are **not** byte-identical to the raw originals. The raw
  originals remain in the reviewers' session files and in session artifact
  `files\final-review\swarm-inputs-ebd087ec\reviews\`.
- Superseded `fdb9f27b`-bound versions are kept in session artifact
  `files\final-review\swarm-inputs\`: CORE report r1 `895d72ab` and r2 `7c102292`, c301 review
  `cea7831d`, and PACK report `d8dc094b`.
- Native state at `9e56dc79`:
  - `li-swarm inspect`: CORE complete, PACK complete, WF `invalid_report` (report incomplete,
    leaves, checks).
  - `verify`: `ok: false`, release clearance false. CORE and PACK are `awaiting_shared_evidence`.
  - Correct result; do not edit statuses to PASS.

## Test evidence (historical, product bytes `fdb9f27b`)

- **Linux:** strict full suite PASS, run by the coordinator. `bash tests/runner/run-all.sh
  --require-all` exit 0, 169/169 suite files, 0 skip, 0 fail, 0 partial, and 23 windows-only
  assertions N/A. Log `posix-fdb9-full-suite.log` (sha256
  `d88de0e16e4b06c039f4874287b0fda6a7a15ea04d5f540a0ae5ecbaddcd2462`), in the coordinator's files
  and in session artifact `files\final-suite\linux\`.
- **Windows strict full suite: NO VERDICT.** Session artifact `files\final-suite\`:
  - The first 7 parallel parts inherited the host environment and ran under combined load, so
    they were not CI-equivalent.
  - `i2.log`: integration 2/4 rc 1, 7 of 8 pass. `domain-installed-consumers.sh` failed its own
    guard against inherited credential variables.
  - `u1.log`: unit 1/2 rc 1, 41 of 45 pass. Failing files: `review-evidence.sh` (11 setUp
    failures, inherited Git command configuration), `cycle-footer.sh` (hang guard),
    `frontend-design-surface-hook.sh` (7.9 s against a 2 s limit) and `managed-transaction.sh`
    (one unexpected retry backoff). None of the four is in the feature diff.
  - `i1`, `i3`, `i4`, `u2`: stopped at the coordinator's decision. Partial logs are marked
    `*.INTERRUPTED.txt`. `other` never started.
  - The earlier `b8312bb7` run is interrupted, not a pass (`fullsuite-b8312bb7.log`).
- **Isolated preflights** (positive-allowlist environment, launcher `files\run-isolated.py`,
  roots under the user profile at `AppData\Local\Temp\lp64`):
  - `review_evidence.py native`: 11/11 OK. The u1 review-evidence class was environmental.
  - `domain-installed-consumers.sh`: the credential guard passed. At a 65-character fixture root,
    the test's own path budget failed at 266 characters against its limit of under 235. The
    deepest path is runtime profile history, not a pattern path. Not yet classified against a
    main-49 baseline.
  - The inherit-minus-token rerun is superseded (NOTE file); the WSL-bash-on-PATH attempt is kept
    separately.
- CORE lane checks in a clean `fdb9f27b` clone, all OK with no skips:
  - V06 PinTests 14, V07 LifecycleTests 9, MaintenanceTests 10, V08 BundleTests 6;
  - ReviewCoverageTests 5, SelectionReportTests 9;
  - `tests/unit/patterns.py` 137 and its wrapper 137, V09 31.

## Boundary deviation (operator recovery decision pending)

At about 14:33 +02 the CORE owner created `C:\lp`, a drive-root directory, contrary to L-050.
It holds fresh LF clones in `C:\lp\{pre,u1,u2,i1,i2,i3,i4,o}\r` (detached at `fdb9f27b`) and
`C:\lp\m` (branch `review-9e56dc79`).

- `iso-u1` (isolated unit 1/2) ran at `C:\lp\u1` and was stopped at 12:47:55Z through its own
  handle. Its partial log is `files\final-suite\iso-u1.log`, not a verdict.
- No process references `C:\lp`. Nothing there was deleted, cleaned up or rolled back, and no
  cleanup is authorized.
- Read-only checks and P05 contexts prepared in `C:\lp\m` are **non-clearing diagnostic history
  only**, not authorized final verification. Copies are in `files\final-review\batch-9e56dc79`
  and `files\final-review\p05-9e56dc79`.
- The earlier P05 context attempt 1 at `fdb9f27b` (content `31bebb6e…`,
  `files\final-review\context.json`) is unmodified history.
- No P05 review record, QA record, corroboration or release record was authorized or produced.

## Blockers

1. **`C:\lp`** stays untouched. No recovery or cleanup decision has been made.
2. **Windows strict suite** has no valid verdict (6.2.a). Full hosted Windows CI is required
   before main. The master authorized bounded focused reruns under `C:\Users\jokerman\lm9854`,
   with these recorded results on `fdb9f27b`:
   - `cycle-footer` rc 1 (5 s hang guard).
   - `frontend-design-surface-hook` rc 1 (3471 ms).
   - `managed-transaction` rc 0.
   - `review-evidence` interrupted, 57 ok and 0 fail, not a verdict.
   - The single main `49f2d152` baseline `domain-installed-consumers` run passed with rc 0
     (8 methods in 167 s). Attribution of the feature-head timeout stays open.

   Details:
   - The launcher starts the parent process from a positive allowlist (`run-clean-parent.ps1`).
   - `domain-installed-consumers.sh --work-dir C:/Users/jokerman/lm9854/d`: rc 1. The path budget
     held (fixture 227, kit 128). The installed worker hit the test's own 240 s timeout after 5 of
     8 methods passed, on a host at 87-94% CPU from other work. It stays red; no retry and no
     longer timeout.
   - The other focused files ran one at a time. Their logs are `files\final-suite\lm-*.log`.
3. **WF acceptance** (RN-14, RN-15, RN-16) is now closed at source/helper level, and 4.3.c and
   5.2.a are ticked. These remain separate and are not feature gates:
     - artifact QA: produced PDF text/pages (RN-05) and Word rendered pages stay unverified, and
       the C-PDF provider failure is history;
     - disclosed deferrals: the six per-consumer model/render/host cells stay unobserved.
4. **Shared Swarm profile.** The `9e56dc79` null profile is history. The parent later performed
   one genuine neutral P07 bootstrap: reference `sha256:adcea18a…fe3a`, generation 1,
   `_default` 1.0.0, bound to this worktree at `64338b6c`. Verify it is current before use, and do
   not bootstrap a second one. Swarm shared lanes still block on missing P05 review, QA and
   corroboration.
   - The actor records bound at `ebd087ec` stay verbatim history. Later plan annotations changed
     lane acceptance, and those records are not rebound.
5. **Final integrated REVIEW and SHIP** stay blocked by the remaining gates, not by WF (closed):
   - 6.2.a: Windows strict or hosted Windows CI verdict.
   - 6.2.b: final integrated P05 context, aggregate review, QA and corroboration.
   - 6.2.c.
   - Native 1a integration and current main.
   - The P07 profile, verified current at that head.
   - Evidence binding at the final head.
   At most an explicitly labelled non-clearing inspection or status record is allowed until then.
6. **Publication.** Master owns the working stored-account Git/API/CI transport. The required app PR tool still selected the EMU account and failed with 403 on the separate L-053-only attempt, so no PR was created. The final feature PR route is centrally unresolved, and no workaround is authorized. The patterns branch is not pushed because it awaits the accepted integration and CI stage, not because of a blanket Git write failure. Historical 403 logs stay verbatim.

## Next safe actions

- Do not touch `C:\lp`. No cleanup or recovery is authorized.
- There are no additional local full, stress or retry runs (Master's settled decision).
  - Windows verification is the required hosted Windows CI on the proper integrated candidate.
  - The completed one-shot main `49f2d152` baseline (rc 0) stays recorded; it is not a template
    for another local run.
- After an authorized final head exists, prepare fresh P05 contexts there. The reviewers author
  their own P05 JSON; the coordinator supplies corroboration only after actual review.
- The next steps are:
  - the native 1a preparation grant (a concrete SHA, still unissued), then an ordinary merge
    with current main;
  - `ef48d7a0` (L-053);
  - regenerating the managed outputs from source;
  - a fresh final P05 context at that head. It selects the changed `references/mockup.md` and
    the regenerated outputs, binds `plan.md` only through the work map, and freezes non-checkbox
    wording first.
- Then come the final independent aggregate review, hosted Windows CI and Master-owned
  publication.
- Keep 6.2.a-c unticked until genuinely observed.
