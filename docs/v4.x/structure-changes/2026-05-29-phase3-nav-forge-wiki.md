# Structure change — Phase 3: navigation + Brief Forge + wiki-gen + v4.0 ship

**Date:** 2026-05-29
**Cycle:** v4.0 Phase 3 (v4.0-rc → v4.0 ship)
**Mode:** meta-infra (M1-M4 active); wiki-gen under internal-tool
**Branch:** `v4.0-phase3-nav-forge-wiki`
**Refs:** `docs/design/lintel-v4.0-reframe-design.md` v2.0 §1.4 (FR-C navigation), §2.2 (FR-A Brief Forge), §2.4 (FR-C wiki-gen), §5.2 Phase 3

## What changed

### Navigation orientator (Chapter 1.C)

- **New:** `skills/orientator/SKILL.md` — lightweight agent that reads operator's prompt + active pack's `navigation.*` block at SENSE time, recommends a workflow with confidence + reasoning. Mechanical-first (keyword + path heuristics) with LLM escalation when mechanical confidence < threshold.
- **New:** `lib/orientator-routing.sh` — sourced helpers for mechanical routing (intent classification, workflow matching, risk assessment).
- **Extended:** `skills/sense/SKILL.md` — adds Step 0d that invokes orientator after Step 0c (meta-infra detection). Orientator output surfaces in SENSE report as routing recommendation.
- **New audit:** `~/.lintel/audit/orientator-decisions.jsonl` — every routing decision logged with input signals + chosen workflow + confidence + budget consumed.

Per design doc §1.4 tweak: orientator budget is pack-configurable via `pack.yaml.navigation.orientator_budget_tokens` (default 2000, caip-se 5000). Auto-mode level (b): auto-start low-risk workflows, confirm high-risk per `pack.yaml.navigation.high_risk_workflows`.

### Brief Forge (Chapter 2.A)

- **New:** `skills/brief-forge/SKILL.md` — universal hand-off gate. Fires at every subagent_spawn, phase_transition, workflow_handoff, cold_executor, operator_input event (per pack policy in `brief_forge_handoffs.*`).
- **New:** `lib/brief-forge.sh` — sourced library exposing `forge_envelope <kind> <from> <to> <content_type> <content_file>` and helpers. Constructs envelopes per `lib/envelope-schema.yaml`.
- **New:** `lib/brief-forge-evaluators.sh` — pluggable evaluator framework. Ships 5 evaluators:
  - `security` — scans payload for secrets, dangerous shell patterns, prompt injection markers
  - `completeness` — checks required content_type fields present, surfaces gaps
  - `stale` — verifies referenced paths/files still exist at hand-off time
  - `sdl_compliance` — verifies SDL hooks ran on payload (ms-internal + caip-se)
  - `trailblazer_alignment` — voice-tier check against Trailblazer corpus (caip-se)
- **New audit:** `~/.lintel/audit/brief-forge.jsonl` + per-date `~/.lintel/audit/envelopes-YYYY-MM-DD.jsonl`

