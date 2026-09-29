# Capture: native client parity, PR-1a

This covers PR-1a only (native Copilot skills and agents, 0.13.0) and was captured on 2026-09-29.
It is not the increment's full recap: PR-1b (hooks) is open, and its items below are pending. For
delivery and review evidence, see [review.md](review.md), "Final review and delivery: PR-1a".

## Migrations (M4)

- **Repository kits:** re-run `li-copilot init` from a reviewed Lintel revision. Resolve any
  refusal, review and commit the regenerated files, then start a new Copilot session.
- **Plugin installations:** update the plugin through the route it was installed with.
- The steps, degradations and rollback are in the
  [migration guide](../../../docs/migrations/2026-09-28-copilot-native-parity.md), which has a row
  in `docs/migrations/_INDEX.md`.

## Conventions and deprecated paths

- **Regenerate after edits:** after editing a canonical skill or agent, regenerate and commit the
  native files, the catalog and the wiki:
  - `li-copilot.py init --target . --source .`
  - `li-catalog.py`
  - `li-wiki-gen`

  CI fails on drift.
- **Bash steps:** native skills run their Bash steps through `bin/li-run`.
- **Pointer files:** generated native files replace the pointer skills and role profiles. The
  migration guide's detect command finds leftovers.

## Pending

- **With PR-1b:** the repository `--hooks` opt-in, the plugin hook registration and
  `LINTEL_HOOKS_DISABLED`.
- **ADV-1 (Low):** the `bin/li-run` signal cleanup is not fixed.
- **Increment 2:** its entry point is the plan's "Increment 2" section. It is not authorized.
