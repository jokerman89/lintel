# P08 frozen partial independent review

**Date:** 2026-09-21

**Selected-subset SPEC:** FAIL

**QUALITY:** NOT STARTED

**Preservation/integration readiness:** BLOCKED

**Whole-P08 acceptance:** not requested and not granted

This is a distinct independent review, not the implementer's self-review. Reviewer
session: `74705f62-a856-4ab9-b62d-0bbd54048e2f`; implementer session:
`036fe896-b2de-4362-8db9-0c4697356afc`. No nested agents, product repairs, shared
plan/memory updates or P08 clearance record were created. The sole repository
output is this report.

## Authority and immutable selection

The checkout was verified clean at
`062ffc6cc0cfecee80646fda2a54bad4db837fad` before inspection and remained at that
revision through all product execution. Its sole parent is product
`8d477701bf05c545790d4c5fdbdc84945dd130db`, whose sole parent/control is
`f9685530c458b456021e30ddab699c03b49614ca`. Original integration baseline
`5c3e7533335eeae15556aeabba422bfdbbe07f46` is an ancestor. The `062ffc6` child
adds only `reports\P08.md`.

Review authority is the **Frozen partial review boundary** in `packages\P08.md`
at coordinator `1105ebeb4df3792c78437a74a5bd852bea96209d`, read directly from
that Git object. The selected `work.json` still maps the original spec, plan,
tasks and prompt; its plan owns the unchanged A-IDs. The original audited
A08/A10/A13 acceptance was read, as were the complete implementer report,
Copilot/Universal contracts, relevant memory and accepted ADRs.

Selection: A08.1-.5, refinements A08.2.a/b/c and A08.3.a/b/c, A10.1-.4 and the
explicitly advisory A13.3 option. A13.1/.2/.4 are intentionally deferred, not
missing implementation in a completion candidate. Artifact availability does
not release those gates.

Independent Git inspection confirmed **46 product paths, +2,747/-942**. Their
set exactly matches the complete enumeration in `reports\P08.md`. That product
footprint excludes this review and the implementer's report. Protected
P03/P04/P05/P06/P07 core and schema/provider paths were not changed by the product;
the released work-map reader and narrow `_context.sh` probe are owned P08 edits.
In particular, `bin\_audit.sh`, `lib\memory.sh`,
`bin\li-lessons-promote` and `lib\paths.sh` remain unchanged.

Separately attributed dependencies remain dependencies, not P08 authorship:

| Coordinator origin | Local dependency | Boundary |
|---|---|---|
| `e3799480` | `8a2429e631841358d05e8497422af546b59b57f9` | Metadata, stable subdivisions and context-probe ownership |
| `c8058497` | `acc728eadf3343e76b7ae37eb0dc411af84dad51` | Selected-analysis SHIP advisory sentence |
| `d53dc38` | `35aff7e31bf67b7bed6ed05f00d71565775d31a9` | Evidence CLI executable mode |
| `aa56a67` | `cce69c82fcea8de0c88af850c20d828cc5faf7fa` | Literal runner diagnostics |
| `935b640` | `f9685530c458b456021e30ddab699c03b49614ca` | Welcome/footer/parity oracle |

The shared Markdown provider is still Git blob
`0b3da55046358864fcd3075ba5bfb6c2348b1fec`. Independently reading the immutable
blob yielded 19,988 bytes and SHA-256
`331c1c62e932b5555089336d1fdcc7031f545780508f1d0f2e11bd9f2a7a8ebf`.
No P10 WIP was imported or inspected as permission to implement A13.

## Specification findings

**Counts: P1 = 2; P2 = 1; P3 = 0.** These are scoped specification findings.
QUALITY has no verdict or severity count because that stage did not start.

### F01 - P1: negated operations leave topic words eligible as write intent

- **Location:** `lib\orientator-routing.sh:79-82`; operation return at `:97-98`.
- **Acceptance:** A08.1, original A08 operation-before-topic/read-intent boundary.
- **Expected:** a prohibition cannot become SHIP authority because its subject
  contains `release`. An explicit subsequent explanation stays read-only;
  prohibition-only input remains a clarification/no-action case.
- **Actual:** `Do not change the release plan; explain it.` returns `ship`.
  `Do not build the release.` also returns `ship`. In both cases the actual
  consumers return `/li:cycle --from SHIP` and confidence `high`.
- **Cause:** after skipping one negated operation, `negated` is reset. The next
  matching subject token is accepted and returned before the later read request.
  The added conjunction handling does not cover this ordinary subject/clause case.
