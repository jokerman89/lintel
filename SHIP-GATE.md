# Ship Gate — Lintel v3.5.0 prerequisites

13 gates that must pass before tagging v3.5.0. v3 (10 gates) + 3 new v3.5 gates covering cycle, role-lifting, and context-warming infrastructure.

Updated for v3.5 cycle architecture (8 phases, role-lifting, context-warming, mode presets). Voice calibration + marketplace submission remain operator-driven.

---

## Gate 1 — Structural (v3.5 layout)

All v3.5 directories populated as intended:

| Path | v3.5 target | Verify command |
|---|---|---|
| `skills/` | 165 skills | `bash install/verify.sh --counts` |
| `agents/` | 70 agents across 8 categories | `bash install/verify.sh --agents-categorized` |
| `hooks/shared/` | 29 hooks | `find hooks/shared -name HOOK.md \| wc -l` |
| `scaffolding/01-foundation/` | base templates intact | `bash install/verify.sh --scaffolding-coherence` |
| `packs/_default/` | neutral baseline pack | `bash install/verify.sh --packs` |
| `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/`, `.copilot-plugin/`, `.droid-plugin/`, `gemini-extension.json` | 7 plugin manifests valid JSON | `bash install/verify.sh --plugin-manifests` |
| `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` at root | 3 entrypoint files | included in `--plugin-manifests` |
| `bin/` | 6 operator-side utilities | `ls bin/` |

**Aggregate target:** 165 skills + 70 agents + 29 hooks + 7 plugin manifests + 3 entrypoint files + 7 bin scripts + 3 default public roles + intact scaffolding templates.

**v3.5-specific subset:**
- 8 phase-skills: li-sense, li-define, li-discover, li-plan, li-build, li-review, li-ship, li-capture
- 2 orchestrator: li-cycle, li-resume
- 4 composites: li-fix, li-research, li-plan-and-build, li-review-and-ship
- 8 role-lifting: li-role-activate, li-role-deep-dive, li-role-frame, li-role-rotate, li-role-deactivate, li-roles-list, li-role-new, li-role-update
- 10 context-warming: li-context-warm, li-context-warm-related/sessions/adrs/customer/from-url, li-context-dump, li-context-snapshot, li-context-budget, li-context-cool

---

## Gate 2 — Frontmatter discipline

