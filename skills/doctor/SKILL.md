---
name: doctor
layer: foundation
description: Use when something seems off with the Lintel install, or to confirm it's healthy, to run a cross-CLI health check — verifies which CLIs are installed, plugin install status, the Lintel version, and surfaces drift. Reach for it to diagnose setup problems before blaming the work.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the li-doctor skill.

## When to use

- Onboarding new operator — verify setup
- Suspect Lintel not loading in CLI X
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

2. **Per detected CLI, check Lintel install:**
   - Claude Code: `~/.claude/plugins/lintel/` or `~/.claude/marketplaces/jokerman-lintel/`
   - Codex: depends on Codex install dir
   - Cursor: `~/.cursor/extensions/` or similar
   - Gemini: `gemini extensions list | grep lintel`
   - OpenCode: `.opencode/plugins/lintel/`
   - Copilot: `copilot plugin list | grep lintel`
   - Droid: `droid plugin list | grep lintel`

3. **Per install, read version** (from plugin.json in each CLI's plugin dir).

4. **Cross-CLI drift detection.** If versions differ across CLIs, flag.

5. **Check scaffolding install.** `~/.lintel/scaffolding/` populated?

6. **Check pack assets.** `~/.lintel/brand/` present + age (warn if >90 days via `brand-staleness-warn` hook). Brand/voice assets are pack-contributed (`resolve_pack_field brand.*`; none by default).

7. **Hook activation status.** `~/.lintel/hooks/<name>` symlinks vs canonical.

8. **Instruction-parity drift check.** Invoke `/li:instruction-parity-check` to verify the 6 multi-CLI instruction files (CLAUDE/AGENTS/GEMINI roots + shims) have not drifted in substance. Surface its verdict (clean / warn / fail) in the drift report below. Triggered by `/li:doctor --instruction-parity`, or always-on in a full health check.

## Output format

```
JSTACK-DOCTOR: health check (date)

## CLIs detected
| CLI | Path | Version | Lintel installed | Lintel version |
|---|---|---|---|---|
| claude | /usr/local/bin/claude | 2.1.x | ✓ | 3.0.0 |
| codex | /usr/local/bin/codex | x.y | ✓ | 3.0.0 |
| cursor | n/a (app) | UI | ✓ | 3.0.0 |
| gemini | ~/bin/gemini | x.y | ✗ NOT INSTALLED | — |
| opencode | n/a | n/a | — | — |
| copilot | /usr/local/bin/copilot | x.y | ✓ | 2.0.5 ⚠ drift |
| droid | n/a | n/a | — | — |

## Drift detected
- Copilot CLI on Lintel v2.0.5 vs others on v3.0.0
  → Action: `copilot plugin update lintel`

## Scaffolding
- ~/.lintel/scaffolding/: ✓ present, last updated <date>

## Pack assets
- ~/.lintel/brand/: ⚠ 95 days old (>90 day threshold)
  → Action: refresh the active pack's brand/voice assets

## Hooks
- Activated: <N>/15 (operator opt-in)
- See: ~/.lintel/hooks/

## Instruction parity (via /li:instruction-parity-check)
- 6/6 instruction files present
- Drift: <none | warn | fail> — see .claude/runtime/audit/instruction-parity-<date>.md

## Voice corpus (pack-contributed)
- Source: <resolve_pack_field voice.corpus — none by default>
- Status: <CALIBRATED | NOT_CALIBRATED | N/A (no pack corpus)>
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

Replaces v2's spec-only `/li:cli-fingerprint` skill with a runtime check that actually runs.
