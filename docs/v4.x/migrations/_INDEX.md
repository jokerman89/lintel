# v4.x Migrations Index

Durable tracker for v4.x migration windows. Each row points to a migration file under `docs/v4.x/migrations/<date>-<slug>.md`. `/li:migrations` reads this file at session-start.

> Per v4.0 design Chapter 4 §5.5: this index is the durable tracker. `tasks/memory.md` stays ephemeral. Migrations live here for the entire grace + removal window.

## Active migrations

| Slug | Started | Grace until | Removal at | Description |
|---|---|---|---|---|
| v3-trailblazer-spine-references | 2026-05-29 | 2026-08-29 | 2026-11-29 | Trailblazer voice + persona corpus + voice corpus lifted from spine to `caip-se` pack. Operators on v3.x continue working via warn-only fallback; CAIP-SE work should migrate via `/li:pack-switch caip-se`. |
| v3-workprofile-profile-field | 2026-05-29 | 2026-08-29 | 2026-11-29 | `~/.lintel/profile.yaml` `workprofile:` field migrated to `pack.compliance.workprofile_default`. Profile field still read for backward-compat; pack value overrides. Detect: `grep '^workprofile:' ~/.lintel/profile.yaml`. |
| v3-skill-rename-grace | 2026-05-29 | 2026-08-29 | 2026-11-29 | Cohort 4 renames (match→skill-router) covered by `config/aliases.yaml`. AMENDED 2026-06-12: setup-brain/sync-brain retired EARLY with their gbrain targets (ADR-0009 0-ref pruning) — those two names no longer resolve; agt-tier-stamp moved to lintel-caip-pack earlier. |
| pack-version-warn-only | 2026-05-29 | 2026-11-29 | 2027-02-28 | v4.0 ships `requires_lintel` enforcement as warn-only. v4.1 will block on incompat. Pack authors should declare `requires_lintel: ">=4.0.0"` now to avoid the future warn-storm. |
| wiki-gen-check-warn-only | 2026-05-29 | 2026-11-29 | 2027-02-28 | CI runs `bin/li-wiki-gen --check` and warns on diff. v4.1 will fail PRs on diff. Operators should regen + commit wiki before that bites. |
| envelope-completeness-soft-gate | 2026-05-29 | 2026-08-29 | 2026-11-29 | Brief Forge envelopes with `completeness_score < 40` surface ESCALATE but currently do not hard-block. v4.1 will hard-block at < 40 unless `--no-brief-forge` is explicit. |
| ta-hooks-warn-only | 2026-05-30 | 2026-11-30 | 2027-02-28 | TA module's 3 hooks (arch-drift, contract-collision, complexity-budget) ship as warn-only in v4.1. v4.2+ may add per-pack opt-in block. Operators wanting block now can use Brief Forge security/sdl_compliance evaluators with hard fail. |
| profile-engineering-block | 2026-05-30 | 2027-05-30 | none-removed | `~/.lintel/profile.yaml` gains an `engineering:` block in v4.1 (TA: tech_architecture.*; v4.2-v4.5 add other domains). Operators without the block see defaults (cyclomatic 12, cognitive 18, etc.). No removal — the block is purely additive. |
| da-hooks-warn-only | 2026-05-30 | 2026-11-30 | 2027-02-28 | DA module's 3 hooks (schema-drift, migration-irreversible, retention-violation) ship as warn-only in v4.2. v4.3+ may add per-pack opt-in block for migration-irreversible specifically (destructive migrations are higher-risk than the others). |
| profile-engineering-data-architecture | 2026-05-30 | 2027-05-30 | none-removed | v4.2 adds `engineering.data_architecture.*` sub-block (primary_store, migration_window, retention_default_days, schema_versioning, require_migration_review_above_rows). Defaults baked in when block absent. Additive only. |
| sc-hooks-warn-only | 2026-05-31 | 2026-11-30 | 2027-02-28 | SC module's 3 hooks (threat-coverage, auth-bypass, compliance-gap) ship as warn-only in v4.3. v4.4+ may add per-pack opt-in block for auth-bypass specifically (high-risk auth patterns are higher-confidence than the others). |
| profile-engineering-security-compliance | 2026-05-31 | 2027-05-31 | none-removed | v4.3 adds `engineering.security_compliance.*` sub-block (sdl_active, secret_management, threat_model_required_on, compliance_frameworks, audit_retention_days). Defaults baked in when block absent. Additive only. |
| dh-hooks-warn-only | 2026-06-02 | 2026-12-02 | 2027-03-02 | DH module's 3 hooks (deploy-without-rollback, observability-gap, cost-budget) ship as warn-only in v4.4. v4.5+ may add per-pack opt-in block for deploy-without-rollback specifically (irreversible deploys are highest-risk). |
| profile-engineering-devops-hosting | 2026-06-02 | 2027-06-02 | none-removed | v4.4 adds `engineering.devops_hosting.*` sub-block (cloud, deployment_pattern, observability_stack, error_budget_window_days, cost_budget_monthly_usd_threshold). Defaults baked in when block absent. Additive only. |
| tq-hooks-warn-only | 2026-06-02 | 2026-12-02 | 2027-03-02 | TQ module's 3 hooks (coverage-drop, perf-regression, contract-break) ship as warn-only in v4.5. v4.6+ may add per-pack opt-in block (contract-break is highest-confidence candidate). |
| profile-engineering-testing-qa | 2026-06-02 | 2027-06-02 | none-removed | v4.5 adds `engineering.testing_qa.*` sub-block (coverage_target, critical_path_coverage, perf_budget_p95_ms, contract_test_framework, chaos_active, flaky_quarantine_threshold). Additive only. |
| full-engineering-pass-graceful-degradation | 2026-06-02 | 2026-12-02 | none-removed | v4.6 composition skill gracefully skips missing modules during the v4.x stacking-rollout window (when v4.3/v4.4/v4.5 land at different times). Once all 5 modules merge to main, composition runs the full DAG. Graceful behavior stays for future partial-rollout scenarios. |
| v5-claude-home-layout | 2026-06-12 | 2026-09-12 | 2026-12-12 | ADR-0005: repo-scoped Lintel output consolidates under `<repo>/.claude/` (knowledge committed: memory/, decisions/, plans/; runtime gitignored: runtime/). Legacy paths (`tasks/*`, `docs/adr/`, `.lintel/state/`, repo-scoped `~/.lintel/{sessions,jobs,audit}`) resolve via fallback until grace ends. Migrate: `bin/li-migrate-claude-home`. Detect: missing `.claude/lintel-layout.yaml` in a Lintel-scaffolded repo (li-doctor warns). |
| v5.1-subtraction-aliases | 2026-06-12 | 2026-09-12 | 2026-09-12 | ADR-0009: 35 engineering sub-skills collapsed into module dispatch tables (invoke `/li:<module> <capability>`) + role family 8→3. 41 aliases route the old names until removal. **Operative dates live in `config/aliases.yaml` (`removal_at: 2026-09-12`)** — aliases are a lighter deprecation than path/layout migrations, so removal coincides with grace-end rather than running a separate +3-month window. Detect: `grep -E 'old: (ta-|da-|sc-|dh-|tq-|role-)' config/aliases.yaml`. |
| v5.2-gstack-deheritage | 2026-06-12 | 2026-09-12 | 2026-12-12 | ADR-0011: gstack residue refactored to native. Grace items: the ship-gate dual-accepts both `## REVIEW REPORT` and `## GSTACK REVIEW REPORT` headings; li-review-read imports legacy ~/.gstack review logs once; frontend-design-surface migrates the gstack disable-file once. Detect: `grep -rn GSTACK skills/ lib/ bin/`. |
| v5.2-security-hardening | 2026-06-12 | none | none | ADR-0010: block hooks broadened (match any git phrasing + scan worktree), modern token formats, vault pre-write PII scan, audit/state newline-safe, li-scaffold sed RCE closed. No operator action — auto via plugin update. Follow-up (own ADR): real git pre-commit/pre-push install supersedes the command-string match. |
| v5-hook-autoregistration | 2026-06-12 | 2026-09-12 | 2026-12-12 | ADR-0008: the plugin auto-registers session-digest + 4 safety hooks + memory-budget-warn via hooks/hooks.json. Operators with MANUAL hook entries in ~/.claude/settings.json should remove them after updating the plugin (double-fire otherwise — harmless but noisy). Re-run install.sh to refresh ~/.lintel hooks + seed profile.yaml. Detect: grep -c lintel ~/.claude/settings.json + li-doctor. |

## Archived migrations

| Slug | Started | Closed | Outcome |
|---|---|---|---|
| _none yet_ | — | — | — |

## Format

Each entry in `docs/v4.x/migrations/<date>-<slug>.md` has frontmatter:

```yaml
---
slug: <kebab-case>
started_at: YYYY-MM-DD
grace_until: YYYY-MM-DD
removal_at: YYYY-MM-DD
old_shape: <description>
new_shape: <description>
risk_class: low | medium | high
detect_pattern: <grep/find pattern operator can run to find callsites>
---
```

When grace expires → migration moves from `## Active` to `## Archived` (operator file PR removing detect_pattern from `/li:migrations` surface).
