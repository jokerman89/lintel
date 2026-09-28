# Research Report: Claude Code Native Customization Surfaces (Sept 2026) — Verification Against Lintel Plugin Layout

## Summary

I verified all six areas against primary sources: **`code.claude.com/docs`** (Anthropic migrated Claude Code docs here; `docs.anthropic.com/en/docs/claude-code/*` and `docs.claude.com/en/docs/claude-code/*` now 301-redirect to `code.claude.com/docs/en/*`) and **`raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md`** (current head at retrieval time: **v2.1.283**). All web lookups were performed **2026‑09‑28**. I cross-checked every finding against Lintel's actual files (`jokerman89/lintel`, branch `jokerman-microsoft-literate-fortnight`). The most consequential discoveries: **all 96 of Lintel's `SKILL.md` files use the field name `tools:` instead of the correct native `allowed-tools:`**, so the intended tool pre-approval has never taken effect; Lintel's plugin agents are **nested in subdirectories, which Claude Code natively supports but folds into the invocation identifier** (`li:engineering:Architect`, not `li:Architect`); Lintel ships a top-level **`bin/`** directory, which is auto-exposed on Claude's `PATH` but **explicitly excludes the plugin from claude.ai/Cowork install**; **AGENTS.md is completely ignored by Claude Code** because a root `CLAUDE.md` also exists (verified Lintel already mitigates this by duplicating, not importing, its shared protocol block); and the hooks surface has grown from Lintel's 5 wired events to **31 native events**, with several high-value ones (PreCompact, SessionEnd, SubagentStop) unused.

---

## Primary sources consulted (retrieved 2026‑09‑28)

| # | URL | Content |
|---|---|---|
| S1 | `code.claude.com/docs/en/plugins` | Plugins overview |
| S2 | `code.claude.com/docs/en/plugins-reference` (= manifest reference) | `plugin.json` fields, standard layout, path rules, env vars |
| S3 | `code.claude.com/docs/en/plugins/components` | Per-component examples ("plugin explorer") |
| S4 | `code.claude.com/docs/en/plugins/marketplace-reference` | `marketplace.json` fields |
| S5 | `code.claude.com/docs/en/plugins/loading` | Load stages, versions/updates, origins |
| S6 | `code.claude.com/docs/en/skills` | Skill discovery, frontmatter, lifecycle |
| S7 | `code.claude.com/docs/en/sub-agents` | Subagent frontmatter, discovery, built-ins |
| S8 | `code.claude.com/docs/en/hooks` | Full hook event list, schemas, exit codes |
| S9 | `code.claude.com/docs/en/hooks-guide` | Hook quickstart/examples |
| S10 | `code.claude.com/docs/en/memory` | CLAUDE.md, AGENTS.md, `.claude/rules/` |
| S11 | `code.claude.com/docs/en/desktop` + `desktop-quickstart` | Claude Desktop / Code tab |
| S12 | `code.claude.com/docs/en/settings-reference` | Settings keys (partial — very large page) |
| S13 | `raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` | Version history (head = 2.1.283) |
| S14 | Local repo files (`jokerman89/lintel`) | Ground truth for gap analysis |

---

## Feature matrix

| Surface | CLI | Desktop Local "Code" | Cloud/Cowork sessions | Primary source |
|---|---|---|---|---|
| Plugins (skills/agents/hooks/MCP/LSP) | ✅ full | ✅ full — same settings files, installable from `+ → Plugins` in-app | ⚠️ partial — no plugin browser; project `.claude/settings.json`-declared and user-scope plugins **don't** load; only `.claude/skills/`-committed skills load | S11 (`desktop.md` "Install plugins"), S5 |
| `bin/` executables on PATH | ✅ | ✅ (Local/SSH) | ❌ — a plugin with a top‑level `bin/` **is refused entirely** by claude.ai/Cowork install | S2 (`plugins-reference` Standard layout, "Executables" row) |
| Skills | ✅ | ✅ (`~/.claude/skills/` loads for Local; SSH reads the *remote* home dir) | Loads claude.ai-synced skills + repo-committed `.claude/skills/` only | S6, S11 |
| Subagents | ✅ | ✅ (same discovery rules) | Same file-based rules apply where the container has the files | S7 |
| Hooks | ✅ | ✅ ("Claude Code fires the same hook events wherever it runs: terminal, IDE extensions, Desktop app, and cloud sessions") | ✅ (fires) but local `~/.claude/settings.json` hooks don't carry over | S8 (Hook lifecycle intro), S6 |
| CLAUDE.md | ✅ | ✅ | ✅ | S10 |
| AGENTS.md (native read) | ✅ v2.1.277+ | ✅ (same engine) | ✅ where no CLAUDE.md shadows it | S10 |
| `.claude/rules/` | ✅ | ✅ | ✅ | S10 |
| Monitors / Workflows / Output styles / Themes / LSP servers | ✅ | ✅ | ⚠️ monitors don't run on Bedrock/Vertex/Foundry; disabled where noted | S2, S3 |
| WSL sessions (Desktop) | — | ❌ **plugins are not available in WSL sessions** on Desktop | n/a | S11 |

