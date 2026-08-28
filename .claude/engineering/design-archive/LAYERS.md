# LAYERS — the 4-layer architecture manifest

> **STATUS: superseded by the v4.0 foundation + packs model.** Layers 2–4 (compliance, personal-advanced, power-user) were folded into the **pack** system: compliance, voice, personas, and brand are now declared by the active pack (`packs/<name>/pack.yaml`), not by `scaffolding/02-*`/`03-*`/`04-*` directories (which no longer exist). Only `scaffolding/01-foundation/` remains on disk. The neutral `_default` pack is the baseline; company identity (e.g. Microsoft CAIP-SE) installs as an external pack (lintel-caip-pack). The historical 4-layer rationale is gone; the current model is documented below. See [.claude/engineering/design-archive/lintel-v4.0-reframe-design.md](.claude/engineering/design-archive/lintel-v4.0-reframe-design.md) for the full design.

Lintel is now built from **two parts**: a stable **foundation** and one active **pack**. The foundation is company-neutral discipline that every repo gets. The pack supplies identity — compliance, voice, personas, brand, roles — and is swappable. Lintel ships only the neutral `_default` pack; company identity installs on top.

```
┌─────────────────────────────────────────────────────────────┐
│  Pack — identity, swappable (packs/<name>/pack.yaml)        │
│    voice · compliance · persona · roles · brand · knowhow   │
│    lessons · opinions · navigation · brief_forge_handoffs   │
│    resolved by lib/pack-resolver.sh                         │
│    _default = neutral baseline · company pack installs over │
├─────────────────────────────────────────────────────────────┤
│  Foundation — discipline, stable (scaffolding/01-foundation)│
│    CORE-PRINCIPLES, EVOLUTION, EVOLUTION-LOG,               │
│    .claude/memory/{lessons,working-state,personas}.md,      │
│    .claude/plans/, .claude/decisions/ templates,            │
│    .claude/agents/, CLAUDE.md.template                      │
└─────────────────────────────────────────────────────────────┘
```

## Foundation — what it holds

`scaffolding/01-foundation/` is the stable, company-neutral base copied into every scaffolded repo via `bin/li-scaffold`. It ships **structure, not content**:

- `CORE-PRINCIPLES.md` — the load-bearing rules, read at session-start.
- `EVOLUTION.md` + `EVOLUTION-LOG.md` — the change process for foundation itself and the log of decisions taken.
- `.claude/memory/{lessons,working-state,personas}.md` + `.claude/plans/todo.md` — working memory templates (lessons, long-running state, operator calibration, the active todo).
- `.claude/decisions/` templates — architecture decision record scaffolding.
- `.claude/agents/` — per-repo subagent override slot.
- `CLAUDE.md.template` — the session entrypoint a new repo starts from.

Foundation **documents discipline; it does not enforce.** Agents read it at session-start; there is no runtime check. It changes rarely, and only through the `EVOLUTION.md` process (a foundation change = explicit decision + `EVOLUTION-LOG.md` entry).

## Pack — what it declares

A pack is `packs/<name>/pack.yaml` plus any corpus files it references. It is where identity lives. The schema (`lib/pack-schema.yaml`) defines these top-level fields:

| Field | Declares |
|---|---|
| `voice` | voice tier (`internal`/`mixed`/`custom`), corpus path, enforcement scope, active gates |
| `compliance` | mode (`hard`/`advisory`/`off`) + which Lintel hooks the pack activates |
| `persona` | operator persona source + whether voice-critic checks output against it |
| `roles` | role-definition directory + default role |
| `brand` | doc-gen templates + color tokens for `/generate-web` etc. |
| `knowhow` | tag-indexed knowledge base + whether it may override session priors |
| `lessons` | immutable lessons shipped with the pack (operator lessons stay outside it) |
| `opinions` | stance documents |
| `navigation` | default + high-risk workflows, orientator token budget, escalation threshold |
| `brief_forge_handoffs` | which evaluators fire on subagent-spawn, phase-transition, workflow-handoff, cold-executor |

The neutral `_default` pack sets all of these to off/null: no voice enforcement, advisory-only compliance with no hooks, no personas, no brand. It is the everything-neutral baseline.

## Resolution and inheritance

`lib/pack-resolver.sh` resolves the active pack at session-start:

- A pack may declare `extends: <parent>` to inherit from another pack. The resolver walks the chain parent→child and merges top-level keys, with the child overriding the parent.
- `_default` is the resolver's **fallback layer for missing fields**, not an implicit `extends` target. Any field a pack leaves unset falls back to the `_default` value (and, last resort, to hardcoded neutral defaults).
- Failure modes are guarded: an `extends:` cycle is refused, and an invalid active pack falls back to `_default` with a warning (if `_default` itself is invalid, the repo is broken and the resolver fails loudly).

So identity composes: a company pack declares only what it changes, inherits the rest from its parent, and anything still unset lands on the neutral baseline.

## Per-repo override mechanism

A scaffolded repo overrides pack/foundation behavior through three levels, repo-most-specific winning:

- `<repo>/CLAUDE.md` — repo-specific rules ALWAYS override Lintel defaults. Per-repo wins.
- `<repo>/.claude/agents/` — repo-level subagents override user-global ones with the same name.
- `~/.lintel/config` — operator-global overrides (which pack is active, compliance-tier elevation, hook activation, voice-tier defaults).

## Durable principles (carried from the layer model into foundation + packs)

Four lessons graduated from `tasks/lessons.md` to architecture-level principles. They
predate the pack model but still shape what foundation and packs each do:

- **L-001 — scaffolding, not content.** Foundation ships *structure* (templates, ADR
  scaffolding, tasks-format); a pack ships *content* (voice corpus, personas, brand).
  Neither holds curated answers — operator + AI generate at invocation time.
- **L-002 — grep existing before designing new.** Before adding a skill family or a
  pack field, enumerate what already exists. The v4.0 spine-extraction audit was L-002
  applied to "what's hardcoded that a pack should own."
- **L-003 — verify counts before applying fact-claims.** Any external claim about the
  codebase (skill counts, which files reference a pack) is verified by tool before action.
- **L-004 — separate decision-layer from rendering-layer.** The clearest application is
  the spine (execution engine) vs packs (decision/identity layer); also the v3.7
  `frontend-*` (design decisions) vs `generate-*` (rendering) split.

The trio L-001/L-002/L-003 plus L-004 form the discipline: respect what exists, respect
what doesn't, verify claims, and split decisions from execution.

## Provenance

The original 4-layer model came from the operator's internal wiki ("My Claude Code Setup (experimental)" — Layer 1 Universal foundation / Layer 2 Compliance / Layer 3 Personal advanced / Layer 4 Power user). v1 operationalized that vision into installable infrastructure; v4.0 collapsed Layers 2–4 into the pack system, leaving the foundation + packs model documented above.
