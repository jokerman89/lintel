---
name: li-onebranch-validate
layer: ms-team
v1_alias: [li-test]
description: Cross-CLI verification — run a smoke matrix across claude-code/codex/copilot per skill cli_support.
color: yellow
tools: Read, Bash, Glob, Grep
voice: internal
cli_support: [claude-code]
---

# /onebranch-validate

The final cross-CLI verification skill. Reads each skill + agent's `cli_support` declaration, runs a smoke matrix across the declared CLIs, surfaces what works / what degrades / what fails. Produces a structured matrix consumed by the ship gate.

`cli_support: [claude-code]` only on the orchestrator itself — the matrix execution requires Claude Code to drive cross-CLI testing.

## When to use

- Pre-v1.0.0 release: must run + pass before tagging
- After adding a new skill / agent — verify cli_support claim is accurate
- After upstream Claude Code / Codex / Copilot version change — re-verify
- Pre-customer-distribution of any cross-CLI artifact

## When NOT to use

- Individual skill development — `/qa` is the fast loop
- One-CLI-only workflow — the matrix is overhead if you're not actually cross-CLI

## Inputs

- Optional `--scope <layer>` — run only specific layer (01-foundation | 02-compliance | 03-personal-advanced | 04-power-user) (default: all)
- Optional `--cli <name>` — restrict to one CLI (claude-code | codex | copilot)
- Optional `--smoke-only` — run only smoke (invoke + verify-no-crash); skip output-quality check
- Optional `--out <path>` — write matrix to file (default: `~/.lintel/test-matrix-<ts>.md`)

## Workflow

1. **Enumerate.** Glob all SKILL.md + agent files. Read each cli_support.
2. **Per skill/agent × per declared CLI:**
   - Construct an invocation that exercises the skill's core path with minimal side effects
   - Execute against the target CLI (Claude Code: native; Codex: `codex exec --quiet`; Copilot: stub — operator manually verifies)
   - Capture: exit code, stdout sample, time taken
3. **Per output, classify:**
   - PASS — invoked + ran + produced expected output shape
   - DEGRADED — invoked but partial (e.g. AskUserQuestion-dependent skill in Codex falls back to sequential prompts)
   - FAIL — error / crash / unexpected behavior
   - SKIPPED — not in cli_support
4. **Aggregate matrix.** Skill × CLI grid with status per cell.
5. **Ship-gate output.** Number of FAILs > 0 = blocks v1.0.0.

## Report format

```
Lintel Test Matrix — 2026-05-27T19:00:00Z

| Skill / Agent                  | claude-code | codex     | copilot   |
|--------------------------------|-------------|-----------|-----------|
| /qa                            | PASS        | DEGRADED  | SKIPPED   |
| /qa-only                       | PASS        | PASS      | SKIPPED   |
| /browse                        | PASS        | SKIPPED   | SKIPPED   |
| /release-ev2                          | PASS        | PASS      | SKIPPED   |
| ...                            | ...         | ...       | ...       |
| CodeReviewer (agent)           | PASS        | DEGRADED  | SKIPPED   |
| OneCSAuditor (agent)    | PASS        | PASS      | DEGRADED  |

## Summary
| CLI         | PASS | DEGRADED | FAIL | SKIPPED |
|-------------|------|----------|------|---------|
| claude-code | 60   | 0        | 0    | 43      |
| codex       | 32   | 18       | 0    | 53      |
| copilot     | 14   | 6        | 0    | 83      |

## Ship-gate status
- FAILs: 0 ✓
- DEGRADED documented in cli_support: yes ✓
- All claude-code-required skills PASS: yes ✓

## Verdict
READY for v1.0.0 ship.
```

## Compliance integration

- Read-only on skills/agents (no modification).
- Test artifacts (matrix output) are engineering-internal — no Layer 2 customer-data concern.
- Audit log: `~/.lintel/audit/test-matrix.jsonl` records each run.

## Voice tier note

`voice: internal`. Test matrix is engineering-internal.

## Failure modes

- **Codex CLI not installed:** mark all codex-cells as SKIPPED-NO-CLI, surface install command.
- **Copilot has no programmatic invocation:** treat as manual-only — print "Copilot manual-verify list" with the relevant skills.
- **Smoke invocation produces an AskUserQuestion (interactive):** mark DEGRADED — non-interactive smoke can't proceed without operator.
- **Skill has cli_support claim but invocation fails:** that's a FAIL — surface as ship-blocker. Either cli_support is wrong or the skill is broken on that CLI.

## Examples

**Full matrix:**
```
> /onebranch-validate
[Iterates 63 skills + 40 agents × 3 CLIs]
60 PASS / 18 DEGRADED / 0 FAIL on claude-code. Matrix written to ~/.lintel/test-matrix-<ts>.md.
```

**Layer-scoped:**
```
> /onebranch-validate --scope 01-foundation
[Foundation skills only]
```

**Smoke-only fast pass:**
```
> /onebranch-validate --smoke-only
[Just verifies invocation works; skips output-quality check]
```

## See also

- `/lintel:li-eval` — voice corpus calibration (different gate)
- TEMPLATE-skill.md / TEMPLATE-agent.md — frontmatter source of truth for cli_support
- `SHIP-GATE.md` — v1.0.0 prerequisites this skill helps enforce
