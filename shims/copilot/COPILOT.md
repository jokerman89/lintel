# Lintel adapter for GitHub Copilot

This contract adapts Lintel's canonical workflows to Copilot CLI, Copilot App, VS Code
and the GitHub cloud agent as distinct surfaces. A workflow is an instruction, not a runtime guarantee. Host
capabilities and enterprise policies remain authoritative.

## Bootstrap and paths

Read the working repository's AGENTS.md (and CLAUDE.md when it contains project
instructions), CORE-PRINCIPLES.md (scaffolding/01-foundation/CORE-PRINCIPLES.md in
Lintel itself), recent .claude/memory/lessons.md and relevant
.claude/decisions/. Preserve the user's existing authorization throughout the task.

The canonical resource root is the directory containing bin/, lib/, skills/ and
scaffolding/. For a downstream kit it is `.github/lintel/`; when developing Lintel
itself it is the repository root. Read source paths from that root. Always write
plans, memory, specs and build evidence into the working repository's `.claude/`
tree. Never write project output into the bundled source directory.

Canonical workflows may refer to another `/li:<skill>` or to `skills/<skill>/SKILL.md`.
On Copilot that workflow is a native `/li-<skill>` skill (see "Native skills and agents"):
invoke it instead of reading its file. Where a surface does not discover it, read the
canonical file from the resource root and execute it using these same adaptations.
Only load the relevant workflow and references. Delivered files are not validation:
do not claim every catalog workflow has been validated in every Copilot client.

For task routing, use `define` for requirements, `inspect` for plan/repository inspection,
`verify` for checks, `diagnose` for investigation and `cross-check` for a separately
attributable review. `verify` is read-only unless repair is explicitly authorized.
Use `pause` and `resume --from <checkpoint-path>` for saved context. Existing
`resume --from <phase|job-step>` overrides remain supported; use an explicit path
such as `./BUILD` for a checkpoint whose name matches a phase or selected step.
These are canonical workflow names; on Copilot each is also a native skill, such as
`/li-verify`. Use the canonical-file fallback above when discovery is unavailable.
Consolidation preserves the selected work map, profile reference and shared review/QA
evidence contracts.

If a shell helper is necessary, use Bash (Git Bash on Windows), keep the current
directory at the working repository, and set LINTEL_REPO_ROOT to that repository.
Resolve the helper by its full path under the resource root. Do not assume the
operator has a global Lintel installation. The bundled neutral pack is the fallback;
company packs and credentials are never copied by the kit. Do not activate or claim
company pack enforcement unless it has been configured and independently verified.

Launch bundled shell tools with `bash <resource-root>/bin/<tool>` and Python tools
with `python3 <resource-root>/bin/<tool>.py` (`python` when that is the Python 3 command).
Always supply the interpreter: a kit committed from Windows may have no executable
file-mode bits on a later Linux or macOS clone. Source `.sh` libraries rather than
executing them as standalone tools.

For a downstream kit, initialize the helper environment in each terminal invocation:

```bash
source .github/lintel/lib/copilot-env.sh
lintel_copilot_env "$PWD"
source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"
```

When developing Lintel itself, source `lib/copilot-env.sh` instead. The helper keeps
canonical source lookup separate from project output, uses local gitignored runtime
storage by default and respects explicit operator configuration. `LINTEL_SOURCE_ROOT`
locates bundled helpers; `LINTEL_REPO_ROOT` locates the working project. A native
skill's Bash step gets the same preparation from `bin/li-run` (see the tool map below).

## Native skills and agents

`li-copilot init` generates a complete, self-contained native skill for every canonical
skill at `.github/skills/li-<name>/SKILL.md`. It also generates a custom agent for every
canonical agent at `.github/agents/<Name>.agent.md`, plus the `lintel-planner`,
`lintel-builder` and `lintel-reviewer` role profiles. The Copilot plugin manifest
`.github/plugin/plugin.json` points at the same two roots. Every workflow is a native
`/li-<name>` skill; named roles such as `CodeReviewer` are custom agents, delegated to
by name.

