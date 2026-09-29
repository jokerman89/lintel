# Tests

Lintel tests check both repository structure and executable behavior. Run the release suite with
Bash, Git, Python 3.9+ and jq installed:

```bash
bash tests/runner/run-all.sh --require-all   # every tier; skipped coverage fails
bash tests/runner/run-all.sh --scope unit    # one tier during development
bash tests/runner/run-all.sh --scope integration --shard 2/4 --require-all   # one CI shard
bash tests/runner/run-all.sh --shape-only    # structural contracts
python3 tests/integration/copilot-kit.py     # portable Copilot behavior, every test in one process
```

`--shard K/N` runs one shard of the discovered files and counts only those, so strict accounting
stays exact within each shard. The shards `1/N` to `N/N` are disjoint and together equal the
unsharded run. A malformed shard exits 2, and an empty shard fails closed. CI runs the unit tier
in 2 shards and the integration tier in 4 on every system it selects (ADR-0032, ADR-0037).

How files are assigned depends on weight headers (ADR-0041):

- **No weights in the scope.** The file at position `i` goes to shard `(i mod N) + 1`.
- **Any file in the scope declares a weight.** A file declares one in its leading comment block
  (the lines before the first line that does not start with `#`), as
  `# SHARD-WEIGHT: <seconds>`, a positive whole number.
  - Files without the header then count 60 seconds.
  - Files go heaviest first, ties in discovery order, each to the least-loaded shard, ties to the
    lowest shard.
  - A shard still runs its files in discovery order, and its summary adds a `Weights:` line.
  - A malformed, misspelled or repeated header exits 2 before any test runs.
- **Where the weights come from.** They are Windows seconds from a hosted run: each entry measured
  from its `RUN` line to the next. Only the heavy integration entries declare one. After a large
  change to an entry, measure it again and update its header.

`tests/runner/unittest_chunk.py MODULE.py` runs a unittest module as `python MODULE.py` would.

- **Chunks.** With `LINTEL_TEST_CHUNK=K/N`, it runs only chunk `K`: the test IDs are sorted, and the
  chunk holds those at positions `i` with `i mod N = K - 1`.
- **Listing.** `--list` prints the selected IDs without running them.
- **Refusals.** A malformed value, an empty chunk, or a chunk combined with test selectors exits 2.
- **The Copilot kit.** `copilot-kit-1.sh` to `copilot-kit-8.sh` run its eight chunks in separate
  entries, so the shards can balance it. Each chunk repeats the kit's class fixture. For a local
  run of the whole kit, use the single `python3` command above instead of the eight wrappers.
  `bash tests/integration/copilot-kit-3.sh --list` shows one chunk's tests.

A unittest skip whose reason begins `platform: windows-only` marks a Windows-native assertion.
Off Windows, the runner reports such skips as `N/A`, not as partial coverage, but only when every
skip in the entry carries that reason and at least one test in it ran. On Windows the same skips
count as partial, so strict mode refuses them. Any other skip reason keeps refusing strict
acceptance. Keep the reason free of apostrophes: unittest then prints it in double quotes, which
the runner does not recognize, so the skip refuses fail-closed.

The full developer suite needs Bash 4+ because several existing routing tests and developer
utilities use associative arrays. On macOS, install modern Bash for the suite. CI separately
checks the bare installer with the stock `/bin/bash` 3.2. On Windows, use Git Bash; native
PowerShell installer verification is `./tests/runner/check-install.ps1`.

Run the suite the way CI does:

- Install the declared optional YAML parser (`python3 -m pip install -r lib/envelope-requirements.txt`).
  The catalog, discovery and envelope tests need it.
- Give the suite a synthetic `HOME` and `USERPROFILE`, with `TEMP`, `TMP` and `TMPDIR` under the
  same parent, and use a physical path with no linked ancestors. On macOS, the default
  `/var/folders/...` directory sits under the `/var` link, which Lintel refuses as a fixture root.

No test needs a PDF library: Lintel has no PDF reader (ADR-0033).

Each test has a shell entry point and exits nonzero on failure. Some entry points execute Python
standard-library unittest suites. The runner discovers current tests instead of relying on a
fixed test count. It prints each test as it starts, aggregates failures, reports skipped coverage,
and rejects an empty run. Use `--require-all` for release evidence.

