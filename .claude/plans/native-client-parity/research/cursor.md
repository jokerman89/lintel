# Cursor Native Customization Surfaces — Research Report

**Retrieved:** 2026-09-28 (all `cursor.com` primary sources fetched live on this date; forum/changelog items dated as noted). **Scope:** Cursor editor (desktop IDE), Cursor CLI (binary `agent`, formerly `cursor-agent`), and Cursor cloud/background agents, as of late September 2026.

**Method note:** All schema/field claims are drawn from direct fetches of `cursor.com/docs/*` (primary docs), `cursor.com/changelog/*` (primary changelog), `cursor.com/help/*` (primary help-center, which sometimes contains FAQ detail not in `/docs`), and one primary JSON Schema file (`cursor.com/schemas/environment.schema.json`). Where I relied on secondary/community sources (forum user posts, blogs, aggregators), I say so explicitly and mark the item **UNVERIFIED**. I also cross-checked findings against Lintel's actual repository files (`hooks/hooks.json`, `.cursor-plugin/plugin.json`, `skills/adr-new/SKILL.md`) to ground the porting notes.

---

## Executive summary

Cursor has, over late 2025–2026, converged on nearly the same five-layer customization model Lintel already uses internally: **Skills** (`SKILL.md`, the open Agent Skills standard), **Rules** (`.mdc` + `AGENTS.md`/`CLAUDE.md`), **Commands** (plain markdown slash-prompts), **Subagents** (`.cursor/agents/*.md`), and **Hooks** (`hooks.json`, stdio JSON protocol, Claude-Code-compatible). All five are bundleable into a **Plugin** (`.cursor-plugin/plugin.json`) distributable via a **Marketplace** (`.cursor-plugin/marketplace.json`). Lintel already has a `.cursor-plugin/plugin.json` at its repo root (currently only declaring `skills` and `agents` paths) and a Claude-Code-format `hooks/hooks.json` that is *not* natively readable by a Cursor Plugin's own hook loader — this is the single most important gap the porting notes address below.

Key timeline (all primary, `cursor.com/changelog/*`): Hooks shipped beta in **Cursor 1.7**; Subagents + Agent Skills shipped in **Cursor 2.4**; the Plugin/Marketplace system shipped in **Cursor 2.5**; Team Marketplaces in **Cursor 2.6**. The CLI binary was renamed `cursor-agent` → `agent` (alias retained) around the **Jan 8, 2026** CLI release.

---

## (a) Capability matrix

