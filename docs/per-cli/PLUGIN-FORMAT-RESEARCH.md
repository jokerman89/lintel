# Per-CLI plugin format research (Phase 0)

**Date:** 2026-05-27
**Researcher:** Claude Code (Opus 4.7)
**Sources:** Official Anthropic docs + obra/superpowers production plugin manifests + per-CLI marketplace docs.

This document captures the actual plugin-manifest format per CLI as of v3 planning. It's the source-of-truth that drives the manifests we ship.

---

## 1. Claude Code

**Source:** [code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins)

**Manifest location:** `.claude-plugin/plugin.json` (only plugin.json goes in `.claude-plugin/`, NOT skills/agents/hooks).

**Schema (minimal):**
```json
{
  "name": "jstack",
  "description": "MS-CAIP-SE session harness",
  "version": "3.0.0",
  "author": { "name": "Azureflipper", "email": "johannes.akerman@microsoft.com" },
  "homepage": "https://github.com/Azureflipper/jokerman-session-setup",
  "repository": "https://github.com/Azureflipper/jokerman-session-setup",
  "license": "MIT",
  "keywords": ["microsoft", "caip", "rais", "compliance", "session-harness"]
}
```

**Directory structure (at plugin root, NOT inside .claude-plugin):**
- `skills/<name>/SKILL.md` — model-invokable skills (slash-commands namespaced as `/jstack:<skill>`)
- `commands/<name>.md` — legacy flat skills (use `skills/` for new plugins)
- `agents/<name>.md` — subagent definitions
- `hooks/hooks.json` — event handlers (same format as `.claude/settings.json` hooks block)
- `.mcp.json` — MCP server configs (optional)
- `.lsp.json` — LSP server configs
- `monitors/monitors.json` — background monitors
- `bin/` — executables added to Bash tool's PATH when plugin is active
- `settings.json` — default settings (only `agent` + `subagentStatusLine` supported)

**Skill namespace:** `/<plugin-name>:<skill>` — e.g. `/jstack:qa`. This protects against conflicts.

**Marketplace:**
- `claude-plugins-official` (curated by Anthropic, no application process)
- `claude-plugins-community` (community-submitted via claude.ai/settings/plugins/submit, reviewed)
- Team marketplaces: `/plugin marketplace add <owner>/<repo>` then `/plugin install jstack@<repo>`

**For JStack:** Team marketplace pattern. MS-CAIP-SE operators run:
```
/plugin marketplace add Azureflipper/jokerman-session-setup
/plugin install jstack@jokerman-session-setup
```

**Plus:** A `.claude-plugin/marketplace.json` if we want to expose JStack-as-a-marketplace that contains multiple plugins (e.g. jstack-core + jstack-ms + jstack-doc-gen). For now: single plugin, single manifest.

**Validation:** `claude plugin validate <path>` locally before any submission.

---

## 2. Codex CLI / Codex App

**Source:** obra/superpowers `.codex-plugin/plugin.json` (production-verified).

**Manifest location:** `.codex-plugin/plugin.json`

**Schema (with `interface{}` block for app UI):**
```json
{
  "name": "jstack",
  "version": "3.0.0",
  "description": "MS-CAIP-SE session harness for OpenAI Codex",
  "author": { "name": "Azureflipper", "email": "...", "url": "https://github.com/Azureflipper" },
  "homepage": "https://github.com/Azureflipper/jokerman-session-setup",
  "repository": "https://github.com/Azureflipper/jokerman-session-setup",
  "license": "MIT",
  "keywords": ["microsoft", "caip", "rais", "session-harness"],
  "skills": "./skills/",
  "interface": {
    "displayName": "JStack",
    "shortDescription": "MS-CAIP-SE session harness — RAIS, OneCS, Trailblazer voice",
    "longDescription": "...",
    "developerName": "Azureflipper",
    "category": "Coding",
    "capabilities": ["Interactive", "Read", "Write"],
    "defaultPrompt": ["Hjälp mig med ett nytt customer engagement.", "Kör /qa på min branch."],
    "websiteURL": "...",
    "privacyPolicyURL": "...",
    "termsOfServiceURL": "...",
    "brandColor": "#0078D4",
    "composerIcon": "./assets/jstack-small.svg",
    "logo": "./assets/app-icon.png",
    "screenshots": []
  }
}
```

