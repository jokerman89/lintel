---
slug: activation-contract
date: 2026-06-12
cycle_id: activation-20260612
operator: jokerman
affected_paths:
  - hooks/hooks.json (new — plugin auto-registration)
  - hooks/claude-code/session-digest.settings.json (path fix)
  - lib/state.sh (new — state ledger helper)
  - skills/ (11 phase/orchestrator skills wired to state_append)
  - install/install.sh (identity seeding)
  - bin/li-doctor (hook drift + auto-registration checks)
  - tests/integration/session-leaves-traces.sh (new — behavior test)
  - all 6 CLI manifests (version 5.0.0)
risk_class: medium
breaking_change: false
---

# Structure change: activation-contract

> Gate M1 artifact — ADR-0008.

## What changed (shape)

New plugin-level `hooks/hooks.json` auto-registers session-digest + 4 safety hooks +
memory-budget-warn on plugin install. New `lib/state.sh` (state_append/state_last); the 9
phase skills + cycle + resume now write the 00-state ledger via one command instead of
hand-authored YAML blocks. install.sh seeds profile.yaml + active-pack. All hook run.sh files
are now 100755 in the index. Manifests 4.9.0 → 5.0.0.

## Backward-compat

Additive. Legacy settings-merge path still works (snippet fixed). Operators with MANUAL hook
entries in ~/.claude/settings.json will double-fire the 4 safety hooks after updating the
plugin — remove the manual entries (one-time; harmless but noisy until done). State files
written by state_append parse identically for the footer/resume.

## Migration path

See _INDEX.md row `v5-hook-autoregistration`: update plugin → remove manual hook entries →
re-run install.sh (refreshes ~/.lintel hooks + seeds identity) → `li-doctor` verifies.

## Forward-compat

New mechanisms must ship with (a) an activation path that requires no manual merge and (b) a
behavior test in tests/integration that asserts the trace, not the prose.

## Verification

- tests/integration/session-leaves-traces.sh — 31 assertions, ALL PASS
- full suite green (see PR)
- li-doctor: hook drift + auto-registration checks live

## Rollback

git revert; removing hooks/hooks.json de-registers the plugin hooks on next update; manual
settings entries (if kept) continue to work as before.
