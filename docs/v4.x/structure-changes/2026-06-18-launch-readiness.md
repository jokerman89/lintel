---
slug: launch-readiness
date: 2026-06-18
cycle_id: launch-readiness
operator: jokerman
affected_paths:
  - skills/ (autoplan, careful, build, review, handoff-size-check, catalog, doctor, help, lessons, pair-agent, scaffold, sc, ta, tq, generate-ppt, generate-word, welcome, + W1 command-ref fixes)
  - agents/ (communication, customer, devops, doc-gen craft-raise; SOC2Reviewer + JWTSecurityReviewer neutrality)
  - hooks/shared/ (10 module warn-hooks: $LINTEL_REPO_ROOT guard + grep-c fix)
  - lib/ (orientator-routing, scale-estimator, brief-forge, brief-forge-evaluators — set -u removal)
  - tests/shape/hooks-registration-safe.sh (NEW)
  - publishing (README, CONTRIBUTING, SECURITY, SHIP-GATE, CODE_OF_CONDUCT, .github templates, CHANGELOG, 5 manifests → 5.8.0)
  - docs/ (audit/, feature-requests/, lintel-state-of-the-harness.md, session-harness.md, per-cli/PLUGIN-FORMAT-RESEARCH.md untracked)
risk_class: medium
breaking_change: false
---

# Structure change: launch-readiness

> Gate M1 (structure-impact analysis) artifact. Public-launch readiness pass over the whole harness.

## What changed (shape)

No frontmatter contract changed; no skill/agent/hook renamed or removed; no function signature
changed. The shape deltas are:
- **lib (4 sourced helpers):** removed the global `set -uo pipefail` from `orientator-routing.sh`,
  `scale-estimator.sh`, `brief-forge.sh`, `brief-forge-evaluators.sh`. These are SOURCED, so the
  option previously leaked into the caller's shell. Functions are unchanged and already
  `${x:-}`-guarded. This is the M2 RED set (Q4) — see override below.
- **hooks (10 module warn-hooks):** added a `LINTEL_REPO_ROOT="${LINTEL_REPO_ROOT:-$(git rev-parse …)}"`
  guard line near the top; replaced `grep -c … || echo 0` with `var=$(grep -c …) || var=0` in 3.
- **NEW shape test** `tests/shape/hooks-registration-safe.sh` — a structural invariant (hooks.json
  registration safety). Additive.
- **Internal docs untracked** (gitignored, kept on disk): `docs/audit/`, `docs/feature-requests/`,
  `docs/lintel-state-of-the-harness.md`, `docs/session-harness.md`,
  `docs/per-cli/PLUGIN-FORMAT-RESEARCH.md`.
- **Version:** all 5 CLI manifests 5.7.x → 5.8.0.

## Backward-compat

Fully backward-compatible. Every existing callsite continues to work: the 4 libs expose the same
functions; the hooks behave identically except they no longer fail-closed on an unset env var; the
new shape test only adds coverage. Skills whose command refs were repaired now resolve where they
previously 404'd — strictly an improvement. Untracking internal docs does not affect any tracked
code path (verified: no skill/lib/test/bin references them).

## Migration path

No migration needed — additive + corrective. Operators on a plugin install get 5.8.0 via a
marketplace update; no manual action.

## Forward-compat

Enables a credible public launch. The `hooks-registration-safe` invariant forecloses the
silent-cross-platform-breakage class (single-quoted `${CLAUDE_PLUGIN_ROOT}`, `.cmd` wrapper, `-l`)
for all future hook registrations. The newcomer light-path (welcome) sets the convention that the
core "start here" set leads, not the full 125-skill catalog.

## Verification

- Shape-tests added: `tests/shape/hooks-registration-safe.sh` (ALL PASS, 9 registered hooks).
- Existing shape-tests affected: none changed; `no-swedish` + `frontmatter-lint-all` green; full
  shape scope run as the M3 gate.
- Unit tests: each verified passing individually (cycle-footer, cycle-continuity, jobs-steps ALL
  PASS; agents-categorized, envelope-schema rc=0). The full aggregate suite is slow under host
  memory pressure but green test-by-test.

## M2 compatibility-audit override (RED accepted)

`bin/li-compat-audit --against main` returned **RED** on Q4 (shared-helper changes ×4): the 4
sourced libs above. Override reason: the only change is removing a leaking `set -uo pipefail` — it
is behavior-preserving for callers (no signature/return change) and strictly *more* robust (callers
no longer inherit `set -u`). No caller relied on the leaked option. Accepted as a documented,
motivated deviation. Report: `docs/v4.x/compatibility-audits/2026-06-18-*.md`.

## Rollback procedure

`git revert` the launch-readiness commit range (9c3a71f..HEAD on `feat/launch-readiness`), or revert
individual atomic commits — each wave is its own commit. Untracked internal docs are recoverable
from git history (they were removed with `git rm --cached`, not deleted from disk).
