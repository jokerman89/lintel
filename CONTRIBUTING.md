# Contributing to Lintel

Lintel is in its **first public beta**. It is a company-neutral, pack-driven session harness for
agent-based development: markdown and bash that a modern AI CLI loads as a plugin. There is no
compiled artifact and no runtime service — the product is text that agents read plus shell scripts
that hooks run.

Beta means interfaces still move, and honest friction reports are the most valuable thing you can
send. Contributions that fix something real are very welcome. Speculative expansion is not.

## This repo is the tooling

Lintel ships `skills/`, `agents/`, `hooks/`, `packs/`, `lib/`, and `scaffolding/` as its product.
That is the opposite of a normal project repo — elsewhere agents and skills live user-global and
never inside a project. Here they are the deliverable.

The rule that governs all of it: **keep the spine company-neutral.** Identity — voice, compliance,
brand, roles — is resolved at runtime from the active pack via `resolve_pack_field`
(`lib/pack-resolver.sh`), never hardcoded into a skill, agent, or hook. Only the neutral `_default`
pack ships here; company identity installs as a separate pack.

## Before you contribute

- [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) — the canonical cross-CLI session ritual.
- [docs/architecture.md](docs/architecture.md) — spine and pack, the mechanical layer, where state lives.
- [docs/the-cycle.md](docs/the-cycle.md) — the nine phases, in depth.
- [scaffolding/01-foundation/CORE-PRINCIPLES.md](scaffolding/01-foundation/CORE-PRINCIPLES.md) — the load-bearing rules.
- [skills/CATALOG.md](skills/CATALOG.md) — all 125 skills, generated from frontmatter. Your idea may
  already exist, or be deliberately scoped out.

[docs/README.md](docs/README.md) indexes the rest of the published documentation.

## What is wanted during beta

Roughly in order of usefulness:

1. **Bug reports with a reproducer.** Which CLI, which skill or hook, what you ran, what happened.
   A failing shell command beats a paragraph.
2. **Reports of a skill or agent that reads well but does not work.** The surface is large — 125
   skills, 69 agents, 33 hooks — and prose drifting away from behavior is the failure mode this
   project is most exposed to. Finding one is a real contribution even without a fix.
3. **Documentation fixes.** Wrong paths, dead links, stale counts, instructions that do not survive
   a literal reading.
4. **Coverage reports for a CLI other than Claude Code.** Hooks fire on Claude Code only; everything
   else is markdown that other CLIs read to varying degrees. Tell us where the degradation is worse
   than [docs/multi-cli.md](docs/multi-cli.md) admits.
5. **A skill, agent, or hook that fills a genuine gap** — open an issue first, so we can agree the
   gap is real before you build.
6. **New CLI support**, following [adding a new CLI](docs/multi-cli.md#adding-a-new-cli).
7. **Subtraction.** Removing a skill, flag, or code path that nothing uses is a welcome change, with
   evidence that nothing uses it.

Naming a limitation is better than hiding it. An issue that says "this does not work and I do not
know why" is more useful than a fix that papers over it.

## How to propose a change

1. **Open an issue first** for anything non-trivial, so we can agree the change is wanted before you
   build it. Typo and dead-link fixes can go straight to a pull request.
2. **Branch from `main`:**
   ```bash
   git checkout -b feat/<short-name>
   ```
3. **Make the change.** Atomic — one logical change per branch.
4. **Run the tests** (below) and confirm they pass.
5. **Open a pull request against `main`** and fill in
   [the template](.github/PULL_REQUEST_TEMPLATE.md).

Participation is governed by the [code of conduct](CODE_OF_CONDUCT.md). Security issues do not go in
public issues — see [SECURITY.md](SECURITY.md).

## Running the tests

Everything runs through one entry point:

```bash
bash tests/runner/run-all.sh
```

Scope it while iterating:

```bash
bash tests/runner/run-all.sh --scope shape        # structural contracts
bash tests/runner/run-all.sh --scope unit         # unit
bash tests/runner/run-all.sh --scope integration  # cross-component
bash tests/runner/run-all.sh --scope e2e          # end to end
bash tests/runner/run-all.sh --tag claude-code-only
```

The four tiers, and what each is for:

| Tier | Count | What it asserts |
|---|---|---|
| `tests/shape/` | 36 | structural contracts — frontmatter completeness, path layout, generated files still regenerate clean, no non-English text on the shipped surface |
| `tests/unit/` | 48 | helpers in `lib/` and `bin/`, and per-skill logic |
| `tests/integration/` | 4 | cross-component behavior, such as a session actually leaving the traces it claims to |
| `tests/e2e/` | 1 | the harness critical path, end to end |

The runner is fail-closed: zero tests discovered, or a filter matching nothing, exits non-zero. A
green run has to assert something. Bash and `git` are the only hard requirements; a handful of tests
reach for `jq`, `node`, or `python3` and skip or degrade when those are absent, so install them
before trusting a local green.

One more check CI runs, worth running locally before you push:

```bash
bash install/verify.sh --all
```

New tests follow `tests/conventions/bash-test-template.sh`. Copy it, fill in the description, tags,
setup, run, and cleanup, then confirm the runner discovers it.

CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)) runs the `install/verify.sh` subcommands,
the unit tier on both Ubuntu and Windows, the shape tier, and the Claude-Code-tagged e2e tier. A
shellcheck job runs warn-only. The suite is noticeably slower on Windows under Git Bash than on
Linux — budget minutes, not seconds.

