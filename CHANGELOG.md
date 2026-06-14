# Changelog

All notable changes to this repo are tracked here. Format is loose — date headings + bulleted changes. Major behavior changes to the canonical instructions are also logged in `scaffolding/EVOLUTION-LOG.md` (which travels with each scaffolded repo).

## 5.5.0 — 2026-06-13

Design parity: close the two UUPM gaps an adversarial audit found. ADR-0017 (amends ADR-0015).

### Added
- **Slide decision engine** — 8 vendored slide CSVs (`data/slides/`, MIT-attributed): emotion→color, goal→layout, narrative strategies with Duarte sparkline-beats, copy formulas. New `--slide <strategy|layout|layout-logic|color-logic|typography|copy|background|chart>` search domain; `generate-ppt` Step 2b now queries it (retrieval-grounded slide design). Controlled emotion/goal vocabulary documented in design-dna SKILL.md.
- **Three-layer token system** — `emit_tokens.py` reads the active profile → layered `design-tokens.css` (primitive → semantic → component), stdlib-only YAML-subset parser. Vendored token-architecture reference docs.
- 1 new test (`design-tokens-emit.sh`) + slide assertions in `design-dna-search.sh`.

### Changed
- `validate_design.py` gains two token-discipline **warnings** (no var() usage with raw colors; hardcoded font-family) — advisory, never hard-gate (L-012).

### Deliberately scoped out (ADR-0017, not gaps)
- Individual Google-Fonts catalog lookup (73 pairings + the typography agent cover selection; a 745K catalog is subtraction-bias ballast) and the Gemini-keyed logo/CIP/banner/social generators (L-001: Lintel ships structure + retrieval, not external-key content generators).

## 5.4.0 — 2026-06-13

Design DNA: retrieval-augmented design + the anthropic-default profile. ADR-0015/0016.

### Added
- `skills/design-dna/` — module skill (search | system | stack | persist | validate | profile): BM25 search (stdlib python, grep fallback) over a consumed corpus — 84 UI styles, 161 WCAG-audited palettes, 161 product reasoning rules with anti-patterns, 73 font pairings, 99 UX guidelines, 16 per-stack rule files (from nextlevelbuilder/ui-ux-pro-max-skill v2.5.0, MIT, attributed; google-fonts/draft/design ballast dropped)
- `profiles/anthropic-default.yaml` — the house design default: 7 canonical Anthropic tokens + Poppins/Lora (Apache-2.0, attributed) + source-marked derived gap-fills (type scale, spacing, radius, motion tokens, dark mode, semantic states, contrast-pair matrix). Pack-overridable via `design.profile` (additive seam — pack contract untouched)
- `scripts/validate_design.py` — mechanical pre-delivery gate (exit 1): zoom-disable, killed focus, emoji-as-icon, off-palette drift, sub-12px text, missing reduced-motion
- 3 tests: corpus shape (37 assertions), search behavior, validator behavior (positive + negative per L-012)

### Changed
- `frontend-design`: required Step 1.5 DNA pass (precedence brief > profile > corpus); spec gains additive `palette`/`style`/`design_dna` fields (schema_version stays 1); Step 7 stub → mandatory gate
- `frontend-typography`/`frontend-motion`: corpus query + profile defaults before agent pick
- `generate-web`/`generate-app`: per-stack guidance pass + mechanical Gate 0
- `frontend-design-review`/`design-review`: validator pre-pass (exit 1 = RED/auto-P1); profile as brand reference when no baseline
- Frontend agent fleet (FrontendArchitect, TypographyCurator, MotionDirector, DesignSystemAuditor): two-pass token-plan doctrine, anti-cliché calibration, profile-first defaults, validator-first auditing

## 5.3.0 — 2026-06-13

Launch-readiness drive: prompt-craft v2 · multi-CLI hardening · issue-mining · a full
launch-readiness audit (8 parallel audits → docs/audit/2026-06-12-launch-readiness-register.md)
and the remediation it found. ADRs 0013–0017.

