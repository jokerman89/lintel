---
slug: copilot-native-parity
started_at: 2026-09-28
grace_until: none
removal_at: none
old_shape: 15 generated Copilot pointer skills in .github/skills/li-<name>/SKILL.md that asked the model to read the canonical file, and 3 pointer agent profiles in .github/agents/lintel-*.agent.md
new_shape: a complete generated native skill for every canonical skill, a custom agent for every canonical agent plus the three lintel-* role profiles, and the bin/li-run shell-step runner
risk_class: medium
detect_pattern: grep -rl "Read the \[Copilot adapter contract\]" .github/skills .github/agents
---

# Copilot native skills and agents

ADR-0039 replaces Lintel's Copilot pointer adapters with complete native files generated from
the canonical sources, starting with the unreleased 0.13.0. Each `li-<name>` skill now carries
the whole canonical method instead of asking the model to read a separate file, and every
canonical agent is a Copilot custom agent. Skill names do not change: `/li-plan` and the other
existing invocations keep working. This guide applies to repository kits, plugin installations
and forks that edit canonical skills or agents.

## What changes

| Before | After |
|---|---|
| 15 pointer skills in `.github/skills/li-<name>/SKILL.md` for the core workflows | A complete generated skill in `.github/skills/li-<name>/SKILL.md` for every canonical skill (96 at this revision) |
| Other catalog workflows read on demand from `.github/lintel/skills/<name>/SKILL.md` | Invoked as native skills, for example `/li-verify`; the canonical file stays the fallback when a surface does not discover a skill |
| 3 pointer profiles: `lintel-planner`, `lintel-builder` and `lintel-reviewer` | The same three role profiles, which now run the native `/li-plan`, `/li-build` and `/li-review` skills, plus a custom agent in `.github/agents/<Name>.agent.md` for every canonical agent (69 at this revision) |
| Shell steps bootstrapped by hand with `lib/copilot-env.sh` | `bin/li-run` prepares the environment for each native skill's Bash step; the manual bootstrap still works |

## Update a repository kit

1. On an upgrade branch, run `init` from the reviewed Lintel revision, then `check`:

   ```bash
   bash bin/li-copilot init --target ../your-repo
   bash bin/li-copilot check --target ../your-repo
   ```

   Until `init` succeeds, `check` reports the new and changed managed files as missing or
   outdated and names the missing `.gitattributes` rules.
