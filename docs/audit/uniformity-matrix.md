# Uniformity coverage matrix — generated

Generated: 2026-06-12T12:04:35Z by `bin/li-uniformity`. **Do not hand-edit** — regenerate
from frontmatter. Contract: [uniformity-contract.md](../concepts/uniformity-contract.md).

This is the living dashboard for uniformity-as-contract. The FLOOR (D14
necessity on workflow_root skills + block-hooks) is mechanically enforced by
`tests/shape/uniformity-coverage.sh`; everything else here is **tracked, not
mandated**. Cells: `yes` = field present · `—` = absent (optional) ·
`MISS` = absent on a FLOOR-required cell (CI-red until backfilled) · `n/a` =
not applicable for this kind (see contract for the per-kind reasons).

## Per-kind adoption summary (D14 necessity — the floor dimension)

| Kind | Count | necessity adoption | gap_if_skipped | navigation |
|---|---|---|---|---|
| workflow_root skills | 8 | 100% | 100% | 100% |
| regular skills | 116 | 12% | 12% | 0% |
| agents | 69 | 0% | 0% | n/a |
| block-hooks | 2 | 100% | 100% | n/a |
| warn-hooks | 27 | 11% | 11% | n/a |
| lifecycle-hooks | 2 | 0% | 0% | n/a |
| packs | 1 | 0% | n/a | 0% |

> The two floor rows are **workflow_root skills** and **block-hooks** — their
> `necessity adoption` must reach 100% for CI to pass. The other rows are the
> tracked long tail; low % there is expected and is not a CI failure.

## Matrix by kind

### Workflow-root skills (n=8)

| Component | D14 necessity | D12 gap | D4 nav | D9 brief-forge | D7 pack | D13 obs | D6 recovery | D5 checkpoints |
|---|---|---|---|---|---|---|---|---|
| `cycle` | yes | yes | yes | — | — | — | — | — |
| `da` | yes | yes | yes | — | — | — | — | — |
| `dh` | yes | yes | yes | — | — | — | — | — |
| `full-engineering-pass` | yes | yes | yes | — | — | — | — | — |
| `plan` | yes | yes | yes | — | — | — | — | — |
| `sc` | yes | yes | yes | — | — | — | — | — |
| `ta` | yes | yes | yes | — | — | — | — | — |
| `tq` | yes | yes | yes | — | — | — | — | — |

Adoption: D14 necessity=100%(floor) · D12 gap=100%(floor) · D4 nav=100%(floor) · D9 brief-forge=0% · D7 pack=0% · D13 obs=0% · D6 recovery=0% · D5 checkpoints=0%

### Regular skills (n=116)

