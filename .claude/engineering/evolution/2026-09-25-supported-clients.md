---
slug: supported-clients
date: 2026-09-25
cycle_id: supported-clients
operator: repository-maintainer
affected_paths:
  - lib/cli-tiers.yaml
  - bin/li-update
  - bin/li-lifecycle.py
  - install/verify.sh
  - GEMINI.md
  - gemini-extension.json
  - .opencode/INSTALL.md
  - skills/*/SKILL.md (cli_support hints)
  - tests/unit/client-capabilities.py
  - tests/unit/cli-tiers.sh
  - tests/integration/universal-adapters.py
  - tests/unit/plugin-manifests-valid.sh
  - tests/shape/manifest-identity.sh
  - tests/unit/test-runner-contract.sh
  - tests/unit/universal-trusted-tools.py
  - tests/integration/universal-lifecycle.py
  - README.md, AGENT-INSTRUCTIONS.md, CLAUDE.md, CONTRIBUTING.md, CHANGELOG.md, docs/*.md
  - docs/migrations/_INDEX.md, docs/migrations/2026-09-25-supported-clients-four-families.md
risk_class: medium
breaking_change: true
---

# Structure change: supported-clients

> Gate M1 (structure-impact analysis) artifact for ADR-0035.

## What changed (shape)

The surface registry shrank from 38 records (37 client surfaces in 14 families plus the manual
`other` route) to 14 records (13 surfaces in the Claude, Copilot, Codex and Cursor families plus
`other`). 20 sources and 8 aliases went with the removed records. The registry schema
(version 2), its validator and every reader are unchanged. Two root entry routes (`GEMINI.md`
with `gemini-extension.json`, and `.opencode/`) were deleted, `bin/li-update` lost its Gemini
and Droid sections, and the doctor probes four client executables instead of seven.
`cli_support` hints no longer name `gemini`, `opencode` or `droid`.

## Backward-compat

- Every Claude, Copilot, Codex and Cursor surface ID and alias resolves as before, with
  the same discovery root, vendor claims and observations.
- Installed kits whose inventory lists only kept surfaces, including this repository's
  own `copilot-cli` kit, check and update unchanged.
- `other` and unknown-ID degradation in `cli_tier_*` are unchanged; a removed ID now
  degrades like any unknown ID (legacy reader) or is refused (installer, `show`, catalog).

## Migration path

Breaking for three groups, documented in
`docs/migrations/2026-09-25-supported-clients-four-families.md` and its
`docs/migrations/_INDEX.md` row (`supported-clients-four-families`):

1. Gemini CLI extension users and Factory Droid plugin users: remove or manage the `li`
   extension/plugin with the host's own commands; `li-update` no longer touches them.
2. OpenCode users of `.opencode/INSTALL.md`: the guide is gone. Any of these hosts can use a
   repository kit with `other`, a manual handoff.
3. A kit initialized from unreleased `main` with a removed surface: `check` and `init` refuse
   before writing. The guide rebuilds it from its own inventory: remove the listed managed
   paths, which stay inside the kit's fixed namespaces, then re-run `init` with each supported
   surface still wanted.

## Forward-compat

Adding a family again is a product decision (a new ADR), then a registry record with
dated sources, installer and consumer cases, and a real client pilot. The schema did not
change, so no reader needs work to accept it.

## Verification

- `tests/unit/client-capabilities.py` gains a test that the families are exactly
  `claude`, `codex`, `copilot`, `cursor` and `other`, that every source is cited, and that
  removed IDs are refused. A new mutation keeps the validator's surface-`sources` check
  covered now that no kept record uses that field.
- `tests/unit/cli-tiers.sh` asserts exactly 14 registered surfaces and that a removed ID
  degrades to the manual route.
- `tests/unit/plugin-manifests-valid.sh` asserts the removed entry routes are not tracked.
- `tests/unit/universal-trusted-tools.py` keeps decoy `gemini`/`droid` commands on `PATH`
  and fails if `li-update` invokes them.
- `tests/integration/universal-lifecycle.py` locks the doctor's four-client probe list.
- Existing shape tests: `cli-tiers-sync.sh`, `manifest-identity.sh`,
  `frontmatter-lint-all.sh`, `welcome-wiring.sh`, `catalog-regenerates-clean.sh`.
- Evidence and timings: `.claude/plans/supported-clients/review.md`.

## Rollback procedure

Revert this branch's commits with `git revert` in a reviewed branch. That restores the
records, entry files, update routes, hints, tests and documentation together; no user
data or installed kit is modified by the revert itself.
