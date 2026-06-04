# CLAUDE.md — repo instructions for LLM assistants

> **Lintel dogfoods its own scaffolding.** This file is the self-contained per-repo
> instruction set that Lintel installs into other repos (`scaffolding/01-foundation/CLAUDE.md.template`),
> instantiated here for Lintel itself. It is **self-sufficient**: an agent can follow it without the
> operator's global `~/.claude/CLAUDE.md` present. The global protocol takes precedence where both
> apply; this file restates the load-bearing parts so the repo works standalone.
>
> Sections between `<!-- PROJECT:START -->` and `<!-- PROJECT:END -->` are Lintel-specific. The rest
> is load-bearing, inherited from [scaffolding/01-foundation/CORE-PRINCIPLES.md](scaffolding/01-foundation/CORE-PRINCIPLES.md).
> Change the load-bearing parts only with an ADR + an entry in the evolution log
> ([docs/v4.x/structure-changes/](docs/v4.x/structure-changes/)).

<!-- PROJECT:START -->

## What this repo is

Lintel is a **company-neutral, pack-driven session harness** for agent-based development — markdown +
bash scaffolding that any modern AI CLI loads as a plugin. It is also the **factory** that installs the
very disciplines in this file into other repos.

Clear ownership domains:

- `skills/` — slash-commands (the 8-phase `/li:cycle` + engineering modules `ta`/`da`/`sc`/`dh`/`tq` + session-harness skills)
- `agents/` — subagent roles per domain (engineering, security, compliance, devops, customer, communication, doc-gen, frontend)
- `hooks/shared/` — pre/post hooks (compliance + workflow enforcement)
- `packs/` — pack manifests; only the neutral `_default` ships here. Company identity (e.g. Microsoft CAIP-SE) installs as an external pack — see [lintel-caip-pack](https://github.com/jokerman89/lintel-caip-pack).
- `lib/` — `pack-resolver.sh`, `brief-forge-evaluators.sh`, schemas — the runtime helpers skills source
- `scaffolding/01-foundation/` — the templates this repo copies INTO other repos via `bin/li-scaffold`
- `bin/` — operator-side utilities (`li-scaffold`, `li-doctor`, `li-lessons-sync`, …)
- `docs/` — `design/` (architecture), `v4.x/structure-changes/` (the evolution log + Gate M1 artifacts), `v4.x/migrations/`, `adr/` (decision records)
- `tests/` — `shape/` (structural contracts), `unit/`, `integration/`, `e2e/`

Frozen / handle-with-care zones:

- `packs/_default/pack.yaml` and `lib/pack-resolver.sh` — the pack contract; ~30 skills depend on it. Change behind a shape-test.
- Frontmatter contracts (`layer`, `category`, `cli_support`, `tier`) — changing them is a meta-infra change touching every skill/agent.
- `AGENT-INSTRUCTIONS.md` — the canonical cross-CLI session ritual.

<!-- PROJECT:END -->

---

## Session-start ritual

1. Read this file (load-bearing rules below) + [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) for the cross-CLI specifics.
2. Review [scaffolding/01-foundation/CORE-PRINCIPLES.md](scaffolding/01-foundation/CORE-PRINCIPLES.md) — the 10 load-bearing rules.
3. Review the most recent entries in [tasks/lessons.md](tasks/lessons.md) — accumulated lessons. **Read before acting.**
4. Skim [tasks/memory.md](tasks/memory.md) — durable cross-session state.
5. List [docs/adr/](docs/adr/) — read any ADR whose title is relevant to the task.
6. Check [docs/v4.x/structure-changes/](docs/v4.x/structure-changes/) for recent structural decisions.

---

## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or an architectural decision).
- If something goes wrong mid-task: STOP and re-plan. Do not push through a broken plan.
- Write the plan to `tasks/todo.md` as checkable items; pause-report before implementing complex work.

### 2. Subagent Strategy
- Use subagents liberally to keep the main context window clean — offload research, exploration, parallel analysis. One task per subagent.
- Pre-defined subagents in `.claude/agents/`: `ReadOnly`, `CodeReviewer`, `TestRunner`, `SanityChecker`.
  Repo also exposes the full `agents/` fleet via the plugin manifest.
- When in doubt, prefer a subagent over polluting main context.

### 3. Self-Improvement Loop
- After ANY correction from the operator: record the pattern in `tasks/lessons.md` as a rule that prevents recurrence.
- Review lessons at session start. This is the only mechanism that compounds learning across fresh sessions.

### 4. Verification Before Done
- Never mark work complete without proof. Green tests are the floor, not the ceiling.
- Run `tests/shape/` + `tests/unit/`; diff behaviour vs main when relevant. Apply the "would a staff engineer approve this?" bar.
- If you stub/mock instead of building the real thing, flag it explicitly as "deferred to phase X".

### 5. Subtraction Bias
- Before finishing a non-trivial change, ask "is there a simpler form?" — fewer parts, not more abstraction. Not a licence to add structure in the name of elegance.

### 6. Autonomous Bug Fixing Within Authorized Scope
- Bugs INSIDE an authorized initiative: fix directly, no hand-holding. Point at logs/errors/failing tests, solve them.
- Bugs OUTSIDE current authority: surface, do not act unbidden. No standing licence to "just fix CI".

---

## Task & decision management

1. **Plan first** — `tasks/todo.md`, checkable items.
2. **Track progress** — mark items done as you go.
3. **Capture lessons** — `tasks/lessons.md` after corrections.
4. **Record decisions** — write an ADR (`docs/adr/NNNN-short-title.md`, from `docs/adr/TEMPLATE.md`) for any non-trivial decision. Structural changes to `skills/`/`agents/`/`hooks/`/`lib/` also get a `docs/v4.x/structure-changes/<date>-<slug>.md` (Gate M1 artifact) under meta-infra discipline.
5. **Review** — add a review section to `tasks/todo.md` at task end.

> **This is the discipline that was missing.** Lintel was built as the factory but never ran the
> factory on itself: until v4.8 the repo had no `.claude/`, no `docs/adr/`, and a thin CLAUDE.md, so
> ADRs and lessons did not happen. Do not let that recur — every non-trivial decision gets an ADR.

---

## Core Principles
- **Simplicity first.** Minimal-impact changes — touch only what is necessary.
- **No laziness.** Find root causes. No temporary patches. Senior-developer standards.
- **Subtraction bias.** Fewer parts beats more abstraction.

(Full set: [scaffolding/01-foundation/CORE-PRINCIPLES.md](scaffolding/01-foundation/CORE-PRINCIPLES.md).)

---

<!-- PROJECT:START -->

## How Lintel works (project specifics)

### Plugin structure
This repo IS a multi-CLI plugin (`.claude-plugin/plugin.json` + per-CLI manifests). Skills at `skills/<name>/SKILL.md`, agents at `agents/<category>/<Name>.md`. Operators install via `/plugin install li@jokerman-lintel`; skills become `/li:<skill>`.

### Pack system (v4.0+)
Identity (voice, compliance, persona, brand, roles) is **not** hardcoded — it is resolved from the active pack via `resolve_pack_field <dotted.path>` (`lib/pack-resolver.sh`). The neutral `_default` pack enforces nothing. Never reintroduce hardcoded company/voice/compliance assumptions into the spine — that is what the v4.7 CAIP extraction removed.

### Local testing
```bash
claude --plugin-dir E:/Workspace/jokerman-session-setup
```

### Skill namespacing
Skills are namespaced `/li:qa`, `/li:cycle`, etc. Inside this repo they work directly via the plugin manifest.

### Catalog
`skills/CATALOG.md` is auto-generated on push to `main` (`.github/workflows/catalog.yml`). Edit frontmatter, not the catalog.

### Per-CLI portability
Same skills/agents/hooks work across 8 CLIs via per-CLI manifests. See [docs/per-cli/](docs/per-cli/).

### How you work here
- Feature branch → PR against `main`. Local verification (shape + unit tests green) before push.
- Conventional Commits, atomic, one logical change per commit. End commit messages with the Co-Authored-By trailer.
- Non-trivial decision → ADR. Structural change → meta-infra `structure-changes/` entry.

<!-- PROJECT:END -->

---

## Shared schema discipline
When two or more components communicate (events, APIs, IPC, the pack contract): define the schema ONCE in a shared location (`lib/*-schema.yaml`), both sides import it, never reinterpret it differently, write at least one integration/shape test per link.

---

## Auto-mode boundaries

**OK without extra prompt:** file edits in the repo · `git commit`/`git push` to feature branches · local tests/builds/lints · read-only external queries · local container builds · subagent invocations.

**Requires explicit per-call authorization:** mutations against live/shared/production resources · secrets/access-policies/firewall rules · DB DDL/DML outside migrations against a live DB · image push to a live registry · deploy-pipeline triggers · `git push` to `main` · **creating a new remote repo or bulk-pushing a tree to a fresh remote** (a hard guardrail — surface it, the operator runs it).

**Borderline — ask first:** production audit events · production data access (even read-only) · branch builds wired to a live deploy.

When a boundary is crossed: stop, verify state read-only, report honestly, propose options with trade-offs, wait for authorization.

---

## Direct-push to main
PR-based by default. Direct-push to `main` is allowed only with explicit authorization for one specific commit batch. The next batch needs fresh approval.

---

## Deviation flagging
If the instruction or spec does not match reality (external API, docs, existing code): STOP, pause-report (what you found with file:line, three alternatives + trade-offs, your recommendation), wait for a decision. Do not silently "fix" it.

---

## Lessons & evolution
- `tasks/lessons.md` — accumulated lessons. Review at session start; add after ANY correction.
- `docs/adr/` — decision records (one per non-trivial decision).
- `docs/v4.x/structure-changes/` — the evolution log for structural changes to the harness.

---

## Subagent development
See [.claude/SUBAGENT-GUIDE.md](.claude/SUBAGENT-GUIDE.md) for how to add or revise subagents.

---

## Voice
Voice is pack-driven. The active pack's voice tier (`resolve_pack_field voice.default_tier`; neutral default `internal`) sets the style; a pack may supply a corpus + critic. Internal dev agents declare `voice: internal`. When in doubt, internal is the default.