**Required for Codex App store submission:** Full `interface{}` block + privacy/terms URLs + icons. For Codex CLI alone: minimal manifest sufficient.

**Marketplace:**
- Codex CLI: in interactive mode, `/plugins` → search → install
- Codex App: sidebar → Plugins → `+` → install
- Plugin source: OpenAI's plugins marketplace at `github.com/openai/plugins`

**Submission:** Via openai/plugins repo PR (or similar — verify before submission).

**Top-level AGENTS.md:** Codex reads `AGENTS.md` at repo root as context file. We need to write one that points to AGENT-INSTRUCTIONS.md.

---

## 3. Cursor

**Source:** obra/superpowers `.cursor-plugin/plugin.json` (production-verified).

**Manifest location:** `.cursor-plugin/plugin.json`

**Schema (richer than Claude, includes hooks):**
```json
{
  "name": "jstack",
  "displayName": "JStack",
  "description": "MS-CAIP-SE session harness",
  "version": "3.0.0",
  "author": { "name": "Azureflipper", "email": "..." },
  "homepage": "https://github.com/Azureflipper/jokerman-session-setup",
  "repository": "https://github.com/Azureflipper/jokerman-session-setup",
  "license": "MIT",
  "keywords": ["microsoft", "caip", "session-harness"],
  "skills": "./skills/",
  "agents": "./agents/",
  "commands": "./commands/",
  "hooks": "./hooks/cursor/hooks-cursor.json"
}
```

**Install command:**
```
/add-plugin jstack
```
(in Cursor Agent chat)

**Marketplace:** Cursor plugin marketplace — search by name post-publish.

**Hooks format:** `hooks-cursor.json` differs from Claude's `hooks.json`. Cursor uses different event types. Verify format before writing.

---

## 4. Gemini CLI

**Source:** obra/superpowers `gemini-extension.json` (production-verified).

**Manifest location:** `gemini-extension.json` (at repo root, not in subdirectory!)

**Schema (minimal):**
```json
{
  "name": "jstack",
  "description": "MS-CAIP-SE session harness for Gemini",
  "version": "3.0.0",
  "contextFileName": "GEMINI.md"
}
```

**Install command:**
```
gemini extensions install https://github.com/Azureflipper/jokerman-session-setup
```

**Update command:** `gemini extensions update jstack`

**Top-level GEMINI.md:** Required. Acts as context file Gemini loads on session start. Should point to AGENT-INSTRUCTIONS.md.

**Skill discovery:** Gemini extensions are simpler than other CLIs — they rely on the context file (GEMINI.md) plus markdown content. No explicit skill-discovery mechanism, so we list skill triggers within GEMINI.md.

---

## 5. OpenCode

**Source:** obra/superpowers `.opencode/INSTALL.md` + `.opencode/plugins/` (production-verified).

**Manifest location:** `.opencode/INSTALL.md` (markdown-based install instructions) + per-skill plugins in `.opencode/plugins/`.

**Schema:** Markdown instructions, not JSON.

**Install command:**
```
Fetch and follow instructions from https://raw.githubusercontent.com/Azureflipper/jokerman-session-setup/refs/heads/main/.opencode/INSTALL.md
```

The operator literally tells OpenCode to fetch and follow the INSTALL.md. OpenCode then does the install steps documented there.

**Format:** Custom per-project. We need to write a well-structured INSTALL.md that OpenCode can follow:
1. Add JStack to OpenCode's plugins dir
2. Symlink skills/, agents/
3. Configure context-file (likely AGENTS.md or similar)

**Status:** Best-effort. OpenCode has the loosest format; we test post-write.

---

## 6. Factory Droid

**Source:** Superpowers README + droid CLI docs.

**Install command:**
```bash
droid plugin marketplace add https://github.com/Azureflipper/jokerman-session-setup
droid plugin install jstack@jstack
```

**Manifest location:** `.droid-plugin/plugin.json` (inferred from pattern). Verify before writing.

**Schema:** Unknown without further research. Pattern suggests similar to Claude/Codex (name, version, description, license, points to skills/agents).

**Action:** Phase 0 follow-up — verify Factory Droid plugin spec by checking their docs or asking the marketplace owner.

---

## 7. GitHub Copilot CLI

**Source:** Superpowers README.

