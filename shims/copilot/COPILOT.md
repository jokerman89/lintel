# Lintel adapter for GitHub Copilot

This contract adapts Lintel's canonical workflows to Copilot CLI, VS Code and the
GitHub cloud agent. A workflow is an instruction, not a runtime guarantee. Host
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
Read that file from the resource root and execute it using these same adaptations.
Only load the relevant workflow and references. The portable kit includes canonical
resources, but only the `li-*` skills in `.github/skills/` are native entry points.
Do not claim every catalog workflow has been validated in every Copilot client.

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
locates bundled helpers; `LINTEL_REPO_ROOT` locates the working project.

## Tool and workflow adaptation

- `Read`, `Grep`, `Glob`: use available file-reading and search tools.
- `Write`, `Edit`: use the host's file editing tools.
- `Bash`: use an approved terminal tool; identify missing Bash/Python dependencies.
- `TodoWrite`: keep checkboxes and status in `.claude/plans/todo.md` and the initiative plan.
- `AskUserQuestion`: ask directly only when information or authorization is actually missing.
- `Task` or named agents: use available native subagent delegation. Copilot CLI, VS Code
  and cloud have different capabilities; never invent a tool or claim a delegated run
  happened. If unavailable, execute sequentially and label self-review accurately.
- `/li:<name>`: invoke `/li-<name>` when a native wrapper exists, otherwise read the
  canonical skill file. Native skill names contain hyphens, not a colon namespace.
- Claude-specific model names, context commands, plugin syntax, `voice` metadata,
  hook APIs and Codex-only operations are host-specific examples. Use available
  equivalents and report unsupported behavior. Do not force a particular model.

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
2. Inspect discovered instructions and skills in the host UI (CLI: `/instructions`,
   `/skills reload`, `/skills info li-plan`). Ensure project instructions also load.
3. Ask `li-plan` for a small change and verify the trio, requirements and build cards.
4. Execute one authorized card with `li-build`; verify tests and a review record.
5. Resume in a fresh session and verify the next card is identified from saved state.

The local `li-copilot check` validates installed files and adapter links. It cannot
prove model behavior, tenant permissions, client discovery or the cloud execution path.
