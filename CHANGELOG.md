# Changelog

All notable changes to this repo are tracked here. Format is loose — date headings + bulleted changes. Major behavior changes to the canonical instructions are also logged in `scaffolding/EVOLUTION-LOG.md` (which travels with each scaffolded repo).

## 2026-05-27 — v2.0 spec-complete (Big Bang)

**JStack v2: scaffolding-only harness for MS-CAIP-SE engagements.** No runtime code; the scaffolding ITSELF is JStack. Operator (or agent reading SKILL.md) executes the work. v1 → v2 is a Big Bang ship with 5 components, eng-review-cleared.

### Naming migration (Phase A)

- 24 skills renamed to mirror MS process: `/ship` → `/release-ev2`, `/compliance-gate` → `/onecs-check`, `/sensitive-use-report` → `/rais-sensitive-use`, `/jstack-test` → `/onebranch-validate`, etc. Full table in [MIGRATION-TABLE.md](MIGRATION-TABLE.md).
- 2 agents renamed: `MSComplianceAuditor` → `OneCSAuditor`; `EvalSuiteAuthor` → `CloudTestSuiteAuthor`.
- 5 voice docs renamed: `TRAILBLAZER-*.md` → `OurVoice-*.md` (matches canonical MS guide title).
- Directory rename: `scaffolding/02-compliance/` → `scaffolding/02-sdl/` (matches SDL framing).
- ~130 markdown files updated with v2 references via global sed.
- `v1_alias:` frontmatter field added to all renamed skills + agents. Aliases retained until v2.5.

### Portability shim (Phase B)

- New: [CLI-SUPPORT-V2-SCHEMA.md](scaffolding/01-foundation/CLI-SUPPORT-V2-SCHEMA.md) — formal per-CLI degradation grammar (full / degraded / not-supported × claude-code / codex / copilot-cli / copilot-app).
- New skill: `/jstack-cli-fingerprint` — 5-step CLI detection cascade with operator-declarable fallback.
- v1 cli_support arrays still parse correctly (backward compat).

### 1M context budget engine (Phase C)

- New: [CONTEXT-ENGINE.md](CONTEXT-ENGINE.md) — phase-declaration grammar, budget tracker semantics, watcher thresholds (80%/100%), decay policies, warmup-task pattern, outcome scoring, cost tracking. **Soft enforcement only in v2.0** per eng-review P1; hard enforcement deferred to v2.0.5.
- New skills: `/context-budget`, `/context-warmup`, `/perf-mode`.
- Rename: `/context-tokenwatch` → `/context-budgetwatch`.
- New agent: `ContextBudgetAdvisor` (Layer 4) — suggests phase declarations for unstructured tasks.

### T0 voice calibration (Phase D)

- New: [T0-CALIBRATION-WORKFLOW.md](T0-CALIBRATION-WORKFLOW.md) — operator workflow for moving Trailblazer corpus from POPULATED → CALIBRATED. Pre-flight smoke-test recipe + per-cell iteration + cell-drop decision.
- Calibration is operator-driven (requires actual LLM-eval calls); JStack documents the recipe.

### Brand integration (Phase E)

- New: [BRAND-INTEGRATION.md](BRAND-INTEGRATION.md) — MS brand asset architecture, cache invalidation, staleness watcher.
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
2. Pull MS brand assets to `~/.jstack/brand/` (Gate 11 prerequisite)
3. CAIP-SE teammate adoption test (Gate 6)
4. Codex outside-voice review (Gate 5)
5. Upstream similarity check T-303 (Gate 7)
6. CI green on next push (Gate 9)
7. When all green: `git tag v2.0.0 && git push origin v2.0.0`

---

## 2026-05-26 — Initial release

- Repo created at `~/Workspace/jokerman-session-setup/` on `main` branch.
- Scaffolding extracted from `claude-scaffolding` and adapted (refs updated to `jokerman-session-setup`).
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
