# GitHub Copilot

Lintel's Copilot integration is generated from its canonical sources. Every canonical skill
becomes a complete, self-contained native skill named `li-<name>`, and every canonical agent
becomes a custom agent, alongside three `lintel-*` role profiles. The same generated files
reach Copilot through the Copilot plugin or through a portable repository kit that travels
with a local checkout and a GitHub cloud agent checkout.

This page separates what Lintel delivers from what GitHub documents and from what a live
session has observed. Client capabilities are recorded with dated primary sources in
`lib/cli-tiers.yaml`; that review is not an end-to-end validation of your installed client
or enterprise configuration.

## What is native

`li-copilot init` generates these files from `skills/` and `agents/`:

| Generated path | Contents |
|---|---|
| `.github/skills/li-<name>/SKILL.md` | One complete skill for every canonical skill (96 at this revision): `name`, `description`, a short Copilot preamble and the full canonical body |
| `.github/agents/<Name>.agent.md` | One custom agent for every canonical agent, with its `name`, `description` and declared `tools` |
| `.github/agents/lintel-planner.agent.md`, `lintel-builder.agent.md`, `lintel-reviewer.agent.md` | Role profiles that run the native `/li-plan`, `/li-build` and `/li-review` skills |
| `.github/copilot-instructions.md`, `.github/instructions/lintel-session.instructions.md` | Short repository instructions that route work to the native skills |

Every workflow is a native skill. Invoke `/li-plan`, `/li-verify` or any other `/li-<name>`
where the host offers slash invocation, or name the skill. Named roles such as
`CodeReviewer` are custom agents that a workflow delegates to by name. Deeper documents in
the source tree use the Claude plugin's `/li:plan` notation. Generated bodies already use
the `/li-<name>` spelling; a colon command is not a Copilot skill identifier.

A generated skill keeps the canonical method apart from deterministic transforms:
`/li:<name>` becomes `/li-<name>`, `AskUserQuestion` becomes `ask_user`, and relative links
are rebased to the generated location. In a vendored kit, a link to a file outside the
bundle becomes a public GitHub URL. The preamble states the resource root, the shell-step
runner `bin/li-run`, the tool map and native invocation. The tool map uses the Copilot CLI
runtime names that GitHub's hooks reference documents: Read=`view`, Write=`create`,
Edit=`edit`, Bash=`bash` or `powershell`, Grep=`grep`, Glob=`glob`,
AskUserQuestion=`ask_user`, WebFetch=`web_fetch`, and a named role=`task` with that custom
agent.

For stdin steps (`bash bin/li-run -`), the runner removes its temporary buffer on
normal exit and catchable HUP, INT or TERM termination. A step's own traps stay
inside its subshell. SIGKILL and host crashes cannot run shell cleanup.

Frontmatter that Copilot does not read is dropped and recorded as a degradation. Skills
keep `name` and `description`; agents keep `name`, `description` and `tools`. Agents lose
persistent memory, a pinned model and catalog metadata, so roles whose method recalls
prior findings are marked `degraded` in their `cli_support` hint. Canonical agent profiles
carry their declared `tools` subset, enforced by Copilot where it honors the field. The
three `lintel-*` role profiles declare no `tools` field and receive all tools. Independent
review means a separate context, not read-only enforcement. The
[Copilot adapter contract](../shims/copilot/COPILOT.md) lists every dropped field.

## Choose an installation route

| Route | How to install | Scope |
|---|---|---|
| Copilot CLI plugin | `copilot plugin install jokerman89/lintel` | Your Copilot CLI configuration, across projects |
| Copilot CLI plugin from Lintel's marketplace | `copilot plugin marketplace add jokerman89/lintel`, then `copilot plugin install li@jokerman-lintel` | The same plugin, versioned through the marketplace |
| GitHub Copilot app | **Customize**, then **Plugins**: browse a marketplace and install the `li` plugin | Your app sessions |
| Copilot cloud agent | Add the `li` plugin to `enabledPlugins` in the repository's `.github/copilot/settings.json` | Cloud agent jobs for that repository |
| Repository kit | `bash bin/li-copilot init --target ../your-repo` from a reviewed Lintel checkout | Committed files that every checkout and cloud job receives |

