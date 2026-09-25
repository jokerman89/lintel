# Review — supported clients: Copilot, Claude, Codex and Cursor

**Date:** 2026-09-25 · **Branch:** `jokerman-microsoft-trim-supported-clients` · **Base:** `1981e591`
(origin/main) · **Plan:** [plan.md](plan.md) · **Decision:** ADR-0035

## Verdict

PASS FOR LOCAL DELIVERY PREPARATION. All 15 leaves are implemented and their local checks
pass. The independent review found no P0 or P1 issue. Its P2/P3 findings are resolved, except
two operator decisions listed under "Open". No push, PR or CI run has happened (L-045, L-053).

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
| 4.3 review and capture | PASS | independent review below; working state, memory index and work index updated |

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

## Open

- The operator decides whether to update the dated presentation deck, or leave it as history.
- Merge order, recorded by the parent coordinator `f4584b03` (not named verbatim by the operator):
  PR #105 (MARS, renumbering its ADR-0034 to 0036) first, then PR #104, then this change, then the
  documentation branches. This branch takes `main` in with an ordinary merge, not a rebase, and
  then applies ADR-0035 to what landed. #104 renames `skills/codex` with `cli_support` still naming
  removed clients, and a documentation branch adds Gemini/OpenCode sections to `docs/multi-cli.md`.
  After each merge, re-run the live-path scan, `li-catalog.py --check` and `li-wiki-gen --check`,
  and verify the combined candidate.
- Push, PR, CI and merge wait for this session's operator (L-045, L-053).
