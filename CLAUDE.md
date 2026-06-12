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

- `skills/` — slash-commands (the 9-step `/li:cycle` (8 core phases + SCOPE) + engineering modules `ta`/`da`/`sc`/`dh`/`tq` + session-harness skills)
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
- `lib/paths.sh`, `lib/memory.sh`, `bin/_context.sh` — the v5 path/memory contract (ADR-0005/0006). Change behind tests/shape/claude-home-paths.sh + tests/unit/memory-v2.sh.
- Frontmatter contracts (skills: `layer` + `cli_support`; agents: `category` + `tier` + `cli_support`) — changing them is a meta-infra change touching every skill/agent.
- `AGENT-INSTRUCTIONS.md` — the canonical cross-CLI session ritual.

<!-- PROJECT:END -->

---

## Session-start ritual

> **Claude Code auto-loads a digest** of the items below via the `session-digest` SessionStart
> hook (active pack/mode/role + recent lessons + open jobs + recent ADRs; see [ADR-0002](.claude/decisions/0002-session-digest-auto-load.md)).
> This ritual is the deeper read on top of that digest — **and the fallback for non-hook CLIs**
> (Codex, Gemini, …), which do not run SessionStart hooks and must read these files explicitly.

1. Read this file (load-bearing rules below) + [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) for the cross-CLI specifics.
2. Review [scaffolding/01-foundation/CORE-PRINCIPLES.md](scaffolding/01-foundation/CORE-PRINCIPLES.md) — the 10 load-bearing rules.
3. Read [.claude/memory/MEMORY.md](.claude/memory/MEMORY.md) — the memory index (Claude Code auto-loads it natively).
4. Review the most recent entries in [.claude/memory/lessons.md](.claude/memory/lessons.md) — accumulated lessons. **Read before acting.**
5. Skim [.claude/memory/working-state.md](.claude/memory/working-state.md) — durable cross-session state.
6. Load operator calibration from [.claude/memory/personas.md](.claude/memory/personas.md) and the active profile (`~/.lintel/profile.yaml`: active pack, mode, role).
7. List [.claude/decisions/](.claude/decisions/) — read any ADR whose title is relevant to the task.
8. Check [docs/v4.x/structure-changes/](docs/v4.x/structure-changes/) for recent structural decisions.

---

## Skill routing

When a request matches a skill, **invoke it** (skills are auto-surfaced — you can see them). A nudge,
not an exhaustive map — run `/li:catalog` to discover the full set.

- Multi-step work / a real task → `/li:cycle` (the 9-step SENSE→CAPTURE loop; writes `.claude/runtime/state/00-state.md`)
- Architecture / data / security / devops / testing depth → `/li:ta` · `/li:da` · `/li:sc` · `/li:dh` · `/li:tq`
- Bug / "why is this broken" → `/li:investigate`  ·  Tests / "does it work" → `/li:qa`
- Plan review → `/li:plan-eng-review` / `/li:plan-ceo-review`  ·  Brainstorm an idea → `/li:office-hours`
- Deep context load → `/li:context-warm`  ·  Save / resume → `/li:context-save` · `/li:resume`
- Record a decision → `/li:adr-new`  ·  Capture a lesson → `/li:capture`
- Switch / inspect identity → `/li:pack-switch` · `/li:pack-list` · `/li:role-activate`
- Discover everything → `/li:catalog`

---

## Where state lives (the memory map)

Lintel's snowball — read on demand, **write after corrections/decisions** so it compounds. One
circle of control (v5, ADR-0005): everything Lintel generates for this repo lives under `.claude/`
— knowledge committed, runtime gitignored. Operator identity stays in `~/.lintel/`.