- **Required repair:** preserve negation and operation/topic boundaries across
  the clause; use safe clarification when ambiguous. Add these discriminating
  producer/consumer cases without losing the retained direct-mutation/IFS cases.
- **Confidence:** 10/10; independently reproduced, not inferred from strings.

### F02 - P1: a safety question becomes a high-confidence deployment route

- **Location:** `lib\orientator-routing.sh:34-44`, falling through to `:63-64`
  and `:97-98`.
- **Acceptance:** A08.1, requested question/read operation before deployment topic.
- **Expected:** `Is it safe to deploy this release?` requests assessment, not
  deployment. It must retain a read/clarification boundary.
- **Actual:** the producer returns `deploy`; the actual route is
  `/li:cycle --from SHIP`, confidence `high`.
- **Cause:** the question-prefix cases cover selected wh-words and `should`,
  but this interrogative reaches the action-token scan unchanged.
- **Required repair:** distinguish informational/safety questions from explicit
  action requests, retaining affirmative `Deploy the reviewed release.` behavior.
  Ambiguity must not be presented as high-confidence write intent.
- **Confidence:** 10/10; independently reproduced.

F01/F02 are remaining defects in the selected A08.1 delivery, not a claim that
both originated in product `8d477701`. Static comparison with `f9685530` shows
the earlier single-operation negation reset and limited question-prefix
approach already present; P08 extends that still-unaccepted routing work.
No parent routing suite was rerun. Unlike accepted P03/P07 dependencies, A08.1
itself was explicitly assigned for review and completion.

**No SHIP/deploy workflow was executed.** These tests call classification,
route selection and confidence only. They demonstrate an incorrect recommendation,
not an observed production mutation or proof that later permission gates were bypassed.

### F03 - P2: PLAN still directs ANALYZE to the global report path

- **Location:** `skills\plan\SKILL.md:271-276`, specifically `:275`.
- **Acceptance:** A08.3.c under original A08.3; selected analysis/report identity
  must follow the original work map rather than global history.
- **Expected:** PLAN delegates with the selected cycle's explicit analysis path
  and preserves its pointer/history, consistently with
  `skills\analyze\SKILL.md:17-20` and `:80-88`.
- **Actual:** the owned PLAN caller still instructs persistence to
  `.claude/runtime/state/analyze-report.md`. The new ANALYZE contract explicitly
  makes that old global path history-only. These shipped instructions disagree
  at the producer boundary and leave two initiatives without one consistent
  output-selection rule.
- **Required repair:** reconcile this caller with the selected-report contract;
  verify actual PLAN-to-ANALYZE selection/history, not only a fixture that manually
  creates already-correct per-initiative reports.
- **Confidence:** 9/10 for the instruction-contract contradiction. This was
  observed during the bounded source read, before the stop instruction. No
  live model execution, overwrite or false release clearance is claimed.

## Exact independent routing evidence

All six inputs below are preserved exactly, including punctuation. The private
probe called these actual functions for each request:

```bash
source "$LINTEL_SOURCE_ROOT/lib/orientator-routing.sh"
actual=$(classify_intent "$request")
workflow=$(match_workflow "$actual" cycle)
confidence=$(score_confidence "$actual" "$workflow")
```

| Exact input | Probe's expected intent | Actual intent | Actual workflow | Confidence | Result |
|---|---|---|---|---|---|
| `Do not change the release plan; explain it.` | `research` | `ship` | `/li:cycle --from SHIP` | `high` | FAIL |
| `Do not edit the deployment code; describe the release process.` | `research` | `research` | `/li:cycle --mode research-dive` | `high` | PASS |
| `Is it safe to deploy this release?` | `research` | `deploy` | `/li:cycle --from SHIP` | `high` | FAIL |
| `Do not build the release.` | `unclear` | `ship` | `/li:cycle --from SHIP` | `high` | FAIL |
| `Review the release plan.` | `review` | `review` | `/li:review` | `high` | PASS |
| `Deploy the reviewed release.` | `deploy` | `deploy` | `/li:cycle --from SHIP` | `high` | PASS |

The acceptance requirement is the safe read/clarification boundary, not a demand
to choose one enum where another safe clarification would be justified. The
three failures instead select explicit write routes with high confidence.

## Per-leaf specification disposition

PASS below is confined to the assessed mechanical or explicitly instruction-only
contract. It is not package integration, release or live-host acceptance. Missing
proof is UNVERIFIED; known unsatisfied dependencies/preservation keep acceptance
BLOCKED. No unassessed leaf is inferred green from the aggregate test result.

