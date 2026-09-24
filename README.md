# Lintel

[Presentation, demos & technical reference](https://jokerman89.github.io/lintel/) · [Presentation source](presentations/tech-shots-2026-09-25/README.md)

**A shared engineering workflow across coding agents.** Turn an issue into a
reviewed plan, small build cards, verified changes and a handoff the next session can use.
Your team's decisions, lessons and working agreements stay in the repository.

Lintel combines repository instructions, canonical skills, specialist methods and reusable
company packs. Start with the task, not a client: preserve its requirements, acceptance,
review evidence and next action when work moves between CLI, desktop, IDE and cloud sessions.
Native adapters expose documented discovery formats; explicit file handoff remains useful
where native integration is unverified.

> **Public beta.** Interfaces may change before 1.0. Repository installation and structural
> contracts are tested; an enterprise rollout still needs a pilot on each intended
> client surface and policy configuration. See the [adoption guide](docs/enterprise-adoption.md).

[Get started](docs/getting-started.md) · [Client adapters](docs/client-adapters.md) ·
[GitHub Copilot](docs/copilot.md) · [Claude Code](docs/claude-code.md) ·
[Enterprise adoption](docs/enterprise-adoption.md) · [Swarming work](docs/concepts/swarming-work.md) ·
[Use with Spec Kit](docs/spec-kit.md)

## Give your team a repeatable session

A productive first session should leave useful work behind for the next developer. Lintel gives
that work a shared shape:

| Your team needs | Lintel provides |
|---|---|
| A consistent starting point | Repository instructions and skills that load the relevant workflow |
| Clear scope before implementation | A specification, implementation plan and build cards with acceptance criteria |
| Reviewable delivery | A review against the specification, quality checks and a documented release decision |
| Safe multi-agent scale | An opt-in swarm profile with bounded ownership, attributable changes, lane evidence and serial fallback |
| Continuity across sessions | Committed lessons, architecture decisions and a current working state |
| Organisation-specific standards | A separate pack for policies, terminology, roles and reusable context |
| Existing investment to carry forward | A workflow bridge for Spec Kit and shared source content for other agent clients |

There is no hosted Lintel service or background daemon. Markdown defines the workflow; local
Bash and Python utilities handle installation and validation. Your agent client executes work
under its existing permissions.

## Start with one useful task

Choose a small fix, a review, an investigation or a bounded feature in a pilot repository.
Define the expected result and its verification before implementation. Existing Spec Kit or
other specifications remain authoritative; Lintel does not require a competing backlog.

Use a reviewed Lintel checkout and select the [adapter](docs/client-adapters.md) for the
exact surface your team uses. A repository-only manual route is available on every host:

```bash
git clone https://github.com/jokerman89/lintel.git
cd lintel
python3 bin/li-adapter.py init --client other --target ../your-repo
python3 bin/li-adapter.py check --target ../your-repo
```

Replace `other` with an exact registered surface for native-format discovery files where
documented. `other` installs a usable canonical-file handoff, not a native plugin.
Use Python 3.9+ (`python` on Windows when that is your Python 3 command), Git and Bash for
shell workflows. For an enterprise
pilot, check out an approved tag or commit before installation and record it in the adoption PR.
The target must be your intended project directory.

Open the target repository in your approved client and inspect its actual discovery. If no
skill is visible, ask it to read the manual entry:

```text
Read .github/lintel/START.md. Plan a health endpoint with a focused acceptance test.
Inspect existing routes and conventions. Do not implement until the plan is authorized.
```

Review the plan, then execute authorized build cards and obtain a separate review. Missing
delegation does not mean lost functionality: use serial work and an external review handoff.
Do not claim independent review by switching roles in the same conversation. The full
[walkthrough](docs/getting-started.md) covers installation, the first build and resuming work.

Existing routes remain: the [Copilot repository kit and CLI plugin](docs/copilot.md),
[Claude skills, agents and optional hooks](docs/claude-code.md), and the other
[client-specific paths](docs/client-adapters.md). No personal installation is needed for
the portable repository kit.

## One workflow, sized to the task

```text
SENSE → SCOPE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE
```

Understand the request, choose the scope, define success, inspect the code, plan the work,
build it, review the result, ship within the authorized scope, and capture what was learned.
Small fixes can use a shorter route. A larger change can span multiple sessions and build cards.

Portable native wrappers expose `li-cycle`, `li-plan`, `li-build`, `li-review` and related
skills; invocation follows the host, not a universal slash spelling. Copilot's native
planner, builder and reviewer profiles remain available. The full catalog contains architecture, data,
security, operations, testing, design and document workflows; load that depth when it helps.

These are agent instructions backed by local helpers. Workflow approvals and review discipline
still depend on the agent following the instructions and the team enforcing its merge rules.
[The cycle](docs/the-cycle.md) explains the phases and their artifacts.

## Scale an approved plan with a swarm

When a reviewed plan contains dependency-independent ownership domains, opt in with `/li:swarm`.
Lintel adds a committed coordination map, charter and per-lane briefs, reports and reviews beside the
existing task map. One coordinator owns shared state, generated outputs, commits and integration.

Native-subagent hosts may fan out writers only when paths do not overlap and every change is
attributable through an isolated worktree, patch or equivalent scoped sandbox. Sequenced hosts run
the same briefs one at a time. Hosts without subagents use the main agent or export replayable briefs
and do not claim independent review. The final REVIEW always runs on the reconciled branch.

The [swarming guide](docs/concepts/swarming-work.md) covers when to select the profile, how to inspect
ownership and status, failure recovery, trusted tool sources and the close gate.

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

The canonical registry distinguishes vendor documentation, delivered discovery/binding and
observed execution per operation and surface. A CLI record never proves desktop, IDE or cloud
parity. The generated view below comes from `lib/cli-tiers.yaml`; use
`python3 bin/li-client-capabilities.py show --client <surface>` for dated sources, conditions
and observation details. Static compatibility tiers are conservative hints, not runtime grants.

<!-- CLI-TIERS:START — generated from lib/cli-tiers.yaml via cli_tiers_markdown_table; do not hand-edit. -->
| Surface | Delivered discovery route | Vendor delegation | Live Lintel evidence |
|---|---|---|---|
| Claude Code CLI | .claude/skills | documented | not_run |
| Claude Desktop Code local | .claude/skills | unknown | not_run |
| GitHub Copilot CLI | .github/skills | documented | not_run |
| GitHub Copilot App | .github/skills | conditional | partial session observations |
| GitHub Copilot VS Code | .github/skills | conditional | not_run |
| GitHub Copilot cloud agent | .github/skills | unknown | not_run |
| Codex CLI | .agents/skills | conditional | not_run |
| Codex desktop | .agents/skills | unknown | not_run |
| Codex IDE extension | .agents/skills | unknown | not_run |
| Codex cloud | manual canonical-file handoff | unknown | not_run |
| Cursor CLI | .cursor/skills | conditional | not_run |
| Cursor editor | .cursor/skills | conditional | not_run |
| Cursor cloud | .cursor/skills | conditional | not_run |
| Gemini CLI | .gemini/skills | conditional | not_run |
| OpenCode CLI/TUI | .opencode/skills | documented | not_run |
| OpenCode desktop | manual canonical-file handoff | unknown | not_run |
| OpenCode IDE | manual canonical-file handoff | unknown | not_run |
| Factory Droid CLI | .factory/skills | conditional | not_run |
| Factory desktop | manual canonical-file handoff | unknown | not_run |
| Factory web/cloud | manual canonical-file handoff | unknown | not_run |
| Antigravity CLI | .agents/skills | unknown | not_run |
| Antigravity desktop | .agents/skills | unknown | not_run |
| Antigravity IDE | .agents/skills | unknown | not_run |
| Kiro CLI | .kiro/skills | conditional | not_run |
| Kiro IDE | .kiro/skills | conditional | not_run |
| Kiro web | .kiro/skills | unknown | not_run |
| Devin Desktop Cascade / Windsurf | .windsurf/skills | unknown | not_run |
| Devin CLI | .devin/skills | conditional | not_run |
| Devin Local | manual canonical-file handoff | unknown | not_run |
| Devin cloud | manual canonical-file handoff | unknown | not_run |
| JetBrains Junie CLI | .junie/skills | unknown | not_run |
| JetBrains Junie IDE | manual canonical-file handoff | unknown | not_run |
| Cline editor | .cline/skills | conditional | not_run |
| Cline CLI | manual canonical-file handoff | conditional | not_run |
| Continue IDE | manual canonical-file handoff | unknown | not_run |
| Continue CLI | manual canonical-file handoff | unknown | not_run |
| Aider CLI | manual canonical-file handoff | unknown | not_run |
| Unidentified host (explicit manual route) | manual canonical-file handoff | unknown | not_run |
<!-- CLI-TIERS:END -->

See [multi-CLI support](docs/multi-cli.md) for invocation differences and activation boundaries.
The portable Copilot kit uses `/li-<skill>` names; legacy plugin workflows use the naming
provided by their host.

## Explore and contribute

- [Documentation index](docs/README.md) · [FAQ](docs/faq.md) · [Glossary](docs/GLOSSARY.md)
- [Architecture](docs/architecture.md) · [Swarming work](docs/concepts/swarming-work.md) · [Engineering modules](docs/concepts/engineering-modules.md)
- [Skill catalog](skills/CATALOG.md) · [Pack resolution](docs/concepts/pack-resolver.md)
- [Contributing](CONTRIBUTING.md) · [Code of conduct](CODE_OF_CONDUCT.md) · [Changelog](CHANGELOG.md)

Bug reports from real client sessions are especially useful: include the exact surface and version,
installation route, task, expected behavior and a sanitized reproduction.

MIT for Lintel's original code; see [LICENSE](LICENSE). Bundled design resources retain their
[third-party attribution and licenses](skills/design-dna/ATTRIBUTION.md).
