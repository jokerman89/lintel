# Plan: DR-36.header-core (size: S; schema: flat)

**Status:** APPROVED by the bounded coordinator grant.
**Specification:** [spec.md](spec.md). **Work map:** [work.json](work.json).

## Summary and plan signals

Deduplicate only the common header parser and validator while preserving the
two family contracts byte-for-byte. Three original leaves, one package, one
existing implementer; phases are implementation, differential verification and
independent source review/handoff. The S whole-cycle default prior is 12,000
tokens, uncalibrated, not measured usage or a price. No new orchestration is needed.

## Profile impact

A new explicit source/target-local context resolves `_default` 1.0.0 with actual
required policy `not_required`, source `bundled-neutral`, applicability
`not_applicable`. Compliance is advisory, hooks are empty. The complete new
reference and roots are private evidence; no previous context is reused.

## Work package

| Package ID | Outcome | Leaf IDs (dependency order) | Owner / edit boundary | Dependencies | Acceptance evidence | Review |
|---|---|---|---|---|---|---|
| DR-36.header-core | Shared parser/validator, unchanged family behavior | DR-36.header-core.1, DR-36.header-core.2, DR-36.header-core.3 | existing implementer; lib/review_headers.py, lib/review_method.py, lib/mars_contract.py, tests/unit/review_method.py, bin/li-copilot.py, skills/review/references/method.md | none | full differential results, consumer/closure checks and source review | substantive |

## Original tasks

- [x] DR-36.header-core.1 Extract the common parser and validator.
- [x] DR-36.header-core.2 Prove differential and installed-consumer compatibility.
- [x] DR-36.header-core.3 Obtain independent source review and hand off the candidate.

### DR-36.header-core.1: Shared implementation

**Requirements:** R1
**Dependencies:** none
**Files:** `lib/review_headers.py`, `lib/review_method.py`, `lib/mars_contract.py`,
`bin/li-copilot.py`, `skills/review/references/method.md`.
**Acceptance:** the pure helper owns common loops/checks; original signatures,
`HEADER_KEY`, exceptions, error order, custom schemas and rendering are unchanged.
**Verification:** baseline differential fixtures first, then shared-core tests;
inspect unchanged converters/renderers and schema bytes against the exact base.
**Evidence:** independent specialization/AST proof and seven differential core
tests confirm the common parser and validator preserve the original behavior.
Family schemas, converters, renderers, metadata and method sections 1-5 remain
unchanged. The new dependency has the repository-standard admission guard.

### DR-36.header-core.2: Compatibility proof

**Requirements:** R1, R2
**Dependencies:** DR-36.header-core.1
**Files:** `tests/unit/review_method.py`.
**Acceptance:** all spec fixtures agree with frozen baseline oracles; the two real
CLIs, source-relative loading and installed resource closure remain functional.
No existing expected value changes.
**Verification:** new header classes first, then the smallest relevant existing
review-method, MARS contract/hook and closure/native checks in synthetic homes.
**Evidence:** the initial 54 scoped tests and native consistency check passed.
After F1, 35 affected tests passed: two guard, seven core, two closure, fourteen
REVIEW and ten MARS consumer cases. These overlap the initial selection and
are not 89 distinct tests. Actual Windows symlink/directory refusal and controlled
reparse classification are distinguished. Raw logs, argv and pre/post source
hashes are retained in the owned private evidence.

### DR-36.header-core.3: Review and handoff

**Requirements:** R3, R4
**Dependencies:** DR-36.header-core.2
**Files:** `.claude/plans/shared-header-core/plan.md`,
`.claude/plans/shared-header-core/prompt.md` and owned private evidence only.
**Acceptance:** existing Deep reviews frozen source SPEC then QUALITY, with no
repair writes. Return source/test/profile receipts, patch, original leaf status
and limits; use one ordinary local commit only after passing checks and review.
**Verification:** original map, current P07, exact source/evidence hashes, scoped
diff and actual separate reviewer report. No source review impersonation.
**Evidence:** independent Deep SOURCE SPEC then QUALITY passed. The same reviewer
then passed the required F1/affected-test recheck, retaining the initial report.
The two reports establish SOURCE CANDIDATE PASS for the revised bytes, not
aggregate, hosted or publication clearance. The coordinator accepted the
remaining optional fixture limitation; exact records accompany the handoff.

