# Wiki generation — both outputs from the same sources

**Last updated:** 2026-05-29 (v4.0 Phase 3)
**Status:** Concept doc — referenced by `bin/li-wiki-gen`, `lib/wiki-gen.sh`, `bin/li-forge-stats` (planned — not yet shipped)

> Lintel has two surfaces that describe itself: the developer-facing wiki (markdown reference for every skill, agent, pack, schema) and the operator-facing showcase HTML (single-file system map). Pre-v4.0 the showcase was hand-curated and the wiki didn't exist as a generated artifact. Both drifted from code. v4.0 closes the gap: `bin/li-wiki-gen` reads the same sources to produce both outputs deterministically.

## The problem

Three documentation surfaces existed pre-v4.0, none in sync:

1. **`docs/showcase/lintel-the-harness.html`** — hand-curated marketing-flavored single-file system map. Last updated whenever someone remembered. Often referenced skill names that had been renamed.
2. **README sections** — text descriptions of subsystems. Same drift problem.
3. **Skill frontmatter** — ground truth, but operators couldn't browse them at the system level.

When v3.7 added Phase D synthetic protocol, a hand-curated showcase reference still said "v3.5 features." When Cohort 4 renamed `setup-brain` to `gbrain-setup`, the showcase HTML still said `setup-brain`. Each drift was small; cumulative the showcase stopped being trustworthy.

The wiki-gen fix is simple: **both outputs regenerate from the same sources, deterministically, on every change**.

## The model

```
Sources (ground truth):
    skills/*/SKILL.md          ← frontmatter is the source of truth
    agents/*/*.md              ← frontmatter
    packs/*/pack.yaml          ← schema-compliant manifest
    lib/pack-schema.yaml       ← schema contract
    lib/envelope-schema.yaml   ← schema contract
        │
        ▼
bin/li-wiki-gen
        │
        │  Reads sources, parses frontmatter + manifests + schemas
        ▼
Outputs:
    docs/wiki/README.md        ← index
    docs/wiki/skills.md        ← skills table
    docs/wiki/agents.md        ← agents table
    docs/wiki/packs.md         ← packs table
    docs/wiki/schemas.md       ← schema summaries
    docs/showcase/lintel-the-harness.html   ← system map (single file)
```

Both outputs are generated. Hand edits will be overwritten on the next regen. Operators wanting to change content edit the source.

## Determinism

`bin/li-wiki-gen` is deterministic given identical sources. Two runs with no source changes produce byte-identical outputs. Verified by `tests/unit/wiki-gen-idempotency.sh`.

How:
- Source enumeration uses `find ... | sort` (deterministic order)
- Timestamps are externalized via `WGEN_TS` env var (defaults to now; CI sets it to commit time for reproducible builds)
- No LLM calls, no network access
- Parsers are awk + grep (no third-party YAML libraries that may sort fields differently across versions)

Determinism matters because the CI check (`bin/li-wiki-gen --check`) fails if regen would diff against committed wiki. Non-deterministic regen would produce false fails.

## Idempotency contract

The contract enforced by `tests/unit/wiki-gen-idempotency.sh`:

```
run_1 = li-wiki-gen output
run_2 = li-wiki-gen output (immediately after, no source changes)
assert md5(run_1) == md5(run_2)
```

If a future change to `bin/li-wiki-gen` introduces non-determinism, this test catches it. Operators can rely on `--check` not flapping.

## The two outputs

### Markdown wiki (`docs/wiki/`)

For developers + LLM-assisted operations. Tables of every skill, agent, pack, schema. Indexes link to concept docs. The wiki is the **reference**: when someone asks "is there a skill for X?" the answer is `docs/wiki/skills.md`.

### Showcase HTML (`docs/showcase/lintel-the-harness.html`)

For operators + external audiences. Single self-contained HTML file (CSS inlined, no JS, no fetches). Counts of skills/agents/packs at the top. Layer map. v4.0 architecture summary. Always reflects what's currently in the repo.

Self-contained is important: the showcase can be opened from a USB stick, attached to an email, hosted from a static host — anywhere. No build step, no external deps.

## CI integration

`bin/li-wiki-gen --check` exits 1 if regenerating would change anything. CI runs it on every PR:

