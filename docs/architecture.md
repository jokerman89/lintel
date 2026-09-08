# Architecture

How Lintel is put together, and why. If you want the workflow rather than the structure, read
[the cycle](the-cycle.md) first.

---

## One sentence

Lintel is a **spine** — a company-neutral execution engine of skills, agents and hooks — plus one
active **pack** that supplies identity. The spine decides *how* work runs; the pack decides *what
counts as correct* for your team.

Everything else in this document is a consequence of that split.

---

## The two parts

```
┌──────────────────────────────────────────────────────────────┐
│  PACK — identity, swappable        packs/<name>/pack.yaml    │
│    voice · compliance · personas · roles · brand · knowhow   │
│    navigation policy · hand-off evaluators                   │
│    resolved by lib/pack-resolver.sh                          │
│    _default = neutral baseline; a company pack layers over it│
├──────────────────────────────────────────────────────────────┤
│  SPINE — execution, stable                                   │
│    skills/   the nine-phase cycle, modules, session harness  │
│    agents/   subagent role definitions, eight categories     │
│    hooks/    selected checks, Claude Code adapter              │
│    lib/      the mechanical helpers everything else sources  │
│    scaffolding/01-foundation/  what gets installed elsewhere │
└──────────────────────────────────────────────────────────────┘
```

The spine carries no company identity. That is not an aspiration — it is enforced: a shape test
fails the build if company-specific or non-English text appears in the public tree. The identity
that used to be hardcoded was extracted wholesale into an external pack, which is what made
publishing the harness possible at all.

---

## The spine

### `skills/` — what your CLI can invoke

Canonical skills live at `skills/<name>/SKILL.md`. Claude plugin workflows use `/li:<name>`; the Copilot repository kit exposes native core adapters as `li-<name>`. They fall into clusters:

| Cluster | What it holds |
|---|---|
| **Cycle** | the nine phase skills, the `cycle` orchestrator, four composite shortcuts, plus `resume`, `status`, `jobs` |
| **Engineering modules** | `ta`, `da`, `sc`, `dh`, `tq` — each an orchestrator plus sub-skills — and `full-engineering-pass`, which composes all five in dependency order |
| **Generate** | a shared content pipeline (outline → write → design → QA) feeding per-format renderers |
| **Frontend** | a design-director orchestrator over typography, motion and shader sub-skills, each emitting a JSON contract, plus a six-dimension review gate |
| **Context** | warming (load specific files, related files, prior sessions, decision records), budget visibility, save and restore |
| **Session harness** | `doctor`, `health`, `scaffold`, `catalog`, `uniformity`, `learn`, `lessons`, `adr-new`, `capture`, `audit`, `code-freeze` |
| **Pack and role** | `pack-create`, `pack-switch`, `pack-list`, `pack-validate`, and the role lifecycle |
| **Plan review** | `office-hours`, `plan-eng-review`, `plan-ceo-review`, `plan-design-review`, `plan-devex-review` |

`skills/CATALOG.md` is generated from skill frontmatter on push, never hand-curated — the same
anti-drift principle as the capability table.

### `agents/` — delegated roles

Agent definitions span eight categories: engineering, security, compliance, devops, customer,
communication, doc-gen and frontend. Each is a markdown role definition with uniform frontmatter
(`name`, `category`, `description`, `tools`, `voice`, `tier`, `cli_support`).

The engineering category splits into general-purpose roles (code review, architecture, refactoring,
debugging, planning, testing) and **module-spawned specialists** — the agent half of the five
engineering modules.

Agent selection follows a five-level precedence model; see [precedence](precedence.md).

### `hooks/` — enforcement

Selected hooks register on a Claude Code plugin install through `hooks/hooks.json`:

| Event | Hook | Behaviour |
|---|---|---|
| SessionStart | `session-digest` | injects active pack, recent lessons, open jobs, recent decision records |
| PreToolUse (Edit/Write) | `no-secrets-in-edit` | warns on a secret about to be written |
| PreToolUse (Bash) | `secret-scan-block` | **blocks** a commit or push introducing a secret |
| PreToolUse (Bash) | `customer-data-block` | **blocks** a commit or push introducing customer data |
| PreToolUse (Bash) | `no-direct-main-push` | warns on a direct push to the default branch |
| PostToolUse (Edit/Write) | `memory-budget-warn` | warns when a memory file outgrows its budget |
| Stop | `cycle-incomplete-warn` | surfaces the position footer when a turn ends mid-cycle |
| UserPromptSubmit | `cycle-position-inject` | re-asserts cycle position at turn start |
| UserPromptSubmit | `no-customer-data-in-message` | scans the prompt itself |