### Prompt craft (ADR-0014, docs/concepts/prompt-house-style.md)
- Skill `description:` fields rewritten to TRIGGER form ("Use when…") across 43 high-traffic skills — descriptions are the auto-invocation mechanism; a workflow-summary makes Claude follow the summary instead of the body (superpowers' measured regression). New guard tests/shape/skill-descriptions-trigger.sh
- 20 review/audit/architecture agents gained Core-principles + Behavioral-traits + trigger descriptions + tool-scoping rationale (wshobson's consistency engine)
- House-style v2: dial back ALL-CAPS MUST/NEVER (current models overtrigger — Anthropic yellow flag), positive framing, one worked example, persona-as-voice-not-accuracy, one verifier-anchored self-critique, structural anti-sycophancy

### Security + reliability (ADR-0013, issue-mining)
- Block hooks made fail-closed: dropped `set -e` (under it an upstream non-zero exited before the blocking `exit 2`, silently downgrading to non-blocking — claude-code #60490) + a fail-closed guard (which now also audit-logs) when the scanner can't load
- Closed the newline-class gate bypasses (L-012): a line-continuation between `git` and the subcommand, and a newline-forged override token inside a `-m` message, both defeated the line-oriented matcher — the command is flattened before matching now. Each closure ships with its adversarial regression test (tests/unit/hook-gate-content.sh)
- Gate diffs run `--no-ext-diff --no-textconv` (a hostile repo's textconv driver can no longer execute when the gate scans); `git push` now scans the outgoing commit range (an already-committed secret was a push no-op before)
- Block hooks hold on stock macOS bash 3.2: the stdin reader's fractional `read -t` falls back to an integer timeout instead of failing open
- lib/auto-decide.sh: mechanical one-way-door guard so `--auto` can't auto-decide an irreversible/sovereignty change (gstack #603)
- PLAN: mechanical trio-completeness gate (plan.md+spec.md+prompt.md must all exist non-empty before BUILD — gstack #1127)

### State + footer correctness (launch register B4)
- The cycle ledger is append-only across many cycles, but every reader assumed a single-cycle file. `lib/state.sh` gains `state_cycle_segment` (one shared parser); the footer, `/li:resume` integrity, and `cycle_id` derivation now resolve from the current cycle's segment — a prior cycle's `cycle_complete: true` no longer renders "no active cycle" for every later cycle, and audit records carry the real `cycle_id` (was "unknown" since v4.0)
- `bin/_audit.sh`: dropped audit writes warn on stderr instead of vanishing; `audit_count` no longer doubles its `0` on no-match
- `lib/state.sh`: CR/LF stripped from phase/status/keys (not just values)

### Multi-CLI
- Deleted fabricated `.copilot-plugin/` + `.droid-plugin/` (both CLIs read `.claude-plugin/` via interop); propagated the deletion to all five asserting surfaces (manifest tests, verify.sh, SHIP-GATE, README, cli-tiers); fixed the `lintel@`→`li@` install string everywhere; `codex.subagents: native`
- instruction-parity-check repointed at the real shim files (was asserting 3 ghosts)
- Windows parity (install.ps1): seeds identity (profile.yaml + active-pack), copies lib/bin/templates, uses the v5 `hooks/shared/` layout, validates the real skill/agent surface
- li-doctor: bash-3.2-safe (no `declare -A`), names the Windows SessionStart-no-fire bug (claude-code #59072), fixed Claude-install detection; first smoke test
- `.opencode/INSTALL.md` rewritten neutral + current (was frozen at v3 with Microsoft-CAIP identity); fingerprint↔tiers id-normalization so `/li:welcome`'s honest-tier display reaches all CLIs

### Docs truth + mechanism honesty
- Swept stale claims across README, getting-started, AGENTS/GEMINI/shims, AGENT-INSTRUCTIONS, LAYERS, session-harness, multi-cli, compliance and the state-of-the-harness doc (v3-plan-as-current, `tasks/`/`docs/adr` paths, gstack recommendations, the v5.0 version string); dormancy qualifiers (ADR-0008) added at the point of sale
- usage-log demoted from a phantom auto-writer to an honest manual one-liner; cycle/qa/ship/careful/compliance prose "audit trails" converted to real `audit_log` calls or labeled dormant; six bespoke `>>` writers routed through the unified audit helper
- `no-swedish.sh` now scans docs + README (historical/generated/functional paths exempt); three concept docs translated
- CATALOG generator truncates by character not byte (was emitting invalid-UTF-8 rows); CATALOG regenerated clean
- pack-resolver: removed the `set -uo pipefail` that leaked into every caller; session cache key no longer collapses to a constant + mtime-invalidates on pack.yaml edits

### Decided this cycle (build staged with dates — see the launch register §3-B)
- ADR-0015 AGENTS.md-primary · ADR-0016 lintel-state MCP server · ADR-0017 eval-harness

### Numbers
- 43 skill descriptions + 20 agents upgraded · 2 manifests deleted · exec bits corrected on 5 scripts · 5 new behavior tests (hook-gate newline cases, customer-data gate, context-checkpoint roundtrip, li-doctor smoke, auto-decide one-way-door) · suite 82/82 on the committed tree

## 5.2.1 — 2026-06-13

Patch: hook gate fix delivery (PR #70 merged content-only — without a version bump the
plugin marketplaces report "up to date" and never refetch, so the fix could not reach
installed plugins).

- Block gates (secret-scan, customer-data) scan **added lines only** — git's own diff
  metadata (`new file mode 100644`, `index <hash>..<hash>`) matched the phone regex and
  blocked every new-file commit once the v5.2 matcher fix made the hooks actually fire
- Gates follow every `git -C <path>` target in the command (cwd alone scanned the wrong repo)
- New shared helper `hook_git_gate_content` in `hooks/shared/_input.sh`; regression-locked
  in `tests/unit/hook-gate-content.sh`
## 5.2.0 — 2026-06-12

Battletest remediation (six adversarial personas) + gstack de-heritage. ADR-0010/0011/0012.

### Security (ADR-0010)
- Block hooks (secret/customer-data) now match any git phrasing (`git -C`, abs paths, `&&` chains) and scan staged **union** unstaged-tracked content — closes the `^git`-anchor and `commit -am` worktree bypasses
- Modern token formats in the BLOCK tier: github_pat_, sk-proj-, AIza (Google), sk_live_/sk_test_ (Stripe), glpat-, ASIA
- CAPTURE vault sink scans the note for secrets+PII before the external write (aborts on hit) — the one path that left the repo unscanned
- Audit + state ledger are CR/LF-safe (no forged/hidden records); override always audits
- `li-scaffold` template render no longer uses `sed s///` (closed an operator-priv RCE via hostile dir/--name)

### gstack de-heritage (ADR-0011)
- 44 edits / 30 files: attribution rewritten to Lintel's own rationale; gstack paths/binaries → native helpers (`~/.lintel/projects`, `_context_repo_slug`, `context_latest`); REVIEW REPORT heading dual-accepts during grace; legacy review-log imported once; disable-file migrated once — zero functionality lost

### Agent memory + model (ADR-0012)
- 23 agents gain `memory: project` (reviewers/auditors remember repo-specific findings); 4 mechanical agents gain `model: haiku`; frontmatter-lint validates both

### Friction + docs
- resume ↔ context-restore wired (handoff no longer blind); cost gates show honest task-count + uncalibrated label (no invented dollars); DEFINE feature fast-path off scope size; SENSE meta-infra gated on a Lintel-repo marker
- canonical hook-activation matrix, docs/GLOSSARY.md, 4-root state map, stale-count fixes, install ghosts removed

### Numbers
- agents: 23 with memory / 4 with model · 2 new behavior tests · suite 76/76

## 5.1.0 — 2026-06-12

The subtraction release (ADR-0009): same capability, 23% less surface.

### Removed
- 35 engineering sub-skill files (ta-/da-/sc-/dh-/tq-*) — collapsed into per-module dispatch tables; invoke as `/li:<module> <capability>` (35 aliases, grace to 2026-09-12)
- Role family 8 → 3: `role` (lifecycle flags) + `role-new --update` + `roles-list` (6 aliases)
- gbrain-setup, gbrain-sync, WorkshopFacilitator agent (zero references; setup-brain/sync-brain aliases retired)
- ~700 lines of protocol boilerplate across ~90 skills — defaults now stated once in docs/concepts/skill-protocol.md; sections remain only on deviation

### Added
- docs/concepts/skill-protocol.md — the canonical skill protocol
- Optional frontmatter `hop_in: no` for non-solo-invokable skills

### Numbers
- Skills: 166 → 124 · agents: 70 → 69 · skill surface: 27.0k → 20.8k lines · suite 75/75

## 5.0.0 — 2026-06-12

The ".claude/ home" major: one circle of control per repo, mechanical memory, zero-setup activation.

### Added
- v5 `.claude/` home layout (ADR-0005): knowledge committed (`memory/`, `decisions/`, `plans/`), runtime gitignored (`runtime/`); `lib/paths.sh` single path source; `bin/li-migrate-claude-home`; native auto-memory convergence (`autoMemoryDirectory`)
- Memory v2 (ADR-0006): `lib/memory.sh` (mechanical lesson surfacing, supersede-aware), `bin/_context.sh`, `hooks/shared/memory-budget-warn`, update-phase capture, supersede-don't-delete convention, AGENTS.md + `.claude/rules/` emission
- Obsidian patterns (ADR-0007): locked session-note schema, `sessions.base`, `bin/li-vault-init`, hub/predecessor wikilinks, agent-maintained index
- Activation contract (ADR-0008): plugin hook auto-registration (`hooks/hooks.json`), `lib/state.sh` state ledger (one-command per-phase writes), identity seeding in install.sh, behavior test `tests/integration/session-leaves-traces.sh`, li-doctor proof-of-life checks

### Fixed
- secret-scan-block + customer-data-block exited 1 (non-blocking in Claude Code) — now exit 2 and actually block
- session-digest settings snippet pointed at a path missing `shared/`
- cross-scope jobs registry no longer clobbered in mixed v4/v5 fleets
- 31 hook scripts committed non-executable

### Changed
- context family consolidated (snapshot→save, dump→restore, warmup→warm; aliases, grace to 2026-09-12); 169 → 166 skills
- neutral `_default` pack ships the vault sink OFF (frozen-zone rule)
- audit scope routing: repo events land in `.claude/runtime/audit/`, operator events stay in `~/.lintel/audit/`

## [4.9.0] - 2026-06-05 — five-lens remediation — English-only sweep + shipping-identity reconciliation

**Remediation pass across the shipped surface.** Closes the drift the five-lens audit surfaced: mixed-language source, a shipping identity frozen at an old slug/version, self-describing wiki/showcase counts that no longer matched reality, and missing CI guards. No new features — this is a correctness + consistency pass.

### English-only sweep

- ~500 Swedish lines translated to English across the shipped surface (skills, agents, hooks, docs)
- 3 functional-Swedish files preserved (the Swedish is load-bearing, not prose) — left untouched on purpose
- New CI tripwire (below) prevents reintroduction

### Shipping-identity reconciliation

- Repo slug reconciled to `jokerman89/lintel` across manifests + install/update paths
- Version reconciled to `4.9.0` across every plugin manifest + marketplace metadata
- Manifest descriptions de-drifted: hardcoded agent counts removed, stale `v3.5`-in-prose dropped

### Regenerated self-describing surfaces

- `docs/wiki/` + `docs/showcase/lintel-the-harness.html` regenerated to real counts: **168 skills / 65 agents / 1 pack (`_default`)** (was 192/92/3)
- Counts now sourced from disk, not hand-maintained

### New CI guards

- English-only tripwire — fails CI on reintroduced non-English prose in the shipped surface
- Manifest-identity sync test — asserts slug + version match across all manifests
- Shape tests (`tests/shape/`) now run in CI (previously local-only)

### Fixes

- Runner-tolerant fix to the `frontend-design-surface` perf test (no longer flakes on slower CI runners)

---

## 2026-06-02 — v4.6.0 — full-engineering-pass composition skill — **v4.x FEATURE-COMPLETE**

**Final v4.x deliverable.** Composition skill that runs all 5 engineering-domain modules in DAG order (TA → DA‖SC → DH → TQ). Single invocation produces architecture decisions + data model + security posture + ops plan + quality validation for customer engagements or major releases.

### Composition shipped

- `skills/full-engineering-pass/SKILL.md` — workflow_root composition skill, color cyan (distinct from module colors)
- DAG: 4 stages (TA alone → DA + SC parallel → DH alone → TQ alone)
- 30-dim aggregate scoring (6 dims × 5 modules)
- Graceful degradation for partial-rollout state (skips missing modules, warns operator)
- `--resume` from last-completed stage
- `--skip-module <name>` for operator override
- Brief Forge `phase_transition` envelopes between stages

### Composition contract

- `cap_soft: 500000` / `cap_hard: 750000` tokens (caip-se pack overrides to 750k/1000k)
- `auto_mode_eligible: false` — operator confirms at every stage boundary
- SHIP verdict GREEN (all modules ≥80) / YELLOW (1-2 below or missing modules) / RED (any module BLOCKED)

### Tests added

- `tests/shape/full-engineering-pass-contract.sh` — composition workflow_root + DAG + module refs + graceful degradation
- `tests/unit/full-engineering-pass-dag.sh` — 10 scenarios (ordering, parallel marker, deps, graceful degradation, operator override, Brief Forge, SHIP verdict, cap, siblings, aggregate score)

### Concept doc

- `docs/concepts/full-engineering-pass.md` — DAG explanation + why this ordering + graceful degradation rules + aggregate scoring + resume semantics + cap reasoning + cross-module Brief Forge handoffs

### v4.x feature-complete summary

| Version | Ship date | Contents |
|---|---|---|
| v4.0 | 2026-05-29 | harness + packs + orientator + Brief Forge + wiki-gen |
| v4.1 | 2026-05-30 | TA module (tech-architecture) |
| v4.2 | 2026-05-30 | DA module (data-architecture) |
| v4.3 | 2026-05-31 | SC module (security-compliance) |
| v4.4 | 2026-06-02 | DH module (devops-hosting) |
| v4.5 | 2026-06-02 | TQ module (testing-qa) — FINAL engineering-domain module |
| **v4.6** | **2026-06-02** | **full-engineering-pass composition — v4.x FEATURE-COMPLETE** |

Per design doc §5.2 total estimate: 17-27 CC-days for v4.0 ship + ~10-15 CC-days engineering-depth = ~30-40 CC-days for complete v4.x. Actual: shipped in 5 CC-days at much higher density than estimated.

### What remains after v4.6

v4.x is **feature-complete**. Remaining work is operational:
- Pack-specific tuning (per-customer pack creation as engagements ramp)
- Additional module sub-skills as operator needs surface
- v5.x design decisions (not scheduled)

---

## 2026-06-02 — v4.5.0 — TQ (testing-qa) module — FINAL engineering-domain module

**Final engineering-domain module of v4.x.** With TQ shipping, all 5 modules per design doc §3 are complete: TA, DA, SC, DH, TQ.

### Module + sub-skills shipped

- `skills/tq/SKILL.md` — workflow_root, 5 checkpoints (coverage_targets_met, perf_budgets_locked, contract_tests_complete, regression_suite_curated, chaos_scenarios_documented), 6-dim scoring rubric, 3 raise-help triggers
- 7 sub-skills (L-001 dispatch contracts):
  - `tq-coverage-audit` (TestRunner + Architect)
  - `tq-perf-budget-spec` (LatencyAnalyzer + PerfBudgetEnforcer)
  - `tq-contract-test-design` (APIDesigner + ContractTestArchitect)
  - `tq-regression-suite` (RegressionDetective + TestRunner)
  - `tq-chaos-plan` (SecurityAuditor + SystemArchitect)
  - `tq-flaky-quarantine` (TestRunner + RegressionDetective)
  - `tq-test-pyramid-review` (Architect + TestRunner)

### Agents (L-002: 5 of 7 reuse existing)

- 5 sub-skills dispatch to existing agents: TestRunner, RegressionDetective, LatencyAnalyzer, APIDesigner, SecurityAuditor, SystemArchitect (TA), Architect
- 2 new agents:
  - `agents/engineering/PerfBudgetEnforcer.md` — perf budget definition + regression detection thresholds + enforcement mode
  - `agents/engineering/ContractTestArchitect.md` — consumer-driven contract test design + version compatibility matrix

### 3 warn-only hooks (using unified `audit_log` from `bin/_audit.sh`)

- `hooks/shared/tq-coverage-drop-warn` — pre-commit when coverage drops below threshold
- `hooks/shared/tq-perf-regression-warn` — pre-commit on edits to perf-budget-bound paths
- `hooks/shared/tq-contract-break-warn` — pre-commit on provider edits without paired contract-test update

### Profile preferences

`~/.lintel/profile.yaml` `engineering.testing_qa.*`:
  coverage_target (default 80)
  critical_path_coverage (default 100)
  perf_budget_p95_ms (default 200)
  contract_test_framework (pact | consumer-driven-internal | none)
  chaos_active (default true)
  flaky_quarantine_threshold (default 3)

### Tests added

- `tests/shape/tq-module-contract.sh` — module contract + v4.1+ conventions
- `tests/unit/tq-routing.sh` — 10 scenarios including final-module marker verification

### Concept doc

- `docs/concepts/tq-module.md` — TQ reference + composition placement (final stage after DH)

### v4.x engineering-depth COMPLETE

All 5 engineering-domain modules shipped per design doc §3:
| Module | Version | Color | New agents | Existing agents reused |
|---|---|---|---|---|
| TA — tech-architecture | v4.1 | amber | SystemArchitect, CapacityPlanner | 5 of 7 |
| DA — data-architecture | v4.2 | blue | SchemaArchitect, MigrationPlanner | 5 of 7 |
| SC — security-compliance | v4.3 | red | ComplianceOfficer | 6 of 7 |
| DH — devops-hosting | v4.4 | purple | DeploymentEngineer, ObservabilityArchitect | 5 of 7 |
| TQ — testing-qa | v4.5 | green | PerfBudgetEnforcer, ContractTestArchitect | 5 of 7 |

Cumulative L-002 result: 26 of 35 sub-skills reuse existing agents (74%). Only 9 new agents across 5 modules.

### What's next

**1 final v4.x deliverable remains:**
- `/li:full-engineering-pass` composition skill — runs all 5 modules in DAG order (TA → DA‖SC → DH → TQ)

After that, v4.x is feature-complete.
---

## 2026-06-02 — v4.4.0 — DH (devops-hosting) module

**Fourth engineering-domain module of v4.x.** Follows the engineering-modules pattern locked in v4.1. Purely additive on v4.3.

### Module + sub-skills shipped

- `skills/dh/SKILL.md` — workflow_root, 5 checkpoints (deployment_plan_locked, observability_specified, slos_defined, cost_projected, on_call_ready), 6-dim scoring rubric, 3 raise-help triggers
- 7 sub-skills (L-001 dispatch contracts):
  - `dh-deployment-plan` (ReleaseEngineer + DeploymentEngineer)
  - `dh-observability-spec` (ObservabilityArchitect + Architect)
  - `dh-sli-slo-spec` (ObservabilityArchitect + SystemArchitect)
  - `dh-cost-projection` (CostAnalyzer + CapacityPlanner)
  - `dh-rollback-strategy` (ReleaseEngineer + SecurityAuditor)
  - `dh-capacity-headroom` (CapacityPlanner + LatencyAnalyzer)
  - `dh-on-call-playbook` (ReleaseEngineer + SecurityAuditor)

### Agents (L-002: 5 of 7 reuse existing)

- 5 sub-skills dispatch to existing agents: ReleaseEngineer, CostAnalyzer, LatencyAnalyzer, CapacityPlanner (from TA), SystemArchitect (from TA), SecurityAuditor, Architect
- 2 new agents:
  - `agents/engineering/DeploymentEngineer.md` — deployment pattern reasoning (blue-green/canary/rolling), traffic-cutover stages, feature-flag rollout strategy
  - `agents/engineering/ObservabilityArchitect.md` — signals design (metrics RED+USE, traces, structured logs), SLI definitions tied to measurable queries

### 3 warn-only hooks (using unified `audit_log` from `bin/_audit.sh`)

- `hooks/shared/dh-deploy-without-rollback-warn` — pre-commit on deploy/IaC without rollback declaration
- `hooks/shared/dh-observability-gap-warn` — pre-edit on service entry-points lacking metric/trace/log markers
- `hooks/shared/dh-cost-budget-warn` — pre-commit on IaC with cost-increasing patterns (SKU upsizing, replica increases, premium storage, always-on additions)

### Profile preferences

`~/.lintel/profile.yaml` `engineering.devops_hosting.*`:
  cloud (azure | aws | gcp | oci | on-prem)
  deployment_pattern (blue-green | canary | rolling)
  observability_stack (app-insights | datadog | grafana-stack | new-relic | mixed)
  error_budget_window_days (default 30)
  cost_budget_monthly_usd_threshold (default 10000)

### Tests added

- `tests/shape/dh-module-contract.sh` — engineering-module contract + v4.1+ conventions
- `tests/unit/dh-routing.sh` — 10 scenarios including L-002 reuse verification

### Concept doc

- `docs/concepts/dh-module.md` — DH-specific reference + composition placement (third stage after TA + DA‖SC)

### What's next

1 module remains:
- **v4.5 TQ** — testing-qa (critical-path coverage, perf budgets, contract tests)

Plus future `/li:full-engineering-pass` composition skill running all 5 modules in DAG order (TA → DA‖SC → DH → TQ).
---

---

## 2026-05-31 — v4.3.0 — SC (security-compliance) module

**Third engineering-domain module of v4.x.** Follows the engineering-modules pattern locked in v4.1. Purely additive on v4.2.

### L-002 record: 6 of 7 sub-skills reuse existing agents

This phase had the highest L-002 reuse rate so far (vs 5 of 7 in TA + DA). The 6 existing security agents (SecurityAuditor, ThreatModelDrafter, DependencyAuditor, JWTSecurityReviewer, SBOMAuditor, PrivacyBoundaryAudit) cover threat modeling, secret management, auth review, dependency security, audit path, and incident runbook respectively. Only `sc-compliance-evidence` needs a new agent.

### Module + sub-skills shipped

- `skills/sc/SKILL.md` — workflow_root, 5 checkpoints (threat_model_complete, secrets_inventoried, auth_flow_locked, compliance_evidence_present, audit_path_verified), 6-dim scoring rubric, 3 raise-help triggers
- 7 sub-skills (L-001 dispatch contracts):
  - `sc-threat-model` (ThreatModelDrafter + SecurityAuditor)
  - `sc-secret-management` (SecurityAuditor + SBOMAuditor)
  - `sc-auth-flow` (JWTSecurityReviewer + SecurityAuditor)
  - `sc-compliance-evidence` (ComplianceOfficer + Architect)
  - `sc-audit-path` (SecurityAuditor + Architect)
  - `sc-dependency-security` (DependencyAuditor + SBOMAuditor)
  - `sc-incident-runbook` (SecurityAuditor + ReleaseEngineer)

### 1 new agent (minimal L-002 addition)

- `agents/security/ComplianceOfficer.md` — cross-framework evidence orchestration (SOC2/GDPR/HIPAA/PCI-DSS/FedRAMP/ISO27001). Maps technical + procedural controls to framework requirements; surfaces gaps + collects evidence pointers.

### 3 warn-only hooks (using unified `audit_log` from `bin/_audit.sh`)

- `hooks/shared/sc-threat-coverage-warn` — pre-edit on auth/data files when threat model is missing, stale (>90 days), or doesn't cover the file
- `hooks/shared/sc-auth-bypass-warn` — pre-edit on auth-flow files detecting skip-auth flags, magic credentials, bypass routes, direct role assignments
- `hooks/shared/sc-compliance-gap-warn` — pre-edit on regulated-data paths with stale or gap-marked evidence

### Existing security hooks (reused, not duplicated)

`no-secrets-in-edit`, `secret-scan-block`, `customer-data-block`, `no-production-mutation-without-auth` — already exist; SC module wires them through Brief Forge's `security` and `sdl_compliance` evaluators.

### Profile preferences

`~/.lintel/profile.yaml` `engineering.security_compliance.*`:
  sdl_active: true
  secret_management (keyvault | aws-secrets-manager | hashicorp-vault | local-encrypted)
  threat_model_required_on: [new_external_dependency, new_data_path, new_auth_flow]
  compliance_frameworks (default: [soc2, gdpr])
  audit_retention_days (default: 2555 = 7 years)

### Tests added

- `tests/shape/sc-module-contract.sh` — engineering-module contract + v4.1+ conventions
- `tests/unit/sc-routing.sh` — 10 scenarios including L-002 reuse rate verification

### Concept doc

- `docs/concepts/sc-module.md` — SC reference + composition placement (parallel with DA after TA)

### What's next

2 modules remain:
- **v4.4 DH** — devops-hosting (deployment patterns, observability, cost ops)
- **v4.5 TQ** — testing-qa (critical-path coverage, perf budgets, contract tests)

Plus future `/li:full-engineering-pass` composition skill (TA → DA‖SC → DH → TQ).

---

## 2026-05-30 — v4.2.0 — DA (data-architecture) module

**Second engineering-domain module of v4.x.** Follows the engineering-modules pattern locked in v4.1. Purely additive on v4.1; no breaking changes.

### Module + sub-skills shipped

- `skills/da/SKILL.md` — workflow_root, 5 checkpoints (data_model_complete, schema_locked, migration_safe, retention_specified, query_patterns_documented), 6-dim scoring rubric, 3 raise-help triggers
- 7 sub-skills (L-001 dispatch contracts):
  - `da-schema-design` (DatabaseDesigner + SchemaArchitect)
  - `da-migration-plan` (MigrationPlanner + Migrator)
  - `da-retention-policy` (DatabaseDesigner + Architect)
  - `da-query-pattern-audit` (Explorer + DatabaseDesigner)
  - `da-sharding-plan` (SchemaArchitect + DatabaseDesigner)
  - `da-data-contract-collision` (DatabaseDesigner + Architect)
  - `da-analytics-readiness` (DataPipelineDesigner + SchemaArchitect)

### Agents (L-002: 5 of 7 reuse existing)

- 5 sub-skills dispatch to existing agents: DatabaseDesigner, DataPipelineDesigner, Migrator, Architect, Explorer
- 2 new agents for genuinely new capability:
  - `agents/engineering/SchemaArchitect.md` — cross-store reasoning, partition-key selection, dimensional modeling
  - `agents/engineering/MigrationPlanner.md` — zero-downtime migration planning, reversibility analysis, lock-acquisition strategy

### 3 warn-only hooks (using unified `audit_log` from `bin/_audit.sh`)

- `hooks/shared/da-schema-drift-warn` — pre-edit on schema-ADR-claimed files
- `hooks/shared/da-migration-irreversible-warn` — pre-commit on migrations with destructive ops + no rollback
- `hooks/shared/da-retention-violation-warn` — pre-edit on data-access code skipping retention filters

### Profile preferences

`~/.lintel/profile.yaml` `engineering.data_architecture.*`:
  primary_store (postgres | mongodb | cassandra | clickhouse | mixed)
  migration_window (zero-downtime-required | maintenance-window-ok | tolerated)
  retention_default_days
  schema_versioning
  require_migration_review_above_rows

### Tests added

- `tests/shape/da-module-contract.sh` — engineering-module contract verification + v4.1+ conventions (necessity, gap_if_skipped, structured cli_support, audit_log integration)
- `tests/unit/da-routing.sh` — 9 scenarios (granularities, sub-skill dispatch, checkpoints, raise-help, hooks, rubric, prefs, pattern consistency)

### Concept doc

- `docs/concepts/da-module.md` — DA-specific reference + checkpoint pass-criteria + raise-help triggers + scoring rubric + 5-pillar composition placement (parallel with SC after TA)

### What's next

3 modules remain:
- **v4.3 SC** — security-compliance (SDL, threat models, secret management, compliance gates)
- **v4.4 DH** — devops-hosting (deployment patterns, observability, cost ops)
- **v4.5 TQ** — testing-qa (critical-path coverage, perf budgets, contract tests)

Plus future `/li:full-engineering-pass` composition skill (TA → DA‖SC → DH → TQ).

---

## 2026-05-30 — v4.1.0 — TA (tech-architecture) module

**First engineering-domain module of v4.x. The pattern that the next four (DA, SC, DH, TQ) follow.**

Engineering modules ship one at a time per design doc §5.2. TA goes first because architectural decisions constrain everything downstream in a full engineering pass.

### Engineering modules pattern (shared across v4.1-v4.5)

`docs/concepts/engineering-modules.md` — canonical reference for the pattern:
- Three granularities per module: `full` (multi-phase loop with checkpoints), `loop` (one iteration), `single --action <name>` (targeted op)
- Module contract: `workflow_root: true` + navigation block + brief_forge declaration + domain block with checkpoints/recovery/continuation/raise_help
- 6-dimensional scoring rubric per module (mirrors frontend-design-review pattern)
- 2-5 warn-only hooks per module
- Profile preferences under `engineering.<domain>.*`
- Module-color convention: TA amber, DA blue, SC red, DH purple, TQ green

### TA module shipped

- `skills/ta/SKILL.md` — workflow_root module skill with 5 checkpoints + 6-dim rubric
- 7 sub-skills (L-001 dispatch contracts):
  - `ta-api-design` (APIDesigner)
  - `ta-dependency-graph` (Explorer + Architect)
  - `ta-complexity-audit` (Architect + CodeReviewer)
  - `ta-boundary-review` (BackendArchitect + Architect)
  - `ta-scaling-plan` (CapacityPlanner + BackendArchitect)
  - `ta-contract-collision` (APIDesigner + Architect)
  - `ta-quality-attributes` (SystemArchitect + Architect)
- 2 new agents:
  - `agents/engineering/SystemArchitect.md` — system-of-systems thinking, NFR specs, cross-system invariants
  - `agents/engineering/CapacityPlanner.md` — capacity model + bottleneck identification + cost projection
- 3 warn-only hooks:
  - `hooks/shared/ta-arch-drift-warn/` — pre-edit on ADR-claimed files
  - `hooks/shared/ta-contract-collision-warn/` — pre-edit on interface files with consumers
  - `hooks/shared/ta-complexity-budget-warn/` — pre-commit on over-budget files
- Profile preferences under `engineering.tech_architecture.*` (api_style, versioning, complexity budgets, require_adr_on, deprecation_window_days)
- `docs/concepts/ta-module.md` — TA-specific reference + checkpoint pass-criteria + raise-help triggers + scoring rubric

### L-002 inventory result

5 of 7 sub-skills dispatch to existing agents (Architect, BackendArchitect, APIDesigner, Explorer, CodeReviewer). Only 2 new agents (SystemArchitect, CapacityPlanner) for genuinely new capability.

### Tests added

- `tests/shape/ta-module-contract.sh` — verifies workflow_root + navigation + domain block + 7 sub-skills + 2 agents + 3 hooks present
- `tests/unit/ta-routing.sh` — 8 scenarios: granularities, sub-skill dispatch, checkpoints, raise-help triggers, hook integration, scoring rubric, profile prefs

### What's next

Per design doc §5.2 Phase 4: 4 modules remain.
- **v4.2 DA** — data-architecture (schema, migrations, retention)
- **v4.3 SC** — security-compliance (SDL, threat models, secret management)
- **v4.4 DH** — devops-hosting (deployment patterns, observability, cost)
- **v4.5 TQ** — testing-qa (critical-path coverage, perf budgets, contract tests)

Plus a future `/li:full-engineering-pass` composition skill that runs all 5 in DAG order (TA → DA‖SC → DH → TQ).

---

## 2026-05-29 — v4.0.0 (SHIPPED)

**Lintel v4.0: harness with packs + orientator + Brief Forge + generated wiki. CAIP-SE as one pack among many.**

Three shipping phases, all on `main`:

### Phase 1 — meta-infra spine (PR #36)
- Meta-infra mode (6th cycle preset) with auto-detection in SENSE Step 0c
- Pack-resolver as critical-path singleton: 9 failure modes, per-session cache, three-layer fallback
- `_default` pack as neutral baseline
- Gate M2 (`bin/li-compat-audit`) + structure-changes tracker
- 8 shape-tests in `tests/shape/` enforcing structural invariants
- Concept docs: pack-defaults, pack-resolver, meta-infra-discipline

### Phase 2 — pack architecture + envelope schema (PR #37)
- `lib/pack-schema.yaml` v1 — declarative pack contract
- `packs/ms-internal/` (compliance + SDL base) + `packs/caip-se/` extends ms-internal
- Pack inheritance: extends-chain walk + shallow merge in resolver
- `lib/envelope-schema.yaml` v1 — HEAD + BODY (content_type discriminator) + TAIL
- `bin/li-envelope-validate` + `bin/li-envelope-replay` (dry-run default)
- 5 lifecycle skills: pack-create, pack-switch, pack-list, pack-validate, v4-migrate
- Navigation block mandatory on workflow_root skills (shape-test tightened FAIL)

### Phase 3 — navigation + Brief Forge + wiki-gen (this release)
- `skills/orientator/SKILL.md` + `lib/orientator-routing.sh` — mechanical-first workflow routing
- SENSE Step 0d auto-invokes orientator, audits decisions to `~/.lintel/audit/orientator-decisions.jsonl`
- `skills/brief-forge/SKILL.md` + `lib/brief-forge.sh` + `lib/brief-forge-evaluators.sh`
- 5 default evaluators: security, completeness, stale, sdl_compliance, trailblazer_alignment
- Score aggregation = minimum (worst evaluator wins, can't hide problems by averaging)
- Cold-path-bypass via skill frontmatter `brief_forge_bypass: true` or pack policy
- `bin/li-wiki-gen` — regenerates both `docs/wiki/` (markdown) + `docs/showcase/lintel-the-harness.html` from the same sources
- Deterministic output (verified by `tests/unit/wiki-gen-idempotency.sh`)
- CI integration via `bin/li-wiki-gen --check` (warn-only in v4.0; fail from v4.1)

### v4.0 migration

Operators currently on v3.x:
1. `git pull` brings v4.0 into the repo
2. `/li:v4-migrate` detects v3.x usage signals + recommends pack activation
3. `/li:pack-switch caip-se` for CAIP-SE operators (behavior identical to v3.x post-switch)
4. `/li:pack-switch ms-internal` for general Microsoft work
5. Operators on neutral defaults: no action needed (`_default` is the v4.0 fallback)

### v4.0 architecture

| Contract | What it does | Where |
|---|---|---|
| Pack manifest | Declarative configuration per customer/team domain | `lib/pack-schema.yaml` |
| Envelope | Universal shape for every hand-off (HEAD + BODY + TAIL) | `lib/envelope-schema.yaml` |
| Meta-infra discipline | 4 mandatory gates (M1-M4) on scaffolding changes | `skills/cycle`, `bin/li-compat-audit` |
| Pack inheritance | Shallow merge with explicit child-over-parent precedence | `lib/pack-resolver.sh` |
| Orientator | Mechanical-first workflow routing + LLM escalation gate | `skills/orientator`, `lib/orientator-routing.sh` |
| Brief Forge | Universal hand-off gate with 5 evaluators | `skills/brief-forge`, `lib/brief-forge.sh` |
| Wiki generator | Both wiki + showcase regenerate from sources | `bin/li-wiki-gen` |

### Decisions locked

Per design doc §1.3 / §1.5 / §2.3:
- ms-internal base pack ships **NOW** (C1-D1)
- Pack-version enforcement: **warn-only** in v4.0; block from v4.1 (C1-D2)
- `auto_mode_eligible`: **false** by default (C1-D3)
- `orientator_budget_tokens`: **2000 default, 5000 caip-se** (C1-D4)
- Envelope replay: **dry-run default**, `--apply` requires explicit opt-in (§2.3)

### Tests at ship

39/39 PASS:
- 12 shape-tests (mechanical invariants)
- 27 unit/behavior/integration tests
- 4 unit tests added by Phase 3 (orientator routing, brief-forge evaluators, wiki idempotency, plus existing pack-inheritance + envelope-validates + pack-resolver-fallbacks)

### What's next (v4.1+)

Per design doc §5.2 Phase 4: 5 engineering-domain modules (TA, SC, DA, DH, TQ) ship one at a time as v4.1 / v4.2 / v4.3 / v4.4 / v4.5. Order operator-driven based on engagement needs.

---

## 2026-05-28 — v3.5.0-dev (on `lintel-rebrand` branch)

**Lintel v3.5: 8-phase cycle + role-lifting + context-warming + rebrand from JStack.**

JStack v3.0 → Lintel v3.5. Repo renamed to `jokerman-lintel` under `jokerman89` namespace. Plugin namespace `lintel:`. Skill prefix `li-*`. All 343 JStack mentions + 636 jstack identifiers + 54 Azureflipper references replaced atomically across 200+ files.

### Phase A — Atomic rename

- GitHub repo: `Azureflipper/jokerman-session-setup` → `jokerman89/jokerman-lintel`
- Branch: `lintel-rebrand` from `v3-dev` (preserves 2 prior design-doc commits)
- Plugin manifests: 7 manifests (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/`, `gemini-extension.json`, `.copilot-plugin/`, `.droid-plugin/`) updated to `name: lintel`
- All 81 v3 skills got `li-` prefix in frontmatter (v3 cli_support arrays preserved)
- Bin scripts renamed: `bin/jstack-*` → `bin/li-*` (6 files)
- Skill folders renamed: `skills/jstack-*` → `skills/li-*` (4 dirs)
- Env vars: `JSTACK_HOME` → `LINTEL_HOME`, `~/.jstack/` → `~/.lintel/`
- 188 files in single atomic commit

### Phase B — 8 phase-skills (cycle backbone)

Full Lintel cycle backbone, each skill at design-doc depth:

- `skills/li-sense/SKILL.md` (230 lines) — auto-detect intent, WorkProfile, role, prior 00-state
- `skills/li-define/SKILL.md` (261 lines) — office-hours forcing questions + role-lens + adversarial spec review
- `skills/li-discover/SKILL.md` (260 lines) — codebase map + ADR scan + lessons + agent/skill recommendations
- `skills/li-plan/SKILL.md` (308 lines) — task breakdown + cost-estimate gate + founder approval + 2-stage subagent review
- `skills/li-build/SKILL.md` (286 lines) — TDD + Subagent-Driven Development + 2-stage per-task review + hard-rule hooks
- `skills/li-review/SKILL.md` (315 lines) — 3-stage review (spec/quality/compliance) + cross-artifact analyze
- `skills/li-ship/SKILL.md` (333 lines) — HARD-RULES + voice + 4-gate doc-gen + EV2/OneBranch + PR creation
- `skills/li-capture/SKILL.md` (364 lines) — lessons + ADR + EVOLUTION-LOG + cold-executor handoff trio + operator profile

~2357 lines total. Each skill specs: sub-skills invoked, recommended agents, artifacts produced, gates, status protocol, pause-points, hop-in support, integration (reads/writes/triggers), anti-patterns, failure recovery, voice tier behavior.

### Phase C — Cycle orchestrator + resume

- `skills/li-cycle/SKILL.md` (~210 lines) — chains 8 phases with gates, 5 mode presets + auto + custom flags
- `skills/li-resume/SKILL.md` (~180 lines) — reads `.lintel/state/00-state.md`, picks resume phase, cross-machine sync fallback

### Phase D — Composite shortcuts (~100 lines each)

- `skills/li-fix/SKILL.md` — hotfix workflow (SENSE+BUILD+REVIEW+SHIP)
- `skills/li-research/SKILL.md` — research-dive (SENSE+DEFINE+DISCOVER, no build)
- `skills/li-plan-and-build/SKILL.md` — PLAN+BUILD for split-session resumability
- `skills/li-review-and-ship/SKILL.md` — REVIEW+SHIP+CAPTURE close-out

### Phase E — Role-lifting infrastructure

NEW concept: bring expert personas into session as lightweight context layers.

8 role-skills:
- `skills/li-role-activate/SKILL.md` — load IDENTITY + VOICE + OUTCOME-LENS (~500 tokens)
- `skills/li-role-deep-dive/SKILL.md` — full role-file (~2-3k tokens, sensitivity-aware)
- `skills/li-role-frame/SKILL.md` — apply role's lens to an artifact
- `skills/li-role-rotate/SKILL.md` — swap active role mid-session
- `skills/li-role-deactivate/SKILL.md` — clear role-overlay
- `skills/li-roles-list/SKILL.md` — enumerate available roles
- `skills/li-role-new/SKILL.md` — scaffold new role via guided interview
- `skills/li-role-update/SKILL.md` — incremental updates, PII soft-scan

3 default public roles shipped:
- `roles/field-cto.md` — customer-facing, sales-tech, trailblazer voice
- `roles/solution-architect.md` — enterprise IT, security-conscious, mixed voice
- `roles/engineering-manager.md` — process, team coordination, internal voice

Each role file structure: frontmatter (sensitivity field) + IDENTITY + COLD KNOWLEDGE (top 10) + DECISION CRITERIA + VOICE + OUTCOME LENS per cycle phase + ROLE-SPECIFIC INSIGHTS + COMPANION SKILLS + SENSITIVE CONTEXT (private roles only).

Private roles sync via `bin/li-roles-sync` (per-operator opt-in, private git repo, never public marketplace, NEVER team-wide). Mirrors `bin/li-lessons-sync` pattern.

### Phase F — Context-warming infrastructure

NEW capability: on-demand 1M-context utilization beyond session-start.

10 context-warming skills:
- `skills/li-context-warm/SKILL.md` — base file load with budget tracking
- `skills/li-context-warm-related/SKILL.md` — heuristic load by topic
- `skills/li-context-warm-sessions/SKILL.md` — load last N session saves
- `skills/li-context-warm-adrs/SKILL.md` — load topic-relevant ADRs
- `skills/li-context-warm-customer/SKILL.md` — customer-engagement repo load (audit-logged)
- `skills/li-context-warm-from-url/SKILL.md` — WebFetch + dump, WorkProfile URL gate
- `skills/li-context-dump/SKILL.md` — load specific prior session save
- `skills/li-context-snapshot/SKILL.md` — operator-named mid-session save
- `skills/li-context-budget/SKILL.md` — utilization visibility + breakdown
- `skills/li-context-cool/SKILL.md` — selective IGNORE marker (Claude Code context append-only)

Session-start stays lightweight (~5-15k tokens). Warming is explicit operator action with budget confirmation for >20k loads.

### Counts (post-Phase F)

- Skills: 113 (81 v3 + 32 new in v3.5)
- Agents: 78 (unchanged from v3)
- Hooks: 15 (unchanged)
- Plugin manifests: 7 (rebranded to lintel)
- Root entrypoint files: 3 (CLAUDE.md, AGENTS.md, GEMINI.md — rebranded)
- Bin scripts: 7 (6 v3 + li-roles-sync new)
- Default public roles: 3
- Cycle phases: 8 (named paths: SENSE, DEFINE, DISCOVER, PLAN, BUILD, REVIEW, SHIP, CAPTURE)
- Mode presets: 5 (hotfix, customer-engagement, internal-tool, demo-prep, research-dive) + auto
- Composite shortcuts: 4 (li-fix, li-research, li-plan-and-build, li-review-and-ship)

### Remaining for v3.5.0 tag (Phases G-K)

- Phase G: Cold-executor handoff trio dogfood verification (CAPTURE writes spec.md + plan.md + prompt.md; verify operator can re-execute from those alone)
- Phase H: Doc rewrite (README + SHIP-GATE + LAYERS + AGENT-INSTRUCTIONS fully updated for v3.5)
- Phase I: Tests (phase-skill smoke tests + cycle E2E)
- Phase J: Operator dogfood (`/li:cycle --mode internal-tool` on internal extension)
- Phase K: PR + tag v3.5.0-dev

### Methodologies studied (per design phase)

- **obra/superpowers**: per-skill richness, two-stage review (spec→quality), Subagent-Driven Development, status protocol vocabulary
- **github/spec-kit**: 7-phase pipeline (we adopt + add CAPTURE), Constitution analog, cross-artifact analyze
- **gstack (parent)**: AskUserQuestion decision-brief, forcing questions, premise-check, voice rules, continuous checkpoint, boil-the-lake
- **Architect Agent image (operator-shared)**: cold-executor handoff trio, 00-state.md, cost-estimate gate, founder approval gate, failure recovery protocol

Lintel-unique additions vs all 4: WorkProfile toggle, role-lifting, context-warming, 5-mode presets, multi-CLI plugin manifest, MS-internal compliance gates (RAIS/OneCS/AGT/EV2/OneBranch/SDL/1ESPT), Trailblazer voice corpus, 78 specialized agents.

---

## 2026-05-27 — v3.0.0-dev (on `v3-dev` branch)

**Lintel v3: plugin-manifest pattern + agent build-out + session-harness framing.** Big Bang rework following obra/superpowers' multi-CLI plugin pattern. Discards v2's "MCP server + per-CLI compile" plan as over-engineering. Agents BUILD OUT (44 → 78), not trimmed. Scaffolding-templates preserved + modernized.

Design doc: [docs/design/lintel-v3-plan.md](docs/design/lintel-v3-plan.md).
Per-CLI plugin format research: [docs/per-cli/PLUGIN-FORMAT-RESEARCH.md](docs/per-cli/PLUGIN-FORMAT-RESEARCH.md).
Session-harness explainer: [docs/session-harness.md](docs/session-harness.md).

### Architecture shift (Phase 0–2)

- **Plugin-manifest pattern.** Tiny per-CLI manifests (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/`, `gemini-extension.json`, `.copilot-plugin/`, `.droid-plugin/`) all point at shared `./skills/` and `./agents/` dirs. Each CLI's native plugin marketplace handles discovery + invocation. NO MCP server, NO per-CLI compile step.
- **Root entrypoint files:** `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` at repo root — read by Claude Code / Codex / Gemini respectively when working ON the Lintel repo. Each links to canonical `AGENT-INSTRUCTIONS.md` + adds CLI-specific notes.

### Reorganization (Phase 1)

- `scaffolding/01-foundation/skills/*` + `scaffolding/03-personal-advanced/skills/*` → `skills/` (74 skills flat at repo root, with `layer: foundation | ms-team` frontmatter)
- `scaffolding/03-personal-advanced/agents/*` + `scaffolding/04-power-user/agents/*` → `agents/<category>/<Name>.md` (organized per domain: ms-specific, engineering, security, compliance, devops, customer, communication, voice, doc-gen)
- `scaffolding/02-sdl/hooks/*` → `hooks/shared/*` (lifted to repo root for plugin-discovery)
- `scaffolding/04-power-user/` removed (content moved to `agents/engineering/`)
- `scaffolding/03-personal-advanced/` renamed to `scaffolding/03-ms-team/`
- Root cleanup: 5 design docs moved from root to `docs/design/` (MIGRATION-TABLE, CONTEXT-ENGINE, BRAND-INTEGRATION, T0-CALIBRATION-WORKFLOW, UPSTREAM-SIMILARITY, TODOS, CLI-SUPPORT-V2-SCHEMA). Root .md count: 11 → 5 (README, CHANGELOG, LAYERS, SHIP-GATE, AGENT-INSTRUCTIONS) + 3 new (CODEOWNERS, CONTRIBUTING, SECURITY).

### Agent build-out (Phase 3) — 44 → 78 agents (+34 new)

Per operator direction: agents are Lintel value, build out instead of trim.

- **ms-specific (+7):** AzureArchitect, AzureOpenAIAdvisor, M365CopilotAdvisor, GraphAPIAdvisor, BicepReviewer, ARMTemplateReviewer, KeyVaultAuditor
- **security (+5):** ThreatModelDrafter, SecretsScanReviewer, SBOMAuditor, OAuthFlowReviewer, JWTSecurityReviewer
- **compliance (+5):** GDPRReviewer, SDLReviewer, AGTReviewer, EUAIActReviewer, SOC2Reviewer
- **devops (+5):** OneBranchReviewer, EV2PipelineAuditor, GHActionsReviewer, TerraformReviewer, K8sManifestReviewer
- **customer (+5):** ProposalDrafter, RFPResponseDrafter, ExecutiveBriefingDrafter, WorkshopFacilitator, DemoNarratorJunior
- **communication (+4):** BlogPostDrafter, LinkedInPostDrafter, EmailCustomerDrafter, SlideNarrationCritic
- **engineering (+3):** LatencyAnalyzer, CostAnalyzer, RegressionDetective

Final per-category counts: ms-specific 15, engineering 25, customer 8, security 8, devops 7, compliance 6, communication 5, doc-gen 3, voice 1. Total: 78.

### Session-harness skills (Phase 4) — 74 → 81 skills (+7 new)

- `/li:lessons-promote` — promote repo lesson → Lintel global
- `/li:adr-new` — bootstrap ADR from template
- `/li:personas-rotate` — load persona context for demos/workshops
- `/li:match` — semantic skill router (free text → top 3 skills)
- `/li:doctor` — cross-CLI health check (replaces v2 spec-only li-cli-fingerprint)
- `/li:scaffold` — invoke repo scaffolding into target
- `/li:lessons` — mid-session lessons.md relevance-filtered review

### Bin/ scripts (Phase 5)

- `bin/li-scaffold` — copy scaffolding/01-foundation/* into target repo with CLAUDE.md template rendering
- `bin/li-doctor` — cross-CLI health check (color-coded output, --verbose, --json)
- `bin/li-lessons-sync` — per-operator opt-in lessons sync across machines (private git repo)
- `bin/li-lessons-promote` — interactive promote of repo lesson → Lintel global
- `bin/li-adr-new` — bootstrap ADR with auto-numbering + commit
- `bin/li-update` — update plugin across detected CLIs

### Docs rewrite (Phase 6)

- README v3-sync with honest multi-CLI table
- `docs/session-harness.md` NEW — full mental model
- `docs/per-cli/PLUGIN-FORMAT-RESEARCH.md` NEW — per-CLI schema findings
- CODEOWNERS, CONTRIBUTING.md, SECURITY.md NEW (repo standards)
- CHANGELOG.md updated with v3.0.0-dev entry

### v2 components retained

- AGENT-INSTRUCTIONS.md (canonical session ritual) — unchanged
- 5+7+8 compliance arch (HARD-RULES + ON-DEMAND + REFERENCE)
- OurVoice corpus (60 paragraphs, 12 cells) — same content, moved to `scaffolding/03-ms-team/voice/`
- Voice tier mechanism (internal / trailblazer / mixed)
- v1_alias frontmatter (retained until v3.5 retire)
- install.sh / install.ps1 / verify.sh (unchanged in this phase — Phase 5b update pending)

### Counts final (post-Phase 5a)

- Skills: 81 (47 foundation + 27 ms-team + 7 new session-harness)
- Agents: 78 (across 9 categories)
- Hooks: 15
- Plugin manifests: 7 (Claude, Codex, Cursor, Gemini, OpenCode, Copilot CLI, Droid)
- Root entrypoint files: 3 (CLAUDE.md, AGENTS.md, GEMINI.md)
- Bin scripts: 6 (scaffold, doctor, lessons-sync, lessons-promote, adr-new, update)
- Scaffolding template tree: 01-foundation (CORE-PRINCIPLES, EVOLUTION, tasks/, docs/adr/, .claude/agents/) + 02-sdl (compliance refs) + 03-ms-team (voice corpus + doc-gen templates)

### Remaining for v3.0.0 tag (Phases 7-9)

- Phase 5b: install.sh + verify.sh extensions for plugin-manifest validation
- Phase 7: tests for plugin-manifests + scaffolding-copy + CI matrix updates
- Phase 8: voice corpus calibration (operator-driven) + marketplace submission
- Phase 9: ship gate v3 + tag v3.0.0

### Operator next steps

1. Push `v3-dev` branch to GitHub
2. Test plugin install in Claude Code via `/plugin marketplace add jokerman89/jokerman-lintel`
3. Test `bin/li-scaffold` in a new repo
4. Run T0 voice calibration
5. Submit to Anthropic + OpenAI + Cursor + Gemini marketplaces (post MS legal review)

---

## 2026-05-27 — v2.0 spec-complete (Big Bang)

**Lintel v2: scaffolding-only harness for MS-CAIP-SE engagements.** No runtime code; the scaffolding ITSELF is Lintel. Operator (or agent reading SKILL.md) executes the work. v1 → v2 is a Big Bang ship with 5 components, eng-review-cleared.

### Naming migration (Phase A)

- 24 skills renamed to mirror MS process: `/ship` → `/release-ev2`, `/compliance-gate` → `/onecs-check`, `/sensitive-use-report` → `/rais-sensitive-use`, `/li:test` → `/onebranch-validate`, etc. Full table in [MIGRATION-TABLE.md](docs/design/MIGRATION-TABLE-v2.md).
- 2 agents renamed: `MSComplianceAuditor` → `OneCSAuditor`; `EvalSuiteAuthor` → `CloudTestSuiteAuthor`.
- 5 voice docs renamed: `TRAILBLAZER-*.md` → `OurVoice-*.md` (matches canonical MS guide title).
- Directory rename: `scaffolding/02-compliance/` → `scaffolding/02-sdl/` (matches SDL framing).
- ~130 markdown files updated with v2 references via global sed.
- `v1_alias:` frontmatter field added to all renamed skills + agents. Aliases retained until v2.5.

### Portability shim (Phase B)

- New: [CLI-SUPPORT-V2-SCHEMA.md](docs/design/CLI-SUPPORT-V2-SCHEMA.md) — formal per-CLI degradation grammar (full / degraded / not-supported × claude-code / codex / copilot-cli / copilot-app).
- New skill: `/li:cli-fingerprint` — 5-step CLI detection cascade with operator-declarable fallback.
- v1 cli_support arrays still parse correctly (backward compat).

### 1M context budget engine (Phase C)

- New: [CONTEXT-ENGINE.md](docs/design/CONTEXT-ENGINE.md) — phase-declaration grammar, budget tracker semantics, watcher thresholds (80%/100%), decay policies, warmup-task pattern, outcome scoring, cost tracking. **Soft enforcement only in v2.0** per eng-review P1; hard enforcement deferred to v2.0.5.
- New skills: `/context-budget`, `/context-warmup`, `/perf-mode`.
- Rename: `/context-tokenwatch` → `/context-budgetwatch`.
- New agent: `ContextBudgetAdvisor` (Layer 4) — suggests phase declarations for unstructured tasks.

### T0 voice calibration (Phase D)

- New: [T0-CALIBRATION-WORKFLOW.md](docs/design/T0-CALIBRATION-WORKFLOW.md) — operator workflow for moving Trailblazer corpus from POPULATED → CALIBRATED. Pre-flight smoke-test recipe + per-cell iteration + cell-drop decision.
- Calibration is operator-driven (requires actual LLM-eval calls); Lintel documents the recipe.

### Brand integration (Phase E)

- New: [BRAND-INTEGRATION.md](docs/design/BRAND-INTEGRATION.md) — MS brand asset architecture, cache invalidation, staleness watcher.
- New skills: `/brand-update`, `/asset-search`.
- New hook: `brand-staleness-warn` (warn-only at >90 days).
- Default fallback templates (per eng-review P1 fix T3): `scaffolding/03-personal-advanced/doc-gen/default-templates/default-{ppt,word,web}-template.{json,html}`. Doc-gen runtime works regardless of operator brand-pull status.

### MS-proprietary doc-gen (Phase F)

- New skills: `/generate-ppt`, `/generate-word`, `/generate-word`, `/generate-web`. 4-gate quality pipeline per output: voice (`/rais-customer-voice-check`) + brand-conformance + honest-limitations + provenance (`/provenance-track`).
- New agents: `PPTNarrativeArchitect`, `WordTechnicalEditor`, `WebExperienceCritic`.
- Library choices locked (skill-level instructions): pptx-genjs (PPT), docx-templater (Word), native HTML/Next.js (Web).

### Ship gate v2 (Phase G)

- [SHIP-GATE.md](SHIP-GATE.md) extended to **12 gates** (10 v1 + Gate 11 doc-gen quality + Gate 12 context-engine readiness).
- `install/verify.sh` extended with 3 new subcommands: `--portability`, `--context-engine`, `--brand`.
- Backward-compat: `verify.sh --voice` and `--compliance` accept both v1 (TRAILBLAZER-*, 02-compliance/) and v2 (OurVoice-*, 02-sdl/) paths.

### Tests infrastructure (P1 fix T2)

- `tests/{unit,integration,e2e,fixtures,runner,conventions}/` structure created.
- `tests/conventions/bash-test-template.sh` — tagged template with assert helpers (assert_eq, assert_file_exists, assert_contains).
- `tests/runner/{run-all,run-unit,run-e2e}.sh` — discovery + tag-filter dispatch.
- `tests/unit/phase-a-naming-migration.sh` — first test, validates Phase A integrity (currently passes 1/1).
- `.github/workflows/ci.yml` extended with 3 new jobs: `unit-tests-linux`, `unit-tests-windows`, `e2e-claude-code-only`.

### Final counts

- **Skills:** 74 (47 Layer 1 + 27 Layer 3)
- **Agents:** 44 (18 Layer 3 promoted + 26 Layer 4 power-user)
- **Hooks:** 15 (12 warn + 2 BLOCK + 1 v2-new brand-staleness)
- **Compliance/voice docs:** 11
- **Top-level v2 design docs:** 5 (MIGRATION-TABLE, CLI-SUPPORT-V2-SCHEMA, CONTEXT-ENGINE, T0-CALIBRATION-WORKFLOW, BRAND-INTEGRATION)
- **Default doc-gen templates:** 3 (PPT JSON, Word JSON, Web HTML)
- **CI jobs:** 7 (4 v1 + 3 v2)
- **Verify.sh subcommands:** 13 (10 v1 + 3 v2)

### Verify status (post-Phase G)

- `bash tests/runner/run-all.sh` → 1/1 PASS
- `bash install/verify.sh --all` → exit 0, ALL CHECKS PASSED
- T0 calibration: NOT CALIBRATED (operator-driven; recipe in T0-CALIBRATION-WORKFLOW.md)
- Hook activation: 0/15 activated locally (expected; operator-driven symlink opt-in)

### Operator path to v2.0.0 tag

Per [SHIP-GATE.md](SHIP-GATE.md) — 12 gates. Remaining work after this spec-complete commit:
1. Run T0-CALIBRATION-WORKFLOW.md → CALIBRATED status (Gate 3)
2. Pull MS brand assets to `~/.lintel/brand/` (Gate 11 prerequisite)
3. CAIP-SE teammate adoption test (Gate 6)
4. Codex outside-voice review (Gate 5)
5. Upstream similarity check T-303 (Gate 7)
6. CI green on next push (Gate 9)
7. When all green: `git tag v2.0.0 && git push origin v2.0.0`

---

## 2026-05-26 — Initial release

- Repo created at `~/Workspace/jokerman-lintel/` on `main` branch.
- Scaffolding extracted from `claude-scaffolding` and adapted (refs updated to `jokerman-lintel`).
- Multi-CLI shim architecture: canonical `AGENT-INSTRUCTIONS.md` + per-CLI shims under `shims/` for Claude Code, GitHub Copilot Enterprise, and Codex CLI.
- Install scripts for bash (`install/install.sh`) and PowerShell 7+ (`install/install.ps1`).
- `install/upstream-sources.yaml` declares 8 upstream sources across 3 tiers (permissive / restricted / reference-only):
  - **Permissive (MIT):** gstack, GSD Redux, AgentShield, ECC.
  - **Restricted:** Trail of Bits skills (CC-BY-SA-4.0), Anthropic skills (mixed Apache-2.0 + source-available).
  - **Reference-only:** Trail of Bits claude-code-config, Anthropic plugins-official.
- New scaffolding files added on top of the `claude-scaffolding` base: `tasks/memory.md`, `tasks/personas.md`, `docs/adr/README.md`, `docs/adr/TEMPLATE.md`, `docs/personas/EXAMPLE.md`.
- Documentation: `README.md`, `getting-started.md`, `multi-cli.md`, `compliance.md`, `promoted-agents.md`, `precedence.md`, `power-user.md`, `faq.md`.
- MIT license (with `LICENSE` note explaining that installed upstreams keep their own licenses).
- `.gitignore` excludes session data, secrets, customer-data-likely paths, and common dev artifacts.
