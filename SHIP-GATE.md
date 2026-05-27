# Ship Gate — JStack v2.0.0 prerequisites

12 gates that must pass before tagging JStack v2.0.0. Updated for v2 Big Bang scope per /office-hours + /plan-eng-review. The original v1 gate list (10) is extended with 2 new gates for MS-proprietary doc-gen quality (Gate 11) and context-engine readiness (Gate 12).

---

## Gate 1 — Structural

All four layers populated with the intended scope:

| Layer | Item | v1 target | v2 target | Verify command |
|-------|------|-----------|-----------|----------------|
| 01-foundation | skills | 43 | 47 (43 + 4 new: jstack-cli-fingerprint, context-budget, context-warmup, perf-mode) | `verify.sh --counts` |
| 02-sdl | SDL docs | 7 | 7 (unchanged; renamed from 02-compliance/) | `verify.sh --compliance` |
| 02-sdl | hooks | 14 | 15 (14 + brand-staleness-warn) | `find hooks -name HOOK.md \| wc -l` |
| 03-personal-advanced | skills | 22 | 27 (22 + 5 new: brand-update, asset-search, generate-ppt, generate-word, generate-web) | `verify.sh --counts` |
| 03-personal-advanced | agents | 15 | 18 (15 + 3 new: PPTNarrativeArchitect, WordTechnicalEditor, WebExperienceCritic) | `find agents -name "*.md" \| wc -l` |
| 03-personal-advanced | voice docs | 7 | 7 (renamed TRAILBLAZER-* → OurVoice-*) | manual count |
| 03-personal-advanced | doc-gen default templates | 0 | 3 (default-ppt + default-word + default-web) | `ls scaffolding/03-personal-advanced/doc-gen/default-templates/` |
| 04-power-user | agents | 25 | 26 (25 + ContextBudgetAdvisor) | `find agents -name "*.md" \| wc -l` |

**Aggregate v2 target:** 74 skills + 44 agents + 15 hooks + 11 compliance/voice docs + 4 new top-level design docs (CONTEXT-ENGINE.md, BRAND-INTEGRATION.md, T0-CALIBRATION-WORKFLOW.md, MIGRATION-TABLE.md).

---

## Gate 2 — Frontmatter discipline

Every skill + every agent must have valid frontmatter:
- name (kebab-case `jstack-*` for skills, CamelCase for agents)
- description
- color
- tools
- voice (internal | trailblazer | mixed)
- cli_support (v1 array OR v2 object array per CLI-SUPPORT-V2-SCHEMA.md)
- For Layer 3 promoted agents: tier (permissive | restricted)
- For renamed skills/agents: v1_alias array

**Verify:** `verify.sh --frontmatter` exits 0.

---

## Gate 3 — T0 voice corpus calibrated

- `OurVoice-corpus.md` has ≥24 paragraphs (≥2 known-good + ≥2 known-bad per cell × 12 cells) — DONE in v1
- `OurVoice-calibration.md` shows status: CALIBRATED — operator-driven via T0-CALIBRATION-WORKFLOW.md
- ≥10 of 12 cells pass at ≥90% known-good AND ≥90% known-bad accuracy

**Verify:** `verify.sh --voice` confirms CALIBRATED. **Status pre-tag:** operator must execute T0-CALIBRATION-WORKFLOW.md.

---

## Gate 4 — Cross-CLI test matrix

`/onebranch-validate --all` produces a matrix with:
- 0 FAIL entries (DEGRADED entries acceptable if documented in cli_support v2 schema)
- All skills declared `cli: claude-code, level: full` PASS on claude-code
- Skills declared `cli: codex` PASS or DEGRADED on codex (per declaration)
- Matrix written to `~/.jstack/test-matrix-<release-ts>.md` for record

---

## Gate 5 — Codex outside-voice review

After all internal review (`/plan-eng-review`, `/review`), one independent Codex review pass on:
- Repo structure as a whole
- 5 representative skills (CodeReviewer agent picks)
- All compliance hooks (highest-risk surface)
- OurVoice-test rubric
- v2-new components: CONTEXT-ENGINE.md, BRAND-INTEGRATION.md, doc-gen 4-gate

Codex P1 findings BLOCK ship. Codex P2 findings: address or document why deferred.

---

## Gate 6 — Teammate adoption verification

Before tagging v2.0.0:
- One CAIP-SE teammate runs through install flow on their machine
- They invoke ≥10 skills successfully (including ≥1 v2-renamed via alias to confirm aliases work)
- They confirm at least 1 customer-engagement flow:
  - `/scaffold-engagement-demo` → `/demo-deliverable-gen` → `/rais-customer-voice-check` → `/provenance-track`
  - OR: `/generate-ppt` → 4-gate pass → distribute
- They report friction points + operator addresses Critical blockers

Human gate, not automated.

---

## Gate 7 — Diff-vs-upstream similarity check

Per T-303 in plan-eng-review: prove "inspired by, not plagiarized" with measurement.

