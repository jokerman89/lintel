# ADR-0041: Weighted integration shards, a chunked Copilot kit and pull-request-only cancellation

- **Status:** Accepted direction, 2026-09-29. Hosted runs of the candidate verify it.
- **Date:** 2026-09-29
- **Deciders:**
  - MasterCoordinator, who selected the design ("C+B" with pull-request-only cancellation) that the
    deep repository review proposed. The selection answers the operator's request to implement the
    review's CI findings rather than only report them.
  - Implemented on `jokerman-microsoft-ci-workload-balance`.
- **Supersedes:** ADR-0032 in part:
  - its rejection "for now" of balancing shards by recorded durations and of splitting
    `copilot-kit.py` into several entries;
  - its trade-off that a new run cancels any running run for the same ref.
- **Superseded by:** —

## Context

ADR-0032 assigns the file at discovery position `i` to shard `(i mod N) + 1` and runs the
integration tier in four shards on each system. It rejected duration balancing and a kit split
for the time being:

- durations would need maintained data;
- the kit was owned by another package late in delivery;
- index modulo kept every shard inside its 300-minute timeout.

ADR-0037 kept all parts, shards and timeouts and chose the operating systems per pull request.

**Timing method.** Main run `36564554824` on `2c81267b` passed all 23 jobs in about 125 minutes of
wall time. There is no per-test timing, so each entry's time is a proxy: from its runner `RUN` line
to the next `RUN` line, or to the summary for the last entry. The proxy includes runner
bookkeeping.

**Measured, from that proxy:**
- **Critical path:** Windows integration-4, 124.8 minutes. `copilot-kit.sh` took 115.3 minutes of
  it on Windows, 37.5 on Ubuntu and 27.5 on macOS.
- **Integration totals:** 239.8 minutes on Windows, 73.8 on macOS and 70.5 on Ubuntu. With four
  shards, Windows cannot finish below about 61 minutes.
- **Entries:** each system runs 175 entries (unit 94, integration 34, behavior 3, e2e 1,
  shape 43).
- **Heavy entries:** the integration entries that take 2 minutes or more on Windows:

| Entry | Windows s | Ubuntu s | macOS s |
|---|---|---|---|
| `copilot-kit.sh` | 6920.3 | 2249.0 | 1647.9 |
| `universal-adapters.sh` | 3244.7 | 535.3 | 357.0 |
| `catalog-installed.sh` | 1008.4 | 277.5 | 188.7 |
| `universal-lifecycle.sh` | 739.4 | 524.4 | 1282.5 |
| `swarm-shared-binding.sh` | 398.7 | 92.8 | 183.3 |
| `universal-a23.sh` | 345.1 | 84.2 | 67.8 |
| `universal-work-lifecycle.sh` | 289.0 | 50.6 | 62.4 |
| `private-sync-binding.sh` | 222.1 | 37.7 | 67.0 |
| `universal-profile-context.sh` | 176.7 | 52.0 | 52.5 |
| `observation-learning.sh` | 147.9 | 21.6 | 39.6 |
| `pattern-portability.sh` | 135.2 | 34.8 | 24.6 |

The 23 other integration entries take 762 seconds on Windows together: 33 seconds on average
and 107 at most.

**Cancellation.** `ci.yml` groups runs by workflow and ref with `cancel-in-progress: true`. On
2026-09-29, the next push to `main` cancelled main runs `36540548586` (on `d89385f2`) and
`36541022839` (on `3dadebaa`). Neither commit got a complete run of its own (review finding C-09).
For pull requests, cancelling the superseded run is wanted.

**Constraints:**
- the 23 job names, parts, shards, timeouts and `bin/li-ci-matrix.py` stay;
- every test still runs strictly on every system it runs on today;
- `catalog.yml` and the syntax job stay;
- no repository settings change;
- no new dependency is added.

## Decision

We chose to split the Copilot kit into test-method chunks, assign integration entries by declared
Windows weights, and cancel running CI only for pull requests.

