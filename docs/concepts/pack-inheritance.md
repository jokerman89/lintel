# Pack inheritance — shallow merge with explicit precedence

**Last updated:** 2026-09-08
**Status:** Concept doc — referenced by `lib/pack-resolver.sh` (`_resolve_extends_chain`, `_merge_packs_into_cache`), `lib/pack-schema.yaml`, `tests/unit/pack-inheritance-depth-3.sh`

> Pack ecosystems have variation: two packs from the same organisation share a set of defaults (compliance hooks, regulatory gates, audit paths) but differ on voice, persona, brand. Without inheritance, every new pack restates the shared defaults — drift becomes inevitable. With inheritance, the shared defaults live in a base pack (`acme-base`) and concrete packs (`acme-eng`, `acme-sales`) extend it. The mechanism is **shallow merge with explicit child-over-parent precedence**.

## The problem

Three failure modes a flat pack ecosystem invites:

1. **Drift across siblings.** `acme-eng` and `acme-sales` both want the same compliance hooks active. If both restate the hook list, they drift when one is updated without the other.
2. **Restatement burden.** A new pack author wanting the organisation's shared defaults must copy every field from a sibling pack. Mistakes happen.
3. **Hidden assumptions.** When `acme-eng` declares `compliance.mode: hard`, is that intentional or inherited from the organisation's base? Without an explicit `extends:` chain, the answer is invisible.

Inheritance solves all three:
- Drift: shared defaults change in one place.
- Burden: new pack declares only what differs.
- Visibility: `extends: acme-base` is the operator's explicit statement of inheritance intent.

## The model

```
_default                  ← Lintel's neutral skeleton (resolver fallback)
   ↑
   │ (NOT extends — _default is the resolver's fallback layer,
   │  not a parent in the extends chain)
   │
acme-base                 ← organisation-wide base
   ↑
   │ extends: acme-base
   │
acme-eng                  ← team-specific
   ↑
   │ extends: acme-eng
   │
foo-customer              ← (future) customer-specific
```

Two distinct mechanisms:
- **`extends:` chain** — operator-declared inheritance from one pack to another. Walked by `_resolve_extends_chain` in the resolver.
- **`_default` fallback** — resolver's last-resort layer for fields the active chain doesn't declare. Three-layer fallback per [pack-resolver.md](pack-resolver.md).

These are NOT the same. A pack that extends nothing still gets `_default` as a fallback layer; a pack that extends `acme-base` gets the explicit `acme-base → child` merge PLUS `_default` as the last-resort fallback for anything still missing.

## Shallow merge semantics

When the resolver primes the cache for pack `acme-eng` (which extends `acme-base`), it walks the chain root → leaf and merges manifests into a single resolved cache file:

1. Start with `acme-base/pack.yaml` content
2. For each top-level key in `acme-eng/pack.yaml`, **replace the corresponding block from the cache wholesale**
3. Write the merged result to `${LINTEL_HOME}/sessions/<session>-pack-cache.yaml`

Top-level keys in pack manifests include: `voice`, `compliance`, `navigation`, `persona`, `roles`, `brand`, `knowhow`, `lessons`, `opinions`, `brief_forge_handoffs`.

**Shallow means:** if `acme-eng` declares `voice:` at all, it REPLACES `acme-base`'s entire voice block. It does not deep-merge sub-fields.

### Why shallow, not deep

Deep-merge produces surprising hybrid states. Consider:

```yaml
# acme-base
voice:
  default_tier: mixed
  gates_active: [voice_critic]

# acme-eng
voice:
  default_tier: internal
```

**Deep merge** would produce `{default_tier: internal, gates_active: [voice_critic]}` — but `voice_critic` was the base pack's choice, and the operator authoring `acme-eng` may not have considered it. They get a hybrid they didn't write.

**Shallow merge** produces `{default_tier: internal}` — and if `acme-eng` wants `voice_critic` too, they list it explicitly. The operator's pack manifest is what runs; no hidden inherited residue.

The cost: every block-level field in a child pack must restate what the operator wants from the parent. The benefit: the child manifest is self-documenting. You read `acme-eng/pack.yaml` and see exactly what is active.

### Evaluator lists follow the same rule

Declaring `brief_forge_handoffs` replaces that entire parent block, including its
evaluator lists. Lists are not concatenated or deduplicated. A child adding an
evaluator must declare every hand-off setting and evaluator it intends to retain.
Omitting the whole block inherits it unchanged. This is the same whole-block rule
described in [the architecture](../architecture.md#resolution-and-inheritance).

## Chain depth + cycle detection

Maximum ancestry: ten parent links. The resolver rejects a chain needing an
eleventh link instead of loading a truncated policy.

Cycle detection: if pack A declares `extends: B` and pack B declares `extends: A` (or any longer cycle through the chain), `validate_pack` refuses activation and falls back to `_default`. Audited.

Cycle test: `tests/unit/pack-resolver-fallbacks.sh` scenario 4.

## Three-level chain example

`foo-customer extends acme-eng extends acme-base`:

1. `_resolve_extends_chain foo-customer` returns: `acme-base acme-eng foo-customer`
2. Cache merge order: acme-base contents → overlay acme-eng → overlay foo-customer
3. Each later overlay wholesale-replaces matching top-level blocks

If `foo-customer` declares no `voice:` block, the cache retains `acme-eng`'s voice. If `foo-customer` declares `voice: {default_tier: custom}`, the cache shows only `{default_tier: custom}` (acme-base AND acme-eng voice blocks both gone).

Tested by `tests/unit/pack-inheritance-depth-3.sh`.

## Missing parent + missing fields

Two distinct failures:

**Missing parent:** `acme-eng extends acme-base` but `acme-base/pack.yaml` doesn't exist. `validate_pack acme-eng` fails (audited), resolver falls back to `_default`.

**Missing field in chain:** the resolver uses that field's neutral `_default`
value; `voice.corpus`, for example, resolves to `null`. Explicit `null`, `false`
and `[]` remain explicit. A field absent from both the effective pack and the
neutral pack returns empty. Required policy fields must exist in the effective
ancestry before activation; fallback does not make an incomplete policy valid.

## Audit trail

Cache priming with an inheritance chain logs the chain to `${LINTEL_HOME}/audit/pack-resolver.jsonl`:

```jsonl
{"ts":"2026-05-29T15:00:00Z","kind":"pack_resolver_cache_primed","msg":"pack=acme-eng chain=acme-base acme-eng session=42071"}
```

The chain is recorded by the shared audit writer and can be inspected in the pack
resolver audit log. `LINTEL_AUDIT_DIR` can select a different audit destination.

## When inheritance is the wrong tool

Inheritance is for shared baseline values across packs that have a common ancestor concept (an organisation's shared defaults, customer-engagement work). It is NOT for:

- **Per-workflow overrides** — use the supported `--mode` or phase-range flags on `/li:cycle`
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
- **Editing parent to fix child** — if `acme-eng` needs `voice.gates_active: [brand_alignment]`, declare it in `acme-eng/pack.yaml`, not by sneaking it into `acme-base`
