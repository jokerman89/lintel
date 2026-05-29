# Cohort 6 findings — engineering domain coverage depth

**Cohort:** 6 — engineering domain coverage (TA / DA / SC / DH / TQ)
**Auditor directive:** operator-flagged depth inconsistency. NO-CUT — uplift thin domains to the strongest peer's depth, never trim the strong one.
**Scale verified:** 144 skills, 83 agents. Engineering-domain agents: 25 engineering + 8 security + 6 compliance + 7 devops = 46 in scope.
**Critical framing:** the five engineering-domain **modules** (TA/DA/SC/DH/TQ) are **DESIGNED but NOT BUILT**. They are specified in `docs/design/lintel-v4.0-reframe-design.md` Ch.3 (§3.3–§3.7) and slated for v4.1+ (one module per minor release, Ch.5 Phase 4). This cohort audits **what exists today** that covers each domain, and measures cross-domain depth inconsistency against the v4.0 module shape as the target bar.

---

## 1. Per-domain inventory (what exists TODAY)

### TA — technical architecture

| Artifact kind | Exists today | Path |
|---|---|---|
| Dedicated skills | **0** | — (designed: `ta-api-design`, `ta-dependency-graph`, `ta-complexity-audit`, `ta-boundary-review`, `ta-scaling-plan`, `ta-contract-collision`, `ta-quality-attributes` — Ch.3 §3.3, none built) |
| Agents | 4–5 | `agents/engineering/Architect.md`, `BackendArchitect.md`, `APIDesigner.md`, `ADRDrafter.md` (+ adjacent: `ContextBudgetAdvisor`). Designed-new: `SystemArchitect`, `CapacityPlanner` (not built) |
| Hooks | 0 | designed: `arch-drift-warn`, `contract-collision-warn`, `complexity-budget-warn` (Ch.3 §3.3, not built) |
| Orchestrator / module entry | **none** | designed `/li:ta full\|loop\|single` (not built) |
| Adjacent skill | `adr-new` | ADR authoring touches TA but is generic doc-gen, not architecture-grade |

