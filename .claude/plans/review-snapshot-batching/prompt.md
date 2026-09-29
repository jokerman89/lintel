# Cold handoff: C-01.blob-reads

Read [spec.md](spec.md), [plan.md](plan.md) and [work.json](work.json).
Keep the original C-01.blob-reads identity and all acceptance.
The baseline is exactly `0baa9a0c6e518dc619668aef03e2889ca599dab8`.

Implement only an optional selected-blob prefetch in the existing P05 snapshot:
one binary `git cat-file --batch` process, lock-step full-hex OID requests,
strict size/type/OID/trailer framing, completed-prefix cache on failure and the
unchanged original per-object fallback. Start no process for an empty OID set.
Selection and all error precedence remain owned by the existing implementation.

Only `lib/review_contract.py`, `tests/unit/review_evidence.py` and this initiative's
minimal records may change. No schemas, versions, changelog, shared todo, MARS
frequency, ignored-file behavior, old Adaptive worktree or other owners' writes.
Use this new worktree's own explicit profile, never the old Adaptive reference.

Run the new differential class first, then the smallest relevant existing tests.
No new actor, dependency, host experiment, benchmark, network or full stress suite.
Keep malformed-protocol observations distinct from real Git fixtures. Compare
full output and first errors to the unchanged path; never change expected values.
Freeze the candidate for the existing independent reviewer before delivery.

Return exact commits/tree, scoped diff, genuine profile, observed test outputs,
process counts and limits. C-01 re-snapshot frequency and C-02 remain open.
The coordinator owns publication and future aggregate acceptance.

## Current state

The scoped implementation, differential proof and independent source review are
complete; see the original completed leaves and retained P3 observations in
plan.md. Do not restart them or reinterpret source review as aggregate/hosted
clearance. The coordinator owns the next integration and its remaining gates.
