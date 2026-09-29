# Codex Native Customization Surfaces — Research Report

**Retrieval date:** 2026-09-28. **Codex version observed:** release train `rust-v0.158.0` (stable) / `rust-v0.159.0-alpha.12` / `rust-v0.160.0-alpha.1` (pre-release), per `https://github.com/openai/codex/releases.atom` (fetched 2026-09-28T04:01Z). The in-repo `docs/*.md` files in `openai/codex` are now thin pointer stubs to hosted docs (confirmed by direct fetch), so **the hosted docs at `developers.openai.com/codex/*` and `learn.chatgpt.com/docs/*` are the canonical, current-state reference** — they describe *current released behavior*, not a version-by-version changelog. `developers.openai.com/codex/llms.txt` 302-redirects to `learn.chatgpt.com/docs/llms.txt` (observed directly), i.e. both hostnames serve the same content; citations below use whichever URL was actually fetched successfully.

Primary sources used (all fetched and read directly this session):
- `openai/codex` GitHub repo: `docs/*.md` (pointer stubs), `CHANGELOG.md`, `codex-rs/hooks/*`, `codex-rs/skills/*`, `codex-rs/plugin/*`, `codex-rs/agent-roles/*`, `codex-rs/prompts/*`
- `learn.chatgpt.com/docs/hooks.md`, `.../build-skills.md`, `.../custom-prompts.md`, `.../agent-configuration/{agents-md,subagents}.md`, `.../config-file/{config-advanced,config-reference}.md`, `.../environments/{cloud-environment,modes}.md`, `.../cloud.md`, `.../cli/slash-commands.md`, `.../codex/ide.md`, `.../developer-commands.md?surface=ide`, `.../customization/overview.md`, `.../enterprise/skills.md`, `.../enterprise/chatgpt-work-cloud-security.md`
- `developers.openai.com/plugins/{concepts/skills,build/skills,build/plugins}.md`

No file outside this report was created or modified — this is research only.

---

## (a) Capability matrix

| Feature | CLI | IDE extension | Desktop app (ChatGPT app "Codex") | Codex cloud (chatgpt.com/codex) | Source |
|---|---|---|---|---|---|
| **Agent Skills** (`SKILL.md`, standalone folders) | ✅ full (`$name`, `/skills`) | ✅ (filesystem skills load; no `/skills` browse command listed) | ✅ full | ⚠️ **UNVERIFIED** — not named in the surface list | `learn.chatgpt.com/docs/build-skills.md`; `.../enterprise/skills.md` |
| **Skills bundled in Plugins** | ✅ (CLI plugin browser) | ❌ explicitly excluded | ✅ | ⚠️ UNVERIFIED (doc lists "Chat/Work on web/desktop/mobile", not "Codex cloud" specifically) | `learn.chatgpt.com/docs/enterprise/skills.md` ("They aren't available in the IDE extension") |
| **Plugins** (full: MCP + hooks + apps) | ✅ `codex plugin marketplace …`, `/plugins` | ❌ not available | ✅ Plugins Directory UI | ⚠️ UNVERIFIED | same as above; `developers.openai.com/plugins/build/plugins.md` |
| **Lifecycle Hooks** | ✅ full, `/hooks` review UI, default-on (`[features].hooks=true`) | ⚠️ UNVERIFIED — no `/hooks` in IDE slash-command reference, but config-layer loading is shared core code | ⚠️ UNVERIFIED (same shared core, no explicit doc confirmation) | ⚠️ UNVERIFIED — never mentioned in cloud docs | `learn.chatgpt.com/docs/hooks.md`; `.../developer-commands.md?surface=ide` (no `/hooks`) |
| **Custom subagents** (`.codex/agents/*.toml`) | ✅ full, `/agent`,`/subagents` | ✅ ("background-agent panel… when available") | ✅ thread panel | ⚠️ UNVERIFIED — subagents doc's "web" tag = ChatGPT Work chat, not confirmed same as Codex-cloud async tasks | `learn.chatgpt.com/docs/agent-configuration/subagents.md` |
| **AGENTS.md** | ✅ | ✅ (shared core discovery) | ✅ | ✅ **confirmed**: "If your repo includes `AGENTS.md`, the agent uses it to find project-specific lint and test commands" | `learn.chatgpt.com/docs/environments/cloud-environment.md` |
| **Custom prompts** (`~/.codex/prompts/*.md`) — **deprecated** | ✅ `/prompts:name` | ✅ `/prompts:name` | ⚠️ UNVERIFIED (doc only names CLI + IDE) | ❌ (home-directory-local by design, not repo-shared) | `learn.chatgpt.com/docs/custom-prompts.md` |
| **Environment/setup scripts** | n/a (local) | n/a (local) | n/a (local) | ✅ setup script + maintenance script, `codex-universal` image | `learn.chatgpt.com/docs/environments/cloud-environment.md` |

Legend: ✅ = explicitly confirmed by a primary source; ❌ = explicitly excluded by a primary source; ⚠️ UNVERIFIED = no primary-source statement found either way (see section (d)).

---

## 1. Agent Skills

### Discovery locations (exact, source-confirmed)
This is the single most important correction versus generic web chatter: **the repo-level directory is `.agents/skills`, not `.codex/skills`.**

| Scope | Exact path | Notes |
|---|---|---|
| `REPO` | `$CWD/.agents/skills` | cwd where Codex launched |
| `REPO` | `$CWD/../.agents/skills` | parent of cwd, inside a git repo |
| `REPO` | `$REPO_ROOT/.agents/skills` | git root |
| `USER` | `$HOME/.agents/skills` | personal, cross-repo |
| `ADMIN` | `/etc/codex/skills` | machine/container-wide |
| `SYSTEM` | bundled with Codex by OpenAI | e.g. `skill-creator`, plan skill |

Source: `learn.chatgpt.com/docs/build-skills.md` (section "Where Codex loads local skills"). Symlinked skill folders are supported and followed. If two skills share a `name`, Codex does **not** merge them — both appear in selectors (same source). Curated skills can also be pulled in with `$skill-installer <name>` (e.g. `$skill-installer linear`), and the reference catalog lives at `github.com/openai/skills` (curated examples: `skills/.curated/gh-fix-ci`, `.../pdf`, `.../linear`).

### SKILL.md frontmatter — fields actually honored
Verified directly from the parser source, the `openai/codex` repository file `codex-rs/skills` crate, `src` directory, `parser.rs`:
```rust
#[derive(Debug, Deserialize)]
struct SkillFrontmatter {
    #[serde(default)] name: Option<String>,
    #[serde(default)] description: Option<String>,
    #[serde(default)] metadata: SkillFrontmatterMetadata,   // only sub-field: short-description
}
```
- **Only `name`, `description`, and `metadata.short-description` are parsed.** `name` ≤ 64 chars (`MAX_NAME_LEN`), `description` required non-empty.
- The struct has **no `#[serde(deny_unknown_fields)]`**, so any extra frontmatter keys (e.g. a Claude-Code-style `allowed-tools:`) are **silently ignored**, not errors — but they also have **zero effect**. There is no Codex-native tool-allowlist field in `SKILL.md` itself.
- Optional **`agents/openai.yaml`** (sits inside the skill folder) adds Codex/ChatGPT-specific metadata, parsed into `SkillMetadata`/`SkillInterface`/`SkillDependencies`/`SkillPolicy` (the `openai/codex` `codex-rs/skills` crate, `src` directory, `model.rs`):
```yaml
interface:
  display_name: "Optional user-facing name"
  short_description: "Optional user-facing description"
  icon_small: "./assets/small-logo.svg"
  icon_large: "./assets/large-logo.png"
  brand_color: "#3B82F6"
  default_prompt: "Optional surrounding prompt to use the skill with"
policy:
  allow_implicit_invocation: false     # default true; false = explicit-only ($skill invocation)
dependencies:
  tools:
    - type: "mcp"
      value: "openaiDeveloperDocs"
      description: "OpenAI Docs MCP server"
      transport: "streamable_http"
      url: "https://developers.openai.com/mcp"
```
Source: `learn.chatgpt.com/docs/build-skills.md`; struct fields cross-checked against `SkillInterface`/`SkillPolicy`/`SkillToolDependency` in `model.rs`.

