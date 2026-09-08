# Documentation

Everything published about Lintel, arranged by what you are trying to do. If you are new, follow
the first section top to bottom — it is ordered.

Internal engineering artifacts — audits, gate records, superseded design docs — live under
`.claude/engineering/` and are deliberately not part of this surface.

---

## Start here

| Doc | What it gives you |
|---|---|
| [Getting started](getting-started.md) | Install the Copilot repository kit and finish one verified build card |
| [GitHub Copilot](copilot.md) | Native skills, custom agents, CLI plugin and cloud-agent boundaries |
| [Enterprise adoption](enterprise-adoption.md) | Pilot criteria, ownership, policy boundaries, upgrades and rollback |
| [Spec Kit](spec-kit.md) | Keep existing specifications and tasks authoritative while adding session continuity |
| [Glossary](GLOSSARY.md) | One screen. Pack, spine, cycle, trio, depth schema — the terms you meet before they are defined |
| [FAQ](faq.md) | Short answers, with links into the deeper pages |

---

## Understand the system

| Doc | What it covers |
|---|---|
| [The cycle](the-cycle.md) | The nine phases, phase by phase: what each does, what it produces, where the gates are, what skipping it costs |
| [Architecture](architecture.md) | Spine and pack, the mechanical layer, navigation, depth modules, where state lives, tests as structural guarantee |
| [Multi-CLI support](multi-cli.md) | One instruction source, per-CLI manifests, and exactly what degrades where |
| [Precedence](precedence.md) | Which agent gets picked, and which instruction file wins when two disagree |
| [Compliance](compliance.md) | The neutral baseline, and what an installed pack can add on top |

---

## Concepts

Deeper treatment of individual mechanisms. Read on demand rather than in order.

**The workflow**
- [Skill protocol](concepts/skill-protocol.md) — the contract every skill declares
- [Orientator](concepts/orientator.md) — how SENSE picks a workflow
- [Planner as module](concepts/planner-as-module.md) — planning as a composable capability
- [Brief forge](concepts/brief-forge.md) · [Envelope](concepts/envelope.md) — the hand-off gate and its schema
- [Jobs system](concepts/jobs-system.md) — tracking work that outlives one session
- [Agent dispatch rules](concepts/agent-dispatch-rules.md) — when to spawn a subagent and when not to
- [Agent memory](concepts/agent-memory.md) — what a subagent is allowed to remember

**Identity and packs**
- [Pack resolver](concepts/pack-resolver.md) — how `resolve_pack_field` finds a value
- [Pack inheritance](concepts/pack-inheritance.md) — `extends:`, and why merging is block-replace
- [Pack defaults](concepts/pack-defaults.md) — what the neutral baseline sets

**Engineering depth**
- [Engineering modules](concepts/engineering-modules.md) — the shared shape of all five
- [TA — tech architecture](concepts/ta-module.md) · [DA — data](concepts/da-module.md) · [SC — security](concepts/sc-module.md) · [DH — devops](concepts/dh-module.md) · [TQ — testing](concepts/tq-module.md)
- [Full engineering pass](concepts/full-engineering-pass.md) — composing all five in dependency order

**Memory and continuity**
- [Memory v2](concepts/memory-v2.md) — memory as commands, not conventions
- [Obsidian integration](concepts/obsidian-integration.md) · [Capture vault sink](concepts/capture-vault-sink.md)

**Keeping the harness honest**
- [Meta-infra discipline](concepts/meta-infra-discipline.md) — gates M1–M4 for changes to Lintel itself
- [Uniformity contract](concepts/uniformity-contract.md) — the small enforced floor and the tracked tail
- [Prompt house style](concepts/prompt-house-style.md) — how skill and agent descriptions are written
- [Wiki generation](concepts/wiki-generation.md) — what is generated and what is hand-written

---

## Use it deeply

| Doc | What it covers |
|---|---|
| [Power user](power-user.md) | Context warming, roles, jobs, budgets, checkpoints |
| [Skill catalog](../skills/CATALOG.md) | Canonical skills with their triggers — generated from frontmatter |
| [Agents](wiki/agents.md) · [Skills](wiki/skills.md) · [Packs](wiki/packs.md) · [Schemas](wiki/schemas.md) | Generated reference |
| [Showcase](showcase/README.md) | A single-file HTML system map you can open in a browser |

---

## Operate and upgrade

| Doc | What it covers |
|---|---|
| [Migrations](migrations/_INDEX.md) | Every migration a Lintel upgrade may ask you to run |
| [Ship gate](../.claude/engineering/SHIP-GATE.md) | The readiness gates a release passes |
| [Changelog](../CHANGELOG.md) | Release notes |

---

## Contribute

| Doc | What it covers |
|---|---|
| [Contributing](../CONTRIBUTING.md) | Branch, commit and review conventions |
| [Code of conduct](../CODE_OF_CONDUCT.md) | Expected behaviour |
| [Security](../SECURITY.md) | How to report a vulnerability |

---

## Where the rest lives

| Location | Holds |
|---|---|
| `.claude/decisions/` | Decision records. One per non-trivial decision, numbered and unique — a shape test enforces both |
| `.claude/memory/` | Lessons, working state, operator calibration |
| `.claude/engineering/` | Internal engineering artifacts: audits, Gate M1 evolution log, Gate M2 compatibility audits, superseded design docs |
| `AGENT-INSTRUCTIONS.md` | The canonical cross-CLI session ritual — the file every CLI's root entry points at |
| `CLAUDE.md` | This repo's own instruction file, and the instantiated form of the template Lintel scaffolds elsewhere |
