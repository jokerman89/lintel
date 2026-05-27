---
name: jstack-doctor
layer: foundation
description: Cross-CLI health check — verifies which CLIs are installed, plugin install status, JStack version, and surfaces drift.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the jstack-doctor skill.

## What this skill does

Diagnostic health-check across operator's machine. Detects which AI CLIs are installed, whether JStack is installed in each, version skew between them, and any drift (e.g., one CLI on v3.0.0, another on v2.x).

## When to use

- Onboarding new operator — verify setup
- Suspect JStack not loading in CLI X
- Quarterly health review
- Pre-engagement-start — confirm tools ready

## When NOT to use

- Single-CLI use — overkill (CLI's native plugin-list is enough)
- Inside CI/automation — different scope

## Workflow

1. **Detect installed CLIs.** Check PATH for:
   - `claude` (Claude Code)
   - `codex` (Codex CLI)
   - `cursor` (Cursor)
   - `gemini` (Gemini CLI)
   - `opencode` (OpenCode)
   - `copilot` (GitHub Copilot CLI)
   - `droid` (Factory Droid)

2. **Per detected CLI, check JStack install:**
   - Claude Code: `~/.claude/plugins/jstack/` or `~/.claude/marketplaces/jokerman-session-setup/`
   - Codex: depends on Codex install dir
   - Cursor: `~/.cursor/extensions/` or similar
   - Gemini: `gemini extensions list | grep jstack`
   - OpenCode: `.opencode/plugins/jstack/`
   - Copilot: `copilot plugin list | grep jstack`
   - Droid: `droid plugin list | grep jstack`

3. **Per install, read version** (from plugin.json in each CLI's plugin dir).

4. **Cross-CLI drift detection.** If versions differ across CLIs, flag.

5. **Check scaffolding install.** `~/.jstack/scaffolding/` populated?

6. **Check brand assets.** `~/.jstack/brand/` present + age (warn if >90 days via `brand-staleness-warn` hook).

7. **Hook activation status.** `~/.jstack/hooks/<name>` symlinks vs canonical.

## Output format

```
JSTACK-DOCTOR: health check (date)

## CLIs detected
| CLI | Path | Version | JStack installed | JStack version |
|---|---|---|---|---|
| claude | /usr/local/bin/claude | 2.1.x | ✓ | 3.0.0 |
| codex | /usr/local/bin/codex | x.y | ✓ | 3.0.0 |
| cursor | n/a (app) | UI | ✓ | 3.0.0 |
| gemini | ~/bin/gemini | x.y | ✗ NOT INSTALLED | — |
| opencode | n/a | n/a | — | — |
| copilot | /usr/local/bin/copilot | x.y | ✓ | 2.0.5 ⚠ drift |
| droid | n/a | n/a | — | — |

## Drift detected
- Copilot CLI on JStack v2.0.5 vs others on v3.0.0
  → Action: `copilot plugin update jstack`

## Scaffolding
- ~/.jstack/scaffolding/: ✓ present, last updated <date>

## Brand assets
- ~/.jstack/brand/: ⚠ 95 days old (>90 day threshold)
  → Action: invoke `/brand-update` skill

## Hooks
- Activated: <N>/15 (operator opt-in)
- See: ~/.jstack/hooks/

## Voice corpus
- Status: <CALIBRATED | NOT_CALIBRATED>
- Last calibration: <date>

## Verdict
- Overall: <green | yellow | red>
- Action items: <count>

## Recommended fixes
- [ ] <fix 1>
- [ ] <fix 2>
```

## Edge cases

- **CLI in PATH but plugin install impossible** — note as "skip (no plugin support yet)".
- **Plugin path not standard** — try multiple known locations.
- **Network-isolated machine** — skip version-check API calls, work with local data.

## Why this matters

Cross-CLI operator may have 3-5 CLIs installed. Version drift between them is real. This skill makes drift visible at a glance.

Replaces v2's spec-only `/jstack-cli-fingerprint` skill with a runtime check that actually runs.