---

## Q1 — Plugins

### `plugin.json` fields (complete, from the authoritative field table)
Required: **`name`** only (kebab-case; namespaces every component, e.g. `deploy-tools:reviewer`).

Optional top-level fields: `$schema`, `displayName`, `version` (not semver-checked; pins the plugin), `description`, `author` (`name` required, `email`/`url` optional), `homepage` (must parse as URL), `repository`, `license` (SPDX id), `keywords`, `metadata` (free-form, unread by Claude Code, requires v2.1.222+), `defaultEnabled` (bool, default `true`), `dependencies` (array of `"name"` / `"name@marketplace"` / object), `settings` (object — **only `agent` and `subagentStatusLine` take effect**; a root `settings.json` file takes precedence over this key), `userConfig` (see below), `channels` (message-channel bindings to an MCP server), `skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `outputStyles`, `workflows`, `experimental` (`themes`, `monitors`, `evals`).
Source: S2 (`plugins-reference`, "Fields" table + per-field subsections).

Unrecognized top-level keys are **silently stripped** (warning only from `claude plugin validate`); unrecognized keys *inside* `userConfig`/`channels`/`lspServers`/`monitors` entries **fail validation**. — S2.

### Default component locations (Standard layout table, verbatim)

| Component | Default location | Notes |
|---|---|---|
| Manifest | `.claude-plugin/plugin.json` | optional |
| Skills | `skills/` | one `<name>/SKILL.md` per skill; a bare root `SKILL.md` with no `skills/` also loads as a single skill |
| Commands | `commands/` | flat `.md` files; **docs say "Prefer `skills/` for new plugins"** |
| **Agents** | **`agents/`** | **"Agent Markdown files. Subfolders are part of the agent name."** |
| Hooks | `hooks/hooks.json` | merges with any manifest `hooks` key |
| MCP servers | `.mcp.json` | merges with manifest `mcpServers` |
| LSP servers | `.lsp.json` | merges with manifest `lspServers` |
| Output styles | `output-styles/` | |
| Workflows | `workflows/` | `.js` files |
| Themes | `themes/` | |
| Monitors | `monitors/monitors.json` | background processes, interactive sessions only |
| Executables | `bin/` | **"Files here are on the Bash tool's `PATH` while the plugin is enabled... claude.ai and Cowork don't install a plugin that has this directory"** |
| Settings | `settings.json` | only `agent`/`subagentStatusLine` apply |

Source: S2 (`plugins-reference`, "Standard layout"). A `CLAUDE.md` at the plugin root is **never loaded as context** — `claude plugin validate` warns if one exists; "to include instructions that load into context, put them in a skill." — S2.

### Nested agent discovery — directly answers your question
> "Claude Code scans `.claude/agents/` and `~/.claude/agents/` recursively... Plugin `agents/` directories are also scanned recursively. Unlike project and user scopes, a subfolder inside a plugin's `agents/` directory becomes part of the scoped identifier: a file at `agents/review/security.md` in plugin `my-plugin` registers as `my-plugin:review:security`."
— S7 (`sub-agents.md`, "Choose the subagent scope").

**This is discovery-positive but naming-changing for Lintel.** `agents/engineering/Architect.md` (`jokerman89/lintel:agents/engineering/Architect.md:1-11`) *is* discovered, but its explicit `@`-mention/scoped id is **`li:engineering:Architect`**, not `li:Architect`. (For plain project/user-scope agents, by contrast, the subfolder path is cosmetic only — identity comes solely from the `name:` frontmatter field, and duplicate `name`s anywhere in the tree cause one to silently lose.)

### Namespacing, `${CLAUDE_PLUGIN_ROOT}`, and `${CLAUDE_PLUGIN_DATA}`
- Skill invocation: `/plugin-name:skill-name`. Agent explicit mention: `@agent-my-plugin:security-reviewer`. — S3.
- **Three** path variables (your question about a `${CLAUDE_PLUGIN_DATA}`-style var is answered — it exists exactly as named):

| Variable | Resolves to | Use for |
|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}` | absolute path of the plugin's *installed version* — **changes on every update** | bundled scripts/binaries/config |
| `${CLAUDE_PLUGIN_DATA}` | `~/.claude/plugins/data/<id>/`, created on first reference, **kept across updates** | installed deps (`node_modules`), generated code, caches |
| `${CLAUDE_PROJECT_DIR}` | the *consuming* project's root | project-local scripts/config |

Source: S2 ("Environment variables"). Resolution differs by component (hook `command`/`args`: all three exported as env vars + inline substitution; MCP stdio: root+data only; skill/agent/command Markdown body: inline substitution only, **not** exported as env vars to anything Claude runs via the Bash tool).