The remaining hooks — the module warn-hooks for architecture drift, schema drift, coverage drops,
missing rollback plans and similar — stay opt-in.

Two properties worth knowing. **Blocks are overridable but never silent:** an override needs an explicit
environment flag, and every one is written to an audit log with whatever reason you supply. And
**warn-hooks fail open:** a missing state directory produces no output rather than an error, so a
half-configured install degrades quietly instead of breaking your session.

This hook bundle implements the **Claude Code protocol**. Copilot has its own hook API, but Lintel does not ship that translation. The Copilot kit installs native skills and agents without hooks; see [Copilot](copilot.md).

### `lib/` — the mechanical layer

This is where the repo's central rule lives: *if a guarantee is only prose, it is not a guarantee.*

| Helper | Responsibility |
|---|---|
| `paths.sh` | one canonical answer for every path, so no skill hand-rolls a location |
| `state.sh` | the cycle ledger. `state_append` / `state_last`, with resolution scoped to the current cycle segment so a prior cycle's entries cannot poison the footer or a resume |
| `memory.sh` | lessons and memory operations as commands, not as a format a skill has to remember |
| `pack-resolver.sh` | `resolve_pack_field <dotted.path>` — the single accessor for all identity |
| `auto-decide.sh` | `is_one_way_door` — classifies selected irreversible decision patterns when the workflow calls it |
| `cycle-footer.sh` | `render_cycle_footer` — the position footer, mode-aware, with an ASCII fallback |
| `scale-estimator.sh` | sizing, and the calibration path that turns token estimates from guesses into measurements |
| `cli-tiers.sh` | generates the capability table from `cli-tiers.yaml`; a shape test fails the build if the README disagrees |

---

## The pack

A pack is `packs/<name>/pack.yaml` plus any corpus files it references. It declares:

| Field | Declares |
|---|---|
| `voice` | tier, corpus path, enforcement scope, active gates |
| `compliance` | mode (`hard` / `advisory` / `off`) and which hooks the pack activates |
| `persona` | operator persona source, and whether output is checked against it |
| `roles` | role definitions directory and default role |
| `brand` | document-generation templates and colour tokens |
| `knowhow` | tag-indexed knowledge, and whether it may override session priors |
| `lessons` | immutable lessons shipped with the pack |
| `opinions` | stance documents |
| `navigation` | default and high-risk workflows, orientator token budget |
| `brief_forge_handoffs` | which evaluators fire at each hand-off boundary |

The neutral `_default` pack supplies advisory defaults and no company-specific policy gates. That is the
point: the harness works out of the box without imposing anyone's opinions.

### Resolution and inheritance

`lib/pack-resolver.sh` resolves the active pack at session start:

- A pack may `extends:` another. The resolver walks parent to child, merging top-level keys with the
  child overriding. Merging is **wholesale block-replace**, not a deep merge — so a pack that
  declares `voice` owns all of `voice`, with no surprise half-inherited state.
- `_default` is the **fallback for missing fields**, not an implicit parent. Anything a pack leaves
  unset lands on the neutral value.
- Failure modes are guarded: an `extends:` cycle is refused, and an invalid active pack falls back
  to `_default` with a warning. If `_default` itself is invalid, the resolver fails loudly rather
  than guessing.

### Extension packs

Since the extension-pack contract, a pack can ship more than identity — it can carry its own skills,
agents, hooks and workflow presets, and install as a plugin in its own right. That is how a team
adds domain-specific capability without forking the spine.

---

## Navigation

Every skill that owns a job declares `workflow_root: true` in frontmatter, along with its entry and
exit conditions. At SENSE an **orientator** reads the request, the active pack's navigation policy
and any open jobs, then recommends a workflow, an entry phase and a risk level.

It is mechanical-first: cheap pattern matching decides the common cases, and only an ambiguous one
escalates to a model call, inside a pack-overridable token budget.

---

## Depth — the engineering modules

Five first-class modules, each with the same internal shape: one orchestrator, sub-skills per
capability, named agents to dispatch to, gates, and a scoring rubric.

| Module | Capabilities |
|---|---|
| `ta` | quality attributes, boundary review, scaling plan, complexity budget |
| `da` | schema design, migration plan, sharding, retention, query-pattern audit, analytics readiness |
| `sc` | threat model, auth review, compliance evidence, dependency and secrets posture |
| `dh` | deployment plan, rollback strategy, observability spec, SLI/SLO, capacity, cost, on-call |
| `tq` | contract tests, perf budgets, coverage strategy, regression detection |

