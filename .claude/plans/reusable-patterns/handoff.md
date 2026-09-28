# Reusable patterns: cold handoff (2026-09-28)

**Status: INCOMPLETE and BLOCKED.** No release clearance, native ADR-0028 v2 review, QA,
corroboration or SHIP result exists. Nothing is pushed and no pull request exists.

## Heads and byte identity

- Branch `jokerman-microsoft-patterns-core-integration`; base (settled main) `49f2d15260f096213086f02dfeb1fae6cbe62d45`.
- Frozen product and docs head `fdb9f27b65359d64b343aac5b0aa0e78dc73b536`. All test evidence
  below ran on these product bytes.
- `ebd087eca0358acde8e3cfc47703e220ec5c30f3`: ledger/plan truth corrections only (plan.md 5.2.a
  wording, build-log). No product file changed from `fdb9f27b`.
- `9e56dc7944acb91fb4a1c44f81958e0348ad4953`: the six actor swarm records only. No product file
  changed from `fdb9f27b`.
- This handoff, the working-state entry and a lessons recurrence are one later docs commit.

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

## Test evidence (product bytes `fdb9f27b`)

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

1. **Operator recovery decision** on `C:\lp` and on any further Windows validation.
2. **Windows strict suite** has no valid verdict. A rerun needs an authorized host/root. The
   path-budget test needs an honest classification, not a workaround.
3. **WF host gates** (required, unverified; not downgraded):
   - 4.3.c PDF conversion is BLOCKED: the existing provider gave no DevTools endpoint and no PDF.
   - Word page rendering is unavailable in the host.
   - 5.2.a per-consumer model/render/host cells are unobserved for `generate-web`, `design-dna`,
     `frontend-typography`, `frontend-motion`, `frontend-shader` and `generate-app`.
4. **Shared Swarm profile:** decision (a). Profile stays null, so shared lane acceptance is
   explicitly blocked (`_verify_profile` requires a P07 reference). Do not create or bind a
   profile to turn it green.
5. **Final integrated REVIEW and SHIP** stay blocked by 1-4. At most an explicitly labelled
   non-clearing inspection or status record is allowed.
6. **GitHub write access** for the feature PR (403, unresolved; no credential changes).

## Next safe actions

- Wait for the operator's `C:\lp` and Windows host decision. Do not touch `C:\lp` until then.
- If a Windows rerun is authorized:
  - use `run-isolated.py` on fresh LF clones of `fdb9f27b` under the approved roots;
  - run u1 and u2 alone, integration parts one or two at a time, and `other` alone;
  - classify any persistent failure against settled main `49f2d152` before calling it a feature
    finding.
- After an authorized final head exists, prepare fresh P05 contexts there. The reviewers author
  their own P05 JSON; the coordinator supplies corroboration only after actual review.
- Keep 4.3.c, 5.2.a and 6.2.a-c unticked until genuinely observed.