| Component | D14 necessity | D12 gap | D4 nav | D9 brief-forge | D7 pack | D13 obs | D6 recovery | D5 checkpoints |
|---|---|---|---|---|---|---|---|---|
| `adr-new` | — | — | — | — | — | — | — | — |
| `analyze` | yes | yes | — | — | — | — | — | — |
| `audit` | — | — | — | — | — | — | — | — |
| `autoplan` | — | — | — | — | — | — | — | — |
| `brief-forge` | — | — | — | — | — | — | — | — |
| `browse` | — | — | — | — | — | — | — | — |
| `build` | yes | yes | — | — | — | — | — | — |
| `capture` | yes | yes | — | — | — | — | — | — |
| `careful` | — | — | — | — | — | — | — | — |
| `catalog` | — | — | — | — | — | — | — | — |
| `clean` | — | — | — | — | — | — | — | — |
| `cli-fingerprint` | — | — | — | — | — | — | — | — |
| `code-freeze` | — | — | — | — | — | — | — | — |
| `code-review` | — | — | — | — | — | — | — | — |
| `code-unfreeze` | — | — | — | — | — | — | — | — |
| `codex` | — | — | — | — | — | — | — | — |
| `compliance-gate` | — | — | — | — | — | — | — | — |
| `context-budget` | — | — | — | — | — | — | — | — |
| `context-cool` | — | — | — | — | — | — | — | — |
| `context-restore` | — | — | — | — | — | — | — | — |
| `context-save` | — | — | — | — | — | — | — | — |
| `context-warm` | — | — | — | — | — | — | — | — |
| `context-warm-adrs` | — | — | — | — | — | — | — | — |
| `context-warm-customer` | — | — | — | — | — | — | — | — |
| `context-warm-from-url` | — | — | — | — | — | — | — | — |
| `context-warm-related` | — | — | — | — | — | — | — | — |
| `context-warm-sessions` | — | — | — | — | — | — | — | — |
| `define` | yes | yes | — | — | — | — | — | — |
| `design-consultation` | — | — | — | — | — | — | — | — |
| `design-html` | — | — | — | — | — | — | — | — |
| `design-review` | — | — | — | — | — | — | — | — |
| `design-shotgun` | — | — | — | — | — | — | — | — |
| `devex-review` | — | — | — | — | — | — | — | — |
| `discover` | yes | yes | — | — | — | — | — | — |
| `doctor` | — | — | — | — | — | — | — | — |
| `document-generate` | — | — | — | — | — | — | — | — |
| `eval` | — | — | — | — | — | — | — | — |
| `fix` | yes | yes | — | — | — | — | — | — |
| `frontend-design` | — | — | — | — | — | — | — | — |
| `frontend-design-review` | — | — | — | — | — | — | — | — |
| `frontend-motion` | — | — | — | — | — | — | — | — |
| `frontend-shader` | — | — | — | — | — | — | — | — |
| `frontend-style-extract` | — | — | — | — | — | — | — | — |
| `frontend-typography` | — | — | — | — | — | — | — | — |
| `generate` | — | — | — | — | — | — | — | — |
| `generate-app` | — | — | — | — | — | — | — | — |
| `generate-design` | — | — | — | — | — | — | — | — |
| `generate-outline` | — | — | — | — | — | — | — | — |
| `generate-pdf` | — | — | — | — | — | — | — | — |
| `generate-ppt` | — | — | — | — | — | — | — | — |
| `generate-qa` | — | — | — | — | — | — | — | — |
| `generate-style-learn` | — | — | — | — | — | — | — | — |
| `generate-visio` | — | — | — | — | — | — | — | — |
| `generate-web` | — | — | — | — | — | — | — | — |
| `generate-word` | — | — | — | — | — | — | — | — |
| `generate-write` | — | — | — | — | — | — | — | — |
| `generate-xlsx` | — | — | — | — | — | — | — | — |
| `handoff-size-check` | — | — | — | — | — | — | — | — |
| `health` | — | — | — | — | — | — | — | — |
| `help` | — | — | — | — | — | — | — | — |
| `hooks-status` | — | — | — | — | — | — | — | — |
| `instruction-parity-check` | — | — | — | — | — | — | — | — |
| `investigate` | — | — | — | — | — | — | — | — |
| `jobs` | — | — | — | — | — | — | — | — |
| `landing-report` | — | — | — | — | — | — | — | — |
| `learn` | — | — | — | — | — | — | — | — |
| `lessons` | — | — | — | — | — | — | — | — |
| `lessons-promote` | — | — | — | — | — | — | — | — |
| `lessons-surface` | — | — | — | — | — | — | — | — |
| `maintenance` | — | — | — | — | — | — | — | — |
| `make-pdf` | — | — | — | — | — | — | — | — |
| `migrations` | — | — | — | — | — | — | — | — |
| `office-hours` | — | — | — | — | — | — | — | — |
| `open-managed-browser` | — | — | — | — | — | — | — | — |
| `orientator` | — | — | — | — | — | — | — | — |
| `pack-create` | — | — | — | — | — | — | — | — |
| `pack-list` | — | — | — | — | — | — | — | — |
| `pack-switch` | — | — | — | — | — | — | — | — |
| `pack-validate` | — | — | — | — | — | — | — | — |
| `pair-agent` | — | — | — | — | — | — | — | — |
| `perfbench` | — | — | — | — | — | — | — | — |
| `perf-mode` | — | — | — | — | — | — | — | — |
| `personas-rotate` | — | — | — | — | — | — | — | — |
| `plan-and-build` | yes | yes | — | — | — | — | — | — |
| `plan-ceo-review` | — | — | — | — | — | — | — | — |
| `plan-design-review` | — | — | — | — | — | — | — | — |
| `plan-devex-review` | — | — | — | — | — | — | — | — |
| `plan-eng-review` | — | — | — | — | — | — | — | — |
| `plan-tune` | — | — | — | — | — | — | — | — |
| `profile-switch` | — | — | — | — | — | — | — | — |
| `qa` | — | — | — | — | — | — | — | — |
| `qa-only` | — | — | — | — | — | — | — | — |
| `research` | yes | yes | — | — | — | — | — | — |
| `resume` | — | — | — | — | — | — | — | — |
| `retro` | — | — | — | — | — | — | — | — |
| `review` | yes | yes | — | — | — | — | — | — |
| `review-and-ship` | yes | yes | — | — | — | — | — | — |
| `role` | — | — | — | — | — | — | — | — |
| `role-new` | — | — | — | — | — | — | — | — |
| `roles-list` | — | — | — | — | — | — | — | — |
| `safe-install` | — | — | — | — | — | — | — | — |
| `scaffold` | — | — | — | — | — | — | — | — |
| `scaffold-internal-tool` | — | — | — | — | — | — | — | — |
| `scaffold-mvp` | — | — | — | — | — | — | — | — |
| `scope` | yes | yes | — | — | — | — | — | — |
| `scrape` | — | — | — | — | — | — | — | — |
| `sense` | yes | yes | — | — | — | — | — | — |
| `setup-browser-cookies` | — | — | — | — | — | — | — | — |
| `ship` | yes | yes | — | — | — | — | — | — |
| `skillify` | — | — | — | — | — | — | — | — |
| `skill-router` | — | — | — | — | — | — | — | — |
| `status` | — | — | — | — | — | — | — | — |
| `uniformity` | — | — | — | — | — | — | — | — |
| `usage-log` | — | — | — | — | — | — | — | — |
| `v4-migrate` | — | — | — | — | — | — | — | — |
| `welcome` | yes | yes | yes | — | — | — | — | — |

