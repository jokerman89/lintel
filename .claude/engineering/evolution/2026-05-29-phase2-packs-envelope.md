# Structure change — Phase 2: pack architecture + envelope schema

**Date:** 2026-05-29
**Cycle:** v4.0 Phase 2 (v4.0-beta)
**Mode:** meta-infra (M1-M4 active)
**Branch:** `v4.0-phase2-packs-envelope` (stacked on Phase 1 PR #36)
**Refs:** `.claude/engineering/design-archive/lintel-v4.0-reframe-design.md` v2.0 §1.3 (FR-B), §1.5 (FR-D), §2.3 (FR-B envelope), §5.2 Phase 2

## What changed

### Pack architecture (Chapter 1.B)

- **New:** `lib/pack-schema.yaml` — declarative pack schema v1, JSON-schema-style, the single source of truth for what a pack manifest may declare. Versioned via `schema_version: "4.0"`.
- **New:** `packs/ms-internal/pack.yaml` — base pack for any Microsoft work. Declares MS-CAIP-SE-adjacent defaults that aren't specific to CAIP-SE (compliance hooks, audit paths). Recommended per design doc §1.3 C1-D1 ("NOW") — pays dividends the moment a sister-pack to CAIP-SE appears.
- **New:** `packs/caip-se/pack.yaml` — concrete pack for CAIP-SE work. Declares `extends: ms-internal`. Lifts pack-bound spine content per `2026-05-29-spine-extraction-audit.md`: Trailblazer voice tier, compliance audit paths, persona inventory pointer, voice corpus pointer.
- **Extended:** `lib/pack-resolver.sh` — shallow-merge of `extends:` chain (max-depth 10), explicit precedence (child overrides parent), parent-walk on missing fields. Cache merges into a single resolved manifest at prime time so downstream reads stay O(1).
- **New:** `packs/_default/pack.yaml` gets `schema_version: "1"` declared at top (was implicit before; Phase 2 makes it explicit).

### Envelope schema (Chapter 2.B)

- **New:** `lib/envelope-schema.yaml` — standardized payload envelope (HEAD 6 required fields + TAIL 4 required fields + BODY free-form by `content_type`). Versioned via `schema_version: "1"`. Single source of truth for every Brief Forge hand-off.
- **New:** `bin/li-envelope-validate` — validates an envelope JSON/YAML against schema, returns PASS/FAIL + per-field error report.
- **New:** `bin/li-envelope-replay` — replays an envelope; defaults to `--dry-run` (re-execute in sandbox, surface what would happen). Actual re-execution requires `--apply`. Reason: envelopes capture state at hand-off time; the world may have moved on.

### Pack lifecycle skills (Chapter 1.B)

- **New:** `skills/pack-create/SKILL.md` — scaffolds a new pack (operator provides name + extends-target).
- **New:** `skills/pack-switch/SKILL.md` — switches active pack (writes `~/.lintel/packs/active-pack`).
- **New:** `skills/pack-list/SKILL.md` — surfaces every pack discoverable in `~/.lintel/packs/` + `<repo>/packs/`.
- **New:** `skills/pack-validate/SKILL.md` — runs validation per the schema + writes audit entry.

### Migration tool (R1 mitigation from §section 8)

- **New:** `skills/v4-migrate/SKILL.md` — walks operator through v3.x → v4.0 migration (pack activation, envelope adoption, deprecated path detection).

### Navigation hardening (preparing for Phase 3)

- **Extended:** `skills/cycle/SKILL.md` — adds `navigation:` block to frontmatter (workflow_root contract per FR-C).
- **Extended:** `skills/plan/SKILL.md` — same.
- **Tightened:** `tests/shape/workflow-root-has-navigation.sh` — Phase 2 = FAIL (was WARN in Phase 1 grace).

## Backward compatibility

| Surface | Phase 2 change | Backward-compat? |
|---|---|---|
| `packs/_default/pack.yaml` | Adds `schema_version: "1"` line at top | YES — additive |
| `lib/pack-resolver.sh` public API | No signature changes; adds inheritance walk internally | YES — additive |
| `packs/caip-se/` | New pack; does not affect existing workflows | YES — additive |
| `packs/ms-internal/` | New pack; does not affect existing workflows | YES — additive |
| `lib/envelope-schema.yaml` | New file; no consumers in Phase 2 (Brief Forge ships Phase 3) | YES — additive |
| `bin/li-envelope-*` | New binaries; no rename of existing | YES — additive |
| `skills/cycle/SKILL.md` navigation block | Additive frontmatter field | YES — additive |
| Shape-test workflow-root-has-navigation | Phase 1 WARN → Phase 2 FAIL | **NO** — but only blocks if a workflow_root skill omits navigation. Phase 2 adds nav to all workflow_root skills before the test tightens, so net effect: no block. |

**Verdict:** GREEN. All Phase 2 changes are additive. The one tightening (shape-test) is preceded by the additions that satisfy it.

## Migration path

For operators currently on `_default` pack: nothing required. `_default` stays a valid pack; the resolver falls back to it for any field a downstream pack omits.

For operators currently using Lintel for CAIP-SE work (the historical primary use case): run `/li:pack-switch caip-se` once after Phase 2 ships. After that, behavior is identical to v3.x — the same voice, compliance hooks, personas, voice corpus that lived in the spine now live in the caip-se pack and resolve to the same effective values.

`/li:v4-migrate` automates this: detects v3.x usage signals (compliance hooks invoked, Trailblazer voice references, CAIP-SE-shaped state), recommends pack activation, can write the active-pack file with `--apply`.

## Forward compatibility

| v4.x consumer | Phase 2 surface used | Forward-compat with planned work? |
|---|---|---|
| Brief Forge (Phase 3) | `lib/envelope-schema.yaml`, `bin/li-envelope-validate` | YES — envelope schema is the universal hand-off shape |
| Navigation orientator (Phase 3) | `pack.yaml.navigation.*` (already in `_default` from Phase 1) | YES — schema captures budget + threshold fields |
| Wiki gen (Phase 3) | `lib/pack-schema.yaml`, `lib/envelope-schema.yaml` | YES — both are documented schemas the generator can consume |
| Engineering modules (Phase 4) | Pack inheritance (`extends:` chain) | YES — `caip-se → ms-internal → _default` already exercises 3-level chain |

The schema-versioning mechanism (`schema_version: "1"`) means Phase 4 can ship `schema_version: "2"` envelopes without breaking Phase 3 consumers — they'll see version mismatch + can request the validator handle both.

## Verification

REVIEW phase runs:
1. `bash tests/runner/run-all.sh` — all 30+ tests pass
2. `bash tests/runner/run-all.sh --shape-only` — 8 shape-tests pass (including the tightened workflow-root-has-navigation)
3. `bash tests/unit/pack-resolver-fallbacks.sh` — 9 scenarios pass + new "extends-chain depth-3 resolves correctly" scenario
4. `bash tests/unit/envelope-schema-validates.sh` — new test: valid envelope passes, invalid envelopes fail per documented field
5. `bin/li-compat-audit` — Gate M2 mechanical sweep produces GREEN verdict
6. `bash bin/li-envelope-validate fixtures/envelope-example.yaml` — example envelope validates

## Rollback

If SHIP discovers a regression:
- **Pack inheritance bug:** revert `lib/pack-resolver.sh` to Phase 1 state; new packs continue to work but inheritance returns empty values (acceptable degradation — operators fall back to `_default` per layer-3 resolver default)
- **Envelope schema bug:** the schema file is read-only at Phase 2 (no consumer in Phase 2); revert is delete-the-file
- **Pack lifecycle skill bug:** revert the skill; operators can still hand-edit `~/.lintel/packs/active-pack`
- **Navigation tightening bug:** revert `tests/shape/workflow-root-has-navigation.sh` to Phase 1 WARN mode

Each rollback is independent. Phase 2 deliverables are stacked but not entangled.

## What this enables

Phase 3 (navigation + Brief Forge + wiki) can ship without further pack-resolver work. The pack architecture is the foundation; envelope is the hand-off contract. With both in place, Phase 3 is:
- Build the orientator agent on top of `pack.yaml.navigation.*`
- Build Brief Forge handoff machinery on top of `lib/envelope-schema.yaml`
- Build wiki generator that reads both schemas + manifests