A generated skill is the canonical body with deterministic transforms: `/li:<name>`
becomes `/li-<name>`, `AskUserQuestion` becomes `ask_user`, and relative links are
rebased to the generated location. A short preamble states the resource root, where
skill-relative paths resolve, the shell-step runner, the tool map and native invocation.
Agents receive the same body transforms and a shorter preamble without the skill-relative
paths bullet. Edit the canonical file, then run `li-copilot init`; `li-copilot check` fails
on drift, and CI runs it.

Skill-relative paths in a native skill's body refer to the Lintel source under the
resource root, not to the generated `.github/skills/li-<name>/` folder, which holds only
`SKILL.md`. The skill's own `scripts/`, `references/` and `data/` folders, and a `<base>`
that the workflow defines as its own directory, mean `skills/<name>/` there; a `<base>`
with another meaning, such as a Git base ref in code review, keeps it.
`${LINTEL_SKILLS_DIR:-skills}` names the skills root, `<resource-root>/skills`. `bin/li-run`
always sets `LINTEL_SKILLS_DIR` to its own source's `skills/` folder and ignores an
inherited value, so a shell step uses `$LINTEL_SKILLS_DIR/<name>/`.

In a vendored kit, a link from a native file to a repository-only file that the bundle
does not carry, for example under `.claude/`, points to the public GitHub source on
`main`. Such a link follows that branch and is not fetched or live-verified by the
installer. Bundled guides that contain such links start with a source note; native
skill and agent files carry no separate source note, so this section documents the
policy.

Generated frontmatter keeps only the fields Copilot reads. Every dropped field is a
recorded degradation, not a silent loss:

- Skills keep `name` and `description` (curated text for the core workflows, at most
  1024 characters). They drop `layer`, `color`, `tools`, `voice`, `cli_support`,
  `necessity`, `gap_if_skipped`, `navigation`, `workflow_root`, `domain`,
  `license_note` and `hop_in`. Without `tools`, a skill does not narrow the session's
  tools.
- Agents keep `name`, `description` and `tools`. They drop `memory`, `model`, `color`,
  `tier`, `voice`, `category` and `cli_support`. GitHub documents no agent memory
  property, so prior findings do not carry over between runs; agents whose method
  recalls them declare `level: degraded` with an `AgentMemory` degradation in their
  `cli_support` hint. Without `model`, the host's configured model applies.
- Pack-resolved identity (voice, compliance, brand) still comes from the active pack at
  runtime; only the catalog metadata is absent from the generated file.

These canonical hints retain their legitimate source meaning. See the Universal
adapter's **Legacy role metadata** section for `tier` versus retained license evidence
and optional `memory`/`model` hints. Dropping a native field is not proof that all
surfaces lack the facility; retaining one is not proof of an observed run. Attribution
and notices for known derivatives remain in source and body links, not in an inferred
license grant from `tier: permissive`.

Tool scope: each generated canonical agent profile carries that agent's declared `tools`
subset, such as `Read, Grep, Glob, Bash`. GitHub documents these names as tool aliases;
the source declaration does not prove how a particular live surface enforces it.
The orchestration profile `lintel-reviewer` declares only the documented `read, search`
aliases, with no edit or shell declaration. `lintel-planner` and `lintel-builder` keep
their existing unrestricted declaration (no `tools` field); their planning/artifact and
implementation needs are unchanged. No canonical agent tool list is narrowed or expanded.

The planner reports trio paths and open decisions; the builder reports actual changes
and checks; the reviewer returns source-bound findings/limits without source edits.
The authorized coordinator supplies the prepared review context and records the actual
reviewer's returned decision through the shared evidence contract. Missing context or
recording ability stays unverified, not fabricated clearance or permission to acquire
write/shell tools. Independent review still requires a separate attributable context.
Generator tests verify emitted configuration only. Actual permitted-tool enforcement
must be observed separately per client/version; neither a role name nor these bytes
establish a live read-only boundary.

## Tool and workflow adaptation

Read the shared Universal contract at `shims/universal/ADAPTER.md` in the source checkout,
or `ADAPTER.md` beside this file in an installed bundle. The canonical registry
`lib/cli-tiers.yaml` separates vendor, delivered and observed facts per surface. Inspect
actual tools and permissions; `bin/li-client-capabilities.py resolve` selects declared
bindings but never executes tools or clears independent review.

