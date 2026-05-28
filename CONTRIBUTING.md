# Contributing to Lintel

Thanks for considering a contribution. Lintel is curated tooling for Microsoft Sweden CAIP-SE — we keep scope tight and quality high.

## Before you contribute

- **Read [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md)** for the session-harness model Lintel follows.
- **Read [docs/session-harness.md](docs/session-harness.md)** for the architecture mental model.
- **Read [docs/design/lintel-v3-plan.md](docs/design/lintel-v3-plan.md)** for the current architecture phase.
- **Check existing skills/agents** — your contribution may already exist (or be deliberately scoped out).

## Contribution types

### New skill

Each skill lives in `skills/<kebab-case-name>/SKILL.md`. Use [scaffolding/01-foundation/TEMPLATE-skill.md](scaffolding/01-foundation/TEMPLATE-skill.md) as starting point.

Frontmatter must include:
- `name` (matches dir name, prefix `li-` for namespacing)
- `layer` (foundation | ms-team)
- `description` (one-line for discoverability)
- `color`, `tools`, `voice`, `cli_support`

Skill body sections: What this skill does / When to use / When NOT to use / Workflow / Output format / Edge cases.

### New agent

Each agent lives in `agents/<category>/<CamelCase>.md`. Use [scaffolding/01-foundation/TEMPLATE-agent.md](scaffolding/01-foundation/TEMPLATE-agent.md).

Frontmatter must include:
- `name` (CamelCase, matches filename)
- `category` (matches dir: ms-specific | engineering | security | compliance | devops | customer | communication | voice | doc-gen)
- `description`, `color`, `tools`, `voice`, `cli_support`, `tier`

### New hook

Each hook lives in `hooks/shared/<kebab-case>/HOOK.md` + `hooks/shared/<kebab-case>/run.sh`. Hooks are opt-in via symlinks operators activate per-machine.

### New compliance rule

Goes into `scaffolding/02-sdl/`. Coordinate with @jokerman89 — compliance changes require legal review for customer-facing engagements.

### New language/CLI plugin

If adding support for a new AI CLI:
1. Create `<.cli-name-plugin>/plugin.json` (or per-CLI's manifest format)
2. Add `docs/per-cli/<cli>.md` with install guide
3. Update README "Multi-CLI support" table
4. Add `tests/e2e/<cli>-smoke.md` (operator checklist)

## Pull request process

1. **Branch from `main` (or `v3-dev` during v3 development)**:
   ```bash
   git checkout -b feat/<short-name>
   ```

2. **Make your change**. Atomic — one logical change per PR.

3. **Verify locally**:
   ```bash
   bash install/verify.sh --all
   bash tests/runner/run-all.sh
   ```

4. **Commit using Conventional Commits**:
   ```
   feat(skills): add /<skill-name> for <use case>
   fix(agents): correct <CategoryName>/<AgentName> frontmatter
   docs(per-cli): add Cursor install guide
   chore(deps): bump <pkg> to <version>
   ```

5. **Open PR against `main`** (or `v3-dev`). Fill PR template completely.

## What we accept

- **Skills/agents that fill genuine gaps** in MS-CAIP-SE workflows
- **Bug fixes** with reproducer
- **Documentation improvements**
- **New CLI plugin support** (with smoke test)
- **Compliance refinements** with explicit rationale

## What we don't accept

- **Third-party-code vendoring.** Lintel ships only operator-authored content.
- **Speculative changes.** Solve a real problem someone hit.
- **Stylistic refactors** without behavior change unless coordinated.
- **PRs without local verify pass.**
- **Customer-specific content.** That belongs in customer engagement repos, not here.

## Lessons-learned mechanism

When a PR is merged that includes a lesson-learned (something a future contributor should know), update `scaffolding/01-foundation/tasks/lessons.md`. This file travels into every scaffolded repo as baseline.

Use `bin/li-lessons-promote` to interactively promote a lesson from a customer repo to the Lintel global lessons file.

## Questions

Open an issue. Tag @jokerman89. Be specific about the problem you're solving.
