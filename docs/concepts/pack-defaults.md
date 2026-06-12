# Pack-defaults — the neutral skeleton every workflow can fall back to

**Last updated:** 2026-05-29 (v4.0 Phase 1)
**Status:** Concept doc — referenced by `packs/_default/pack.yaml`, `lib/pack-resolver.sh`, `skills/cycle/SKILL.md` (meta-infra mode)

> Lintel as scaffolding has no opinions about voice, compliance, brand, or roles — those belong to whoever uses it. The `_default` pack is the **explicit neutral skeleton** that says "these are the fields a pack can set, and here is the harmless value Lintel falls back to when nothing sets them." It is the contract for what a pack must declare to be a pack.

## The problem

Every workflow in Lintel reads "pack-shaped" inputs — voice tier, compliance hooks, persona corpus, role inventory, brand language, knowhow domains, lessons surface, opinions, navigation tuning, brief-forge handoffs. Before v4.0 those values were inlined wherever they were needed:

- Trailblazer voice references baked into customer-facing skill copy.
- Compliance gate names hardcoded into REVIEW.
- Persona corpus assumed by skills that referenced "Kennie" or "Lisa" by name.
- Navigation budget assumed by orientator.

That meant Lintel-the-harness and Microsoft-the-pack were tangled. Two consequences:

1. A second pack (e.g. Foo Corp) could not be added without forking Lintel.
2. A first-time operator on a clean repo with no active pack would crash on missing values instead of getting a sane neutral fallback.

## The model

```
packs/
├── _default/
│   └── pack.yaml          ← neutral skeleton, lives in the harness, never edited per-customer
├── microsoft/
│   └── pack.yaml          ← Trailblazer + Compliance + Personas + Voice corpus
└── <future-pack>/
    └── pack.yaml
```

The active pack is selected by `~/.lintel/active-pack` (a single-line file naming a packs/ directory). When no active pack is selected, `_default` is used.

`_default/pack.yaml` carries every declarable field with a neutral or empty value. The harness assumes nothing beyond what `_default` declares.

## What `_default` declares

```yaml
schema_version: "4.0"
requires_lintel: ">=4.0.0"

voice:
  tier_default: internal          # internal | trailblazer | mixed
  corpus: []                       # no brand corpus by default
  gates_active: []                 # no voice gates unless pack opts in

compliance:
  hooks_active: []                 # no compliance gates unless pack opts in
  audit_paths: []

persona:
  inventory: []                    # no personas by default
  corpus_path: null

roles:
  active: []
  inventory_path: null

brand:
  name: null
  short: null
  copy_tone: neutral

knowhow:
  domains: []
  corpus_path: null

lessons:
  surface_on_sense: true           # generic mechanism, always on
  paths: [".claude/memory/lessons.md"]

opinions:
  inventory: []

navigation:
  orientator_budget_tokens: 2000
  escalation_threshold: medium      # low | medium | high

brief_forge_handoffs:
  budget_tokens: 5000
  cold_path_bypass: true            # operator can skip Brief Forge with --no-handoff
  types:
    - operator_to_skill              # standard hand-off
    - skill_to_skill                 # within-cycle propagation
    - skill_to_agent                 # spawn-time brief
    - cycle_to_cycle                 # resume context
    - external_to_cycle              # cold ingestion (chat-import etc.)
```

Every field is declared even when empty. That is the contract: a pack overriding `_default` sees the full surface area it can opt into. A new pack author copies `_default/pack.yaml`, fills in what they want, and ships.

## How resolution works

`lib/pack-resolver.sh` is the only path through which scaffolding reads pack values. Workflows never `grep packs/ directly`. The resolver:

1. Reads `~/.lintel/active-pack` (or returns `_default` if missing).
2. Validates the pack file exists, parses, and declares required fields. On failure: warn + fall back to `_default`.
3. Caches the resolved values per-session in `${LINTEL_HOME}/sessions/<session-id>-pack-cache.yaml`.
4. Serves `resolve_pack_field <dotted.path>` calls from cache; falls back to `_default` if the active pack omits the path; falls back to a hardcoded resolver default if `_default` itself is malformed.

Three layers of fallback (active → `_default` → hardcoded) means a missing or broken pack never crashes a workflow — it degrades.

See [pack-resolver.md](pack-resolver.md) for the resolution machinery in detail.

## What `_default` does not declare

Anything that requires a value to function. If Lintel cannot proceed without a value, the resolver fails loud rather than guessing.

Examples:
- `voice.gates_active` is `[]` in `_default` because no voice gate is required to ship.
- `compliance.hooks_active` is `[]` in `_default` because no compliance gate is required to ship.
- `persona.inventory` is `[]` because persona-bound skills check inventory before referencing personas.

A workflow that requires a value the resolver cannot produce (active pack didn't set it, `_default` didn't declare it) must surface the gap, not silently substitute.

## Why this matters for meta-infra mode

Changes to `_default/pack.yaml` ripple to every downstream cycle on every pack. That is why edits to `packs/_default/` automatically activate meta-infra mode (Gate M1 structure-impact, M2 compatibility audit). A field added to `_default` is a new contract surface; a field renamed in `_default` breaks every pack that referenced the old name.

The structure-changes/<date>-<slug>.md entry for any `_default` edit must document:
- What changed (field added/removed/renamed)
- Backward-compat (will existing packs still resolve?)
- Migration path (how should pack authors update?)
- Forward-compat (does the new shape leave room?)

## Integration points

**Reads:**
- `packs/_default/pack.yaml` — declared by the harness, never edited per-customer
- `packs/<active>/pack.yaml` — declared per pack
- `~/.lintel/active-pack` — single-line pack name

**Writes:**
- `${LINTEL_HOME}/sessions/<session-id>-pack-cache.yaml` — session-scoped cache

**Triggers:**
- Every workflow that needs pack-shaped input calls `resolve_pack_field` from `lib/pack-resolver.sh`

## Anti-patterns

- **Inlining pack values into workflows** — every reference goes through the resolver
- **Editing `_default` per-customer** — `_default` is the harness contract; per-customer values live in a real pack
- **Adding a field to `_default` without a structure-changes entry** — every `_default` edit is meta-infra mode
- **Falling back silently when a required field is missing** — surface the gap, do not guess
