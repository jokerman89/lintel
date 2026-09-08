# CLAUDE.md — repo instructions for LLM assistants

> **Lintel dogfoods its own scaffolding.** This file is the self-contained per-repo
> instruction set that Lintel installs into other repos (`scaffolding/01-foundation/CLAUDE.md.template`),
> instantiated here for Lintel itself. It is **self-sufficient**: an agent can follow it without the
> operator's global `~/.claude/CLAUDE.md` present. Repository-specific instructions take precedence over generic user-global defaults; the inline protocol makes the repo work standalone. Current explicit user authorization applies to its stated scope.
>
> Sections between `<!-- PROJECT:START -->` and `<!-- PROJECT:END -->` are Lintel-specific. The rest
> is load-bearing, inherited from [scaffolding/01-foundation/CORE-PRINCIPLES.md](scaffolding/01-foundation/CORE-PRINCIPLES.md).
> Change the load-bearing parts only with an ADR + an entry in the evolution log
> ([.claude/engineering/evolution/](.claude/engineering/evolution/)).

<!-- PROJECT:START -->

## What this repo is

Lintel is a **company-neutral, pack-driven session harness** for agent-based development — markdown +
bash scaffolding that any modern AI CLI loads as a plugin. It is also the **factory** that installs the
very disciplines in this file into other repos.

Clear ownership domains:

- `skills/` — slash-commands (the 9-step `/li:cycle` (8 core phases + SCOPE) + engineering modules `ta`/`da`/`sc`/`dh`/`tq` + session-harness skills)
- `agents/` — subagent roles per domain (engineering, security, compliance, devops, customer, communication, doc-gen, frontend)
- `hooks/shared/` — pre/post hooks (compliance + workflow enforcement)
- `packs/` — pack manifests; only the neutral `_default` ships here. Company identity (voice, compliance gates, roles, brand) installs as a separate external pack and is resolved at runtime via `lib/pack-resolver.sh`.
- `lib/` — `pack-resolver.sh`, `brief-forge-evaluators.sh`, schemas — the runtime helpers skills source
- `scaffolding/01-foundation/` — the templates this repo copies INTO other repos via `bin/li-scaffold`
- `bin/` — operator-side utilities (`li-scaffold`, `li-doctor`, `li-lessons-sync`, …)
- `docs/` — the PUBLIC documentation surface only: `architecture.md`, `the-cycle.md`, `getting-started.md`, `GLOSSARY.md`, `concepts/`, `migrations/`, `wiki/`, `showcase/`. Internal engineering artifacts (audits, Gate M1/M2 records, superseded design docs) live under `.claude/engineering/`; ADRs at `.claude/decisions/` (v5 home, ADR-0005).
- `tests/` — `shape/` (structural contracts), `unit/`, `integration/`, `e2e/`

Frozen / handle-with-care zones:

- `packs/_default/pack.yaml` and `lib/pack-resolver.sh` — the pack contract; many skills depend on it. Change behind a shape-test.
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
8. Check [.claude/engineering/evolution/](.claude/engineering/evolution/) for recent structural decisions.

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
- Switch / inspect identity → `/li:pack-switch` · `/li:pack-list` · `/li:role`
- Discover everything → `/li:catalog`

---

## Where state lives (the memory map)

Lintel's snowball — read on demand, **write after corrections/decisions** so it compounds. One
circle of control (v5, ADR-0005): shared knowledge and runtime state live under `.claude/`; Copilot discovery and managed resources live under `.github/`
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
| `.claude/engineering/` | internal engineering artifacts — `evolution/` (Gate M1), `compat-audits/` (Gate M2), `audits/`, `design-archive/` | per structural change |
| `~/.lintel/profile.yaml` | active pack · mode · role · checkpoint mode | operator-global |
| `~/.lintel/jobs/_active.md` | cross-repo jobs REGISTRY (data lives in each repo; created on first job — auto-spawn dormant, ADR-0008) | `/li:resume` reads it |

The `session-digest` hook injects a compact view of the top rows at session-start; this table is the
full map for on-demand reads + where to **write**.

