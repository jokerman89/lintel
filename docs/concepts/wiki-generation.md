# Wiki and showcase generation

`bin/li-wiki-gen` produces reference tables and the single-file showcase from repository sources.
Edit the source metadata or generator, then regenerate. Do not patch generated outputs as the
final fix: the next run would overwrite the change.

## Sources and outputs

| Source | Generated output |
|---|---|
| `skills/*/SKILL.md` frontmatter | `docs/wiki/skills.md` and skill counts |
| `agents/*/*.md` frontmatter | `docs/wiki/agents.md` and agent counts |
| `packs/*/pack.yaml` | `docs/wiki/packs.md` and pack counts |
| Shared schemas in `lib/` | `docs/wiki/schemas.md` |
| Generator templates and those inventories | `docs/wiki/README.md`, `docs/showcase/lintel-the-harness.html` |

The wiki answers structural questions: which skills and agents exist, what their metadata says,
and which contracts packs use. Handwritten concept guides explain how to use those mechanisms.
They should link to the generated inventory rather than repeat changing counts.

The showcase is an overview for adopters. Its counters describe repository content, not the
number of native entry points supported by each client. See [Copilot](../copilot.md) for the
portable kit and plugin scope.

## Commands

```bash
bash bin/li-wiki-gen
bash bin/li-wiki-gen --showcase-only
bash bin/li-wiki-gen --check
```

Generation performs local reads and writes; it does not call a model or fetch live vendor facts.
`--check` exits non-zero when the generated result differs. The generator and its
`lib/wiki-gen.sh` helper define timestamp and enumeration behavior; keep those deterministic
when changing sources or templates.

`tests/unit/wiki-gen-idempotency.sh` covers repeated generation. Run the generator check before
release and inspect the generated diff. A stable generated output proves source/output consistency,
not the truth of every runtime claim in a source description.

## Related generated surfaces

The README capability table comes from `lib/cli-tiers.yaml` through `lib/cli-tiers.sh`, with its
own synchronization test. The skill catalog comes from canonical skill frontmatter. Copilot
native adapters come from the Copilot generator and are verified separately. Each output has
one owner; fix the source or generation contract when drift is found.

See [contributing](../../CONTRIBUTING.md), [architecture](../architecture.md), and
[the showcase](../showcase/README.md).
