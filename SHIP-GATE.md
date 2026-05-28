# Ship Gate — Lintel v3.0.0 prerequisites

10 gates that must pass before tagging v3.0.0. Replaces v2's 12-gate list (consolidated by combining related gates + removing spec-only checks that have real implementations now).

Updated for v3 plugin-manifest architecture (no more MCP/compile checks since those were dropped). Voice calibration + marketplace submission remain operator-driven.

---

## Gate 1 — Structural (v3 layout)

All v3 directories populated as intended:

| Path | v3 target | Verify command |
|---|---|---|
| `skills/` | 81 skills (74 v2 + 7 new) | `bash install/verify.sh --counts` |
| `agents/` | 78 agents across 9 categories | `bash install/verify.sh --agents-categorized` |
| `hooks/shared/` | 15 hooks | `find hooks/shared -name HOOK.md \| wc -l` |
| `scaffolding/01-foundation/` | base templates intact | `bash install/verify.sh --scaffolding-coherence` |
| `scaffolding/02-sdl/` | 7 compliance docs intact | `bash install/verify.sh --compliance` |
| `scaffolding/03-ms-team/voice/` | OurVoice corpus + tests + calibration | `bash install/verify.sh --voice` |
| `scaffolding/03-ms-team/doc-gen/default-templates/` | 3 default templates | `ls scaffolding/03-ms-team/doc-gen/default-templates/` |
| `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/`, `.copilot-plugin/`, `.droid-plugin/`, `gemini-extension.json` | 7 plugin manifests valid JSON | `bash install/verify.sh --plugin-manifests` |
| `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` at root | 3 entrypoint files | included in `--plugin-manifests` |
| `bin/` | 6 operator-side utilities | `ls bin/` |

**Aggregate v3 target:** 81 skills + 78 agents + 15 hooks + 7 plugin manifests + 3 entrypoint files + 6 bin scripts + intact scaffolding templates.

---

## Gate 2 — Frontmatter discipline

Every skill + every agent must have valid frontmatter:
- `name` (kebab-case `li-*` for skills, CamelCase for agents)
- `description`
- `color`
- `tools`
- `voice` (internal | trailblazer | mixed)
- `cli_support` (v2 array — retained for compat; v3 plugin manifests handle CLI discovery)
- `category` (NEW v3 — for agents only; matches directory)
- `layer` (NEW v3 — for skills only; foundation | ms-team)
- `tier` (REQUIRED for ms-specific / security / compliance agents — permissive default for engineering)

**Verify:** `bash install/verify.sh --frontmatter && bash install/verify.sh --agents-categorized` both exit 0.

---

## Gate 3 — T0 voice corpus calibrated

- `OurVoice-corpus.md` has ≥24 paragraphs (≥2 known-good + ≥2 known-bad per cell × 12 cells) — DONE in v1
- `OurVoice-calibration.md` shows status: CALIBRATED — operator-driven via `docs/design/T0-CALIBRATION-WORKFLOW.md`
- ≥10 of 12 cells pass at ≥90% known-good AND ≥90% known-bad accuracy

**Verify:** `bash install/verify.sh --voice` confirms CALIBRATED.

**Status pre-tag:** operator must execute T0-CALIBRATION-WORKFLOW.md (3-5 rounds, $1.80-6 per round).

---

## Gate 4 — Cross-CLI verification

Each plugin manifest installs into its CLI's plugin system and the operator can invoke at least 3 skills via the CLI's native mechanism.

| CLI | Verification |
|---|---|
| Claude Code | `claude plugin validate .claude-plugin/` passes, then `/plugin install lintel@jokerman-lintel` works, `/lintel:qa` invokable |
| Codex CLI | `/plugins` → search lintel → Install Plugin works, 3 skill invocations succeed |
| Cursor | `/add-plugin lintel` works, 3 skill invocations succeed |
| Gemini CLI | `gemini extensions install <url>` works, GEMINI.md loads |
| OpenCode | Manual via `.opencode/INSTALL.md` instructions — best-effort |
| Copilot CLI | `copilot plugin install` works (schema may need adjustment post-launch) |
| Factory Droid | `droid plugin install` works (schema may need adjustment) |

**Acceptable:** 4 of 7 CLIs fully verified at v3.0.0 tag time. Remaining 3 documented as "in-progress" / "schema confirmation pending".

---

## Gate 5 — Cross-tool independent review

After internal review (`/plan-eng-review`, `/review`), one independent Codex review pass on:
- Repo structure as a whole
- 5 representative skills (CodeReviewer or operator picks)
- All compliance hooks (highest-risk surface)
- OurVoice-test rubric
- v3-new components: plugin manifests, session-harness skills, bin/ scripts

Codex P1 findings BLOCK ship. Codex P2 findings: address or document why deferred.

---

## Gate 6 — Teammate adoption verification

Before tagging v3.0.0:
- One CAIP-SE teammate runs through install flow on their machine
- They install plugin in their preferred CLI (Claude Code or Codex)
- They invoke ≥10 skills successfully (including ≥3 v3-new session-harness skills)
- They run `li-scaffold init` in a test repo and confirm output
- They report friction points + operator addresses Critical blockers

Human gate, not automated.

---

## Gate 7 — Diff-vs-upstream similarity check

Per T-303 (v2 placeholder, methodology finalization required before v3.0.0):

