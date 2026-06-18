---
name: help
layer: foundation
description: List the Lintel skills + agents + hooks available in this session. Filter by category, voice tier, or CLI support.
color: blue
tools: Read, Bash, Grep, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
  - cli: copilot
    level: degraded
---

# /li:help

Meta-skill. Lists what Lintel makes available in this session so the operator knows what they can
run, without grepping the plugin tree. A quick in-session lister; for the full generated reference
see `/li:catalog` (it builds `skills/CATALOG.md` from frontmatter), and for install/version health
see `/li:doctor`.

## When to use

- First session after install — discover what's there
- Picking the right skill for a task (filter by category)
- Onboarding a teammate to Lintel
- Debugging "is this skill available?" / "is it the right CLI?"

## Inputs

Optional flags:
- `--category <name>` — filter to one category (`plan`, `qa`, `ship`, `compliance`, `voice`, `meta`, `ops`)
- `--voice <internal|customer|mixed>` — filter by voice tier
- `--cli <claude-code|codex|copilot>` — show only skills supported on a specific CLI
- `--verbose` — include description per entry (default: one-line entries)

No arguments: full list grouped by category, one line per skill.

## Workflow

Lintel ships as a plugin, so skills/agents/hooks are resolved from the installed plugin — not from a
hand-managed `~/.claude/` tree.

1. Resolve the plugin root: `${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}`.
2. Glob `"$root"/skills/*/SKILL.md` for the available skills (they are invoked namespaced as `/li:<name>`).
3. Glob `"$root"/agents/*/*.md` for the subagent fleet (resolve by name via the Agent tool).
4. For each skill/agent, parse YAML frontmatter for: name, description, voice, cli_support, color.
5. Filter per operator's flags.
6. Group by category (heuristic from skill name: `plan-*` → plan, `qa*` → qa, etc.).
7. Output structured list. Read the plugin version from `"$root"/.claude-plugin/plugin.json`.

## Report format

**Default (full list):**
```
Lintel v<version> — <N skills>, <M agents>, <K hooks>

## Plan (<count>)
- /li:plan-ceo-review     [internal, all CLIs] — Strategy & scope review
- /li:plan-eng-review     [internal, all CLIs] — Architecture & tests review
- /li:plan-design-review  [internal, claude-code] — UI/UX gaps
- /li:plan-devex-review   [internal, all CLIs] — DX gaps

## QA + debug (<count>)
- /li:qa                  [internal, claude-code] — Real-browser testing
- /li:qa-only             [internal, claude-code] — Test-only flow
- /li:investigate         [internal, all CLIs] — Bug forensics
- /li:review              [internal, all CLIs] — Diff-scoped pre-ship review

## Voice (<count>)
- /li:eval               [internal, claude-code] — Calibrate the pack's voice corpus

## Compliance (<count>)
- /li:compliance-gate    [internal, all CLIs] — Run the active pack's compliance gates

## Meta + ops (<count>)
- /li:context-save       [internal, claude-code] — Save checkpoint
- /li:context-restore    [internal, claude-code] — Read checkpoint
- /li:clean              [internal, claude-code] — Manual self-maintenance
- /li:help               [internal, all CLIs] — This skill
- /li:doctor             [internal, all CLIs] — Install/version/hook health check

## Agents (the plugin fleet)
- CodeReviewer           [engineering, claude-code] — Reviews diffs for correctness/quality/security
- SecurityAuditor        [security, claude-code] — Injection/secret/auth-bypass audit
- ...  (run /li:catalog for the full list)

## Hooks (activation per ADR-0008)
- Auto-registered on plugin install (9): session-digest, secret-scan-block, customer-data-block,
  no-secrets-in-edit, no-direct-main-push, memory-budget-warn, cycle-incomplete-warn,
  cycle-position-inject, no-customer-data-in-message
- Opt-in module warn-hooks (24): the ta/da/sc/dh/tq-* warn hooks — enable via a `~/.lintel/hooks`
  symlink. Run /li:hooks-status for live state.
```

**Filtered by category:**
```
> /li:help --category qa
QA + debug skills:
- /li:qa            [internal, claude-code]
- /li:qa-only       [internal, claude-code]
- /li:investigate   [internal, all CLIs]
- /li:review        [internal, all CLIs]
```

**Filtered by CLI (Copilot user):**
```
> /li:help --cli copilot
Lintel skills supported on Copilot Enterprise:
- /li:plan-ceo-review   [internal]
- /li:plan-eng-review   [internal]
- /li:investigate       [internal]
- /li:help              [internal]
- /li:doctor            [internal]

Copilot has no slash-command mechanism. Use the canonical-instructions
shim at .github/copilot-instructions.md for the parts that DO port.
```

## Edge cases

- **Plugin root not resolvable:** report "Lintel plugin not detected — install via `/plugin install li@jokerman-lintel`, then restart the session."
- **Skill missing frontmatter fields:** flag the skill (`⚠ <name>: missing cli_support`) — report it.
- **Filter matches zero skills:** report "no skills match these filters" + suggest dropping a flag.
- **Version drift across CLIs:** defer to `/li:doctor`, which is the cross-CLI drift checker.

## Failure modes

- **No `skills/` under the plugin root:** report "no Lintel skills found at the plugin root."
- **Frontmatter parse error in a skill:** skip that skill, report which one was unparseable.

## Examples

```
> /li:help
[full list output]

> /li:help --category compliance --verbose
Lintel compliance skills:
- /li:compliance-gate  [internal, all CLIs]
    Runs the active pack's compliance gates (`resolve_pack_field
    compliance.hooks`; none by default). Surfaces results; does NOT
    enforce — operator confirms.

> /li:help --voice customer
Lintel customer-voice skills:
- /li:eval  [claude-code]
```

## See also

- `/li:catalog` — the full generated skill reference (built from frontmatter)
- `/li:doctor` — install + version + hook-firing health (cross-CLI)
- `/li:hooks-status` — live hook activation state
- `AGENT-INSTRUCTIONS.md` — canonical session-start ritual