## Commit and pull request style

[Conventional Commits](https://www.conventionalcommits.org/), atomic, one logical change per commit:

```
feat(skills): add /<skill-name> for <use case>
fix(agents): correct <category>/<AgentName> frontmatter
docs(multi-cli): document Factory Droid install
chore(lib): tidy pack-resolver error message
```

Two hard rules on commit messages. Both are new for the public beta, neither is machine-enforced
yet, and existing history violates both in places:

- **English only.** No other language in subjects or bodies — the same rule the shipped tree is
  already tested for.
- **No AI-authorship trailers.** Do not add a `Co-Authored-By:` line for an assistant, or any other
  "generated by" attribution. Authorship of a contribution is yours; the tooling you used to write
  it is not a co-author.

On content, the English-only rule *is* enforced: `tests/shape/no-swedish.sh` fails CI on non-English
text anywhere in `skills/`, `agents/`, `hooks/`, `install/`, `.github/`, `seeds/`, `docs/`, or
`README.md`. Headings are sentence case — no title case, no all-caps.

## Record decisions

Any non-trivial decision gets an architecture decision record in
[.claude/decisions/](.claude/decisions/), numbered `NNNN-short-title.md`, from
[.claude/decisions/TEMPLATE.md](.claude/decisions/TEMPLATE.md). A structural change to `skills/`,
`agents/`, `hooks/`, or `lib/` also gets an entry under
[.claude/engineering/evolution/](.claude/engineering/evolution/) — see
[docs/concepts/meta-infra-discipline.md](docs/concepts/meta-infra-discipline.md). Capturing the
*why* is what keeps the harness coherent across contributors and sessions.

## Component contracts

Frontmatter is checked by `tests/shape/frontmatter-lint-all.sh`. Get it wrong and CI fails.

### A new skill

Lives at `skills/<kebab-case-name>/SKILL.md`. Copy the shape of an existing one —
`skills/qa/SKILL.md` is a good reference. Required frontmatter:

`name` (matches the directory), `layer`, `description`, `color`, `tools`, `voice`, `cli_support`.

Every skill shipped today is `layer: foundation`. `description` is the auto-invocation trigger, not
a summary: it must say *when* to reach for the skill, and must not carry version archaeology.
`tests/shape/skill-descriptions-trigger.sh` enforces that for the skills already migrated to trigger
form. See [docs/concepts/skill-protocol.md](docs/concepts/skill-protocol.md) and
[docs/concepts/prompt-house-style.md](docs/concepts/prompt-house-style.md).

Note that `scaffolding/01-foundation/TEMPLATE-skill.md` is the template Lintel installs into *other*
repos for user-global skills. It is not the shape for a skill contributed here.

### A new agent

Lives at `agents/<category>/<CamelCase>.md`, where the category is one of `communication`,
`compliance`, `customer`, `devops`, `doc-gen`, `engineering`, `frontend`, `security`. Required
frontmatter:

`name` (matches the filename), `category` (matches the directory), `description`, `color`, `tools`,
`voice`, `cli_support`.

`tier` is additionally required by `install/verify.sh --tier-stamps` for the `security`,
`compliance`, and `customer` categories; every agent shipped today declares `tier: permissive`.
Optional `memory:` (`project`, `user`, or `local`) and `model:` are validated when present. Give an
agent only the tools it actually needs.

### A new hook

Lives at `hooks/shared/<kebab-case>/HOOK.md` plus `hooks/shared/<kebab-case>/run.sh`. `HOOK.md`
declares at least `name`, `tier`, `event`, `fires_on`, `override`, and what breaks if the hook is
skipped.

Two things to know before writing one. **Hooks fire on Claude Code only** — every other CLI ignores
them, so a hook can never be the only thing between a user and a mistake. And of the 33 hook
directories here, 9 auto-register through `hooks/hooks.json` when the plugin is installed; the rest
are opt-in. Adding a directory does not make a hook fire.

Hooks run with the operator's privileges. Keep them minimal, fail open when expected state is
missing rather than blocking the session, and never write outside the repo's `.claude/runtime/` or
`~/.lintel/`.

## What is not accepted

- **Third-party code.** Lintel ships only original, MIT-licensed content. The installer does not
  clone, vendor, or update anything — `install/upstream-sources.yaml` is a declaration list that
  nothing acts on. Do not add code you did not write.
- **Company-specific identity in the spine.** Voice, compliance, and brand belong in a pack, not in
  `skills/`, `agents/`, or `hooks/`.
- **Internal jargon in user-facing text.** If a newcomer cannot decode it without reading this
  repo's history, rewrite it.
- **Speculative changes.** Solve a problem someone actually hit.
- **Stylistic refactors** with no behavior change, unless coordinated first.
- **Pull requests with the test suite red.**

## Lessons

When a pull request teaches something a future contributor should know, record it in
[.claude/memory/lessons.md](.claude/memory/lessons.md) as a rule that prevents the mistake
recurring. `bin/li-lessons-promote` lifts a repo-local lesson into the scaffolding baseline, so
every future scaffolded repo inherits it. (`bin/li-lessons-sync` is a different tool — it syncs one
operator's lessons across their own machines, and is not part of this workflow.)

## Questions

Open an issue. Be specific about the problem you are solving.
