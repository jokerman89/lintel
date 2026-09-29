# Handoff: CI workload balance (original W2-6 split, TCI-02, C-09)

Read [spec.md](spec.md), [plan.md](plan.md), [ADR-0041](../../decisions/0041-weighted-shards-kit-chunks-pr-cancellation.md),
ADR-0032 and ADR-0037. The selected map is [work.json](work.json). Keep the original IDs.

## Goal

The full CI run waits for one Windows integration shard, the one that holds the Copilot kit
(124.8 minutes in main run `36564554824`). Remove that bottleneck without changing the job set
or the coverage.

- **Kit chunks:** `tests/runner/unittest_chunk.py` runs the chunk of the kit's sorted test IDs that
  `LINTEL_TEST_CHUNK=K/N` selects. `copilot-kit-1.sh` to `copilot-kit-8.sh` replace `copilot-kit.sh`.
- **Weights:** `run-all.sh` reads `# SHARD-WEIGHT: <seconds>` headers in one awk pass. It assigns
  longest-first to the least-loaded shard and falls back to `(i mod N) + 1` when no entry in the
  scope has a header.
- **Cancellation:** `ci.yml` cancels in-progress runs only for pull requests.

## Hard constraints

- **Coverage:** every test still runs on every system, in the same 23 jobs with the same timeouts.
- **Untouched:**
  - `bin/li-ci-matrix.py`, `catalog.yml` and the syntax job;
  - settings, rulesets, merge queue, schedules, permissions and Pages;
  - `tests/integration/copilot-kit.py`, whose bodies and fixtures belong to the held hook work;
  - any hook or held hook-branch content;
  - version manifests and CHANGELOG, which the central coordinator owns.
- **No new dependencies:** Python 3.9+ standard library, POSIX awk, and Bash 3.2-compatible
  `run-all.sh`.
- **No silent narrowing:** a malformed chunk, an empty chunk, a malformed weight or a conflicting
  selector exits 2.

## Acceptance

- **Kit chunks:** `bash tests/unit/unittest-chunk.sh` passes. It covers:
  - the helper's refusals and its unset behavior;
  - `--list` through each real wrapper giving non-empty, disjoint chunks whose union equals an
    independent discovery;
  - wrappers exactly `1..N`, with no other entry invoking `copilot-kit.py`.
- **Weights:** `bash tests/unit/test-runner-contract.sh` passes. It covers the existing cases, plus
  weighted disjointness and completeness for N = 1 to 5, determinism, a hand-computed longest-first
  case, the equal-weights-to-modulo case and refusal of malformed headers.
- **Cancellation:** `bash tests/unit/ci-matrix.sh` passes, including the pinned concurrency block.
- **Hosted:** the candidate's hosted runs are 23 of 23. On every system, each kit chunk runs once
  with no skip or partial, and the entry count per system is the base plus 8. Report the
  re-measured critical path as a measurement.

## Re-execute or extend

1. Regenerate nothing: no generated artifact depends on these files.
2. After a hosted run, derive per-entry times with the proxy method in ADR-0041, then update the
   weights in the affected headers.
3. Keep the default weight and the header grammar unless a new ADR changes them.

## Out of scope

This slice does not complete the other W2 cards (W2-1, W2-2, W2-3, W2-4, W2-5 and W2-7), DR-24 as a
whole, or the agent-count part of W2-6 (DR-19). Do not mark them done.
