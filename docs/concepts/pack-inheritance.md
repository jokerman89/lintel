# Pack inheritance — shallow merge with explicit precedence

**Last updated:** 2026-05-29 (v4.0 Phase 2)
**Status:** Concept doc — referenced by `lib/pack-resolver.sh` (`_resolve_extends_chain`, `_merge_packs_into_cache`), `lib/pack-schema.yaml`, `tests/unit/pack-inheritance-depth-3.sh`

> Pack ecosystems have variation: a CAIP-SE pack and a future Foo-Corp pack will share MS-internal-ish defaults (compliance hooks, SDL gates, audit paths) but differ on voice, persona, brand. Without inheritance, every new pack restates the shared defaults — drift becomes inevitable. With inheritance, the shared defaults live in a base pack (`ms-internal`) and concrete packs (`caip-se`, `foo-corp`) extend it. The mechanism is **shallow merge with explicit child-over-parent precedence**.

## The problem

Three failure modes a flat pack ecosystem invites:

1. **Drift across siblings.** `caip-se` and `foo-corp` both want SDL hooks active. If both restate the SDL hook list, they drift when one is updated without the other.
2. **Restatement burden.** A new pack author wanting MS-internal defaults must copy every field from a sibling pack. Mistakes happen.
3. **Hidden assumptions.** When `caip-se` declares `compliance.mode: hard`, is that intentional or inherited from MS-internal context? Without an explicit `extends:` chain, the answer is invisible.

Inheritance solves all three:
- Drift: shared defaults change in one place.
- Burden: new pack declares only what differs.
- Visibility: `extends: ms-internal` is the operator's explicit statement of inheritance intent.

## The model

```
_default                  ← Lintel's neutral skeleton (resolver fallback)
   ↑
   │ (NOT extends — _default is the resolver's fallback layer,
   │  not a parent in the extends chain)
   │
ms-internal               ← Microsoft-internal base
   ↑
   │ extends: ms-internal
   │
caip-se                   ← CAIP-SE-specific
   ↑
   │ extends: caip-se
   │
foo-customer              ← (future) customer-specific
```

Two distinct mechanisms:
- **`extends:` chain** — operator-declared inheritance from one pack to another. Walked by `_resolve_extends_chain` in the resolver.
- **`_default` fallback** — resolver's last-resort layer for fields the active chain doesn't declare. Three-layer fallback per [pack-resolver.md](pack-resolver.md).

These are NOT the same. A pack that extends nothing still gets `_default` as a fallback layer; a pack that extends `ms-internal` gets the explicit `ms-internal → child` merge PLUS `_default` as the last-resort fallback for anything still missing.

## Shallow merge semantics

When the resolver primes the cache for pack `caip-se` (which extends `ms-internal`), it walks the chain root → leaf and merges manifests into a single resolved cache file:

1. Start with `ms-internal/pack.yaml` content
2. For each top-level key in `caip-se/pack.yaml`, **replace the corresponding block from the cache wholesale**
3. Write the merged result to `${LINTEL_HOME}/sessions/<session>-pack-cache.yaml`

Top-level keys in pack manifests include: `voice`, `compliance`, `navigation`, `persona`, `roles`, `brand`, `knowhow`, `lessons`, `opinions`, `brief_forge_handoffs`.

**Shallow means:** if `caip-se` declares `voice:` at all, it REPLACES `ms-internal`'s entire voice block. It does not deep-merge sub-fields.

### Why shallow, not deep

Deep-merge produces surprising hybrid states. Consider:

```yaml
# ms-internal
voice:
  default_tier: mixed
  gates_active: [voice_critic]

# caip-se
voice:
  default_tier: trailblazer
```

**Deep merge** would produce `{default_tier: trailblazer, gates_active: [voice_critic]}` — but `voice_critic` was an MS-internal choice, and the operator authoring `caip-se` may not have considered it. They get a hybrid they didn't write.

**Shallow merge** produces `{default_tier: trailblazer}` — and if `caip-se` wants `voice_critic` too, they list it explicitly. The operator's pack manifest is what runs; no hidden ms-internal residue.

