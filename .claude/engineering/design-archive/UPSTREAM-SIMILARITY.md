# Upstream Similarity Methodology (T-303)

Methodology placeholder for Gate 7 of `SHIP-GATE.md`. Operationalizes "inspired by, not plagiarized" with measurement.

## The question this answers

> "Is the Lintel version of skill X (or agent Y) structurally distinct enough from the upstream version that we can honestly claim it's inspired rather than copied?"

## The method (current placeholder — T-303 to finalize)

For each `(Lintel item, upstream-equivalent)` pair:

1. **Segmentation:**
   - Skill files: split into frontmatter + body (workflow + report-format sections)
   - Agent files: split into frontmatter + body
   - Compare body-to-body; ignore frontmatter (frontmatter conventions are inherently similar)

2. **Embedding:**
   - Use `sentence-transformers/all-MiniLM-L6-v2` (or operator-chosen baseline; `all-mpnet-base-v2` for higher quality)
   - Embed each segment as a 384-dim (or 768-dim) vector
   - One embedding per skill/agent body

3. **Similarity:**
   - Cosine similarity between paired embeddings
   - Range: -1.0 to 1.0 (1.0 = identical; 0 = orthogonal; -1.0 = opposite)

4. **Threshold:** **0.6**
   - <0.6 = "inspired but structurally distinct" — passes
   - ≥0.6 = "too close to upstream" — refactor required

5. **Output:** structured CSV / JSON with one row per pair:
   - `lintel_path`, `upstream_path`, `similarity_score`, `verdict` (PASS / FLAG)

## Why 0.6 specifically?

**Empirical default**, not a derived number. Selected per plan-eng-review session 2 (T-303) as a starting point. Real value should be determined by:

1. Run the method against a sample of pairs (5-10)
2. Manually classify each pair as plagiaristic / inspired / distinct
3. See what threshold separates the human judgments
4. Adjust 0.6 → empirically-validated value

Anti-pattern: pick 0.6 forever without empirical validation. The number must earn itself.

## What this method does NOT capture

- **Semantic plagiarism without lexical overlap:** if Lintel restates upstream's logic with completely different words, similarity may be low even if conceptually identical. Mitigation: pair with manual review for high-stake skills.
- **Structural plagiarism:** if Lintel copies the section ordering + bullet structure exactly but rewrites prose, similarity drops but plagiarism may remain. Mitigation: section-structure diff as supplement.
- **License-load-bearing content:** even low-similarity content may violate license if it's distinctive enough to be the "creative work". License compatibility is orthogonal to similarity score (see `LICENSE-TIERS.md`).

## What to do when a pair flags

Operator response when a pair scores ≥0.6:

1. **Read both files side by side.** Is it actually too similar, or is the method over-flagging?
2. **If actually too similar:** restructure Lintel version. Options:
   - Different section ordering
   - Different framing (e.g. "what NOT to do" first instead of "what to do")
   - Different examples (build the Lintel example from CAIP-SE context)
   - Different vocabulary (where upstream uses one term consistently, use a synonym for the same concept)
3. **Re-measure.** If still ≥0.6: keep restructuring until <0.6.
4. **If method is over-flagging:** operator documents why in `~/.lintel/audit/upstream-similarity-overrides.jsonl` with rationale. Periodic review of overrides.

## Implementation status

**Current state:** PLACEHOLDER. The skill / script that runs this methodology is NOT YET BUILT.

**Path to implementation:**
1. Pick the embedding model (default proposal: `all-MiniLM-L6-v2` for speed; upgrade to `all-mpnet-base-v2` for quality)
2. Implement segmentation (frontmatter strip + body extract)
3. Implement pair-matching (Lintel → upstream by name + role)
4. Implement similarity compute
5. Implement threshold + reporting
6. Run on sample, tune threshold

**Estimated effort:** ~2 SE-days for a working implementation.

**Owner:** TBD. Plan-eng-review T-303 names this as a v1.0.0 blocker.

## Pre-implementation manual gate

Until the script exists, the operator manually:

1. For each Lintel skill/agent, identify its closest upstream analog (from gstack, ECC, GSD Redux, etc.)
2. Read both side by side for 30 seconds
3. Honestly classify: distinct / inspired / too-close
4. Record the classification in `~/.lintel/manual-similarity-review.md`

This is slower + more subjective, but defensible while the script is pending.

## See also

- `SHIP-GATE.md` Gate 7 — where this methodology applies
- `LICENSE-TIERS.md` — orthogonal concern (compatibility, not similarity)
- `install/upstream-sources.yaml` — the upstream sources to compare against
- plan-eng-review T-303 (in the design doc) — the formal task assignment
