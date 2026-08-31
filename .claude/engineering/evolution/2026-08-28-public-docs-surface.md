---
slug: public-docs-surface
date: 2026-08-28
cycle_id: beta-release-docs
operator: jokerman
affected_paths:
  - docs/
  - .claude/engineering/
  - README.md
  - LAYERS.md
  - SHIP-GATE.md
  - CLAUDE.md
  - AGENTS.md
  - GEMINI.md
  - AGENT-INSTRUCTIONS.md
  - CONTRIBUTING.md
  - CHANGELOG.md
  - bin/li-wiki-gen
  - bin/li-uniformity
  - bin/li-compat-audit
  - install/verify.sh
  - tests/shape/no-swedish.sh
  - skills/cycle/SKILL.md
  - skills/sense/SKILL.md
  - skills/uniformity/SKILL.md
  - lib/state.sh
  - lib/auto-decide.sh
  - hooks/shared/cycle-position-inject/run.sh
risk_class: medium
breaking_change: false
---

# Structure change: public-docs-surface

> Gate M1 (structure-impact analysis) artifact. Created under meta-infra mode for the
> `v0.9.0-beta` public release.

## What changed (shape)

The repository gained a **published/internal split** it did not previously have.

Before: `docs/` held both adopter documentation and internal engineering artifacts — audit records,
Gate M1 evolution entries, Gate M2 compatibility audits, superseded design documents. 130 markdown
files, undifferentiated.

After: `docs/` is the published surface only (48 files). Internal engineering artifacts live under a
new root, `.claude/engineering/`, with four sub-directories:

| New path | Holds | Moved from |
|---|---|---|
| `.claude/engineering/audits/` | audit records | `docs/audit/` (28) + `docs/lintel-state-of-the-harness.md` |
| `.claude/engineering/compat-audits/` | Gate M2 artifacts | `docs/v4.x/compatibility-audits/` (14) |
| `.claude/engineering/evolution/` | Gate M1 artifacts (the evolution log) | `docs/v4.x/structure-changes/` (22) |
| `.claude/engineering/design-archive/` | superseded design documents | `docs/design/` (23), `docs/feature-requests/`, `docs/per-cli/`, `LAYERS.md`, `docs/session-harness.md` |
| `.claude/engineering/SHIP-GATE.md` | the internal release checklist | repo root |

Also: `docs/v4.x/migrations/` became `docs/migrations/` (it is adopter-facing and the `v4.x` prefix
had become misleading), and three new published documents were added — `docs/README.md`,
`docs/architecture.md`, `docs/the-cycle.md`.

This is a **placement** change. No skill, agent, hook or helper changed behaviour; the frontmatter
contracts are untouched.

## Backward-compat

233 inbound references were repointed in the same change. The classes:

- **Generator write-paths (2).** `bin/li-uniformity` wrote to `docs/audit/uniformity-matrix.md` and
  `bin/li-compat-audit` wrote to `docs/v4.x/compatibility-audits/` from two branches. Unrepointed,
  these would have silently recreated the public directories on the next run — the failure mode that
  made the previous attempt at this move unsafe.
- **CI-gating checks (2).** `install/verify.sh` resolved `docs/design/CONTEXT-ENGINE.md` and
  `docs/design/CLI-SUPPORT-V2-SCHEMA.md`; the first fails hard, and `--all` runs in three CI jobs on
  Ubuntu and Windows.
- **Structured-comment `# intent:` headers (3).** `lib/state.sh`, `lib/auto-decide.sh` and the
  registered `cycle-position-inject` hook cited moved records.
- **Gate instructions in skills (5).** `skills/cycle/SKILL.md` (M1 template path, M2 output path) and
  `skills/sense/SKILL.md` named paths an agent is told to open.
- **Emitted operator-facing text (6).** `bin/li-uniformity`'s `--help` window and
  `skills/uniformity/SKILL.md`'s executable block printed paths to the operator.
- **Prose links (~193)** across decision records, memory files, concept docs and the changelog.
- **Test control flow (2).** `tests/shape/no-swedish.sh` had directory allowlist branches.

Nothing outside this repository is affected. No consumer repo references these paths — they are
Lintel-internal artifact locations, not part of the scaffolding installed elsewhere.

## Migration path

No migration needed — placement-only, and every inbound reference moved in the same change.

## Forward-compat

**Enables.** A published surface that can be audited as a unit: "is every file under `docs/`
something an adopter should read?" is now a meaningful question with a yes/no answer. It also makes
the internal record safe to keep growing — audit and gate artifacts accumulate under
`.claude/engineering/` without diluting the documentation an adopter navigates.

**Forecloses.** Nothing structural. The one cost is that the meta-infra gates now write outside
`docs/`, so a future contributor looking for the evolution log will not find it by browsing the
documentation tree — `CLAUDE.md` and `docs/README.md` both name the new location to compensate.

**Deliberate deviation.** The approved plan named `.claude/audit/`. That would have collided
conceptually with `.claude/runtime/audit/`, which holds JSONL event logs — two different things
called "audit" one directory apart. `.claude/engineering/` avoids the collision and states the kind
plainly.

## Verification

- **Shape tests added:** none. This change adds no new contract.
- **Existing shape tests affected:** `tests/shape/no-swedish.sh` (two dead allowlist branches
  removed — the English-only guard now covers the public tree with no directory exemptions);
  `tests/shape/uniformity-coverage.sh` (printed path corrected);
  `tests/shape/cli-tiers-sync.sh` (unaffected, and confirms the rewritten README's generated table
  still matches `lib/cli-tiers.yaml` byte for byte).
- **Regression coverage:** full shape suite green (36/36) immediately after the relocation and again
  after the documentation rewrite. A link checker over the published tree resolves every relative
  markdown link.
- **Independent verification:** the reference map that drove the repoint was produced by a read-only
  agent sweep over all file types, not by a single grep — it found 40 live dependencies where a
  hand grep of markdown had found substantially fewer, including both CI breakers.

## Rollback procedure

The pre-change history is captured in two places:

1. `../lintel-pre-beta-history.bundle` — a verified `git bundle --all` of the complete
   pre-rewrite repository, sitting beside the working copy.
2. The relocation is a single commit range on `feat/launch-readiness`; `git revert` of that range
   restores both the file placement and every repointed reference together, because they moved in
   the same commits.

Manual step after a revert: re-run `bin/li-wiki-gen` to regenerate `docs/wiki/` and the showcase
page against the restored tree.