| Original/refinement leaf | SPEC | QUALITY | Evidence and remaining boundary |
|---|---|---|---|
| A08.1 | FAIL | NOT STARTED | F01/F02. Retained 54 assertions pass, but the independent six-case probe has three failures. |
| A08.2.a | PASS | NOT STARTED | r03: actual begin/idempotency, protected identity, interruption, failed writer, reader error, operator-field injection, framing and truncated-DONE cases. This does not close inherited checkpoint/bisect preservation. |
| A08.2.b | PASS | NOT STARTED | r03 actual footer distinguishes STARTING, BLOCKED, DONE and DONE_WITH_CONCERNS; selected-range next-phase case passes. Historical 46-assertion footer evidence was not rerun here. |
| A08.2.c | UNVERIFIED | NOT STARTED | Phase selector/range/no-duplicate cases pass and the single dispatch loop was read. Actual host invocation of that instruction loop was not observed. |
| A08.2 parent | BLOCKED | NOT STARTED | Mechanical positive evidence does not close the unverified orchestration and preservation obligations. |
| A08.3.a | PASS | NOT STARTED | r03: explicit original map/IDs, distinct bytes/warming, exact capacity boundary, missing inputs and P05 `bind_work`/progress preservation. Source reuses P04 parsing and P03 selection, not another acceptance hash. |
| A08.3.b | UNVERIFIED | NOT STARTED | Real P07 fresh-shell resume, required-policy drift, missing-pin no-recreation and target/map argument-refusal cases pass. No additional independent cross-target-transfer or forged generation/digest consumer matrix was executed before stopping. |
| A08.3.c | FAIL | NOT STARTED | F03 remains. The selected analysis-pointer/binding fixture passes, including stale global history and changed selected report, but it is not actual PLAN/ANALYZE orchestration. CAPTURE/BUILD/budget instruction integration is not fully accepted. |
| A08.3 parent | FAIL | NOT STARTED | F03 plus remaining profile/consumer evidence prevent complete acceptance. |
| A08.4 | PASS | NOT STARTED | r03 executes actual DISCOVER content/ADR snippets and directory-derived trusted-source inventory; jobs retain old, blocked and unknown-age records without read-side writes. P10 migration work remains separately owned. |
| A08.5 | BLOCKED | NOT STARTED | r03 two-initiative history, original Spec Kit IDs, loop-back and cold-shell recovery pass. The required inherited preservation failures remain unresolved; this is not full interrupted-recovery acceptance. |
| A10.1 | UNVERIFIED | NOT STARTED | Shared intake instructions and real capability resolver with synthetic allowed/denied/conversation bindings were assessed. No actual host question interaction was exercised. |
| A10.2 | UNVERIFIED | NOT STARTED | Reviewed DEFINE/office-hours/research/CEO instructions retain useful methods and make venture framing optional. No live maintenance/migration/research intake comparison was performed. |
| A10.3 | UNVERIFIED | NOT STARTED | r03 executes real plan-eng-review validate/writer/latest-reader/QA/SHIP and later-rejection revocation. Synthetic records are not live independent actors; all alternative entry points were not executed end to end. |
| A10.4 | PASS | NOT STARTED | Instruction-only dormancy verified: plan-tune states no active shared reader or decision effect; canonical PLAN no longer treats it as a conflict resolver. No activation is claimed. |
| A13.3 advisory option | UNVERIFIED | NOT STARTED | Implementer's advisory freeze evidence was read, not adopted as independent execution. The observation-learning wrapper was not run by this reviewer before the bounded stop. |

After the confirmed A08.1 counterexamples, MasterSession explicitly directed a
bounded report-only checkpoint without expanded testing or repair. The already
in-flight r03 lifecycle suite completed; it does not override F01/F02. Remaining
specification proofs stay open. Stage 2 never began, so there is no whole-46-file
correctness, concurrency, recoverability or quality signoff. Stage 3 also did not
begin.

## Commands actually executed and isolation

Product verification used a private session driver, never the implementer's
runtime driver. Each invocation constructed a new allowlisted child environment.
It set synthetic HOME, USERPROFILE, HOMEDRIVE/HOMEPATH, APPDATA/LOCALAPPDATA,
XDG configuration/data/state/cache/runtime, temp, LINTEL_HOME and GSTACK_HOME.
Inherited LINTEL/CLAUDE/GSTACK, Git, BASH_ENV/ENV and Python redirects were not
carried over. Intentional trusted source/target and interpreter inputs were
reconstructed; Python user-site and bytecode were disabled.

