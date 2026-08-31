# Lintel

**A session harness for AI coding agents.** Markdown and bash — no runtime, no daemon, nothing to
run. Your CLI executes; Lintel supplies the discipline: a nine-phase development cycle with real
gates, memory that survives a context wipe, safety hooks that block rather than warn, and identity
that plugs in as a swappable **pack**.

> **Status: v0.9.0-beta.** The harness has been in daily use on its own repo since v1 — every
> feature below is dogfooded here before it ships. Beta means the surface is stable and tested
> (90 tests, CI on Ubuntu and Windows) but the public API is not yet frozen. Feedback wanted.

```
125 skills · 69 agents · 33 hooks · 1 neutral pack · 8 CLIs · 90 tests
```

---

## The problem

An AI coding session has no spine. The agent starts strong, drifts, and three compactions later has
forgotten why the design was chosen. Nothing records the decision. Nothing notices that the plan was
never reviewed. Nothing stops an auto-mode run from walking through a one-way door. The next session
starts from zero and re-derives everything — badly.

Lintel is the harness around that session. It does not replace your agent; it gives the agent a
structure to work inside, a place to put what it learns, and gates it cannot silently skip.

---

## Quick start

**1. Install for your CLI**

```
Claude Code         /plugin marketplace add jokerman89/lintel
                    /plugin install li@jokerman-lintel
Codex CLI / App     /plugins, search lintel, Install
Cursor              /add-plugin lintel
Gemini CLI          gemini extensions install https://github.com/jokerman89/lintel
GitHub Copilot CLI  copilot plugin marketplace add jokerman89/lintel
                    copilot plugin install li@jokerman-lintel
Factory Droid       droid plugin marketplace add jokerman89/lintel
                    droid plugin install li@jokerman-lintel
OpenCode            fetch and follow .opencode/INSTALL.md
```

**2. Run `/li:welcome`**

It detects your CLI, tells you honestly what works and what does not on that CLI, runs one cycle in
dry-run so you feel the discipline without mutating anything, and demonstrates a safety hook firing.
Five minutes, no commitment.

**3. Do real work with `/li:cycle`**

That is the whole onboarding. Everything below explains what you just used.

Full walkthrough: **[docs/getting-started.md](docs/getting-started.md)**. New to the vocabulary?
**[docs/GLOSSARY.md](docs/GLOSSARY.md)**.

---

## The cycle

The centrepiece. Nine phases, each its own skill, each with a declared gate and a declared cost of
being skipped:

```
SENSE → SCOPE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE
```

| Phase | What it does | Produces | What skipping it costs you |
|---|---|---|---|
| **SENSE** | Silent one-screen diagnostic: intent, active pack and compliance mode, active role, prior cycle state, context budget | SENSE report + scale pre-read | every downstream phase is mis-scoped |
| **SCOPE** | Sizes and disambiguates the request. Fires **at most one** clarifying question, and only when the request is genuinely bimodal | `scope.md` — size, depth schema, chosen reading | scale ambiguity is never resolved; PLAN picks the wrong template |
| **DEFINE** | Forcing questions. Locks premises, forces alternatives, picks the wedge. Hard gate until you approve | approved design doc | PLAN and BUILD consume ad-hoc prose with nothing locked |
| **DISCOVER** | Read-only map of the codebase, prior ADRs, past lessons, and reusable skills and agents touching the wedge | `discover-report.md` | the work reinvents or contradicts decisions already made |
| **PLAN** | Cold-executor trio born together (`plan.md`, `spec.md`, `prompt.md`), five-minute task granularity, cost estimate, **mandatory approval gate** | the trio + a token estimate | BUILD runs against an unwritten, unreviewed plan |
| **BUILD** | One fresh subagent per task, two-stage review each: spec compliance, then quality | code, atomic commits | no implementation is produced |
| **REVIEW** | Adversarial three-stage: spec compliance, code quality, pack compliance. A P1 finding blocks SHIP | review + compliance reports | unreviewed code reaches SHIP with no signal |
| **SHIP** | PR by default. Final compliance hard-stops, voice gates, CI validation, audit record | PR, release notes, audit log | no deploy validation, no rollback path, no audit trail |
| **CAPTURE** | Durable close: lessons, an ADR for any non-trivial decision, evolution-log entry, working-state update | lessons, ADR, log entries | the next session re-derives everything from scratch |

Not every job needs all nine. Mode presets pick the subset: `hotfix` runs SENSE → BUILD → REVIEW →
SHIP; `research-dive` stops after DISCOVER; `meta-infra` runs everything and activates four extra
gates for changes to the harness itself.

