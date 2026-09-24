# ADR-0032: Deterministic shards for the strict CI suite

- **Status:** Accepted direction, 2026-09-24; the final PR's first CI run verifies it
- **Date:** 2026-09-24
- **Deciders:** coordinator88 (P15 final delivery), under the operator's "drive to finish"
  authorization
- **Supersedes:** —
- **Superseded by:** —

## Context

`.github/workflows/ci.yml` runs `bash tests/runner/run-all.sh --require-all` once per
operating system, with `timeout-minutes: 30`. The last main run took 0.8, 2.5 and 11.1
minutes on Ubuntu, macOS and Windows. Since then the initiative has added real
installed-consumer, lifecycle and transaction tests.

Local Windows timings on a loaded host sum to about 7.1 hours. By scope:

| Scope | Entries | Local time |
|---|---|---|
| integration | 30 | about 5.4 h, of which `copilot-kit.sh` alone is about 2.6 h |
| unit | 75 | about 2.3 h |
| shape, behavior and e2e together | 45 | under 20 minutes |

A GitHub-hosted job stops at 6 hours. Linux and macOS have not run here.

Local strict runs are impossible, because jq is denied (L-046). The final PR's CI is
therefore the first strict full-suite run, and A23.4's strict evidence comes from it.
Every discovered test must still run under `--require-all` on every system.
`main` has no branch protection or ruleset, so job names are free to change.

## Decision

- **Runner.** `tests/runner/run-all.sh` gains `--shard K/N`. After discovery (the fixed
  scope order, and files sorted within each directory), the file at zero-based position
  `i` belongs to shard `(i mod N) + 1`. Only that shard's files are counted and run.
  - The other files are not counted as skipped, so strict accounting stays exact
    within the shard.
  - The summary reports the shard and how many discovered files it selected.
  - Malformed shard arguments exit 2, and an empty shard fails closed as before.
  - Without the option, behavior is unchanged.
- **CI.** The suite job becomes a matrix of each operating system by one of seven parts:
  `unit` in 2 shards, `integration` in 4 shards, and an `other` part that runs `behavior`,
  `e2e` and `shape` with `--require-all`. The once-per-system steps run only in `other`:
  - repository structure verification;
  - the stock Bash 3.2 install on macOS;
  - the PowerShell install check on Windows;
  - the catalog, instructions, adapter and wiki checks.
- **Timeouts** are sized from the local measurements: 300 minutes for integration shards,
  180 for unit shards and 60 for `other`.
- **Windows** jobs select the approved PowerShell 7 with
  `LINTEL_POWERSHELL=<path of pwsh.exe>`. `tests/integration/universal-a23.py` requires it,
  and every local Windows result used it.

## Alternatives considered

- **Raise the single job's timeout to 360 minutes.** Rejected: the Windows estimate is
  above 6 hours even before any runner variance, so the job would still be cut off.
- **Shard by `--scope` only.** Rejected: Windows integration alone is about 5.4 hours,
  too close to the 6-hour limit. Tag filters cannot help either, because strict mode
  counts filtered-out tests as skipped.
- **Balance shards by recorded durations, or split `copilot-kit.py` into several
  entries.** Rejected for now. Durations would need a maintained data file and would
  drift. Splitting the kit changes a test that P10 owns and SAME reviewed, late in
  delivery. Index-modulo sharding already caps the largest local shard at about 2.9
  hours, the shard holding the kit.

## Consequences

- **Positive:** every test still runs strictly on every system, now within job limits.
  Shards run in parallel, so the wall time is bounded by the kit's shard.
- **Negative:** adding or renaming a test file can move other files between shards, so
  the balance is not guaranteed. Twenty-one jobs repeat checkout and setup. Durations on
  hosted runners are unknown until the first run.
- **Neutral:** the runner contract test proves that the shards are disjoint and that
  together they cover exactly the unsharded set. The CI logs show each shard's selection.

## References

- P13 installed review N1 and the P14 A23 unit, which measure their entries against the
  30-minute budget.
- `.claude/plans/universal-implementation/handoff.md`, the P15 delivery-risk finding.
- L-045 (no push or CI before the accepted batch), L-046 (jq denied).
