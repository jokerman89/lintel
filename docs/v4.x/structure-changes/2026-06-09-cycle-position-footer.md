---
slug: cycle-position-footer
date: 2026-06-09
cycle_id: cycle-2026-06-09-footer
operator: Azureflipper
affected_paths:
  - lib/cycle-modes.sh
  - lib/cycle-footer.sh
  - tests/unit/cycle-footer.sh
  - skills/cycle/SKILL.md
  - skills/code-review/SKILL.md
  - docs/adr/0003-cycle-position-footer.md
risk_class: low
breaking_change: false
---

# Structure change: cycle-position-footer

> Gate M1 (structure-impact analysis) artifact. Authored in BUILD (Phase 1) per ADR-0003.

## What changed (shape)

Two new `lib/` helpers + one new output convention:

- `lib/cycle-modes.sh` — the canonical 9-step order (8 core phases + SCOPE) + the mode→skipped map, defined once.
  Previously the skip behaviour was implicit only in the `skills/cycle/SKILL.md` preset prose.
- `lib/cycle-footer.sh` — `render_cycle_footer`, a 3-tier (full / compact / thin) position footer
  read from the existing `.lintel/state/00-state.md` append-log. No state schema change: it *reads*
  the already-written `phase:` / `status:` / `next_recommended:` keys and an optional `cycle_mode:`.
- `skills/cycle/SKILL.md` — one new closing-step instruction (render the footer at phase boundaries).
- Bundled fix (P0-1): `skills/code-review/SKILL.md` frontmatter `name: review` → `name: code-review`
  (was colliding with `skills/review`, silently dropping it from the catalog).

## Backward-compat

Fully additive. No existing skill, agent, hook, or shape contract changes behaviour. Skills that do
not yet call `render_cycle_footer` are unaffected (Phase-2 work, tracked). The `name:` fix only
*restores* a skill that was being dropped — no existing invocation path changes (`/li:code-review`
was always the dir-derived namespace; only the catalog dedup was wrong).

## Migration path

No migration needed — additive change. Optional forward step (Phase 3): the orchestrator will write
`cycle_mode:` into `00-state.md` so the footer reads mode from state without `--mode`; until then it
falls back to env/explicit/“skip nothing”, which is harmless.

## Forward-compat

Enables: a single, mode-aware position indicator reusable by every official skill; a shared skip-map
both the footer and the cycle presets can consume (kills future drift). Forecloses nothing — tiers
and glyph sets are parameterised, so new modes/CLIs extend the data, not the code.

## Verification

- Shape-tests added: none yet (Phase 2 adds `tests/shape/cycle-footer-present.sh` once the 9 phase
  skills are wired — a presence check would currently fail by design).
- Unit-tests added: `tests/unit/cycle-footer.sh` (30 assertions — tiers, skip precedence, positional
  done-state, ASCII fallback, state-file parse, question-mode, complete→thin).
- Existing shape-tests affected: none. `bash -n` clean on both helpers.
- Regression coverage: full suite re-run green (see BUILD evidence).

## Rollback procedure

Additive + isolated. To revert: `git rm lib/cycle-modes.sh lib/cycle-footer.sh
tests/unit/cycle-footer.sh docs/adr/0003-cycle-position-footer.md` and revert the single closing-step
edit in `skills/cycle/SKILL.md`. The `code-review` `name:` fix should be kept independently (it fixes
a separate, pre-existing P0). No state or contract cleanup required.