GitHub documents the plugin routes in [about Copilot plugins](https://docs.github.com/en/copilot/concepts/agents/about-plugins)
and the [CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference).
Lintel's marketplace is not one of the CLI's default marketplaces. For the cloud agent, also
add it to `extraKnownMarketplaces` in the same settings file, following GitHub's
documentation for the exact entry format. Lintel does not create
`.github/copilot/settings.json`, enable organisation policies or provision Copilot access.
GitHub's [skills documentation](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
and [CLI customization overview](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/overview)
describe host-specific discovery and configuration.

A plugin installed on your workstation is not installed for other developers; share it
through `enabledPlugins` or the committed kit. Update or remove it with
`copilot plugin update li` and `copilot plugin uninstall li`; check `copilot plugin --help`
for the commands your installed version supports. The plugin and the kit carry the same
generated skills and agents under the same names. Use one route per repository and check
which copy the client selects before relying on it, so a personal copy does not shadow
the one you reviewed.

## Repository kit

From a reviewed Lintel checkout:

```bash
bash bin/li-copilot init --target ../your-repo
bash bin/li-copilot check --target ../your-repo
```

The same ownership/bundling engine has a Universal entry. Select the exact surface, for example
`python3 bin/li-adapter.py init --client copilot-app --target ../your-repo`, and use its `check`
command to verify the installed surface set. Repeated `--client` flags add teammates' documented
native routes without duplicating the source bundle or removing Copilot's native files.

The optional `--source PATH` selects local source content. Installation uses ordinary files,
not symlinks or an installed plugin cache. The target's `.github/lintel/` resources are designed
to remain available when another developer or a cloud agent checks out the repository.

The kit delivers the same generated skills and custom agents as the plugin, with the canonical
resources bundled under `.github/lintel/`. The `lintel-planner`, `lintel-builder` and
`lintel-reviewer` role profiles focus on planning, implementation and independent review. No
generated agent forces a model, grants permissions or promises parallel execution. Use actual
host delegation and attributable isolated writes when available; otherwise retain
serial/manual package handoffs. A self-review cannot close a requirement for a separately
attributable independent reviewer.

Every catalog workflow, including `inspect`, `verify` (read-only unless repair is authorized),
`diagnose`, `cross-check` and `pause`, is a native skill such as `/li-verify`. If a surface
does not discover a skill, read its canonical file at `.github/lintel/skills/<name>/SKILL.md`
in the repository kit, or the plugin's installed `skills/<name>/SKILL.md`. Delivered files do
not prove that every specialist skill or agent works on every Copilot surface. Former entry
names are mapped in the [native workflow migration](migrations/2026-09-25-native-workflows.md);
they are not aliases.

## Verify discovery

Start a new session in the repository root after installing or updating, then compare what
the host discovered with what was delivered:

- `copilot skill list --json` prints each discovered skill's name, description, source, path
  and enabled state. Expect one enabled `li-<name>` skill for every canonical skill (the total
  in [the skill catalog](../skills/CATALOG.md)), from the route you installed.
- In an interactive Copilot CLI session, `/agent` browses the available custom agents. Expect
  one per canonical agent plus `lintel-planner`, `lintel-builder` and `lintel-reviewer`.
- For the repository kit, `bash bin/li-copilot check --target ../your-repo` verifies the
  generated files, inventory and links. It proves integrity, not discovery.

Then run the session acceptance check in the
[Copilot adapter contract](../shims/copilot/COPILOT.md#session-acceptance-check): plan a small
change with `/li-plan`, execute one authorized card with `/li-build`, and resume in a fresh
session with `/li-resume`. Record the result with the
[live-client acceptance](#live-client-acceptance-before-rollout) checklist.

## Surface matrix

Vendor facts below are documented by GitHub and cited in the registry or this page; the routes
are delivered by Lintel. The registry records one live observation of these native skills and
agents, on the Copilot CLI; every other live verification cell is pending observation.

| Surface | Delivered route | Documented by GitHub | Live verification |
|---|---|---|---|
| Copilot CLI | Plugin or repository kit | Skills, custom agents and plugin installation | Observed on Windows with the plugin loaded through `--plugin-dir` and with a vendored kit. CLI 1.0.89: all native skills discovered, `li-cycle` delivered in full, and `CodeReviewer` selected (as `li:CodeReviewer`). CLI 1.0.90: the host listed all generated agents on both routes. Installed-plugin and marketplace routes, other operating systems, versions and models are pending |
| GitHub Copilot app | Plugin (**Customize**, then **Plugins**) or the kit in the selected local worktree | Skills and plugin installation; the cited custom-agent reference does not name the app | Pending observation |
| Copilot in VS Code | Repository kit | Skills and custom agents; tool names and formats may differ from the preamble's map | Pending observation |
| Copilot cloud agent | Plugin through `enabledPlugins`, or the kit committed to the branch the agent receives | Skills, custom agents and `enabledPlugins` | Pending observation |
| Other Copilot IDE clients | Repository instructions where supported | Varies by client; no blanket parity claim | Pending observation |

`python3 bin/li-client-capabilities.py show --client copilot-cli` prints one surface's sources,
delivered bindings and recorded observations. Only a recorded observation turns a pending cell
into a live claim; see [pilot evidence](#pilot-evidence) for what to record.

## Working with existing repository instructions

Keep the repository's real build commands, architecture constraints and verification procedures
in its existing instruction files. Add a short Lintel entry point and link to detailed resources
as needed. Repository-wide instructions should stay concise; specialized workflows belong in
skills. The installer preserves an existing `.github/copilot-instructions.md` and adds
`.github/instructions/lintel-session.instructions.md` for Lintel. It inserts the full shared
session protocol into marked blocks in `AGENTS.md` and `CLAUDE.md`, retaining project prose
outside those blocks. Subsequent local edits to a managed block or file cause an update conflict
instead of being silently overwritten.

GitHub's own instruction scoping determines which files Copilot automatically loads. Lintel's
[instruction precedence](precedence.md) is an additional workflow convention, not a replacement
for the host's rules. If two instructions conflict, resolve the conflict explicitly in the project.

## Cloud agent environment

Commit the complete kit, or the `.github/copilot/settings.json` entry that enables the plugin,
together with the project knowledge the task needs. A cloud agent cannot read a
local workstation's `~/.lintel/profile.yaml`, private pack checkout or previous chat transcript.
Put approved, non-secret project policy context in the repository or provision it through your
organisation's supported environment setup.

Provide project build tools, Bash and Python 3.9+ through that environment; native skills
run their shell steps through `bin/li-run`, which needs Bash. Keep authentication in
the platform's supported secret mechanisms. Lintel neither provisions credentials nor broadens
the cloud agent's repository access. Confirm setup and tests in a real pilot job before rollout.

## Hooks and security controls

GitHub Copilot CLI and cloud agents support native hooks in `.github/hooks/*.json`; see
[GitHub's hook reference](https://docs.github.com/en/copilot/reference/hooks-reference).
**Lintel does not currently ship a Copilot translation of its Claude Code hook bundle.**
The repository kit installs no hook configuration. Instructions to check secrets or obtain
approval therefore remain cooperative workflow rules on this route.

Use your organisation's repository protection, CI, secret scanning and access policies for
controls that must hold independently of the agent. Test any custom Copilot hook against the
host's actual input/output contract. Do not infer enforcement from a file named `HOOK.md`.

## Upgrade and rollback

Run `init` from the next approved Lintel revision on an upgrade branch. Managed files that remain
unchanged may refresh; local edits or conflicting files require review before an update proceeds.
Every planned write is bound to the exact file state its bytes or create/merge decision came
from. A file created, edited or deleted after planning refuses the write before publication
and is preserved. Files that were only read are compared once more just before publication; a
change after that final comparison is outside this non-atomic guarantee.
Run `check`, inspect the diff, and repeat your pilot task before merging.

An upgrade can add, replace or remove many generated files under `.github/skills/` and
`.github/agents/`. Review them as generated output rather than editing them, and read the
[migration index](migrations/_INDEX.md) for the actions a release needs.

`init` records an owned file transaction with an explicit separate recovery store.
Its reported default is a compact full-target-bound sibling; `--store` or
`LINTEL_RECOVERY_STORE` overrides it exactly. Interruption is not completion and blocks
a new init until explicitly reconciled. To inspect or reverse verified owned bytes:

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-copilot.py" inspect \
  --target "$target" --store "$store" --transaction "$id"
python3 "$LINTEL_SOURCE_ROOT/bin/li-copilot.py" recover \
  --target "$target" --store "$store" --transaction "$id"
```

Recovery refuses later edits, foreign/corrupt receipts and reuse of consumed restore
permission. It does not reactivate/deactivate a host or roll back external effects.
See [lifecycle operations](lifecycle.md) for source/profile boundaries and limitations.

The reusable-patterns release adds `patterns.source: null` to the bundled neutral pack. That
changes the neutral manifest, so every bound profile context, including ones used only by
unrelated callers, reports drift until you rebind it explicitly with a reason. Then re-plan the
affected work. Nothing rebinds automatically. See [reusable patterns](concepts/patterns.md).

Rollback the adoption or upgrade through a reviewed Git change, retaining project lessons,
plans and decisions. The installer has no remove command; consult its inventory and remove
only files introduced by that installation after checking for subsequent edits. Avoid deleting
whole `.github/` or `.claude/` directories.

## Live-client acceptance before rollout

Run this checklist on each intended client and record its exact version, policies and Lintel
revision. Repeat it in the cloud execution environment if that is part of the rollout.

1. Confirm that project instructions, the full inline session protocol, every generated `li-*`
   skill and every custom agent (the canonical agents and the three `lintel-*` role profiles)
   are discovered from the reviewed installation, as described in
   [verify discovery](#verify-discovery).
2. Complete one bounded plan/build/review task. Inspect the specification, build-card IDs,
   actual tests and independent-review evidence; label sequential self-review honestly.
3. Start a fresh checkout/session without the original runtime state or personal instruction
   home. Verify `/li-resume` selects the committed active work map and the correct next card.
4. For a Spec Kit project, verify original spec/design/tasks paths and task IDs stay authoritative,
   with no duplicate backlog or unsolicited initialization.
5. Confirm the platform's required checks, reviews and permission boundaries under its approved
   test procedure. Verify that no Lintel Copilot hook protection is being assumed.

Passing local installation and contract tests supports the repository integration. It does
not replace this client acceptance, prove enterprise compliance or constitute a 1.0 support claim.

## Pilot evidence

Record the Lintel revision, exact Copilot surface/version, enabled policies, repository kit check output,
observed skill and agent discovery, first-task result, verification output and fresh-session
resume result. Mark anything untested explicitly. A structural check is useful evidence of
installation integrity; it does not establish model adherence, productivity gains or compliance.

See [enterprise adoption](enterprise-adoption.md) for the rollout decision and
[Spec Kit](spec-kit.md) for projects that already use specification-driven development.
