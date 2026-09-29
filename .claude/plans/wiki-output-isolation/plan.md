# Plan: isolate partial wiki output

**Status:** APPROVED.
**Base:** `19b30eef82abed3ac931cdae5e298a648291db54`.
**Spec:** [spec.md](spec.md).
**Original scope:** W1-6 / BIN-02; all other helper and portfolio cards remain open.

| Package ID | Outcome | Leaf IDs | Owner / edit boundary | Dependencies |
|---|---|---|---|---|
| P1 | Explicit output selection is truthful in generation and read-only checks. | W1-6.wiki | Coordinator; `bin/li-wiki-gen`, `tests/unit/wiki-gen-idempotency.sh`, `docs/concepts/wiki-generation.md`, `.claude/plans/wiki-output-isolation` | none |

- [ ] W1-6.wiki Isolate partial generation/check output; preserve default artifacts and validate invalid selectors before writes. Verify R1-R5 with the existing generator and new regression cases.

## Execution

1. Preserve the pre-fix observation of README appearing in a fresh showcase-only
   output directory; do not claim index preservation from a failed metadata guard.
2. Extend the existing unit script with selected-file sets, sentinel preservation,
   partial check/no-write behavior and invocation refusals.
3. Select outputs once; reuse one selected-generation path for write and check
   modes, preserving existing renderers and schema checks.
4. Run targeted unit and default drift checks in the owned synthetic environment.
5. Freeze a coherent candidate for a separate reviewer; the coordinator handles
   any later joined version, hosted verification and publication.

## Limits and review

No source/target profile is borrowed. Targeted local verification is not live-host
acceptance or proof of the full matrix. The generator and regression changes are implemented locally. The expanded unit
script and default generated-output check pass, including selected drift refusal
without baseline writes. Independent review and current integrated verification
remain pending; no branch cleanup or publication is authorized by this plan.
