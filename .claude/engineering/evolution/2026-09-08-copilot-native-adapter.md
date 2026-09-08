---
slug: copilot-native-adapter
date: 2026-09-08
cycle_id: copilot-enterprise-launch
operator: repository-maintainer
affected_paths:
  - .github/
  - bin/
  - lib/cli-tiers.yaml
  - skills/
  - scaffolding/
  - install/
  - tests/
risk_class: medium
breaking_change: false
---

# Structure change: Copilot native adapter

## What changed

Add host-native generated Copilot entry files, offline adapter init/check, explicit CLI plugin
metadata, a Spec Kit workflow bridge and installation/CI validation. See ADR-0024 and the
copilot-enterprise-launch plan for contracts and acceptance criteria.

## Compatibility and migration

Canonical paths, pack resolver schema and existing Claude hooks are preserved. No migration is
required for existing users. Copilot users opt into `li-copilot init` or `li-scaffold --copilot`.
Managed-file conflicts stop with actionable guidance; user-owned content is preserved.

## Verification and rollback

Run adapter integration tests, complete existing suite, installed-runtime verification and generated
artifact checks. Revert the initiative commits to remove the new source feature. In consumer repos,
review and revert the adapter installation commit; do not bulk-delete .github or user files.

## Forward compatibility

Explicit native adapters allow Copilot to evolve without weakening the shared instruction/pack
contract. Hooks need a separate tested schema adapter before claiming Lintel enforcement on Copilot.
