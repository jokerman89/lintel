# Tests

Lintel tests check both repository structure and executable behavior. Run the release suite with
Bash, Git, Python 3.9+ and jq installed:

```bash
bash tests/runner/run-all.sh --require-all   # every tier; skipped coverage fails
bash tests/runner/run-all.sh --scope unit    # one tier during development
bash tests/runner/run-all.sh --scope integration --shard 2/4 --require-all   # one CI shard
bash tests/runner/run-all.sh --shape-only    # structural contracts
bash tests/integration/copilot-kit.sh       # portable Copilot behavior
```

`--shard K/N` runs the discovered files at positions `i` with `i mod N = K - 1`, counting
only those, so strict accounting stays exact within each shard. The shards `1/N` to `N/N`
are disjoint and together equal the unsharded run. A malformed shard exits 2, and an empty
shard fails closed. CI runs the unit tier in 2 shards and the integration tier in 4 on
every system (ADR-0032).

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

CI runs every tier on Ubuntu, macOS and Windows, with explicit Python and jq preflight. Actions
use reviewed commit pins and read-only repository tokens. Catalog drift checks never push a
follow-up commit to the default branch. Native Windows install/reinstall tests require no Pester
installation and assert preservation of operator profile, packs and custom hooks.

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