**Install command:**
```bash
copilot plugin marketplace add Azureflipper/jokerman-session-setup
copilot plugin install jstack@jokerman-session-setup
```

**Manifest location:** `.copilot-plugin/plugin.json` (inferred). Verify before writing.

**Important distinction:** GitHub Copilot CLI (`gh copilot`) is DIFFERENT from GitHub Copilot in VSCode/JetBrains:
- Copilot CLI = standalone command-line tool with newer plugin system
- Copilot VSCode = uses `.github/copilot-instructions.md` + `.github/prompts/*.prompt.md` (different mechanism)

For v3 we target **Copilot CLI** (has plugin system). VSCode Copilot remains via copilot-instructions.md shim (existing v2 pattern).

---

## 8. GitHub Copilot VSCode/JetBrains

**Source:** GitHub Copilot Custom Instructions docs.

**Mechanism (NOT a plugin):** `.github/copilot-instructions.md` at repo root.

**Plus:** `.github/prompts/<name>.prompt.md` for slash-commands (VSCode 2024-Q4+).

**For JStack:** This is the v2 shim pattern. v3 keeps `shims/copilot-instructions.md` as fallback for VSCode/JetBrains Copilot, but primary install for Copilot CLI uses the plugin manifest.

---

## 9. Summary table

| CLI | Manifest format | Manifest location | Marketplace | v3 status |
|---|---|---|---|---|
| Claude Code | JSON | `.claude-plugin/plugin.json` | `claude-plugins-official` (curated) + team via `/plugin marketplace add` | ✓ DONE — pattern verified |
| Codex CLI/App | JSON with `interface{}` | `.codex-plugin/plugin.json` | OpenAI marketplace | ✓ Pattern verified (superpowers) |
| Cursor | JSON | `.cursor-plugin/plugin.json` | Cursor marketplace | ✓ Pattern verified (superpowers) |
| Gemini CLI | JSON (tiny) | `gemini-extension.json` (root) | Gemini extensions | ✓ Pattern verified (superpowers) |
| OpenCode | Markdown | `.opencode/INSTALL.md` | None (URL fetch) | ✓ Pattern verified (superpowers) |
| Copilot CLI | JSON (unknown schema) | `.copilot-plugin/plugin.json` (inferred) | `copilot plugin marketplace add` | ⚠ Need to verify exact schema |
| Factory Droid | JSON (unknown schema) | `.droid-plugin/plugin.json` (inferred) | `droid plugin marketplace add` | ⚠ Need to verify exact schema |
| Copilot VSCode | Markdown | `.github/copilot-instructions.md` | n/a (shim) | ✓ v2 fallback pattern |

---

## 10. Action items

**Confirmed schemas (write manifests now):**
- ✓ `.claude-plugin/plugin.json`
- ✓ `.codex-plugin/plugin.json` (with full `interface{}` block)
- ✓ `.cursor-plugin/plugin.json`
- ✓ `gemini-extension.json` + root `GEMINI.md`
- ✓ `.opencode/INSTALL.md` + `.opencode/plugins/`

**Needs follow-up research (write best-guess, refine in Phase 8):**
- ⚠ `.copilot-plugin/plugin.json` — write minimal, document as "experimental until schema confirmed"
- ⚠ `.droid-plugin/plugin.json` — same

**Entrypoint context files (write at repo root):**
- ✓ `CLAUDE.md` (existing — keep at shims/, also at root pointing to AGENT-INSTRUCTIONS.md)
- ✓ `AGENTS.md` (existing — at shims/, also at root for Codex)
- ✓ `GEMINI.md` (NEW for v3)

**Validation:**
- `claude plugin validate` for Claude manifest
- Manual format-check JSON-files
- Tests: `tests/unit/plugin-manifests-valid.sh` schema check

---

## 11. Constraints we accept

- **MS-internal first.** Public marketplace submission requires MS legal review. Default v3.0.0 ships only the team-marketplace pattern (`/plugin marketplace add Azureflipper/jokerman-session-setup`). Public submission deferred to v3.x post-legal-clear.
- **Per-CLI UX differences accepted.** Skill-namespacing differs (Claude `/jstack:qa` vs others), hook formats differ, subagent mechanisms differ. We document, don't normalize.
- **Schema-drift over time.** CLIs update plugin specs. We commit to verify per-CLI version every release.

---

*Research complete 2026-05-27. v3-dev Phase 0 done.*
