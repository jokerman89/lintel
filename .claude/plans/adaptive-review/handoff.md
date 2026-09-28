# Adaptive review integration handoff

**Status:** local source implemented and frozen at
`f01294db59f4d6ca13d9c43745ef0df6c014f983`; final independent SPEC and QUALITY
PASS, zero open P1/P2/P3. Read [the final source review](final-review.md).
The unchanged P05 regression entry was interrupted with no suite verdict.
No release clearance, remote publication or merge to main.

Read [spec.md](spec.md), [plan.md](plan.md), [verification.md](verification.md) and
the actual final review before continuing. Preserve T1-T12, ADR-0040 and the
existing work map; do not create another backlog.

## Ownership and ordering

The portfolio coordinator is `9854860c-9038-488a-b7b6-1b14150fbaa6`
(Lintel master merge). Agreed landing order is native1a, then patterns, then
adaptive review. Hooks1b is separate and must not have duplicate generator or
manifest ownership. Native1a reserves 0.13.0; select the next genuinely free
version at integration time, not a hardcoded 0.13.1.

Adaptive branch: `jokerman-microsoft-adaptive-review`. Original base is
`49f2d152`; current main subsequently advanced to
`c3ffa153561108f8dd9bd656b05af62476d816be` through another owner's work.
Do not treat the original base as final current-main acceptance.

No native generator, cli_support frontmatter, adapter, hooks, plugin version,
P05/P07 schema, MARS defaults or shared todo.md was changed. Canonical body joins
must be regenerated with the actually landed native1a generator. Never hand-edit
generated discovery files. The held unrelated review-remediation backlog stays
held; this feature does not claim its closure.

## Provider and source boundaries

The patterns provider is absent on this branch's main baseline. The adapter
reports unavailable, not empty; known pattern/policy dependencies cannot pass.
The real synthetic-lock test passed on an isolated checkout of frozen
`64338b6c`; later owner metadata `82e97d74` does not alter those product bytes.
This is only adapter integration evidence. The patterns stack remains separately
blocked on its original host/Windows/PDF/P07 acceptance; no evidence transfers.

`lib/review_context.py` uses only the trusted sibling provider's own parsers,
verification, projection and coverage. It does not implement policy resolution,
load assets automatically or invent a new pack field. The calling workflow still
obtains a current roots envelope and includes its actual inputs in P05 selection.

## Continue safely

1. Read the final review and exact freeze commit, then inspect the current branch
   and owner messages. Verify any later correction as a new ordinary commit.
2. Reconcile native1a/current-main/patterns through ordinary integration, regenerate
   native artifacts, and run current exact-tree checks. The earlier merge-tree
   observation had zero text conflicts but is not a later integration result.
3. Preserve original independent lane reports, their actual attempts and bindings.
   They are local observations; final P05 context, QA, corroboration and strict
   SHIP remain the integration coordinator's current-tree responsibility.
4. Select release metadata only after the version slot and actual code are known.
   The portfolio coordinator reports its authorized `jokerman89` publication
   route is now verified and owns publication through that route. This session
   must not try the injected/app identity or duplicate publication. Do not
   inspect, switch or recover credentials.

## Interrupted checks

The host cleared final reviewer `08b772fd-f505-45b0-b12f-16ef18ee9378` and shell
77 during the last bounded step. The P05 entry last showed 53 passing tests and
one in progress; it did not return a 117-test verdict. Keep it interrupted.
Recovery reviewer `010f0e08-076c-4683-8b28-1146251104be` reviewed only the existing
final fixes at `17f70f52` (SPEC PASS, QUALITY PASS with one display-only P3).
The same reviewer passed its correction at `f01294db`, including 17 adaptive
and 41 MARS tests. It did not repeat the whole audit or P05 suite.
The full 117-case P05 entry remains REQUIRED before merge, through the final
PR's full hosted matrix after source acceptance and the native1a/patterns join.
No local duplicate is requested while those streams share this host.
No additional pilot, adjacent work or broad benchmark should start while waiting
for native1a/patterns. Preserve final evidence and resume only the required
post-integration delta review.

T12 remains unchecked because the current-main join, native regeneration,
required hosted matrix, current shared release evidence and publication are
not completed. Its local source review and durable handoff are complete.

No CyberGym task, exploit, container or leaderboard submission ran. The optional
scorer reads imported receipts only. The small live toy pilot did not outperform
the generic baseline; use matched held-out real tasks before claiming an edge.