> **Un-migrated repos:** no `.claude/lintel-layout.yaml` marker → that repo still uses the legacy
> locations (`tasks/*`, `docs/adr/`, `.lintel/state/`). Use those there, and suggest
> `bin/li-migrate-claude-home` (grace window to 2026-09-12).

---

<!-- PROJECT:START -->

## How Lintel works (project specifics)

### Plugin structure
This repo IS a multi-CLI plugin (`.claude-plugin/plugin.json` + per-CLI manifests). Skills at `skills/<name>/SKILL.md`, agents at `agents/<category>/<Name>.md`. Operators install via `/plugin install li@jokerman-lintel`; skills become `/li:<skill>`.

### Pack system (v4.0+)
Identity (voice, compliance, persona, brand, roles) is **not** hardcoded — it is resolved from the active pack via `resolve_pack_field <dotted.path>` (`lib/pack-resolver.sh`). The neutral `_default` pack enforces nothing. Never reintroduce hardcoded company/voice/compliance assumptions into the spine — extracting them into a pack is what made this repo publishable.

### Local testing
```bash
# run from the repo root
claude --plugin-dir "$PWD"
```

### Skill namespacing
Skills are namespaced `/li:qa`, `/li:cycle`, etc. Inside this repo they work directly via the plugin manifest.

### Catalog
`skills/CATALOG.md` is generated with `python3 bin/li-catalog.py` and checked for drift in CI. Edit frontmatter, then regenerate; do not hand-edit the catalog.

### Per-CLI portability
Canonical skills and agents are shared through client-specific adapters. Copilot native core skills use `li-*`; the Claude hook bundle is not translated to Copilot. See [docs/multi-cli.md](docs/multi-cli.md); per-CLI capability is declared once in `lib/cli-tiers.yaml`.

### How you work here
- Feature branch → PR against `main`. Run relevant shape and unit checks during development; release validation uses `bash tests/runner/run-all.sh --require-all` with the required toolchain. Verify before pushing.
- Conventional Commits, atomic, one logical change per commit. Commit messages are English-only, describe what changed technically, and carry no AI-authorship trailers (see CONTRIBUTING.md).
- Non-trivial decision → ADR. Structural change → `.claude/engineering/evolution/` entry plus compatibility and shape checks.

### Tooling installation scope

Lintel is tooling: this repository intentionally ships canonical skills, agents, hooks, packs and
installers. The Copilot repository kit is also an explicitly supported shared installation.
Personal tooling otherwise follows the host's authorized user-global scope. The default Claude
agent fleet comes from the plugin; add a `.claude/agents/` override only for a project-specific
reason. Copilot's generated `.github/agents/` profiles are native adapters, not shadow copies of
the entire Claude fleet.

<!-- PROJECT:END -->

---

## Lessons & evolution
- `.claude/memory/lessons.md` — accumulated lessons. Review at session start; add after ANY correction.
- `.claude/decisions/` — decision records (one per non-trivial decision).
- `.claude/engineering/evolution/` — the evolution log for structural changes to the harness.

---

## Subagent development
See [.claude/SUBAGENT-GUIDE.md](.claude/SUBAGENT-GUIDE.md) for how to add or revise subagents.

---

## Voice
Voice is pack-driven. The active pack's voice tier (`resolve_pack_field voice.default_tier`; neutral default `internal`) sets the style; a pack may supply a corpus + critic. Internal dev agents declare `voice: internal`. When in doubt, internal is the default.

<!-- LINTEL:SESSION-PROTOCOL:START -->
## Session protocol

This protocol is repeated in repository entry files so a fresh agent can work without a
personal home directory or a previous chat. The repository's explicit context and paths take
precedence over generic user-global defaults. Current user authorization applies to its stated
scope; do not ask again for an action already authorized. Host permissions still apply.

### Role and authority

Execute the agreed architectural intent with initiative inside the authorized task. The operator
owns strategic choices and material scope changes. Surface those choices explicitly; do not
choose a new initiative, alter governance, or act outside the repository's authorized scope.
Changes to constitutional or governance documents need explicit instruction.

