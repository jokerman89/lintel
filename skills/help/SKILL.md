---
name: li-help
layer: foundation
description: List installed Lintel skills + agents + hooks. Filter by category, voice tier, or CLI support.
color: blue
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# /help

Meta-skill. Lists what Lintel has installed on this machine so the operator knows what's available without grep-ing `~/.claude/skills/`.

## When to use

- First session after install — discover what's there
- Picking the right skill for a task (filter by category)
- Onboarding a teammate to Lintel
- Debugging "is this skill installed?" / "is it the right CLI?"

## Inputs

Optional flags:
- `--category <name>` — filter to one category (`plan`, `qa`, `ship`, `compliance`, `voice`, `meta`, `ops`)
- `--voice <internal|trailblazer|mixed>` — filter by voice tier
- `--cli <claude-code|codex|copilot>` — show only skills supported on a specific CLI
- `--verbose` — include description per entry (default: one-line entries)

No arguments: full list grouped by category, one line per skill.

## Workflow

1. Read `INSTALL-MANIFEST.json` if present at `~/.claude-scaffolding/` to confirm install version.
2. Glob `~/.claude/skills/lintel:li-*/SKILL.md` for installed skills.
3. Glob `~/.claude/agents/*.md` for installed agents (filter to Lintel-relevant: check for `cli_support` field).
4. For each skill/agent, parse YAML frontmatter for: name, description, voice, cli_support, color.
5. Filter per operator's flags.
6. Group by category (heuristic from skill name: `plan-*` → plan, `qa*` → qa, etc.).
7. Output structured list.

## Report format

**Default (full list):**
```
Lintel v<version> — <N skills>, <M agents>, <K hooks>

## Plan (<count>)
- /plan-ceo-review     [internal, all CLIs] — Strategy & scope review
- /plan-eng-review     [internal, all CLIs] — Architecture & tests review
- /plan-design-review  [internal, claude-code] — UI/UX gaps
- /plan-devex-review   [internal, all CLIs] — DX gaps

## QA + debug (<count>)
- /qa                  [internal, claude-code] — Real-browser testing
- /qa-only             [internal, claude-code] — Test-only flow
- /investigate         [internal, all CLIs] — Bug forensics
- /review              [internal, all CLIs] — Diff-scoped pre-ship review

## Voice (<count>)
- /rais-customer-voice-check [trailblazer, claude-code] — Eval against MS Our Voice grid
- /msvoice-rewrite     [trailblazer, claude-code] — Rewrite to specific Provoke technique

## Compliance (<count>)
- /compliance-check    [internal, all CLIs] — Run 7 on-demand rules

## Meta + ops (<count>)
- /context-save        [internal, claude-code] — Save checkpoint
- /context-restore     [internal, claude-code] — Read checkpoint
- /clean               [internal, claude-code] — Manual self-maintenance
- /help                [internal, all CLIs] — This skill
- /health              [internal, all CLIs] — Install/upstream status check

## Agents available at user-global
- AgentShield          [Level 3, permissive, claude-code]
- CodeReviewer         [Level 4, internal, claude-code]
- ...

## Hooks at ~/.lintel/hooks/ (activate via symlink to ~/.claude/hooks/)
- li-token-watcher       [warn-only, INACTIVE]
- li-secret-scan         [block, INACTIVE]
- li-customer-data-block [block, INACTIVE]
- ...

Manifest: ~/.claude-scaffolding/INSTALL-MANIFEST.json (v1.0.0, installed 2026-05-27)
```

**Filtered by category:**
```
> /help --category qa
QA + debug skills:
- /qa            [internal, claude-code]
- /qa-only       [internal, claude-code]
- /investigate   [internal, all CLIs]
- /review        [internal, all CLIs]
```

**Filtered by CLI (Copilot user):**
```
> /help --cli copilot
Lintel skills supported on Copilot Enterprise:
- /plan-ceo-review     [internal]
- /plan-eng-review     [internal]
- /investigate         [internal]
- /help                [internal]
- /health              [internal]

NOT supported on Copilot (Claude Code only):
- /qa, /qa-only, /design-review, /context-save, /clean, ...

Copilot has no slash-command mechanism. Use the canonical-instructions
shim at .github/copilot-instructions.md for the parts that DO port.
```

## Edge cases

- **No Lintel installed:** report "Lintel not detected at ~/.claude-scaffolding/. Run `bash install/install.sh` from the Lintel repo first."
- **Skill missing frontmatter fields:** flag the skill (`⚠ li-X: missing cli_support`) — operator should re-install or report.
- **Filter matches zero skills:** report "no skills match these filters" + suggest dropping a flag.
- **Multiple Lintel versions installed (manifest + filesystem disagree):** flag drift.

## Compliance integration

None — read-only meta information.

## Failure modes

- **`~/.claude/skills/` doesn't exist:** report "no Claude Code skills directory found."
- **Frontmatter parse error in a skill:** skip that skill, report which one was unparseable.

## Examples

```
> /help
[full list output]

> /help --category compliance --verbose
Lintel compliance skills:
- /compliance-check  [internal, all CLIs]
    Runs the 7 on-demand compliance rules (OneRAI registration, threat
    model, DPIA, transparency doc, sensitive-use report, SAST, Entra
    Agent ID). Surfaces results; does NOT enforce — operator confirms.

> /help --voice trailblazer
Lintel trailblazer-voice skills:
- /rais-customer-voice-check  [claude-code]
- /msvoice-rewrite       [claude-code]
- /demo-deliverable-gen  [claude-code]
```

## See also

- `/health` — install + upstream status (sibling skill)
- `LAYERS.md` at repo root — architecture overview
- `AGENT-INSTRUCTIONS.md` — canonical session-start
