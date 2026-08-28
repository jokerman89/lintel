# Glossary

The load-bearing terms a Lintel newcomer meets before they are defined. One screen; skim it once and
refer back. Fuller treatment lives in [architecture](architecture.md), [the cycle](the-cycle.md),
and the per-mechanism pages under [concepts/](concepts/).

| Term | What it means |
|---|---|
| **spine** | The company-neutral core — 125 skills, 69 agents, 33 hooks, and the `lib/` helpers they all source. The spine decides *how* work runs. It carries no company identity, and that is enforced rather than promised: a shape test fails the build if company-specific or non-English text appears in the public tree. |
| **pack** | The identity layer the spine reads from — voice, compliance gates, personas, brand, roles, navigation policy. Nothing is hardcoded; every value resolves through `resolve_pack_field` (`lib/pack-resolver.sh`). Lintel ships exactly one pack, the neutral `_default`, which enforces nothing. Switch with `/li:pack-switch`. |
| **extension pack** | A pack that ships more than identity — its own skills, agents, hooks and workflow presets, installed as a plugin in its own right. How a team adds domain capability without forking the spine. `_default` declares `is_extension: false`; see [pack inheritance](concepts/pack-inheritance.md). |
| **cycle** | The main workflow, run by `/li:cycle`: nine phases that turn a raw request into shipped, captured work. Every phase declares what it produces and what skipping it costs. |
| **the nine phases** | **SENSE → SCOPE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE** — eight core phases plus the light SCOPE phase between SENSE and DEFINE. Detailed in [the cycle](the-cycle.md). |
| **mode preset** | A named subset of the nine, selected with `--mode`. `hotfix` skips SCOPE, DEFINE, DISCOVER, PLAN and CAPTURE; `research-dive` stops after DISCOVER; `full`, `internal-tool` and `meta-infra` run everything. The skip map lives once in `lib/cycle-modes.sh`, so no skill can disagree about which phases a mode runs. |
| **wedge** | The specific first cut of the problem — the slice DEFINE commits to instead of the whole problem space. DISCOVER maps the codebase around the wedge; PLAN breaks that wedge down, not the original vague ask. |
| **depth schema** | How deep the work breakdown goes: `flat` (size XS/S), `phased` (M), or `tree` (L/XL). SCOPE derives it from the estimated size and PLAN reads it to pick the breakdown template. One signal, three values. |
| **`scope.md`** | What SCOPE emits: resolved size, the chosen reading of an ambiguous request, the depth schema, and any route override. Written into the active job directory, or `.claude/runtime/state/scope.md` when no job is open. DEFINE inherits the wedge from it; PLAN inherits the depth schema. |
| **trio** | The three cold-executor files born together in PLAN — `plan.md`, `spec.md`, `prompt.md` — under `.claude/plans/<slug>/`. PLAN blocks if any of the three is missing or empty, because a two-of-three hand-off fails silently later. |
| **cold executor** | Whoever picks the work up with no prior context: a fresh session after a compaction, a spawned subagent, or a different CLI entirely. The trio exists so that reader needs nothing beyond it. |
| **`workflow_root`** | Frontmatter flag marking a skill that owns a job and can spawn sub-work. Nine skills carry it: `/li:cycle`, `/li:plan`, the five engineering modules (`ta`, `da`, `sc`, `dh`, `tq`), `/li:full-engineering-pass` and `/li:uniformity`. The job-begin hook keys on this flag. |
| **hand-off envelope** | The standard wrapper for work crossing a boundary — subagent spawn, phase transition, cold-executor pass — scored by the active pack's evaluators. The schema (`lib/envelope-schema.yaml`) and evaluators ship, but envelope construction is dormant by decision: opt-in, not auto-armed. |
| **lesson** | A numbered rule recorded after a correction, in `.claude/memory/lessons.md`. Surfaced mechanically at SENSE via `/li:lessons-surface` rather than left to be remembered — the only mechanism that compounds learning across fresh sessions. |
| **ADR** | Architecture decision record: one markdown file per non-trivial decision, at `.claude/decisions/NNNN-short-title.md`. Start one with `/li:adr-new`. A shape test enforces unique numbering. |
| **shape test** | A test asserting the repo's *structure* is still legal, rather than that one function works — every agent is categorised, every `workflow_root` skill declares navigation, the catalog regenerates clean. 36 of them, out of 90 tests total (36 shape, 48 unit, 4 integration, 1 behavior, 1 end-to-end). |
| **block hook vs warn hook** | Hooks declare a `tier:`. A **block hook** stops the action; there are exactly two, both firing at `git commit`/`push` — introduced secrets and customer data — each overridable with an explicit environment variable that is audit-logged. Everything else is a **warn hook**: it prints and gets out of the way. Hooks fire on **Claude Code only**; 9 of the 33 register automatically when the plugin installs. |
| **meta-infra** | Changes to the harness's own structure — `skills/`, `agents/`, `hooks/`, `lib/`, the frontmatter contracts. Held to a stricter discipline because they ripple into every downstream cycle: four extra gates, plus an entry in the evolution log under `.claude/engineering/evolution/`. See [meta-infra discipline](concepts/meta-infra-discipline.md). |
| **Gate M1–M4** | Those four extra gates. **M1** structure-impact entry at DEFINE, **M2** compatibility audit and **M3** the shape-test suite at REVIEW, **M4** future-operator clarity at CAPTURE. SHIP is blocked when M2 comes back red or M3 fails. |
| **the `.claude/` home** | Everything Lintel generates for a repo, under one root (ADR-0005). Durable knowledge you commit: `.claude/memory/` (lessons, working state, operator calibration), `.claude/decisions/`, `.claude/plans/`. Churn you do not: `.claude/runtime/` (cycle state, jobs, session saves, audit log), gitignored by default. Operator identity stays outside the repo, in `~/.lintel/profile.yaml`. |

---

Next: [getting started](getting-started.md) to install and run a first cycle, or the
[documentation index](README.md) for everything else.
