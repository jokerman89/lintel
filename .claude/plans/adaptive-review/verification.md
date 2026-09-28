# Adaptive review verification

**Status:** final local source review PASS; hosted integration gates remain open.
**Coordinator:** `d9057650-8028-439a-85da-5849b5470136`.
**Source freeze:** `f01294db59f4d6ca13d9c43745ef0df6c014f983`.
This includes both independently reviewed lanes and the final-review correction
of a MARS metadata-downgrade flaw. The bounded recovery review passed at
`17f70f52` with one display-only origin-reference regression; `f01294db` fixes
that regression and passed the same reviewer's narrow recheck.
Final SPEC PASS and QUALITY PASS have zero open P1, P2 or P3 findings;
see [the independent report](final-review.md).
No uncommitted product edits remain.

## Attributable implementation

| Package | Isolated source | Independent review | Integrated source |
|---|---|---|---|
| P1, T1-T4 | Session `56c89e70-0422-47d9-a28d-c138830e7ee6`, branch `jokerman-microsoft-review-context-engine` | `09fa60d1-964d-4ede-a1f6-5c2a39699aaf`: spec then quality PASS; diagnostics and parser corrections re-reviewed | `0993b682`, follow-up `c849f9a7`, ordinary merges `54919b03` and `8707d732` |
| P2, T5-T6 | Workspace `afe3d52d-dda8-4dba-9da2-a4b92d524911`, reported execution context `b10ea612-ce4b-4ce8-9123-35f32238dbca`, branch `jokerman-microsoft-review-evaluation-engine` | Same independent reviewer: a1 quality FAIL for malformed-input crashes; a2 spec/quality PASS after correction | `d6c6f277`, ordinary merge `d8dd2d57` |
| P3, T7-T10 | Coordinator-owned files only | `08b772fd-f505-45b0-b12f-16ef18ee9378` found a MARS metadata-downgrade P2; recovery reviewer `010f0e08-076c-4683-8b28-1146251104be` verified its fix and the display-only P3 correction, SPEC/QUALITY PASS | `454fa4b8`, `17f70f52`, `f01294db` |

Worker reports and lane reviews are under `swarm/reports` and `swarm/reviews`.
Raw file snapshots, host-observed separate contexts and Git attribution are
different evidence. A worktree is not a sandbox. These records are local
observations, not the shared P05 release decision, QA or clearance.

## Actual checks

| Check | Observed result | Boundary |
|---|---|---|
| `python -B tests/unit/review_context.py` | 35 tests PASS on integrated P1 | Windows, Python 3.11.9; 3.9 grammar only |
| `python -B tests/unit/review_evaluation.py` | 38 tests PASS on integrated P2 | Synthetic input/arithmetic and real CLI cases; no benchmark execution |
| `python -B tests/unit/review_method.py` | 21 tests PASS | Existing behavior and v2 body/metadata integration |
| `python -B tests/unit/adaptive_review.py` | 17 tests PASS on `f01294db` bytes, plus the focused relative-brief/origin/cleanup regression | Mandatory versus advisory, original body, legacy rewrite refusal, cleanup, malformed input, depth, source provenance, parity and reference sizes |
| `python -B tests/unit/mars_contract.py` | 41 tests PASS | Actual local MARS state/content checks, no paid panel |
| `python -B tests/unit/mars_hooks.py` | 3 tests PASS | Canonical workflow joins, not native discovery |
| `python -B tests/integration/adaptive-patterns.py` on this branch | 1 test PASS, provider explicitly absent | Not an empty-pattern or real-provider claim |
| Same integration check in isolated pinned patterns worktree | 5 tests PASS | Real provider on synthetic local locks, not private packs or stack acceptance |
| BUILD, SC and ADR-number shape scripts | PASS | Structure only |
| `python -B tests/shape/native-command-surface.py` | PASS after the optional-path wording correction; final `--json` run also passed with the complete capture artifacts | Existing historical observation remains; no legacy evidence rewritten |
| `python -B bin/li-catalog.py --check` | PASS | Skill metadata unchanged |
| `python -B bin/li-copilot.py check --target . --source .` | PASS, 21 managed files | Baseline generator integrity, not pending native1a discovery |
| Baseline generator in-memory resource closure | Seven new review dependencies present | No target files written; repeat with actually landed native1a generator |
| `bash bin/li-compat-audit --against 49f2d152 --output adaptive-review` | GREEN | Its four legacy checks do not validate Python API/method-version semantics; those have explicit tests above |
| `git merge-tree --write-tree --name-only HEAD 64338b6c` | Exit 0, no textual conflicts; tree `f08e1c8c46d03230556e9e10202a453f44db1953` | No branch moved or stack accepted; repeat for final current-main integration |
| In-memory mutation restoring the pre-fix MARS legacy-metadata bypass | New regression failed exactly once as expected; zero unexpected errors | Demonstrates that the regression distinguishes the original flaw; no product files changed |
| `bash tests/shape/no-swedish.sh` | PASS | Public language contract only |

