# GitHub Copilot

Lintel's Copilot integration starts with a portable repository kit: short custom instructions,
native core workflow skills and three custom agent profiles. The same reviewed files travel with
a local checkout and a GitHub cloud agent checkout. The CLI plugin packages the same native core adapters as an optional route.

This page separates what Lintel ships from what the Copilot host supports. Client capabilities
were checked against GitHub's primary documentation on 2026-09-08; that review is not an
end-to-end validation of your installed client or enterprise configuration.

## Choose the integration

| Surface | Lintel entry point | Validation to perform |
|---|---|---|
| Copilot in VS Code | Repository kit: `.github/copilot-instructions.md`, `.github/skills/`, `.github/agents/` | Discover `li-plan`, choose an agent, complete a small task, resume in a fresh session |
| Copilot CLI | Repository kit, or optional CLI plugin | List installed skills and agents, execute a bounded plan, confirm written state |
| GitHub cloud agent | Commit the repository kit to the branch the agent receives | Verify resources, tools, policies and behavior inside the cloud execution environment |
| Other Copilot IDE clients | Repository instructions where supported | Validate skills and custom agents on that client's current version; no blanket parity claim |

GitHub supports repository skills and custom agents as customization mechanisms. Follow the
[skills documentation](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
and [CLI customization overview](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/overview)
for host-specific discovery and configuration. Lintel does not enable organisation policies or
provision Copilot access.

## Repository kit

From a reviewed Lintel checkout:

```bash
bash bin/li-copilot init --target ../your-repo
bash bin/li-copilot check --target ../your-repo
```

The optional `--source PATH` selects local source content. Installation uses ordinary files,
not symlinks or an installed plugin cache. The target's `.github/lintel/` resources are designed
to remain available when another developer or a cloud agent checks out the repository.

Core skills are `li-welcome`, `li-cycle`, `li-sense`, `li-scope`, `li-define`, `li-discover`,
`li-plan`, `li-build`, `li-review`, `li-ship`, `li-capture`, `li-resume` and `li-spec-kit`. Invoke them as
`/li-plan` and similar where the host offers slash invocation; otherwise name the skill or its
file. These are adapters to Lintel's canonical workflow, whose deeper documents often use
`/li:plan` notation. A colon command is not the portable skill's identifier.

The kit exposes `lintel-planner`, `lintel-builder` and `lintel-reviewer` profiles. They focus on
planning, implementation and independent review. They do not force a model, grant permissions
or promise parallel execution. Use host delegation when available; otherwise apply the roles
in sequence and report when review could not be independent.

The kit and CLI plugin expose the same native core entry points. The wider canonical catalog remains source content to read on demand. Their presence does not prove
that every specialist skill in the full catalog works on every Copilot surface.

## Copilot CLI plugin

For an operator who prefers plugin distribution of the same native core workflow:

```bash
copilot plugin marketplace add jokerman89/lintel
copilot plugin install li@jokerman-lintel
```

Inspect the plugin's discovered skills and agents in your installed CLI. Use the names it lists;
the native core adapters use `li-*`. A plugin installed on your workstation is not automatically
installed in a GitHub cloud agent job or another developer's checkout. Use the repository kit
for a shared, reviewable project configuration.

Check `copilot plugin --help` for update and removal commands supported by your installed
version. Avoid installing duplicate personal and project copies without checking which one the
client selects. [GitHub CLI customization](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/overview)
explains the available integration mechanisms.

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

Commit the complete kit and project knowledge needed for the task. A cloud agent cannot read a
local workstation's `~/.lintel/profile.yaml`, private pack checkout or previous chat transcript.
Put approved, non-secret project policy context in the repository or provision it through your
organisation's supported environment setup.

Provide project build tools, Bash and Python 3.9+ through that environment. Keep authentication in
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
Run `check`, inspect the diff, and repeat your pilot task before merging.

Rollback the adoption or upgrade through a reviewed Git change, retaining project lessons,
plans and decisions. The installer has no remove command; consult its inventory and remove
only files introduced by that installation after checking for subsequent edits. Avoid deleting
whole `.github/` or `.claude/` directories.

## Live-client acceptance before rollout

Run this checklist on each intended client and record its exact version, policies and Lintel
revision. Repeat it in the cloud execution environment if that is part of the rollout.

1. Confirm that project instructions, the full inline session protocol, all intended `li-*`
   skills and the three custom agent profiles are discovered from the reviewed installation.
2. Complete one bounded plan/build/review task. Inspect the specification, build-card IDs,
   actual tests and independent-review evidence; label sequential self-review honestly.
3. Start a fresh checkout/session without the original runtime state or personal instruction
   home. Verify `/li-resume` selects the committed active work map and the correct next card.
4. For a Spec Kit project, verify original spec/design/tasks paths and task IDs stay authoritative,
   with no duplicate backlog or unsolicited initialization.
5. Confirm the platform's required checks, reviews and permission boundaries under its approved
   test procedure. Verify that no Lintel Copilot hook protection is being assumed.

Passing local installation and contract tests supports the **0.9.0 public beta** release. It does
not replace this client acceptance, prove enterprise compliance or constitute a 1.0 support claim.

## Pilot evidence

Record the Lintel revision, Copilot client/version, enabled policies, repository kit check output,
observed skill and agent discovery, first-task result, verification output and fresh-session
resume result. Mark anything untested explicitly. A structural check is useful evidence of
installation integrity; it does not establish model adherence, productivity gains or compliance.

See [enterprise adoption](enterprise-adoption.md) for the rollout decision and
[Spec Kit](spec-kit.md) for projects that already use specification-driven development.
