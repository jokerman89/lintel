# Feature Request — Generic spine + packs + navigation (the Lintel reframe)

**Compiled:** 2026-05-28 · from a design conversation between operator and Claude.
**Status:** Standalone feature request (separate from `lintel-v3.6-backlog.md` and `lintel-feature-curated-flow-tracking.md`). Consolidated into v4.0 via [`.claude/engineering/design-archive/lintel-v4.0-reframe-design.md`](../design/lintel-v4.0-reframe-design.md) Chapter 1.
**Scope:** A reframing of what Lintel *is* — from a CAIP-SE tool with generic capabilities to a generic spine with CAIP-SE as one pack among many. Four chapters, shippable independently.

**Locked decisions (operator):**
- Packs live in `~/.lintel/packs/` (per-operator).
- CAIP-SE pack extraction is part of THIS request (FR-D).
- Orientator auto-mode runs at level (b): auto-starts low-risk workflows, confirms high-risk.
- One document, four chapters, independently shippable.

**Operator stance:** Bold, effective, operator carries the responsibility. The design assumes a capable operator, refuses padding for novice protection, and is opinionated about what spine demands from any workflow.

---

> Original full text is preserved in the project's external archive. This file is the canonical reference within the repo. v4.0 design doc consolidates and interprets — see [Chapter 1 of v4.0 reframe](../design/lintel-v4.0-reframe-design.md#chapter-1--generic-spine--packs--navigation) for the unified implementation plan.

## Summary of the four chapters

**FR-A — Generic spine extraction.** Audit Lintel's core for CAIP-SE-specific assumptions (Trailblazer voice, MS compliance hooks, sales-engineer persona, WorkProfile binding). Replace hardcoded references with a `PackResolver` shim. Ship an empty `_default` pack. Move CAIP-SE content out of core into a holding pen.

**FR-B — Pack architecture and lifecycle.** Per-operator `~/.lintel/packs/<name>/` with `pack.yaml` manifest declaring voice, compliance, persona, roles, brand, knowhow, lessons, opinions, navigation. Inheritance via `extends:`. Lifecycle skills (`pack-new`, `pack-switch`, `pack-edit`, `pack-remove`, `pack-list`, `pack-validate`, `pack-export`, `pack-import`, `pack-init-default`). Pack-validation hook.

**FR-C — Navigation as requirement.** Every `workflow_root: true` skill MUST declare `navigation:` block with `valid_entries`, `valid_exits`, `auto_mode_eligible`, `risk_level`. Orientator agent at SENSE reads request + pack + open jobs. Mechanical-first; LLM only on escalation. Auto-mode level (b) — auto-start low-risk, confirm high-risk.

**FR-D — CAIP-SE as reference pack.** Migrate existing CAIP-SE-specific content (Trailblazer corpus, MS hooks, personas, roles, brand templates) into `packs/caip-se/`. Activate as operator's default. Document as canonical pack-building example.

## Operator validation criteria

When all four ship, success looks like:

1. A colleague at Microsoft, not in CAIP-SE, clones the repo, runs `/li-pack-new`, builds their own pack in 10 minutes, uses Lintel without touching CAIP-SE content.
2. An indie builder clones the repo, runs `/li-cycle` with `_default` active, gets a clean cold-executor trio with no MS branding.
3. Operator's daily workflow unchanged — sourced from caip-se pack now, switching to `_default` removes MS context without breaking the spine.
4. Typing a vague request gets an auto-mode proposal in one line correct ≥80% of the time; high-risk workflows always confirm.
5. A workflow_root skill without `navigation:` block fails to load. The architectural guarantee holds.
6. Exporting caip-se and importing it on a different machine reproduces the setup exactly.

## Decisions still open

1. **D.3 — `ms-internal` base pack now or later?** Recommended now (clean inheritance). Cost is ~1 hour of structuring.
2. **Pack-versioning enforcement strictness** — warn-only or block-on-incompatible? Recommended warn-only for v1; block once pack ecosystem grows.
3. **Default `auto_mode_eligible` for new workflow_roots** — true or false by convention? Recommended `false` by default; operator opts in per workflow.

See [v4.0 design Chapter 1.2-1.4](../design/lintel-v4.0-reframe-design.md#chapter-1--generic-spine--packs--navigation) for AI interpretation + recommendations on each.
