# ADR-0018: extension-pack contract — packs may ship skills, agents, hooks, and a workflow

- **Status:** Accepted
- **Date:** 2026-06-14
- **Deciders:** operator (S4L initiative, decision D1)
- **Supersedes:** —
- **Superseded by:** —

## Context

A Lintel pack today is **identity only**: `packs/<name>/pack.yaml` declares voice, compliance,
persona, roles, brand, knowhow, navigation, lessons, opinions — and `pack-create` scaffolds nothing
else. The executable surface (skills, agents, hooks, the cycle) lives in the Lintel plugin and is
fixed; a pack can point `navigation.default_workflow` at a workflow but cannot *bring its own*.

The Set4Life (S4L) initiative needs a pack that ships its **own** skills (~25-30 marketing prompts),
its **own** agents (marketing personas), its **own** hooks (claim-honesty / offer-completeness
gates), and its **own** cycle-like workflow (`/s4l:forge`, 12 phases, Path A/B/C modes) — a complete
domain product on top of Lintel's spine, in its own repo, installable like any pack. That is beyond
what the current pack contract allows.

Constraints that are non-negotiable: the change must be **additive** (the ~30 spine skills depend on
the pack contract — frozen zone; identity-only packs must be entirely unaffected), behind shape
tests, and must keep packs company-neutral (no S4L specifics leak into the spine).

## Decision

We extended the pack contract so a pack may be an **extension pack**: a pack repo that is *also* a
Claude Code plugin. It ships `skills/ agents/ hooks/` in the plugin-standard layout (so each host CLI
discovers them natively, with namespacing and hook auto-registration handled by the platform) **and**
carries a `pack.yaml` with a new optional `extension:` block that declares its identity to Lintel:

```yaml
extension:
  is_extension: true        # ships executable surface
  namespace: s4l            # skill/agent prefix the host CLI applies (/s4l:…)
  workflow: s4l-forge       # the pack's own cycle (also mirrored to navigation.default_workflow)
  provides_skills: true     # awareness flags — Lintel surfaces, never re-implements discovery
  provides_agents: true
  provides_hooks: true
```

The block is deliberately **flat (two-level)**: `resolve_pack_field` is a two-level
`parent.key` resolver, so a nested `provides:` sub-block would not resolve. `validate_pack`
enforces that `namespace` + `workflow` are present whenever `is_extension: true`.

Lintel's spine gains *awareness* of pack-shipped surface (resolver, `pack-switch`, `catalog`,
`doctor`, `help`, cycle footer) but does **not** re-implement discovery — the platform plugin loader
already does that. `bin/li-pack-scaffold` scaffolds the extension-pack skeleton.

## Alternatives considered

- **Plugin + pack hybrid with no core change** (the originally-recommended option): ship S4L purely
  as a separate plugin and lean on a plain identity `pack.yaml`. Rejected by the operator: Lintel
  would have no first-class notion of a pack that brings a workflow/skills, so `pack-switch`,
  `catalog`, `doctor`, and the orientator would be blind to it — extension packs would be second-class.
- **Runtime-load skills from `packs/<name>/skills/`**: have Lintel itself load a pack's skills at
  runtime. Rejected — host CLIs discover skills via plugin manifests, not arbitrary runtime paths;
  this would fork discovery, break namespacing/hook-registration, and not port across the 8 CLIs.
- **Bake S4L into the Lintel repo**: rejected — couples a sellable marketing product to the
  company-neutral harness and violates the spine's neutrality.

## Consequences

- **Positive:** packs become first-class *capability* extensions, not just identity skins. S4L (and
  any future domain pack) ships a complete workflow+skills+agents+hooks product in its own repo,
  installable via `/plugin install` + `/li:pack-switch`. The platform does the heavy lifting
  (discovery, namespacing, hook registration); Lintel adds awareness + scaffolding.
- **Negative:** the pack contract grows (a new optional block) and several spine skills gain
  pack-awareness branches — more surface to keep correct, guarded by a new shape test. Two layers
  (plugin manifest + pack.yaml) must stay consistent in an extension pack.
- **Neutral:** identity-only packs are unchanged (`extension:` absent ⇒ `is_extension:false`). The
  `_default` pack documents the block as null/false.

## Implementation notes

Meta-infra (M1–M4): `.claude/engineering/evolution/<date>-extension-pack-contract.md`; `li-compat-audit`
(expect GREEN — additive, no default changed); shape test `tests/shape/extension-pack-contract.sh`
(asserts the `extension:` block schema + that `_default` keeps it off + resolver tolerance); migration
note (none required for existing packs). Sequencing: schema + resolver → pack-switch/catalog/doctor
awareness → scaffolder → tests → green suite → PR. Then the S4L pack (separate repo) consumes it.

## References

- `.claude/plans/s4l-extension-pack/todo.md` (the initiative plan + wave breakdown)
- `packs/_default/pack.yaml` (the pack contract), `lib/pack-resolver.sh`, `skills/pack-create/`
- ADR-0015 (AGENTS.md primary), the v4.0 pack system (resolve_pack_field)