| Store | Holds | Lifecycle |
|---|---|---|
| `.claude/memory/MEMORY.md` | the index (≤200 lines, auto-loads on Claude Code) | keep current, consolidate |
| `.claude/memory/lessons.md` | lessons from corrections (`L-NNN`) | append after ANY correction |
| `.claude/memory/working-state.md` | durable cross-session working state | update on durable state changes |
| `.claude/memory/personas.md` | operator calibration | read at session-start |
| `.claude/decisions/NNNN-*.md` | decision records | one per non-trivial decision |
| `.claude/plans/` | todo.md + cold-executor trios (`<slug>/{plan,spec,prompt}.md`) | per initiative |
| `.claude/runtime/state/` | per-repo cycle + module state (gitignored) | written by cycle/module skills |
| `.claude/runtime/{sessions,jobs,audit}/` | context-saves · job data · repo event log (gitignored) | written by skills/hooks |
| `docs/v4.x/structure-changes/` | evolution log (Gate M1 artifacts) | per structural change |
| `~/.lintel/profile.yaml` | active pack · mode · role · checkpoint mode | operator-global |
| `~/.lintel/jobs/_active.md` | cross-repo jobs REGISTRY (data lives in each repo) | `/li:resume` reads it |

The `session-digest` hook injects a compact view of the top rows at session-start; this table is the
full map for on-demand reads + where to **write**.

> **Un-migrated repos:** no `.claude/lintel-layout.yaml` marker → that repo still uses the legacy
> locations (`tasks/*`, `docs/adr/`, `.lintel/state/`). Use those there, and suggest
> `bin/li-migrate-claude-home` (grace window to 2026-09-12).

---

## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or an architectural decision).
- If something goes wrong mid-task: STOP and re-plan. Do not push through a broken plan.
- Write the plan to `.claude/plans/todo.md` as checkable items; pause-report before implementing complex work.

### 2. Subagent Strategy
- Use subagents liberally to keep the main context window clean — offload research, exploration, parallel analysis. One task per subagent.
- Pre-defined subagents in `.claude/agents/`: `ReadOnly`, `CodeReviewer`, `TestRunner`, `SanityChecker`.
  Repo also exposes the full `agents/` fleet via the plugin manifest.
- When in doubt, prefer a subagent over polluting main context.

### 3. Self-Improvement Loop
- After ANY correction from the operator: record the pattern in `.claude/memory/lessons.md` as a rule that prevents recurrence.
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

1. **Plan first** — `.claude/plans/todo.md`, checkable items.
2. **Track progress** — mark items done as you go.
3. **Capture lessons** — `.claude/memory/lessons.md` after corrections.
4. **Record decisions** — write an ADR (`.claude/decisions/NNNN-short-title.md`, from `.claude/decisions/TEMPLATE.md`) for any non-trivial decision. Structural changes to `skills/`/`agents/`/`hooks/`/`lib/` also get a `docs/v4.x/structure-changes/<date>-<slug>.md` (Gate M1 artifact) under meta-infra discipline.
5. **Review** — add a review section to `.claude/plans/todo.md` at task end.

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
# run from the repo root
claude --plugin-dir "$PWD"
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

## Structured comment format

Meaningful code/spec files carry a header linking back to intent (adjust comment syntax to language):

```
# component: <name>
# implements: <ADR-IDs comma-separated>
# intent: docs/<file>.md
# constraints: docs/risks/<RISK-IDs>
# last_intent_review: YYYY-MM-DD
```

Explains *why*, not *what*. Lets a reader trace any file back to the decision that created it.

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
- `.claude/memory/lessons.md` — accumulated lessons. Review at session start; add after ANY correction.
- `.claude/decisions/` — decision records (one per non-trivial decision).
- `docs/v4.x/structure-changes/` — the evolution log for structural changes to the harness.

---

## Subagent development
See [.claude/SUBAGENT-GUIDE.md](.claude/SUBAGENT-GUIDE.md) for how to add or revise subagents.

---

## Voice
Voice is pack-driven. The active pack's voice tier (`resolve_pack_field voice.default_tier`; neutral default `internal`) sets the style; a pack may supply a corpus + critic. Internal dev agents declare `voice: internal`. When in doubt, internal is the default.
