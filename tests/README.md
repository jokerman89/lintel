# Tests

Lintel tests check both repository structure and executable behavior. Run the release suite with
Bash, Git, Python 3.9+ and jq installed:

```bash
bash tests/runner/run-all.sh --require-all   # every tier; skipped coverage fails
bash tests/runner/run-all.sh --scope unit    # one tier during development
bash tests/runner/run-all.sh --shape-only    # structural contracts
bash tests/integration/copilot-kit.sh       # portable Copilot behavior
```

The full developer suite needs Bash 4+ because several existing routing tests and developer
utilities use associative arrays. On macOS, install modern Bash for the suite. CI separately
checks the bare installer with the stock `/bin/bash` 3.2. On Windows, use Git Bash; native
PowerShell installer verification is `./tests/runner/check-install.ps1`.

Each test has a shell entry point and exits nonzero on failure. Some entry points execute Python
standard-library unittest suites. The runner discovers current tests instead of relying on a
fixed test count. It prints each test as it starts, aggregates failures, reports skipped coverage,
and rejects an empty run. Use `--require-all` for release evidence.

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