Unavailable assertions must emit a `SKIP:` line, not an informational `NOTE:`.
For example, missing jq leaves manifest version-parity coverage unrun even when
the other identity checks pass. The runner reports that suite as partial and
`--require-all` refuses full acceptance; a non-strict run may retain the partial result.
The same rule applies to hook JSON-extraction checks and manifest parsing/field
checks. Missing parsers must not print `valid JSON`; an available parser that
fails remains a failed check, not a dependency skip.

## The tiers

| Tier | What it verifies |
|---|---|
| `shape/` | Required metadata, generated artifact drift, hook registration, canonical paths, unique decision numbers and public-language contracts. |
| `unit/` | State, pack resolution, memory, routing, installer metadata validation, catalog generation and test-runner behavior. |
| `integration/` | Real boundaries: Copilot repo generation and conflict refusal, security hooks, session traces, wiki output and startup protocol generation. |
| `behavior/` | A mechanism actually firing in isolation, including installer failure reporting. |
| `e2e/` | Install into an isolated home, resolve its pack and footer, then create/check a consumer Copilot repo from installed assets. |

## What a green run establishes

The suite verifies portable files, parser contracts and local runtime behavior. Copilot tests use
real temporary repositories and filesystem operations. They do not make paid model calls or
establish that an organization's client settings, entitlement or policies permit a live task.
Record live VS Code, CLI and cloud-agent acceptance separately; use the
[release checklist](../.claude/engineering/SHIP-GATE.md).

`shape/build-workflow-contract.sh` checks BUILD's instruction structure. Its old location
under `behavior/build-pilot.sh` overstated that evidence. The enterprise integration tests
execute actual workflow snippets and pack consumers; neither test category proves a live
model follows the complete cycle or establishes measured enterprise productivity.

CI runs every tier on Ubuntu for every pull request and push, with explicit Python and jq preflight.
Pushes to `main`, manual dispatches, pull requests labelled `ci:full-matrix` and pull requests that
touch a platform-sensitive path also run every tier on macOS and Windows. Adding, deleting or
renaming any file outside `docs/`, `.claude/` and `presentations/` counts as platform-sensitive;
editing existing Markdown, HTML, text or images outside code locations does not. A
documentation-only pull request stays on Ubuntu, and a diff that cannot be computed selects all
three (ADR-0037,
`tests/unit/ci-matrix.sh`). Actions use reviewed commit pins and read-only repository tokens.
A newer push to a pull request cancels that pull request's running CI. A running push or dispatch
run, including one on `main`, is not cancelled: a newer run waits. GitHub keeps at most one run
waiting per branch and replaces it when a newer one arrives, so an intermediate commit can end
without a run (ADR-0041).
Catalog drift checks never push a
follow-up commit to the default branch. Native Windows install/reinstall tests require no Pester
installation and assert preservation of operator profile, packs and custom hooks.

Hook tests run the Claude Code hook scripts locally with synthetic input. They do not prove that
any host registered or ran a hook, and that bundle is not translated to other clients. Adapter
tests for Copilot, Codex, Cursor and the Universal handoff likewise check generated files and
local behavior, not a live client session.

## Adding a test

1. Start from `tests/conventions/bash-test-template.sh`, or wrap a Python unittest module in a
   shell entry point when filesystem scenarios are clearer in Python.
2. Choose a tier based on the contract under test. Explain the failure the test prevents.
3. Use an isolated temporary repository/home. Keep secrets, customer data and the operator's
   actual installed state out of fixtures.
4. Exercise a meaningful negative case as well as success. A file's existence alone does not
   prove that an installer, gate or generator works.
5. Return nonzero and print the cause on failure. Report unavailable coverage explicitly.
6. Record executable mode for new invokable `bin/li-*` tools with `git update-index --chmod=+x`
   before the final suite. Linux and the executable-mode shape test enforce the committed mode.

For generated files, fix the source and regenerate before running drift checks:

```bash
python3 bin/li-catalog.py
python3 bin/li-instructions.py sync
bash bin/li-wiki-gen
bash bin/li-copilot init --target .
```