- Re-run T-303 methodology against v3-new components (session-harness skills, 34 new agents)
- Confirm threshold (<0.6 cosine similarity for "inspired but structurally distinct") holds
- Document any near-similarity to obra/superpowers (we explicitly used their pattern; that's attributed, not plagiarized)

**Methodology placeholder:** see `docs/design/UPSTREAM-SIMILARITY.md` for full method.

---

## Gate 8 — Honest mirror review

Before tagging v3.0.0:
- Confirm `HONEST-MIRROR-v3.md` is written — operator review of scope drift between v3 plan and v3 delivery
- Review any drift between v3 plan and v3 delivery — confirm aligned or document acceptances
- Particular focus: did agents stay focused or did build-out drift into bloat?

---

## Gate 9 — CI matrix green

`.github/workflows/ci.yml` runs on every PR + push. For v3.0.0 tag:
- Latest commit on `main` (after v3-dev merge) must have CI green across:
  - `verify-linux` (with v3 paths in --layers, --frontmatter, --counts)
  - `install-linux` (install.sh against test LINTEL_HOME with v3 paths)
  - `verify-windows` (install.ps1 + bash verify on Windows)
  - `unit-tests-linux` (includes new tests/unit/plugin-manifests-valid.sh + agents-categorized.sh)
  - `unit-tests-windows` (same on Windows)
  - `e2e-claude-code-only` (acceptable as smoke-test)
- `e2e-cross-cli` acceptable as `if: false` (Codex CLI not in CI yet)
- `compliance-check` acceptable as `if: false` (CI-mode pending)

---

## Gate 10 — License posture

- LICENSE file: MIT
- All v3-new agents stamped `tier: permissive` (operator IP, MS-internal MIT)
- README clearly states: "Lintel contains operator-authored content (MIT)"
- v3 ships NO vendored upstream code (v2's upstream-sources.yaml retained but no upstream agents in v3 — operator-authored only)
- `docs/promoted-agents.md` updated to reflect v3 zero-upstream posture

---

## How to run the gate sequence (operator)

```bash
# Gates 1, 2, 9, 10 — fully automated
bash install/verify.sh --all

# Specific v3 checks
bash install/verify.sh --plugin-manifests
bash install/verify.sh --agents-categorized
bash install/verify.sh --scaffolding-coherence
bash tests/unit/plugin-manifests-valid.sh
bash tests/unit/agents-categorized.sh

# Gate 3 (operator-driven via LLM-eval)
# See docs/design/T0-CALIBRATION-WORKFLOW.md
# Run /lintel:li-eval --corpus ... → iterate rubric → status: CALIBRATED
# Cost estimate: $1.80-6 per round, 3-5 rounds typical

# Gate 4 (per-CLI smoke test)
# Install plugin into each CLI you have:
#   Claude Code:    /plugin marketplace add jokerman89/jokerman-lintel
#                   /plugin install lintel@jokerman-lintel
#   Codex:          /plugins → search → install
#   Cursor:         /add-plugin lintel
#   Gemini:         gemini extensions install <url>
# Then invoke 3 skills, confirm they work.

# Gate 5 (outside-voice)
# Open a Codex session:
#   /codex review --paths skills/ agents/ hooks/

# Gate 6 (operator-driven; handoff to CAIP-SE teammate)

# Gate 7 (T-303 methodology against v3-new components)

# Gate 8 (manual)
# Write HONEST-MIRROR-v3.md; review scope drift

# Gate 9 (check GitHub Actions dashboard after PR merge)

# Tag if all 10 green:
git tag v3.0.0
git push origin v3.0.0
```

---

## Pre-tag automated status (as of this commit)

Last `verify.sh --all` run shows:
- ✓ Gate 1: Structural — all v3 dirs + manifests present
- ✓ Gate 2: Frontmatter — all skills+agents valid
- ⚠ Gate 3: Voice corpus — NOT_CALIBRATED (operator-driven, pending)
- — Gate 4: Cross-CLI verification — operator-driven (3+ CLIs to verify post-merge)
- — Gate 5: Cross-tool review — operator-driven
- — Gate 6: Teammate adoption — operator-driven
- — Gate 7: T-303 — methodology pending
- — Gate 8: HONEST-MIRROR-v3.md — pending operator write
- — Gate 9: CI — pending PR merge + push
- ✓ Gate 10: License posture — v3 ships only operator-authored

**Automated gates green. Operator-driven gates pending.**

---

## What happens after v3.0.0

- README links to this SHIP-GATE document
- Tag triggers release notes generation (via `/landing-report`)
- Operator runs `/rais-customer-voice-check` on release notes before publishing
- Quarterly re-run of Gates 3, 4, 7 to detect drift
- v3.0.5 patch when:
  - Copilot CLI + Factory Droid plugin schemas verified empirically
  - First batch of marketplace-submission feedback addressed
  - Any P2 findings from Gate 5 deferred to patch

---

## See also

- `docs/design/lintel:li-v3-plan.md` — current architecture
- `docs/design/lintel:li-v2-design.md` — v2 design (historical)
- `docs/design/MIGRATION-TABLE-v2.md` — v1→v2 rename mapping
- `docs/per-cli/PLUGIN-FORMAT-RESEARCH.md` — per-CLI plugin schema findings
- `docs/session-harness.md` — full session-harness mental model
- `docs/design/T0-CALIBRATION-WORKFLOW.md` — Gate 3 operator workflow
- `bash install/verify.sh --all` — automates Gates 1, 2, 10