- **v4.0:** warn-only (the workflow report says "wiki would change; consider regenerating")
- **v4.1+:** block PRs (consistent with pack-version enforcement progression per design doc §1.3 C1-D2)

Pre-commit hook (optional, operator-installed via `bin/li-scaffold`): runs `bin/li-wiki-gen --check` and prompts to regen.

The warn-then-block progression gives operators time to internalize the discipline before it bites.

## What lives in the wiki vs in concept docs

Wiki tables are **machine-generated indexes** of what exists. They answer "is there a skill for X?" / "which packs declare hard compliance?" — purely structural questions.

Concept docs in `docs/concepts/` are **hand-authored explanations** of why things work the way they do. They answer "why does the resolver fall back to _default in three layers?" / "what's the difference between an envelope and a brief?" — purely conceptual questions.

The two never overlap. Concept docs link into wiki tables for structural reference; wiki tables link out to concept docs for conceptual context.

## What does NOT regenerate

- `docs/concepts/*.md` — hand-authored, not regenerated
- `docs/design/*.md` — hand-authored design docs, not regenerated
- `docs/audit/*.md` — review artifacts, not regenerated
- `docs/v4.x/*` — meta-infra deliverables, not regenerated
- `tasks/*.md` — operator's working memory, never regenerated

Only `docs/wiki/` and `docs/showcase/lintel-the-harness.html` regenerate. The split is intentional: hand-authored docs explain intent; generated docs surface state.

## How operators customize

To change wiki output without forking `bin/li-wiki-gen`:

1. **Skill / agent / pack content** — edit the source (frontmatter or pack.yaml). Wiki picks it up next regen.
2. **Add a new wiki section** — edit `bin/li-wiki-gen` to add a new `gen_wiki_*` function. The README index lists every section by convention.
3. **Custom showcase** — Phase 4 will add `--template <file>` flag so operators can substitute their own showcase template. v4.0 ships the default template only.

## Failure modes

| Failure | Cause | Mitigation |
|---|---|---|
| Wiki has stale skill | Skill renamed, regen not run | CI `--check` warns; operator runs regen |
| Showcase counts wrong | Skills moved between dirs | regen runs find on entire skills/ |
| Regen produces non-deterministic output | New parser introduces sort-instability | `tests/unit/wiki-gen-idempotency.sh` catches |
| CI check flaps | Source has timestamp that changes | Externalize timestamp via `WGEN_TS` |
| Operator hand-edited wiki, regen overwrites | Did not know wiki regenerates | Every generated file has top-of-file warning |

## Anti-patterns

- **Hand-editing wiki output** — edits will be overwritten on next regen
- **Hand-editing showcase HTML** — same
- **Mixing generated + hand-authored content in the same file** — split into two files, one per source
- **Adding LLM calls to wiki-gen** — wiki-gen is deterministic, mechanical, fast; LLM would break that
- **Skipping `--check` in CI** — without enforcement, drift returns

## Integration points

**Reads:**
- `skills/*/SKILL.md` (frontmatter)
- `agents/*/*.md` (frontmatter)
- `packs/*/pack.yaml` (manifest)
- `lib/pack-schema.yaml` (schema_version + structure)
- `lib/envelope-schema.yaml` (schema_version + structure)

**Writes:**
- `docs/wiki/README.md`
- `docs/wiki/skills.md`
- `docs/wiki/agents.md`
- `docs/wiki/packs.md`
- `docs/wiki/schemas.md`
- `docs/showcase/lintel-the-harness.html`

**Public functions in lib/wiki-gen.sh:**
- `wgen_yaml_scalar <file> <key>` — parse YAML scalar (block + inline)
- `wgen_fm_scalar <file> <field>` — parse markdown frontmatter scalar
- `wgen_is_workflow_root <file>` — yes/no for workflow_root: true
- `wgen_render_row <cell>...` — markdown table row
- `wgen_count <dir> <pattern>` — count entries
- `wgen_ts` — deterministic timestamp (env-overridable)

**Tested by:**
- `tests/unit/wiki-gen-idempotency.sh`
- `tests/shape/wiki-regenerates-clean.sh`