**Methodology placeholder (T-303 finalization required before v2.0.0):**
See `UPSTREAM-SIMILARITY.md` for full method. Threshold: <0.6 cosine for "inspired but structurally distinct". v2.0 specifically: re-run on v2-new components to confirm divergence from gstack/speckit/superpowers.

---

## Gate 8 — Honest mirror review

Before tagging v2.0.0:
- Confirm `HONEST-MIRROR-v2.md` is written (operator review of scope drift since /office-hours approval)
- Review any scope drift since v1 → v2 transition
- Confirm any drift is documented + accepted, OR refactor

---

## Gate 9 — CI matrix green

`.github/workflows/ci.yml` runs on every PR + push to main. For v2.0.0 tag:
- Latest commit on main must have CI green across all jobs:
  - verify-linux, install-linux, verify-windows (from v1)
  - unit-tests-linux, unit-tests-windows, e2e-claude-code-only (new in v2 Phase A)
- e2e-cross-cli is acceptable as `if: false` (Codex CLI not in CI yet)
- No pending or warning-level CI signals

---

## Gate 10 — License posture

- LICENSE file: MIT (operator-confirmed)
- All Layer 3 promoted agents tier-stamped permissive (verified via `verify.sh --tier-stamps`)
- All Layer 4 agents stamped or default-permissive
- `install/upstream-sources.yaml` declares each upstream's license tier
- README clearly states: "JStack contains operator-authored content (MIT) + installs (does NOT bundle) upstream content per its declared licenses"
- `LICENSE-NOTES.md` includes gstack-IP-reuse confirmation (per office-hours assignment)

---

## Gate 11 (NEW for v2) — MS-proprietary doc-gen quality

For v2 doc-gen skills (/generate-ppt, /generate-word, /generate-web):
- 4-gate pipeline operational: voice + brand-conformance + honest-limitations + provenance
- Test fixture: one .pptx generated by /generate-ppt passes all 4 gates against a sample brief
- Same for /generate-word and /generate-web
- `BRAND-INTEGRATION.md` documents acquisition + maintenance
- Default fallback templates ship in repo (`scaffolding/03-personal-advanced/doc-gen/default-templates/`)
- `brand-staleness-warn` hook fires correctly when brand >90 days old

---

## Gate 12 (NEW for v2) — Context engine readiness

For v2 context-budget engine:
- `CONTEXT-ENGINE.md` documents phase declarations + watchers + decay
- 4 new skills documented (context-budget, context-warmup, perf-mode, context-budgetwatch)
- `ContextBudgetAdvisor` agent documented
- Test fixture: a multi-phase task declares phases + budget tracker increments correctly (soft enforcement only in v2.0)
- Config example present in `install/layer-config.yaml.example`
- Audit trail format documented

---

## How to run the gate sequence (operator)

```bash
# Gate 1 + 2 + 10
bash install/verify.sh --all

# Gate 3 (operator-driven)
# See T0-CALIBRATION-WORKFLOW.md
# /jstack-eval --corpus ... → iterate rubric → status: CALIBRATED

# Gate 4 (in Claude Code session)
# /onebranch-validate

# Gate 5 (outside-voice)
# /codex review

# Gate 6 (operator-driven; handoff to CAIP-SE teammate)

# Gate 7 (run T-303 methodology — script TBD; operator runs methodology against v2 components)

# Gate 8 (manual)
# Write HONEST-MIRROR-v2.md if not yet done; review scope drift

# Gate 9 (check GitHub Actions dashboard)

# Gates 11 + 12 (operator + Codex review)
# Run /generate-ppt/word/web against a sample brief, confirm all 4 gates pass
# Run /perf-mode + /context-budget against a sample multi-phase task

# Tag if all 12 green:
git tag v2.0.0
git push origin v2.0.0
```

---

## What happens after v2.0.0

- README links to this SHIP-GATE document
- Tag triggers release notes generation (via `/landing-report`)
- Operator runs `/rais-customer-voice-check` on release notes before publishing
- Quarterly re-run of Gates 3, 4, 7 to detect drift
- v2.0.5 patch lands when:
  - Hard enforcement for context engine becomes worthwhile (usage data shows operators ignoring soft warnings)
  - First batch of alias-usage data informs v2.5 retirement decisions
  - Any P2 findings from Gate 5 (Codex review) that were deferred

---

## See also

- `MIGRATION-TABLE.md` — Phase A rename source-of-truth
- `CLI-SUPPORT-V2-SCHEMA.md` — Phase B portability schema
- `CONTEXT-ENGINE.md` — Phase C engine architecture
- `T0-CALIBRATION-WORKFLOW.md` — Phase D operator workflow
- `BRAND-INTEGRATION.md` — Phase E brand architecture
- `/jstack-test` (renamed `/onebranch-validate`) — Gate 4 automation
- `/jstack-eval` — Gate 3 automation
- `/codex` — supports Gate 5
- `install/verify.sh --all` — automates Gates 1, 2, 10
- `UPSTREAM-SIMILARITY.md` — Gate 7 methodology
- `LAYERS.md` — 4-layer architecture
