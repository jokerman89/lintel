# Spec: balanced CI integration shards and uncancelled main runs

**Status:** APPROVED for the bounded W2 slice that MasterCoordinator selected on 2026-09-29.
**Source findings:** the deep repository review's original IDs.
- W2-6: only the part that splits `integration/copilot-kit.sh`, refined from "smoke + full" to
  method chunks.
- TCI-02: the integration shard balance, a component of DR-24.
- C-09: only the part where a later push cancels a running main run.

**Authority:** the operator asked for the review findings to be implemented, not only reported.
MasterCoordinator selected design "C+B" (kit chunks plus duration weights) with PR-only
cancellation. That selection does not authorize the other W2 cards, settings or governance
changes.
**Decision:** [ADR-0041](../../decisions/0041-weighted-shards-kit-chunks-pr-cancellation.md).
**Plan:** [plan.md](plan.md).

## Architecture

ADR-0032 shards the strict suite by index modulo. ADR-0037 selects each run's operating
systems. The OS selection and job topology stay: the 23 job names, parts, shard counts,
timeouts, `bin/li-ci-matrix.py`, `catalog.yml` and the syntax job remain. The change affects
three things:

1. **Which test entries exist.** The Copilot kit becomes eight chunk entries.
2. **How the runner assigns entries to shards.** It uses declared weights.
3. **Which suite runs a newer run cancels.** Only pull request runs are cancelled.

## Requirements

| ID | Required behavior | Leaf |
|---|---|---|
| R1 | `tests/runner/unittest_chunk.py MODULE.py [--list \| unittest arguments]` behaves as follows.<br>**With `LINTEL_TEST_CHUNK` unset:** the module's tests run through `unittest.main` at verbosity 2 with the given arguments, so selectors are kept and the tests and results are those of `python MODULE.py [arguments]`. The process itself differs: the module name (not `__main__`), `sys.argv`, an extra `sys.path` entry and bytecode writing (ADR-0041). `--list` prints every test ID, sorted.<br>**With `LINTEL_TEST_CHUNK=K/N`** (1 ≤ K ≤ N, no leading zeros): tests are sorted by ID, and chunk K holds the tests at zero-based positions `i` with `i mod N = K - 1`. The chunk runs through the same unittest text runner, so the runner's `Ran N test`, `OK (skipped=N)` and `platform: windows-only` parsing and `--require-all` still apply per entry. `--list` prints the chunk's IDs and runs nothing.<br>**Refusals:** each of these exits 2 before any test runs:<br>- a malformed or empty value;<br>- an empty chunk;<br>- a chunk combined with any unittest argument;<br>- `--list` combined with another argument;<br>- a missing module. | W2-6 |
| R2 | `tests/integration/copilot-kit.sh` is replaced by `copilot-kit-1.sh` to `copilot-kit-8.sh`.<br>- **Each wrapper:** keeps the original description and tags, exports `LINTEL_TEST_BASH`, sets the chunk inline (not exported) and forwards its arguments (for `--list`).<br>- **Discovery:** no unchunked kit entry is discovered.<br>- **Direct run:** `python3 tests/integration/copilot-kit.py` still runs every test in one process, because the module is not edited.<br>- **`universal-adapters`** stays one entry. | W2-6 |
| R3 | A unit contract lists every chunk through the real wrappers. Each chunk is non-empty, the chunks are pairwise disjoint, and their union equals an independent `TestLoader` discovery of the module, computed rather than fixed (52 today). The wrappers are exactly `1..N` with one `N`, and no other discovered entry invokes `copilot-kit.py`. | W2-6 |
| R4 | `tests/runner/run-all.sh` discovers files as before: the scope directories in order, `find \| sort` within each. The shard assignment then works as follows.<br>- **Reading headers:** one `awk` process reads each discovered file's leading comment block. `# SHARD-WEIGHT: <seconds>` takes a positive whole number of 1 to 9 digits with no leading zero; a trailing CR is tolerated.<br>- **Refusal:** a near-miss spelling, an invalid value or a second header exits 2 before any test runs.<br>- **No headers in the scope:** the assignment is exactly `(i mod N) + 1`.<br>- **Any header in the scope:** unweighted entries count 60 s, and entries go longest-first, ties in discovery order, to the least-loaded shard, ties to the lowest shard.<br>- **Order:** a shard runs its entries in discovery order.<br>- **Unchanged:** tag filtering after assignment, accounting, empty-shard refusal and `--require-all`.<br>- **Summary:** a weighted, sharded run adds one `Weights:` line.<br>- **Compatibility:** the script stays Bash 3.2 compatible. | TCI-02 |
| R5 | **Weights:** Windows proxy seconds from main run `36564554824` (at `2c81267b`), rounded half up. They apply to the ten integration entries at or above 120 s, plus 865 s for each kit chunk (6920.3 s / 8, with no fixture cost added). One partition serves every system. | TCI-02 |
| R6 | `.github/workflows/ci.yml` uses `cancel-in-progress: ${{ github.event_name == 'pull_request' }}` with the same group, pinned in `tests/unit/ci-matrix.py`.<br>- **Still cancelled:** a newer pull request run cancels the running one.<br>- **No longer cancelled:** a running push or dispatch run, including one on `main`.<br>- **Pending runs:** GitHub still replaces a pending run in the group with a newer one, and the replaced run shows as cancelled, so an intermediate commit may get no run. | C-09 |
| R7 | **ADR-0041:** records the decision.<br>**ADR-0032 and ADR-0037:** gain narrow "Superseded by (in part)" metadata pointers to ADR-0041; ADR-0037's pointer concerns only the already-authorized running-CI cancellation change. Their historical bodies stay unchanged.<br>**`tests/README.md`:** documents the header, the default weight, the chunk variable, the wrappers, the direct full run and the fixture cost of unsharded local runs. | all |

## Constraints

- **Dependencies:** only the Python 3.9+ standard library, POSIX awk and the existing Bash.
  Nothing new is installed.
- **Unchanged:**
  - `tests/integration/copilot-kit.py` (the held hook work owns its test bodies and
    fixtures);
  - hooks;
  - `bin/li-ci-matrix.py`;
  - `catalog.yml`;
  - the syntax job;
  - schedules, rulesets, merge queue, Actions permissions, deploy and Pages.
- **Central ownership:** version, manifests and CHANGELOG belong to the central coordinator.
  This slice does not bump them.
- **Timings are proxies:** each entry is measured from its `RUN` line to the next one. The modeled
  Windows critical path of about 61-62 minutes is not acceptance. Only hosted runs on the candidate
  verify it.

## Out of scope and still open

| Item | Covers |
|---|---|
| W2-1 | The PR p50 target (DR-24) |
| W2-2 and W2-4 | Settings, and C-09's enforced checks |
| W2-3 | The syntax fold |
| W2-5 | The PR template |
| W2-7 | Slow Windows test timeouts |
| W2-6 agent-count part | DR-19, batch 2 |

None of these is marked done by this slice.
