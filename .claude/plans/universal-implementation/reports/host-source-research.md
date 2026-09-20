# Official host-source evidence for Universal adapters

Checked 2026-09-20. Sources below are public official documentation, not installed-client
or Lintel execution evidence. A native research agent performed the main bounded source
pass; MasterSession directly checked the additional Antigravity/Kiro/Devin/Junie pages.
No new client installation, credential access or paid model invocation occurred.

## Source-backed surfaces

| Surface | Documented capability / important boundary | Sources |
|---|---|---|
| Claude Code CLI | Skills, subagents, hooks, planning, worktrees; configured Chrome integration is conditional | [overview](https://code.claude.com/docs/en/features-overview), [CLI](https://code.claude.com/docs/en/cli-reference) |
| Claude Desktop Code local | Shared instructions/skills, local worktree sessions, preview and plugin manager; not Chat/Cowork or cloud parity | [desktop](https://code.claude.com/docs/en/desktop) |
| Copilot CLI | Skills, agents/subagents, hooks, instructions/planning/MCP; exact installed APIs still require inspection | [comparison](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/comparing-cli-features) |
| Copilot App | Dedicated worktrees/branches, modes, customization; separate organization policy and cloud boundaries | [app](https://docs.github.com/en/copilot/concepts/agents/github-copilot-app) |
| Copilot VS Code | Skills, delegated agents, hooks, browser and planning; harness-specific support and preview worktrees | [overview](https://code.visualstudio.com/docs/agents/overview), [customization](https://code.visualstudio.com/docs/agents/concepts/customization), [planning](https://code.visualstudio.com/docs/agents/run/planning) |
| Copilot cloud | Ephemeral task environment, custom agents/skills/hooks, Playwright; a cloud task is not nested local delegation | [cloud](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent) |
| Codex CLI | Interactive/headless workflows, skills, subagents, resume, MCP/web search; web search is not browser control | [CLI](https://learn.chatgpt.com/docs/codex/cli.md), [skills](https://learn.chatgpt.com/docs/build-skills) |
| Codex desktop | Current docs identify Codex within ChatGPT desktop; managed Git worktrees and skills, not blanket CLI parity | [desktop](https://learn.chatgpt.com/docs/app.md), [worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees.md) |
| Cursor editor | Questions/browser/rules; plugins package skills/agents/hooks; exact delegation/isolation remains surface-specific | [agent](https://cursor.com/docs/agent/overview), [plugins](https://cursor.com/docs/plugins) |
| Cursor CLI | Interactive/print, Plan/Ask modes and resume/cloud handoff; do not copy editor flags wholesale | [CLI](https://cursor.com/docs/cli/overview) |
| Gemini CLI | Skills, extensions, subagents, Plan; worktrees experimental and browser agent opt-in; no nested subagents | [skills](https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/cli/skills.md), [subagents](https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/core/subagents.md), [CLI](https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/cli/cli-reference.md) |
| OpenCode CLI/TUI | Skills, primary/subagents, Build/Plan, AGENTS.md and question permission; Plan is not unconditional no-write enforcement | [start](https://opencode.ai/docs/), [agents](https://opencode.ai/docs/agents/), [skills](https://opencode.ai/docs/skills/) |
| OpenCode desktop | Official product exists; specific desktop APIs were not established by the general/TUI documentation | [overview](https://opencode.ai/docs/) |
| Factory Droid CLI | Skills, Task/custom droids, hooks, AGENTS.md, Spec Mode/plugins; subagents cannot AskUser or nest Task | [CLI](https://docs.factory.ai/droid-cli/overview), [subagents](https://docs.factory.ai/harness/subagents), [skills](https://docs.factory.ai/harness/skills) |
| Cline editor | Skills and experimental research subagents; subagents are read-only, cannot browser/MCP/edit/nest | [skills](https://docs.cline.bot/customization/skills.md), [subagents](https://docs.cline.bot/features/subagents) |
| Cline CLI | Interactive/headless, Plan/MCP and ask/say outputs; research-subagent restrictions still apply | [CLI](https://docs.cline.bot/usage/cli-overview.md) |
| Continue IDE | Chat/Plan/Agent, rules and tool policy; model/provider tool support matters | [agent](https://docs.continue.dev/ide-extensions/agent/quick-start), [rules](https://docs.continue.dev/customize/rules) |
| Continue CLI | Interactive/headless/read-only/resume, rule and profile configuration; agent profile is not subagent delegation | [CLI](https://docs.continue.dev/cli/quickstart) |
| Aider CLI | Conversation, ask/read-only/load/save, architect/editor and web scraping; neither implies independent subagent review/browser control | [commands](https://aider.chat/docs/usage/commands.html), [usage](https://aider.chat/docs/usage.html) |
| Antigravity desktop/CLI/IDE | Distinct documented discovery roots; desktop/CLI use project `.agents/skills`, CLI has `agy plugin`; do not infer Gemini parity | [skills](https://www.antigravity.google/docs/skills?tab=ide) |
| Kiro CLI/IDE/web | Subagents and parallel contexts documented; custom-agent/permission support varies, shared workspace is not isolated writes | [subagents](https://kiro.dev/docs/custom-agents/subagents/), [skills](https://kiro.dev/docs/skills/) |
| Devin Desktop Cascade | `.windsurf/skills` and optional cross-agent discovery, automatic or @ invocation; Local/CLI uses a different contract | [Cascade skills](https://docs.devin.ai/desktop/cascade/skills), [CLI skills](https://docs.devin.ai/cli/extensibility/skills/overview) |
| Junie CLI/IDE | Open skill bundles on both; CLI discovers `.junie/skills`, trusted `.agents/skills`, extension/configured paths | [skills](https://junie.jetbrains.com/docs/agent-skills.html) |

## What is not established

Every source-only row has observation status `not_run`. Documentation on a project's main
branch is not a released-version test. Exact structured-question APIs, worktree ownership,
permission setup, plugin controls and browser session integration require the intended
surface's actual tool schema. Do not infer missing capability from a source not checked.

No cross-vendor `.disabled` marker is established. Enable/disable/install mechanisms differ.
Model names and tool IDs are adapter bindings, not mandatory canonical role names. Keep
source URL, checked date, conditions and version/revision scope with each claim.

## Observed local evidence in this initiative

Separately from source research, the current Copilot App successfully created four
`lintel-builder` child sessions in distinct Git worktrees at `21261f1`, and one independent
review worktree pinned to `e74849d`. Git worktree enumeration confirmed distinct paths and
branch ownership. This demonstrates local session/worktree delegation in this session,
not complete Lintel client acceptance, organizational enforcement or other-client parity.
The parent used the actual ask_user tool in the earlier account clarification; no generic
tool-name assumption is needed for this host.