Adoption: D14 necessity=12% · D12 gap=12% · D4 nav=0% · D9 brief-forge=0% · D7 pack=0% · D13 obs=0% · D6 recovery=0% · D5 checkpoints=0%

### Agents (n=69)

| Component | D14 necessity | D12 gap | D4 nav | D9 brief-forge | D7 pack | D13 obs | D11 delegate |
|---|---|---|---|---|---|---|---|
| `BlogPostDrafter` | — | — | n/a | — | — | — | n/a |
| `EmailCustomerDrafter` | — | — | n/a | — | — | — | n/a |
| `LinkedInPostDrafter` | — | — | n/a | — | — | — | n/a |
| `SlideNarrationCritic` | — | — | n/a | — | — | — | n/a |
| `EUAIActReviewer` | — | — | n/a | — | — | — | n/a |
| `GDPRReviewer` | — | — | n/a | — | — | — | n/a |
| `SOC2Reviewer` | — | — | n/a | — | — | — | n/a |
| `CustomerEmpathyCheck` | — | — | n/a | — | — | — | n/a |
| `DemoNarrativeArc` | — | — | n/a | — | — | — | n/a |
| `DemoNarratorJunior` | — | — | n/a | — | — | — | n/a |
| `ExecutiveBriefingDrafter` | — | — | n/a | — | — | — | n/a |
| `PostDemoFollowup` | — | — | n/a | — | — | — | n/a |
| `ProposalDrafter` | — | — | n/a | — | — | — | n/a |
| `RFPResponseDrafter` | — | — | n/a | — | — | — | n/a |
| `DevOpsToolchain` | — | — | n/a | — | — | — | n/a |
| `GHActionsReviewer` | — | — | n/a | — | — | — | n/a |
| `K8sManifestReviewer` | — | — | n/a | — | — | — | n/a |
| `PerformanceAnalyzer` | — | — | n/a | — | — | — | n/a |
| `TerraformReviewer` | — | — | n/a | — | — | — | n/a |
| `PPTNarrativeArchitect` | — | — | n/a | — | — | — | n/a |
| `WebExperienceCritic` | — | — | n/a | — | — | — | n/a |
| `WordTechnicalEditor` | — | — | n/a | — | — | — | n/a |
| `AccessibilityChecker` | — | — | n/a | — | — | — | n/a |
| `ADRDrafter` | — | — | n/a | — | — | — | n/a |
| `APIDesigner` | — | — | n/a | — | — | — | n/a |
| `Architect` | — | — | n/a | — | — | — | n/a |
| `BackendArchitect` | — | — | n/a | — | — | — | n/a |
| `CapacityPlanner` | — | — | n/a | — | — | — | n/a |
| `ChangelogMaintainer` | — | — | n/a | — | — | — | n/a |
| `CodeReviewer` | — | — | n/a | — | — | — | n/a |
| `ContextBudgetAdvisor` | — | — | n/a | — | — | — | n/a |
| `ContractTestArchitect` | — | — | n/a | — | — | — | n/a |
| `CostAnalyzer` | — | — | n/a | — | — | — | n/a |
| `DatabaseDesigner` | — | — | n/a | — | — | — | n/a |
| `DataPipelineDesigner` | — | — | n/a | — | — | — | n/a |
| `DebugForensics` | — | — | n/a | — | — | — | n/a |
| `DeploymentEngineer` | — | — | n/a | — | — | — | n/a |
| `DocWriter` | — | — | n/a | — | — | — | n/a |
| `Explorer` | — | — | n/a | — | — | — | n/a |
| `FrontendBuilder` | — | — | n/a | — | — | — | n/a |
| `LatencyAnalyzer` | — | — | n/a | — | — | — | n/a |
| `MigrationPlanner` | — | — | n/a | — | — | — | n/a |
| `Migrator` | — | — | n/a | — | — | — | n/a |
| `ObservabilityArchitect` | — | — | n/a | — | — | — | n/a |
| `PerfBudgetEnforcer` | — | — | n/a | — | — | — | n/a |
| `Planner` | — | — | n/a | — | — | — | n/a |
| `ReadOnly` | — | — | n/a | — | — | — | n/a |
| `Refactorer` | — | — | n/a | — | — | — | n/a |
| `RegressionDetective` | — | — | n/a | — | — | — | n/a |
| `ReleaseEngineer` | — | — | n/a | — | — | — | n/a |
| `ResearchSynthesizer` | — | — | n/a | — | — | — | n/a |
| `SanityChecker` | — | — | n/a | — | — | — | n/a |
| `SchemaArchitect` | — | — | n/a | — | — | — | n/a |
| `SystemArchitect` | — | — | n/a | — | — | — | n/a |
| `TestRunner` | — | — | n/a | — | — | — | n/a |
| `DesignSystemAuditor` | — | — | n/a | — | — | — | n/a |
| `FrontendArchitect` | — | — | n/a | — | — | — | n/a |
| `MotionDirector` | — | — | n/a | — | — | — | n/a |
| `ShaderEngineer` | — | — | n/a | — | — | — | n/a |
| `TypographyCurator` | — | — | n/a | — | — | — | n/a |
| `ComplianceOfficer` | — | — | n/a | — | — | — | n/a |
| `DependencyAuditor` | — | — | n/a | — | — | — | n/a |
| `JWTSecurityReviewer` | — | — | n/a | — | — | — | n/a |
| `OAuthFlowReviewer` | — | — | n/a | — | — | — | n/a |
| `PrivacyBoundaryAudit` | — | — | n/a | — | — | — | n/a |
| `SBOMAuditor` | — | — | n/a | — | — | — | n/a |
| `SecretsScanReviewer` | — | — | n/a | — | — | — | n/a |
| `SecurityAuditor` | — | — | n/a | — | — | — | n/a |
| `ThreatModelDrafter` | — | — | n/a | — | — | — | n/a |

