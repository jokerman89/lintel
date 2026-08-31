---
slug: battletest-remediation
date: 2026-06-12
cycle_id: battletest-20260612
operator: jokerman
affected_paths:
  - hooks/shared/{secret-scan-block,customer-data-block}/run.sh + _patterns.sh (ADR-0010)
  - bin/_audit.sh, lib/state.sh, bin/li-scaffold, install/install.ps1 (ADR-0010)
  - skills/capture/SKILL.md (vault PII scan, ADR-0010; gstack attribution, ADR-0011)
  - agents/**/*.md (memory:/model: frontmatter, ADR-0012) + tests/shape/frontmatter-lint-all.sh
  - ~30 files gstack de-heritage (ADR-0011)
  - skills/{resume,context-restore,context-save,define,sense,plan,cycle}/SKILL.md (friction, synthesis Wave H)
  - README, getting-started, welcome, CLAUDE.md, install.sh, docs/GLOSSARY.md (docs, Wave D)
risk_class: high
breaking_change: false
---

# Structure change: battletest-remediation

> Gate M1 artifact. Six-persona adversarial battletest (.claude/engineering/audits/2026-06-12-battletest-synthesis.md)
> + gstack de-heritage. Four ADRs: 0010 (security), 0011 (gstack), 0012 (agent memory/model).

## What changed (shape)

Security (ADR-0010): block hooks match any git phrasing + scan staged∪worktree; modern token
formats; vault pre-write PII scan; CR/LF-safe audit + state; li-scaffold sed RCE closed.
gstack (ADR-0011): 44 edits / 30 files — attribution rewritten to native rationale, gstack
paths/binaries → native helpers, REVIEW REPORT heading dual-accept + legacy review-log import +
disable-file migration (all zero-loss, grace 2026-09-12). Agent frontmatter (ADR-0012): 23
agents `memory: project`, 4 `model: haiku`, frontmatter-lint extended. Friction (Wave H):
resume↔context-restore wired, cost-gate honesty, DEFINE feature fast-path, SENSE meta-infra
marker-gated. Docs (Wave D): canonical hook-activation matrix, GLOSSARY, stale-count fixes,
4-root state map, install ghosts removed.

## Backward-compat

Additive or alias-covered. New frontmatter keys optional. gstack names route via aliases +
dual-accept heading. No required contract dropped (M2 RED = additive frontmatter + alias-covered
removals; override documented).

## Migration path

Two rows in _INDEX.md (v5.2-gstack-deheritage, v5.2-security-hardening). Security auto-applies
via plugin update; gstack grace to 2026-09-12.

## Verification

Suite 76/76; new behavior tests tests/integration/security-controls-fire.sh (15 assertions,
caught 2 real bugs in the fixes) + session-leaves-traces. frontmatter-lint + no-swedish green.

## Rollback

git revert per ADR; aliases + dual-accept revert cleanly; frontmatter keys are optional.

## Planned (not in this change — own ADRs)

Eval-harness (H1/H5) · BUILD parallelism (H9) · module-YAML enforcement (H10) · MCP server (H11)
· portability collapse to AGENTS.md (H13) · pack provenance (H17) · plugin pinning (H18) · real
git pre-commit/pre-push install (supersedes ADR-0010's command-string match) · v6 shrink-to-kernel.