The cost: every block-level field in a child pack must restate what the operator wants from the parent. The benefit: the child manifest is self-documenting. You read `caip-se/pack.yaml` and see exactly what is active.

### The one exception

`brief_forge_handoffs.<event>.evaluators` arrays merge by concatenation + dedup. Reason: evaluators are additive by nature — a child rarely wants to remove a parent's evaluator, but often wants to add its own. Concatenation matches operator intent without the deep-merge surprise. This exception is documented in `lib/pack-schema.yaml` and tested in the inheritance unit harness.

## Chain depth + cycle detection

Maximum chain depth: 10. A pack that declares `extends: <name>` triggers the resolver to walk up the chain until it finds a root (a pack without `extends:`) or hits depth 10.

Cycle detection: if pack A declares `extends: B` and pack B declares `extends: A` (or any longer cycle through the chain), `validate_pack` refuses activation and falls back to `_default`. Audited.

Cycle test: `tests/unit/pack-resolver-fallbacks.sh` scenario 4.

## Three-level chain example

`foo-customer extends caip-se extends ms-internal`:

1. `_resolve_extends_chain foo-customer` returns: `ms-internal caip-se foo-customer`
2. Cache merge order: ms-internal contents → overlay caip-se → overlay foo-customer
3. Each later overlay wholesale-replaces matching top-level blocks

If `foo-customer` declares no `voice:` block, the cache retains `caip-se`'s voice. If `foo-customer` declares `voice: {default_tier: custom}`, the cache shows only `{default_tier: custom}` (ms-internal AND caip-se voice blocks both gone).

Tested by `tests/unit/pack-inheritance-depth-3.sh`.

## Missing parent + missing fields

Two distinct failures:

**Missing parent:** `caip-se extends ms-internal` but `ms-internal/pack.yaml` doesn't exist. `validate_pack caip-se` fails (audited), resolver falls back to `_default`.

**Missing field in chain:** chain resolves but no pack in the chain declares `voice.corpus`. Resolver returns empty (or hardcoded fallback if `voice.corpus` is in the known-critical list). Workflow that needs this field decides what to do — surface or substitute.

## Audit trail

Cache priming with an inheritance chain logs the chain to `${LINTEL_HOME}/audit/pack-resolver.jsonl`:

```jsonl
{"ts":"2026-05-29T15:00:00Z","kind":"pack_resolver_cache_primed","msg":"pack=caip-se chain=ms-internal caip-se session=42071"}
```

The chain field surfaces in `bin/li-doctor --packs` for operator inspection.

## When inheritance is the wrong tool

Inheritance is for shared baseline values across packs that have a common ancestor concept (MS-internal work, customer-engagement work). It is NOT for:

- **Per-workflow overrides** — use `--mode` or `--pack <name>` flags on `/li:cycle`
- **One-off field tweaks** — edit the pack manifest directly
- **Pack composition** — Lintel v4.0 does not support multi-parent inheritance. A pack has 0 or 1 parents. Multi-parent (diamond inheritance) is rejected by `validate_pack` if attempted via two `extends:` declarations.

## Integration points

**Reads:**
- `packs/<name>/pack.yaml` (one or more, depending on chain depth)

**Writes:**
- `${LINTEL_HOME}/sessions/<session>-pack-cache.yaml` (merged manifest)
- `${LINTEL_HOME}/audit/pack-resolver.jsonl` (chain audit)

**Public functions in lib/pack-resolver.sh:**
- `_resolve_extends_chain <name>` — returns space-separated chain (root → leaf)
- `_merge_packs_into_cache <chain>` — writes merged manifest to cache
- (Both are private-by-convention but useful from inheritance tests.)

## Anti-patterns

- **Deep-merge expectation** — chain inheritance is shallow; child block replaces parent block
- **Diamond inheritance** — `extends:` is a single string, not a list
- **Inheritance for one-off overrides** — use mode/flag instead
- **Skipping the explicit `extends:`** — implicit inheritance through naming convention is brittle
- **Editing parent to fix child** — if `caip-se` needs `voice.gates_active: [trailblazer_alignment]`, declare it in `caip-se/pack.yaml`, not by sneaking it into `ms-internal`
