---
name: cli-fingerprint
layer: foundation
description: Detect which CLI is running Lintel — env-var → process → tool-probe → config fallback.
color: blue
tools: Read, Bash
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: full
  - cli: copilot-cli
    level: full
  - cli: copilot-app
    level: full
---

# /li:cli-fingerprint

CLI detection runtime that feeds the portability shim. **Foundational** — every other skill's degradation decision depends on knowing which CLI is currently running.

P1 fix T2 (eng-review): Phase B sub-step 0. Without reliable detection the shim layer is guessed.

Detected IDs (the enum): `claude-code`, `codex`, `copilot-cli`, `copilot-app`, `cursor`, `gemini`, `opencode`, `droid`. For capability-tier lookups the ID is normalized onto the 8 rows of `lib/cli-tiers.yaml` via `cli_tier_normalize` (`lib/cli-tiers.sh`): `copilot-cli`/`copilot-app` → `copilot`; anything unrecognized → `other`. That mapping is what lets `/li:welcome`'s honest-tier banner reach every row.

## When to use

- Session start (auto-run by `/help` and other entry skills)
- Operator unsure which CLI Claude / agent is actually running in
- Debugging shim behavior ("why did this skill use degraded path?")
- After CLI install/update — verify detection still picks the right one

## When NOT to use

- Inside a skill that already received its CLI ID from session cache
- Test fixtures with mock CLI ID (use `LINTEL_CLI=test` instead)

## Inputs

- Optional `--force-redetect` — ignore session cache, re-run all detection steps
- Optional `--declare <cli-id>` — operator-side manual declaration (writes to `~/.lintel/cli-id.txt`)
- Optional `--verbose` — print the cascade evaluation step-by-step

## Workflow

1. **Check explicit env var first.**
   ```bash
   if [ -n "${LINTEL_CLI:-}" ]; then
     return "$LINTEL_CLI"
   fi
   ```
   This is the highest-priority signal — operator pinned via shell init or per-invocation `LINTEL_CLI=codex command`.

2. **Process inspection.**
   - Check `$0` / `process.argv0` for known binary patterns:
     - `claude-code`, `claude` → `claude-code`
     - `codex`, `codex exec` → `codex`
     - `gh-copilot`, `gh copilot`, `copilot` → `copilot-cli`
     - GitHub Copilot App native bundle paths → `copilot-app`
     - `cursor`, `cursor-agent` → `cursor`
     - `gemini` → `gemini`
     - `opencode` → `opencode`
     - `droid` → `droid`
   - Check parent process tree (1 level up) for the same patterns. Some CLIs spawn shells that obscure $0.

3. **Tool-availability probe.**
   - Check for CLI-specific env vars:
     - `CLAUDE_CODE_VERSION` (or `ANTHROPIC_*`) → `claude-code`
     - `CODEX_*` → `codex`
     - `GH_TOKEN` + `gh copilot` subcommand available → `copilot-cli`
     - `CURSOR_TRACE_ID` (or other `CURSOR_*`) → `cursor`
     - `GEMINI_CLI` / `GEMINI_*` → `gemini`
     - `OPENCODE_*` → `opencode`
     - `FACTORY_*` → `droid`
   - Check for CLI-specific filesystem markers (all weak signals — could be stale installs):
     - `~/.claude/config.json` exists → suggests `claude-code`
     - `~/.codex/config.toml` exists → suggests `codex`
     - `~/.cursor/` exists → suggests `cursor`
     - `~/.gemini/settings.json` exists → suggests `gemini`
     - `~/.config/opencode/` exists → suggests `opencode`
     - `~/.factory/` exists → suggests `droid`

4. **Operator-declared fallback.**
   - Read `~/.lintel/cli-id.txt` if exists
   - This is operator-set via `/li:cli-fingerprint --declare <cli-id>`

5. **Refuse + ask.**
   - If all detection steps fail: print:
     ```
     Could not detect CLI. Lintel needs to know which CLI it's running in
     to apply the correct shim behavior.

     Set LINTEL_CLI env var:
       export LINTEL_CLI=claude-code
       # or: codex / copilot-cli / copilot-app / cursor / gemini / opencode / droid

     Or declare via skill:
       /li:cli-fingerprint --declare <cli-id>
     ```
   - Exit 1.

6. **Cache result.**
   - Write detected CLI to `~/.lintel/sessions/$SESSION_ID/cli-id.txt`
   - Subsequent skill invocations read cache instead of re-running detection.

7. **Report.**

## Report format

```
CLI fingerprint: claude-code

Detection cascade:
  Step 1 (env var LINTEL_CLI):     not set
  Step 2 (process inspection):     match — process.argv0 contains "claude-code"
  Step 3 (tool probe):             skipped (matched at step 2)
  Step 4 (declared fallback):      skipped
  Step 5 (refuse):                 skipped

Cached to: ~/.lintel/sessions/47821-1716926400/cli-id.txt
TTL: session
Override: LINTEL_CLI=<other> in env, or /li:cli-fingerprint --declare <other>

Shim behavior for this CLI:
  AskUserQuestion: native
  Agent tool:       native (Task tool)
  Browser tool:     full
  MCP:              full
```

## Compliance integration

- CLI ID is not sensitive — Layer 2 rules don't apply.
- Audit log entry per detection event: `.claude/runtime/audit/cli-detect.jsonl`. Helps debug "why is this skill using degraded path?".
- Operator-declared override is logged with operator reason if provided.

## Failure modes

- **Detection cascade falls through to step 5:** refuse + clear instructions. Don't guess.
- **Env var contains invalid CLI ID:** validate against the enum (`claude-code`, `codex`, `copilot-cli`, `copilot-app`, `cursor`, `gemini`, `opencode`, `droid`); reject unknown values with error.
- **Cache file unreadable / corrupted:** delete cache + re-run detection. Should be transparent to operator.
- **Process inspection finds multiple matches (claude-code + codex both in process tree):** prefer the one with shorter PID distance to current process. If tie: prefer claude-code (most common case).
- **Conflicting signals (env var says codex, process says claude-code):** env var wins. Log conflict to audit.

## Examples

**Standard session-start:**
```
> /li:cli-fingerprint
✓ Detected: claude-code (via process inspection)
Cached to session.
```

**Force redetect after CLI upgrade:**
```
> /li:cli-fingerprint --force-redetect --verbose
[Step-by-step cascade printed]
✓ Detected: codex (env var LINTEL_CLI=codex)
```

**Operator declares manually:**
```
> /li:cli-fingerprint --declare copilot-app
Wrote ~/.lintel/cli-id.txt = copilot-app
Subsequent detections will use this declared value (step 4) if no env var or process match.
```

**Refusal:**
```
> /li:cli-fingerprint
✗ Could not detect CLI.
[Instructions printed]
```

## See also

- `lib/cli-tiers.sh` — `cli_tier_normalize` maps these IDs onto the 8 `lib/cli-tiers.yaml` rows for the honest-tier lookup (`/li:welcome`)
- `CLI-SUPPORT-V2-SCHEMA.md` — schema this skill's output feeds
- `~/.lintel/config.yaml` — operator overrides per-skill cli_support
- `verify.sh --portability` — schema validation
- Phase B design — full shim runtime that consumes detection