Every skill + every agent must have valid frontmatter:
- `name` (kebab-case `li-*` for skills, CamelCase for agents)
- `description`
- `color`
- `tools`
- `voice` (internal | mixed | custom — resolves to active pack's voice tier)
- `cli_support` (v2 array — retained for compat; v3 plugin manifests handle CLI discovery)
- `category` (NEW v3 — for agents only; matches directory)
- `layer` (for skills only; foundation)
- `tier` (REQUIRED for security / compliance agents — permissive default for engineering)

**Verify:** `bash install/verify.sh --frontmatter && bash install/verify.sh --agents-categorized` both exit 0.

---

## Gate 3 — voice corpus (pack-driven)

Lintel itself ships no voice corpus (the `_default` pack enforces no voice). This gate applies to a **company pack** (e.g. lintel-caip-pack), verified in that pack's own ship gate:
- The pack's voice corpus has adequate known-good / known-bad coverage per cell
- The pack's calibration status is CALIBRATED
- Cell accuracy meets the pack's threshold

**Verify:** `bash install/verify.sh --voice` confirms CALIBRATED.

**Status pre-tag:** operator must execute T0-CALIBRATION-WORKFLOW.md (3-5 rounds, $1.80-6 per round).

---

## Gate 4 — Cross-CLI verification

Each plugin manifest installs into its CLI's plugin system and the operator can invoke at least 3 skills via the CLI's native mechanism.

| CLI | Verification |
|---|---|
| Claude Code | `claude plugin validate .claude-plugin/` passes, then `/plugin install lintel@jokerman-lintel` works, `/li:qa` invokable |
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
- the active pack's voice rubric (if any)
- v3-new components: plugin manifests, session-harness skills, bin/ scripts

Codex P1 findings BLOCK ship. Codex P2 findings: address or document why deferred.

---

## Gate 6 — Teammate adoption verification

Before tagging v3.0.0:
- One teammate runs through install flow on their machine
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
- All agents stamped `tier: permissive` (operator IP, MIT)
- README clearly states: "Lintel contains operator-authored content (MIT)"
- v3 ships NO vendored upstream code (v2's upstream-sources.yaml retained but no upstream agents in v3 — operator-authored only)
- `docs/promoted-agents.md` updated to reflect v3 zero-upstream posture

---

## Gate 11 (NEW v3.5) — Cycle infrastructure

Lintel 8-phase cycle ships with full depth:
- All 8 phase-skills present + valid frontmatter
- li-cycle orchestrator can dispatch each phase
- li-resume reads 00-state.md correctly
- 4 composite shortcuts delegate properly to li-cycle
- generic mode presets defined in li-cycle (hotfix, internal-tool, research-dive, meta-infra); customer-engagement/demo-prep are pack-contributed
- 00-state.md schema consistent across all phases

**Verify:**
```bash
bash install/verify.sh --counts | grep -E "^Skills:" # ≥165
ls skills/li-{sense,define,discover,plan,build,review,ship,capture}/SKILL.md
ls skills/li-{cycle,resume,fix,research,plan-and-build,review-and-ship}/SKILL.md
bash tests/unit/cycle-skills-present.sh
```

**Operator dogfood requirement:** Run `/li:cycle --mode internal-tool` on real work, validate phase transitions + gates fire correctly.

---

## Gate 12 (NEW v3.5) — Role-lifting infrastructure

Role-lifting capability operational:
- All 8 role-skills present + valid frontmatter
- 3 default public roles ship (field-cto, solution-architect, engineering-manager)
- Role files follow AI-optimized format (IDENTITY + COLD KNOWLEDGE + DECISION CRITERIA + VOICE + OUTCOME LENS per phase + INSIGHTS + COMPANION SKILLS)
- `bin/li-roles-sync` script executable, setup/push/pull/status/forget commands work
- Sensitivity field enforced (public vs private separation in storage)
- Lightweight session-start load (~500 tokens via li-role-activate)
- Deep-dive on-demand (~2-3k tokens via li-role-deep-dive)

**Verify:**
```bash
ls roles/{field-cto,solution-architect,engineering-manager}.md
ls skills/li-role-{activate,deep-dive,frame,rotate,deactivate,new,update}/SKILL.md
ls skills/li-roles-list/SKILL.md
test -x bin/li-roles-sync
bash tests/unit/role-files-valid.sh
```

**Operator dogfood requirement:** Activate field-cto role pre-customer-meeting, verify lens applies in DEFINE phase.

---

## Gate 13 (NEW v3.5) — Context-warming infrastructure

On-demand 1M-context utilization beyond session-start:
- All 10 context-warm skills present + valid frontmatter
- Base `li-context-warm` accepts paths/globs, reports tokens added
- Variant skills (warm-related, warm-sessions, warm-adrs, warm-customer, warm-from-url) delegate to base
- URL gate active for warm-from-url when pack compliance mode is `hard`
- Customer-repo access audit-logged
- Budget tracking via `.lintel/state/context-budget.md`
- Selective cool via IGNORE markers (li-context-cool)

**Verify:**
```bash
ls skills/li-context-{warm,warm-related,warm-sessions,warm-adrs,warm-customer,warm-from-url}/SKILL.md
ls skills/li-context-{dump,snapshot,budget,cool}/SKILL.md
bash tests/unit/context-warm-skills-present.sh
```

**Operator dogfood requirement:** `/li:context-warm-adrs networking` during PLAN phase, validate budget tracking accurate.

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
# Run /li:eval --corpus ... → iterate rubric → status: CALIBRATED
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

# Gate 6 (operator-driven; handoff to a teammate)

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
- Operator runs the active pack's voice gate (if any) on release notes before publishing
- Quarterly re-run of Gates 3, 4, 7 to detect drift
- v3.0.5 patch when:
  - Copilot CLI + Factory Droid plugin schemas verified empirically
  - First batch of marketplace-submission feedback addressed
  - Any P2 findings from Gate 5 deferred to patch

---

## See also

- `docs/design/lintel-v4.0-reframe-design.md` — current architecture
- `docs/design/lintel-v3-plan.md` — v3 design (historical)
- `docs/design/lintel-v2-design.md` — v2 design (historical)
- `docs/design/MIGRATION-TABLE-v2.md` — v1→v2 rename mapping
- `docs/per-cli/PLUGIN-FORMAT-RESEARCH.md` — per-CLI plugin schema findings
- `docs/session-harness.md` — full session-harness mental model
- `docs/design/T0-CALIBRATION-WORKFLOW.md` — Gate 3 operator workflow
- `bash install/verify.sh --all` — automates Gates 1, 2, 10