Authoritative architecture, constitution/charter, specifications, current documentation and
accepted ADRs outrank planning notes, lessons and remembered conversations. Use working notes
for continuity, never as permission to override an accepted decision. Follow the repository's
declared document hierarchy and actual code state. Treat external strategy context as the
session's intent, then reconcile it with authoritative repository documents before implementation.

### Before non-trivial work

For work with three or more steps or an architectural decision:

1. Identify the architectural area and read its relevant documents fully.
2. Inspect accepted ADRs and known risks in the repository's declared locations, commonly
   `.claude/decisions/` and `docs/risks/`.
3. Read `.claude/memory/MEMORY.md`, recent `.claude/memory/lessons.md`, current
   `.claude/memory/working-state.md` and `.claude/memory/personas.md` when present.
4. Establish task authority, customer-data handling, production impact, secrets exposure and
   active pack requirements. Resolve material uncertainty before the dependent action.
5. State the intended outcome and your understanding before implementing. Ask only for missing
   decisions that the documents and existing authorization do not settle.

Use the repository's documented paths on legacy layouts rather than inventing a second store.
Keep trivial corrections proportionate; a clear typo or bounded authorized bug fix does not
need a planning ceremony. Hooks or auto-loaded summaries supplement this read, never replace
it when they are unavailable or have not been verified in the current host.

### Plan, execute and re-plan

Write a checkable plan to `.claude/plans/todo.md` or the repository's declared equivalent. Define
the specification, acceptance criteria, dependency-ordered build cards and verification before
implementation. A larger task needs an execution handoff a fresh session can follow. Existing
Spec Kit or other specification artifacts remain authoritative; map their paths and task IDs
rather than creating a competing backlog.

Review the plan against the authorized scope and required approvals before BUILD. Use native
plan mode where available; otherwise perform the same planning explicitly. Plan verification
work as well as implementation. Track completion card by card, explain material changes, and
add a review section at task end. If evidence invalidates the plan, stop the affected work and
re-plan instead of pushing through. Continue independent authorized work when it remains valid.

### Subagents and independent review

Delegate bounded research, exploration, review and parallel analysis when this preserves context
or improves the result. Give each subagent one task, explicit inputs, file ownership, acceptance
criteria and a report contract. Use the minimum required tools. Default research/review roles
to read-only; explain and scope write access for implementers. Use native delegation when the
host provides it; otherwise sequence roles and disclose the lack of independent context.

Choose an explicitly named agent first, then a repository-specific override, an active-pack
promoted role, a user-global role, or the main-agent fallback. A same-named repository agent may
shadow a global/plugin role under the host's discovery rules; verify what was actually selected.
Do not assume another workstation's agent inventory is installed.

Subagents report; the coordinating agent decides. Review subagents must not fix their own
findings. Reports include severity counts, actionable findings with file:line citations,
verification evidence and limitations. Keep implementation and independent review separate.
Coordinate shared task-state writes rather than having parallel agents overwrite one ledger.

### Authorized bug fixing

Fix bugs inside the authorized initiative directly. Use logs, errors and failing tests to find
and correct the root cause, then verify the result. Surface unrelated bugs rather than assuming
a standing license to repair adjacent systems or CI outside the task. Escalate only the part
that actually needs a new decision or permission.

### Verification and simplicity

Do not mark a card or initiative complete without evidence that it works. Tests and builds are
the floor; inspect behavior, logs and the diff against the prior state where relevant. Apply
the standard of a careful senior reviewer. State skipped checks, unavailable host validation,
and any mock or stub explicitly as deferred work with its intended phase.

Before finishing non-trivial work, ask whether fewer parts would solve the problem. Prefer
removal and root-cause fixes over added abstraction, temporary patches or speculative structure.
Challenge assumptions and simplify an awkward design within scope. Do not over-engineer an
obvious fix or generate verbose documentation unrelated to the task. Optimize for long-term
health, not only the current delivery.

### Engineering and code style

