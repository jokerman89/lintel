# Getting started

Start with a small change in a pilot repository. The Copilot repository kit installs the workflow
beside your code so teammates and repository-based agents can discover the same instructions.
You do not need a global Lintel installation or a company pack.

## 1. Install the Copilot repository kit

Prerequisites: Git, Bash and Python 3.9+, plus your organisation's approved Copilot client and access.
Use Git Bash on Windows. Installation itself makes no network requests; cloning below retrieves
Lintel from GitHub.

```bash
git clone https://github.com/jokerman89/lintel.git
cd lintel
bash bin/li-copilot init --target ../your-repo
bash bin/li-copilot check --target ../your-repo
```

Replace `../your-repo` with the intended existing project directory. For a controlled rollout, check out
a reviewed Lintel tag or commit before `init`. Review the generated diff and record the source
revision in the adoption pull request.

`init` preserves unrelated files. It can refresh unchanged files it manages, but refuses to
replace modified managed files or conflicting existing files. Resolve such a conflict in a
reviewed branch; do not delete team instructions to make an installer succeed. `check` inspects
the installed artifacts and source drift. It does not authenticate Copilot or prove discovery in
your client.

The optional `--source PATH` selects a different local Lintel source directory. The equivalent
factory entry is `bash bin/li-scaffold init --copilot --target ../your-repo` from the same
checkout; it also needs no global installation. On that route, `--copilot` accepts `--target`
only. Name, pack, mode, voice and compliance flags belong to the separate bare scaffold route
and are rejected rather than silently ignored.

## 2. Verify discovery in Copilot

Open the target repository in VS Code with Copilot, Copilot CLI, or a configured GitHub cloud
agent environment. Ensure the repository is trusted and customizations are enabled by your
organisation's policy. GitHub documents repository discovery of agent skills under
`.github/skills/`; availability and invocation UI vary by host.
[GitHub's skill guide](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
describes the supported surfaces.

Run `/li-welcome`, or ask:

```text
Read .github/skills/li-welcome/SKILL.md and follow it. Show the repository instructions,
active workflow and current work. Report any unavailable integration or missing files.
```

Confirm that the response refers to this repository's actual files. The kit includes
`lintel-planner`, `lintel-builder` and `lintel-reviewer` custom agent profiles. Select a profile
when your client exposes an agent picker; otherwise the skills can guide the main session.

## 3. Complete one build card

Try a bounded request relevant to your project:

```text
/li-plan Add a health endpoint. Define the expected response, failure behavior and a
focused acceptance test. Inspect existing routes and test conventions before planning.
```

The plan should identify the specification, acceptance criteria, affected files, verification
commands and small build cards. Review it before implementation. Then:

```text
/li-build Execute the approved plan one build card at a time. Verify each card against
its acceptance criteria and record completed work and any blocker.
```

Use `/li-review` for an independent review against the specification and changed code. Use
`/li-ship` to prepare the authorized delivery, with relevant checks and a reviewable diff.
Deployment, repository permissions and publishing still require the authority established for
that task. `/li-capture` records lessons and decisions for the next session.

## 4. Resume in a fresh session

After the first change, open a fresh session and run `/li-resume`. Ask it to identify completed
cards, remaining work, the verification evidence and the next action from the repository files.
This is the most useful pilot check: continuity should survive closing the original chat.

## Where things live

| Path | Purpose |
|---|---|
| `AGENTS.md` and `CLAUDE.md` | Full shared session protocol alongside preserved project instructions |
| `.github/copilot-instructions.md` | Short entry point when absent; an existing team entry is preserved |
| `.github/instructions/lintel-session.instructions.md` | Additive scoped entry to the Lintel workflow |
| `.github/skills/li-*/SKILL.md` | Native skills for the core development workflow |
| `.github/agents/lintel-*.agent.md` | Planner, builder and reviewer profiles |
| `.github/lintel/` | Managed local workflow resources; portable to another machine or cloud checkout |
| `.claude/memory/` | Committed lessons, working state and personas |
| `.claude/plans/` | Committed plans and implementation handoffs |
| `.claude/decisions/` | Architecture decisions |
| `.claude/runtime/` | Local session state, excluded from Git |

The `.claude/` name is Lintel's shared storage convention, including when you use Copilot.
It does not require Claude Code. The installer inventory identifies managed resources; knowledge
written during a project belongs to the project, not to an upstream template update.

For a bare global installation, `~/.lintel/` additionally holds profile settings, packs and
helper resources. That is an optional installation route, not a Copilot kit prerequisite.

Pack selection normally lives in `~/.lintel/packs/active-pack`; `profile.yaml`
stores preferences such as mode and role. A bare-install pack switch therefore
affects subsequent sessions sharing that operator home, not just the current
repository. The current session keeps its cached identity. Repository adapters
can configure separate roots through `LINTEL_HOME`, `LINTEL_PACKS_DIR` and
`LINTEL_ACTIVE_PACK_FILE`; inspect the resolved paths before changing a pack.
See [pack resolution](concepts/pack-resolver.md) for source and target precedence.

## How hook activation works

| Install route | Lintel hook behavior |
|---|---|
| Copilot repository kit | No Lintel hooks installed |
| Copilot CLI plugin | Skills and agents; no claim that Claude Code hooks are adapted |
| Claude Code plugin | Selected hooks register through `hooks/hooks.json` |
| Bare installer | Hook files copied inert; activation requires explicit hook registration |
| Other clients | Follow the integration capability table |

Copilot has a native hook API, but its schema differs from Claude Code's. Do not copy
`hooks/hooks.json` into `.github/hooks/` and assume it works. Teams can build and validate their
own Copilot hooks using [GitHub's hook documentation](https://docs.github.com/en/copilot/concepts/agents/hooks).
Lintel's workflow instructions apply even when no hooks run. See [compliance](compliance.md)
for the distinction between instructions, pattern scanning and enforceable repository controls.

## Other installation routes

Use [multi-CLI support](multi-cli.md) for Claude Code, Codex, Cursor and other clients.
For plugin distribution of the same native core workflows, see [Copilot CLI plugin](copilot.md#copilot-cli-plugin).
The global Bash or PowerShell installers remain available for shared resources:

```bash
bash install/install.sh
```

```powershell
pwsh -File install/install.ps1
```

The global installers are different from the per-repository Copilot kit. Before choosing one,
review the installer and its target paths. They create machine-level state in `~/.lintel/`.

## Troubleshooting

- **Skill absent in the picker:** check repository trust, organisation policy and the client's
  support for repository skills. Start a fresh session or use the client's reload mechanism.
  Ask Copilot to read the exact `SKILL.md` path as a diagnostic.
- **Installer conflict:** inspect the named path. Preserve your existing instructions and merge
  the needed Lintel entry manually; rerun `check` and review any reported drift.
- **Missing Bash or Python:** use Git Bash on Windows and make Python 3.9+ available on that shell's
  PATH. The portable resources must also be available in a cloud agent environment.
- **Hooks absent:** this is expected on the Copilot kit. Configure required CI checks and merge
  policies independently of Lintel.
- **Session loses its plan:** verify that the plan and working state were written into the
  repository, and ask `/li-resume` to cite those files.

Next: [Copilot](copilot.md), [enterprise adoption](enterprise-adoption.md),
[Spec Kit](spec-kit.md), [the cycle](the-cycle.md), or the [documentation index](README.md).