- **Kit chunks.**
  - **The helper.** `tests/runner/unittest_chunk.py MODULE.py` loads a unittest module by path.
    - **Without `LINTEL_TEST_CHUNK`:** it runs the module as `python MODULE.py` would, through
      `unittest.main` at verbosity 2, and keeps any selectors.
    - **With `LINTEL_TEST_CHUNK=K/N`:** it sorts the test IDs and runs those at positions `i` with
      `i mod N = K - 1`, through the same text runner.
    - **`--list`:** prints the selected IDs and runs nothing.
    - **Refusals:** each of these exits 2 before any test runs:
      - a malformed value;
      - an empty chunk;
      - a chunk combined with any other unittest argument.
  - **The wrappers.** `tests/integration/copilot-kit-1.sh` to `copilot-kit-8.sh` replace
    `copilot-kit.sh`.
    - Each keeps the original description and tags and sets its chunk inline.
    - `copilot-kit.py` is not edited, so `python3 tests/integration/copilot-kit.py` still runs all
      tests in one process.
    - `universal-adapters` stays one entry.
- **Weighted assignment.** `tests/runner/run-all.sh` first discovers every entry in scope, in the
  order ADR-0032 defines. One `awk` process then reads each entry's leading comment block, meaning
  the lines before the first line that does not start with `#`.
  - **Header grammar:** `# SHARD-WEIGHT: <seconds>`, a positive whole number of 1 to 9 digits with
    no leading zero.
  - **Refusals:** a near-miss spelling, another value or a second header exits 2 before any test
    runs. A trailing carriage return is ignored.
  - **No header in the scope:** the assignment stays exactly `(i mod N) + 1`.
  - **Any header in the scope:**
    - An unweighted entry counts 60 seconds, about twice the mean of the unweighted integration
      entries, so a new unmeasured entry is not treated as free.
    - Entries go longest-first, with ties in discovery order, each to the least-loaded shard, with
      ties to the lowest shard number. With equal weights this reproduces `(i mod N) + 1`.
  - **Unchanged:** a shard still runs its entries in discovery order, and tag filtering, strict
    accounting, the empty-shard refusal and `--require-all` do not change.
  - **Summary:** a weighted, sharded run adds a `Weights:` line.
- **Weights.**
  - **Heavy entries:** each of the ten entries above, other than the kit, declares its Windows
    proxy seconds, rounded half up. These are 3245, 1008, 739, 399, 345, 289, 222, 177, 148 and 135.
  - **Kit chunks:** each declares 865 seconds, the kit's 6920.3 seconds divided by eight. How the
    kit's time splits across its methods is unknown, and the duplicated class fixture is not
    included.
  - **One partition:** the same weights serve every system. Per-system weights give the same Windows
    critical path in the model.
- **Pull-request-only cancellation.** `ci.yml` keeps its group and uses
  `cancel-in-progress: ${{ github.event_name == 'pull_request' }}`.
  - A newer pull request run cancels the running one.
  - A newer push or `workflow_dispatch` run waits instead, so a running `main` run is no longer
    cancelled.
  - GitHub still allows only one pending run per group by default. A newer run cancels and replaces
    a pending one, which shows as cancelled
    ([GitHub concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)).
    Not every intermediate commit is therefore promised a run.
  - `catalog.yml` keeps cancelling.

**Model.** This is an estimate from the same proxy data, with an assumed repeated class fixture of
0.5 minutes per chunk on Windows and 0.2 elsewhere, which was not measured. It sums each shard's
proxy times, and for today's assignment it lands within 0.3 minutes of the measured job wall times.
The table gives the longest integration shard, in minutes:

| Option | Ubuntu | macOS | Windows |
|---|---|---|---|
| Measured job wall time today (round-robin) | 40.1 | 30.2 | 124.8 |
| Modeled: this decision (ten weighted entries, eight chunks, 60 s default) | 24.4 | 34.1 | 62.3 |

## Alternatives considered

- **A pull request smoke tier (W2-1).** Not chosen here. It changes what a pull request must pass,
  which ADR-0037 set, so it remains a separate acceptance decision.
