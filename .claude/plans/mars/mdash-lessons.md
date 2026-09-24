# MDASH lessons for Lintel: catch it inline, need the scanner less

**Date:** 2026-09-24
**Sources:** [Microsoft Security blog, 2026-05-12](https://www.microsoft.com/en-us/security/blog/2026/05/12/defense-at-ai-speed-microsofts-new-multi-model-agentic-security-system-tops-leading-industry-benchmark/),
[Codename MDASH overview](https://learn.microsoft.com/en-us/security-exposure-management/ai-code-security-overview),
[MAI-Cyber-1-Flash inside MDASH](https://microsoft.ai/news/introducing-mai-cyber-1-flash-inside-mdash/).

## What MDASH is

Microsoft's multi-model agentic scanning harness orchestrates 100+ specialized agents over a
panel of frontier and distilled models in five stages: **prepare** (index, attack surface,
threat model from past commits), **scan** (per-bug-class auditors emit hypotheses with
evidence), **validate** (debaters argue for/against reachability and exploitability),
**dedupe** (collapse equivalent findings) and **prove** (build and run a triggering input).
Its stated advantage is the system, not a single model; disagreement between models is used
as a signal, and a cheap distilled model does high-volume passes while SOTA models reason.

## What Lintel should take (so fewer bugs reach an MDASH-class scanner)

| MDASH practice | Inline Lintel equivalent | Where |
|---|---|---|
| Prepare: threat model from past commits and CVEs | Surface bug classes this repo has actually shipped (lessons, reverted fixes, P1 history) into PLAN and BUILD, not just REVIEW. | `lessons-surface` keywords per package; `sc` threat-model on security-touching packages |
| Specialized auditors per bug class | Per-class checklists in the builder's definition of done: path/traversal, off-by-one/boundaries, error swallowing, auth, concurrency, injection. One short list per touched class. | build card acceptance; CodeReviewer lens |
| Hypothesis + evidence, not vibes | Every finding carries a concrete failing input or counterexample (MARS protocol enforces this). | `skills/mars/references/protocol.md` |
| Debate before trusting a finding | MARS blind pass + one challenge round; disagreement is a signal, majority is not truth. | `/li:mars` |
| Prove stage | "Prove before claiming": a finding or a fix is done when a failing test reproduces it and passes after. Turn each accepted MARS/review finding into a regression test. | BUILD verification; ADR-0008 behavior tests |
| Dedupe | Synthesis collapses equivalent claims into one ID with all evidence. | MARS synthesis rubric |
| Cheap model for volume, strong model for depth | Default MARS roster mixes families; use subagents (low overhead) for volume, reserve nested sessions/extra effort for high-stakes subjects. | `lib/mars-defaults.json` |
| Plugins with domain invariants | Pack `knowhow` supplies domain invariants (lock rules, trust boundaries) to builders and reviewers. | pack-resolver `knowhow` |
| Zero-noise culture | Confidence per finding, file:line citation, unique catches must survive challenge; low-confidence items go to an appendix. | CodeReviewer + MARS |

## The inline loop (cheapest place to catch a bug)

1. **Write the invariant first.** Docstring/contract states preconditions (1-based page,
   stays inside root, re-raises last error). The pilot's three seeded bugs were all
   contract-vs-code mismatches that a one-line boundary test would have caught.
2. **Boundary test per touched function** before the implementation is called done:
   first/last/empty/zero, hostile input for anything path- or auth-shaped, the error path.
3. **Run the check you are about to claim.** No "should work": the builder executes the
   failing input from the card.
4. **Escalate by risk, not by habit.** Mechanical packages: self-check + independent review.
   Security, data-loss or irreversible packages: add MARS before merge. Whole-codebase
   vulnerability discovery stays MDASH/CodeQL territory; Lintel prevents, MDASH hunts.

## What not to copy

- A 100-agent always-on pipeline. Lintel stays deliberate: MARS is bounded and opt-in.
- Autonomous exploit generation against real systems. Proof stays a local test.
- Claims of recall/precision. MDASH's numbers are its own benchmarks; Lintel records
  per-panel evidence only.