## Review and retained boundaries

ADR-0036 and ADR-0040 keep one reviewer method but distinct family contracts and
independent entry points. Extraction is not schema consolidation. No new ADR
or changed approval policy is proposed. Parent DR-36/LIB-04 and all unselected
recommendations stay open. Hosted validation and publication stay Master-owned.

### Source review disposition, 2026-09-30

The first independent SOURCE SPEC and QUALITY reviews passed with three P3
observations. The coordinator requires F1 before commit: apply the established
trusted-sibling guard to refuse linked, reparse-point or non-regular helper
files before executable loading, with narrowly scoped inert refusal fixtures.
This is dependency admission only; all original parsing, validation and normal
file behavior stays bound to the original acceptance.

F2 (installed closure test cost and unit placement) is accepted as disclosed;
no test relocation or shard change is released. F3 is clarified in additive
evidence: distinguish the pre-section-7 prefix hash from the actual sections
1-5 output. Preserve the initial observations and decision unchanged. Revised
product bytes require the same reviewer's bounded F1/affected-test recheck.

### Final local disposition

F1 is corrected and independently rechecked: linked, reparse-point and
non-regular helper files are rejected before loading. This did not change
parser/validator or normal-file behavior. The inert red/green observations and
the initial review remain unchanged history.

F2 remains accepted as disclosed: the installed closure test takes about
165 seconds on the observed Windows host and remains in the unit tier. No
performance improvement, shard change or relocation is claimed.

F3 is clarified by an additive receipt. The original hash measures the whole
prefix before section 7; the actual `method_sections()` output (sections 1-5)
is separately recorded as 6,236 bytes, byte-identical to the base. No earlier
observation was rewritten.

The recheck's optional P3 R1 is accepted as a test-fixture portability limitation,
not an observed product defect. Its controlled symlink-mode fixture assumes
`Path.is_symlink()` routes through `Path.lstat()` in the CPython 3.9-3.12
implementation; newer-runtime behavior is unverified. Actual local execution
was Python 3.11.9 only, not every version in that range. The real Windows
symlink/directory refusal and the product guard remain proved.

Both independent records, the original and affected command receipts, exact
source/test hashes, unchanged current profile and mapping, and separate
old-worktree preservation evidence are retained under
`.claude/runtime/header-core/`. Windows runtime observations and Python 3.9
syntax checking do not establish Linux/macOS or whole-matrix acceptance.
Master owns hosted, aggregate, version and publication work. Only this local
DR-36.header-core slice is complete; parent DR-36/LIB-04 remains open.

## Integrated delivery

The local record above is preserved as the source handoff. The integrated
candidate `a3ec21ed` subsequently passed independent specification and quality
review, current QA, actual host corroboration and the shared latest-reader/SHIP
gate, then landed on main as 0.13.6.

The joined local batch ran nine commands and 93 unittest methods with zero
failures or skips on the exact tree later committed. Hosted run
[36657454823](https://github.com/jokerman89/lintel/actions/runs/36657454823)
passed 23 jobs and 549 strict script-file executions (183 per OS), without
failed, skipped or partial entries. Hosted results are script-file level;
local method-level and runtime-version limitations remain distinct.

The installed bundle includes `lib/review_headers.py`; update it through the
existing adapter rather than copying a partial dependency set. The product
version change requires the existing explicit profile rebind and fresh
dependent evidence. One non-blocking changelog wording observation remains:
a trusted installed bundle can itself reside inside a target repository;
the prohibited behavior is selecting arbitrary target code as a fallback.

This completes DR-36.header-core, not the distinct schemas, registry-freshness
recommendation or broader DR-36/LIB-04 parent. The preserved runtime evidence
belongs to its producing targets and is not automatically available in a clone.
