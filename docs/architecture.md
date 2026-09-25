# Architecture

How Lintel is put together, and why. If you want the workflow rather than the structure, read
[the cycle](the-cycle.md) first.

---

## One sentence

Lintel is a **spine** of company-neutral workflows and local helpers, plus an active **pack**
for team identity and policy. Thin client adapters bind workflow operations to actual host
tools. The spine is not a universal execution engine: the host owns execution and permissions.

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
| **Cycle** | the nine phase skills, the `cycle` orchestrator with explicit phase ranges, the `fix` shortcut, the opt-in `swarm` execution profile, plus `resume`, `status`, `jobs` |
| **Engineering modules** | `ta`, `da`, `sc`, `dh`, `tq` — each an orchestrator plus sub-skills — and `full-engineering-pass`, which composes all five in dependency order |
| **Generate** | a shared content pipeline (outline → write → design → QA) feeding per-format renderers |
| **Frontend** | a design-director orchestrator over typography, motion and shader sub-skills, each emitting a JSON contract, plus a six-dimension review gate |
| **Context** | `context-warm` modes for files, related sources, prior sessions and decision records; budget visibility; `pause` and `resume` |
| **Session harness** | `doctor`, `scaffold`, `catalog`, `uniformity`, `lessons-add`, `lessons-surface`, `adr-new`, `capture`, `audit`, `code-freeze` |
| **Pack and role** | `pack-create`, `pack-switch`, `pack-list`, `pack-validate`, and the role lifecycle |
| **Intake and inspection** | `define` for task-relevant requirements and optional strategy; `inspect` with plan/repo targets and engineering/design/devex lenses |
| **Verification and diagnosis** | `verify` with read-only default and explicitly authorized repair, `diagnose`, and `cross-check` with an actual independent reviewer |
| **Browser and documents** | `web-session` browse/scrape/open/cookies modes, `generate-docs`, and the retained per-format document providers |

`skills/CATALOG.md` is generated from skill frontmatter on push, never hand-curated — the same
anti-drift principle as the capability table.

Consolidation changes entrypoints, not accepted evidence, ownership or provider contracts.
The [native workflow migration](migrations/2026-09-25-native-workflows.md) maps older entrypoints
to current methods and explains non-destructive updates.

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
| `client_capabilities.py` and `cli-tiers.sh` | one validated surface/operation registry, explicit session-binding selection and conservative legacy/table views |
| `swarm_contract.py` and `li-swarm.py` | validate opt-in swarm topology, per-lane scope and close evidence without executing artifact content |

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

It is mechanical-first: pattern matching recommends common routes. An ambiguous result needs
explicit clarification or judgment; a configured budget or staged escalation path is not evidence
that an additional model call occurred.

## Swarming as an execution profile

Swarming is an explicit profile over PLAN, BUILD and REVIEW, not a tenth phase. PLAN keeps one
authoritative task map and adds a pointer to committed execution topology only after operator opt-in.
BUILD can then fan out dependency-ready lanes whose write scopes are disjoint and whose changes are
attributable to separate worktrees, patches or an equivalent host-enforced sandbox. If the host or
isolation cannot prove that attribution, the same lane briefs run sequentially.

Every swarm has one coordinator. Workers own only their declared paths and report; independent
reviewers own only their lane reviews. The coordinator alone writes shared ledgers, generated
reducers, commits and integration history. Passing lane reviews are inputs to fan-in; REVIEW still
checks the reconciled branch across specification, quality and active-pack compliance.

The committed contract lives beside the trio under
`.claude/plans/<initiative>/swarm/`. Runtime attempts stay gitignored. This makes recovery depend on
reviewable artifacts and attributable changes rather than chat memory or a still-running worker.
See [swarming work](concepts/swarming-work.md) for the artifact tree and operating procedure.

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
pack's evaluators before it is allowed through. The schema, helpers and evaluator policy ship, but
there is no universal automatic interceptor: a workflow must invoke Brief Forge explicitly, as the
swarm profile does before dispatch. Pack configuration selects behavior for an invocation; it does
not install a host hook.

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
| `<repo>/.claude/` | per-repo, **committed** | `memory/` (lessons, working state, personas), `decisions/`, `plans/` including optional swarm topology and evidence |
| `<repo>/.claude/runtime/` | per-repo, **gitignored** | cycle state, job data, session saves, repo event log |

The committed/gitignored split is the load-bearing part. Knowledge that should be reviewed in a pull
request is committed. Churn that would only create merge conflicts is not.

A repo carrying `.claude/lintel-layout.yaml` is on this layout. One without it predates the move and
still uses the legacy locations.

---

## Multi-CLI without duplication

Two mechanisms, one source each:

1. **Instructions** — the shared `SESSION-PROTOCOL.md` is repeated inline in AGENTS.md, CLAUDE.md and both scaffold templates. `bin/li-instructions.py` keeps those marked blocks identical while preserving unique project context. `AGENT-INSTRUCTIONS.md` supplies the navigation/read order; personal global files are unnecessary for the reusable protocol. This deliberate repetition supersedes the older pointer-only direction.
2. **Skills and agents** — written once at the repo root, exposed through native plugins,
   generated discovery wrappers or explicit manual handoff. Existing Claude skills/agents/hooks,
   Copilot native kit and other useful routes remain. `li-adapter.py` delegates to the same
   `li-copilot.py` source-bundling and ownership engine rather than duplicating an installer.

`lib/cli-tiers.yaml` is schema-version-2 JSON-compatible YAML, read by the standard-library
`client_capabilities.py`. Every CLI/desktop/IDE/cloud surface keeps vendor documentation,
delivered integration and observed execution distinct per operation. The installer, generated
README and compatibility shell API consume that source. Exact IDs and legacy aliases never
collapse neighboring surfaces.

Current session bindings select actual tool names, availability, permissions and attributable
isolation. The selector does not execute tools, grant permission or clear independent review.
Unknown/denied capabilities remain explicit; manual/serial handoffs retain the original map,
acceptance and effective profile reference. See [Universal support](multi-cli.md) and the
[adapter contract](../shims/universal/ADAPTER.md).

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

## Portable repository boundary

Selected clients receive core wrappers only under their documented repository discovery roots,
or an explicit manual `START.md` route. Copilot retains `.github/skills/li-*` and its three
`.github/agents/` profiles. All use one `.github/lintel/` bundle, including actual source product
metadata, so another checkout does not depend on the originating workstation.

Installation records managed files, selected surfaces and protocol blocks, preserves project prose
and refuses local-edit conflicts before writes. It does not provision accounts, enable policies,
install private packs, change models or activate/adapt hooks. Local integrity is not live client
acceptance. See [client adapters](client-adapters.md) and [enterprise adoption](enterprise-adoption.md).