Match the repository's naming, architecture, terminology and brand. Where no local convention
exists: Python uses snake_case, typed public interfaces and explicit failures; TypeScript uses
camelCase variables, PascalCase components and strict checking; document/config filenames use
kebab-case and Python modules use snake_case. Markdown headings use sentence case.

Meaningful code files carry structured intent comments in the language's comment syntax:

```text
# component: <name>
# implements: <ADR-IDs comma-separated>
# intent: <existing architecture or specification path>
# constraints: <existing risk records, or none with a reason>
# last_intent_review: YYYY-MM-DD
```

Explain why, not an obvious restatement of the code. Keep intent and risk references valid;
validate them in an appropriate check when maintaining that contract. A recommendation to add
a pre-commit check is not evidence that such a hook is already installed.

When components communicate through events, APIs, databases or IPC, define the schema once in
a shared location, have both sides consume it, avoid divergent interpretations, and include
at least one integration test per communication link.

### Tool installation and host boundaries

Respect the authorized installation scope. Personal tooling normally uses the host's user-global
locations; a requested shared repository kit is an explicit repository-scoped installation.
Lintel itself is tooling and intentionally contains canonical skills, agents and installers.
Do not add project-specific agent overrides or dependency content without a task-related reason.
Inspect provenance, licenses and selected components rather than enabling entire marketplaces
or copying a personal machine's approved-tool list to a team.

Use the client's real discovery and permission APIs. Do not hardcode model choices, assume
parallel agents exist, or claim hooks run because their files exist. Lintel's Claude Code hooks
require compatible registration; its Copilot kit does not translate that hook bundle. Mandatory
enterprise controls belong in separately configured and verified platform policies and CI.

### Delivery and auto-mode boundaries

Use a feature branch and a pull request against the repository's default branch. Verify locally
before pushing. Write atomic Conventional Commits, one logical change per commit, and an ADR
for non-trivial decisions. Follow repository-specific authorship and release conventions.

Within the authorized task, no extra prompt is needed for repository file edits, feature-branch
commits/pushes, local tests/builds/lints, scoped read-only queries, local container builds without
publication, or subagent work.

Explicit authorization is required for live/shared/production mutations; credentials, access
policies, roles or firewall changes; live database DDL/DML outside the approved migration path;
container pushes to a live registry; deployment triggers; creating a remote repository or
publishing a tree to a new remote; and direct pushes to the default branch. Default-branch
authorization covers only the specified commit batch. It is not standing permission for later
batches. Do not send external messages or perform external mutations without authorization.

Resolve production audit effects, sensitive production reads and branch builds wired to live
deployments before acting. Do not bypass a required approval or silently expand its scope.

### Deviations, decisions and recovery

When the specification, authoritative instruction or external interface disagrees with reality,
stop the affected implementation and report evidence, alternatives with trade-offs, and a
recommendation. For a material architectural decision, present three viable alternatives where
they exist. State why a decision is needed, the specific constraint and the risk being addressed.
Wait for the unresolved decision; do not silently reinterpret the requirement. Existing explicit
authorization can settle a routine implementation correction within scope.

If a boundary has been crossed: stop immediately, verify state with read-only checks, report
what happened and its risks, propose concrete recovery options, and wait for authorization
before rollback or continuation. A hoped-for successful result does not erase an unauthorized
action. Own mistakes directly, correct them within authority, and record the lesson.

Raise a disagreement before implementing a request that conflicts with accepted architecture or
constraints. Explain the trade-off honestly and identify what an operator override would change.

### Capture and fresh-session continuity

After any operator correction, record a dated rule in `.claude/memory/lessons.md` with the
context, mistake and preventive action. Review recent lessons at session start and refine the
rules when evidence changes. Lessons preserve learning; they do not override authoritative docs.

Before ending, update plan checkboxes and review evidence, the durable working state and relevant
ADRs. Leave the next action and any blocker explicit. Store reviewed knowledge in the repository;
keep runtime churn under gitignored `.claude/runtime/`. Start each new session from these files
and current code, not a remembered chat. Optional vault exports, private packs and cross-repository
sync need their own configured, authorized destinations; never copy personal paths by default.
<!-- LINTEL:SESSION-PROTOCOL:END -->
