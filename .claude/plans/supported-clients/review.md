# Review — supported clients: Copilot, Claude, Codex and Cursor

**Date:** 2026-09-25 · **Branch:** `jokerman-microsoft-trim-supported-clients` · **Base:** `1981e591`
(origin/main) · **Plan:** [plan.md](plan.md) · **Decision:** ADR-0035 · **Merged:** PR #107 as
`10b0eea7` on 2026-09-27

## Verdict

PASS, and delivered. All 15 leaves are implemented and their local checks pass. The independent
review found no P0 or P1 issue, and its P2/P3 findings are resolved; one operator decision remains
under "Open". Until 2026-09-27 nothing was pushed (L-045, L-053). The branch then converged onto
#104, Go Live published it as PR #107, and #107 merged into `main` (see "Convergence onto #104"
and "Delivery").

## Environment

- Windows, Git Bash (Git for Windows 2.55.0), Python 3.11.9 with the declared PyYAML 6.0.3,
  PowerShell 7.6.6 selected through `LINTEL_POWERSHELL`.
- Every test and helper ran through a launcher that sets a synthetic `HOME`, `USERPROFILE`,
  `APPDATA`, `LOCALAPPDATA`, `HOMEDRIVE`/`HOMEPATH`, `TEMP`, `TMP`, `TMPDIR` and XDG roots under
  `%LOCALAPPDATA%\Temp\tsc`, and removes `COPILOT_*`, `GIT_*`, `GH_*`, `GITHUB_*`, `LINTEL_*`,
  `CLAUDE*` and `PYTHON*` variables before the first child starts (L-051). The MSYS `/tmp` mount
  never pointed at that root (it stayed on another session's root, later the real user temp),
  so no mount-backing directory was removed (L-049).
- jq is not used (L-046), so jq-only assertions skip. Runs are therefore non-strict; the
  strict `--require-all` suite is CI's job.
- The host was heavily loaded by other sessions, so timings are relative, not benchmarks.

## Leaf status

| Leaf | Result | Evidence |
|---|---|---|
| 1.1 registry | PASS | `li-client-capabilities.py validate`: 14 surfaces; families exactly claude, codex, copilot, cursor, other; 16 sources, 6 aliases |
| 1.2 update and doctor | PASS | `bash -n bin/li-update`; Updater tests; doctor probe-list test |
| 1.3 entry routes | PASS | three files deleted; `install/verify.sh --all` passes |
| 1.4 metadata | PASS | `li-catalog.py --check`; `frontmatter-lint-all.sh` |
| 2.1–2.5 tests | PASS | table below |
| 3.1–3.2 documentation | PASS | `li-wiki-gen --check` clean; `li-instructions.py check`; `li-copilot.py check --target . --source .` (20 managed files, `copilot-cli`); live-path scan below |
| 3.3 records | PASS | ADR-0035, M1 evolution entry, migration guide and index row (parsed by `li-lifecycle.py migrations`: `schedule: open`), changelog |
| 4.1 verification | PASS | this file |
| 4.2 compatibility audit | RED, dispositioned | `.claude/engineering/compat-audits/2026-09-25-supported-clients.md` |
| 4.3 review and capture | PASS | independent review below; working state and memory index updated. The work-index pointer was withdrawn when converging onto #104 (see below) |

## Tests

All entries ran under the launcher. "Before" ran on the unchanged tree (the first nine in this
worktree before any edit, the rest in a shallow clone of `1981e591`). Before and after ran at
different times on a host whose load varied a lot, so only the paired `cli-tiers.sh` rows compare
like with like.

| Entry | Before | After | Notes |
|---|---|---|---|
| `tests/unit/client-capabilities.sh` | PASS, 16 tests, 7 s | PASS, 17 tests, 1 s | new family/source/removed-ID test; `sources` mutation |
| `tests/unit/cli-tiers.sh`, paired back-to-back runs | PASS, 35 s and 36 s | PASS, 28 s and 17 s | one helper process per surface: 38 → 14 in its loop; one more assertion |
| `tests/unit/plugin-manifests-valid.sh` | PASS, 67 s | PASS, 9 s | removed routes must not be tracked |
| `tests/shape/manifest-identity.sh` | PASS (jq skip), 5 s | PASS (jq skip), 1 s | |
| `tests/shape/cli-tiers-sync.sh` | PASS, 9 s | PASS, 1 s | README table regenerated |
| `tests/unit/test-runner-contract.sh` | PASS, 403 s | PASS, 69 s | fixture copies the six manifests plus `CLAUDE.md`/`AGENTS.md` |
| `tests/shape/welcome-wiring.sh` | PASS, 3 s | PASS, 1 s | |
| `tests/shape/frontmatter-lint-all.sh` | PASS, 463 s | PASS (shape tier) | |
| `tests/unit/catalog-metadata.sh` | PASS, 31 tests, 322 s | PASS, 31 tests, 30 s | |
| `tests/unit/catalog-selection.sh` | PASS, 29 tests, 397 s | PASS, 29 tests, 90 s | |
| `tests/shape/catalog-regenerates-clean.sh` | PASS, 2 s | PASS (shape tier) | |
| `tests/unit/universal-trusted-tools.sh` | PASS, 51 tests, 352 s | PASS, 49 tests, 384 s | Gemini and Droid failure tests removed; decoy stubs must never run |
| `tests/integration/universal-adapters.sh` | PASS, 17 tests, 6662 s | PASS, 17 tests, 5730 s | all-surface install: 38 → 14 clients, 12 → 4 native roots |
| `universal-lifecycle.sh ProfileLifecycle.test_doctor_reports_bytes_not_hook_counts_or_historic_host_activity` | not run | PASS, 1 test | locks the four-client probe list |
| shape tier (`run-all.sh --scope shape`) | not run as a tier | PASS 41/41, 1 partial (jq) | M3 |
| `install/verify.sh --all` | not run | ALL CHECKS PASSED | one pre-existing warning about a legacy `li:cli-fingerprint` path |

Not run locally: the other integration entries (for example `copilot-kit.sh`, which takes
hours here and does not depend on the removed records), strict mode, Linux and macOS.

## Live-path scan

`git grep -n -i -E "gemini|opencode|antigravity|\bkiro\b|devin|windsurf|junie|\bcline\b|\baider\b|\bdroid\b|droid-cli|continue-ide|continue-cli|\.factory/|factory-(skills|agents|surfaces|desktop|cloud|droid)"`
over tracked files, excluding history (`.claude/engineering/**`, earlier `.claude/plans/**`,
`.claude/memory/**`, ADRs 0001–0029), the dated presentation deck and the design-dna data files
(which match "Android"). Every remaining hit is intended: removal notes (changelog, migration
index and guide, ADR-0035), refusal and decoy tests, a third-party project description in
`install/upstream-sources.yaml`, and the Gemini API mention in `skills/design-dna/ATTRIBUTION.md`.

## Compatibility audit (M2)

`bin/li-compat-audit` reports RED with 13 mechanical hits. See its disposition section:
the six `cli_support` value narrowings (counted under Q1 and Q3) and the registry are the
intended change; no frontmatter field, schema or helper signature changed.

## Independent review

A separate reviewer agent (`lintel-reviewer`, read-only) reviewed the staged diff three times.
First pass: PASS WITH FINDINGS, 0 P0, 0 P1, 3 P2, 6 P3. Second pass on the fixes: seven
resolved, four new (one P2, three P3). Third pass: all four resolved, no new issue. The
reviewer ran no tests; the results above are the coordinator's.

| Finding | Resolution |
|---|---|
| P2-1 evidence missing | this file, the audit disposition and the working state |
| P2-2 README links the deck | README labels the link as a 2026-09-25 event snapshot; the deck is unchanged |
| P2-3 migration steps | guide `docs/migrations/2026-09-25-supported-clients-four-families.md` |
| N1 unsafe delete command | removed; bounded manual step with the valid namespaces |
| P3 items and N2–N4 | test hardening, wording and record fixes (see plan and evolution entry) |

## CI effect

The CI matrix and shards are unchanged (ADR-0032): 21 suite jobs plus syntax and catalog.
No test file was deleted. Two test methods were removed and one added. The affected entries do
less work: 24 fewer registry surfaces, 8 fewer native roots in the all-surface install, fewer
helper processes in `cli-tiers.sh`, `plugin-manifests-valid.sh` and `universal-adapters.py`.
The long CI shards are dominated by entries this change does not touch, such as
`copilot-kit.sh`, so fewer or shorter CI jobs need a separate shard decision.

## Convergence onto #104 (2026-09-27)

Go Live (`88aecc43`), which the operator authorized on 2026-09-27 to publish and merge the open
pull requests, asked this branch's owner to converge onto #104 before #104 lands. The instruction
reached this session through Go Live, not from the operator directly (L-057).

- **Merge:** ordinary merge `66b56aa4` of #104's published head `22d502be`, which already
  contains `main` at `af94ff74` (PR #105). No rebase, amend or hook override (L-055, L-060).
- **Conflicts:** seven, resolved as follows.
  - `GEMINI.md` and `gemini-extension.json` stay deleted (ADR-0035).
  - The two skills that #104 retired in favor of native delegation or a swarm stay deleted.
    This branch had only narrowed their `cli_support` lists, so nothing needed carrying over.
  - `.claude/memory/working-state.md` keeps both active entries.
  - `docs/wiki/skills.md` is regenerated by `bin/li-wiki-gen`.
  - `.claude/plans/todo.md` takes #104's bytes exactly. Its four reviewed spans are bound to the
    whole file's SHA-256, so the pointer this branch had added there would have invalidated the
    guard's span register (L-061). The pointer stays in `working-state.md` and `MEMORY.md`.
- **Sweep:** Git's rename detection carried the `cli_support` trim into #104's renamed review
  skill, now `skills/cross-check`. A scan of the merged live paths finds no other removed-client
  route. The remaining hits are this change's own notes and tests, Gemini as a MARS model
  family, and third-party text. The changelog entry moved to #104's 0.12.0 section, and its link
  now points to the migration guide instead of the migration index (`bed56fc8`).
- **Generated outputs:** registry validation, `li-catalog.py --check`, `li-copilot.py check`
  (21 managed files), `li-instructions.py check`, `li-wiki-gen --check`, `adr-numbers-unique.sh`
  (ADR-0033 to ADR-0037 are unique) and `cli-tiers-sync.sh` pass on `bed56fc8`.
- **Guard:** in a `core.autocrlf=false` clone of `bed56fc8`, the shape tier ran 42 entries and
  #104's `native-command-surface.sh` failed with two findings on one line of this file's former
  "Open" section, which named the path of the retired review skill. The rewrite in `d2ea0f45`
  clears them. On that head the guard prints `native-command-surface: PASS (0 findings; 1
  historical observations in 1 declared records)`. Its observation lines include #104's
  registered records and 12 inventory entries from this change's compatibility audit.
- **Publication:** Go Live published the branch as `jokerman89` as draft PR #107, first with
  #104's branch as its base and then retargeted to `main`. The app's PR tool in this session had
  been refused on 2026-09-25 (403 for the Enterprise Managed User) and was not retried.
- **Local runs:** under the same launcher, in fresh `core.autocrlf=false` clones, without jq.
  - Shape tier on `d2ea0f45`: 42 of 42 pass, 1 jq-only partial.
  - Unit tier on `bed56fc8`: 85 of 85 pass, 1 jq-only partial.
  - `tests/integration/universal-adapters.sh` on `bed56fc8`: 17 tests pass.
  - The lifecycle doctor test and `install/verify.sh --all` pass.
  - `d2ea0f45` differs from `bed56fc8` only in three record files.

## Delivery

- **Independent review:** a read-only `lintel-reviewer` (`49a756b1`), commissioned by Go Live,
  reviewed `22d502be..d2ea0f45` and passed it: 0 P0, 0 P1, 0 P2 and 5 P3 findings. All five were
  record wording in this file and are fixed on `jokerman-microsoft-supported-clients-record-fixes`.
  Go Live holds the report (SHA-256
  `805a7799f1777232c2d7793b9d017efd9064922a74df0978adb7710cbff99389`).
- **CI and merge:** PR #107's hosted CI passed 23 of 23 jobs. Go Live merged it at
  2026-09-27 22:01:18Z as `10b0eea7`, with parents `22413558` and `d2ea0f45`. The merged tree
  equals the tested head's tree (`24895535`).

## Open

- When each remaining documentation PR merges `main` after #107, re-run the live-path scan,
  `li-catalog.py --check` and `li-wiki-gen --check` on the combined candidate (ADR-0035).
- The operator decides whether to update the dated presentation deck, or leave it as history.
