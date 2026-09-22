# Getting started

Start with a bounded task in a pilot repository: a fix, investigation, review or small
feature with a clear acceptance check. Lintel keeps the scope, short build cards, evidence
and handoff usable across coding clients. A global installation or company pack is optional.

## 1. Choose the outcome before the client

Read the project's existing instructions and specifications. Decide what the first task
must demonstrate, for example an endpoint's expected response and failure behavior.
Keep existing work maps and task IDs; Spec Kit does not need a second backlog.

Use the proportionate workflow. A review-only request stays read-only. Small fixes do not
need a venture interview or every phase of the cycle. Optional architecture, data, security,
operations, testing, design and document methods remain available when the task needs them.

## 2. Select a repository adapter

From a reviewed Lintel checkout, inspect the exact CLI, desktop, IDE or cloud surface:

```bash
python3 bin/li-client-capabilities.py list
python3 bin/li-client-capabilities.py show --client codex-cli
```

The report separates dated vendor documentation, delivered discovery/binding and observed
execution. A neighboring surface is not evidence for yours. See [client adapters](client-adapters.md)
for selection, [Copilot](copilot.md) and [Claude Code](claude-code.md) for their preserved routes.

Install only into the intended existing project directory:

```bash
python3 bin/li-adapter.py init --client codex-cli --target ../your-repo
python3 bin/li-adapter.py check --target ../your-repo
```

Substitute the selected surface. Repeat `--client` to share one source bundle across a team:

```bash
python3 bin/li-adapter.py init --client copilot-app --client gemini-cli --target ../your-repo
```

On Windows, use Python 3.9+ through its actual executable, for example:

```powershell
python bin\li-adapter.py init --client copilot-app --target ..\your-repo
python bin\li-adapter.py check --target ..\your-repo
```

Git and Bash are needed by workflows that use them; use Git Bash on Windows. No client,
account, global configuration, model settings, hooks or MCP servers are installed by this
command. Native-format output is written only to the selected documented project root.

If native discovery is unverified, use `--client other`, or the exact manual surface ID.
This installs a **manual canonical-file handoff**, not a native plugin. The same plan,
build, review and resume resources are bundled, so missing discovery does not discard them.

`init` and `check` reuse the Copilot kit's managed inventory, source bundling and full
preflight. The existing `bash bin/li-copilot init|check --target ...` entry is preserved.
`--source PATH` selects a reviewed local source. Updates retain project prose and refuse
conflicting managed files or protocol blocks before writing; do not erase customizations
to force an update. Review and commit the installation diff, including its source revision.
`check` is an integrity check, not client authentication or live workflow acceptance.

## 3. Inspect actual discovery and finish one card

Open the target in the selected client. Inspect the host's actual skills/agent UI under
its trust and organization policies; do not assume a reload command works everywhere.
The portable wrappers are named `li-*`; invocation syntax follows the host. Claude's
preserved plugin names use `/li:<skill>`.

When discovery is absent or uncertain, use the explicit route:

```text
Read .github/lintel/START.md and its Universal adapter. Use the canonical plan workflow
for a health endpoint. Inspect existing routes, tests and project authority. Define
expected behavior, acceptance, affected paths and dependency-ordered short build cards.
```

Confirm the result cites real project files. Review the plan and authorize its intended
scope, then ask the build workflow to implement and verify each card. Use the actual host
question channel for missing decisions, not a vendor-specific tool name.

Obtain an independent review of the relevant content and acceptance. Without a separate
agent, preserve an external/human review handoff; a second role in the same session is not
independent. Without safe attributable write isolation, serialize. Missing browser evidence
stays unverified. Shipping remains bounded by the task's real permissions.

## 4. Resume from repository evidence

Open a fresh session and invoke the discovered `li-resume`, or explicitly read
`.github/lintel/skills/resume/SKILL.md`. It should select the same work map and original
task IDs, cite completed cards and real verification, retain the effective profile reference,
and identify the next action or blocker. It must not need the prior chat or a personal home.

Record the exact client/version, Lintel revision, discovered names, actual tool path, task
result and fresh-session outcome. Mark unrun cases explicitly. This is live pilot evidence,
unlike vendor documentation or a generated-file check.

## Where things live

| Path | Purpose |
|---|---|
| `AGENTS.md`, `CLAUDE.md` | Full shared protocol with preserved project prose |
| Selected native discovery root | Small `li-*` wrappers where documented; none on manual routes |
| `.github/lintel/START.md` | Explicit manual entry on every route |
| `.github/lintel/` | One shared managed source bundle, not a requirement to use Copilot |
| `.github/lintel/manifest.json` | Selected surfaces, owned file hashes and owned protocol blocks |
| `.claude/memory/`, `.claude/plans/`, `.claude/decisions/` | Project-owned durable knowledge, work and decisions |
| `.claude/runtime/` | Gitignored local session state, not installed source |

The historical directory names preserve compatibility. They do not require a particular
vendor. The installer seeds missing project knowledge but does not overwrite later lessons
or plans. Private company packs are not copied; follow the explicit source and identity
contract in [pack resolution](concepts/pack-resolver.md).

## How hook activation works

| Route | Boundary |
|---|---|
| Portable repository adapters, including Copilot and Claude | No hooks installed or activated |
| Claude Code plugin | Selected compatible registrations in `hooks/hooks.json`; verify actual host execution |
| Preserved bare installer | Hook files copied inert; registration is a separate authorized action |
| Other client hook APIs | Vendor capability is not a delivered Lintel hook translation |

Do not copy Claude hook JSON to another client and assume it enforces anything. Required
controls belong in separately configured and verified host policy/CI or an accepted tested
equivalent. See [compliance](compliance.md); a missing mandatory control does not become
an advisory pass.

## Existing routes and troubleshooting

The Copilot native kit/plugin, Claude plugin/skills/agents/hooks, Codex and Cursor manifests,
Gemini extension and OpenCode manual guide remain available. Choose intentionally to avoid
duplicate skills or shadowed project definitions. Global Bash/PowerShell installers still
exist as a separate operator-chosen scope, not a prerequisite or side effect of this path.

For a missing skill, inspect the actual host discovery, trust and permissions, then use a
permitted explicit file read. For an installer conflict, preserve the named path and reconcile
in a reviewed branch. For a missing interpreter, report the failed check rather than claiming
installation success. For a lost plan, locate the selected committed work map, not the newest
file by timestamp. See [enterprise adoption](enterprise-adoption.md) for pilot acceptance.