```
/li:cycle                    full pipeline
/li:cycle --mode hotfix      known bug, fix path clear
/li:cycle --from PLAN        hop in — dependencies are verified first
/li:cycle --dry-run          show the plan and its cost, execute nothing
/li:resume                   pick up where the last session stopped
```

### Why this is not just a checklist

Because the position is **mechanical**, not remembered. Every phase appends to a state ledger, and
three hooks read it:

- **`session-digest`** (SessionStart) injects the active pack, recent lessons, open jobs and recent
  decision records into a fresh session — so session two knows what session one learned.
- **`cycle-position-inject`** (UserPromptSubmit) re-asserts your position at the *start* of every
  turn: which phase is done, which is next.
- **`cycle-incomplete-warn`** (Stop) fires when a turn ends mid-cycle, so work never goes quiet
  without telling you where it stopped.

The result is a footer you always get, wherever you entered the cycle:

```
Lintel cycle · mode meta-infra · done ✅ · skipped ⊘ · here 📍 · pending ▢

SENSE ✅ → SCOPE ✅ → DEFINE ✅ → DISCOVER ✅ → PLAN 📍 → BUILD ▢ → REVIEW ▢ → SHIP ▢ → CAPTURE ▢

▶ Awaiting your answer: Proceed with BUILD? [Y/n/edit-plan]
```

Deeper: **[docs/the-cycle.md](docs/the-cycle.md)**.

---

## Mechanical, not aspirational

The rule the repo holds itself to: *if a guarantee is only prose, it is not a guarantee.* A few
worth knowing about:

| Guarantee | How it is actually enforced |
|---|---|
| Auto-mode never decides a one-way door | `lib/auto-decide.sh` — a deliberately broad keyword guard over the irreversible classes: delete, drop, migrate, schema change, production, force-push, secret, rename a skill or agent, breaking change. A false positive only means "ask the operator"; a false negative is the failure being guarded, so the set errs wide. |
| Secrets and customer data never reach a commit | `secret-scan-block` and `customer-data-block` **block** at `git commit` and `git push`. They scan added lines only and follow `git -C` targets. Overriding one is possible and always audit-logged — the record captures the reason you give, or `no-reason-given` if you give none. |
| The capability table cannot drift from reality | `lib/cli-tiers.yaml` is the single source; the table below is generated from it, and `tests/shape/cli-tiers-sync.sh` fails the build if the two disagree. |
| Memory is code, not an obligation | `lib/memory.sh`, `lib/state.sh`, `lib/paths.sh` — one command per operation. A phase writes `state_append PHASE DONE`; it does not perform a YAML ritual it might forget. |
| Structure cannot silently rot | 36 shape tests assert structural contracts: frontmatter fields, hook registration, path canonicality, decision-record number uniqueness, no non-English text in the public tree. |

Nine hooks auto-register on a plugin install across five events — zero setup. On a bare install
they ship inert until you arm them; Lintel never edits your `settings.json` behind your back.
**Hooks are a Claude Code mechanism** — see the honest table below.

---

## Identity is a pack, not a hardcode

The spine is company-neutral. Voice, compliance posture, personas, brand, roles and navigation
policy are **not** written into the skills — they resolve at runtime from the active pack through a
single accessor, `resolve_pack_field <dotted.path>` (`lib/pack-resolver.sh`).

Lintel ships exactly one pack: `_default`, which enforces nothing. A company pack declares only what
it changes and inherits the rest through `extends:`, with cycle detection and a loud failure if the
neutral baseline itself is broken. Build your own with `/li:pack-create`.

This is what makes the harness publishable: the company identity that used to be hardcoded was
extracted wholesale into an external pack. Nothing company-specific remains in the spine, and a
shape test keeps it that way.

---

## Engineering depth on demand

Five composable domain modules, each an orchestrator plus sub-skills plus its own agent fleet:

| Module | Domain | Reach for it when |
|---|---|---|
| **`/li:ta`** | tech architecture | quality attributes, boundary review, scaling plan |
| **`/li:da`** | data architecture | schema design, migrations, sharding, retention, analytics readiness |
| **`/li:sc`** | security and compliance | threat model, auth review, compliance evidence |
| **`/li:dh`** | devops and hosting | deployment plan, rollback, observability, SLI/SLO, capacity, cost |
| **`/li:tq`** | testing and quality | contract tests, perf budgets, coverage strategy |

