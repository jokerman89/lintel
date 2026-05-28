---
name: jstack-health
layer: foundation
description: JStack install + upstream status check. Verifies layers, manifest, hooks, upstream pins, CLI shims.
color: green
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# /health

Diagnostic skill. Runs the same checks as `verify.sh` but inline in a Claude Code session — surfaces install issues without leaving the editor.

## When to use

- After fresh install — confirm everything landed
- After a JStack update (`bash install/install.sh` re-run) — confirm nothing broke
- When a skill or agent behaves oddly — confirm it's installed at the right path with the right frontmatter
- Teammate reports "JStack isn't working" — first triage step

## When NOT to use

- Pure code work — no health concern
- During a long-running tool sequence — don't interrupt

## Inputs

Optional flags:
- `--fast` — only the cheap checks (no upstream license-freshness, no full cross-ref scan)
- `--upstream-only` — just the 8 upstream-sources status
- `--layers-only` — just the 4 layer install paths
- `--hooks-only` — just the symlink state for the 14 hooks
- `--json` — machine-readable output (for CI)

No arguments: full check, ~10-30 second runtime.

## Workflow

Runs these checks in order. Each check passes/fails independently; report aggregates.

1. **Install manifest:** read `~/.claude-scaffolding/INSTALL-MANIFEST.json`. Confirm fields present (installed_at, repo_commit, layers_enabled, upstream_sha_per_source, host_platform, host_user, jstack_version).
2. **Layers:** for each `layer_N.enabled: true` in `~/.jstack/config.yaml`, confirm `install_path` exists and contains expected files.
3. **Cross-refs:** spot-check that key links resolve — `AGENT-INSTRUCTIONS.md` → layer READMEs → CORE-PRINCIPLES.md.
4. **Upstream sources:** for each entry in `~/.claude-scaffolding/upstream-sources.yaml`, confirm clone exists at install_path + HEAD matches the pinned SHA.
5. **Hooks:** for each `~/.jstack/hooks/jstack-*.sh`, check whether a symlink exists at `~/.claude/hooks/jstack-*.sh`. Report active vs inert.
6. **Skill frontmatter:** glob `~/.claude/skills/jstack-*/SKILL.md`. Confirm required fields (name, description, color, tools, voice, cli_support). Flag any with missing fields.
7. **Agent frontmatter:** same check on `~/.claude/agents/` (filter to JStack-relevant).
8. **Voice corpus:** if `~/.claude-scaffolding/03-personal-advanced/voice/OurVoice-calibration.md` exists, parse the status table — report per-cell calibration status (PASS / PARTIAL / FAIL / PENDING).
9. **CLI shims:** for the current repo (if in one), check whether `CLAUDE.md`, `.github/copilot-instructions.md`, `AGENTS.md` are present.
10. **License freshness:** for each upstream, check `last_verified` against today. Warn if >90 days.

## Report format

**Healthy (--fast):**
```
JStack v1.0.0 health: ✓ all checks pass
  Manifest: 2026-05-27, commit 7e7a021
  Layers (4/4): 01-foundation ✓ 02-compliance ✓ 03-personal-advanced ✓ 04-power-user ✓
  Skills (25/25): all frontmatter valid
  Agents (40/40): all frontmatter valid
  Voice corpus: PENDING (T0 — no calibration data yet)
```

**Issues (full):**
```
JStack v1.0.0 health: ⚠ 3 issues, 1 warning

✓ Manifest: present, last installed 2026-05-27
✓ Layers (4/4 enabled, all install paths exist)
✗ Skill frontmatter:
    jstack-foo: missing `cli_support` field
    jstack-bar: invalid voice tier value ("trailerblazer" — typo of "trailblazer")
✗ Upstream pin drift:
    trailofbits-skills: HEAD at abc1234, pinned to def5678 (10 commits ahead)
⚠ License freshness:
    anthropic-skills: last_verified 2026-02-15 (>90 days stale)
✓ Hooks (1/14 active): jstack-secret-scan symlinked
✓ Voice corpus: 8/12 cells PASS, 4/12 PENDING (waiting for T0 completion)
✓ CLI shims for current repo: CLAUDE.md ✓, .github/copilot-instructions.md ✓, AGENTS.md missing (not on Codex)

Recommended next steps:
1. Re-run install.sh to refresh skill frontmatter for jstack-foo and jstack-bar
2. Decide on trailofbits-skills update — review changes since pinned SHA, bump if safe
3. Run quarterly review on anthropic-skills upstream, update last_verified
```

**JSON mode (--json) for CI:**
```json
{
  "version": "1.0.0",
  "manifest": {"present": true, "installed_at": "...", "commit": "..."},
  "layers": {"enabled": 4, "all_paths_exist": true},
  "skills": {"total": 25, "frontmatter_issues": []},
  "agents": {"total": 40, "frontmatter_issues": []},
  "upstreams": {"total": 8, "pin_drift": [], "stale_verifications": []},
  "hooks": {"total": 14, "active": 1, "inactive": 13},
  "voice_calibration": {"pass": 8, "partial": 0, "fail": 0, "pending": 4},
  "shims_current_repo": {"claude_md": true, "copilot": true, "codex": false},
  "exit_code": 0
}
```

## Edge cases

- **Not in a git repo:** skip CLI-shim check, report N/A.
- **`~/.claude-scaffolding/` doesn't exist:** report "JStack not installed. Run install.sh."
- **`INSTALL-MANIFEST.json` missing but scaffolding present:** report "scaffolding present but no manifest — install predates manifest feature, run install.sh to regenerate."
- **Multiple layer-config.yaml files (one user-global, one operator-override):** report which takes precedence.

## Compliance integration

- This skill is read-only. Doesn't touch external systems.
- One indirect compliance link: if `voice_calibration` shows FAIL cells, that's relevant to "is JStack's customer-facing surface safe to use?" — operators can use the answer for risk decisions.

## Failure modes

- **YAML parse error in config or upstream-sources:** report the file + line + error, fail the relevant check, continue with others.
- **`gh` not on PATH but used for upstream API check:** skip API-dependent checks, report "gh unavailable, upstream license-freshness check skipped."
- **Slow upstream check (network):** with `--fast` skip; otherwise warn ">15s spent on upstream check, consider --fast for quick triage."

## Examples

**Triage a working install:**
```
> /health --fast
JStack v1.0.0 health: ✓ all checks pass (5s)
```

**Full audit after upgrade:**
```
> /health
[full output, 25s]
```

**CI integration:**
```
> /health --json
[machine-parseable, exit 0 = healthy]
```

## See also

- `install/verify.sh` — same checks as a standalone shell script (CI uses this)
- `/help` — what's installed
- `INSTALL-MANIFEST.json` — authoritative install state
