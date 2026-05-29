# Pack-resolver — single critical-path lookup with explicit failure semantics

**Last updated:** 2026-05-29 (v4.0 Phase 1)
**Status:** Concept doc — referenced by `lib/pack-resolver.sh`, `tests/shape/pack-resolver-fallbacks.sh`, `tests/unit/pack-resolver-fallbacks.sh`

> Thirty-plus skills read pack-shaped state — voice tier, compliance mode, navigation budgets, brief-forge handoff caps. If each grepped `packs/<active>/pack.yaml` directly, every skill would carry the same parsing logic, every skill would degrade differently on malformed input, and every pack-schema change would ripple to thirty-plus call sites. The pack-resolver is the **single sourced lookup function**: it parses once per session, caches per session, surfaces explicit failure semantics, and is the only thing in Lintel that reads pack manifests.

## The problem

Before the resolver, "read the active pack" meant either:
- Inline `grep -E '^voice_tier:' packs/microsoft/pack.yaml` everywhere, or
- A loose convention that each skill should look up its own values.

That created three failure surfaces:

1. **Parsing drift.** A skill that expected `voice_tier:` would silently misread `voice:\n  tier_default:` after the schema nested it.
2. **Failure invisibility.** A skill with a typo'd field path would get an empty string and proceed — no warning, no audit trail.
3. **Pack-switch ambiguity.** Operator switches active-pack mid-session; some skills read the new value, others held the old. Race conditions across phases.

The resolver fixes all three by being **the only path** through which pack values are read.

## The model

```
Operator                    Skill                  pack-resolver               Filesystem
   │                          │                         │                          │
   │                          │  source pack-resolver   │                          │
   │                          │────────────────────────►│                          │
   │                          │                         │                          │
   │                          │  resolve_pack_field     │  _prime_cache (once)    │
   │                          │────────────────────────►│─────────────────────────►│
   │                          │                         │   read active-pack       │
   │                          │                         │   validate manifest      │
   │                          │                         │   copy to session-cache  │
   │                          │                         │◄─────────────────────────│
   │                          │                         │                          │
   │                          │                         │   read from cache        │
   │                          │◄────────────────────────│                          │
   │                          │  "internal"             │                          │
```

Cache is per-session at `${LINTEL_HOME}/sessions/<session-id>-pack-cache.yaml`. Cache survives pack-switches mid-cycle (the cycle reads the pack it started with). Cache is rebuilt at next session.

## Failure semantics (9 scenarios)

The resolver has explicit behavior for nine failure modes, asserted by `tests/unit/pack-resolver-fallbacks.sh`:

| # | Scenario | Resolver behavior |
|---|----------|-------------------|
| 1 | No active-pack file | Returns `_default` values; no warning (this is the supported empty state) |
| 2 | Active-pack file names an existing pack | Returns pack's values |
| 3 | Active-pack file names a pack that doesn't exist | Falls back to `_default`, warns to stderr, audits to `pack-resolver.jsonl` |
| 4 | Active pack has `extends:` cycle (a → b → a) | Refuses activation, falls back to `_default`, audits |
| 5 | Active pack missing required field (`name`, `version`, `voice`, `compliance`, `navigation`) | Refuses load, falls back to `_default`, audits |
| 6 | Concurrent reads in same session | All readers see identical cached value (immutable per session) |
| 7 | Operator changes `active-pack` mid-cycle | Current cycle keeps its cached pack; next session picks up new pack |
| 8 | Pack file deleted after cache is primed | Cache survives; resolver continues serving cached values until session ends |
| 9 | Active-pack explicitly = `_default` | Returns neutral skeleton values; no warning |

Every scenario is exercised by an isolated `LINTEL_HOME` in `tests/unit/pack-resolver-fallbacks.sh`. The shape-test wrapper at `tests/shape/pack-resolver-fallbacks.sh` runs the unit harness as part of meta-infra Gate M3.

## Three layers of fallback

When a workflow calls `resolve_pack_field voice.tier_default`:

1. **Active pack's value.** Read from session cache.
2. **`_default` pack's value.** If active pack omits the field, the cache (primed from active) won't contain it. Resolver re-reads `_default/pack.yaml` for the missing field. (Phase 2: cache will merge active over `_default` at prime time; Phase 1 reads on demand.)
3. **Hardcoded resolver default.** If both packs omit, the resolver returns a baked-in neutral default for known critical fields:
   - `voice.default_tier` → `internal`
   - `compliance.mode` → `advisory`
   - `compliance.workprofile_default` → `off`
   - `navigation.default_workflow` → `cycle`
   - `navigation.orientator_budget_tokens` → `2000`
   - `navigation.orientator_max_output_tokens` → `200`
   - `navigation.escalation_threshold` → `medium`
   - `brief_forge_handoffs.budget_tokens` → `5000`

For paths not in the hardcoded list, the resolver returns empty string. Workflows that need a value must either declare a hardcoded fallback themselves or surface the gap (per L-004: decisions are explicit, not silent).

## Caching strategy

- **Cache key:** `${LINTEL_HOME}/sessions/${LINTEL_SESSION_ID}-pack-cache.yaml`
- **Cache contents:** a copy of the active pack's `pack.yaml` at prime time
- **Cache lifetime:** session (PPID-bound)
- **Cache invalidation:** explicit `clear_pack_cache` call or next session
- **Cache priming:** lazy — first `resolve_pack_field` call triggers `_prime_cache_for_session`, subsequent calls hit cache

Why session-bound rather than cycle-bound? Sessions can run multiple cycles. The expectation is that the active pack doesn't shift mid-session — if it does, the operator gets the pack they had when the cycle started. Mid-cycle pack-switch is deferred to Phase 3.

## Audit trail

Every fallback, warning, and cache-prime event is appended to `${LINTEL_HOME}/audit/pack-resolver.jsonl`:

```jsonl
{"ts":"2026-05-29T14:32:01Z","kind":"pack_resolver_cache_primed","msg":"pack=microsoft session=42071"}
{"ts":"2026-05-29T14:35:18Z","kind":"pack_resolver_warn","msg":"active pack 'foo-corp' invalid; falling back to _default"}
{"ts":"2026-05-29T14:35:19Z","kind":"pack_resolver_cache_primed","msg":"pack=_default session=42071"}
```

This is what Gate M2 (compatibility audit) inspects when checking whether a recent change broke pack resolution downstream.

## Why this matters for meta-infra mode

The resolver is critical-path: 30+ skills source it. A breaking change here breaks every workflow on every pack. Edits to `lib/pack-resolver.sh` therefore activate meta-infra mode automatically (Step 0c in SENSE detects `lib/` in cwd diff).

Specifically, Gate M2 (compatibility audit) verifies on every meta-infra cycle:
- Did the resolver's public API change? (`resolve_pack_field`, `get_active_pack_name`, `get_loaded_pack`, `validate_pack`, `pack_field_is_true`, `clear_pack_cache`)
- Did failure-mode behavior change? Run the 9-scenario unit harness.
- Did the hardcoded fallback list shrink? Any field removed from the fallback table must have a structure-changes entry.

## Integration points

**Reads:**
- `~/.lintel/packs/active-pack` — single-line file naming active pack
- `~/.lintel/packs/<name>/pack.yaml` — pack manifests (home dir)
- `<repo>/packs/<name>/pack.yaml` — pack manifests (repo dir, used when home dir absent)

**Writes:**
- `${LINTEL_HOME}/sessions/<session-id>-pack-cache.yaml` — per-session cache
- `${LINTEL_HOME}/audit/pack-resolver.jsonl` — append-only audit log

**Public functions:**
- `get_active_pack_name` — returns active pack name (or `_default` if no active-pack file)
- `validate_pack <name>` — returns 0 if pack valid, 1 if rejected (with audit + stderr)
- `resolve_pack_field <dotted.path>` — returns field value or empty
- `pack_field_is_true <dotted.path>` — returns 0 if value is true/yes/on
- `get_loaded_pack` — returns name of cached pack (operator visibility)
- `clear_pack_cache` — explicit cache invalidation

## Anti-patterns

- **Skill greps `packs/` directly** — every read goes through the resolver
- **Workflow assumes a pack is loaded** — call `get_loaded_pack` first if you need to surface it
- **Skill catches resolver failure and proceeds silently** — surface or fail; L-004
- **Editing `lib/pack-resolver.sh` outside meta-infra mode** — every edit activates Gate M2
- **Adding a hardcoded fallback for a non-critical path** — the fallback list is for paths that must never be empty; everything else returns empty so the workflow can decide
