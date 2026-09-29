# Plan: architecture enforcement claims

Status: APPROVED for a bounded documentation correction under the existing
report-driven remediation mandate. Base: `5df540cefb5278b4f9e4607d8554bb261bd5d376`.
The base's hosted delivery remains a separate prerequisite for publication.

One task, hotfix route: SENSE, BUILD, REVIEW, SHIP. No design or structural change.
Planning estimate: approximately 5,000 tokens, uncalibrated; not measured usage.

| Package ID | Outcome | Leaf IDs | Owner / edit boundary | Dependencies | Acceptance evidence |
|---|---|---|---|---|---|
| P1 | Architecture distinguishes the existing check from a general guarantee | W1-9.claims | coordinator; docs/architecture.md, .claude/plans/architecture-claims/spec.md, .claude/plans/architecture-claims/plan.md, .claude/plans/architecture-claims/prompt.md, .claude/plans/architecture-claims/work.json | none | R1-R3 source comparison, linked-path check, existing language/native checks |

- [x] W1-9.claims Correct the two unsupported enforcement claims.

Requirements: R1-R3. Change only the neutrality paragraph and the shape-tier table.
Compare both against `tests/shape/no-swedish.sh`; preserve its exact behavior.
Verify the relative link, unchanged scanner hash, English prose and native drift
with the existing checks. No new test dependency or full matrix is required for
this documentation-only slice.

## Review and evidence

Mechanical coordinator review, SPEC then QUALITY, with no independent-review
claim. Record actual document/check outcomes in the shared QA contract.
Use this worktree's own neutral profile, never the base candidate's reference.
No mutation of the frozen base, private histories, held work or shared main tree.

No general publication guard is implemented or declared passed by this task.

The coordinator's mechanical SPEC review passed R1-R3, then QUALITY passed:
the change names the actual check and its limits without weakening the intended
boundary. This is self-review, not independent review. The link and unchanged
scanner were checked; the work-map reader, existing language check and native
drift check exited 0. A final prose refinement limits the exemption wording to
functional data and generated documents, matching the source exactly.
These local observations do not authorize publication of an unverified base.
