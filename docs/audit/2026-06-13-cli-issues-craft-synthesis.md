# Multi-CLI · issues-we'll-share · prompt-craft — research synthesis + plan

> 2026-06-13. Three operator-requested workstreams: (1) make multi-CLI support the best it can
> be; (2) mine the resolved issues of the tools we descend from / run on, for traps we share;
> (3) study how the best competitors write agents/skills/prompts and raise our bar. Each backed
> by web research with cited sources (full agent reports in the cycle transcript). This is the
> authoritative findings + action register.

## Headline

Three findings dominate, one per workstream:
1. **Multi-CLI:** the "fictional install" battletest flag is now STALE — Codex/Cursor/Copilot/
   Droid all shipped real plugin systems Feb–May 2026, and AGENTS.md is a verified Linux-
   Foundation standard read natively by 8+ CLIs. The win is *subtraction* (delete 2 fabricated
   manifests, ride AGENTS.md + Claude-plugin interop) + one tools-only MCP server for portable
   state. (H13 decision: AGENTS.md-primary = YES.)
2. **Issues we'll share (CRITICAL):** the two BLOCK hooks run `set -euo pipefail` with the
   blocking `exit 2` at the end — an upstream `grep`/`tr` returning non-zero exits the script
   FIRST under `-e`, silently downgrading the block to non-blocking. A secret can commit through.
   The happy-path test misses it. [claude-code #60490/#66573] This is fixed NOW.
3. **Prompt craft (the bar-raise):** our skill `description:` fields SUMMARIZE the workflow
   ("Phase 5 — execute plan via TDD + subagent-driven-development…") — the exact pattern that
   made Claude do *one* review instead of two in superpowers' diagnosed regression. Descriptions
   must state WHEN to use (trigger), not WHAT it does. AND: newer models (Opus 4.5+/Fable 5)
   OVERTRIGGER on ALL-CAPS MUST/NEVER/CRITICAL — Anthropic now names it a yellow flag — yet our
   spine leans on it heavily. Both are evidence-backed, cheap, and high-leverage.

## Workstream 1 — Multi-CLI (corrected reality)

| Action | Disposition |
|---|---|
| Delete `.copilot-plugin/` (fabricated path) + `.droid-plugin/` (wrong name) — both read `.claude-plugin/` via interop | **FIX NOW** (Wave B) |
| `lib/cli-tiers.yaml` Copilot install `lintel@` → `li@`; `codex.subagents: sequenced → native` | **FIX NOW** (Wave B) |
| `instruction-parity-check` asserts 3 ghost files (.claude/AGENTS.md, .codex/CLAUDE.md, .github/copilot-instructions.md) that don't exist — repoint to real files | **FIX NOW** (Wave B) |
| AGENTS.md becomes the canonical instruction substance; CLAUDE.md a pointer (it's a LF standard read by Codex/Cursor/Copilot/Droid/Gemini/opencode/Zed/Windsurf) | **PLAN** ADR-0019 (file moves; do carefully) |
| TOML/command stubs for Gemini `commands/`, Cursor `.cursor/commands/`, Codex `prompts/` — flips `skills_native` true; one generator from skill frontmatter | **PLAN** (generator) |
| `lintel-state` tools-only MCP server (state/lessons/jobs as TOOLS not resources → ~10 clients, more reach than 6 manifests) | **PLAN** ADR-0020 |
| scaffold emits `.cursor/rules/` + `GEMINI.md` so scaffolded repos aren't Claude-only | **PLAN** |

## Workstream 2 — issues we'll share (16 findings; TIER-1 here)

| # | Source | Lintel exposure | Action |
|---|---|---|---|
| I1 | claude-code #60490/#66573 — exit-2 block downgraded if an upstream cmd fails under `set -e` | secret-scan-block + customer-data-block: `set -euo pipefail`, `exit 2` last | **FIX NOW** (Wave A) — guard the block path; negative test |
| I2 | claude-code #59072 — SessionStart hooks silently never fire on Windows | session-digest is our only SessionStart hook; operator on Win11 | **FIX NOW** (Wave B) — li-doctor loud no-fire warn |
| I3 | gstack #603/#1740 — AI auto-decided a scope change; sovereignty incident | our AUTO_DECIDE is 100% prose, no mechanical door_type | **FIX NOW** (Wave B) — mechanical one-way-door keyword guard |
| I4 | gstack #1127/#1791 — cold-executor trio drift; `li-envelope-validate` exists but PLAN never calls it | PLAN Step 11 is prose-only | **FIX NOW** (Wave B) — wire the validator |
| I5 | superpowers v5.0.6 — plan/spec review subagents removed (zero quality lift); CODE review kept | our plan-*-review may dispatch where inline self-review suffices | **PLAN** — measure before changing (needs the eval) |
| I6 | claude-code #63855 — subagents inherit full CLAUDE.md+rules+skills at boot → context cap | every Lintel subagent dispatch pays this | **MONITOR** — keep CLAUDE.md lean; adopt loadProjectRules:false when it ships |
| I7 | gstack #1048 — blanket subtraction produced harmful schema advice | our Subtraction Bias is a core principle | **PLAN** — carve a data-modeling exception (ADR) |

## Workstream 3 — prompt craft (the bar-raise)

Evidence-backed craft upgrades (Anthropic best-practices + superpowers + wshobson/VoltAgent +
rules-format authors + 2026 prompt SOTA). Ranked:

1. **Description = trigger, not summary** (superpowers' measured regression; Anthropic "what +
   when, third person, key terms"; wshobson lint-enforced). Our descriptions summarize. **FIX NOW**
   — rewrite to `Use when …` trigger form across the surface + a MISSING_TRIGGER shape guard.
2. **Dial back ALL-CAPS MUST/NEVER/CRITICAL** — current models overtrigger; Anthropic names it a
   yellow flag. State the rule + the WHY instead. **FIX NOW** (house-style v2 + targeted sweep).
3. **Behavioral Traits + Core Principles blocks on agents** (wshobson's consistency engine —
   disposition for the gray zone, distinct from Voice). **FIX NOW** (Wave C, agent fleet).
4. **Positive over negative framing** ("compose flowing prose" not "don't use markdown"). House-style.
5. **Examples: 1 excellent worked example, Good/Bad paired, XML-tagged** (superpowers + SOTA).
6. **Word/instruction budgets** — spine skills are 300-487 lines; field budgets are <500 lines /
   ~150 instructions. Subtraction already started (ADR-0009); continue with the budget stated.
7. **Eval-driven iteration** — the real unlock, and the thing most likely missing. 20-50 tasks
   per critical skill, pass/fail verifier, positive+negative. **PLAN** ADR-0021 (battletest H1/H5).
8. **Anti-sycophancy structurally** — fresh-context judge agents + question-reframing beat "be
   harsh"; our subagent review already fits. House-style note.
9. **Persona-for-accuracy is overrated** — roles steer voice/behavior, not correctness. House-style.

## This cycle (build now) vs planned

- **Wave A (security, ADR-0014):** block-hook fail-open under `set -e` + negative test. Dangerous; first.
- **Wave B (multi-CLI + issue subtraction):** delete fabricated manifests, fix cli-tiers + parity-
  check, li-doctor Windows hook-fire warn, mechanical one-way-door guard, wire li-envelope-validate.
- **Wave C (prompt craft, ADR-0014 craft):** house-style v2 doc; MISSING_TRIGGER shape guard;
  description→trigger rewrite (highest-traffic skills first); agent Behavioral-Traits/Core-Principles;
  dial-back aggressive language in the spine.
- **PLANNED (own ADRs):** AGENTS.md-primary (ADR-0019) · lintel-state MCP server (ADR-0020) ·
  eval-harness (ADR-0021) · Subtraction-Bias data-modeling exception · the field-wide
  aggressive-language sweep · per-CLI command-stub generator.

## The strategic through-line (all three workstreams agree)

Lintel's craft is already above the public median (When-NOT sections, report contracts, uniform
rhythm) but is tuned to a PRE-4.5 model generation (pushy MUST/NEVER triggers, workflow-summary
descriptions) and over-weighted on manifests vs the AGENTS.md+MCP standards that now do the
portability work. The bar-raise is: trigger-form descriptions, dial-back imperatives, judgment-
front-loaded agents, and — the real unlock — an eval set so every future prompt change is decided
on evidence, not craft intuition. That last one is also battletest H1/H5; it keeps recurring
because it's the foundation the rest should stand on.