2. Resolve any refusal. `init` checks every path before it writes, and one refusal stops the
   whole update: it preserves your files, writes nothing and names each path. A managed
   pointer you edited is a modified managed file; move your edits into project-owned files.
   A project file at a new generated path is an unmanaged collision, most likely a custom
   agent of yours with a generated name; see
   [custom agents with a generated name](#custom-agents-with-a-generated-name). Run `init`
   again after each fix.
3. Review the diff. `init` rewrites the managed pointer skills and the three role profiles,
   adds a skill directory for every other canonical skill and an `.agent.md` file for every
   canonical agent, and refreshes the `.github/lintel/` bundle (which includes `bin/li-run`),
   the instruction files it owns and the inventory `.github/lintel/manifest.json`. It appends
   missing line-ending rules to `.gitattributes`, one of which also covers your own agent
   files; see [line endings of agent files](#line-endings-of-agent-files). Two of those rules
   name hook registration paths that this release does not create; the inventory records
   `hooks_installed: false`.
4. Commit the regenerated files and start a new Copilot session. Verify discovery as described
   in the [Copilot guide](../copilot.md#verify-discovery), then repeat your pilot task.

Project-owned files, lessons, plans and decisions are not touched.

## Custom agents with a generated name

The update adds a custom agent for every canonical agent at `.github/agents/<Name>.agent.md`,
for example `Planner.agent.md`, `Explorer.agent.md` and `CodeReviewer.agent.md`. If your
repository already has a custom agent at one of those paths, `li-copilot init` refuses the
whole update as an unmanaged collision. It writes nothing and reports each such file, for
example `Unmanaged collision (preserved): .github/agents/Planner.agent.md`; `check` from the
same revision lists the same collisions without writing. This also applies when you install
the kit for the first time.

To resolve a collision:

1. In a reviewed change, rename your agent, giving both its file and its `name` field a name
   that no generated agent uses so the two stay distinguishable, or remove it if the generated
   agent replaces it.
2. Update any prompt or instruction that selects your agent by its old name.
3. Run `init` again, then `check`.

A skill directory of yours at a new generated `.github/skills/li-<name>/` path collides the
same way; rename or remove it before you run `init` again. GitHub also documents that a
repository-level custom agent takes precedence over an organization- or enterprise-level
agent with the same file name
([custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)).
In this repository, a generated agent therefore takes precedence over such an agent, so check
those levels for the generated names before you roll out.

## Line endings of agent files

`init` appends the rule `.github/agents/*.agent.md text eol=lf` when it is missing. It
matches every agent file directly in that folder, including agents your project owns, not
only the generated ones. Git then normalizes those files to LF when they are added and checks
them out with LF, whatever `core.autocrlf` says
([gitattributes](https://git-scm.com/docs/gitattributes)). `init` only appends rules, so an
earlier `.github/agents/lintel-*.agent.md` line stays; it is harmless.

If your own agent files were committed with CRLF line endings, normalize them in a reviewed
commit of their own, as Git's documentation describes:

```bash
git add --renormalize .github/agents
git status
```

## Update a plugin installation

Update the plugin through the route you installed it with, for example
`copilot plugin update li`. For a marketplace installation, refresh the catalog first with
`copilot plugin marketplace update jokerman-lintel`. The plugin ships Lintel's own generated
`.github/skills/` and `.github/agents/`, so it gains every skill and agent at once. When a
repository also carries a kit, both copies expose the same names; keep one route per
repository and check which copy the client selects.

## What the generated files leave out

Copilot reads only some frontmatter, so the generator drops the rest and records each loss as a
degradation:

- **Skills** keep `name` and `description` (curated for the core workflows, at most 1024
  characters). They lose `layer`, `color`, `tools`, `voice`, `cli_support`, `necessity`,
  `gap_if_skipped`, `navigation`, `workflow_root`, `domain`, `license_note` and `hop_in`.
- **Agents** keep `name`, `description` and `tools`. They lose `memory`, `model`, `color`,
  `tier`, `voice`, `category` and `cli_support`. Without memory, an agent that recalls prior
  findings starts fresh on every run; those agents declare `level: degraded` in their
  `cli_support` hint. Without `model`, the host's configured model applies.
- **Tool scope:** canonical agent profiles carry their declared `tools` subset, enforced by
  Copilot where it honors the field. The three `lintel-*` role profiles declare no `tools`
  field and receive all tools. Independent review means a separate context, not read-only
  enforcement.

The body of each generated file is the canonical text with only the documented transforms:
`/li:<name>` becomes `/li-<name>`, `AskUserQuestion` becomes `ask_user`, and links are rebased.
In a vendored kit, a link to a file outside the bundle becomes a public GitHub URL, so those
few references need network access. The [Copilot adapter contract](../../shims/copilot/COPILOT.md)
states the full model.

## Run shell steps with bin/li-run

Native skills tell the model to save each Bash snippet to a temporary `.sh` file and run
`bash "<resource root>/bin/li-run" <file>`; in a kit, the resource root is `.github/lintel`.
`--repo <dir>` selects the working repository, and `-` reads the step from standard input. The
runner sets `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT` and the profile context, then exits with the
step's status: 2 means a usage error or a missing script, and 1 an environment it could not
prepare. Provide Bash wherever Copilot runs these skills, including cloud agent environments;
on Windows use Git for Windows' `bash.exe`, never `System32\bash.exe`.

## Regenerate after editing a skill or agent

The generated files are committed and drift-checked. In Lintel itself or a fork, after you add
or edit a canonical skill or agent, run these commands and commit the regenerated files with
the change:

```bash
python bin/li-copilot.py init --target . --source .
python bin/li-catalog.py
bash bin/li-wiki-gen
```

CI fails on drift in any of the three outputs. Never edit `.github/skills/` or
`.github/agents/` by hand; see [contributing](../../CONTRIBUTING.md). In a consumer kit the
same files belong to the kit's inventory: update them by running `init` from a reviewed Lintel
revision, not by editing them.

## Hooks

This change installs no Copilot hooks; the hook boundaries in the
[Copilot guide](../copilot.md#hooks-and-security-controls) still apply. Copilot hook
activation arrives in a later release, which adds its own section to this guide.

## Roll back

Revert the upgrade commit with a reviewed `git revert`, which restores the earlier files and
inventory together. Do not run an earlier Lintel revision's `init` over an upgraded kit: it
refuses the new inventory because the canonical agent paths lie outside its managed
namespaces. Do not delete whole `.github/` or `.claude/` directories.