Each runs full, in a loop, or as a single capability. `/li:full-engineering-pass` composes all five
in dependency order for a release or an engagement that needs the whole picture at once.

---

## The factory

Lintel installs its own disciplines into *other* repos:

```
cd ~/new-repo
li-scaffold init --mode internal-tool --pack _default
```

Thirty seconds later that repo has a `CLAUDE.md`, `CORE-PRINCIPLES.md`, and a `.claude/` home with
memory (lessons, working-state, personas), plans, and decision-record templates.

Lintel dogfoods this: **this repo's own `CLAUDE.md` is the instantiated form of the template it
ships.**

---

## Multi-CLI support — the honest table

Full on three CLIs, supported on four, best-effort elsewhere. The **enforcement hooks fire only on
Claude Code**; every other CLI still gets the skills, the cycle discipline and the pack-driven
knowledge, just not the live gate. This table is generated from `lib/cli-tiers.yaml` and shape-tested
against it, so it cannot drift.

<!-- CLI-TIERS:START — generated from lib/cli-tiers.yaml via cli_tiers_markdown_table; do not hand-edit. -->
| CLI | Tier | Skills | Subagents | Hooks |
|---|---|---|---|---|
| Claude Code | full | native | native | yes |
| Codex CLI / App | full | native | native | no (Claude Code only) |
| Cursor | full | native | sequenced | no (Claude Code only) |
| Gemini CLI | supported | manual | none | no (Claude Code only) |
| OpenCode | supported | manual | none | no (Claude Code only) |
| GitHub Copilot CLI | supported | native | none | no (Claude Code only) |
| Factory Droid | supported | native | none | no (Claude Code only) |
| Cline / Continue / Aider | best-effort | manual | none | no (Claude Code only) |
<!-- CLI-TIERS:END -->

---

## Where things live

Four roots — two machine-global, two in your repo:

| Root | Scope | Holds |
|---|---|---|
| `~/.lintel/` | machine-global | operator identity — active pack, mode and role, installed packs, cross-repo job registry, audit log |
| `~/.claude/` | machine-global | your CLI's own home — `settings.json`, and any hooks you armed by hand on a bare install |
| `<repo>/.claude/` | per-repo, **committed** | knowledge that travels with the code — `memory/`, `decisions/`, `plans/` |
| `<repo>/.claude/runtime/` | per-repo, **gitignored** | churn that should not — cycle state, job data, session saves, event log |

The committed/gitignored split is deliberate: knowledge is reviewed in pull requests, runtime noise
stays local.

---

## What you do not get

Stated plainly, because a launch page that hides its gaps is worth less than one that names them:

- **Hooks on every CLI.** Enforcement is a Claude Code mechanism. Elsewhere the hooks do not fire.
- **`/li:generate-pdf`, `/li:generate-xlsx`, `/li:generate-visio`** are self-labelled template-only
  slots — structure without curated content.
- **No runtime.** Markdown and bash. Your CLI is the execution engine.
- **No bundled third-party code.** Lintel ships only operator-authored content.
- **No customer data, ever.** This is tooling; customer artifacts never land here.

---

## Documentation

**Start here**
- [Getting started](docs/getting-started.md) — install, first cycle, where files land
- [Glossary](docs/GLOSSARY.md) — pack, spine, cycle, trio, the load-bearing terms
- [FAQ](docs/faq.md)

**Understand it**
- [The cycle](docs/the-cycle.md) — nine phases, gate by gate
- [Architecture](docs/architecture.md) — spine, packs, navigation, depth
- [Multi-CLI support](docs/multi-cli.md) — what degrades where, and why
- [Precedence](docs/precedence.md) — which instruction file wins when they conflict

**Use it deeply**
- [Power user](docs/power-user.md) — context warming, roles, jobs, budgets
- [Engineering modules](docs/concepts/engineering-modules.md) — TA, DA, SC, DH, TQ
- [Pack resolution](docs/concepts/pack-resolver.md) — resolution, inheritance, defaults
- [Compliance](docs/compliance.md) — the neutral baseline and what a pack can add
- [Skill catalog](skills/CATALOG.md) — all 125 skills, auto-generated

**Contribute**
- [Contributing](CONTRIBUTING.md) · [Code of conduct](CODE_OF_CONDUCT.md) · [Security](SECURITY.md)
- [Changelog](CHANGELOG.md)

Full index: **[docs/README.md](docs/README.md)**.

---

## License

MIT — see [LICENSE](LICENSE). Lintel ships only operator-authored content; nothing is vendored.

## Security

See [SECURITY.md](SECURITY.md) for the disclosure process.
