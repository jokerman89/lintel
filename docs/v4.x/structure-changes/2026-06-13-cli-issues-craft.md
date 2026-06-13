---
slug: cli-issues-craft
date: 2026-06-13
cycle_id: cli-craft-20260613
operator: jokerman
affected_paths:
  - hooks/shared/{secret-scan-block,customer-data-block}/run.sh (fail-closed, ADR-0014/issue I1)
  - lib/auto-decide.sh (new — one-way-door guard, I3)
  - skills/plan/SKILL.md (trio-completeness gate I4 + founder→operator)
  - skills/instruction-parity-check/SKILL.md (ghost files → real shims)
  - bin/li-doctor (Windows hook-fire note, I2)
  - lib/cli-tiers.yaml (li@ typo + codex native); .copilot-plugin/, .droid-plugin/ deleted
  - skills/ (43 descriptions → trigger form); agents/ (20 + traits/principles)
  - docs/concepts/prompt-house-style.md (new); tests/shape/skill-descriptions-trigger.sh (new)
risk_class: medium
breaking_change: false
---

# Structure change: cli-issues-craft

> Gate M1 — ADR-0014. Three workstreams (multi-CLI, issue-mining, prompt-craft) from
> docs/audit/2026-06-13-cli-issues-craft-synthesis.md.

## What changed (shape)

Prompt craft: 43 skill descriptions rewritten to trigger form; 20 agents gained
Core-principles + Behavioral-traits + trigger descriptions; house-style v2 doc + a
description-trigger shape guard. Security/reliability: block hooks fail-closed (no set -e +
scanner guard); lib/auto-decide.sh mechanical one-way-door guard; PLAN trio-completeness gate;
li-doctor Windows note. Multi-CLI: 2 fabricated manifests deleted (interop covers them);
cli-tiers typo + codex cell fixed; instruction-parity-check repointed at real shims.

## Backward-compat

Additive or corrective. Descriptions changed (auto-trigger improves; no skill renamed). Deleted
manifests were fabricated/wrong — Copilot+Droid read .claude-plugin/ via interop, so install is
unaffected. No frontmatter contract changed.

## Migration path

None. Operator-facing behavior unchanged or improved.

## Verification

Suite green incl. new tests/shape/skill-descriptions-trigger.sh + the existing security
behavior test (with the I1 fail-closed regression assertions). frontmatter-lint, no-swedish,
agents-categorized green.

## Rollback

git revert; the guard test reverts with it.

## Planned (own ADRs)

AGENTS.md-primary portability (ADR-0015) · lintel-state MCP server (ADR-0016) · eval-harness
(ADR-0017) · Subtraction-Bias data-modeling exception · per-CLI command-stub generator · the
field-wide description-trigger + aggressive-language sweep (remaining ~80 skills).