The provider observation used exact commit
`64338b6c9fc30fb3618cc9f46b66d8b0d2ab1e7c`, product `fdb9f27b`.
The later `82e97d74` patterns update is metadata-only according to its owner.
The test generated real locks through `resolve`, `build_lock`, `write_lock` and
`map_lock`, then exercised the adapter's real `verify_lock`, `project_package`
and `review_coverage`. It observed settings/clause preservation, zero asset reads,
missing mandatory evidence returning `review-unmet`/CLI exit 7, revocation
stopping before projection, and fallback never becoming empty.

Two initial test-fixture mistakes were corrected rather than accepted as provider
failures: the provider correctly required an existing destination directory, and
a fallback profile correctly required an explicit diagnostic. The final run was 5/5.
No frozen patterns source, private pack, held resource or original evidence changed.

The existing unchanged P05 regression suite was started under a synthetic parent
environment. A host interruption cleared shell 77 before a final verdict: the
last retained output shows 53 completed passing tests and a subsequent test in
progress, out of 117 defined tests. This is **interrupted, not PASS**. It is not
being duplicated as another full run while native1a/patterns integration is pending.
The portfolio coordinator explicitly retains the complete 117-case entry as a
**required pre-merge gate in the final PR's full hosted operating-system matrix**.
The local partial run and targeted tests do not waive or replace that gate.
No Linux/macOS or hosted CI result,
new native-client discovery, private company-policy acceptance or release is claimed.

The same interruption cleared the final reviewer's runtime handle before its
correction recheck produced a durable final-review file. Its earlier SPEC PASS
and QUALITY CHANGES REQUESTED remain history. A separate bounded recovery
review assessed `17f70f52`, wrote `final-review.md`, then rechecked the
display-only successor `f01294db` with 17 adaptive and 41 MARS tests plus
the relevant synthetic origin probes. It independently returned SPEC PASS
and QUALITY PASS. The missing original recheck is not treated as evidence.

T1-T11 are complete locally. T12's source-review and handoff portions are
complete, but its final current-main/native1a/patterns integration, full hosted
matrix including all 117 P05 cases, current shared evidence and publication
remain with the portfolio coordinator. The unchecked T12 records that boundary,
not an outstanding source defect.

## Small live review pilot

Eight self-authored toy snippets had a prewritten oracle: four contract defects,
two clean cases and two safe decoys. Both actual reviewer calls used Opus 5.5,
high, long_context, view-only, one complete subject, no execution and no other
file access. They ran in separate contexts:

- Baseline generic prompt: `37c9dd23-c700-4b50-8ef5-44ad28a97692`.
- Actual adaptive packet: `2e2f7784-f347-4942-9859-a006f3d5dc01`.

Both found all four defects and produced zero false positives on the four
clean/decoy cases. The candidate answered all 13 selected questions and the
shared checker accepted the report's structure and returned `fail` for its
four P1 contract defects, with `release_clearance: false`.

The offline evaluator consumed the manually mapped observations against the
prewritten canonical inventory digest
`50e9652e51ff91d4c93ba1102409bfddbe75e0e62d461b4b0a82b5cf394ef60f`.
Recall and precision were 4/4 for both, negative-case handling 4/4 for both,
completion 8/8 for both; all deltas were zero. No token, per-case latency or cost
measurement was supplied or invented. Scorer input is explicitly synthetic
because these are toy cases; actual host calls are established by their separate
receipts, not by the scorer's data classification.

This is a small functionality observation, not a statistically controlled
performance benchmark. The oracle was authored by the coordinator, the cases
are easy, there was one run per method, and real systems/costs were not measured.
It demonstrates **no detection advantage** over the baseline. It cannot support
a CyberGym score, ranking or MDASH/Ultrareview parity claim.

The source, fixed oracle, frozen candidate packet/meta/report and both imported
run records persist in the coordinator's session artifact area. A separate
benign local execution confirmed all eight toy oracle observations afterwards;
neither reviewer executed them or saw the answer key.

## Overhead observation

A 100-iteration hot-process local depth/render/metadata probe observed a
1.909 ms median and 176.209 ms maximum while this shared host was busy. The
then-current 11-question, three-character-subject packet was 12,507 UTF-8 bytes.
Subsequent renderer reuse reduces repeated JSON presentation. This measures
only local helper work, not startup, repository scanning, inference or end-to-end
review latency. No model or network call occurred in that probe.

All on-demand review references remain below 20,000 bytes. Canonical entrypoint
changes are small links/method joins, not an embedded company knowledge corpus.