### `marketplace.json` fields
Required: `name`, `owner` (`{name, email?, url?}`), `plugins` (array). Optional: `$schema`, `description`, `version`, `metadata.description`/`metadata.version`/`metadata.pluginRoot`, `forceRemoveDeletedPlugins`, `displaceDependenciesOn`, `renames` (former→current name map). — S4.

Plugin-entry fields: `name`, `source` (required); `description`, `version`, `category`, `tags`, `strict` (bool, **default `true`**), `relevance`, `dependencies`, `defaultEnabled`, `displayName`, `metadata`, `headers`, `headersHelper`. — S4.

**Strict mode** (governs what happens when the fetched plugin *also* ships its own `plugin.json`, which is Lintel's case): with `strict: true` (default), the entry's component fields (`commands`/`agents`/`skills`/`hooks`/`outputStyles`/`themes`) are *appended* to `plugin.json`; with `strict: false` (**Lintel's actual setting** — `jokerman89/lintel:.claude-plugin/marketplace.json:15`), any entry component field is a hard **conflict and the plugin fails to load**. Lintel's entry declares no component fields, so this is currently a no-op/safe setting — but it means **Lintel cannot add any component override directly in the marketplace entry** without first flipping `strict` or removing the conflicting field. — S4 ("Strict mode" table).

### Version-gated updates
Plugin id = `<name>@<origin>` (`@<marketplace>`, `@inline`, `@skills-dir`, `@synced`). Three load stages — **Declared** (settings) → **Fetched** (`~/.claude/plugins/{cache,known_marketplaces.json,installed_plugins.json}`) → **Loaded** (running session). Setting `version` in `plugin.json` **pins** it until changed; changes only take effect after `/reload-plugins` or a new session (`claude plugin update` prints "Restart to apply changes."). `github`/`url`/`git-subdir` sources support `sha` pinning (survives upstream branch/tag deletion, on GitHub/GitLab/Bitbucket). — S5, S4 ("Plugin sources").

---

## Q2 — Skills

### Complete frontmatter reference (exact field-name table, hyphenated fields matched literally; unrecognized fields silently ignored)

| Field | Native? | Purpose |
|---|---|---|
| `name` | Yes | command name in `/` menu; defaults to directory name |
| `description` | Recommended | when Claude auto-invokes; defaults to first non-empty body line; combined with `when_to_use` capped at **1,536 chars** |
| `when_to_use` | Yes | extra trigger phrases, appended to `description`, counts toward the same 1,536-char cap |
| `argument-hint` | Yes | autocomplete hint, e.g. `[issue-number]` |
| `arguments` | Yes | **named** positional args for `$name` substitution (space-separated string or YAML list) |
| `disable-model-invocation` | Yes | `true` blocks auto-invocation; also blocks preloading into subagents and scheduled-task firing (v2.1.196+) |
| `user-invocable` | Yes | `false` hides from `/` menu — Claude-only, background knowledge |
| `allowed-tools` | Yes | tools usable without prompting **for the invoking turn only**; clears on next message |
| `disallowed-tools` | Yes | tools removed while skill active; clears on next message |
| `model` | Yes | override for the active turn only (or the forked subagent's model, with `context: fork`) |
| `effort` | Yes | `low`/`medium`/`high`/`xhigh`/`max`, overrides session effort while active |
| `context` | Yes | `fork` → runs in a forked subagent context |
| `agent` | Yes | which subagent type to use, only meaningful with `context: fork` |
| `background` | Yes | with `context: fork` only; `false` waits inline instead of backgrounding (default `true`, v2.1.218+) |
| `hooks` | Yes | hooks registered on invocation, **persist for the rest of the session** (not just the invoking turn) unless `once: true` |
| `paths` | Yes | glob patterns that auto-scope when the skill activates (same syntax as CLAUDE.md path rules) |

Source: S6 ("Frontmatter reference"). Boolean fields accept `yes/no/on/off/1/0` case-insensitively (v2.1.218+) in addition to `true/false`.

### Body injection and `$ARGUMENTS`
The **entire body is injected only when the skill is invoked/loaded** — "unlike CLAUDE.md content, a skill's body loads only when it's used, so long reference material costs almost nothing until you need it." — S6 (overview). Dynamic context injection: a line starting with `` !`command` `` is shell-executed and its output inlined *before* Claude sees the content (e.g. `` !`git diff HEAD` ``) — S6. Named args declared via `arguments:` map to positional `$name` substitutions; the generic form is `$ARGUMENTS` for the raw invocation text (confirmed via the "available string substitutions" reference anchored in S6, alongside `${CLAUDE_PROJECT_DIR}`/`${CLAUDE_SESSION_ID}` placeholders that also resolve in skill bodies).

### Size guidance
No hard limit stated for skill *bodies* (unlike CLAUDE.md's ~200-line guidance), but the docs explicitly warn: "keep the body itself concise… every line is a recurring token cost" once loaded, since content **stays in context across turns** for the rest of the session (S6, "skill-content-lifecycle"). Command-name + description text for **every** auto-invocable skill/agent/command is in context on **every turn**, whether used or not — this is the main plugin "context cost" lever. — S1.

---

## Q3 — Subagents

### Complete frontmatter reference

| Field | Req'd | Notes |
|---|---|---|
| `name` | Yes | unique; **hooks receive this as `agent_type`**; can't contain `:` (v2.1.218+ enforced) |
| `description` | Yes | delegation trigger |
| `tools` | No | comma string or YAML list; inherits all if omitted; use `skills:` (not `Skill` in `tools:`) to preload skill content |
| `disallowedTools` | No | removed from inherited/specified tools |
| `model` | No | `sonnet`/`opus`/`haiku`/`fable`/full id/`inherit` |
| `permissionMode` | No | `default`\|`acceptEdits`\|`auto`\|`dontAsk`\|`bypassPermissions`\|`plan`\|`manual` — **⚠️ ignored for plugin subagents** |
| `maxTurns` | No | caps agentic turns; partial-output marker (v2.1.246+); resumable |
| `skills` | No | preloads **full** skill content (not just description) into context at startup |
| `mcpServers` | No | server refs/inline configs — **⚠️ ignored for plugin subagents** |
| `hooks` | No | lifecycle hooks scoped to the subagent's run — **⚠️ ignored for plugin subagents** |
| `memory` | No | `user`\|`project`\|`local` persistent cross-session learning |
| `background` | No | `true` forces background even if asked to run foreground |
| `omitClaudeMd` | No | skips user/project/local CLAUDE.md (managed policy still loads); v2.1.271+ |
| `effort` | No | `low`\|`medium`\|`high`\|`xhigh`\|`max` |
| `isolation` | No | `worktree` → runs in an isolated git worktree branched from the default branch |
| `color` | No | `red`\|`blue`\|`green`\|`yellow`\|`purple`\|`orange`\|`pink`\|`cyan` — display only |
| `initialPrompt` | No | auto-submitted first turn when run as *main session agent* (`--agent`); ignored for plugin subagents |
| `experimental.cacheTtl` | No | `5m`/`1h` prompt-cache TTL override, v2.1.248+ |

Source: S7 ("Frontmatter reference" table). **Critical, directly-cited caveat repeated twice in the docs**: *"For security reasons, plugin subagents don't support the `hooks`, `mcpServers`, or `permissionMode` frontmatter fields. These fields are ignored when loading agents from a plugin."* — S7.

### Discovery locations & precedence (highest→lowest)
Managed settings (org) → `--agents` CLI flag (session) → `.claude/agents/` (project, walked **up** to repo root) → `~/.claude/agents/` (user) → plugin `agents/` (lowest). Project/user scopes scan **recursively** (subfolders are organizational only there); duplicate `name` in the same directory tree = one silently wins (filesystem read order) — `/doctor` flags this. — S7.

### Invocation
Automatic delegation via `description` matching, or explicit `@agent-<scope>:<name>` (plain) / `@agent-<plugin>:<subfolder-path>:<name>` (plugin, nested). Built-ins: `Explore`, `Plan`, `general-purpose`, `claude` (catch-all), `statusline-setup`, `claude-code-guide`. — S7.

**Lintel-specific verification**: grepping all 30 files under `jokerman89/lintel:agents/**/*.md` for `model:|permissionMode:|isolation:|memory:|maxTurns:|disallowedTools:|mcpServers:` → **zero matches**. Confirmed frontmatter in use (e.g. `jokerman89/lintel:agents/engineering/Architect.md:1-11`) is `name, category, description, color, tools, voice, cli_support, tier` — i.e. only `name`/`description`/`color`/`tools` are native; `category`/`voice`/`cli_support`/`tier` are Lintel's own metadata (harmlessly ignored by Claude Code).

---

## Q4 — Hooks

### Complete current event list (31 events, per the lifecycle table)
`SessionStart`, `Setup`, `UserPromptSubmit`, `UserPromptExpansion`, `PreToolUse`, `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Notification`, `MessageDisplay`, `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `Stop`, `StopFailure`, `TeammateIdle`, `InstructionsLoaded`, `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `PostCompact`, `PreModelSwitch`, `PostModelSwitch`, `Elicitation`, `ElicitationResult`, `SessionEnd`. — S8 ("Hook lifecycle" table). **Lintel currently wires 5**: `SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`, `UserPromptSubmit` (`jokerman89/lintel:hooks/hooks.json:1-70`).

### `PreCompact` — exists, and it can block
`PreCompact` fires "before context compaction," matcher filters on `manual`/`auto`, and **exit code 2 blocks compaction outright** (per the "Exit code 2 behavior per event" table). `PostCompact` fires after, can't block (stderr shown to user only). — S8.

### Context-injection vs. blocking mechanics
- **Exit code 0** + no stdout → no decision, normal flow proceeds. Exit 0 + JSON → the JSON decides (regardless of "0"). **Exit code 1 does *not* block** on its own for almost all events (a common misconception) — only **exit code 2** blocks through the exit code alone, and even a JSON `permissionDecision: "allow"` **cannot override** an exit-2 block. — S8 ("Exit code 2").
- JSON output shape uses `hookSpecificOutput: { hookEventName, permissionDecision: "allow"|"deny"|"ask", permissionDecisionReason }` for tool-gating events, plus universal `systemMessage` (surfaced to the user) and `additionalContext` (injected into the model's context) fields, and `updatedInput` (rewrite tool args). — S8.
- **Full "exit code 2 behavior per event" table** (the parts most relevant to your question):

| Event | Can block via exit 2? | Effect |
|---|---|---|
| `PreToolUse` | Yes | blocks the tool call |
| `UserPromptSubmit` | Yes | blocks + **erases** the prompt |
| **`Stop`** | **Yes** | **"Prevents Claude from stopping, continues the conversation"** |
| `SubagentStop` | Yes | prevents the subagent from stopping |
| `PreCompact` | Yes | blocks compaction |
| `PreModelSwitch` | Yes | blocks the switch |
| `PostToolUse` / `PostToolUseFailure` | No | only shows stderr to Claude — the action already happened |
| `PermissionDenied` / `Notification` / `Setup` | No | exit code ignored entirely |

Source: S8 ("Exit code 2 behavior per event").

**Direct answer to "can a Stop hook safely warn without forcing continuation?"**: Yes — **exit 0** with a `systemMessage`/`additionalContext` in JSON (or even nothing) lets Claude stop normally while still surfacing your message; **only exiting 2** (or emitting an explicit blocking `decision` in the standard model) forces continuation. Lintel's `cycle-incomplete-warn` hook (`jokerman89/lintel:hooks/hooks.json:52-60`) must exit non‑2 to warn-without-blocking — worth an explicit test, since this is exactly the ambiguity the question raises.

### Matcher semantics & tool names
Matcher evaluation: `"*"`/`""`/omitted = all; letters/digits/`_`/`-`/space/`,`/`|` = exact-string set (`Edit|Write`); anything else = unanchored JS regex. Tool names for `PreToolUse`/`PostToolUse`/etc. matchers: exact tool names, e.g. `Bash`, `Edit`, `Write`, `MultiEdit`, `NotebookEdit`, `Read`, **`PowerShell`** (a first-class tool name, matchable as `Bash|PowerShell`), and MCP tools as `mcp__<server>__<tool>` (plugin-bundled: `mcp__plugin_<plugin>_<server>__<tool>`). A separate, more powerful **`if`** field (only on tool events) uses **permission-rule syntax** against tool name *and args together*, e.g. `"Bash(git *)"`, `"Edit(*.ts)"` — richer than `matcher`. — S8.

### Windows execution of `command` strings (definitive answer)
Two forms:
- **Exec form** (`args` present): `command` resolved as a real executable on `PATH`, spawned directly, **no shell**, no tokenization — placeholders substituted as literal strings. **On Windows, exec form requires a true executable (`.exe`)**; `.cmd`/`.bat` shims (npm/npx/eslint in `node_modules/.bin`) **cannot** be spawned this way — invoke the underlying script via `node` instead, or use shell form.
- **Shell form** (`args` omitted, Lintel's pattern): the string is passed to a shell — **`sh -c` (macOS/Linux), Git Bash (Windows), or PowerShell when Git Bash isn't installed**. The `shell` field (`"bash"`|`"powershell"`) picks explicitly.

Source: S8 ("Exec form and shell form", "Command hook fields"). This is the exact primary-source confirmation of the rationale already documented in Lintel's own hooks.json comment (`jokerman89/lintel:hooks/hooks.json:1`, "Shell-string form is used so Windows resolves bash via Claude Code's Git Bash discovery").

### Hooks in skill/subagent frontmatter — lifetime differs by component
- **Subagent-frontmatter hooks**: run only while that subagent executes; removed on completion; a `Stop` hook here is **auto-converted to `SubagentStop`**.
- **Skill-frontmatter hooks**: registered on invocation and **kept running for the rest of the session** (even after the invoking turn) unless `once: true` is set — `once` is **only honored for skill-frontmatter hooks**, ignored elsewhere.
Source: S8 ("Hooks in skills and agents").

### Plugin hook registration
`hooks/hooks.json` **merges** (doesn't replace) with any manifest-declared `hooks` key; all settings-level + plugin hooks **merge across scopes** (don't replace each other); hooks also fire inside subagents, carrying `agent_id`/`agent_type` in the JSON input. — S8, S2.

---

## Q5 — Claude Desktop, Local "Code" mode

Confirmed directly: *"The desktop app includes Claude Code, so you don't need to install Node.js or the CLI"* (S11, `desktop-quickstart.md`) — Local Code-tab sessions run the **same engine**, so plugins, skills, agents, hooks and CLAUDE.md all apply identically to CLI, with three concrete deltas:

1. **Plugins install natively from the app** (`+ → Plugins → Add plugin`, browsing the same marketplaces as CLI, including Anthropic's official one); scope choices (user/project/local) match CLI. — S11 ("Install plugins").
2. **WSL sessions on Desktop do not support plugins at all** ("Plugins aren't available in WSL sessions") — a real gap if a Windows user runs Lintel via Desktop→WSL rather than Local/SSH. — S11.
3. **Cloud/Cowork sessions differ materially**: no plugin browser; a repo's `.claude/settings.json`-declared plugins and any user-scope-installed plugin **do not load**; only skills committed to the cloned repo's `.claude/skills/` and skills enabled for the user's claude.ai account load. — S11, S5, S6 ("Skills in Cowork and cloud sessions").

`~/.claude/skills/` loads for Local sessions; for an SSH session it reads the **remote** host's home directory, not the local machine's. — S11.

---

## Q6 — Instructions: CLAUDE.md, `@imports`, AGENTS.md, `.claude/rules/`

### CLAUDE.md discovery & `@imports`
Load order (broadest→narrowest, concatenated not overridden): managed policy → `~/.claude/CLAUDE.md` → `./CLAUDE.md`/`./.claude/CLAUDE.md` → `./CLAUDE.local.md`. Loaded from cwd **and every parent directory up to filesystem root** at launch; subdirectory CLAUDE.md files load **lazily** when Claude touches files there. `@path/to/file` import syntax: relative paths resolve against the *importing file's* location (not cwd); max recursion depth **4**; skips fenced code/inline code spans (wrap in backticks to cite without importing); imports pointing outside the working directory trigger a one-time approval dialog (except user-scope files, and except Cowork sessions, which skip such imports silently). HTML comments (`<!-- ... -->`) are **stripped before injection** (free "maintainer notes"). Target: **under 200 lines** per file. Source: S10.

### AGENTS.md — direct answer: yes, natively read, but conditionally
Claude Code reads `AGENTS.md` directly as of **v2.1.277+**, per this exact precedence table:

| Repo has | Claude reads |
|---|---|
| `AGENTS.md`, no `CLAUDE.md`/`CLAUDE.local.md` | `AGENTS.md` |
| `AGENTS.md` **and** `CLAUDE.md`/`CLAUDE.local.md` | **`CLAUDE.md` files only** — AGENTS.md is ignored |
| `CLAUDE.md` that itself does `@AGENTS.md` | `CLAUDE.md`, with AGENTS.md pulled in via the import |

Source: S10 ("AGENTS.md" section). **Lintel-specific verification**: Lintel ships both `jokerman89/lintel:CLAUDE.md` and `jokerman89/lintel:AGENTS.md` at the repo root, and I grepped `CLAUDE.md` for `AGENTS\.md|@AGENTS` → **zero matches** — it does not import AGENTS.md. Per the table above, **native Claude Code sessions on this repo never read AGENTS.md**; Lintel's own `AGENTS.md:1-6` header even self-documents this split ("This file is read by agent hosts… GitHub Copilot also loads…"). I then confirmed Lintel's mitigation is sound: the `<!-- LINTEL:SESSION-PROTOCOL:START/END -->` block is **duplicated verbatim** in both files (`CLAUDE.md:171-370` and `AGENTS.md`, byte-identical), rather than imported — which is actually the *correct* choice given the exclusivity rule, since `@AGENTS.md`-importing would also pull AGENTS.md's Codex-specific sections as pure token noise into every Claude Code session. The residual risk is **manual drift** if the shared block is edited in only one file.

### `.claude/rules/` — confirmed to exist, full spec
Directory of topic `.md` files, discovered **recursively** (subfolders like `frontend/`, `backend/` OK). Only frontmatter field read: `paths` (glob list/comma-string) — everything else silently ignored. Rules **without** `paths` load unconditionally at the same priority as `.claude/CLAUDE.md`; rules **with** `paths` load only when Claude reads a matching file (not on every tool call). Brace-expansion budget: 1,000 patterns / 4 MiB per rule. Supports symlinks (external-target symlinks need the same external-import approval, and then only `paths`-less rules load). `~/.claude/rules/` = user-level, loads before project rules; neither overrides the other on conflict. Fires the `InstructionsLoaded` hook event (reasons: `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`). Source: S10, S8. **Gap**: Lintel does not currently use `.claude/rules/` anywhere in the shipped plugin (its equivalent concern is handled by skills instead — a defensible choice, since the docs themselves recommend skills over rules for anything more than always-on file-scoped facts).

---

## Gap list — what Lintel should adopt, fix, or reconsider

**High-confidence, concrete, verified against the actual repo:**

1. **Bug: all 96 `SKILL.md` files use `tools:` instead of `allowed-tools:`.** Verified by grep: `tools:` appears in 96/96 files (e.g. `jokerman89/lintel:skills/cycle/SKILL.md:6`), `allowed-tools:` appears in **0**. `tools:` is not a recognized skill field (it's the *subagent* field name) — Claude Code silently drops it per-spec ("Claude Code ignores a field it doesn't recognize without reporting an error" — S6). Net effect: **the intended per-skill tool pre-approval has never functioned**; every skill invocation goes through the normal permission-prompt flow regardless of this frontmatter. This is a one-line rename per file, and the single highest-value fix from this audit.
2. **`bin/` at plugin root blocks claude.ai/Cowork distribution.** Lintel ships 40+ executables directly under `jokerman89/lintel:bin/` (e.g. `li-scaffold`, `li-doctor`, `li-swarm`). Per S2, this directory is auto-added to the Bash tool's `PATH` (likely intentional/useful) **but also causes claude.ai and Cowork to refuse to install the plugin at all**. If Lintel ever wants claude.ai/Cowork-account distribution, `bin/` needs to move (Anthropic's own doc on this: "Keep executables out of the top-level bin directory" via org-sync docs). If Lintel is CLI/Desktop-only by design, this is fine as-is but should be a documented, deliberate trade-off rather than an incidental one.
3. **Plugin-scoped agent identifiers are nested, not flat.** Because Lintel's `agents/` uses category subfolders (`agents/engineering/Architect.md`), each agent's explicit scoped id is `li:engineering:Architect`, not `li:Architect` — confirmed 0 uses of `@agent-li:` anywhere in `skills/`, so no *existing* text breaks, but any future docs/onboarding material that tells a human operator to type `@agent-li:Architect` will fail; it must say `@agent-li:engineering:Architect`. Worth a one-line note in `docs/architecture.md` or the (missing) agent catalog.
4. **`hooks`/`mcpServers`/`permissionMode` in agent frontmatter would be silently inert.** If Lintel ever adds these to any `agents/**/*.md` file (currently it adds none — verified 0/30 via grep), they will be **ignored outright** because these are plugin subagents (S7, stated twice in docs). Any future per-agent hook/MCP/permission-mode idea must instead go through Lintel's existing `hooks/hooks.json` + `permissions` settings, or instruct users to copy the agent file into their own `.claude/agents/`.
5. **`SessionStart` matcher omits two valid trigger reasons.** Lintel's hook fires on `"startup|resume|clear"` (`jokerman89/lintel:hooks/hooks.json:6-15`); the native matcher also supports `compact` and `fork` (S8's per-event matcher table). If `session-digest` is meant to refresh after a compaction or a forked session, it currently won't.
6. **31 native events exist; 5 are wired.** Concrete, low-risk additions with clear fit to Lintel's own stated mechanisms:
   - **`PreCompact`**: inject/refresh the cycle-position summary right before compaction discards it (complements the existing `UserPromptSubmit`→`cycle-position-inject` hook, which otherwise has to be rediscovered post-compact).
   - **`SessionEnd`**: natural hook point for a final lessons/capture nudge (Lintel already has a `capture`/`lessons-add` skill; today this is manual).
   - **`SubagentStop`**: since a `Stop` hook set in *subagent* frontmatter auto-converts to this event, and Lintel's agents don't define subagent-scoped hooks at all — an audit trail per-delegated-agent-run is a straightforward addition.
   - **`PermissionDenied`**: pairs naturally with the existing `secret-scan-block`/`customer-data-block` Bash-matcher hooks for closing the loop on denied attempts.
7. **`allowed-tools`/`disallowed-tools`, `context: fork`, `paths`, `disable-model-invocation`, `when_to_use`, `arguments` are all zero-adoption** (verified via grep: 0 matches across all `SKILL.md` files for each). Highest-value candidates: `disable-model-invocation: true` for destructive/one-way skills (`ship`, `code-freeze`); `context: fork` + `agent:` for the longer-running skills (`full-engineering-pass`, `swarm`, `research`) to keep their exploration out of the main transcript exactly as the docs recommend subagents for; `paths:` to auto-scope frontend-* skills to matching file globs instead of relying purely on description-matching.
8. **Subagent fields `model`, `memory`, `isolation`, `maxTurns`, `disallowedTools`, `skills` are zero-adoption** (0/30, verified). Strongest fits: `isolation: worktree` for `Migrator`/`Refactorer`/`DeploymentEngineer`/`ReleaseEngineer` (risky/destructive changes get an isolated checkout for free); `model:` pinning for cost control on cheap/mechanical agents (e.g. `ChangelogMaintainer`, `SanityChecker`) vs. reasoning-heavy ones (`SystemArchitect`); `disallowedTools` to positively deny e.g. `Bash` on `ReadOnly`/`SanityChecker` rather than relying only on `tools:` omission. Note on `memory:` — Lintel already has its own `.claude/memory/lessons.md` convention; adopting native per-agent `memory:` should be evaluated deliberately to avoid two parallel, possibly-conflicting persistent-memory systems rather than adopted reflexively.
9. **`${CLAUDE_PLUGIN_DATA}` is unused.** Any future durable, cross-update plugin state (resolved-pack caches, generated indexes) that isn't the *consuming project's* own data belongs in `${CLAUDE_PLUGIN_DATA}` rather than being re-derived each install — currently Lintel doesn't reference this variable anywhere in `hooks/hooks.json` or `lib/`.
10. **`plugin.json` omits several low-risk, high-value fields**: no `displayName`, `defaultEnabled`, `dependencies`, `metadata`, `$schema` (for editor autocomplete). None are required, but `displayName` improves the `/plugin` marketplace listing UX, and `$schema` costs nothing.
11. **Root `CLAUDE.md` is a no-op when Lintel is *installed* as a plugin elsewhere** (S2: plugin-root CLAUDE.md is never loaded as context, and triggers a `claude plugin validate` warning). This is not a bug — Lintel's own `CLAUDE.md:1-9` header confirms its *actual* distribution path for this content is the `scaffolding/01-foundation/CLAUDE.md.template` copy mechanism via `li-scaffold`, not native plugin loading — but it's worth explicitly confirming `claude plugin validate .` is run in CI and that its CLAUDE.md warning is an expected/allow-listed one, not an overlooked signal.
12. **Not currently applicable but worth a deliberate decision**: `workflows/` (`.js`-orchestrated multi-subagent pipelines) is a plausible native alternative/complement to how the `/li:cycle` 9-step pipeline currently coordinates skills — evaluate rather than adopt reflexively, since it would be an architecture-level change, not a small addition. Similarly `monitors/` (background `tail`-style processes, with `when: "on-skill-invoke:<skill>"`) could tie into `context-warm`/`build`-phase log-watching.

---

## UNVERIFIED list (retrieved 2026‑09‑28; flagged because I could not confirm from a primary source within this session's research budget)

- **Exact per-event JSON schema field names for every one of the 31 events** (e.g. the complete `PreCompact`/`SessionEnd`/`ElicitationResult` input/output field tables). I verified the *general* decision model, common input fields (`session_id`, `transcript_path`, `cwd`, `permission_mode`, `effort`, `hook_event_name`, `prompt_id`, `scratchpad_dir`), and the exit-code-2-per-event table directly from `code.claude.com/docs/en/hooks`, but the reference page is extremely long (100K+ characters) and I did not fetch every individual event subsection (e.g., did not confirm the exact output field name Claude Code expects for a non-blocking `Stop` "warning" — I inferred `systemMessage`/`additionalContext` from the universal JSON-output table and the general decision model, not from the `Stop` event's own worked example).
- **The precise `$ARGUMENTS` vs. named `$name` substitution behavior** — I confirmed `arguments:` (named, positional) exists as a frontmatter field and that `$ARGUMENTS`-style placeholders are referenced in the "available string substitutions" anchor, but did not fetch that anchor's dedicated content directly (it was referenced from an adjacent, already-fetched page section rather than read in full).
- **Full `settings-reference` key list** — this single page is unusually large (dozens of screens of JS-rendered filter UI before content); I confirmed specific keys referenced elsewhere (`disableAllHooks`, `disableBundledSkills`, `allowedHttpHookUrls`, `httpHookAllowedEnvVars`, `strictPluginOnlyCustomization`, `enabledPlugins`, `pluginConfigs`, `claudeMdExcludes`) but did not enumerate the complete settings index.
- **claude.ai/Cowork component-support matrix details** beyond what's stated on the Claude Code side (the authoritative comparison table lives at `claude.com/docs/plugins/platform-support`, a claude.com—not code.claude.com—page I did not fetch).
- **CHANGELOG.md historical dates for specific feature introductions** (e.g., exactly which release added `PreCompact`, `monitors`, or hooks-in-skill-frontmatter) — I confirmed current existence and, where the docs stated it inline, the specific version gate (e.g., "requires v2.1.277", "v2.1.218+"), but did not mine the full CHANGELOG history feature-by-feature; I only read the most recent entries (v2.1.283).
- **Whether Lintel's `hooks/shared/*/run.sh` scripts themselves are POSIX-portable when invoked via Git Bash on Windows** — I confirmed the *mechanism* (shell-form → Git Bash resolution) from primary sources, but did not audit the actual script contents for Windows/Git-Bash compatibility.