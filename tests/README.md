# Lintel Tests

Test infrastructure for Lintel v2.0+. Spec'd in v2 design as P1 fix T2 (eng-review).

## Structure

```
tests/
  unit/           per-component unit tests (TS or shell)
  integration/    cross-component integration (shell)
  e2e/            end-to-end multi-skill flow (shell)
  fixtures/       sanitized test data
  runner/         test runners (run-all.sh / run-unit.sh / run-e2e.sh)
  conventions/    bash-test-template.sh + style rules
```

## Running tests

```bash
bash tests/runner/run-all.sh         # everything (gated by tag availability)
bash tests/runner/run-unit.sh        # unit only
bash tests/runner/run-e2e.sh         # e2e only
bash tests/runner/run-all.sh --tag claude-code-only  # filter by tag
```

## Conventions

Bash tests follow `tests/conventions/bash-test-template.sh`. Each test declares:

- **Description** — one line at top of file
- **Tags** — dependencies the test requires (`claude-code`, `codex`, `browser`, `gstack-binaries`)
- **Setup** — fixtures or env vars needed
- **Run** — the actual test
- **Cleanup** — return repo to original state

Tests opt-in to "requires-claude-code" / "requires-codex" / "requires-browser" via the `# TAGS:` header line. Runner respects tags + skips tests whose deps are missing in the current environment.

TS tests (where applicable, doc-gen) use vitest. Config at `tests/vitest.config.ts` (created in Phase F when doc-gen libs land).

## Adding a new test

1. Copy `tests/conventions/bash-test-template.sh` to your target dir
2. Fill in DESCRIPTION, TAGS, SETUP, RUN, CLEANUP
3. Add a meaningful assertion (use `assert_eq`, `assert_file_exists`, `assert_contains` helpers in template)
4. Run locally: `bash tests/your-new-test.sh` to verify it passes
5. Verify it's discovered by runner: `bash tests/runner/run-all.sh | grep your-test`

## CI integration

`.github/workflows/ci.yml` runs:
- `unit-tests` (Linux + Windows) — `tests/unit/` + `tests/runner/run-unit.sh`
- `e2e-claude-code-only` (Linux) — `tests/e2e/` with `--tag claude-code-only`
- `e2e-cross-cli` (Linux) — full e2e when Codex available in CI environment

Phase G updates ship gate (`SHIP-GATE.md` Gate 9) to require all unit + e2e-claude-code-only jobs green before v2.0 tag.

## What's NOT in scope here

- LLM evaluation tests (those live in `eval/<feature>/` per component; see `/lintel:li-eval` skill)
- Performance benchmarks (those use `/perfbench` skill, results in `~/.lintel/benchmarks/`)
- Manual QA testing (operator-driven; see `/qa` and `/qa-only` skills)

## Status

Created in Phase A of Lintel v2.0 build. Currently contains scaffolding only — actual tests land in Phase A.8 onwards as components are built.
