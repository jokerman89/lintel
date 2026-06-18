# Contributing to Lintel

Thanks for considering a contribution. Lintel is a company-neutral, pack-driven session harness for
agent-based development — markdown + bash scaffolding that any modern AI CLI loads as a plugin. We keep
scope tight and quality high, but contributions that fill a genuine gap are very welcome.

## This repo IS the tooling

One thing to understand up front: Lintel is the tooling, so it ships `skills/`, `agents/`, `hooks/`,
`packs/`, `lib/`, and `scaffolding/` as its product. That is the opposite of a normal project repo —
elsewhere, agents and skills live user-global and never inside a project. Here they are the deliverable.
Keep the spine **company-neutral**: identity (voice, compliance, brand, roles) is resolved from the
active pack, never hardcoded into skills, agents, or hooks.

## Before you contribute

- Read [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) for the cross-CLI session-harness model.
- Read [docs/session-harness.md](docs/session-harness.md) for the architecture mental model.
- Skim [scaffolding/01-foundation/CORE-PRINCIPLES.md](scaffolding/01-foundation/CORE-PRINCIPLES.md) — the load-bearing rules.
- Check existing skills/agents (`/li:catalog` or `skills/CATALOG.md`) — your contribution may already exist, or be deliberately scoped out.

## How to propose a change

1. **Open an issue first** for anything non-trivial, so we can agree the change is wanted before you build it.
2. **Branch from `main`:**
   ```bash
   git checkout -b feat/<short-name>
   ```
3. **Make your change.** Atomic — one logical change per branch.
4. **Run the tests** (see below) and confirm they pass.
5. **Open a pull request against `main`** and fill in the PR template.

## Running the tests

The full suite runs through one entry point:

```bash
bash tests/runner/run-all.sh
```

You can scope it while iterating:

```bash
bash tests/runner/run-all.sh --scope shape   # structural contracts (incl. the English-only tripwire)
bash tests/runner/run-all.sh --scope unit     # unit tests
```

Everything must be **English only** — a shape test fails the build on non-English words.

## Commit style

Use [Conventional Commits](https://www.conventionalcommits.org/) — atomic, one logical change per commit:

```
feat(skills): add /<skill-name> for <use case>
fix(agents): correct <category>/<AgentName> frontmatter
docs(per-cli): add Cursor install guide
chore(lib): tidy pack-resolver error message
```

End each commit message with the `Co-Authored-By:` trailer if an AI assistant co-authored it.

## Record decisions (ADRs)

Any non-trivial decision gets an Architecture Decision Record at
[.claude/decisions/](.claude/decisions/), numbered `NNNN-short-title.md` from
[.claude/decisions/TEMPLATE.md](.claude/decisions/TEMPLATE.md). A structural change to
`skills/`/`agents/`/`hooks/`/`lib/` also gets an evolution-log entry under
[docs/v4.x/structure-changes/](docs/v4.x/structure-changes/). Capturing the *why* is the discipline
that keeps the harness coherent across contributors and sessions.

## Frontmatter contracts

These are enforced by shape/unit tests — get them right or CI fails.

### New skill

Each skill lives in `skills/<kebab-case-name>/SKILL.md`. Start from
[scaffolding/01-foundation/TEMPLATE-skill.md](scaffolding/01-foundation/TEMPLATE-skill.md).

Required frontmatter:
- `name` (matches the directory name)
- `layer` — the skill-layer contract
- `cli_support` — which CLIs the skill targets
- plus `description`, `color`, `tools`, `voice`

Body sections: What this skill does / When to use / When NOT to use / Workflow / Output format / Edge cases.

### New agent

Each agent lives in `agents/<category>/<CamelCase>.md`. Start from
[scaffolding/01-foundation/TEMPLATE-agent.md](scaffolding/01-foundation/TEMPLATE-agent.md).

Required frontmatter:
- `name` (CamelCase, matches the filename)
- `category` (matches the directory: engineering | security | compliance | devops | customer | communication | doc-gen | frontend)
- `tier` — the trust/permission tier
- `cli_support`
- plus `description`, `color`, `tools`, `voice`

### New hook

Each hook lives in `hooks/shared/<kebab-case>/HOOK.md` + `hooks/shared/<kebab-case>/run.sh`.
Hooks run with operator privileges — keep them minimal, side-effect-aware, and well-commented.

### New CLI plugin support

If adding support for a new AI CLI:
1. Add the per-CLI manifest in that CLI's expected format.
2. Add `docs/per-cli/<cli>.md` with an install guide.
3. Add a smoke checklist under `tests/e2e/<cli>-smoke.md`.

## What we accept

- Skills, agents, or hooks that fill a genuine gap.
- Bug fixes with a reproducer.
- Documentation improvements.
- New CLI plugin support (with a smoke test).

## What we don't accept

- **Third-party-code vendoring.** Lintel ships only original, MIT-licensed content.
- **Company-specific identity in the spine.** Voice, compliance, and brand belong in a pack, not in skills/agents/hooks.
- **Speculative changes.** Solve a real problem someone hit.
- **Stylistic refactors** without behavior change unless coordinated first.
- **PRs with the test suite red.**

## Lessons-learned mechanism

When a PR teaches something a future contributor should know, capture it in
[.claude/memory/lessons.md](.claude/memory/lessons.md) as a rule (`L-NNN`) that prevents the mistake
recurring. Use `bin/li-lessons-sync` to promote a repo-local lesson into the scaffolding baseline so
every future scaffolded repo inherits it.

## Questions

Open an issue. Be specific about the problem you're solving.