| Feature | Editor (desktop IDE) | CLI (`agent`, alias `cursor-agent`) | Cloud / background agents | Primary source |
|---|---|---|---|---|
| Agent Skills (`SKILL.md`) | ✅ full | ✅ full (same discovery + `/skill-name`) | ✅ project skills (`.cursor/skills`, `.agents/skills` in repo); personal (`~/.cursor/skills`) only if **synced** | [docs/skills](https://cursor.com/docs/skills), [changelog/2-4](https://cursor.com/changelog/2-4) |
| Project Rules (`.cursor/rules/*.mdc`) | ✅ | ✅ ("CLI agent supports the same rules system") | ✅ (files ship in repo) | [docs/rules](https://cursor.com/docs/rules), [docs/cli/using](https://cursor.com/docs/cli/using) |
| `AGENTS.md` (root + nested) | ✅ | ✅ (explicitly read) | ✅ (explicitly read; recommended location for cloud-only setup notes) | [docs/rules#agentsmd](https://cursor.com/docs/rules), [docs/cli/using](https://cursor.com/docs/cli/using), [docs/cloud-agent/setup](https://cursor.com/docs/cloud-agent/setup) |
| `CLAUDE.md` (root) | ✅ (confirmed only in **help center**, not `/docs/rules`) | ✅ (explicitly read, "applies them as rules alongside `.cursor/rules`") | Not explicitly documented; inferred yes (same file-based mechanism as AGENTS.md) — **UNVERIFIED for cloud specifically** | [help/customization/rules](https://cursor.com/help/customization/rules), [docs/cli/using](https://cursor.com/docs/cli/using) |
| Legacy `.cursorrules` | ⚠️ Still loaded but explicitly called "legacy" and "will be deprecated" — migrate away | Not documented either way — **UNVERIFIED** | Not documented — **UNVERIFIED** | [help/customization/rules](https://cursor.com/help/customization/rules) |
| Custom Commands (`.cursor/commands/*.md`) | ✅ (`/` menu) | ✅ (same `/` menu system; `.cursor/commands` is project-scoped, not CLI-specific) | Not documented — commands are a chat/prompt-invocation surface; cloud agents have no interactive `/` menu — **UNVERIFIED / likely N/A** | [docs/customize-cursor](https://cursor.com/docs/customize-cursor), [docs/reference/plugins](https://cursor.com/docs/reference/plugins) |
| Subagents (`.cursor/agents/*.md`) | ✅ | ✅ (explicit: "You can use subagents in the editor, CLI, and Cloud Agents") | ✅ + dedicated **cloud subagents** (`/in-cloud`, `/autopilot`) | [docs/subagents](https://cursor.com/docs/subagents) |
| Hooks — agent-loop events (`preToolUse`, `beforeShellExecution`, etc.) | ✅ | ✅ (strong evidence: CLI-specific changelog entry "Hooks (3)" with perf work; `workspaceOpen` doc explicitly says "Runs in the Cursor desktop app and CLI") — exact per-event CLI parity table not separately published, so treat as **verified-with-minor-gap** | ✅ for most events — **explicit per-event table published**, see §Q5 | [docs/hooks](https://cursor.com/docs/hooks), [docs/cli/changelog (Jan 8 2026)](https://cursor.com/changelog/cli-jan-08-2026) |
| Hooks — Tab events (`beforeTabFileRead`, `afterTabFileEdit`) | ✅ | Tab is an IDE-only feature; CLI has no Tab — **N/A** | ❌ explicitly not applicable | [docs/hooks](https://cursor.com/docs/hooks) |
| Hooks — `workspaceOpen` | ✅ | ✅ (explicit) | ❌ explicitly not applicable | [docs/hooks](https://cursor.com/docs/hooks) |
| Claude Code hook compatibility (`.claude/settings.json`) | ✅ (toggle: Settings → Agents → Third-Party Imports, on by default) | Not explicitly scoped separately — assume same core, **UNVERIFIED for CLI specifically** | Not listed among cloud hook sources (only Project/Team/Enterprise `.cursor/hooks.json`) — **appears unsupported in cloud** | [docs/reference/third-party-hooks](https://cursor.com/docs/reference/third-party-hooks) |
| Plugins (`.cursor-plugin`, Agent Plugins `plugin.json`) | ✅ (Customize UI) | ✅ (`/plugin [subcommand]` — "Manage plugins and marketplaces") | Plugin-distributed **hooks** run in cloud (team/enterprise); plugin-distributed **skills/rules/agents** are not documented as syncing to cloud automatically — **partially UNVERIFIED** | [docs/cli/reference/slash-commands](https://cursor.com/docs/cli/reference/slash-commands), [docs/plugins](https://cursor.com/docs/plugins) |
| `.cursor/environment.json` | N/A (editor uses local machine, not cloud VM) | N/A | ✅ this *is* the cloud agent environment config | [docs/cloud-agent/setup](https://cursor.com/docs/cloud-agent/setup), [schemas/environment.schema.json](https://cursor.com/schemas/environment.schema.json) |
| Team/Enterprise managed rules & hooks | ✅ | ✅ (implied, same client) | ✅ explicitly (Enterprise dashboard-distributed hooks run in cloud) | [docs/hooks](https://cursor.com/docs/hooks) |

---

## (b) Exact schemas and minimal examples

### Q1 — Agent Skills

**Discovery locations** (auto-loaded, recursive, monorepo-aware) — [docs/skills](https://cursor.com/docs/skills):

| Location | Scope |
|---|---|
| `.agents/skills/` | Project-level |
| `.cursor/skills/` | Project-level |
| `~/.agents/skills/` | User-level (local machine only) |
| `~/.cursor/skills/` | User-level (local; sync to Cloud Agents is opt-in, see below) |
| `.claude/skills/`, `.codex/skills/`, `~/.claude/skills/`, `~/.codex/skills/` | Compatibility shims for Claude/Codex-authored skills |

Cursor also discovers `.cursor/skills/` (or `.agents/skills/`) **nested anywhere in the repo** (e.g. `apps/web/.cursor/skills/`) — these are auto-scoped to files under that subdirectory, equivalent to setting `paths`. `~/.cursor/skills/` (personal) is **not** copied to Cloud Agents/remote-SSH/self-hosted workers unless you enable **Sync Skills for Cloud Agents** (Settings → Agents).

**Minimal file layout:**
```text
.cursor/skills/deploy-app/
├── SKILL.md
├── scripts/deploy.sh        # optional, executable
├── references/REFERENCE.md  # optional, loaded on demand
└── assets/config-template.json  # optional
```

**Frontmatter fields** (YAML) — [docs/skills](https://cursor.com/docs/skills):

| Field | Required | Notes |
|---|---|---|
| `name` | Yes | lowercase, numbers, hyphens only; **must match parent folder name** |
| `description` | Yes | what + when; used by the agent to decide relevance |
| `paths` | No | glob(s), comma-string or list; scopes skill to matching files in context. Legacy alias: `globs` (still accepted, "new skills should use `paths`") |
| `disable-model-invocation` | No | `true` ⇒ only reachable via explicit `/skill-name`, never auto-invoked |
| `icon` | No | Custom-Mode badge icon (e.g. `code`, `terminal`, `bug`, `beaker`, `shield`, `rocket`); unrecognized falls back to lightning icon |
| `color` | No | one of `default, green, cyan, blue, purple, magenta, orange, yellow, red, brand` |
| `metadata` | No | arbitrary key-value map |

No documented character/line-count limit is published by Cursor for `name`/`description`/body size (unlike the base **Agent Skills open standard** at agentskills.io, which specifies `name` 1–64 chars and `description` 1–1024 chars, plus optional `license`, `compatibility`, `allowed-tools` fields — Cursor's own docs table does **not** list `license`, `compatibility`, or `allowed-tools` as honored fields, so treat standard-only fields as **UNVERIFIED for Cursor**). Cursor's guidance is qualitative: "Keep your main SKILL.md focused," move detail to `references/`.

**Minimal example:**
```markdown
---
name: deploy-staging
description: Deploy the current app branch to the staging environment after running tests.
paths: "**/*.tsx, deploy/**"
icon: rocket
color: green
---

# Deploy to Staging

## When to Use
- You want to test new features in staging before releasing to production.

## Instructions
1. Run the test suite.
2. Build the production bundle.
3. Deploy to the staging environment: `scripts/deploy.sh staging`.
```

**Invocation:** Automatic (model decides relevance from `description`) **or** manual via `/skill-name` in Agent chat (attaches for one message) **or** `Option+Enter`/`Alt+Enter` to pin it as a **Custom Mode** for the whole session (badge shown in chat input, styled by `icon`/`color`). Setting `disable-model-invocation: true` forces manual-only (command-like) behavior.

**Full body injection:** Docs describe "progressive" loading — the skill is presented to the agent (name+description surfaced first), and once relevant "resources load on demand," with `scripts/`, `references/`, `assets/` loaded only when the agent's instructions reference them. This implies the `SKILL.md` body itself is injected in full once the skill is selected/invoked, while bundled files are pulled in lazily — this exact mechanic (what's in the "first pass" context vs. lazy-loaded) is not spelled out at a wire-protocol level in the docs; treat the precise trigger boundary as **inferred, not explicitly documented**.

**Built-in Cursor skills** ship out of the box (`/automate`, `/autopilot`, `/canvas`, `/create-hook`, `/create-rule`, `/create-skill`, `/create-subagent`, `/cursor-blame`, `/loop`, `/migrate-to-skills`, `/review`, `/review-bugbot`, `/review-security`, `/sdk`, `/shell`, `/split-to-prs`, `/statusline`, `/update-cli-config`, `/update-cursor-settings`) — full list at [docs/skills](https://cursor.com/docs/skills). Notably `/migrate-to-skills` (shipped in 2.4) auto-converts "Apply Intelligently" rules and slash commands into skills.

Skills cannot be "imported" bare from a repo — only via a **Plugin** (`.cursor-plugin/marketplace.json` or team marketplace); see Q6.

---

### Q2 — Rules and instructions

**Four rule types** — [docs/rules](https://cursor.com/docs/rules):

1. **Project Rules** — `.cursor/rules/*.mdc` (must be `.mdc`; a bare `.md` file in that directory is **ignored** because it has no frontmatter mechanism recognized by the rule system).
2. **User Rules** — global, set in Customize → Rules (a settings-stored string, *not* a file — also unofficially mirrored as local files at `~/.cursor/rules`/`%USERPROFILE%\.cursor\rules`, which "stay on the machine and do not sync," per [help/customization/rules](https://cursor.com/help/customization/rules)).
3. **Team Rules** — dashboard-managed, Team/Enterprise; free-form text (no folder structure), support `globs`, can be "Enforced" (undismissable) or optional.
4. **`AGENTS.md`** — plain markdown, no frontmatter, root **and nested subdirectories**; nested instructions combine with parents, more specific wins.

**Precedence when merged:** Team Rules → Project Rules → User Rules (earlier wins on conflict) — [docs/rules](https://cursor.com/docs/rules).

**`.mdc` frontmatter fields:**

| Field | Type | Behavior |
|---|---|---|
| `description` | string | Used by the agent to decide relevance ("Apply Intelligently") |
| `globs` | string or comma-separated list | File-pattern auto-attach |
| `alwaysApply` | boolean | `true` ⇒ injected into every chat session, ignoring `description`/`globs` |

Combination table (exact, from source):

| `alwaysApply` | `description` | `globs` | Behavior |
|---|---|---|---|
| `true` | — | — | Always included |
| `false` | — | provided | Auto-attached on matching file in context |
| `false` | provided | omitted | Agent-decides ("Apply Intelligently") |
| `false` | omitted | omitted | Manual only, via `@rule-name` mention |

**Minimal examples** (four variants, one per mode) — [docs/rules](https://cursor.com/docs/rules):
```md
---
alwaysApply: true
---
- All source files must include the company copyright header
```
```md
---
globs: src/components/**/*.tsx
alwaysApply: false
---
- Use named exports, not default exports
```
```md
---
description: RPC service conventions and patterns for the backend
alwaysApply: false
---
- Define each service in its own file under `src/services/`
```

**Glob syntax:** `*` (one segment), `**` (recursive dirs), commas separate multiple patterns, e.g. `docs/**/*.md, docs/**/*.mdx`.

**Best-practice guidance (explicit in docs):** keep rules **under 500 lines**; split into focused composable files; reference files with `@filename.ts` instead of inlining; avoid restating linter-enforced style or common tool knowledge.

**`AGENTS.md`:** plain markdown, root + any subdirectory, nested files combine (child overrides/extends parent) — [docs/rules#agentsmd](https://cursor.com/docs/rules). Cloud agents explicitly read it; docs recommend a dedicated "Cursor Cloud specific instructions" heading for cloud-only setup notes — [docs/cloud-agent/setup](https://cursor.com/docs/cloud-agent/setup).

**`CLAUDE.md`:** *Not* mentioned on the `/docs/rules` reference page, but explicitly confirmed on the **help-center** FAQ page: *"Cursor reads `CLAUDE.md` files the same way it reads `AGENTS.md`... `CLAUDE.md` files are always applied to every conversation, regardless of any `alwaysApply` frontmatter setting... If you need conditional rules, use project rules in `.cursor/rules/` instead."* — [help/customization/rules](https://cursor.com/help/customization/rules). CLI docs separately and independently confirm: *"The CLI also reads `AGENTS.md` and `CLAUDE.md` at the project root (if present) and applies them as rules alongside `.cursor/rules`."* — [docs/cli/using](https://cursor.com/docs/cli/using). Net: **CLAUDE.md is always-applied, unconditional, root-only** (no confirmed nested-subdirectory support, unlike `AGENTS.md`).

**Legacy `.cursorrules`:** confirmed only on the help-center page, explicit migration guidance given: *"The `.cursorrules` file in your project root is legacy and will be deprecated."* Steps: create a new rule via Command Palette → "New Cursor Rule," copy content in, set type to "Always Apply," delete `.cursorrules` — [help/customization/rules](https://cursor.com/help/customization/rules). No firm removal date is published.

**Scope limitation (explicit FAQ):** "Rules only apply to Agent (Chat). They do not apply to Tab completion, Inline Edit, or Bugbot PR reviews." User Rules additionally do not apply to Inline Edit (Cmd/Ctrl+K) — [docs/rules](https://cursor.com/docs/rules), [help/customization/rules](https://cursor.com/help/customization/rules).

---

### Q3 — Custom commands

There is **no dedicated top-level `/docs/commands` page** (`cursor.com/docs/commands` → 404 as of this retrieval); commands are documented only inside [docs/customize-cursor](https://cursor.com/docs/customize-cursor) (one paragraph) and [docs/reference/plugins](https://cursor.com/docs/reference/plugins) (as a plugin component format).

**Definition:** *"Reusable prompts you invoke with `/` in Agent chat. Commands are markdown files that define a focused workflow or action."* — [docs/customize-cursor](https://cursor.com/docs/customize-cursor).

**Format** (from the plugin-component reference, which is the only place the file schema is documented) — [docs/reference/plugins](https://cursor.com/docs/reference/plugins):
- Location: `commands/` directory (plugin) — for a bare, non-plugin project the equivalent is `.cursor/commands/` (confirmed only via community sources — **not found in official docs directly**, so mark the exact project-level bare path as **UNVERIFIED from primary source**, though strongly implied by symmetry with `.cursor/rules`, `.cursor/agents`, `.cursor/skills`).
- Extensions: `.md`, `.mdc`, `.markdown`, `.txt`.
- Optional YAML frontmatter: `name` (string, lowercase kebab-case identifier) and `description` (string).

```markdown title="commands/deploy-staging.md"
---
name: deploy-staging
description: Deploy the current branch to the staging environment
---

# Deploy to staging

Steps to deploy to staging:
1. Run tests
2. Build the project
3. Push to staging branch
```

**Argument passing:** No `$ARGUMENTS`/positional-placeholder substitution syntax is documented in any primary Cursor source I could find (this exists in Claude Code's command format, and secondary blogs speculate Cursor might support similar placeholders, but I found no `cursor.com` confirmation). Treat command "arguments" as: the command's markdown body is inserted, and any text you type after invoking `/command-name` is appended as ordinary chat text — **mark exact mechanics UNVERIFIED**.

**Relationship to skills:** Commands are simpler/static (no frontmatter-driven auto-invocation, no bundled `scripts/`/`references/`/`assets/`, no automatic model-triggered relevance matching) — pure explicit "insert this prompt" building blocks. Cursor's own migration tooling treats them as convertible: the built-in `/migrate-to-skills` skill (2.4+) converts slash commands into skills with `disable-model-invocation: true`, "preserving their explicit invocation behavior" — [docs/skills](https://cursor.com/docs/skills). This strongly implies Cursor sees Commands as a legacy/simpler subset of what Skills can do, and steers authors toward Skills going forward.

---

### Q4 — Subagents / custom agents

**File locations** (exact precedence order) — [docs/subagents](https://cursor.com/docs/subagents):

| Type | Location | Scope |
|---|---|---|
| Project | `.cursor/agents/` | current project |
| Project (compat) | `.claude/agents/`, `.codex/agents/` | current project |
| User | `~/.cursor/agents/` | all projects, this user |
| User (compat) | `~/.claude/agents/`, `~/.codex/agents/` | all projects, this user |

`.cursor/` wins over `.claude/`/`.codex/` on name conflicts.

**File format:**
```markdown
---
name: security-auditor
description: Security specialist. Use when implementing auth, payments, or handling sensitive data.
model: inherit
readonly: true
---

You are a security expert auditing code for vulnerabilities.

When invoked:
1. Identify security-sensitive code paths
2. Check for common vulnerabilities (injection, XSS, auth bypass)
...
```

**Frontmatter fields (complete list, verbatim from docs):**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `name` | string | No | derived from filename | lowercase + hyphens |
| `description` | string | No | — | shown in Task-tool delegation hints; agent reads it to decide when to delegate. Include "use proactively"/"always use for" to bias automatic delegation |
| `model` | string | No | `inherit` | `inherit` or an explicit model ID, optionally with bracketed parameters, e.g. `claude-opus-5[effort=high,context=300k]` |
| `readonly` | boolean | No | `false` | `true` = no file edits, no state-changing shell commands |
| `is_background` | boolean | No | `false` | `true` = runs without blocking the parent |

**There is no `tools` (or `allowed-tools`/`mcp_tools`) frontmatter field.** I verified this by reading the entire configuration-fields table in the primary doc (only the five fields above exist); this is corroborated by an open, unresolved Cursor forum feature request (*"Cursor Subagent MCP Toolset Control Request"*, community, not staff) asking for exactly this capability. Today the **only** access lever is the coarse boolean `readonly`. This directly matters for Lintel: its skill/subagent frontmatter uses a Claude-style `tools: Read, Bash, Edit, Glob` field (verified in `skills/adr-new/SKILL.md` in the Lintel repo) — **Cursor will not enforce that allow-list**; it is inert metadata to Cursor.

**Invocation:**
- **Automatic**: agent decides based on `description`, task complexity, context.
- **Explicit**: `/subagent-name <task>` or natural language ("Use the verifier subagent to...").
- **Parallel**: multiple Task-tool calls in one message run subagents concurrently; nesting allowed since **Cursor 2.5** (subagent → subagent, one level deep only; the top agent and its direct subagents can spawn, a grandchild cannot).
- **Isolation**: by default subagents share the parent checkout; asking for isolation gives each its own git worktree or cloud VM+branch.
- **Cloud subagents**: `/in-cloud` (next task runs as a cloud subagent on its own VM+branch) and `/autopilot` (hand a PR to a cloud subagent) — these use the *team's* MCP config, not the local session's.

**Built-in subagents** (auto-used, not user-configured): `explore` (codebase search, faster model), `bash` (shell command runner), `browser` (MCP browser control) — [docs/subagents](https://cursor.com/docs/subagents).

**Surface support:** explicitly "editor, CLI, and Cloud Agents" per the doc's opening paragraph.

---

### Q5 — Hooks (the core mechanism for Lintel's lifecycle logic)

**Config file locations, in priority order (highest → lowest)** — [docs/hooks](https://cursor.com/docs/hooks):

| Level | Path | Notes |
|---|---|---|
| Enterprise | macOS `/Library/Application Support/Cursor/hooks.json`; Linux/WSL `/etc/cursor/hooks.json`; Windows `C:\ProgramData\Cursor\hooks.json` | MDM-managed, system-wide |
| Team | Cloud dashboard (`cursor.com/dashboard/team-content?section=hooks`) | Enterprise-only, auto-synced every 30 min |
| Project | `<project-root>/.cursor/hooks.json` | version-controlled, runs from **project root** |
| User | `~/.cursor/hooks.json` | runs from `~/.cursor/` |

**All matching hooks from every source run together**; responses are merged: `deny` beats `ask` beats `allow`; `user_message`/`agent_message` are **concatenated** across sources; other scalar fields (e.g. `followup_message`) use **last-writer-wins** in the priority order above (a lower-priority source can override a field set by a higher one — verbatim from docs, slightly counter-intuitive, worth re-testing before relying on it).

**Top-level schema:**
```json
{
  "version": 1,
  "hooks": {
    "<hookName>": [
      { "command": "…", "type": "command", "timeout": 30, "matcher": "regex", "failClosed": false, "loop_limit": 5 }
    ]
  }
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `version` | number | required | must be a positive integer, use `1` |
| `command` | string | required | shell string / absolute / relative path (relative to project root for project hooks, `~/.cursor/` for user hooks) |
| `type` | `"command"` \| `"prompt"` | `"command"` | `"prompt"` = LLM-evaluated natural-language policy (see below) |
| `timeout` | number (seconds) | platform default | execution timeout |
| `loop_limit` | number \| `null` | `5` (Cursor hooks); `null` (Claude-imported hooks) | caps auto-follow-up loops for `stop`/`subagentStop` |
| `failClosed` | boolean | `false` | `true` ⇒ crash/timeout/non-zero-exit/no-output **blocks** the action instead of failing open. Permission hooks (see below) already block on invalid JSON/schema mismatch regardless of this flag |
| `matcher` | string (regex) | — | empty string or `"*"` matches everything; meaning of what's matched is **per-hook** (see table below) |

**Prompt-based hooks** (LLM-evaluated, no script needed):
```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [
      { "type": "prompt", "prompt": "Does this command look safe to execute? Only allow read-only operations.", "timeout": 10 }
    ]
  }
}
```
Returns `{ ok: boolean, reason?: string }`; runs on a fast Cursor-managed model; `$ARGUMENTS` is substituted with the hook's JSON input (auto-appended if `$ARGUMENTS` is absent); optional `model` field overrides the model.

**Exit-code semantics** (command hooks):

| Exit code | Meaning |
|---|---|
| `0` | Success — use JSON stdout. For **permission hooks** (`beforeShellExecution`, `beforeMCPExecution`, `beforeReadFile`, `beforeTabFileRead`, `subagentStart`, `preToolUse`), invalid JSON or a schema-mismatched response **blocks the action** regardless of `failClosed` |
| `2` | Block the action (`permission: "deny"` equivalent) — this matches Claude Code, intentionally, for hook-script portability |
| other | Failed — action proceeds (**fail-open**) unless `failClosed: true` |

**Complete hook-event catalog** (three categories) — [docs/hooks](https://cursor.com/docs/hooks):

*Agent hooks (fire during Cmd+K / Agent Chat sessions):* `sessionStart`, `sessionEnd`, `preToolUse`, `postToolUse`, `postToolUseFailure`, `subagentStart`, `subagentStop`, `beforeShellExecution`, `afterShellExecution`, `beforeMCPExecution`, `afterMCPExecution`, `beforeReadFile`, `afterFileEdit`, `beforeSubmitPrompt`, `preCompact`, `stop`, `afterAgentResponse`, `afterAgentThought`.

*Tab hooks (autonomous inline completions):* `beforeTabFileRead`, `afterTabFileEdit`.

*App-lifecycle hook (outside any session):* `workspaceOpen` — fires on workspace open and every folder change; can return `pluginPaths` (array of absolute paths) to dynamically load additional plugins for that workspace.

**Common input envelope (all hooks receive this, merged with hook-specific fields):**
```json
{
  "conversation_id": "string",
  "generation_id": "string",
  "model": "string",
  "model_id": "string",
  "model_params": [{ "id": "string", "value": "string" }],
  "hook_event_name": "string",
  "cursor_version": "string",
  "workspace_roots": ["<path>"],
  "user_email": "string | null",
  "transcript_path": "string | null"
}
```
(`workspaceOpen` omits `conversation_id`, `generation_id`, `model`, `session_id`, `transcript_path`.)

**Per-event payloads** (input → output), condensed from the primary doc:

| Event | Key input fields | Output fields | Can block? | Can inject context? |
|---|---|---|---|---|
| `preToolUse` | `tool_name` (`Shell`/`Read`/`Write`/`Grep`/`Delete`/`Task`/`MCP:<name>`), `tool_input`, `tool_use_id`, `cwd`, `agent_message` | `permission: allow\|deny`, `user_message`, `agent_message`, `updated_input` (replaces tool input) | ✅ (`ask` accepted by schema, **not enforced today**) | via `updated_input` only |
| `postToolUse` | + `tool_output` (JSON string), `duration` | `updated_mcp_tool_output` (MCP only), `additional_context` | ❌ (already ran) | ✅ `additional_context` |
| `postToolUseFailure` | `error_message`, `failure_type` (`error`\|`timeout`\|`permission_denied`), `duration`, `is_interrupt` | `additional_context` | ❌ | ✅ |
| `subagentStart` | `subagent_id`, `subagent_type`, `task`, `parent_conversation_id`, `tool_call_id`, `subagent_model`, `is_parallel_worker`, `git_branch` | `permission: allow\|deny`, `user_message` | ✅ (`ask` **treated as deny**) | ❌ |
| `subagentStop` | `subagent_type`, `status` (`completed`\|`error`\|`aborted`), `summary`, `duration_ms`, `modified_files`, `loop_count`, `agent_transcript_path` | `followup_message` | N/A (post-hoc) | ✅ via auto-continue message; capped by `loop_limit` (default 5) |
| `beforeShellExecution` | `command`, `cwd`, `sandbox` | `permission: allow\|deny\|ask`, `user_message`, `agent_message` | ✅ full 3-state | via `agent_message` only |
| `afterShellExecution` | `command`, `output`, `duration`, `sandbox` | — (observational) | ❌ | ❌ |
| `beforeMCPExecution` | `tool_name`, `tool_input`, `mcp_server_name`, + (`mcp_server_url`/`url`) or (`command`) | `permission: allow\|deny\|ask`, `user_message`, `agent_message` | ✅ | via `agent_message` |
| `afterMCPExecution` | `tool_name`, `tool_input`, `mcp_server_name`, `result_json`, `duration` | — (observational) | ❌ | ❌ |
| `beforeReadFile` | `file_path`, `content`, `attachments[{type: file\|rule, file_path}]` | `permission: allow\|deny`, `user_message` | ✅ | ❌ |
| `afterFileEdit` | `file_path`, `edits[{old_string,new_string}]` | **no output schema documented** | ❌ | ❌ (use `postToolUse` matcher `Write` instead if you need `additional_context`) |
| `beforeTabFileRead` | `file_path`, `content` (no `attachments`) | `permission: allow\|deny` | ✅ | ❌ |
| `afterTabFileEdit` | `file_path`, `edits[{old_string,new_string,range,old_line,new_line}]` | none supported | ❌ | ❌ |
| `beforeSubmitPrompt` | `prompt`, `attachments` | `continue: bool`, `user_message` | ✅ (block submission) | **❌ no `additional_context` field documented** |
| `afterAgentResponse` | `text` | none | ❌ | ❌ |
| `afterAgentThought` | `text`, `duration_ms` | none | ❌ | ❌ |
| `stop` | `status` (`completed`\|`aborted`\|`error`), `loop_count` | `followup_message` | N/A | ✅ via auto-submitted follow-up message (loop, capped) |
| `sessionStart` | `session_id`, `is_background_agent`, `composer_mode` | `env` (object), `additional_context`; fire-and-forget, **not blocking even if you set `continue:false`** | ❌ | ✅ `additional_context` + session-scoped `env` vars |
| `sessionEnd` | `session_id`, `reason` (`completed`\|`aborted`\|`error`\|`window_close`\|`user_close`), `duration_ms`, `final_status`, `error_message` | none (fire-and-forget, response logged not used) | ❌ | ❌ |
| `preCompact` | `trigger` (`auto`\|`manual`), `context_usage_percent`, `context_tokens`, `context_window_size`, `message_count`, `messages_to_compact`, `is_first_compaction` | `user_message` | ❌ (observational only) | only a user-facing message |
| `workspaceOpen` | (common fields only) | `pluginPaths` (array) | ❌ | indirectly, by loading more plugins |

**Matcher semantics per hook** (what the regex tests against) — [docs/hooks](https://cursor.com/docs/hooks):

| Hook | Matched against |
|---|---|
| `preToolUse`/`postToolUse`/`postToolUseFailure` | tool type: `Shell`, `Read`, `Write`, `Grep`, `Delete`, `Task`, or `MCP:<tool_name>` |
| `subagentStart`/`subagentStop` | subagent type (`generalPurpose`, `explore`, `shell`, etc.) |
| `beforeShellExecution`/`afterShellExecution` | the full shell command string |
| `beforeReadFile` | literal value `Read` |
| `afterFileEdit` | literal value `Write` |
| `beforeTabFileRead` / `afterTabFileEdit` | literal `TabRead` / `TabWrite` |
| `beforeSubmitPrompt` | literal `UserPromptSubmit` |
| `stop` | literal `Stop` |
| `afterAgentResponse` / `afterAgentThought` | literal `AgentResponse` / `AgentThought` |

**Environment variables passed to every hook script:**

| Variable | Always present? |
|---|---|
| `CURSOR_PROJECT_DIR` | Yes |
| `CURSOR_VERSION` | Yes |
| `CURSOR_USER_EMAIL` | if logged in |
| `CURSOR_TRANSCRIPT_PATH` | if transcripts enabled |
| `CURSOR_CODE_REMOTE` | `"true"` for remote workspaces |
| `CLAUDE_PROJECT_DIR` | Yes (Claude-compat alias) |

`sessionStart`'s `env` output is passed to **all subsequent hook executions in that session**.

**Cloud-agent hook support** (explicit table) — [docs/hooks](https://cursor.com/docs/hooks):

Supported: `beforeShellExecution`, `afterShellExecution`, `beforeReadFile`, `afterFileEdit`, `preToolUse`, `postToolUse`, `postToolUseFailure`, `subagentStart`, `subagentStop`, `beforeSubmitPrompt`, `preCompact`, `afterAgentResponse`, `afterAgentThought`, `stop`.

Not supported: `sessionStart`/`sessionEnd` (cloud agents have no matching lifecycle boundary; a cloud `sessionStart` would fire *after* the first write since agents can start read-only), `beforeMCPExecution`/`afterMCPExecution` (same read-only-start timing issue), `beforeTabFileRead`/`afterTabFileEdit` (Tab is IDE-only), `workspaceOpen` (IDE-only). Cloud agents run **command-based hooks only** — prompt-based hooks require auth wiring unavailable in the cloud sandbox. Cloud agents load hooks from **project** `.cursor/hooks.json` always; **Team/Enterprise** hooks only on Enterprise plans. **User-level `~/.cursor/hooks.json` never reaches cloud agents** (no access to your home directory).

**Windows support:** Confirmed at the *configuration-distribution* level — Windows has a documented global hooks path (`C:\ProgramData\Cursor\hooks.json`) and CLI config path (`$env:USERPROFILE\.cursor\cli-config.json`), so Windows is an officially supported OS for Cursor generally. However, **I found no official documentation of which shell/interpreter runs a hook's `command` string on native Windows**, or whether POSIX shebang scripts (`#!/bin/bash`) work out of the box. Multiple **community forum threads** (not staff posts) report that bash-shebang scripts fail on native Windows and must be wrapped in a `.ps1` launcher that explicitly invokes `bash.exe`/PowerShell and prints JSON to stdout — **mark this UNVERIFIED / community-only**; if Lintel targets Windows Cursor users running hooks outside WSL, budget for a PowerShell-wrapper fallback per hook script.

**Third-party (Claude Code) hook compatibility — critical for Lintel:**

Cursor natively loads and executes Claude Code's `hooks` config, gated by **Settings → Agents → Third-Party Imports → "Include Third-Party Plugins, Skills, and Other Configs"** (on by default) — [docs/reference/third-party-hooks](https://cursor.com/docs/reference/third-party-hooks).

Load locations, in priority (below Cursor's own Project/User hooks):
1. Enterprise (managed)
2. Team (dashboard)
3. Project `.cursor/hooks.json`
4. User `~/.cursor/hooks.json`
5. `.claude/settings.local.json` (project, gitignored)
6. `.claude/settings.json` (project, checked in)
7. `~/.claude/settings.json` (user)

Event-name mapping (automatic):

| Claude Code | Cursor |
|---|---|
| `PreToolUse` | `preToolUse` |
| `PostToolUse` | `postToolUse` |
| `UserPromptSubmit` | `beforeSubmitPrompt` |
| `Stop` | `stop` |
| `SubagentStop` | `subagentStop` |
| `SessionStart` | `sessionStart` |
| `SessionEnd` | `sessionEnd` |
| `PreCompact` | `preCompact` |

Response format: Cursor accepts **both** Claude's nested `hookSpecificOutput.{permissionDecision, permissionDecisionReason, updatedInput}` and Cursor's flat `{permission, user_message, updated_input}` — they're treated as equivalent. For `Stop`/`SubagentStop`, Claude's `{"decision":"block","reason":"..."}` (nested or flat legacy form) is treated as Cursor's `followup_message`. Exit code `2` blocks in both systems (explicitly aligned for portability).

**Directly relevant to Lintel:** Lintel's repo-root `hooks/hooks.json` is **already** in Claude-Code-plugin shape (`hooks.SessionStart[].hooks[].command` using `${CLAUDE_PLUGIN_ROOT}`, matchers like `"Edit|Write"`, `"Bash"`, `"startup|resume|clear"`). This is *not* one of the seven paths Cursor's third-party loader scans (that list is `.claude/settings*.json`, not an arbitrary `hooks/hooks.json`) — so as-is, this file is invisible to Cursor. See Porting Notes below.

**Troubleshooting/observability:** a **Hooks tab in Customize** plus a dedicated **Hooks output channel** for debugging. `hooks.json` is watched and hot-reloaded on save (restart if it doesn't pick up).

**Version history (primary, `cursor.com/changelog`):**
- **Cursor 1.7** ("Browser Controls, Plan Mode, and Hooks") — Hooks shipped **in beta**. [changelog/1-7](https://cursor.com/changelog/1-7)
- **Cursor 2.0** and later — Enterprise cloud hook distribution added (documented in `/docs/hooks`, not independently re-verified against a specific numbered changelog entry in this pass).
- **CLI, Jan 8 2026 release** — "major hooks performance improvements" (10–20× faster per secondary reporting cross-referencing this exact URL), `afterFileEdit` gained previous-file-content-for-diffing capability. [changelog/cli-jan-08-2026](https://cursor.com/changelog/cli-jan-08-2026)

---

### Q6 — Plugins

Cursor supports **two manifest formats** simultaneously — [docs/reference/plugins](https://cursor.com/docs/reference/plugins), [docs/plugins](https://cursor.com/docs/plugins):

| Format | Manifest | Components |
|---|---|---|
| **Agent Plugins** (open standard, [agent-plugins.org](https://agent-plugins.org)) | `plugin.json` at plugin root | Skills, MCP servers only |
| **Cursor Plugins** | `.cursor-plugin/plugin.json` | Skills, MCP servers, **+ Rules, Agents (subagents), Commands, Hooks, Variables** |

**Cursor Plugin directory layout:**
```text
my-plugin/
├── .cursor-plugin/
│   └── plugin.json        # required manifest
├── rules/                 # .mdc files
├── skills/                 # SKILL.md-containing folders
├── agents/                 # subagent .md files
├── commands/                # command .md/.mdc/.markdown/.txt files
├── hooks/
│   └── hooks.json          # Cursor-native schema (NOT Claude schema)
├── mcp.json
├── assets/logo.svg
├── scripts/
└── README.md
```

**`plugin.json` manifest fields:**

Required: `name` (string, lowercase kebab-case, must start/end alphanumeric).

Optional: `description`, `version` (semver), `author {name, email}`, `homepage`, `repository`, `license`, `keywords[]`, `logo` (relative path → resolves to `raw.githubusercontent.com`, or absolute URL), `category`, `tags[]`, `rules`/`agents`/`skills`/`commands` (string or array — **overrides** default folder discovery for that component when present), `hooks` (string path or inline object), `mcpServers` (string/object/array), `variables` (JSON-Schema object declaring **names only**, never values — actual secret values are set by admins in the dashboard **Plugins → Configure**).

```json title=".cursor-plugin/plugin.json — minimal"
{
  "name": "my-plugin",
  "description": "Custom development tools",
  "version": "1.0.0",
  "author": { "name": "Your Name" }
}
```

**Component auto-discovery (used whenever the manifest omits an explicit path):**

| Component | Default folder | Discovery rule |
|---|---|---|
| Skills | `skills/` | each subdir containing `SKILL.md` |
| Rules | `rules/` | all `.md`/`.mdc`/`.markdown` |
| Agents | `agents/` | all `.md`/`.mdc`/`.markdown` |
| Commands | `commands/` | all `.md`/`.mdc`/`.markdown`/`.txt` |
| Hooks | `hooks/hooks.json` | parsed for hook event names |
| MCP servers | `mcp.json` | parsed for server entries |
| Root skill | `SKILL.md` at plugin root | single-skill plugin, only if no `skills/` dir and no manifest `skills` field |

If a manifest field is explicitly set, it **replaces** (not adds to) folder discovery for that component.

**Variables (secrets-by-reference) example:**
```json title=".cursor-plugin/plugin.json"
{
  "name": "example-plugin",
  "variables": {
    "type": "object",
    "properties": { "API_TOKEN": { "type": "string", "title": "API token" } },
    "required": ["API_TOKEN"]
  }
}
```
Only a fixed JSON-Schema subset is honored: `type, title, description, default, enum, const, properties, required, items`, common length/numeric constraints. Placeholders `${VAR}` in `mcp.json`/other config are substituted at runtime; never commit actual secret values.

**Plugin-root variable for command expansion:** `${CURSOR_PLUGIN_ROOT}` (and, for compatibility, `${CLAUDE_PLUGIN_ROOT}`) are expanded by Cursor to the plugin's install path — **explicitly documented for `mcp.json`'s `command`/`args`/`env`/`cwd`**. I did **not** find an equally explicit statement that hook `command` strings inside a plugin's `hooks/hooks.json` also get this expansion (the one worked example uses a plain relative path, `./scripts/format-code.sh`) — **mark variable-expansion-in-hook-commands as UNVERIFIED**; prefer plugin-root-relative paths without variable syntax unless you test and confirm expansion works.

**Marketplace manifest** (`.cursor-plugin/marketplace.json`, for multi-plugin repos):
```json
{
  "name": "my-marketplace",
  "owner": { "name": "Your Org", "email": "plugins@yourorg.com" },
  "metadata": { "description": "A collection of developer tool plugins" },
  "plugins": [
    { "name": "plugin-one", "source": "plugin-one", "description": "First plugin" },
    { "name": "plugin-two", "source": "plugin-two", "description": "Second plugin" }
  ]
}
```
`name`/`owner`/`plugins` required; whole file capped at **10 MB**. Each `plugins[]` entry may carry its own `description`/`version`/`author`/`homepage`/`repository`/`license`/`keywords`/`logo`/`category`/`tags`/component-paths/`hooks`/`mcpServers`/`variables`, which **merge with and take precedence over** the per-plugin `.cursor-plugin/plugin.json` if both exist.

**Install / update:**
- Editor: **Customize** sidebar panel → find plugin → **Install** (choose project or user scope). Also: **Customize → "From GitHub Repository"** (needs `.cursor-plugin/marketplace.json`) to import a whole repo of plugins, or add as a **Team Marketplace**.
- CLI: `/plugin [subcommand]` — "Manage plugins and marketplaces" — [docs/cli/reference/slash-commands](https://cursor.com/docs/cli/reference/slash-commands). Also editor-only shorthand `/add-plugin` mentioned in the 2.5 changelog for marketplace installs.
- Local dev/testing (no marketplace needed): drop either format into `~/.cursor/plugins/local/<name>/`, then **Developer: Reload Window**. On Teams/Enterprise this path is gated by admin setting **"Allow Local Plugin Imports"** (off by default on Enterprise). A marketplace-installed plugin of the same name takes precedence over the local copy. Symlinks only resolve if the target is inside that folder.
- Submission for the public Cursor Marketplace: `cursor.com/marketplace/publish`, manually reviewed; checklist includes valid manifest, unique kebab-case `name`, valid frontmatter on all components, relative-only paths (no `..`, no absolute paths), and — for multi-plugin repos — a root `.cursor-plugin/marketplace.json`.

**Namespacing:** Not explicitly documented as a formal namespace mechanism (e.g., no `plugin-name/skill-name` prefixing scheme described). Practically, uniqueness is enforced only at the `plugin.json`/`marketplace.json` `name` level (must be globally unique on the marketplace, kebab-case); individual skills/rules/agents/commands inside are discovered by their own `name` field, and Cursor's project-over-compat precedence rules (Q4) are the only documented conflict-resolution mechanism I found for name collisions — **treat cross-plugin skill/agent name collision behavior as UNVERIFIED**.

**Team/Enterprise distribution:** Team plans get **1 team marketplace**; Enterprise gets **unlimited**. Admin-controlled **Marketplace Access** (restrict to Organization Groups, SCIM-syncable) and **installation modes** per plugin: `Default Off` (opt-in), `Default On` (opt-out), `Required` (cannot uninstall). GitHub-imported marketplaces support **Auto Refresh** (re-index within 10 min of a push, requires the Cursor GitHub App) or manual **Refresh**; GitLab/Bitbucket/Azure DevOps imports are manual-refresh only. A **Default team marketplace** additionally lets admins publish personal skills for teammates to opt into (`Publish` from Customize → Skills), separate from the sync-for-cloud-agents mechanism.

**Version history (primary):** Plugins/Marketplace shipped in **Cursor 2.5** ("Plugins on the Cursor Marketplace... package skills, subagents, MCP servers, hooks, and rules") — [changelog/2-5](https://cursor.com/changelog/2-5); **Team Marketplaces** in **Cursor 2.6** — [changelog/2-6](https://cursor.com/changelog/2-6); the unified **Customize** page (leaderboard, plugin canvases, multi-provider team-marketplace import) shipped in a separate, undated changelog entry — [changelog/customize](https://cursor.com/changelog/customize).

---

### Q7 — Cloud/background agents

**Which surfaces apply:** see the capability matrix above; in short — Skills (project-level, always; personal only if synced), Rules + `AGENTS.md` (+ inferred `CLAUDE.md`) (always, they're just repo files), Subagents (yes, plus dedicated cloud-subagent handoff via `/in-cloud`/`/autopilot`), Hooks (yes, with the explicit supported/unsupported table in Q5), Plugins (project-declared hooks run; skills/rules ship as plain repo files so they load regardless of plugin wrapping; but plugin-distributed **hooks specifically** are called out as loading "from your repository," i.e., they must resolve to a `.cursor/hooks.json` file physically present, not just an installed-but-unsynced plugin reference — **mark whether an *installed marketplace plugin's* bundled rules/skills/agents sync into the cloud VM the same way repo files do as partially UNVERIFIED**, since the docs frame cloud hook loading specifically around "`.cursor/hooks.json` at the root of your project").

**`.cursor/environment.json` — full authoritative schema**, fetched directly from Cursor's published JSON Schema at **[cursor.com/schemas/environment.schema.json](https://cursor.com/schemas/environment.schema.json)** (draft 2019-09, `allowComments: true`):

Merges two definition blocks, `common` + `container` (`allOf`, `unevaluatedProperties: false` — i.e. no undeclared fields allowed):

**`common` fields:**

| Field | Type | Description |
|---|---|---|
| `name` | string | environment name |
| `user` | string | user to run the environment as |
| `install` | string | script to run on VM startup to refresh dependencies (this is what the prepared-Build system executes; **must be idempotent**) |
| `start` | string | command run when the environment starts (long-running processes) |
| `repositoryDependencies` | string[] | additional repo URLs (e.g. `github.com/org/repo`) required for the token grant |
| `disableAllMcpServers` | boolean | blocks all user/team MCP servers (built-in Cursor MCP servers exempted) |
| `mcpServerAllowlist` | array of `{name?, serverUrl? \| command?, toolAllowlist?[]}` | fine-grained MCP allow-list (mutually exclusive `serverUrl`/`command`, `anyOf` required) |
| `egressAllowlist` | string[] | extra outbound domains |
| `egressMode` | enum: `allow_all`, `parent_plus_network_settings`, `default_with_network_settings`, `network_settings_only` | how the allowlist combines with inherited team/user network policy |
| `chromeExecutablePath` | string | for browser-based testing |
| `enable_testing` | boolean or `"true"`/`"false"` | allow computer-use/cloud testing; default `true` |
| `ports` | array of `{name?, port: 1-65535}` | container ports to expose (devcontainer-style) |
| `terminals` | array (flat objects or arrays of objects) `{name?, command, description?}` | processes kept alive in a shared `tmux` session |

**`container` fields:**

| Field | Type | Description |
|---|---|---|
| `build.dockerfile` | string | path relative to the `environment.json`-containing folder |
| `build.dockerfileContents` | string | inline Dockerfile text (alternative to `dockerfile`) |
| `build.context` | string | build context path, relative to the environment.json folder |
| `image` | string | explicit registry image reference |
| `snapshot` | string | snapshot ID; **takes precedence over `build`/`image`** |
| `agentCanUpdateSnapshot` | boolean | default `true` for snapshot/default-base envs; always `false` for `build`/`image` base |

**Minimal examples** (both confirmed from live docs) — [docs/cloud-agent/setup](https://cursor.com/docs/cloud-agent/setup):
```json
{ "snapshot": "snapshot-20260212-00000000-0000-0000-0000-000000000000", "install": "npm install" }
```
```json
{ "build": { "dockerfile": "Dockerfile", "context": ".." }, "install": "pnpm install && ./custom_script.sh" }
```
Path quirk (explicit, easy to get wrong): `dockerfile`/`context` are relative to **`.cursor/`**, not the repo root; omitting `context` defaults to `.cursor`; the literal values `.`, `./`, `..` are special-cased to mean the **repo root** instead.

**Environment resolution order:** (1) `.cursor/environment.json` in the repo → (2) a personal saved environment → (3) a team saved environment.

**Secrets:** managed via the Secrets tab in the Cloud Agents dashboard (exposed as env vars), optionally **environment-scoped** (only available to agents using that one environment); supports OIDC-token minting and AWS IAM role assumption (`CURSOR_AWS_ASSUME_IAM_ROLE_ARN` + external ID + trust policy) as alternatives to long-lived keys.

**Self-Hosted Machines** (Pools / My Machines) run the same project hooks (+ team/enterprise hooks on Enterprise); `sessionStart`/`sessionEnd` fire on worker-claim/claim-release rather than being unsupported outright, unlike standard cloud agents — [docs/hooks](https://cursor.com/docs/hooks) → cross-referencing [docs/cloud-agent/self-hosted/pool](https://cursor.com/docs/cloud-agent/self-hosted/pool.md#hooks) (not independently re-fetched in this pass; **treat the Pools-specific hook timing detail as secondary/summarized from the hooks page, not independently verified against the Pools page itself**).

---

## (c) Porting notes — Lintel hooks → closest Cursor event

Grounded directly in Lintel's actual `hooks/hooks.json` (repo evidence: it is a **Claude-Code-plugin-format** file using `${CLAUDE_PLUGIN_ROOT}`, nested `matcher`+`hooks[]` arrays, PascalCase event names — i.e., written for Claude Code's own plugin hook auto-registration, per the file's own `_comment`/ADR-0008 reference). This is *not* the shape a Cursor Plugin's `hooks/hooks.json` expects (Cursor Plugin hooks use the flat, camelCase native schema shown in Q5/Q6), and it is *not* one of the seven paths Cursor's Claude-compatibility loader scans (`.claude/settings*.json` only) — so **today this file is invisible to Cursor either way**. Building a genuinely native integration means emitting a real `.cursor/hooks.json` (or a plugin-bundled `hooks/hooks.json` in Cursor's own schema), which the table below assumes.

| Lintel hook (from `hooks/hooks.json`) | Claude event + matcher | Closest Cursor event(s) | Blocking mechanism | Context-injection mechanism | Verdict |
|---|---|---|---|---|---|
| **session-start context digest** (`shared/session-digest`) | `SessionStart`, matcher `startup\|resume\|clear` | `sessionStart` | N/A — `sessionStart` is explicitly **fire-and-forget**; even `continue:false` doesn't block session creation | ✅ `additional_context` (added to initial system context) + `env` (session-scoped vars for later hooks) | **Portable, with one loss**: Cursor's `sessionStart` has **no documented `matcher`** — it fires uniformly for every new composer conversation. Lintel's `startup\|resume\|clear` granularity (e.g., skip digest on `clear`) cannot be replicated by config; the hook script itself would need to inspect `is_background_agent`/other input fields to approximate the distinction, or you accept it firing every time. **Not available in cloud agents** (explicitly excluded — cloud has no equivalent lifecycle boundary while it can still start read-only). |
| **pre-tool-use blocker: secrets in file edits** (`shared/no-secrets-in-edit`) | `PreToolUse`, matcher `Edit\|Write` | `preToolUse` with `"matcher": "Write"` | ✅ `{"permission":"deny","user_message":...,"agent_message":...}` | via `updated_input` if you want to auto-redact instead of hard-block | **Fully portable.** Note Cursor's tool taxonomy has no separate "Edit" tool name — file edits are all `Write` for matcher purposes. |
| **secret scanning in shell commands** (`shared/secret-scan-block`) | `PreToolUse`, matcher `Bash` | `beforeShellExecution` (preferred, dedicated) or `preToolUse` matcher `"Shell"` | ✅ full 3-state `allow\|deny\|ask` on `beforeShellExecution` (generic `preToolUse`'s `ask` is accepted but **not enforced**) | via `agent_message` | **Fully portable — use `beforeShellExecution`, not generic `preToolUse`**, since it gives you the real command string directly (`command` field) for regex/content scanning and supports `ask`. Cursor's own worked example in the docs is literally a git-command blocker with this exact shape (`block-git.sh`). Runs in cloud agents too. |
| **customer-data blocking (shell)** (`shared/customer-data-block`) | `PreToolUse`, matcher `Bash` | `beforeShellExecution` | ✅ same as above | via `agent_message` | **Fully portable**, same event as above; can co-exist as a second entry in the `beforeShellExecution` array (Cursor runs *all* matching hooks and merges responses, deny-wins). |
| **blocking direct git pushes to main** (`shared/no-direct-main-push`) | `PreToolUse`, matcher `Bash` | `beforeShellExecution`, with `matcher` prefiltering on `git push` and branch logic inside the script (parse `command`, same technique as Lintel's own script) | ✅ `permission: deny` | via `agent_message` telling the agent what to do instead | **Fully portable**, and doubly reinforceable: also add a **CLI-only** declarative `permissions.json`/`cli-config.json` `deny` entry as defense-in-depth (coarser — `Shell(git)` denies/allows by first token only, cannot itself express "only if target is main", so the hook script remains necessary for the actual logic; the declarative permission is a blunt backstop, not a replacement). |
| **post-edit memory-budget warning** (`shared/memory-budget-warn`) | `PostToolUse`, matcher `Edit\|Write` | `postToolUse` with `"matcher": "Write"` (preferred) — **not** `afterFileEdit` | ❌ not needed (informational) | ✅ `additional_context` on `postToolUse` | **Portable, with a schema caveat**: `afterFileEdit` (the more "obvious" name match) has **no documented output schema** in Cursor's reference — it only receives `{file_path, edits}` and nothing you return is consumed. Use `postToolUse` matched to `Write` instead, which explicitly documents `additional_context` as a supported response field. |
| **stop/turn-end "cycle incomplete" warning** (`shared/cycle-incomplete-warn`) | `Stop` (no matcher) | `stop` | N/A (runs at loop end) | ✅ `followup_message` — Cursor **auto-submits it as the next user message**, i.e. strictly more capable than Claude's block+reason (which just re-prompts) | **Fully portable, arguably improved.** Respect the default `loop_limit: 5` (configurable per hook, `null` = unlimited) to avoid infinite "keep going" loops — set this deliberately rather than relying on the default. Supported in cloud agents. |
| **per-prompt cycle-position context injection** (`shared/cycle-position-inject`) | `UserPromptSubmit` (no matcher) | `beforeSubmitPrompt` | (not needed) | **❌ No `additional_context`-equivalent field is documented for `beforeSubmitPrompt`** — its only outputs are `continue` (bool) and `user_message` (shown only when blocked) | **This is the one Lintel hook that does not have a clean native equivalent today.** `beforeSubmitPrompt` is a *gate*, not a *content injector*, per the documented schema. Practical workaround: have a different hook (e.g. `postToolUse`/`stop`) **rewrite a small always-applied rule file** (e.g. `.cursor/rules/_cycle-position.mdc` with `alwaysApply: true`, or an `AGENTS.md` fragment) with the current cycle-position text; since rules/`AGENTS.md` are re-read fresh each turn, the *next* prompt automatically picks up the update — this achieves the same practical effect one turn later, through the Rules surface rather than a Hooks surface. Flag this explicitly to whoever signs off on the port: it's a workaround, not a like-for-like hook. |
| **per-prompt customer-data check** (`shared/no-customer-data-in-message`) | `UserPromptSubmit` (no matcher) | `beforeSubmitPrompt` | ✅ `{"continue": false, "user_message": "..."}` | not needed (this hook only needs to gate, not inject) | **Fully portable** — this is exactly the shape `beforeSubmitPrompt` was designed for. |

**Overall packaging recommendation:** Ship a native `.cursor/hooks.json` (or, better, bundle it inside `.cursor-plugin/hooks/hooks.json` referenced from Lintel's existing `.cursor-plugin/plugin.json`, which today only declares `"skills"` and `"agents"` — it needs `"hooks"` and, if Lintel has rule-equivalent content, `"rules"` added). Do **not** rely on the `.claude/settings.json` third-party passthrough as the primary path: it is (1) a compatibility shim explicitly framed as such, (2) user-togglable (Settings → Agents → Third-Party Imports; on by default but user can turn it off), (3) not listed as one of the cloud-agent hook sources at all, and (4) the current Lintel file isn't even at one of the three scanned paths (`.claude/settings.json`, `.claude/settings.local.json`, `~/.claude/settings.json`) — it lives at `hooks/hooks.json`. If Lintel wants a defense-in-depth layer, additionally emit a `.claude/settings.json` with the same logic (Cursor will merge it in, deny-wins), but treat that as a *secondary* safety net, not the system of record — the native `.cursor/hooks.json`/plugin-bundled hooks file should be authoritative so the integration doesn't silently stop working if a user (or an Enterprise admin) disables third-party imports.

**Two structural gaps worth flagging to whoever owns the Lintel↔Cursor port**, beyond the hook mapping table:

1. **No tool-scoping on skills or subagents.** Lintel's `SKILL.md` frontmatter carries a `tools: Read, Bash, Edit, Glob` field (verified directly in `skills/adr-new/SKILL.md`), and presumably Lintel's ~60 subagent role definitions carry similar restrictions. Cursor's `SKILL.md` schema has no tool-scoping field at all, and its subagent schema has only the boolean `readonly`. Porting will silently drop this restriction unless enforced elsewhere — the only native lever left is `readonly: true` on a `.cursor/agents/*.md` subagent (all-or-nothing), or a `beforeShellExecution`/`preToolUse` hook that inspects which skill/subagent is "active" (not itself exposed to hooks in any field I found — `preToolUse`/`beforeShellExecution` payloads carry `tool_name`/`cwd`/`command`, not "current skill" or "current subagent" identity for the *top-level* agent's own tool calls) and denies accordingly. Recommend documenting this as a known, accepted gap rather than assuming silent parity.
2. **Extra Lintel frontmatter fields are inert, not rejected.** Fields like `layer: foundation`, `voice: internal`, `cli_support: [claude-code, codex]` in `skills/adr-new/SKILL.md` are not part of Cursor's documented `SKILL.md` schema. Nothing in the docs suggests Cursor errors on unknown keys, but nothing confirms they're preserved/read either — safest path is to fold anything Lintel needs to retain into the explicitly-supported `metadata:` map (a documented arbitrary key-value passthrough) rather than inventing new top-level keys, and to add `cursor` to any `cli_support` enumeration as part of the native-artifact generation step.

---

## (d) UNVERIFIED items and open questions

Consolidated from flags raised throughout this report, plus a few additional open items:

**Confirmed only in secondary/community sources (not `cursor.com` primary, not a staff forum post):**
- Exact shell/interpreter behavior for hook `command` execution on **native Windows** (whether shebang lines work, whether PowerShell wrapping is required). Docs confirm Windows *config* paths exist; they do not document Windows *execution* semantics. Forum threads describing bash-shebang failures and `.ps1`-wrapper workarounds are user reports, not staff-confirmed fixes.
- Whether `${CURSOR_PLUGIN_ROOT}`/`${CLAUDE_PLUGIN_ROOT}` variable expansion applies inside a plugin's `hooks/hooks.json` `command` strings (explicitly documented only for `mcp.json`'s `command`/`args`/`env`/`cwd`).
- The exact argument-passing mechanism (if any) for Custom Commands (no `$ARGUMENTS`-style placeholder found in any primary Cursor doc; unclear whether text typed after `/command-name` is appended as plain chat text or substituted into the command body).
- The precise bare, non-plugin project path for commands (`.cursor/commands/` is the natural inference by symmetry with `.cursor/rules`, `.cursor/skills`, `.cursor/agents`, and is asserted by several third-party guides, but I did not find it stated verbatim on any `cursor.com` page — the only primary schema for "Commands" I found is scoped to the plugin `commands/` folder).
- Whether `CLAUDE.md` is read by **cloud agents** specifically (confirmed for editor via help-center FAQ, confirmed for CLI via `docs/cli/using`, but the cloud-agent docs I fetched only explicitly name-check `AGENTS.md`, not `CLAUDE.md`, when describing what cloud agents read).
- Whether an *installed marketplace plugin's* bundled skills/rules/agents (as opposed to hooks) are made available to cloud agent runs the same way plain repo files are — the hooks page is explicit that cloud agents load project hooks "from your repository," but I found no equivalently explicit statement for plugin-bundled skills/rules/agents reaching the cloud VM when the plugin itself isn't just files already checked into the repo.
- Cross-plugin name-collision behavior for skills/rules/agents/commands (I found a precedence rule for `.cursor/` vs `.claude/`/`.codex/` compatibility directories, and for Project vs Team vs User rules, but nothing for two *installed plugins* declaring the same skill/agent name).
- Self-Hosted Machine (Pools) `sessionStart`/`sessionEnd` timing-on-claim/release detail — sourced from a cross-reference on the main hooks page pointing to a Pools-specific subpage I did not independently re-fetch in full.
- Exact current Cursor **application version number** as of the retrieval date. Primary `cursor.com/changelog` confirms the most recent entries are date-labeled rather than version-numbered (a Rollouts/Security-Review release, undated in the markdown I fetched but corroborated by search as ~Sept 23 2026; a Projects beta ~Sept 10 2026; Self-Hosted Machines ~Sept 2 2026), suggesting Cursor moved away from strict `X.Y` changelog slugs sometime after **2.6**. A specific claim of "Cursor v3.22.7 (Sept 24, 2026)" surfaced only from third-party aggregator sites (not `cursor.com`) — **do not rely on that specific patch number**.
- Whether Cursor enforces any of the base **Agent Skills open standard's** optional fields (`license`, `compatibility`, `allowed-tools`) even though its own documented `SKILL.md` frontmatter table omits them.
- Whether `preToolUse`'s documented-but-unenforced `"ask"` permission value, or `subagentStart`'s explicit "`ask` is treated as deny," are stable long-term semantics or a currently-in-flux implementation detail (the docs phrase both with hedges like "not enforced **today**").

**Explicitly stated as beta/private-beta/in-flux by Cursor itself (not a gap in my research — a genuine product-maturity flag to carry into planning):**
- Hooks shipped labeled **"(beta)"** at launch (Cursor 1.7); current docs no longer carry a beta label, but no explicit "hooks are now GA" statement was found either.
- "Cursor-configured Dockerfiles" for cloud environments are explicitly **"private beta,"** Enterprise-only, request-access-only.
- `/goal` (durable goal tracking) in the CLI is explicitly **"rolling out."**
- Subagent nesting (subagent-launches-subagent) is **"Since Cursor 2.5"** — a recent capability, worth version-gating any Lintel logic that assumes it.

**Open questions for the main agent / Lintel maintainers to decide (product decisions, not documentation gaps):**
1. Should the native port target the **flat Cursor-native hook schema** exclusively, or also keep shipping the existing Claude-shaped `hooks/hooks.json` for genuine Claude Code users, accepting that Cursor will not read that specific file (it isn't on the three scanned `.claude/settings*.json` paths) unless it's duplicated/symlinked there too?
2. For the cycle-position per-prompt injection gap (no native `beforeSubmitPrompt` context-injection field): is the "rewrite an always-applied rule file one turn late" workaround acceptable, or does Lintel need to file a Cursor feature request and accept a temporary capability loss on this one surface?
3. Given Cursor's own `/migrate-to-skills` and `/create-skill`/`/create-hook`/`/create-subagent` built-ins exist specifically to *generate* these artifacts, is there value in having Lintel's generator shell out to (or mimic the output shape of) those built-ins for maximum forward-compatibility with future Cursor schema changes, rather than hand-rolling the schema independently?
4. Whether to register Lintel's ~96 skills as a **single Cursor Plugin** (current `.cursor-plugin/plugin.json` already exists and could be extended) versus per-pack plugins — the marketplace model (Q6) suggests one plugin per logical unit is idiomatic, and Lintel's existing single-manifest layout is already aligned with that.

---

## Primary source index (all fetched live, 2026-09-28)

- Skills: https://cursor.com/docs/skills · https://cursor.com/help/customization/skills
- Rules / AGENTS.md / CLAUDE.md / `.cursorrules`: https://cursor.com/docs/rules · https://cursor.com/help/customization/rules
- Commands: https://cursor.com/docs/customize-cursor · https://cursor.com/docs/reference/plugins
- Subagents: https://cursor.com/docs/subagents
- Hooks: https://cursor.com/docs/hooks · https://cursor.com/docs/reference/third-party-hooks
- Plugins: https://cursor.com/docs/plugins · https://cursor.com/docs/reference/plugins
- Cloud agents / environment: https://cursor.com/docs/cloud-agent · https://cursor.com/docs/cloud-agent/setup · https://cursor.com/docs/cloud-agent/capabilities · https://cursor.com/schemas/environment.schema.json
- CLI: https://cursor.com/docs/cli/overview · https://cursor.com/docs/cli/installation · https://cursor.com/docs/cli/using · https://cursor.com/docs/cli/reference/slash-commands · https://cursor.com/docs/cli/reference/configuration · https://cursor.com/docs/cli/reference/permissions · https://cursor.com/docs/cli/changelog
- Run modes / permissions context: https://cursor.com/docs/agent/security/run-modes
- Changelog anchors: https://cursor.com/changelog/1-7 (Hooks beta) · https://cursor.com/changelog/2-4 (Subagents + Skills) · https://cursor.com/changelog/2-5 (Plugins/Marketplace) · https://cursor.com/changelog/2-6 (Team Marketplaces) · https://cursor.com/changelog/customize · https://cursor.com/changelog/cli-jan-08-2026 (CLI hooks perf + `agent` rename) · https://cursor.com/changelog (root, current as of retrieval)

**Lintel repo evidence used for grounding (this workspace):** `hooks/hooks.json`, `hooks/claude-code/session-digest.settings.json`, `.cursor-plugin/plugin.json`, `skills/adr-new/SKILL.md`.

This closes out all seven questions with primary-source citations, the requested capability matrix, full schemas/examples, the hook-by-hook porting map, and a consolidated UNVERIFIED list. No repository files other than this report were modified during this research.
