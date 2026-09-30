# Cold handoff: DR-36.header-core

**Status:** APPROVED for the bounded local implementation.
**Work map:** [work.json](work.json).

Read [spec.md](spec.md) and [plan.md](plan.md), retaining original leaves
DR-36.header-core.1/.2/.3 under parent DR-36 / LIB-04. Work only in the new
isolated feature tree rooted at exact base
`a017e548cf7870b4043f5d896d8f5df296bbbae1`.

Extract common header parsing/validation into the pure trusted sibling
`lib/review_headers.py`. Keep original public adapters, error callbacks,
signatures, input/error order and returned identities. Do not merge schemas or
change the separate conversion/rendering functions. Preserve literal v1 bytes,
custom schemas, HEADER_KEY, Python 3.9 and standalone MARS without full REVIEW.
Declare the new helper in the portable MARS resource closure.

Use frozen original functions as differential oracles, not updated expectations.
Run the new header classes first, then bounded existing review/MARS/closure tests.
All processes need explicit synthetic parent homes and an owned output location.
The worktree's own P07 context is required; old Adaptive/C-01 profiles and evidence
are history, not authority. Stop the affected work if behavior would change.

Freeze product bytes for the existing independent Deep reviewer. Reviewer writes
only its report. After actual SPEC then QUALITY pass, make an ordinary local
commit and deliver exact source/test/evidence/profile hashes and limitations.
No new actor/model/dependency, full local matrix, remote operation, version bump,
held scope, old worktree mutation or cleanup. Master owns aggregate and hosted
validation and publication; only DR-36.header-core can be reported complete.

## Current state

The local extraction, compatibility proof and independent source review are
complete, including the coordinator-required F1 helper-admission correction
and same-reviewer recheck. See plan.md for accepted F2/R1 limits and additive
F3 evidence clarification. Do not repeat completed local work or treat source
acceptance as hosted, aggregate or publication clearance.
