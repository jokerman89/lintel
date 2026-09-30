# Plan: C-01.blob-reads

**Status:** APPROVED by the existing bounded implementation grant.
**Specification:** [spec.md](spec.md).
**Scope:** optional selected-blob cache prefetch; one writer in a new worktree.

## Profile and authority

An explicitly selected new work context is bound to this worktree's own
`.claude/runtime/lintel-home`, source and target. It resolves the actual
neutral `_default` 1.0.0, required policy `not_required`, compliance advisory
and no hooks. No prior Adaptive profile or clearance transfers here.
The current generation/reference is retained locally with verification evidence.

Local implementation, synthetic fixtures and ordinary feature commits are
authorized. Publication, hosted CI, PR, main integration and cleanup are not.
No additional approval interview or model/agent launch is needed.

## Work package

| Package ID | Outcome | Leaf IDs (dependency order) | Owner / edit boundary | Dependencies | Acceptance evidence | Review |
|---|---|---|---|---|---|---|
| C-01.blob-reads | Fewer selected-blob Git processes with identical snapshots and errors | C-01.blob-reads.1, C-01.blob-reads.2, C-01.blob-reads.3 | existing root implementer; lib/review_contract.py, tests/unit/review_evidence.py | none | differential results, exact errors, process counts and focused regressions | substantive |

## Original scoped tasks

- [x] C-01.blob-reads.1 Add the optional batch prefetch without changing strict consumption.
- [x] C-01.blob-reads.2 Demonstrate differential behavior, fallback and process counts.
- [x] C-01.blob-reads.3 Run applicable regressions and obtain independent implementation review.

### C-01.blob-reads.1: Prefetch

**Requirements:** R1-R6.
**Files:** `lib/review_contract.py`.
**Dependencies:** none
**Acceptance:** private helper, unchanged mode values, one cache-initialization
replacement after selection walk; untouched strict fallback and entry loop.
**Verification:** new `BlobBatching` class in the existing evidence test file.
**Evidence:** the 11-case `BlobBatching` selection passed. Independent AST review
confirmed that the original strict read and entry loop are unchanged.

### C-01.blob-reads.2: Differential proof

**Requirements:** R1-R6.
**Files:** `tests/unit/review_evidence.py`.
**Dependencies:** C-01.blob-reads.1
**Acceptance:** the exact fixture matrix in spec.md; compare both successful
full JSON and first error with prefetch patched empty, never rewritten expected
values. Observe actual `Popen` counts and request bytes.
**Verification:** `python -B tests/unit/review_evidence.py batching`.
**Evidence:** full snapshot/canonical JSON and first-error comparisons passed.
Actual Popen observations for twelve distinct selected blobs were 18 original
versus 7 batched Git processes, with zero individual batched-path blob calls.
Untracked-only selection remained 6/6 with no batch. Complete serialized output
pairs were byte-identical. Protocol doubles remain distinct from real Git cases.

### C-01.blob-reads.3: Regressions and handoff

**Requirements:** R7.
**Files:** owned verification/handoff record here; no additional product scope.
**Dependencies:** C-01.blob-reads.2
**Acceptance:** smallest applicable existing review/mandatory/MARS/adaptive
selections pass; independent Deep implementation review reports actual findings.
Retain failed observations and host limits. Provide exact head/tree, profile,
diff, equality and process-count receipts for later aggregate review.
**Verification:** bounded selectors from the existing test entrypoints; no full
runner/stress/live/model/network operation. Hosted verification remains Master-owned.
**Evidence:** 150 scoped local tests passed, zero failed/skipped: 11 new batching,
117 existing P05/control/hook, 11 MARS binding, 7 adaptive panel/packet and 4
required-profile bridge cases. All command receipts retain unchanged source/test
hashes before and after execution. Independent Deep SPEC then QUALITY passed.

## Review

On 2026-09-29 the independent Deep implementation review returned SOURCE
CANDIDATE PASS: SPEC PASS, then QUALITY PASS, and neutral-profile compliance PASS.
The reviewer authored the design, not the implementation; independence is
declared, not authenticated. P0/P1/P2 counts were zero. No new ADR was needed:
public behavior is unchanged and the existing reader remains authoritative.

The four source-review observations below are retained as history, without
rewriting the original decision. Final integrated dispositions follow them.

Retained observation F1 (P3): normal completion may kill the child just before
its normal exit; the process double does not separately assert the already-exited
no-kill branch.

Retained observation F2 (P3): an exceptional failure to kill an owned child could
escape prefetch or block cleanup. This double-fault case was not reproduced.

Retained observation F3 (P3): macOS command-line Unicode precomposition may
collapse the index-only NFD fixture name; this was expected, not observed on the
local Windows host.

Retained observation F4 (P3): the full `mars-contract`, `mars-hooks`,
`review-method`, `universal-trusted-tools`, `planning-consolidation` and
`no-merge-without-review` suites remain a Master-owned hosted verification
obligation; the scoped local selection is not a substitute.

The primary private verification summary, process-count/output artifacts,
command receipts, complete independent report and preserved failed observations
remain under the implementing target's ignored runtime, not in a fresh clone. The initial
newline-index fixture failure and two rejected handoff transports are history,
not passing observations.

Runtime evidence is Windows/Git 2.53.0/Python 3.11.9 only; Python 3.9 was checked
for syntax, not executed. No wall-time gain is claimed. The new explicit profile
and full required policy were verified without rebinding or changing the home.
Original Adaptive preservation is separate evidence, not acceptance of this code.

The local implementation and source review were followed by independent
canonical aggregate review, current QA, actual host corroboration and SHIP.
The exact integrated candidate passed hosted run
[36642145033](https://github.com/jokerman89/lintel/actions/runs/36642145033):
23 successful jobs, 549 strict script-file executions (183 per OS), no failed,
skipped or partial entries. C-01.blob-reads landed in `5df540ce` (0.13.5).

F4 is closed at hosted script-file level, not by fabricated per-method output.
The final reviewer narrowed F3: the index-only Unicode fixture is covered at
file level across the hosted matrix; worktree-created NFD names remain
unobserved. F1 and F2 remain disclosed. The Windows method-level observations
above are still their original local evidence; no wall-time improvement or
universal Python-version coverage is claimed.

C-01 MARS re-snapshot frequency, C-02 ignored-file semantics and filesystem path
cost remain OPEN; no wider completion is claimed.
