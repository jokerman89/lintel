# Migrations

Current public releases use the 0.9.0 beta line. Older 3.x–5.x labels below record historical engineering transitions; they are not current minimum install versions. For repository kits, adopt or upgrade through the selected `li-adapter.py init`/`li-copilot init` operation and verify with `check`. See [lifecycle operations](../lifecycle.md) and [Copilot](../copilot.md#upgrade-and-rollback).

Every change that may need action from you, with its grace window. `/li:migrations` reads this file
at session start and surfaces anything still open for your repo; you can also just read it.

Each row lives here for the whole grace-plus-removal window, so a repo that has been dormant for
months can still find out what it missed. Detailed guides, where one exists, live beside this file
as `<date>-<slug>.md`.

Past dates are historical schedules, not automatic removal instructions. Unresolved or
undetectable consumer work remains visible as overdue or unknown. `li-lifecycle.py migrations`
reads this installed-source table without executing its example detection commands.

## Active migrations

| Slug | Started | Grace until | Removal at | Description |
|---|---|---|---|---|
| native-workflow-consolidation | 2026-09-25 | none | none | Related entrypoints now share native methods; use the [capability replacement guide](2026-09-25-native-workflows.md). Update owned installations through their inventory; preserve user files, receipts, old checkpoints and historical evidence. No data-removal deadline is introduced. |
| v3-voice-spine-references | 2026-05-29 | 2026-08-29 | 2026-11-29 | Voice, persona and corpus content lifted out of the spine into an installable pack. Repos on the older layout keep working through a warn-only fallback; activate a pack with `/li:pack-switch <name>`. |
| v3-workprofile-profile-field | 2026-05-29 | 2026-08-29 | 2026-11-29 | Historical `profile.yaml` `workprofile:` preference moved into pack policy. The current structured resolver does not use this legacy preference as policy or pack selection. Inspect the configured profile explicitly; preserve it until a reviewed migration establishes the intended equivalent. |
| v3-skill-rename-grace | 2026-05-29 | 2026-08-29 | 2026-11-29 | Historical skill-alias schedule. Amended 2026-06-12: two skills were retired early with their targets and one moved into an external pack. Expired aliases are no longer a supported invocation route; consult the current catalog and capability replacement guide rather than assuming an old target still exists. This does not authorize deleting project data. |
| pack-version-warn-only | 2026-05-29 | 2026-11-29 | 2027-02-28 | Historical warn-only compatibility is superseded by ADR-0029. Pack schema/release, source product and capability versions are separate. Exact legacy `requires_lintel: ">=4.0.0"` remains a pack-v1 marker; other legacy ranges need explicit migration. Required/explicit compatibility failure blocks instead of selecting neutral. |
| wiki-gen-check-warn-only | 2026-05-29 | 2026-11-29 | 2027-02-28 | `bin/li-wiki-gen --check` exits non-zero when the generated wiki is stale. It is not wired into CI yet; run it before a release and commit the result. |
| envelope-completeness-soft-gate | 2026-05-29 | 2026-08-29 | 2026-11-29 | Brief Forge envelopes with `completeness_score < 40` surface ESCALATE but currently do not hard-block. v4.1 will hard-block at < 40 unless `--no-brief-forge` is explicit. |
| ta-hooks-warn-only | 2026-05-30 | 2026-11-30 | 2027-02-28 | TA module's 3 hooks (arch-drift, contract-collision, complexity-budget) ship as warn-only in v4.1. v4.2+ may add per-pack opt-in block. Operators wanting a hard block now can run the Brief Forge security evaluator with a failing threshold. |
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
| v5.1-subtraction-aliases | 2026-06-12 | 2026-09-12 | 2026-09-12 | ADR-0009: 35 engineering sub-skills collapsed into module dispatch tables (invoke `/li:<module> <capability>`) + role family 8→3. The historical 41-alias grace ended on 2026-09-12; use surviving module/role methods, not expired aliases. Counts describe that transition, not a current removal quota. Preserve saved work and inspect consumers before an owned update. |
| v5.2-gstack-deheritage | 2026-06-12 | 2026-09-12 | 2026-12-12 | ADR-0011: historical transition to native routing. The original identifier and dates are retained for traceability. Earlier heading compatibility, review-log import and disable-file migration are historical behavior, not current clearance. Review history remains evidence of its original attempt; current approval requires the shared content-bound v2 review/QA contract and cannot be inferred from a report heading. |
| v5.2-security-hardening | 2026-06-12 | none | none | ADR-0010: block hooks broadened (match any git phrasing + scan worktree), modern token formats, vault pre-write PII scan, audit/state newline-safe, li-scaffold sed RCE closed. No operator action — auto via plugin update. Follow-up (own ADR): real git pre-commit/pre-push install supersedes the command-string match. |
| v5-hook-autoregistration | 2026-06-12 | 2026-09-12 | 2026-12-12 | ADR-0008: the plugin auto-registers session-digest + 4 safety hooks + memory-budget-warn via hooks/hooks.json. Operators with MANUAL hook entries in ~/.claude/settings.json should remove them after updating the plugin (double-fire otherwise — harmless but noisy). Re-run install.sh to refresh ~/.lintel hooks + seed profile.yaml. Detect: grep -c lintel ~/.claude/settings.json + li-doctor. |
| v5.7-cycle-position-inject | 2026-06-17 | none | none | ADR-0023: adds the `cycle-position-inject` **UserPromptSubmit** hook (turn-start cycle-position re-assertion — completes the continuity trifecta) + co-registers the orphaned `no-customer-data-in-message` hook. Additive, auto-registers via hooks.json. No operator action beyond **updating the plugin to li ≥5.7.0** so it fires (li-doctor warns if the installed plugin is stale). Detect: `grep -c cycle-position-inject ~/.claude/plugins/cache/*/li/*/hooks/hooks.json`. |

## Archived migrations

| Slug | Started | Closed | Outcome |
|---|---|---|---|
| _none yet_ | — | — | — |

## Format

Each entry in `docs/migrations/<date>-<slug>.md` has frontmatter:

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

Move a record to archived history only after the migration/removal decision and its
consumer recovery path are documented. Expiry alone does not establish completion or
authorize deleting aliases, redirect stubs or backups. Archived rows remain available
with `--all`; rows without executable detectors are explicitly unknown.
