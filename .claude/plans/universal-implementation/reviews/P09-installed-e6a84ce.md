# P09 installed-source closure review

**Verdict: scoped SPEC PASS, then eligible QUALITY PASS.** No actionable findings:
P0 0 / P1 0 / P2 0 / P3 0. This is SAME447's independent review of the released
installed-source unit, not acceptance of whole P09, A09/A17 parents or all role/client
combinations. The reviewer changed no implementation, test or owner report.

## Frozen scope

Reviewer: `447d97f5-7919-4433-8f65-a64016c0dbdf`. Authority is the P09 card's
"Installed-source closure after P10 integration" at
`f7cbe5bc55ade50117ab040334f9a7b6438724b4`.

| Identity | Exact value |
|---|---|
| Sole product base | `860da27c5e447a5a8a34b0ccc67f3f88af4f02ac` |
| Product | `e6a84ce634ce5a5cb07600430ed809bc09fce1c3` |
| Product tree | `ad5a801de38c36126aeff5b514e4f0c5f3ea8e84` |
| Report-only direct child / review parent | `0247a8675495dc9f0d928260361649bd9a081ff0` |
| Frozen child tree | `57797ae3f878e65eadf5decd645ceeb48cec5e32` |
| Owner report Git/LF SHA-256 | `e94d27d0528f8269822f7e706d44641e73d723f997e72b58c2a1d1c6aa14c4d9` |

Verified the exact checkout, clean index/worktree, ancestry through the release and
`8754515a`, and all seven changed paths below. Read the complete installed append,
owner report lines 1217-1397; its original 1216-line prefix is preserved. The child
changes only the report, preserves the product's 1350-line report prefix, and retains
all six test blobs/modes, including the new shell entry's `100755`.

| Reviewed path | Selected purpose |
|---|---|
| `tests\integration\domain-installed-consumers.py` | Actual installation, installed imports/CLIs, eight cases and cold fixture |
| `tests\integration\domain-installed-consumers.sh` | Ordinary executable entry |
| `tests\integration\installed_consumer_checks.py` | Shared mandatory-control and fresh-shell profile assertions |
| `tests\integration\domain-result-handoff.py` | Optional external evidence root and selector-free mode |
| `tests\integration\domain-module-consumers.py` | Positive complete composition before missing-domain refusal |
| `tests\integration\copilot-kit.py` | Existing callers reuse the shared assertions |
| `.claude\plans\universal-implementation\reports\P09.md` | Frozen evidence, claims and limitations |

Accepted role/content, data, module, N1 and finite-effect reviews were not reopened.
The delta changes no installer, provider, production helper, schema, role or module
body. This review adds only this report to the frozen child.

## SPEC: selected installed obligations

| Released obligation | Result and concrete evidence |
|---|---|
| A09.5 installed discovery and data handoff | PASS. Both real accepted installation surfaces discover all five modules plus full-engineering-pass. Imports resolve inside the resulting installation. Removing its domain helper refuses a target decoy; restoring it restores the positive case. See `domain-installed-consumers.py:103-141`. |
| A09.5 identity, filenames and interruption | PASS. Original grouped package/leaf/profile identities survive real producers/readers; wrong package, parent/leaf omissions, draft maps and Windows aliases/traversal refuse. Missing, failed, error, unknown, zero-test and skipped required work cannot be hidden by score 100. The started-but-incomplete case does not replay. |
| A17.5 installed receiver and cold example | PASS within this unit. The selected installed ContractTestArchitect/design-only pair works; wrong role or execution mode refuses. The actual original cold actor chooses the unmet TQ checkpoint, supplies a useful compatibility design and refuses clearance. It is not a registered named role or executed compatibility test. |
| Required reuse and scope | PASS. Existing domain cases are reused, and both callers consume the same controls/profile helper. The older copied-source callers remain explicitly regression coverage. No new dispatcher, result contract, provider or policy implementation was introduced. |

The missing-domain test now proves the complete positive summary before removing SC
(`domain-module-consumers.py:159-171`); its negative is not a baseline that always
fails. The shared helper checks mandatory pass/fail/unverified using the real schema
and verifies stable fresh-shell profile identity, same-mtime input drift refusal,
unchanged selected pin and successful restoration
(`installed_consumer_checks.py:20-92`).

## Independent execution and eligible QUALITY

Both runs used the committed ordinary shell entry, not a copied product tree. Each
performed the real install, initial/final installer checks, shared controls/profile
checks, eight domain methods and cold preparation. Every suite had zero skips.

| Reviewer-owned fixture | Surface and outcome | Measured domain worker |
|---|---|---|
| `C:\li-p09-447\f\n` | Approved PowerShell 7.6.6 native install/check: all exits 0; 8/8 PASS | 85.604s |
| `C:\li-p09-447\f\l` | Accepted `li-lifecycle scaffold init/check --copilot`: all exits 0; 8/8 PASS | 85.283s |

