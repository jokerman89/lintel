---
slug: native-client-parity
date: 2026-09-28
cycle_id: native-client-parity-20260928
operator: jokerman
affected_paths:
  - bin/li-copilot.py
  - lib/native_artifacts.py
  - hooks/adapters/
  - hooks/shared/_input.sh
  - .github/skills/
  - .github/agents/
  - .github/hooks/lintel.json
  - .github/plugin/
  - shims/copilot/COPILOT.md
  - lib/cli-tiers.yaml
  - skills/*/SKILL.md (cli_support hints only)
risk_class: high
breaking_change: true   # behavior change: updating the Copilot plugin activates blocking hooks
---

# Structure change: native-client-parity

> Gate M1 (structure-impact analysis) artifact for increment 1, GitHub Copilot. Design:
> [design.md](../../plans/native-client-parity/design.md). Increment 2 (Claude, Codex, Cursor)
> adds its own section before it ships.

> **Landing split (2026-09-28, recorded 2026-09-29).** Increment 1 lands in two pull requests
> (plan "Landing split and execution boundaries"). PR-1a, version 0.13.0, carries the native skills
> and agents and installs no hooks. The hook adapter, the hook registrations and the hook statements
> below (activation, `LINTEL_HOOKS_DISABLED`, `--hooks`, the vendored `hooks/` bundle) belong to
> PR-1b and its own version. The breaking change for PR-1a is the one the migration guide
> describes: generated native files replace the pointer wrappers, and a consumer agent with a
> generic Lintel agent name blocks the update.

## What changed (shape)

- Copilot native skills move from 15 generated pointer files to one self-contained generated
  `SKILL.md` for every canonical skill. The name pattern `li-<name>` is unchanged; the body is the
  canonical body plus deterministic transforms and a Copilot preamble.
- Copilot native agents grow from 3 pointer profiles to 3 role profiles plus one generated
  `.agent.md` per canonical agent. Canonical names are kept, and the frontmatter is allowlisted to
  `name`, `description` and `tools`.
- A hook host adapter layer (`hooks/adapters/`) runs the unchanged canonical `hooks/shared/*/run.sh`
  scripts behind each client's documented hook I/O. Copilot registrations are generated into the
  plugin hooks file and a repository `.github/hooks/lintel.json`.
- The vendored repository bundle now includes `hooks/`, and the kit inventory records the hooks it
  installed.
- `cli_support` values gain `copilot` entries for skills that are now delivered natively. The
  frontmatter contract (field names and types) is unchanged.

## Backward-compat

- **Existing Copilot invocations keep working.** `/li-<name>` names are unchanged, and the core 15
  keep their curated descriptions.
- **Kits update through their managed inventory.** `li-copilot init` or `check` on an existing
  vendored kit reports the new managed files and refuses unmanaged collisions, as before.
- **Claude plugin users see no change.** `hooks/hooks.json`, `skills/` and `agents/` are unchanged
  apart from `cli_support` hint values.
- **Codex and Cursor output is unchanged in increment 1.** Their repository wrappers stay pointers.

## Migration path

This is a behavior change, though no file format breaks. Updating the Copilot plugin to 0.13.0
activates the nine auto-registered hooks, two of which block commits or pushes that contain secrets
or customer data. `docs/migrations/2026-09-28-copilot-native-parity.md`, indexed in
`docs/migrations/_INDEX.md`, covers:

- what activates, and the per-session escape hatch `LINTEL_HOOKS_DISABLED=1`;
- the PowerShell override syntax;
- re-running `li-copilot init` for kits;
- the explicit `--hooks` opt-in for repository hooks and what it trusts;
- why the plugin and repository hooks should not both be installed (both run, with no
  cross-origin suppression, so a double install duplicates context).

## Forward-compat

- **Enables:** the same generator host-profile and hook-adapter core for Claude, Codex and Cursor in
  increment 2; per-host tool and invocation rewrites without editing canonical content; and live
  observations per surface in the registry.
- **Forecloses:** hand-edited native skill files, which are now generated and drift-checked.

## Verification

- **New tests:**
  - generated-skill shape (frontmatter, completeness, no residual `/li:`, links resolve);
  - agent shape (allowlist, size limit);
  - hook adapter unit tests with recorded Copilot payloads;
  - a vendored-kit integration test.
- **Existing tests affected:** the Copilot kit integration test, catalog and wiki hint counts, and
  the `li-copilot check` drift gate.
- **Live acceptance:** a headless Copilot CLI session in a temporary consumer repository (AC6),
  recorded as registry observations.

## Rollback procedure

Revert the increment's merge commit with an ordinary `git revert`. Kit owners then re-run
`li-copilot init` from the reverted source, which removes files that are no longer generated through
the managed inventory. Plugin users update to the next version. Do not rewrite history.