The generated preamble maps canonical tool names to the Copilot CLI runtime tools that
GitHub's hooks reference documents. Other surfaces can name their tools differently;
bind the tool the host actually offers.

- `Read`=`view`, `Write`=`create`, `Edit`=`edit`, `Grep`=`grep`, `Glob`=`glob`: the
  host's file-reading, editing and search tools.
- `Bash`=`bash` or `powershell`: an approved terminal tool; identify missing Bash/Python
  dependencies. Run a skill's Bash snippet through `bin/li-run`, described below.
- `TodoWrite`: keep checkboxes and status in `.claude/plans/todo.md` and the initiative plan.
- `AskUserQuestion`=`ask_user`: the host's actual question tool, only when information
  or authorization is missing. Use conversation only when no question tool exists;
  never route around a denied permission.
- `Task` or a named role=`task` with that custom agent: use available native subagent
  delegation. Copilot CLI, VS Code and cloud have different capabilities; never invent a
  tool or claim a delegated run happened. Without attributable parallel isolation,
  serialize. Without delegation, preserve a usable external/manual brief and label
  self-review accurately; required independent review stays outstanding.
- `WebFetch`=`web_fetch`: fetch only what the task authorizes.
- `/li:<name>`: invoke the native `/li-<name>` skill; generated bodies already use that
  spelling. Read the canonical skill file only when the surface does not discover the
  skill. Native skill names contain hyphens, not a colon namespace.
- Claude-specific model names, context commands, plugin syntax, `voice` metadata,
  hook APIs and Codex-only operations are host-specific examples. Use available
  equivalents and report unsupported behavior. Do not force a particular model.

`bin/li-run` runs one Bash step with the Lintel environment prepared. Save the snippet
to a temporary `.sh` file and run `bash "<resource-root>/bin/li-run" <file>`, or pass `-`
to read the step from standard input. `--repo <dir>` selects the working repository;
the default is `LINTEL_REPO_ROOT`, then the current directory. The runner sets
`LINTEL_SOURCE_ROOT` to its own source tree and `LINTEL_SKILLS_DIR` to that tree's `skills/`
folder, ignoring inherited values of both, prepares `LINTEL_REPO_ROOT` and the profile
context through `lib/copilot-env.sh`, runs the step in the working repository and exits
with the step's status. It exits 2 for a usage error or a missing script and 1 when the
environment cannot be prepared. It changes no host permissions.

PLAN produces the cold-executor trio under `.claude/plans/<initiative>/`: plan.md,
spec.md and prompt.md. Use the templates under `scaffolding/01-foundation/templates/plan/`
in the resource root. Give each build card requirements, dependencies, changed files,
acceptance criteria and a verification command. A plan starts as draft unless the user
already authorized execution; record that authorization rather than asking again.

BUILD executes each authorized card, records real test output, and obtains spec and
quality review. Use a different subagent for independent review when available. The
cloud agent should leave changes in its pull request for normal repository review;
do not bypass branch rules, approvals or required checks.

SHIP does not imply deployment or permission to push main. Confirm that the requested
action is within the existing user authorization and host policy. Never substitute
"tests passed" for testing a real Copilot session: report which layer was verified.

## Hooks and trust

This kit installs no hooks, MCP servers, credentials, permission overrides, automatic
tool approvals or model configuration. Lintel's Claude Code hooks have a different
event contract and are not ported by copying their JSON. Read any canonical claims
that hooks "fire automatically" as conditional on a separately verified host adapter.
Perform the applicable policy review explicitly, and describe it as advisory unless
an actual enforcement mechanism was tested. Keep branch protection, required checks
and enterprise access controls as independently managed controls.

## Session acceptance check

1. Start a new session in the repository root after installation or update.
2. Inspect discovered instructions, skills and custom agents in the host UI (CLI:
   `/instructions`, `/skills reload`, `/skills info li-plan`). Ensure project
   instructions also load.
3. Ask `li-plan` for a small change and verify the trio, requirements and build cards.
4. Execute one authorized card with `li-build`; verify tests and a review record.
5. Resume in a fresh session and verify the next card is identified from saved state.

The local `li-copilot check` validates installed files and adapter links. It cannot
prove model behavior, tenant permissions, client discovery or the cloud execution path.