Cold-path-bypass: skills declaring `brief_forge_bypass: true` in frontmatter skip the gate entirely (operator's hotfix flow). Pack policy can additionally list eligible skills under `brief_forge_handoffs.cold_path_bypass.eligible_skills`.

### Wiki generation (Chapter 2.C)

- **New:** `bin/li-wiki-gen` — regenerates both outputs from current sources:
  - **Markdown wiki:** `docs/wiki/` (skills, agents, packs, schemas, navigation map, envelope shape)
  - **Showcase HTML:** `docs/showcase/lintel-the-harness.html` regenerated from sources rather than hand-curated
- **New:** `lib/wiki-gen.sh` — sourced helpers (parse frontmatter, build TOC, render markdown table).
- **New:** `bin/li-forge-stats` — aggregates Brief Forge envelopes from audit logs, reports per-skill / per-pack completeness scores.

Closes v3.7 gap "wiki vs showcase drift" per design doc §2.4: same generator produces both outputs from the same sources.

### SHIP gate (v4.0 ship event)

- **New:** `bin/li-ship-gate-v4.0` — runs all four M-gates + verifies migration index is current + writes ship-gate audit. This is the canonical pre-ship check.
- **Extended:** `docs/v4.x/migrations/_INDEX.md` — adds Phase 3 entries (orientator invocation, brief-forge wiring, wiki-gen pre-commit).
- **New:** `CHANGELOG.md` (or extended if existing) — v4.0 release notes.

## Backward compatibility

| Surface | Phase 3 change | Backward-compat? |
|---|---|---|
| SENSE workflow | Adds Step 0d (orientator invocation) | YES — orientator surfaces recommendation but never blocks |
| Operator manual workflow choice | Operator's explicit `--mode <preset>` still wins | YES — orientator runs only when no explicit choice |
| Hand-off plumbing | Brief Forge fires on configured events | YES, additive — packs that don't opt in (`enabled: false`) skip evaluators |
| Skill frontmatter | New optional `brief_forge_bypass: bool` field | YES — additive, default false |
| `lib/envelope-schema.yaml` | No change (shipped Phase 2) | YES |
| `lib/pack-resolver.sh` | No public API change; reads new `brief_forge_handoffs.*` field (already declared in _default/ms-internal/caip-se) | YES |
| Wiki output | Replaces hand-curated `docs/showcase/lintel-the-harness.html` | **MAYBE** — operators with custom showcase edits will be overwritten. Mitigation: pre-commit hook stages diff for review |

**Verdict:** GREEN with one YELLOW note: existing showcase replacement is documented in `docs/v4.x/migrations/_INDEX.md` so operators know what to expect.

## Migration path

For operators using v4.0-alpha/beta (Phase 1+2):

1. After this PR lands: `git pull` brings orientator, Brief Forge, wiki-gen into the repo
2. Next session SENSE Step 0d invokes orientator automatically (silent if mechanical confidence ≥ threshold)
3. Brief Forge fires at hand-offs per active pack's policy (default policies in `_default`/`ms-internal`/`caip-se` are already correct)
4. Operators wanting to bypass Brief Forge on a specific skill add `brief_forge_bypass: true` to that skill's frontmatter
5. CI starts running `bin/li-wiki-gen --check` and fails on diff (warn-only per design doc §2.4 in v4.0; fail-on-diff from v4.1)

`/li:v4-migrate` (from Phase 2) gets a Phase 3 addendum: detects Phase 1+2 state, recommends no action (already current).

## Forward compatibility

Phase 4 engineering-domain modules (TA, SC, DA, DH, TQ) read:
- `pack.yaml.brief_forge_handoffs.*` to wire their own hand-offs through Brief Forge
- `lib/envelope-schema.yaml` content_types to add module-specific shapes (e.g. `content_type: tech_architecture_review`)
- `lib/orientator-routing.sh` to extend routing heuristics

The mechanical-first / LLM-escalation pattern in orientator is the template for Phase 4 modules that need mode-aware decisions.

## Verification

REVIEW phase runs:
1. `bash tests/runner/run-all.sh` — all 32+ existing tests pass plus 3 new Phase 3 unit tests + 4 new shape tests
2. `bash tests/runner/run-all.sh --shape-only` — 12 shape-tests total now (8 existing + 4 new)
3. `bash tests/unit/orientator-mechanical-routing.sh` — 6 routing scenarios pass
4. `bash tests/unit/brief-forge-evaluator-runs.sh` — 5 evaluators execute correctly + envelope construction roundtrip
5. `bash tests/unit/wiki-gen-idempotency.sh` — `li-wiki-gen` run twice produces identical output (deterministic)
6. `bin/li-compat-audit` — Gate M2 mechanical sweep produces GREEN verdict
7. `bin/li-ship-gate-v4.0` — all M-gates pass, migration index current, ship verdict GREEN

## Rollback

If SHIP discovers a regression after v4.0 ships to main:

- **Orientator wrong on common routes:** revert `skills/sense/SKILL.md` Step 0d invocation; orientator skill stays in repo as standalone
- **Brief Forge evaluator false positives:** disable specific evaluator via pack override (`brief_forge_handoffs.<event>.evaluators` list excludes the bad evaluator)
- **Brief Forge breaks hand-offs:** every pack can set `brief_forge_handoffs.<event>.enabled: false` to disable wholesale; cold-path-bypass remains
- **Wiki-gen produces wrong output:** disable CI check; manually edit showcase until generator fixed
- **Ship-gate false fail:** explicit override via `--force` flag, audited

Each rollback is independent. The four Phase 3 deliverables are layered but not entangled.

## What this enables (post-v4.0)

- Phase 4 modules can ship one at a time without further plumbing work
- Operators authoring custom packs inherit orientator + Brief Forge + wiki-gen automatically
- `bin/li-forge-stats` gives operators visibility into hand-off completeness over time — informs Phase 4 module design
- Wiki + showcase stay in sync with code forever