Each runs at three granularities — full, loop, or a single capability — so the module is useful both
as a half-day architecture pass and as a two-minute question.

`full-engineering-pass` composes all five in dependency order: architecture first, then data and
security in parallel, then hosting, then testing.

---

## Cross-cutting constructs

**Hand-off envelopes.** Work crossing a boundary — spawning a subagent, transitioning a phase,
passing to a cold executor — can be wrapped in a standardised envelope and scored by the active
pack's evaluators before it is allowed through. *Envelope construction is dormant by decision: it is
opt-in, not auto-armed.* The schema and evaluators ship; the automatic gate does not.

**Meta-infra discipline.** Changes to the harness's own structure ripple into every downstream
cycle, so they run under four extra gates — a structure-impact entry, a compatibility audit, the
shape-test suite, and a future-operator recap. See [the cycle](the-cycle.md#the-gates-in-one-list).

---

## Where state lives

Four roots. Two are machine-global, two live in your repo:

| Root | Scope | Holds |
|---|---|---|
| `~/.lintel/` | machine-global (configurable with `LINTEL_HOME`) | operator preferences in `profile.yaml` (mode, role); active pack selected by `packs/active-pack`; installed packs, cross-repo job registry, operator audit log |
| `~/.claude/` | machine-global | your CLI's own home — `settings.json`, and hooks you armed by hand on a bare install |
| `<repo>/.claude/` | per-repo, **committed** | `memory/` (lessons, working state, personas), `decisions/`, `plans/` |
| `<repo>/.claude/runtime/` | per-repo, **gitignored** | cycle state, job data, session saves, repo event log |

The committed/gitignored split is the load-bearing part. Knowledge that should be reviewed in a pull
request is committed. Churn that would only create merge conflicts is not.

A repo carrying `.claude/lintel-layout.yaml` is on this layout. One without it predates the move and
still uses the legacy locations.

---

## Multi-CLI without duplication

Two mechanisms, one source each:

1. **Instructions** — the shared `SESSION-PROTOCOL.md` is repeated inline in AGENTS.md, CLAUDE.md and both scaffold templates. `bin/li-instructions.py` keeps those marked blocks identical while preserving unique project context. `AGENT-INSTRUCTIONS.md` supplies the navigation/read order; personal global files are unnecessary for the reusable protocol. This deliberate repetition supersedes the older pointer-only direction.
2. **Skills and agents** — written once at the repo root, shipped through small per-CLI plugin
   manifests and generated adapters that reference shared canonical content. Copilot uses generated native core adapters and a dedicated manifest; the portable installer bundles referenced resources for other checkouts. Other adapters may use manifest interoperability.

Per-CLI capability is declared once in `lib/cli-tiers.yaml` and everything else generates from it —
the README table, and the honest tier message `/li:welcome` prints on first run.

---

## The factory

`bin/li-scaffold` installs the disciplines above into any other repo: a `CLAUDE.md`, the core
principles, and a `.claude/` home with memory, plans and decision-record templates.

Lintel dogfoods this. This repo's own `CLAUDE.md` is the instantiated form of the template it ships
— which means the factory is exercised on every commit here, not only when someone runs it.

---

## Tests as structural checks

The test runner discovers checks in five tiers. Counts change as contracts are added:

| Tier | Asserts |
|---|---|
| **shape** | structural contracts — required frontmatter fields, hook registration, canonical paths, decision-record number uniqueness, generated-table sync, no non-English or company-specific text in the public tree |
| **unit** | helper behaviour — state segmenting, memory operations, pack resolution and inheritance, one-way-door detection |
| **integration** | cross-component links |
| **end-to-end** | a full path through the harness |
| **behavior** | a mechanism exercised hermetically, to prove it fires rather than merely exists |

The shape tier is the interesting one. It is what stops the system drifting from its own
self-description — historically this repo's dominant failure mode, and the reason the tier exists.

---

## See also

- [The cycle](the-cycle.md) · [Getting started](getting-started.md) · [Glossary](GLOSSARY.md)
- [Multi-CLI support](multi-cli.md) · [Precedence](precedence.md) · [Compliance](compliance.md)
- Decision records: `.claude/decisions/`

## Copilot repository boundary

The portable kit adds native core skills under `.github/skills/li-*` and three custom agent profiles under `.github/agents/`. Installed repositories carry workflow resources under `.github/lintel/` so a new checkout does not depend on the originating workstation. Installation records managed artifacts and refuses local-edit conflicts. It does not provision accounts, enable enterprise policies, install private packs or adapt Claude hooks. See [Copilot](copilot.md) and [enterprise adoption](enterprise-adoption.md).