Depth note: TA has solid **agents** (Architect's body has problem/constraints/three-alternatives/recommendation/interface/sequence-diagram structure — see `Architect.md:42-92`), but **no skill layer, no hooks, no audit log, no module orchestration**. Architecture decisions are agent-spawned ad hoc, never gated or checkpointed.

### DA — data architecture (operator + review flagged THINNEST)

| Artifact kind | Exists today | Path |
|---|---|---|
| Dedicated skills | **0** | — (designed: `da-schema-design`, `da-migration-plan`, `da-index-audit`, `da-query-perf`, `da-data-flow`, `da-retention-policy`, `da-pii-scan` — Ch.3 §3.4, none built) |
| Agents | **2** | `agents/engineering/DatabaseDesigner.md`, `DataPipelineDesigner.md`. Designed-new: `SchemaMigrator` (not built) |
| Hooks | **0** | designed: `schema-breaking-change-warn`, `pii-in-schema-warn`, `retention-policy-required-warn` (Ch.3 §3.4, not built) |
| Orchestrator / module entry | **none** | designed `/li:da full\|loop\|single` (not built) |
| Audit log | **none** | DatabaseDesigner/DataPipelineDesigner write no `~/.lintel/audit/*.jsonl` |

Depth note: **DA is the floor of the cohort.** 2 agents, 0 skills, 0 hooks, 0 audit log, 0 orchestration. The two agents are competently bodied (DatabaseDesigner has schema/migration-safety/RLS/query-strategy sections — `DatabaseDesigner.md:30-94`) but they are the *entire* domain surface. Compare to SC's 14 agents + 14 skills + 7 hooks. DA's only compliance touchpoint is a one-line cross-reference to `/dpia-submit-draft` (`DataPipelineDesigner.md:68`) — DA *consumes* the SC stack but contributes no enforcement of its own.

### SC — security-compliance (review flagged STRONGEST/deepest)

| Artifact kind | Exists today | Path |
|---|---|---|
| Dedicated skills | **14** | `caip-audit`, `cloudtest-eval-suite`, `compliance-gate`, `dpia-submit-draft`, `dsb-submit-draft`, `entra-agent-id-submit-draft`, `first-party-check`, `onebranch-validate`, `onecs-check`, `onerai-submit-draft`, `rais-customer-voice-check`, `rais-impact-assessment`, `rais-sensitive-use`, `rais-transparency-note` |
| Agents | **14** | 8 security (`SecurityAuditor`, `DependencyAuditor`, `JWTSecurityReviewer`, `OAuthFlowReviewer`, `PrivacyBoundaryAudit`, `SBOMAuditor`, `SecretsScanReviewer`, `ThreatModelDrafter`) + 6 compliance (`AGTReviewer`, `EUAIActReviewer`, `GDPRReviewer`, `RAIReviewer`, `SDLReviewer`, `SOC2Reviewer`) |
| Hooks | **7+** block-hooks | `customer-data-block`, `no-customer-data-in-message`, `no-customer-data-in-screenshot`, `no-secrets-in-edit`, `secret-scan-block`, `no-production-mutation-without-auth`, `non-first-party-warn` (+ `entropy-secret-check.sh`) |
| Orchestrator / module entry | partial | `onecs-check` is the closest to a module entry (runs 7 items, aggregates verdict). Designed `sc-orchestrator` + `SCOrchestrator` agent formalize this (Ch.3 §3.5, not built) |
| Audit log | **yes, pervasive** | `~/.lintel/audit/security-audits.jsonl`, `compliance-gate-*.jsonl`, `onecs-check.jsonl` etc. — every gate event append-only |

Depth note: **SC is the bar.** It has all four layers (skill / agent / hook / audit), AskUserQuestion gates (`onecs-check.md:52`), per-item PASS/NEEDS_ACTION/NOT_APPLICABLE verdicts, downstream-blocking semantics (`onecs-check.md:100` — "A NEEDS_ACTION item BLOCKS downstream /release-ev2"), cross-artifact consistency checks (`RAIReviewer.md:49`), and an explicit "refuse to record the gate event without audit trail" failure mode (`onecs-check.md:111`).

### DH — devops-hosting

| Artifact kind | Exists today | Path |
|---|---|---|
| Dedicated skills | **4** | `release-ev2`, `release-deploy-ev2`, `safe-deploy-ring`, `setup-ev2-targets` |
| Agents | **7** | `DevOpsToolchain`, `EV2PipelineAuditor`, `GHActionsReviewer`, `K8sManifestReviewer`, `OneBranchReviewer`, `PerformanceAnalyzer`, `TerraformReviewer`. Designed-new: `SREOrchestrator` (not built) |
| Hooks | 2 (shared) | `no-direct-main-push`, `no-merge-without-review` (release-adjacent); `brand-staleness-warn` tangential |
| Orchestrator / module entry | partial | `release-ev2`/`release-deploy-ev2` chain is a de-facto deploy pipeline. Designed `/li:dh full\|loop\|single` formalizes (Ch.3 §3.6, not built) |
| Audit log | partial | release skills sanity-scan + reference Layer-2 traceability; no dedicated `dh-*.jsonl` |

Depth note: DH is mid-pack. Strong **deploy** coverage (release/canary skills have full failure-modes + examples + downstream-gate semantics — `release-ev2.md:72-102`) but **thin on the rest of the domain** designed in §3.6: no ci-design, infra-as-code, observability-setup, runbook, cost-audit, rollback-plan skills. Agents cover review (Terraform/K8s/GHActions/OneBranch reviewers) but there is no orchestrator and no SLO/cost/observability enforcement.

### TQ — testing-qa

| Artifact kind | Exists today | Path |
|---|---|---|
| Dedicated skills | **3** | `qa`, `qa-only`, `eval` (+ `cloudtest-eval-suite` shared with SC) |
| Agents | 2–3 | `agents/engineering/TestRunner.md`, `RegressionDetective.md`, `SanityChecker.md`. Designed-new: `QAOrchestrator`, `FlakinessHunter` (not built) |
| Test harness infra | **yes** | `tests/runner/{run-all,run-unit,run-e2e}.sh`, `tests/unit/*` (presence tests), `tests/shape/*` (frontmatter/nav/forge shape tests), `tests/behavior/build-pilot.sh` (only behavior test — gap 6.9), `tests/integration/*` |
| Hooks | 0 | designed: `coverage-drop-warn`, `flaky-test-quarantine-warn`, `behavior-test-missing-warn` (Ch.3 §3.7, not built) |
| Orchestrator / module entry | partial | `qa` is a competent runner-loop (detect/baseline/classify/auto-fix/re-run — `qa.md:34-46`) but only operates on the *target repo's* test suite. No coverage/mutation/contract/load skills. |
| Audit log | partial | `qa` writes `~/.lintel/audit/qa-fixes.jsonl` (`qa.md:75`) |

Depth note: TQ has a strong *self-test* shape layer (`tests/shape/`) and a solid `qa` runner skill, but the **strategic TQ skills** designed in §3.7 (coverage-audit, regression-design, mutation, e2e-design, contract-test, load-test, flakiness-hunt) don't exist. The repo dogfoods presence-tests but has only one behavior test (gap 6.9 is acknowledged in §3.7 itself).

---

## 2. Domain × D1–D14 depth matrix

Scoring each **domain's coverage depth today** per dimension. Legend: **deep** = skill+agent+hook+audit-log+gate present and orchestrated · **mid** = some layers present, not orchestrated · **thin** = agents-only or single-skill, no enforcement · **absent** = nothing exists.

| Dimension | TA | DA | SC | DH | TQ |
|---|---|---|---|---|---|
| **D1 — Head / entry** (declared invocation + input validation) | thin (agent-spawn only, no `/li:` entry) | thin (agent-spawn only) | **deep** (`/onecs-check --scope/--artifact`, validated) | mid (`/release-ev2` flags validated) | mid (`/qa --scope/--no-fix`) |
| **D2 — Tail / exit** (explicit verdict + output validation) | thin (agent report, no verdict protocol) | thin | **deep** (PASS/NEEDS_ACTION verdict, blocks downstream) | mid (Ship Status report) | mid (CLEAN/STUCK state) |
| **D3 — Objects (in/out contract)** | mid (agent report format defined) | mid (DatabaseDesigner report format) | **deep** (per-artifact contracts, cross-artifact consistency) | mid (PR body contract) | mid (failure-bucket contract) |
| **D4 — Entry-points** (which workflows reach it) | thin (no skill ⇒ no `/li:` entry-point) | **thin/absent** (no skill, only Task-tool spawn) | **deep** (session-start auto + on-demand + pre-ship gate) | mid (ship/deploy chain) | mid (post-build, pre-ship) |
| **D5 — Checkpoints** | absent (designed §3.3, not built) | **absent** (designed §3.4, not built) | mid (per-item status; full checkpoint set designed §3.5) | mid (ramp gates in `safe-deploy-ring`) | mid (per-iteration in `qa`) |
| **D6 — Recovery points** | thin (agent "what to do when blocked") | thin (agent edge-cases only) | **deep** (CRITICAL raises immediately, accept-with-attestation path) | mid (`safe-deploy-ring` abort-safe) | mid (`qa` revert-fix, max-iterations STUCK) |
| **D7 — Pack / WorkProfile influence** | absent | absent | mid (ms-team layer gates fire by profile; full `engineering.security_compliance.*` prefs designed §3.5) | thin (EV2 vs GHActions not profile-driven yet) | thin (no profile-driven coverage targets yet) |
| **D8 — Frontmatter completeness** | mid (agents have name/category/color/voice/cli_support; no necessity) | mid (same) | **deep** (skills add layer/v1_alias; agents add `tier: permissive`) | mid | mid |
| **D9 — Brief Forge integration** | absent | absent | absent-but-designed (§3.5 evaluators `[security-eval]`) | absent | absent (designed §3.7) |
| **D10 — Knowledge / lessons integration** | thin (Architect reads CLAUDE.md/ADRs — `Architect.md:32`) | thin (agents read existing schema/migrations) | mid (reads ON-DEMAND-RULES, RAI canonical docs) | thin | thin |
| **D11 — Subagent / context delegation** | **deep** (agents ARE the delegation target; curated-brief shape) | mid (2 agents spawnable) | **deep** (14 agents, curated) | mid (7 review agents) | mid (TestRunner/RegressionDetective) |
| **D12 — Failure mode** | thin (agent edge-cases) | thin (agent edge-cases) | **deep** (explicit per-skill `## Failure modes`, refuse-without-audit) | **deep** (`release-ev2` 5 failure modes) | **deep** (`qa` 4 failure modes) |
| **D13 — Observability** (audit/usage log) | **absent** (no jsonl) | **absent** (no jsonl) | **deep** (pervasive append-only jsonl) | mid (Layer-2 ref, no dedicated log) | mid (`qa-fixes.jsonl`) |
| **D14 — Necessity declaration** (REQUIRED/RECOMMENDED + gap-if-skipped) | absent | absent | mid (downstream-block = implicit REQUIRED; not a declared field) | thin | thin |

### Relative depth ranking (deepest → thinnest)

1. **SC** — bar-setter. 12/14 dimensions deep-or-mid, deep on D1/D2/D4/D6/D11/D12/D13.
2. **DH** — strong on deploy slice (D12 deep), mid elsewhere, thin on the non-deploy half of §3.6.
3. **TQ** — strong runner + self-test infra (D12 deep), mid on strategy skills, absent on §3.7 enforcement hooks.
4. **TA** — good agents (D11 deep) but no skill/hook/audit layer; absent on D5/D7/D9/D13/D14.
5. **DA** — **thinnest.** 2 agents, 0 skills, 0 hooks, 0 audit. absent on D4(near)/D5/D7/D9/D13/D14, thin on the rest. Only domain where the *entire surface* is two agent files.

---

## 3. The DA → SC uplift spec (raise DA to SC's bar — NO-CUT)

The concrete SC-vs-DA gap, by layer, with the uplift that closes it. This is **additive only**; nothing in SC is trimmed.

| Layer | SC has (bar) | DA has today | Uplift to reach bar |
|---|---|---|---|
| **Skill family** | 14 skills (`onecs-check.md`, `rais-impact-assessment.md`, …) | **0** | Build the 7 designed `da-*` sub-skills (Ch.3 §3.4): `da-schema-design`, `da-migration-plan`, `da-index-audit`, `da-query-perf`, `da-data-flow`, `da-retention-policy`, `da-pii-scan`. Each authored to SC skill-template depth: Inputs / Workflow / Report format / Compliance integration / **Failure modes** / Examples / See also. |
| **Module entry** | `onecs-check` aggregates a multi-item verdict | none | Build `da` module-root skill (`/li:da full\|loop\|single`) per the §3.2 module pattern, mirroring how `onecs-check` orchestrates items. |
| **Verdict protocol (D2)** | PASS / NEEDS_ACTION / NOT_APPLICABLE, blocks `/release-ev2` (`onecs-check.md:100`) | agent prose only | Give `da` a checkpoint-verdict (Ch.3 §3.4 lists 5: access-patterns documented, schema normalized-or-justified, migration shadow-tested, retention declared, PII tagged). Wire NEEDS_ACTION to block `/release-ev2` for schema-bearing changes — same semantics SC already enforces. |
| **Hooks (D13/enforcement)** | 7 block-hooks (`secret-scan-block`, `customer-data-block`, …) | **0** | Build the 3 designed DA hooks (§3.4): `schema-breaking-change-warn` (column drop/rename without shim), `pii-in-schema-warn` (pattern-match PII field names — composes with SC's existing `secret-scan-block` shape), `retention-policy-required-warn` (new entity without TTL). |
| **Audit log (D13)** | `~/.lintel/audit/*.jsonl` append-only, refuse-without-audit (`onecs-check.md:111`) | **none** | DA module + sub-skills write `~/.lintel/audit/da-*.jsonl` per gate event, with the same "refuse to record the gate event without audit trail" failure mode SC declares. |
| **AskUserQuestion gate (D1/D6)** | operator confirms each NEEDS_ACTION individually (`onecs-check.md:52,110`) | none | DA checkpoint 1 ("operator confirms top 5 query patterns" — §3.4) becomes an AskUserQuestion gate, mirroring `onecs-check`'s per-item confirm-don't-bulk-confirm rule. |
| **Cross-domain compose (D10)** | RAIReviewer cross-checks artifacts (`RAIReviewer.md:49`) | one-line `/dpia-submit-draft` ref | `da-pii-scan` formally composes into the SC module (§3.4 says it "composes with security-compliance module"). Define the contract so DA's PII findings feed SC's `PrivacyBoundaryAudit` rather than living as a comment. |
| **Necessity declaration (D14)** | implicit REQUIRED via downstream-block | none | DA module declares `necessity: STRONGLY RECOMMENDED when work touches schema/migrations/storage` + `gap_if_skipped:` (unreviewed migration risk, undeclared retention/PII). |
| **Frontmatter (D8)** | skills declare layer/v1_alias; agents `tier:` | agents have base set, no necessity | Add to `DatabaseDesigner`/`DataPipelineDesigner` + new `SchemaMigrator`: any module-handoff frontmatter the v4.0 module pattern standardizes (brief_forge_handoffs, expected_inputs/outputs). |

**The single biggest DA gap:** DA has **no enforcement layer at all** — no skill, no hook, no audit log, no verdict that can block a ship. SC blocks `/release-ev2` on an open compliance item; DA cannot block a destructive migration or an untagged-PII schema from landing. A schema change today reaches `main` through the generic ship path with zero DA-specific gate. That is the load-bearing difference, and it is exactly what the 3 designed DA hooks + the module verdict close.

### TA / DH / TQ — same uplift, smaller deltas

- **TA → SC:** TA has deep agents but is missing the *entire* skill+hook+audit triad (parallel to DA's gap, but TA's agents are stronger). Build the 7 `ta-*` skills + 3 arch hooks + `ta` module entry + audit log. Biggest TA gap: **D5 checkpoints absent** — architecture decisions have no checkpoint/recovery loop today; an ADR can be contradicted by a later edit with no `arch-drift-warn`.
- **DH → SC:** DH's deploy slice already matches SC depth (D12 deep, gate semantics present). Gap is **breadth**: build the non-deploy §3.6 skills (ci-design, infra-as-code, observability-setup, runbook, cost-audit, rollback-plan) + `SREOrchestrator` + the 3 infra hooks (`infra-drift-warn`, `slo-uncovered-warn`, `cost-spike-warn`). Biggest DH gap: **D13 dedicated observability log + SLO enforcement absent**.
- **TQ → SC:** TQ's runner (`qa`) and self-test shape layer are strong; gap is the **strategy skills** (coverage/mutation/contract/load/flakiness — §3.7) + the 3 TQ hooks, the most load-bearing being `behavior-test-missing-warn` which would close gap 6.9 systemically (currently only one behavior test exists). Biggest TQ gap: **D9 Brief Forge + coverage-enforcement hooks absent**.

---

## 4. Designed-not-built module note

All five domains' *target* depth is specified in `docs/design/lintel-v4.0-reframe-design.md` Ch.3 (§3.2 module pattern, §3.3–§3.7 per-domain specs). None of the five modules is built yet:

- The module pattern (§3.2) requires `workflow_root: true`, navigation block, brief_forge block, and a new `domain:` frontmatter concept with `granularities: [full, loop, single]`, `checkpoints`, `recovery`, `continuation`, `raise_help`. **No skill in the repo declares this `domain:` block today** — it is a v4.0 net-new concept.
- Ch.5 Phase 4 sequences the modules to ship **one per minor release** (v4.1–v4.5), operator-ordered by engagement need, each as a standard internal-tool PR with a "what's net-new vs reused" inventory (design line ~636, ~844).
- Therefore this cohort's uplift recommendations are **not new design** — they are the prioritization signal for *which module to build first*. The audit's data says: **build DA first** (thinnest, highest enforcement-gap, operator-flagged), with SC's already-built stack as the copy-from template (SC is explicitly an "uplift of existing infrastructure into a cohesive module" per §3.5 — the orchestration pattern is the reusable part).

This audit removes nothing. It surfaces that DA and TA need the skill+hook+audit triad that SC already proves works, and that DH and TQ need breadth across their designed sub-skill families.

---

## 5. Top findings (operator_decision_required)

| ID | Finding | Domains | operator_decision_required | priority |
|---|---|---|---|---|
| C6-F1 | DA has zero enforcement layer (0 skills, 0 hooks, 0 audit log) — a destructive migration or untagged-PII schema can reach `main` with no DA gate, whereas SC blocks ship on any open item. | DA vs SC | **yes** (which module ships first in Phase 4) | high |
| C6-F2 | TA has strong agents but no skill/hook/audit triad and **no checkpoint/recovery loop** (D5 absent) — ADRs can be silently contradicted; no `arch-drift-warn`. | TA vs SC | **yes** (build TA module + arch hooks?) | high |
| C6-F3 | D13 observability is binary across the cohort: SC writes pervasive audit jsonl, TA+DA write **none**. Uniformity break on the observability promise. | TA, DA | yes | high |
| C6-F4 | D9 Brief Forge fires in **no** engineering domain (designed in every §3.x but built nowhere) — uniform absence, but a designed-promise gap. | all 5 | no (tracked as designed-not-built) | medium |
| C6-F5 | D14 necessity + gap-if-skipped is a declared field nowhere in the cohort; SC enforces necessity only *implicitly* via downstream-block. | all 5 | no | medium |
| C6-F6 | DH and TQ are deep on their core slice (deploy / runner) but thin across the rest of their §3.6/§3.7 sub-skill families — breadth gap, not depth gap. | DH, TQ | yes (sub-skill enumeration scope per §C3-D2) | medium |

**operator_decision_required count: 4** (C6-F1, C6-F2, C6-F3, C6-F6).

---

## Cohort summary

- **Bar:** SC. **Floor:** DA. The cohort's depth spread is wide and asymmetric: SC has all four layers (skill/agent/hook/audit) + verdict + gate; DA has only the agent layer.
- The depth inconsistency the operator flagged is **real and structural**, not cosmetic: it is the absence of the skill+hook+audit+verdict triad in DA and TA, against its full presence in SC.
- The fix is the v4.0 Ch.3 module program, with **DA prioritized first** and **SC as the copy-from template**. Nothing is trimmed.
- Designed-not-built status confirmed for all 5 modules; this cohort produces the *build-order* signal Phase 4 needs.