- **Weights only, no kit split.** Rejected: the kit alone keeps Windows at about 115 minutes.
- **Kit chunks with round-robin assignment.** Rejected: about 92 minutes on Windows in the model,
  and the result depends on where the chunks sort.
- **Per-system weights.** Rejected: the same Windows critical path in the model, with three data
  sets to maintain.
- **Six integration shards.** Rejected: it changes the job set, which this decision keeps.
- **Also split `universal-adapters` into three.** Rejected: the modeled Windows path does not
  improve (61.5 against 61.1 minutes in the proposal's model), and each chunk repeats a fixture.
- **Weights in a separate data file.** Rejected: a second source drifts away from the entries it
  describes. A header sits next to its entry, and an entry without one keeps working.
- **Keep cancelling every run for the same ref.** Rejected: running `main` runs keep being
  cancelled (C-09).
- **Never cancel.** Rejected: after each push to a pull request, a superseded run would hold hours
  of runner capacity.
- **Queue every `main` run (`queue: max`).** Not chosen. Every intermediate commit would get a
  full run, at about two hours of Windows capacity each, and this change has not verified how the
  option combines with an expression for `cancel-in-progress`. Merge queues and required checks are
  repository settings (W2-2, W2-4).

## Consequences

- **Positive:**
  - The modeled Windows critical path falls from the measured 124.8 minutes to about 62 minutes.
    The model is not a guarantee; hosted runs on the candidate measure it.
  - The balance no longer depends on where the kit sorts.
  - A `main` run that starts is no longer cancelled by a later push.
- **Negative:**
  - The weights are data that can drift. When an entry changes a lot, or a new entry becomes heavy,
    re-measure with the same proxy and update its header.
  - How long each chunk takes is unknown until hosted runs report it. Record the per-chunk times
    from the first runs.
  - Each chunk repeats the kit's class fixture. Running the eight wrappers without sharding pays it
    eight times; `python3 tests/integration/copilot-kit.py` runs everything in one process.
  - The helper names the module `copilot_kit`, so chunked test IDs read `copilot_kit.CopilotKit...`
    instead of `__main__.CopilotKit...`.
  - A newer `main` run waits for the running one, so the newest commit's result comes later.
    GitHub replaces a pending run when a newer one queues, so an intermediate commit can end with
    no run.
- **Neutral:**
  - The 23 jobs, their names, parts, shards and timeouts, and `bin/li-ci-matrix.py` are unchanged.
  - Each system runs 183 entries instead of 175: seven more integration entries (34 to 41) and one
    new unit contract.
  - The unit, shape, behavior and e2e tiers declare no weights, so their assignment is unchanged.
  - ADR-0037 notes that both workflows cancel an older run for the same ref. For `ci.yml` that now
    holds for pull request runs; `catalog.yml` is unchanged.

## Implementation notes

- **Contracts.** `tests/unit/unittest-chunk.sh` lists each chunk through its real wrapper. The
  chunks must be non-empty and pairwise disjoint, and their union must equal an independent
  `TestLoader` discovery of the module. `tests/unit/test-runner-contract.sh` covers:
  - the weighted partitions for one to five shards;
  - determinism;
  - a hand-computed longest-first case;
  - equal weights matching modulo;
  - refusal of malformed headers.

  `tests/unit/ci-matrix.py` pins the concurrency block.
- **Re-measuring.** After a hosted run, derive each entry's proxy time and compare the critical path
  with 124.8 minutes. Report the result as a measurement.

## References

- ADR-0032, in part superseded here; ADR-0037.
- Findings of the deep repository review:
  - W2-6: the kit split part only. The agent-count part (DR-19) stays open.
  - TCI-02: a component of DR-24.
  - C-09: only the part where a later push cancels a running main run.
- Still open: W2-1, W2-2, W2-3, W2-4, W2-5 and W2-7.
- `.claude/plans/ci-workload-balance/` (spec, plan and handoff).
- `tests/runner/run-all.sh`, `tests/runner/unittest_chunk.py`, `tests/README.md` and
  `.github/workflows/ci.yml`.