The eight cases cover installed discovery/removal, original grouped IDs/decoys,
wrong/draft/missing identities, complete-to-missing composition, required-result
failures/zero/skips, interrupted non-replay, receiver mismatches and portable paths.
Recorded expected refusal exits were 20 instances of 2 and 11 of 3 on each surface;
these are negative evidence, not successful handoffs. Native/lifecycle installations
contained 533/441 files; maximum installed paths were 105/110 characters and maximum
whole-fixture paths were 218, below the asserted 235 budget.

QUALITY also passed the two changed existing Copilot callers
(`test_installed_review_controls_use_real_schema_and_reject_required_failure` and
`test_joined_installed_profile_is_pinned_across_fresh_shells_and_detects_drift`):
2/2, no skips, 305.761s. The default source-backed composition caller passed 1/1,
no skips, 19.698s. These are regression checks, not additional installed/native
acceptance. Five changed Python files passed Python 3.9 grammar parsing; the shell
entry passed Bash syntax checking. Actual execution used Python 3.11.9 on Windows.

Source/test inspection and these discriminating checks found no actionable quality
defect. Before and after execution, all 1,128 frozen tracked files matched their
original raw-byte seals and the checkout remained clean.

**Retained reviewer failure:** the native suite passed, but its first private
collector exited 1 because it incorrectly required the owner's raw manifest hash.
Native installation preserves physical checkout EOLs. Read-only reconciliation
proved identical 521 managed paths and each inventory's matching actual bytes:
346 files differ solely by UTF-8 CRLF versus LF, with no normalized-content
difference; the other files match raw bytes. The lifecycle's 459 managed entries
match without normalization. The failed wrapper logs remain; the native suite was
not replayed to replace them. This was a reviewer oracle correction, not a product
finding or silent normalization of source.
The report-only pre-commit check also rejected CRLF in this newly authored report;
only this report was formatted to LF. Its failed check and pre-format bytes remain.

## Original cold evidence and semantics

Independently verified the owner's retained r4/r5 receipt, inventory, argument,
environment, exit and stream evidence. For r1, read the actual target, exact installed
guidance, caller transcription and receipt. The receiver preserves
`specs/chosen/work.json`, P09/T014/T001 and the synthetic-strict generation-1 profile.
It finds TA declared/unreviewed and TQ start present/result absent, chooses
`tq/contract_tests_complete`, and does not substitute a historical result or checkbox.

The original response distinguishes strict A from tolerant B and omission from null
and value. It identifies A's nullable/value addition as breaking, orders an adapter
or versioned response before producer rollout, and requests real serializers,
deserializers and versioned consumer/provider contracts. Its matrix is explicitly
predicted design. Unknown versions remain blockers; nothing is averaged into
compatibility or release acceptance. The actual installed post-read summary is
still exit 3 for the missing required result.

The existing actor was `cd1837f5-080a-42b9-90af-9c7dc484c067`, a generic source-guided
explore context. Direct live retrieval was unavailable to this reviewer. Subsequently
verified the owner's narrow original host export: seven boundary events and 30
read-only operation starts (29 views and one search), original invocation/result
binding, raw-line hashes and recorded configuration `claude-opus-5.5`, max,
long_context. No actor was resumed or newly launched. The original extracted
response SHA-256 is
`fffb13c6db59608da9c9bb3f3d7f75750b19dc34d57e70673682bb7d9b7dca25`.
The host-export manifest SHA-256 is
`1f08b76331707493c5cb311a9eaef7bd4083bd26267e5fb50ac5cad9e457d418`.
This is verified original event-export evidence, not a signed host attestation.
The initial caller extraction guard failure and earlier retrieval limitation remain
recorded; neither is rewritten as a successful live retrieval.

## Evidence and limits

Private evidence is retained under SAME447's
`files\p09-installed-review`: intake/source seals, owner verification, original host
events verification, native/lifecycle results and inventory comparisons, regression
logs and the final delivery receipt. Original owner evidence remains at
`C:\li-p09-installed`; the r1 fixture and installed guidance were sealed unchanged.

Synthetic HOME/USERPROFILE/AppData/XDG/temp roots, PATHEXT and Git discovery ceilings
were explicit; process streams were preopened. No inherited `LINTEL_*` selector was
injected into installed runs. Accepted bootstrap-derived exports are not injected
selectors. No real profile, network, dependency installation, global configuration,
denied PowerShell 5.1/jq retry, old finite effect or native actor replay was used.

The suite proves installed process/data/transport behavior with synthetic observations,
not domain-service correctness or semantic truth merely from schema validity. The cold
actor ran no shell, writes or tests. There is no full-suite, Python 3.9 runtime,
other-OS, native registration, all-role/client, live API/database/deployment or corporate
policy certification claim. Earlier failures and accepted-unit limitations remain.
Original-leaf/compound acceptance and any subsequent publication stay coordinator-owned.
Any later P10 payload change requires revalidation on that corrected base.