Adoption: D14 necessity=0% · D12 gap=0% · D9 brief-forge=0% · D7 pack=0% · D13 obs=0%

### Block-hooks (n=2)

| Component | D14 necessity | D12 gap | D4 nav | D9 brief-forge | D7 pack | D13 obs | D6 recovery |
|---|---|---|---|---|---|---|---|
| `customer-data-block` | yes | yes | n/a | n/a | — | — | n/a |
| `secret-scan-block` | yes | yes | n/a | n/a | — | — | n/a |

Adoption: D14 necessity=100%(floor) · D12 gap=100%(floor) · D7 pack=0% · D13 obs=0%

### Warn-hooks (n=27)

| Component | D14 necessity | D12 gap | D4 nav | D9 brief-forge | D7 pack | D13 obs | D6 recovery |
|---|---|---|---|---|---|---|---|
| `context-bloat-warn` | — | — | n/a | n/a | — | — | n/a |
| `da-migration-irreversible-warn` | — | — | n/a | n/a | — | — | n/a |
| `da-retention-violation-warn` | — | — | n/a | n/a | — | — | n/a |
| `da-schema-drift-warn` | — | — | n/a | n/a | — | — | n/a |
| `dh-cost-budget-warn` | — | — | n/a | n/a | — | — | n/a |
| `dh-deploy-without-rollback-warn` | — | — | n/a | n/a | — | — | n/a |
| `dh-observability-gap-warn` | — | — | n/a | n/a | — | — | n/a |
| `frontend-design-surface` | — | — | n/a | n/a | — | — | n/a |
| `frozen-zone-warn` | — | — | n/a | n/a | — | — | n/a |
| `job-stale-warn` | — | — | n/a | n/a | — | — | n/a |
| `memory-budget-warn` | — | — | n/a | n/a | — | — | n/a |
| `no-customer-data-in-message` | — | — | n/a | n/a | — | — | n/a |
| `no-customer-data-in-screenshot` | — | — | n/a | n/a | — | — | n/a |
| `no-direct-main-push` | yes | yes | n/a | n/a | — | — | n/a |
| `no-merge-without-review` | — | — | n/a | n/a | — | — | n/a |
| `no-production-mutation-without-auth` | yes | yes | n/a | n/a | — | — | n/a |
| `no-secrets-in-edit` | — | — | n/a | n/a | — | — | n/a |
| `sc-auth-bypass-warn` | — | — | n/a | n/a | — | — | n/a |
| `sc-compliance-gap-warn` | — | — | n/a | n/a | — | — | n/a |
| `sc-threat-coverage-warn` | — | — | n/a | n/a | — | — | n/a |
| `session-digest` | yes | yes | n/a | n/a | — | — | n/a |
| `ta-arch-drift-warn` | — | — | n/a | n/a | — | — | n/a |
| `ta-complexity-budget-warn` | — | — | n/a | n/a | — | — | n/a |
| `ta-contract-collision-warn` | — | — | n/a | n/a | — | — | n/a |
| `tq-contract-break-warn` | — | — | n/a | n/a | — | — | n/a |
| `tq-coverage-drop-warn` | — | — | n/a | n/a | — | — | n/a |
| `tq-perf-regression-warn` | — | — | n/a | n/a | — | — | n/a |

Adoption: D14 necessity=11% · D12 gap=11% · D7 pack=0% · D13 obs=0%

### Lifecycle-hooks (n=2)

| Component | D14 necessity | D12 gap | D4 nav | D9 brief-forge | D7 pack | D13 obs | D6 recovery |
|---|---|---|---|---|---|---|---|
| `job-begin` | — | — | n/a | n/a | — | — | n/a |
| `job-end` | — | — | n/a | n/a | — | — | n/a |

Adoption: D14 necessity=0% · D12 gap=0% · D7 pack=0% · D13 obs=0%

### Packs (n=1)

| Component | D14 necessity | D7 pack | D4 nav | D9 brief-forge | D13 obs |
|---|---|---|---|---|---|
| `_default` | — | n/a | — | n/a | n/a |

Adoption: D14 necessity=0% · D4 nav=0%

---

Regenerate: `bin/li-uniformity`. Check-only (CI): `bin/li-uniformity --check`.
Floor gate: `bash tests/shape/uniformity-coverage.sh`.