### Minimal working SKILL.md
```
my-skill/
├── SKILL.md          # required
├── scripts/          # optional: executable code
├── references/       # optional: docs/background
├── assets/            # optional: templates
└── agents/openai.yaml # optional: UI + policy + tool deps
```
```md
---
name: skill-name
description: Explain exactly when this skill should and should not trigger.
---

Skill instructions for ChatGPT or Codex to follow.
```
Source: `learn.chatgpt.com/docs/build-skills.md`.

### Invocation and body injection (the key finding for Lintel)
- **Explicit**: `$skill-name` in Codex composer (ChatGPT uses `@skill-name`); CLI/IDE also support `/skills` to browse (CLI slash-command table lists `/skills`: "Browse and use skills").
- **Implicit**: model matches user request against `description` (unless `policy.allow_implicit_invocation: false`).
- **Progressive disclosure, not "go read this file"**: "ChatGPT and Codex start with each skill's name and description, then load the full `SKILL.md` instructions when they decide to use that skill." **"When Codex selects a skill, it still reads the full `SKILL.md` instructions for that skill."** This means Codex's own mechanism *injects the full body automatically upon selection* — it is not a pointer the model must independently decide to open. Source: `learn.chatgpt.com/docs/build-skills.md`.

### Documented size limits
- Skill `name`: **64 characters max** (source: `parser.rs`, `MAX_NAME_LEN`).
- **Initial skill list** (name+description+path shown to the model before selection) is capped at **2% of the model's context window, or 8,000 characters if the context window is unknown**. If many skills are installed, Codex shortens descriptions first, then may omit skills entirely with a warning. Source: `build-skills.md`.
- **No documented byte/line limit on the `SKILL.md` body itself** once a skill is selected — UNVERIFIED (not found in any fetched primary source; Lintel's canonical files may still be too large for this budget even though Codex does read the whole file, since it competes with the rest of context).

### Bundled scripts/resources
`scripts/`, `references/`, `assets/` are conventional subfolders; `SKILL.md` prose must explicitly tell the model when/how to load or run them ("Reference supporting files from `SKILL.md` and explain when to load or run them. Do not add a script when instructions and existing tools can complete the task reliably." — `developers.openai.com/plugins/build/skills.md`).

### Enable/disable without deleting
```toml
# ~/.codex/config.toml
[[skills.config]]
path = "/path/to/skill/SKILL.md"
enabled = false
```
Restart required. Source: `build-skills.md`.

---

## 2. Hooks

### Feature flag / maturity
Hooks are **enabled by default**, not experimental: `[features] hooks = true` (canonical key `hooks`; deprecated alias `codex_hooks` still works — implying an earlier internal/experimental name that was later renamed). Admins force-disable via `requirements.toml` `[features].hooks = false`. Source: `learn.chatgpt.com/docs/hooks.md`.

### Config locations (four canonical, all loaded and merged)
- `~/.codex/hooks.json`
- `~/.codex/config.toml` (inline `[hooks]` tables)
- `<repo>/.codex/hooks.json`
- `<repo>/.codex/config.toml`

Plus: plugin-bundled `hooks/hooks.json` (or manifest override), and enterprise `requirements.toml` managed hooks. **Project-local hooks load only when the project `.codex/` layer is trusted**; user/system hooks load regardless of trust. If a layer has both `hooks.json` and inline `[hooks]`, Codex loads and merges both, with a startup warning. Source: `learn.chatgpt.com/docs/hooks.md`, `.../config-file/config-advanced.md`.

### Complete event list (12 events, source-confirmed against `HookEventName` enum usage in `openai/codex:codex-rs/hooks/src/declarations.rs` and the generated schemas in `codex-rs/hooks/schema/generated/`)

| When | Events |
|---|---|
| During a turn | `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStop`, `Stop` |
| Interrupt | `Interrupt` (main thread only, not subagents) |
| Session/subagent start | `SessionStart`, `SubagentStart` |
| Main thread end | `SessionEnd` (not subagents) |

Generated JSON Schema files exist per event, e.g. `pre-tool-use.command.{input,output}.schema.json`, `session-start.*`, `stop.*`, `subagent-start.*`, `subagent-stop.*`, `user-prompt-submit.*`, `pre-compact.*`, `post-compact.*`, `post-tool-use.*`, `permission-request.*`, `interrupt.*`, `session-end.*` — full directory listing confirmed at `openai/codex:codex-rs/hooks/schema/generated/`.

### Config shape (`hooks.json`)
```json
{
  "description": "Optional lifecycle hooks for this workspace.",
  "hooks": {
    "SessionStart": [
      { "matcher": "startup|resume",
        "hooks": [ { "type": "command", "command": "python3 ~/.codex/hooks/session_start.py",
                     "statusMessage": "Loading session notes", "additionalContextLimit": 5000 } ] } ],
    "PreToolUse": [
      { "matcher": "^Bash$",
        "hooks": [ { "type": "command", "command": "python3 .../pre_tool_use_policy.py", "timeout": 30 } ] } ]
  }
}
```
Equivalent TOML:
```toml
[[hooks.PreToolUse]]
matcher = "^Bash$"
[[hooks.PreToolUse.hooks]]
type = "command"
command = '/usr/bin/python3 ".../pre_tool_use_policy.py"'
timeout = 30
statusMessage = "Checking Bash command"
```
Source: `learn.chatgpt.com/docs/hooks.md`.

### Handler `type`s
`command` and `mcp_tool` are executed; **`prompt` and `agent` are parsed but currently skipped** (confirmed in both docs and `openai/codex:codex-rs/hooks/src/declarations.rs` test fixture, which constructs `HookHandlerConfig::Prompt {}` and `HookHandlerConfig::Agent {}` variants). `mcp_tool` handler fields: `server` (required), `tool` (required), `input` (template object, supports `${field.nested}` expansion), `timeout` (default 600s).

### Common input fields (every command hook, stdin JSON)
`session_id` (string), `transcript_path` (string|null), `cwd` (string), `hook_event_name` (string), `model` (string, Codex extension). Turn-scoped events add `turn_id` (Codex extension). Most events add `permission_mode`: `default|acceptEdits|plan|dontAsk|bypassPermissions`.

### PreToolUse — exact schema (verified against the generated JSON Schema)
Input (`openai/codex:codex-rs/hooks/schema/generated/pre-tool-use.command.input.schema.json`): required `cwd, hook_event_name(const "PreToolUse"), model, permission_mode, session_id, tool_input, tool_name, tool_use_id, transcript_path, turn_id`.
Output (`.../pre-tool-use.command.output.schema.json`): optional `continue(bool,default true), decision("approve"|"block"), hookSpecificOutput{hookEventName, additionalContext, permissionDecision("allow"|"deny"|"ask"), permissionDecisionReason, updatedInput}, reason, stopReason, suppressOutput, systemMessage`.

**Blocking mechanisms** (all three are equivalent and Codex-wide, not just `PreToolUse`):
1. Exit code **`2`** + write the reason to `stderr`.
2. Legacy block shape: `{"decision": "block", "reason": "..."}`.
3. Structured shape: `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}`.

**Rewriting a call without blocking** (`PreToolUse` only): `{"hookSpecificOutput": {"hookEventName":"PreToolUse", "permissionDecision":"allow", "updatedInput": {"command": "echo rewritten"}}}` — `updatedInput.command` (string) for Bash/`apply_patch`, or a full replacement args object for MCP/other tools.

**Non-blocking context injection**: `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "..."}}` — this is the general mechanism (`additionalContext`) used by `SessionStart`, `UserPromptSubmit`, `SubagentStart`, `PreToolUse`, `PostToolUse` alike. Plain text on `stdout` is also treated as `additionalContext` for `SessionStart`/`UserPromptSubmit`/`SubagentStart` (but *ignored* for `PreToolUse`/`PostToolUse`/`PermissionRequest`, which require the JSON shape).

Source: `learn.chatgpt.com/docs/hooks.md` + `openai/codex:codex-rs/hooks/schema/generated/pre-tool-use.command.{input,output}.schema.json`.

### Other events — condensed reference (all confirmed in `hooks.md`)
| Event | matcher filters | Key input fields | Key output behavior |
|---|---|---|---|
| `SessionStart` | `source`: `startup\|resume\|clear\|compact` | `source` | `additionalContext`; runs again after compaction with `source:"compact"` |
| `SessionEnd` | `reason` (only `"other"` today) | `reason` | advisory only, always sync, no `async` |
| `SubagentStart` | `agent_type` | `agent_id, agent_type, permission_mode` | `additionalContext` for the subagent; `continue:false` parsed but ignored |
| `PermissionRequest` | tool name (`Bash`,`apply_patch`*,MCP) | `tool_input.description` | `decision.behavior: "allow"\|"deny"` (deny wins on conflicts); no matching hook ⇒ normal approval prompt |
| `PostToolUse` | tool name | `tool_response` | `decision:"block"` replaces tool result with feedback (can't undo side effects); `continue:false` also replaces result |
| `PreCompact`/`PostCompact` | `trigger`: `manual\|auto` | `trigger` | `continue:false` stops compaction (PreCompact) |
| `UserPromptSubmit` | not supported | `prompt` | `additionalContext`; block via `decision:"block"` + `reason`, or exit 2 |
| `SubagentStop` | `agent_type` | `agent_transcript_path, stop_hook_active, last_assistant_message` | `decision:"block"` continues the subagent with `reason` as new instruction |
| `Stop` | not supported | `stop_hook_active, last_assistant_message` | `decision:"block"` → Codex auto-creates a continuation prompt from `reason` (does **not** reject the turn) |
| `Interrupt` | ignored | `turn_id, permission_mode` | 1s default/3s max timeout; can't prevent the interruption |

### Matcher syntax
Regex string; `"*"`, `""`, or omitted = match everything (where supported). Aliases: `apply_patch` also matches `Edit`/`Write` (hook input still reports `tool_name:"apply_patch"`); shell + unified-exec both report as `Bash`; MCP tools as `mcp__server__tool` (wildcard `mcp__filesystem__.*` works); other local function tools by name (e.g. `update_plan`); `spawn_agent` also matches alias `Agent`. **Hosted tools (e.g. `WebSearch`) never go through the hook path at all.**

### Timeouts
Default `600` seconds for `command`/`mcp_tool` handlers; `SessionEnd`/`Interrupt` default to `1`s, capped at `3`s. `commandWindows` (`command_windows` in TOML) is a Windows-only command override.

### Large output handling
Model-visible hook output capped at ~2,500 tokens per handler (`additionalContextLimit`, default omitted = 2500; `0` = unlimited/pass full text; overflow is "spilled" to `<temp_dir>/hook_outputs/<session_id>/<uuid>.txt` with a head/tail preview).

### Background hooks
`"async": true` runs a command hook without blocking; delivered at the next safe point; max **8 concurrent** background hooks per session; cancelled/discarded at session end; `SessionEnd` always runs synchronously regardless of `async`.

### Trust/approval and Windows/enterprise
- CLI `/hooks` inspects sources, reviews new/changed hooks (hash-based trust — changing a hook re-triggers review), trusts/disables individual non-managed hooks.
- `--dangerously-bypass-hook-trust` CLI flag bypasses persisted trust for one invocation.
- **Managed hooks** (`requirements.toml` `[hooks]`) are pre-trusted and cannot be disabled by users; `allow_managed_hooks_only = true` (top-level in `requirements.toml` only, **not** `config.toml` — confirmed by `openai/codex:docs/config.md` pointer stub) ignores user/project/session/plugin hooks entirely. `managed_dir` (macOS/Linux) / `windows_managed_dir` (Windows) hold the actual scripts, distributed by enterprise MDM, not by Codex.
- **Windows**: `commandWindows`/`command_windows` per-handler override; `windows_managed_dir` for managed hooks.

### Claude Code compatibility
- **Environment variables for plugin hook scripts**: Codex sets both its own `PLUGIN_ROOT`/`PLUGIN_DATA` **and**, for compatibility, `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA`.
- A **legacy-compatible marketplace path** `$REPO_ROOT/.claude-plugin/marketplace.json` is recognized alongside the native `.agents/plugins/marketplace.json`.
- **Codex does not appear to directly read `.claude/settings.json` hooks at runtime.** The only documented bridge is the CLI `/import` slash command: **"Import Claude Code or Cursor setup, projects, and chats — Migrate supported external-agent artifacts into Codex configuration and local files."** (`learn.chatgpt.com/docs/cli/slash-commands.md`). Whether `/import` specifically converts Claude Code hooks (vs. just MCP servers/memories/projects) is **UNVERIFIED** — the doc snippet retrieved didn't enumerate exactly which artifact types `/import` migrates.

---

## 3. Plugins

### Two manifest forms
1. **Portable "Agent Plugins" package** — root `plugin.json` conforming to `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`, with OpenAI-specific fields under an `extensions.com.openai` key.
2. **Legacy/compatibility form** — `.codex-plugin/plugin.json`, "remain supported as a compatibility fallback" (this is what `@plugin-creator`/`$plugin-creator` still scaffolds today).

Source: `developers.openai.com/plugins/build/plugins.md`.

### Exact manifest fields (verified from `openai/codex:codex-rs/plugin/src/manifest.rs`, the parsed/normalized in-memory form used regardless of which JSON file supplied it)
```rust
pub struct PluginManifest<Resource> {
    pub name: String,
    pub version: Option<String>,
    pub description: Option<String>,
    pub keywords: Vec<String>,
    pub paths: PluginManifestPaths<Resource>,       // skills, onboarding_skill, mcp_servers, apps, hooks
    pub interface: Option<PluginManifestInterface<Resource>>,
}
pub struct PluginManifestPaths<Resource> {
    pub skills: Vec<Resource>,
    pub onboarding_skill: Option<Resource>,
    pub mcp_servers: Option<PluginManifestMcpServers<Resource>>,   // Path(file) | Object(inline)
    pub apps: Option<Resource>,
    pub hooks: Option<PluginManifestHooks<Resource>>,              // Paths([..]) | Inline([..])
}
pub struct PluginManifestInterface<Resource> {
    pub display_name, short_description, long_description, developer_name,
        category: Option<String>,
    pub capabilities: Vec<String>,
    pub website_url, privacy_policy_url, terms_of_service_url: Option<String>,
    pub default_prompt: Option<Vec<String>>,
    pub brand_color: Option<String>,
    pub composer_icon, logo, logo_dark: Option<Resource>,
    pub screenshots: Vec<Resource>,
}
```
**Components a plugin can bundle**: skills (`skills/` dir or manifest `skills` path), one MCP-server config (`mcp.json`/`.mcp.json`), one "apps" registration file (`.app.json`), lifecycle hooks (`hooks/hooks.json` by default, or manifest `hooks:` = a `./`-prefixed path, array of paths, an inline hooks object, or array of inline hooks objects). **There is no manifest field for subagents or custom prompts** — plugins in the current schema cannot bundle `.codex/agents/*.toml` custom agents or `~/.codex/prompts/*.md` prompt files; only skills/MCP/apps/hooks are first-class plugin components. This is directly relevant to Lintel's ~60 subagent roles — they cannot ship as plugin components today (see open questions).

### Minimal working plugin
```
my-first-plugin/
├── plugin.json
└── skills/  (one folder per skill, for example a "hello" folder holding SKILL.md)
```
```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "my-first-plugin",
  "version": "1.0.0",
  "description": "Reusable greeting workflow"
}
```
Source: `developers.openai.com/plugins/build/plugins.md`.

### Discovery paths inside the plugin
- Skills: `skills/<skill-name>/SKILL.md` (portable packages default to root `skills/`; legacy manifest sets `"skills": "./skills/"` explicitly).
- Hooks: `hooks/hooks.json` by default; manifest `hooks` field overrides (paths must stay inside the plugin root).
- MCP: `.mcp.json` (legacy) / `mcp.json` (portable, declares transport `type` per server — "Don't just rename `.mcp.json`").
- Apps/UI registration: `.app.json`.

### Environment variables for plugin hook scripts
`PLUGIN_ROOT` (Codex extension, installed plugin root), `PLUGIN_DATA` (Codex extension, writable data dir), plus `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA` for Claude-Code-plugin compatibility. Source: `learn.chatgpt.com/docs/hooks.md`.

### Install / update mechanisms
- **Marketplace catalogs** (JSON): repo `$REPO_ROOT/.agents/plugins/marketplace.json`, personal `~/.agents/plugins/marketplace.json`, legacy-compat `$REPO_ROOT/.claude-plugin/marketplace.json`.
```json
{
  "name": "local-example-plugins",
  "interface": { "displayName": "Local Example Plugins" },
  "plugins": [
    { "name": "my-plugin",
      "source": { "source": "local", "path": "./plugins/my-plugin" },
      "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
      "category": "Productivity" }
  ]
}
```
  `source.source` can be `local`, `url` (git, plugin at repo root), `git-subdir` (`{url, path, ref|sha}`), or `npm` (`{package, version?, registry?}`).
- **CLI**: `codex plugin marketplace add owner/repo[@ref] [--ref X] [--sparse PATH]`, `codex plugin marketplace list|upgrade [name]|remove name`.
- **UI**: `/plugins` slash command (CLI) to browse/install/manage; ChatGPT desktop app "Plugins Directory".
- **Per-project enable/disable**: `.codex/config.toml`:
```toml
[plugins."my-plugin@local-repo"]
enabled = true
```
  key = `plugin-name@marketplace-name`.
- Installed plugins cache at `~/.codex/plugins/cache/$MARKETPLACE_NAME/$PLUGIN_NAME/$VERSION/` (`$VERSION` = `local` for local-source plugins).
- Enterprise: `codex plugin` marketplaces can also be defined centrally in system `config.toml`/managed config (`developers.openai.com/codex/enterprise/managed-configuration`), and workspace-level plugin import/sync is separate (`learn.chatgpt.com/docs/enterprise/plugin-management.md`).

Source for this whole subsection: `developers.openai.com/plugins/build/plugins.md`.

### Namespacing
The manifest doc states plainly: **"Use a stable plugin `name` in kebab-case. Plugin hosts use it as the plugin identifier and component namespace."** (`developers.openai.com/plugins/build/plugins.md`). The *exact* invocation syntax for a namespaced plugin skill (e.g., whether it's addressed as `$plugin-name` vs. a compound name) is **UNVERIFIED** — not spelled out in the fetched pages.

### Surface support (explicit)
**"Plugins work in Chat and Work across ChatGPT on the web, desktop, and mobile, in Codex in the ChatGPT desktop app, and through the Codex CLI plugin browser. They aren't available in the IDE extension."** Source: `learn.chatgpt.com/docs/enterprise/skills.md`. Codex-cloud (`chatgpt.com/codex` async tasks) is not named in this list either way — see open questions.

---

## 4. Custom subagents / custom agents

### File format and locations
Standalone **TOML** files (one agent per file), discovered recursively (subdirectories are walked) under:
- `~/.codex/agents/*.toml` — personal/user scope
- `<repo>/.codex/agents/*.toml` — project scope (only loaded when the project `.codex/` layer is trusted, same rule as hooks/config)

Confirmed in source: `openai/codex:codex-rs/agent-roles/src/loader.rs` (`config_folder.join("agents")` per config layer) and `codex-rs/agent-roles/src/discovery.rs` (`collect_agent_role_files` recursively walks subdirectories collecting `*.toml`). Doc source: `learn.chatgpt.com/docs/agent-configuration/subagents.md`.

### Required/optional fields
Per-file required (per docs) / actually enforced (per source):
```rust
#[serde(deny_unknown_fields)]
struct RawAgentRoleFileToml {
    name: Option<String>,              // falls back to filename-derived hint if absent
    description: Option<String>,       // required after precedence resolution (validated in loader.rs)
    nickname_candidates: Option<Vec<String>>,
    #[serde(flatten)] config: ConfigToml,   // developer_instructions + any other config.toml key
}
```
So the file also accepts **any other `config.toml` key**, notably `developer_instructions` (validated non-blank, required for role files with no name hint), `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`.

### Minimal working custom agent
```toml
# .codex/agents/pr-explorer.toml
name = "pr_explorer"
description = "Read-only codebase explorer for gathering evidence before changes are proposed."
model = "gpt-6-luna"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Stay in exploration mode. Trace the real execution path, cite files and symbols,
and avoid proposing fixes unless the parent agent asks for them.
"""

[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
```
Source: `learn.chatgpt.com/docs/agent-configuration/subagents.md` (worked "PR review" example with 3 cooperating custom agents).

### Built-ins and precedence
Built-in agents: `default`, `worker`, `explorer`. A custom agent whose `name` collides with a built-in **takes precedence** over the built-in.

### Global settings (`[agents]` in `config.toml`)
| Key | Type | Default | Purpose |
|---|---|---|---|
| `agents.enabled` | bool | `true` | master on/off for multi-agent tools |
| `agents.max_concurrent_threads_per_session` (legacy alias `agents.max_threads`) | number | Codex default | cap concurrent spawned threads |
| `agents.default_subagent_model` | string | — | default model for spawned agents |
| `agents.default_subagent_reasoning_effort` | string | — | default reasoning effort |
| `agents.interrupt_message` | bool | `true` | record a model-visible note when a subagent turn is interrupted |

Model/effort resolution order: explicit spawn value → `[agents]` default → parent's value → (if a custom-agent file sets only `model`, previously resolved effort is preserved unless the file also sets `model_reasoning_effort`).

### Invocation
- Natural-language delegation request in the prompt ("Spawn `pr_explorer`…", "Review this branch with parallel subagents…").
- Codex also delegates automatically "when applicable `AGENTS.md` or skill instructions request it" (CLI/IDE/app).
- CLI: `/agent` (alias `/subagents`) switches/inspects agent threads; approval overlay lets you press `o` to open the source thread before approving.

### Surface support and sandbox inheritance
- CLI: full, incl. thread switching and approval routing across threads.
- Desktop app: subagent thread panel + a "Subagents" panel with read-only Active/Done lists elsewhere, direct steer/stop via chat.
- IDE extension: "When the background-agent UI is available, active subagents appear above the composer" — conditional/rolling-out language, hence not unconditionally guaranteed.
- ChatGPT Work ("web"): hosted subagents, **no local sandbox/approval concept**, read-only Active/Done panel only.
- Subagents **inherit the parent's current sandbox/approval/permission mode**; a custom agent file's own `sandbox_mode` can be overridden by **live runtime overrides** the user set interactively (e.g. `/permissions`, `--yolo`) — those win over the file's static default.

Source for this subsection: `learn.chatgpt.com/docs/agent-configuration/subagents.md`.

---

## 5. Instructions (AGENTS.md)

### Discovery and merge order (exact algorithm)
1. **Global scope**: in `CODEX_HOME` (default `~/.codex`, overridable via `CODEX_HOME` env var), read `AGENTS.override.md` if present, else `AGENTS.md`. Only the first non-empty file at this level is used.
2. **Project scope**: starting at the project root (nearest ancestor matching `project_root_markers`, default `[".git"]`; set `project_root_markers = []` to disable upward search), walk **down** to the current working directory. In each directory: check `AGENTS.override.md`, then `AGENTS.md`, then any names in `project_doc_fallback_filenames`. At most one file per directory.
3. **Merge**: concatenate root-to-leaf, joined by blank lines. Files closer to cwd win on conflicts because they appear **later** in the combined prompt (not because earlier content is deleted).
4. Empty files are skipped. Concatenation **stops once the combined size reaches `project_doc_max_bytes`** (files not yet added are excluded — the docs phrase this as "stops adding files", implying whole-file granularity rather than mid-file truncation, though the exact mid-file-cutoff edge case is not spelled out — flagged as UNVERIFIED nuance below).

Source: `learn.chatgpt.com/docs/agent-configuration/agents-md.md`.

### `project_doc_max_bytes`
**Default 32 KiB**, configurable in `config.toml`:
```toml
project_doc_max_bytes = 65536   # e.g. raise to 64 KiB
```
Source: `learn.chatgpt.com/docs/agent-configuration/agents-md.md` ("Codex skips empty files and stops adding files once the combined size reaches the limit defined by `project_doc_max_bytes` (32 KiB by default)").

### Fallback filenames
`project_doc_fallback_filenames` — an array config key checked per directory after `AGENTS.override.md`/`AGENTS.md` (exact default list not enumerated in the fetched excerpt — UNVERIFIED whether it's empty by default or includes legacy names like `CLAUDE.md`/`.cursorrules`).

### CLI tooling
`/init` generates an `AGENTS.md` scaffold for the current project (CLI and IDE both list this command). GitHub code-review integration additionally reads a `## Code Review Rules` heading inside the nearest applicable `AGENTS.md` to customize what Codex reviews (`learn.chatgpt.com/docs/third-party/github#customize-what-codex-reviews`, referenced from `agents-md.md`).

---

## 6. Custom prompts / slash commands

**Status: explicitly deprecated.** *"Custom prompts are deprecated. Use skills for reusable instructions that Codex can invoke explicitly or implicitly."* Source: `learn.chatgpt.com/docs/custom-prompts.md`.

- **Location**: `~/.codex/prompts/*.md` — home-directory only, **flat, top-level Markdown files only** ("Codex scans only the top-level Markdown files in that folder... place each custom prompt directly under `~/.codex/prompts/` rather than in subdirectories"). **No project/repo-level support** — "they're not shared through your repository."
- **Frontmatter**: `description` (shown in popup), `argument-hint` (documents expected params, e.g. `[FILES=<paths>] [PR_TITLE="<title>"]`).
- **Argument syntax**: `$1`…`$9` positional; `$ARGUMENTS` = all args; `$NAME` uppercase named placeholders bound via `KEY=value` (quote values with spaces); `$$` emits a literal `$`.
- **Invocation**: `/prompts:<filename-without-.md>`, e.g. `/prompts:draftpr FILES="a.ts b.ts" PR_TITLE="Add hero animation"`.
- Restart Codex (or new chat) to pick up prompt-file edits; non-Markdown files in the directory are ignored.

Minimal example:
```markdown
---
description: Prep a branch, commit, and open a draft PR
argument-hint: [FILES=<paths>] [PR_TITLE="<title>"]
---
Create a branch named `dev/<feature_name>` for this work.
If files are specified, stage them first: $FILES.
Open a draft PR. Use $PR_TITLE when supplied; otherwise write a concise summary yourself.
```
Source: `learn.chatgpt.com/docs/custom-prompts.md`.

---

## 7. Codex cloud specifics

### What's confirmed
- **AGENTS.md applies**: explicitly stated in the cloud-run description — step 4 of "How Codex cloud chats run": *"The agent runs terminal commands in a loop... If your repo includes `AGENTS.md`, the agent uses it to find project-specific lint and test commands."* Source: `learn.chatgpt.com/docs/environments/cloud-environment.md`.
- **Environment setup pipeline**: (1) container created, repo checked out at branch/SHA; (2) setup script runs (+ optional maintenance script on cached-container resume); (3) internet-access policy applied — setup scripts always get internet, agent phase is off by default (configurable to limited/unrestricted, `learn.chatgpt.com/docs/cloud/internet-access.md`); (4) agent loop runs; (5) result + diff shown, PR optional.
- **Default image**: `universal`, pinned versions configurable via "Set package versions"; reference Dockerfile at `github.com/openai/codex-universal`.
- **Env vars vs. secrets**: env vars persist through setup *and* agent phase; **secrets are stripped before the agent phase starts** and are only available to the setup script.
- **Setup scripts run in a separate Bash session** from the agent phase — `export` does not persist; persist via `~/.bashrc` or environment-variable settings instead.
- **Container caching**: up to 12 hours; auto-invalidated by changes to setup/maintenance script, env vars, or secrets; manual "Reset cache" available; shared across a Business/Enterprise workspace's users of that environment.
- **Network proxy**: all outbound traffic passes through an HTTP/HTTPS proxy.
- **Automatic dependency install** for `npm/yarn/pnpm/pip/pipenv/poetry`.

Source for this subsection: `learn.chatgpt.com/docs/environments/cloud-environment.md`, `.../cloud.md`.

### What's NOT confirmed either way (see also section (d))
Skills, hooks, plugins, and custom-agent TOML files are **never mentioned** in the cloud/environment docs retrieved. Because a cloud task does check out the full repository, files like `<repo>/.agents/skills/*` or `<repo>/.codex/agents/*.toml` or `<repo>/.codex/hooks.json` *would physically be present* in the container — but whether the cloud execution harness's config loader actually scans `.agents/`/`.codex/` the way the local CLI/IDE/desktop-app core does is undocumented in every page fetched (`build-skills.md`'s surface list for standalone skills names only "ChatGPT desktop app, Codex CLI, and IDE extension"; `enterprise/skills.md`'s plugin-surface list names "Chat/Work web/desktop/mobile" + "Codex in the ChatGPT desktop app" + "Codex CLI plugin browser" — Codex-cloud is absent from both lists). No page found says "Codex cloud does/doesn't load hooks.json" or "...does/doesn't load `.agents/skills`" explicitly. Marked **UNVERIFIED** below.

Related background (not Codex-cloud itself, but the closest adjacent product): `learn.chatgpt.com/docs/enterprise/chatgpt-work-cloud-security.md` states *"Work Cloud uses the Codex task-execution harness. Work and Codex share core execution and isolation mechanisms, but their available tools, permissions, and administrative controls aren't identical."* — confirming the two are related but explicitly not identical, without detailing which controls differ.

---

## (b) Schema/example index (cross-reference)

All exact schemas and minimal working examples requested are embedded in the numbered sections above; this index maps each artifact to its location for quick lookup:

| Artifact | Exact schema | Minimal example | Section |
|---|---|---|---|
| `SKILL.md` frontmatter | `SkillFrontmatter` Rust struct (`parser.rs`) | `skill-name` example | §1 |
| `agents/openai.yaml` (skill metadata) | `SkillInterface`/`SkillPolicy`/`SkillDependencies` (`model.rs`) | dice-roller MCP-dependency YAML | §1 |
| `hooks.json` / inline `[hooks]` | Generated JSON Schema (`pre-tool-use.command.{input,output}.schema.json`) + per-event field tables | `SessionStart`+`PreToolUse` config | §2 |
| Plugin manifest (`plugin.json` / `.codex-plugin/plugin.json`) | `PluginManifest`/`PluginManifestPaths`/`PluginManifestInterface` (`manifest.rs`) | `my-first-plugin` | §3 |
| Marketplace catalog (`marketplace.json`) | prose fields (`name`, `interface.displayName`, `plugins[].source/policy/category`) | `local-example-plugins` | §3 |
| Custom subagent (`.codex/agents/*.toml`) | `RawAgentRoleFileToml` (`agent_role_config.rs`) | `pr-explorer.toml` | §4 |
| `AGENTS.md` / `AGENTS.override.md` | discovery algorithm + `project_doc_max_bytes`/`project_doc_fallback_filenames`/`project_root_markers` keys | global + payments-override example | §5 |
| Custom prompt (`~/.codex/prompts/*.md`) | `description`/`argument-hint` frontmatter + `$1..$9`/`$ARGUMENTS`/`$NAME`/`$$` syntax | `draftpr.md` | §6 |

---

## (c) Porting notes — Lintel hooks → closest Codex mechanism

| Lintel hook | Closest Codex event | Blocking mechanism | Context-injection mechanism | Feasibility notes |
|---|---|---|---|---|
| **Session-start context digest** | `SessionStart` (matcher `source: startup\|resume\|clear\|compact`) | n/a (informational) | stdout plain text, or JSON `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"..."}}` | Direct 1:1 mapping. Re-fires on `source:"compact"` too, which Lintel's current design probably doesn't have an analog for — bonus coverage. |
| **Pre-tool-use blocker: secrets in edits** | `PreToolUse` with `matcher: "apply_patch\|Edit\|Write"` | Exit code 2 + stderr, **or** `{"decision":"block","reason":"..."}`, **or** `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"..."}}` | `tool_input.command`/patch text is directly inspectable in the hook payload before Codex writes it | Full 1:1 mapping; can even **rewrite** the patch via `permissionDecision:"allow"` + `updatedInput` instead of hard-blocking, which Claude-Code-style hooks in Lintel likely don't support today — an upgrade opportunity. |
| **Secret scanning in shell commands** | `PreToolUse` with `matcher: "Bash"` | same three mechanisms as above | `tool_input.command` (the literal shell command string) | Direct mapping; also covers `exec_command` (unified exec) since it reports as `Bash` too. |
| **Customer-data blocking** | `PreToolUse` (matcher `Bash\|apply_patch\|Edit\|Write` or specific MCP tool names as needed) — for chat-level scanning also add `UserPromptSubmit` | `PreToolUse`: same 3 mechanisms; `UserPromptSubmit`: `{"decision":"block","reason":"..."}` or exit 2 | `additionalContext` on either event to warn without hard-blocking | Needs **two** hooks registered (one per surface: tool calls and prompt submission) since Codex doesn't have one unified "any content" event; `PostToolUse` can additionally catch data that already leaked into a tool *result* (`tool_response`) via `decision:"block"` (replaces the tool result, can't undo side effects). |
| **Blocking direct pushes to main** | `PreToolUse` with `matcher: "Bash"`, inspect `tool_input.command` for `git push` + branch | Exit 2 / `decision:"block"` / `hookSpecificOutput.permissionDecision:"deny"` | n/a | Direct mapping — same pattern as secret scanning, just a different predicate on `tool_input.command`. |
| **Post-edit memory-budget warning** | `PostToolUse` with `matcher: "apply_patch\|Edit\|Write"` | Not a hard block — use non-blocking path: return `systemMessage` (UI warning) and/or `hookSpecificOutput.additionalContext` | `additionalContext` (added as developer context) + `systemMessage` (surfaced as a UI warning) | Full mapping. Note `PostToolUse`'s `decision:"block"` **cannot undo the edit** (side effect already happened) — appropriate for Lintel's "warning" semantics, not a true rollback. |
| **Stop/turn-end "cycle incomplete" warning** | `Stop` | `{"decision":"block","reason":"Cycle still has N open build cards..."}` → Codex auto-generates a continuation prompt from `reason` and keeps going (does *not* reject/undo the turn) | n/a (the `reason` string itself becomes the next-turn instruction) | Good conceptual match for "nag the model to keep going", but it's a **continue-the-turn** mechanism, not a passive warning banner — if Lintel wants a non-blocking FYI instead, just return `systemMessage` and omit `decision`/`continue:false`. Also register `SubagentStop` (parallel field/shape) if cycle checks must also apply inside subagent threads. |
| **Per-prompt cycle-position context injection** | `UserPromptSubmit` | n/a (informational) | Plain stdout text, or `{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"You are on build-card 4 of 9..."}}` | Direct 1:1 mapping — this is exactly what `UserPromptSubmit` is documented for ("Customize prompting when in a certain directory" is a listed use case). |
| **Per-prompt customer-data check** | `UserPromptSubmit` | `{"decision":"block","reason":"..."}` or exit 2 with stderr reason | `additionalContext` if only warning, not blocking | Direct 1:1 mapping; can run in the same hook process as the cycle-position injector if desired (Codex just merges concurrent matching hooks' `additionalContext`). |

**General porting caveats:**
- All hook scripts run as **synchronous child processes** reading one JSON object from **stdin** and writing to **stdout/stderr**, with the documented exit-code/JSON contract above — Lintel's hook scripts need a thin JSON-in/JSON-out (or exit-code) shim per event, not a direct code port, since Codex's schema differs field-for-field from Claude Code's (`tool_name` values, `hookSpecificOutput` wrapper, `permissionDecision` enum names, etc.).
- **Concurrency**: "Multiple matching command hooks for the same event are launched concurrently, so one hook can't prevent another matching hook from starting" — if Lintel currently relies on strict hook *ordering* (e.g., secret-scan must run before customer-data-check), that ordering guarantee does not exist in Codex; each Lintel check should be written as an independent, order-agnostic hook.
- **Trust**: every non-managed hook (i.e., anything not shipped via `requirements.toml`) requires one-time interactive trust via `/hooks` before it runs — a from-scratch Lintel install would need either (a) a one-time onboarding step asking the user to run `/hooks` and trust the generated hooks, or (b) ship as **managed hooks** via enterprise `requirements.toml` if Lintel is deployed org-wide (bypasses per-user trust).
- All the above assumes hook execution is available on the surface Lintel targets — per the capability matrix, this is **confirmed only for CLI**; IDE/desktop/cloud parity is UNVERIFIED (see (d)).

---

## (d) UNVERIFIED items and open questions

1. **Hook execution on IDE extension / desktop app / Codex cloud.** No primary source states hooks *do* or *do not* run outside the CLI. The `/hooks` review command is documented only in the CLI slash-command reference, and the IDE extension's own slash-command reference (`developer-commands.md?surface=ide`) lists no `/hooks`, `/plugins`, `/skills`, or `/agent`/`/subagents` command at all — suggestive but not conclusive, since the underlying config-loading engine (`hooks.json`/inline `[hooks]`) is shared Rust core code across local surfaces. **Action for Lintel**: test empirically in the IDE extension and desktop app before relying on hook enforcement there; do not assume parity with CLI.
2. **Skills/hooks/plugins/custom-agent-TOML support in Codex cloud** (`chatgpt.com/codex` async tasks). Explicitly absent from every surface-support sentence found in `build-skills.md`, `enterprise/skills.md`, and `hooks.md`. The cloud docs only confirm `AGENTS.md`. Given the repo *is* checked out into the cloud container, `.agents/skills` and `.codex/agents/*.toml` files would be physically present, but no statement was found that the cloud harness's loader scans them. **Treat as unsupported until confirmed otherwise.**
3. **"Web" vs. "Codex cloud" terminology overlap.** `agent-configuration/subagents.md` differentiates a `web` surface (= ChatGPT Work chat, hosted subagents) from `app/cli/ide` (local Codex clients); it never uses a distinct "cloud" tag matching the `docs/cloud.md` product (`chatgpt.com/codex`). It is unclear whether "web" in the subagents doc is the same execution surface as "Codex cloud" tasks, a related but distinct product ("ChatGPT Work"), or both. `enterprise/chatgpt-work-cloud-security.md` confirms they are related but explicitly *not* identical, without detailing the differences relevant to skills/hooks/plugins.
4. **`/import` (Claude Code migration) exact scope.** Confirmed to exist ("Import Claude Code or Cursor setup, projects, and chats") but could not verify from the fetched excerpt whether it converts `.claude/settings.json` hooks, `.claude/skills`, or only MCP-server/memory/project artifacts. No evidence Codex reads `.claude/settings.json` directly at runtime without this explicit one-time import step.
5. **Exact namespacing syntax for skills bundled in a plugin.** Manifest doc says plugin `name` is "the component namespace" but doesn't show the literal invocation string (e.g., is a plugin-bundled skill still just `$skill-name`, or `$plugin-name:skill-name`?).
6. **`project_doc_fallback_filenames` default value.** Referenced by name in `agents-md.md` and `config-advanced.md` but its default list (empty? legacy names like `CLAUDE.md`, `.cursorrules`?) was not shown in the fetched excerpts.
7. **Mid-file vs. whole-file truncation at `project_doc_max_bytes`.** Docs say Codex "stops adding files" once the cap is hit, which reads as whole-file exclusion rather than truncating the last file mid-content — but this exact edge case isn't spelled out verbatim.
8. **No SKILL.md body size limit found.** Only the *initial skill list* (name/description/path) has a documented budget (2% of context window / 8,000 chars); no documented cap was found on an individual `SKILL.md`'s own content length once selected.
9. **Precise historical "introduced in version X" data for skills/hooks/plugins/subagents.** OpenAI's docs are current-state references, not versioned changelogs (the hooks page says so explicitly: "The linked `main` branch schemas may include hook fields that are not in the current release. Use this page as the release behavior reference."). No dated/versioned introduction notes were found in the in-repo `CHANGELOG.md` (which itself just points to the GitHub Releases page) or in the small slice of release notes fetchable via `releases.atom` (which only returns the most recent ~3 entries with no further pagination available through the tools used). The deprecated `codex_hooks` config-key alias for `hooks` is *indirect* evidence that hooks existed earlier under a different/experimental name, but that rename could not be dated. **Any specific version number claimed by general web search results for these features (e.g., "hooks landed in 0.5.x") came from non-primary blog aggregators and has been deliberately excluded from this report's citations as unreliable/likely fabricated.**
10. **Feature-flag/experimental status.** Skills: no flag found (always-on). Hooks: on by default (`[features] hooks = true`), not listed under the CLI's `/experimental` toggle (which only covers "Network proxy" and "Prevent sleep while running"). Subagents: on by default (`agents.enabled = true`). Plugins: no general "experimental" flag was found gating installation/use; the only plugin-specific flag located is `features.plugin_sharing` (settable to `false` in `requirements.toml`), which gates **workspace publishing** of a plugin, not plugin installation or use in general. Custom prompts: the only one of these six features on a *sunset* trajectory rather than an experimental/opt-in one — fully implemented and working today but documented as deprecated in favor of skills, with no removal date given in the fetched pages. **Net assessment: skills, hooks, subagents, and plugins are all current, default-on, non-experimental, generally-available features as of the Sept 2026 doc snapshot** — none require an opt-in flag to use.
11. **`extensions.com.openai` parsing bridge.** The docs describe a portable root `plugin.json` with OpenAI-specific fields nested under `extensions.com.openai`, and the *normalized* in-memory `PluginManifest` struct was confirmed in `openai/codex:codex-rs/plugin/src/manifest.rs`. However, a code search for the literal string `"extensions.com.openai"` inside `openai/codex` returned **zero results**, meaning the code that actually reads that key (if it lives in this repo at all) uses a differently-spelled constant, is constructed programmatically, or the parsing/bridging happens server-side (e.g., in the plugin submission/hosting pipeline) rather than in the `codex-rs` client. **Practical implication for Lintel:** until this is confirmed, prefer authoring plugins in the **legacy `.codex-plugin/plugin.json` form**, which is unambiguously what `codex-rs/plugin/src/manifest.rs` and the `@plugin-creator`/`$plugin-creator` scaffold both target today, per `developers.openai.com/plugins/build/plugins.md` ("The current scaffold uses the Codex compatibility layout, not the portable Agent Plugins layout").
12. **Sandboxing of skill `scripts/`.** Not explicitly documented, but structurally implied: a skill's `scripts/` entry is just a file the model runs via a normal shell/`exec` tool call once the skill's instructions tell it to, so it should be subject to the same sandbox policy, approval flow, and `PreToolUse`/`PostToolUse` hooks as any other command — no primary source states this explicitly, so treat it as a reasonable but **unverified inference** rather than a documented guarantee.
13. **Practical budget risk for ~96 Lintel skills.** The initial skill list is capped at "2% of the model's context window, or 8,000 characters when the context window is unknown," with Codex shortening descriptions first and then omitting skills (with a warning) if the budget is still exceeded (`learn.chatgpt.com/docs/build-skills.md`). With ~96 skills, even short one-line descriptions (≈60–80 chars each, plus the file path Codex also lists per skill) will approach or exceed an 8,000-character flat budget quickly, and will very likely exceed 2% of context on smaller-context models. This is a first-order risk for a "fully native" Lintel port: **some fraction of the 96 skills may be silently dropped from implicit-invocation consideration** unless descriptions are kept unusually terse or the skill set is pruned/consolidated. No documented per-skill-set count limit beyond this character/percentage budget was found.
14. **`nickname_candidates` field.** Present in the custom-agent-role source (`openai/codex:codex-rs/agent-roles/src/agent_role_config.rs`, `loader.rs`) — validated as a de-duplicated list of ASCII-letters/digits/space/hyphen/underscore strings — but its exact runtime semantics (alternate names the model/user can use to address the same agent? candidate display names Codex randomly assigns to spawned instances?) were not explained in the doc excerpts fetched. Flagged as **UNVERIFIED** pending a dedicated doc section or changelog entry.
15. **GitHub code-search blind spots.** Several `search_code` queries against `openai/codex` (e.g., `".codex/prompts"`, `"extensions.com.openai"`, `discover_prompts`) returned zero hits despite the corresponding behavior being documented in prose, which most likely reflects GitHub code search's indexing/tokenization limits on quoted paths and dotted identifiers rather than the feature being absent from the codebase — these null results were not treated as evidence of non-existence, only as a gap that could not be closed with source-level confirmation in the time available.

### Summary for the Lintel port

The two headline findings that most directly unblock Lintel's stated goal ("ship complete native artifacts instead of tiny pointer files") are:

1. **Skills are genuinely native, not a pointer convention.** Codex's own skill-selection mechanism reads the full `SKILL.md` body into context the moment a skill is chosen — implicitly by `description` match or explicitly via `$skill-name`/`/skills` — so Lintel's ~96 skills can be ported as real `SKILL.md` files (with `references/`, `scripts/`, `assets/`) placed at `$REPO_ROOT/.agents/skills/<name>/SKILL.md` (repo-wide) and/or `$HOME/.agents/skills/<name>/SKILL.md` (personal), **not** at the previously-assumed `.codex/skills`. Only `name`, `description`, and `metadata.short-description` are parsed from frontmatter — anything else (including a Claude-Code-style `allowed-tools:`) is inert.
2. **Hooks are a first-class, default-on Codex primitive with a strictly richer event/decision model than a simple pass/fail script**, covering all nine of Lintel's described lifecycle points via `SessionStart`, `PreToolUse` (×4 for the various blockers), `PostToolUse`, `Stop`, and `UserPromptSubmit` (×2), using `hooks.json`/inline `config.toml` `[hooks]` tables at `~/.codex/` and `<repo>/.codex/`, with three interchangeable blocking mechanisms (exit-code 2, legacy `decision:"block"`, structured `hookSpecificOutput.permissionDecision`) and a dedicated `additionalContext` channel for non-blocking injection — this maps cleanly onto every Lintel hook the task described, per the table in section (c).

The two headline **risks** are: (i) plugins — the only Codex component that can bundle skills + hooks + MCP into one distributable, installable unit — have no manifest slot for subagents or custom prompts, so Lintel's ~60 subagent roles cannot travel inside a single plugin package today and must instead be distributed as raw `.codex/agents/*.toml` files committed to the repo (or a personal `~/.codex/agents/` install step); and (ii) surface parity is genuinely unverified beyond the CLI — plugins are confirmed *excluded* from the IDE extension, and neither skills, hooks, nor plugins are confirmed to run inside Codex cloud tasks at all, so a "fully native, self-contained" integration should be validated empirically on each target surface (CLI, IDE, desktop, cloud) rather than assumed from CLI-centric documentation.

---

## Source index

**Official OpenAI documentation (primary):**
- `https://developers.openai.com/plugins/concepts/skills` (and `.md`)
- `https://developers.openai.com/plugins/build/skills` (and `.md`)
- `https://developers.openai.com/plugins/build/plugins` (and `.md`)
- `https://developers.openai.com/llms.txt`
- `https://developers.openai.com/codex/llms.txt` (redirects to `learn.chatgpt.com/docs/llms.txt`)
- `https://learn.chatgpt.com/llms.txt` / `https://learn.chatgpt.com/docs/llms.txt`
- `https://learn.chatgpt.com/docs/hooks.md`
- `https://learn.chatgpt.com/docs/build-skills.md`
- `https://learn.chatgpt.com/docs/custom-prompts.md`
- `https://learn.chatgpt.com/docs/agent-configuration/agents-md.md`
- `https://learn.chatgpt.com/docs/agent-configuration/subagents.md`
- `https://learn.chatgpt.com/docs/config-file/config-advanced.md`
- `https://learn.chatgpt.com/docs/config-file/config-reference.md`
- `https://learn.chatgpt.com/docs/environments/cloud-environment.md`
- `https://learn.chatgpt.com/docs/environments/modes.md`
- `https://learn.chatgpt.com/docs/cloud.md`
- `https://learn.chatgpt.com/docs/cli/slash-commands.md`
- `https://learn.chatgpt.com/docs/codex/ide.md`
- `https://learn.chatgpt.com/docs/developer-commands.md?surface=ide`
- `https://learn.chatgpt.com/docs/customization/overview.md`
- `https://learn.chatgpt.com/docs/enterprise/skills.md`
- `https://learn.chatgpt.com/docs/enterprise/chatgpt-work-cloud-security.md`

**`openai/codex` GitHub repository (primary source code, commit `44fe510ce3ee61c8ef623adcbf89b901c73ddd61`, `main` branch as of 2026-09-28):**
- `docs/agents_md.md`, `docs/skills.md`, `docs/slash_commands.md`, `docs/config.md`, `docs/sandbox.md` (pointer stubs)
- `CHANGELOG.md`
- `codex-rs/hooks/src/{lib.rs,types.rs,declarations.rs,registry.rs,schema.rs,config_rules.rs,mcp.rs,output_spill.rs}`
- `codex-rs/hooks/schema/generated/pre-tool-use.command.{input,output}.schema.json` (and sibling files for all 12 events, directory listing confirmed)
- `codex-rs/skills/src/{model.rs,parser.rs,loading.rs,selection.rs,invocation.rs,mentions.rs,interface.rs}`
- `codex-rs/plugin/src/{manifest.rs,lib.rs,load_outcome.rs,provider.rs,bundled_hooks.rs}`
- `codex-rs/agent-roles/src/{agent_role_config.rs,loader.rs,discovery.rs,lib.rs}`
- `codex-rs/prompts/src/*` (internal system-prompt crate, distinct from the deprecated user-facing "custom prompts" feature)
- `https://github.com/openai/codex/releases.atom`

**Explicitly excluded from citation** (non-primary, third-party blog aggregators surfaced by web search but not used as evidence for any claim in this report): `doc.jarvisuni.com`, `codex.danielvaughan.com`, `agensi.io`, `ryan-yang125.github.io`, `axiomstudio.ai`, `itecsonline.com`, `codexhandbook.com`, `skillmd.com`, `news.creeta.com`, `releases.sh`, `opentools.ai`, `hackernoon.com`, `proflead.dev`, `simonwillison.net` (used only as a search hit, not cited for any factual claim), `grafsoul.com`, `hashgraph-online/awesome-codex-plugins`.
