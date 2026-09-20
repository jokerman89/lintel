# Claude Code

Lintel preserves its Claude-native plugin, canonical skills, specialist agents and hook
adapter. The Universal repository route is additive: it does not replace these methods
or require teammates to use Claude. CLI and Desktop Code local are distinct surfaces;
Chat, Cowork and cloud are not implied.

## Choose a route

The existing Claude Code plugin path is:

```text
/plugin marketplace add jokerman89/lintel
/plugin install li@jokerman-lintel
```

Inspect the installed client's real plugin UI and policies first. The plugin manifest
references canonical `skills/` and `agents/`; namespaced workflows use `/li:<skill>`.
It can register the selected Claude-compatible hooks in `hooks/hooks.json`. Installation
or registration alone is not evidence of actual enforcement.

For a shared **repository-only, hook-free** kit, use a reviewed Lintel checkout:

```bash
python3 bin/li-adapter.py init --client claude-code --target ../your-repo
python3 bin/li-adapter.py check --target ../your-repo
```

Use `claude-desktop` for Desktop Code local. This generates documented
`.claude/skills/li-*/SKILL.md` wrappers and the common `.github/lintel/` source bundle,
plus full startup protocol blocks while preserving existing project prose. It installs
no personal settings, agents, model overrides or hooks. Avoid duplicate plugin and
repository copies unless their precedence is deliberately checked.

## Start and resume a task

Read the project's CLAUDE.md/AGENTS.md and relevant memory/decisions. Inspect discovered
skills; use the host's actual invocation, or explicitly read `.github/lintel/START.md`.
Plan one bounded change, execute authorized cards, record actual checks, obtain independent
review and resume the same committed work map in a fresh session.

Native delegation, worktrees, browser integrations and memory depend on current tools,
version and permissions. A worktree provides change attribution, not a security sandbox.
Optional native agent memory and model configuration remain usable through the Claude
adapter where supported; the canonical role's purpose is not a mandatory model choice.
Repository knowledge and review evidence remain authoritative for cross-host handoff.

## Hooks and acceptance

The bare installer preserves inert hook files. Activating any hook is a separate authorized
host configuration action, not a side effect of welcome or the portable generator.
Check the actual input/event contract, registration, output and limits on a non-sensitive
fixture before relying on a control. Other vendors' hook APIs require their own adapter.

The [registry](../lib/cli-tiers.yaml) records dated official sources and live limits.
Installer tests verify native-format files, source portability and conflict refusal;
they do not validate Claude discovery, model behavior or organizational policy. Record
the exact surface/version, source revision, task and evidence in a real approved pilot.
See [getting started](getting-started.md) and [enterprise adoption](enterprise-adoption.md).