Before each of the three test commands, actual `paths.sh`, resolver, audit and
read-only jobs path resolution verified and recorded **32 contained locations**,
including packs, active pointer, profile, global/hook/resolver audit, job roots,
active/archive/registry paths, state and session roots. The outer HOME was 142
characters, LINTEL_HOME 150, and disposable source/target 141. No shorter-root
preservation substitute was used. Inner test fixtures remained beneath synthetic
temp and inherited synthetic outer Windows/XDG roots, not personal defaults.

Every command ran against a separate disposable copy of all 959 tracked frozen
checkout files, with synthetic Git metadata for helpers that resolve a repository.
This included the implementer report and the final cycle instructions. No executing
source was edited. Per-command raw-byte manifests of both the original and the
copy were unchanged after execution. Source status used explicit checkout-equivalent
`core.autocrlf=true`; fixture Git settings were isolated separately. Python working
files remain CRLF where checked out that way; frozen shell files remain LF.
This is not a claim that all tested working bytes equal raw LF Git blobs.

Hooks/signing were disabled for Git operations, global/system Git configuration
and attributes were isolated, and no source normalization/reset occurred. Approved
jq was hash-verified as
`a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`
and supplied only on the child PATH. Python was **3.11.9**. No tool installation,
PowerShell test/policy override, network, credential operation, live install,
paid-model call or hook activation was performed.

`$Private` below denotes this reviewer's private session artifact directory;
`$FrozenCheckout` denotes the exact original checkout, not a caller-selected home.
Raw expanded commands, environment, path results, stdout, stderr, exits, timing,
manifests and cleanup records are retained privately.

```powershell
python -I -S -X utf8 "$Private\p08_review_runner.py" --repo "$FrozenCheckout" --slot r01 --suite "tests\unit\intent-operation-boundary.sh"
python -I -S -X utf8 "$Private\p08_review_runner.py" --repo "$FrozenCheckout" --slot r02 --probe "$Private\p08_operation_probe.sh"
python -I -S -X utf8 "$Private\p08_review_runner.py" --repo "$FrozenCheckout" --slot r03 --suite "tests\integration\universal-work-lifecycle.sh"
```

The suite child command is `bash --noprofile --norc <frozen-fixture-wrapper>`.
The independent probe is supplied as literal stdin to
`bash --noprofile --norc -s`. The lifecycle wrapper invokes the actual Python
test file with `--root <frozen-fixture-source>`; it is not a zero-run proxy.

| Run | Reviewer-observed result | Exit | Child duration |
|---|---|---|---|
| r01 | 54 routing assertions, zero failures | 0 | 22.484 s |
| r02 | Six independent routing cases, three failures | 1 | 5.813 s |
| r03 | 29 lifecycle methods, OK, zero errors/skips; unittest time 507.405 s | 0 | 509.031 s |

These commands were serial. All three reported no remaining entries in their
synthetic temp directory; no cleanup error was relabeled as green. Their outer
source/home/evidence fixtures are deliberately retained privately, not represented
as deleted. No broad cleanup or actual-home inspection was performed.

Evidence identities:

| Artifact | SHA-256 |
|---|---|
| Private driver | `4202cc9ddb52d96a3dbb9c8b00589f88e67943146e7a455d6ba5a5f8ac579d7d` |
| Exact six-case probe/stdin | `dcc1fc28ca1bdf2582366a0ad2d6c1cf88030890e467d18fdd7af4fdedc215cc` |
| Identical source manifest for r01/r02/r03 | `517f7e8569f4be96e19ad39314d15f4b41d8c430f0bb8081819fdeff5f35a5cf` |
| r01 command/result metadata | `5ffdc2482d580669ddf55abc6aea87b8909f32d27f1d8fae3bc4ded20605a2b2` |
| r02 command/result metadata | `9f2321ed3e07796bfcd9e5d563c094014abbc75ed367209ed2619637afdc1ec5` |
| r02 exact output | `548028bdcda56215f216446a4ec4ea588426a7e47d63478dc8f7f7701108eec6` |
| r03 command/result metadata | `d5c2853b1565cbe8d8b141fa0b606dfd742359b3be9a674770743ecd416b8263` |
| r03 unittest output | `45e632f3c0dfd104d897de3bc5a08fcc95f7c2ef06c45a7f9e1db45ff445d578` |

## Oracle and instruction evidence boundaries

The two changed shape files were read against their actual authoritative producers,
not accepted because their strings agree with edited prose:

- `handoff-cap-wired.sh` retains PLAN/CAPTURE invocation, selected-map continuity,
  advisory/off-switch and substantive-review preservation assertions. Accepted
  `context_safety.context_budget` and `skills\context-budget\SKILL.md` make
  absent capacity/usage unknown; 500k/750k are historical advice, not host defaults.
  r03 independently exercises distinct bytes, unknown capacity, observed versus
  estimated usage, exact-fit/one-token-over boundary and missing provenance.
- `discover-scans-all-agent-categories.sh` retains directory-derived discovery
  and the negative hardcoded-category assertion. r03 executes the actual DISCOVER
  snippet with a trusted source, a future category, spaced filenames and a target
  decoy that must not be read.

Neither shape wrapper was independently executed in this stopped review. Their
inspection and the actual producer/snippet cases above do not turn the failed
preservation aggregate into a pass.

The two disclosed post-builder-run cycle authority sentences were inspected as
instructions: after SENSE, retain existing authority; before BUILD, ask only for
an unresolved plan/resource decision. They are not covered by the builder's
p8r4/p8r5 bytes. Although r03 used the final frozen source copy, it did not execute
a live agent following those sentences; semantic host adherence remains unobserved.
Wrapper executable-mode staging is likewise distinct from explicit Bash invocation.

## Inherited preservation blockers, not new P08 defect attribution

The complete `reports\P08.md` was read before tests. Its following results remain
**implementer/control evidence**, not this reviewer's counts or reruns:

| Existing evidence | Required disposition |
|---|---|
| p8r4: lifecycle 29 OK in 218.743 s; observation two OK in 3.382 s | Positive bounded self-evidence, not independent or complete preservation acceptance |
| p8r5: 14/18 wrappers exit zero; four exit nonzero | FAILED aggregate, not waived |
| p8r6: unchanged `f9685530` reproduces all four failures with 16/16 matching effective-path lengths per slot | Attribution only, not passing acceptance |
| Checkpoint reservations at 268/278/277/290 characters | Ownership, roundtrip and memory checkpoint proofs remain BLOCKED/UNVERIFIED |
| Context-safety 22/23; Git bisect ref-lock at 283 characters | Separate failing operation; complete dirty-source success/error preservation remains BLOCKED/UNVERIFIED |

No common root cause between checkpoint reservation and Git ref-lock failure is
asserted. Their P03/P07/test snapshots were reported raw CRLF-byte identical
between candidate/control; the committed-revision export and checkout EOL facts
must not be relabeled as a raw-LF claim. The P03 owner retains the bounded
investigation. This review did not duplicate it, alter accepted helpers, change
long-path settings, relocate default stores or substitute a shorter-path pass.

Historical **shell27 remains INVALID authorized evidence**, with actual-home
effects UNKNOWN. There was no inspection, recovery or rollback. In p8r2, the
fixture's explicit unlink failed before the missing-profile assertion; that is
not a P07 operation failure. Its separate teardown errors and p8r1 zero-test
setup failure remain failures, not retrospective acceptance.

## Explicit deferrals and integration stop

| Leaf/gate | Disposition |
|---|---|
| A13.1 | DEFERRED/BLOCKED by exact producer-interface release. No common event/audit implementation or roundtrip acceptance. |
| A13.2 | DEFERRED/BLOCKED. No new learning/promotion implementation, configured-sink acceptance or promotion invocation. |
| A13.4 | DEFERRED/BLOCKED. No complete event/promoted-lesson/incomplete-log roundtrip acceptance. |
| Whole 46-file QUALITY | NOT STARTED because selected SPEC is non-passing; not merely review of the last routing diff. |
| Joined distribution/preflight | Coordinator-owned and pending, including new trusted dependency `lib\workflow.sh` and generated catalog/wiki/README/native-kit reconciliation. |
| P10/F01/P14 | Default-store/cleanup, migration repair and installed scaffold caller/child bridge remain with their respective owners. |
| Actual Python 3.9, other OSs, live question/model/client behavior | UNOBSERVED. Grammar, injected probes, synthetic bindings and source metrics are not runtime, permission, capacity or measured-usage evidence. |
| Integration, release and real-home recovery | NOT AUTHORIZED by this report. |

Return F01/F02 and the already-observed F03 caller inconsistency to the original
builder through MasterSession for scoped repair. Renew affected SPEC evidence on
the resulting immutable revision before considering QUALITY. Retain all original
reports, failure evidence, A13 gates and inherited preservation obligations.

This report-only checkpoint neither updates authoritative completion state nor
grants partial-source integration, whole-P08 acceptance or initiative completion.
