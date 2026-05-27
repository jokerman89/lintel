# cli_support v2 schema

Frontmatter schema for skill + agent CLI support declarations. v2 introduces per-CLI degradation maps + runtime enforcement (Phase B).

**P1 fix T8 from eng-review.** Source of truth referenced by `TEMPLATE-skill.md` and `TEMPLATE-agent.md`.

---

## v1 schema (deprecated, accepted as legacy)

```yaml
cli_support: [claude-code, codex, copilot]
```

Simple array. Each entry = CLI ID. No degradation info. v2 still parses this as shorthand for `level: full` on every listed CLI.

---

## v2 schema (canonical)

```yaml
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: auto-pick-recommended
      - capability: Agent
        strategy: codex-exec-subprocess
  - cli: copilot-cli
    level: not-supported
    reason: requires Agent tool, no Codex shim available
  - cli: copilot-app
    level: not-supported
    reason: same as copilot-cli
```

### Required fields

- **`cli`** (string) — CLI identifier. Valid values: `claude-code`, `codex`, `copilot-cli`, `copilot-app`
- **`level`** (string) — one of `full`, `degraded`, `not-supported`

### Conditionally required

- **`degradation`** (array) — required when `level: degraded`. List of capability → strategy mappings.
- **`reason`** (string) — required when `level: not-supported`. One-line operator-readable explanation.

### Capability → strategy enumeration

Allowed `capability` values:
- `AskUserQuestion` — interactive decision prompts
- `Agent` — subagent spawning (Task tool)
- `Browser` — managed Chromium via /browse
- `MCP` — Model Context Protocol calls
- `WebFetch` — fetch arbitrary URLs
- `WebSearch` — web search calls
- `Bash` — shell execution (always present; rare degradation case)

Allowed `strategy` values:
- `auto-pick-recommended` — non-interactive, pick the option labeled `(recommended)` in AskUserQuestion
- `sequential-prompt` — emit prompts as numbered list, operator replies with number
- `codex-exec-subprocess` — spawn `codex exec` to handle Agent-tool work
- `gh-copilot-suggest` — use `gh copilot suggest` for one-shot prompts
- `refuse-with-message` — skill declines to run, surfaces message
- `manual-fallback` — operator-driven workaround documented in skill body
- `degraded-output` — skill runs but produces less complete output (e.g. text-only screenshot description instead of actual screenshot)

### v1 backward compatibility

v1 schema `cli_support: [claude-code, codex]` is automatically interpreted as v2:

```yaml
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: full
```

Skills written in v1 keep working. Migration to v2 happens on next edit of the skill (P3 backlog).

---

## Validation rules

`verify.sh --portability` enforces:

1. Every skill/agent has a `cli_support` field.
2. Field is either v1 (array of strings) or v2 (array of objects).
3. v2 schema: every object has `cli` + `level`. `degraded` objects also have `degradation`. `not-supported` objects also have `reason`.
4. `cli` values from valid enum (4 CLIs above).
5. `level` values from valid enum (3 levels).
6. v2 `capability` + `strategy` values from valid enums.
7. At least one CLI declared (skill marked `cli_support: []` is rejected — declare explicitly or omit field entirely).

Schema validation runs at install time + in CI (`unit-tests-linux` job exercises `tests/unit/phase-b-portability-schema.sh`).

---

## Lookup performance (P3 fix T13)

The shim runtime builds a hashmap on session start: `<cli>:<capability>` → `<strategy>`. O(1) lookup. The hashmap also contains aliases — v1 skill names like `jstack-ship` resolve to v2 canonical via the same map (single resolution layer).

Map persisted to `~/.jstack/sessions/$SESSION_ID/shim-map.json`. Recomputed if config changes mid-session.

---

## Examples

### Pure claude-code skill (e.g. `/pair-agent`)

```yaml
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: not-supported
    reason: requires Agent tool, no Codex equivalent
  - cli: copilot-cli
    level: not-supported
    reason: same
  - cli: copilot-app
    level: not-supported
    reason: same
```

### Full multi-CLI skill (e.g. `/qa`)

```yaml
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: auto-pick-recommended
  - cli: copilot-cli
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: sequential-prompt
  - cli: copilot-app
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: sequential-prompt
```

### Browser-dependent skill (e.g. `/browse`)

```yaml
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: not-supported
    reason: requires browser tool, no managed Chromium in Codex
  - cli: copilot-cli
    level: not-supported
    reason: same
  - cli: copilot-app
    level: not-supported
    reason: same
```

### Doc-gen skill (e.g. `/generate-ppt`)

```yaml
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: auto-pick-recommended
      - capability: Browser
        strategy: degraded-output
    note: brand template selection uses defaults; voice-check feedback loop sequential
```

(`note` field is optional, free-text, surfaces in skill help output.)

---

## Migration path from v1 to v2 (per skill)

For each skill being edited in v2:

1. Read existing `cli_support` array
2. For each CLI listed:
   - claude-code → `level: full`
   - codex → `level: degraded` if AskUserQuestion is in skill body, `level: full` otherwise
   - copilot-cli / copilot-app → `level: not-supported` UNLESS skill is pure-Bash + no Agent + no AskUserQuestion + no Browser
3. Add degradation map if degraded
4. Validate via `verify.sh --portability`

Automated bulk migration is out-of-scope for v2.0. Per-skill conversion happens on next edit (annotated as TODO if not yet done).

---

## Operator overrides

`~/.jstack/config.yaml` can override per-skill cli_support:

```yaml
overrides:
  cli_support:
    - skill: /onebranch-validate
      cli: codex
      level: not-supported
      reason: codex install unstable on this machine
```

Override takes precedence over skill frontmatter. Logged on use.

---

## See also

- `scaffolding/01-foundation/TEMPLATE-skill.md` — references this schema
- `scaffolding/01-foundation/TEMPLATE-agent.md` — references this schema
- `/jstack-cli-fingerprint` skill — runtime CLI detection that feeds shim lookup
- `verify.sh --portability` — schema validation subcommand
- Phase B implementation (this design) — runtime that consumes the schema
