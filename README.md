# Lintel

**A shared session workflow for teams building with GitHub Copilot.** Turn an issue into a
reviewed plan, small build cards, verified changes and a handoff the next session can use.
Your team's decisions, lessons and working agreements stay in the repository.

Lintel combines repository instructions, native agent skills, specialist agents and reusable
company packs. Start with Copilot in VS Code, Copilot CLI or a GitHub cloud agent; keep the
same engineering workflow when teammates use Claude Code or Codex.

> **Public beta: 0.9.0.** Interfaces may change before 1.0. Repository installation and structural
> contracts are tested; an enterprise rollout still needs a pilot on your approved Copilot
> client and policies. See the [adoption guide](docs/enterprise-adoption.md) for acceptance criteria.

[Get started](docs/getting-started.md) · [GitHub Copilot guide](docs/copilot.md) ·
[Enterprise adoption](docs/enterprise-adoption.md) · [Use with Spec Kit](docs/spec-kit.md)

## Give your team a repeatable session

A productive first session should leave useful work behind for the next developer. Lintel gives
that work a shared shape:

| Your team needs | Lintel provides |
|---|---|
| A consistent starting point | Repository instructions and skills that load the relevant workflow |
| Clear scope before implementation | A specification, implementation plan and build cards with acceptance criteria |
| Reviewable delivery | A review against the specification, quality checks and a documented release decision |
| Continuity across sessions | Committed lessons, architecture decisions and a current working state |
| Organisation-specific standards | A separate pack for policies, terminology, roles and reusable context |
| Existing investment to carry forward | A workflow bridge for Spec Kit and shared source content for other agent clients |

There is no hosted Lintel service or background daemon. Markdown defines the workflow; local
Bash and Python utilities handle installation and validation. Your agent client executes work
under its existing permissions.

## Start with GitHub Copilot

Install the repository kit into a pilot repository. It is self-contained, reviewable in a pull
request, and usable by teammates without a global Lintel installation.

```bash
git clone https://github.com/jokerman89/lintel.git
cd lintel
bash bin/li-copilot init --target ../your-repo
bash bin/li-copilot check --target ../your-repo
```

Use Bash, Git and Python 3.9+. On Windows, run the same commands in Git Bash. For an enterprise
pilot, check out an approved tag or commit before installation and record it in the adoption PR.
The target must be your intended project directory.

Open the target repository in your Copilot client, enable its repository customizations, and run:

```text
/li-welcome
/li-plan Add a health endpoint with a focused acceptance test.
```

Review the generated plan, then ask Copilot to execute its build cards. If the client does not
list a skill, ask it to read `.github/skills/li-plan/SKILL.md` directly. The full
[walkthrough](docs/getting-started.md) covers installation, the first build and resuming work.

Already use the Copilot CLI plugin manager? The [Copilot guide](docs/copilot.md#copilot-cli-plugin)
provides the plugin path. Claude Code's existing installation is in
[multi-CLI support](docs/multi-cli.md#claude-code).

## One workflow, sized to the task

```text
SENSE → SCOPE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE
```

Understand the request, choose the scope, define success, inspect the code, plan the work,
build it, review the result, ship within the authorized scope, and capture what was learned.
Small fixes can use a shorter route. A larger change can span multiple sessions and build cards.

The portable Copilot kit exposes this workflow as `/li-cycle`, `/li-plan`, `/li-build`,
`/li-review` and related skills. Its planner, builder and reviewer profiles help separate
implementation from independent review. The full catalog contains architecture, data,
security, operations, testing, design and document workflows; load that depth when it helps.

These are agent instructions backed by local helpers. Workflow approvals and review discipline
still depend on the agent following the instructions and the team enforcing its merge rules.
[The cycle](docs/the-cycle.md) explains the phases and their artifacts.

## Make it your organisation's workflow

A pack contains the standards your organisation owns: policy references, voice, roles and
context. The core stays company-neutral, so teams can evolve their pack without forking Lintel.
The included `_default` pack starts with advisory settings and no company-specific gates.

Start with one repository and one well-defined change. Choose a platform owner, keep pack
changes reviewable, measure first-session success and resumption quality, then expand after
review. [Enterprise adoption](docs/enterprise-adoption.md) includes a pilot checklist, an
ownership model, upgrade and rollback guidance, and the evidence to collect.

Spec Kit can remain the source for your constitution, specification, implementation plan and
task list. Lintel adds session continuity, execution and review around those artifacts;
[the integration guide](docs/spec-kit.md) defines how to avoid duplicate plans.

## Know which controls you have

| Layer | What it does | Boundary |
|---|---|---|
| Repository instructions and skills | Guide planning, implementation, review and handoff | Cooperative agent behavior |
| Local helpers and tests | Validate structure, installation state and selected behavior | Only the paths and assertions they check |
| Lintel's Claude Code hooks | Scan selected agent tool calls and surface session state | Claude Code activation; pattern checks can miss data and be overridden |
| Your GitHub policies and CI | Control reviews, checks, access and release permissions | Configure and verify in your organisation |

GitHub Copilot supports its own hooks, but Lintel's Claude Code hook bundle is **not installed
or adapted by the Copilot kit**. Lintel is not a compliance certification, data-loss-prevention
system or substitute for repository protection. [Security](SECURITY.md) and
[compliance](docs/compliance.md) explain what is implemented and what remains your responsibility.

## Multi-CLI support

This table describes the Lintel integration shipped in this repository. Host capabilities can be
broader; a declared integration is not proof of a live session on every client version.
The table is generated from `lib/cli-tiers.yaml` and checked for drift.

<!-- CLI-TIERS:START — generated from lib/cli-tiers.yaml via cli_tiers_markdown_table; do not hand-edit. -->
| CLI | Tier | Skills | Subagents | Lintel hooks |
|---|---|---|---|---|
| Claude Code | full | native | native | yes |
| Codex CLI / App | full | native | native | not ported |
| Cursor | full | native | sequenced | not ported |
| Gemini CLI | supported | manual | none | not ported |
| OpenCode | supported | manual | none | not ported |
| GitHub Copilot CLI | supported | native | native | not ported |
| Factory Droid | supported | native | none | not ported |
| Cline / Continue / Aider | best-effort | manual | none | not ported |
<!-- CLI-TIERS:END -->

See [multi-CLI support](docs/multi-cli.md) for invocation differences and activation boundaries.
The portable Copilot kit uses `/li-<skill>` names; legacy plugin workflows use the naming
provided by their host.

## Explore and contribute

- [Documentation index](docs/README.md) · [FAQ](docs/faq.md) · [Glossary](docs/GLOSSARY.md)
- [Architecture](docs/architecture.md) · [Engineering modules](docs/concepts/engineering-modules.md)
- [Skill catalog](skills/CATALOG.md) · [Pack resolution](docs/concepts/pack-resolver.md)
- [Contributing](CONTRIBUTING.md) · [Code of conduct](CODE_OF_CONDUCT.md) · [Changelog](CHANGELOG.md)

Bug reports from real Copilot sessions are especially useful: include the client version,
installation route, task, expected behavior and a sanitized reproduction.

MIT for Lintel's original code; see [LICENSE](LICENSE). Bundled design resources retain their
[third-party attribution and licenses](skills/design-dna/ATTRIBUTION.md).
