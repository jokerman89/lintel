# Ship Gate — JStack v1.0.0 prerequisites

Document the gates that must pass before tagging JStack v1.0.0. Path C accepted multi-week build with full vision; this gate enforces "full vision actually present".

## Gate 1 — Structural

All four layers populated with the intended scope:

| Layer                | Item                | Count target | Verify command           |
|----------------------|---------------------|--------------|--------------------------|
| 01-foundation        | skills              | 43           | `verify.sh --counts`     |
| 02-compliance        | compliance docs     | 7            | `verify.sh --compliance` |
| 02-compliance        | hooks               | 14           | `find hooks -name HOOK.md \| wc -l` |
| 03-personal-advanced | skills              | 22 (20 + jstack-test + jstack-eval) | `verify.sh --counts` |
| 03-personal-advanced | agents              | 15           | `find agents -name "*.md" \| wc -l` |
| 03-personal-advanced | voice docs          | 7 (corpus/test/calibration + 4 reference) | manual count |
| 04-power-user        | agents              | 25           | `find agents -name "*.md" \| wc -l` |

**Aggregate target:** 65 skills + 40 agents + 14 hooks + 11 compliance/voice docs.

## Gate 2 — Frontmatter discipline

Every skill + every agent must have valid frontmatter:
- name (kebab-case for skills, CamelCase for agents)
- description
- color
- tools
- voice (internal | trailblazer | mixed)
- cli_support (array)
- For Layer 3 promoted agents: tier (permissive | restricted)

**Verify:** `verify.sh --frontmatter` exits 0.

## Gate 3 — T0 voice corpus calibrated

- TRAILBLAZER-CORPUS.md has ≥24 paragraphs (≥2 known-good + ≥2 known-bad per cell × 12 cells)
- TRAILBLAZER-CALIBRATION.md shows status: CALIBRATED
- ≥10 of 12 cells pass at ≥90% known-good AND ≥90% known-bad accuracy

**Verify:** `verify.sh --voice` confirms CALIBRATED.

## Gate 4 — Cross-CLI test matrix

`/jstack-test --all` produces a matrix with:
- 0 FAIL entries (DEGRADED entries are acceptable if documented in cli_support)
- All skills declared `cli_support: [claude-code, ...]` PASS on claude-code
- Skills declared `cli_support: [..., codex, ...]` PASS or DEGRADED on codex
- Matrix written to `~/.jstack/test-matrix-<release-ts>.md` for record

## Gate 5 — Codex outside-voice review

After all internal review (`/plan-eng-review`, `/review`), one independent Codex review pass on:
- Repo structure as a whole
- 5 representative skills (CodeReviewer agent picks)
- All compliance hooks (these are the highest-risk surface)
- TRAILBLAZER-TEST rubric

Codex P1 findings BLOCK ship. Codex P2 findings: address or document why deferred.

## Gate 6 — Teammate adoption verification

Before tagging v1.0.0:
- One CAIP-SE teammate runs through the install flow on their machine
- They invoke ≥10 skills successfully
- They confirm at least 1 customer-engagement flow (scaffold-customer-demo → demo-deliverable-gen → customer-voice-check → provenance-track)
- They report friction points + the operator addresses Critical-blockers

This is a HUMAN gate, not an automated one. The point: JStack works on someone else's machine, not just the author's.

## Gate 7 — Diff-vs-upstream similarity check

Per T-303 in plan-eng-review: prove "inspired by, not plagiarized" with measurement.

**Methodology placeholder (T-303 finalization required before v1.0.0):**

For each upstream source (gstack, ECC, GSD Redux, etc. — see `install/upstream-sources.yaml`):
1. Compute embedding of each upstream SKILL.md / agent .md / hook (sentence-transformer baseline; details TBD)
2. Compute embedding of each JStack equivalent (where one exists)
3. Compute cosine similarity per pair
4. Threshold: <0.6 cosine = "inspired but distinct"; ≥0.6 = "too close to upstream, refactor"
5. Aggregate report: which pairs are flagged for refactor

**Why 0.6:** Empirical default per plan-eng-review session 2. Real value TBD after running the method on a sample. Methodology details (which embedding model, which segmentation, normalization) are part of T-303.

**Action if threshold violated:** rewrite the JStack version with structural changes — different ordering, different framing, different examples — until similarity drops below threshold. The point isn't to dodge similarity; it's to confirm JStack adds value beyond reformatting.

## Gate 8 — Honest mirror review

At Phase 4 completion (already done), the design doc required writing `HONEST-MIRROR-PHASE-4.md` with scope-drift table. Before tagging v1.0.0:

- Confirm HONEST-MIRROR was written (if applicable)
- Review scope drift since approval
- Confirm any drift is documented + accepted, OR refactor

## Gate 9 — CI matrix green

`.github/workflows/ci.yml` runs on every PR + push to main.

For v1.0.0 tag:
- Latest commit on main must have CI green across all jobs (verify-linux, install-linux, verify-windows)
- No pending or warning-level CI signals

## Gate 10 — License posture

- LICENSE file: MIT (operator-confirmed)
- All Layer 3 promoted agents tier-stamped permissive (verified via `verify.sh --tier-stamps`)
- All Layer 4 agents stamped or default-permissive
- `install/upstream-sources.yaml` declares each upstream's license tier
- README clearly states: "JStack contains operator-authored content (MIT) + installs (does NOT bundle) upstream content per its declared licenses"

## How to run the gate sequence

```bash
# Gate 1+2+10
bash install/verify.sh --all

# Gate 3
# (Operator: populate corpus, then run /jstack-eval)

# Gate 4
# (In Claude Code session: /jstack-test)

# Gate 5
# (In Claude Code session: /codex --diff main --strict)

# Gate 6
# (Hand-off to teammate; not scriptable)

# Gate 7
# (Run T-303 methodology — script to be added once methodology finalized)

# Gate 8
# (Manual review of HONEST-MIRROR-PHASE-4.md if applicable)

# Gate 9
# (Check GitHub Actions / Azure DevOps dashboard)

# Tag if all green:
git tag v1.0.0
git push origin v1.0.0
```

## What happens after v1.0.0

- README links to this SHIP-GATE document
- Tag triggers release notes generation (via `/landing-report`)
- Operator runs `/customer-voice-check` on release notes before publishing
- Quarterly re-run of Gates 3, 4, 7 to detect drift

## See also

- `/jstack-test` skill — automates Gate 4
- `/jstack-eval` skill — automates Gate 3
- `/codex` skill — supports Gate 5
- `install/verify.sh --all` — automates Gates 1, 2, 10
- `UPSTREAM-SIMILARITY.md` — Gate 7 methodology (to be finalized)
- `LAYERS.md` — 4-layer architecture (matches Gate 1 counts)
