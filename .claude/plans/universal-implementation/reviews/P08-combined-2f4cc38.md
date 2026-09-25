# P08 combined selected-subset independent review

**Date:** 2026-09-22

**Selected-subset SPEC: FAIL. QUALITY: NOT STARTED.**

**Integration readiness: BLOCKED. No whole-P08 acceptance.**

The original independent reviewer, session
`9dbf0a9b-750d-45c2-968c-41a5acb11c92`, reviewed the frozen combined candidate.
This is not the implementer's self-review or a new root-only review. All 21
earlier routing cases now pass, but four of the 12 predefined nearby contrasts
fail the requested compound-operation boundary. The valid lifecycle and
preservation evidence is retained separately. It does not override those failures
or supply unobserved semantic/host behavior.

MasterSession instructed this reviewer to freeze this report from existing valid
evidence, with no further product tests/replay or QUALITY. That stop was honored.
No product repair, dependency import, shared plan/memory edit, nested agent,
generated output, release clearance or external operation belongs to this review.
The sole tracked deliverable is this report.

## Authority and immutable source

The authorized boundary remains original A08.1-.5, their approved refinements,
A10.1-.4 and the explicitly advisory A13.3 option. A13.1/.2/.4 remain deliberately
deferred; they are not missing delivery in a whole-P08 completion candidate.
The selected `work.json` still points to the original spec/plan/tasks/prompt;
the tasks source is the original `plan.md`, not this report or the audit checklist.

The original frozen-partial authority at
`1105ebeb4df3792c78437a74a5bd852bea96209d`, narrow repair at
`04e0ba94c1d42f6b7198e7175f67c4e45d8b4333`, and the root re-plan, dependency join
and harness-correction sections of `packages\P08.md` at
`5efd5da534776a6e7d1043ed9319125db1a0fe1e` were read. The root authority is
`679c6b8` and dependency-join authority is
`733b28a8cc6285c33234f11ad860e60ecede33a5`. Original audited A08,
A10 and A13 acceptance, repository/adapter context, relevant memory/ADRs, both
prior independent rejections and the full appended builder report were inputs.
The coordinator's final freeze instruction limits the remaining action to this
report and its local report-only commit.

The nine phases remain SENSE, SCOPE, DEFINE, DISCOVER, PLAN, BUILD, REVIEW, SHIP
and CAPTURE. Resume is a utility, not a replacement three-stage lifecycle.
ANALYZE is an advisory utility, not a tenth phase or a PLAN completion event.

| Identity | Exact revision |
|---|---|
| Frozen review checkout; sole required parent of this report | `8eb00b87a9a14da7eaf949d11f1d1b444e9ecd8d` |
| Combined product; sole parent of `8eb00b87` | `2f4cc38077f547bc0ab006ecf9c90d6ba727db7a` |
| Fixture-only native-path consumer migration, +5/-4 in lifecycle test | `2f4cc38077f547bc0ab006ecf9c90d6ba727db7a` |
| Fixture dependency import | `1bb75560f685f9113b5f481e01db2d0f6a636fda` |
| Core dependency import | `7a4fcdbac45ffd6f86de45ac982eb3be40800999` |
| Preserved pre-join report checkpoint | `723b067f1bbfe4f0cbd2b86614973b4c556f36c7` |
| Five-path root correction | `171daa8d44f8e758bc1f6e98ff1c3a11a477ea18` |
| Earlier narrow repair/report | `44e2ef7d77ee1d9d68e466f2c7b11cd58be0d148` / `8bde7005a1c6408f66c8656dc2e8a2923044b005` |
| Prior independent closure rejection | `af5c93999b5e83357ae337d92cfd4abde872e235` |
| Original independent rejection | `9faebd2b7d027283a21a470c8e81473e39bd7a23` |
| Original partial product/report | `8d477701bf05c545790d4c5fdbdc84945dd130db` / `062ffc6cc0cfecee80646fda2a54bad4db837fad` |
| Original dependency control / integration ancestor | `f9685530c458b456021e30ddab699c03b49614ca` / `5c3e7533335eeae15556aeabba422bfdbbe07f46` |

The checkout was clean before execution and still clean at exact `8eb00b87`
before writing this report. The original reviewer branch remains at `9faebd2b`;
the prior report objects were not replaced. This continuation was detached, with
no reset, amendment, discard or named-ref rewrite. Shared repository checkpoint
refs and the separate coordinator branch changed during other sessions; no
claim that the entire shared ref namespace was frozen is made.

Dependency `7a4fcdba` attributes exact upstream
`ce7415f6342220e49746880dd7338a6e7d9294ed`; `1bb75560` attributes exact
`5fc657f14123daca9ec126cadc1e9d64ee60691c`. Their previously accepted P03/P07
work is a dependency, not P08 authorship or a new acceptance by this reviewer.
The four root-correction blobs below remain identical to `171daa8d`; the only
subsequent P08 test edit is the separately attributed lifecycle import migration.

| Path | Combined Git blob | Mode |
|---|---|---|
| `lib\orientator-routing.sh` | `f63e2cbf87f583c4d1c2236286a320245ffc5b3b` | `100644` |
| `lib\workflow.sh` | `27afa35ef9a826da57c8972b94d959bec60fbd9f` | `100644` |
| `skills\plan\SKILL.md` | `9597eba668bc7825429df6e39b25ff11926bf53f` | `100644` |
| `tests\unit\intent-operation-boundary.sh` | `923f4bbfc4414f73c70cfca7225fab0b555de5cf` | `100755` |
| `tests\integration\universal-work-lifecycle.py` | `d1ab38cedc7f3dad10b07a7a9f553e6d13bda766` | `100644` |
| `lib\context_safety.py` | `b3d3f6e761ae0fa4562ccd992e1a5e7d3bc464c6` | `100644` |
| `lib\native_paths.py` | `835098264c9228f74caae5c63f1ded1430dbd94d` | `100644` |
| `lib\profile_context.py` | `ce7ac27636b1d9f987408559b99f221414b01900` | `100644` |
| `lib\markdown_source.py` | `0b3da55046358864fcd3075ba5bfb6c2348b1fec` | `100644` |

The earlier 46-path partial product and its original five separately attributed
dependencies retain the ownership recorded in `9faebd2b`. The combined range
after `8bde7005` is 22 paths including the appended builder report; it must not
be described as 22 new P08-owned product files. This reviewer changed none of
those paths and did not import or accept P10 WIP.

## Findings and F01/F02/F03 disposition

**Current reproducible specification findings: P1 = 0, P2 = 2, P3 = 0.**
F04/F05 below describe the two current failure mechanisms, not four phrase-level
findings. Historical F01/F02 P1 and F03 P2 rejections remain immutable evidence;
their historical severities are not counted again as new observations.
QUALITY has neither a verdict nor a finding count.

| Finding/control | Disposition |
|---|---|
| F01/F02 joint operation-authority closure | **OPEN at class level.** All original 21 examples pass, including prohibitions and indirect inquiries. No re-failure of those old inputs is claimed. The authorized replacement request grammar still grants a single high-confidence route to unresolved independent operations, as F04/F05 show. A08.1 and its r1/r2 refinements are not accepted. |
| F03 global-history PLAN caller defect | **CLOSED for the bounded mechanical selection defect**, using the separately valid c20 caller tests, not q02. Relative, drive-qualified forward-slash and native-backslash history pointers are refused present/absent. This is not complete A08.3.c semantic-consumer acceptance. |
| A08.3.c remaining original consumers | **UNVERIFIED** for actual semantic analysis, accepted-finding carry-forward and full CAPTURE/BUILD/original-task update behavior. A correct path and synthetic INCOMPLETE prose are not those proofs. |
| Whole selected subset | **FAIL**; unproved original requirements also remain open in the per-leaf matrix. QUALITY and integration stay blocked. |

### F04 - P2: conjunction heads use a smaller verb set than initial heads

**Location:** `lib\orientator-routing.sh:78-89,143-153`.

**Acceptance:** A08.1 and A08.1.r1/r2; independently requested operations must
be collected before resolution, while object coordination remains useful.

**Confidence:** 10/10.

The initial request-head recognizer accepts `edit`, `change` and `provision`.
The later `and|or` branch recognizes only a different, smaller set of candidate
operation heads. Consequently the following predefined probes return the first
operation with high confidence:

| Exact input | Expected | Actual |
|---|---|---|
| `Build the service and edit its configuration.` | unclear / `/li:cycle` / low | build / `/li:cycle` / high |
| `Deploy the release and change the deployment manifest.` | unclear / `/li:cycle` / low | deploy / `/li:cycle --from SHIP` / high |
| `Build the service and provision the environment.` | unclear / `/li:cycle` / low | build / `/li:cycle` / high |

The paired semicolon forms all return unclear/low. `Implement audit and review
logging.` still returns build/high, demonstrating the intended distinction from
object coordination. This is not a request to reject every `and`, nor an
instruction to add three isolated verb exceptions. Reuse one governing-head
recognition rule across independent clauses/conjunctions and resolve the whole
request before assigning a route.

The defect is lost compound intent and unjustified confidence, not evidence that
the user prohibited the first imperative. No returned build/ship workflow ran.

### F05 - P2: a newline erases an independent request boundary

**Location:** `lib\orientator-routing.sh:185-190,215-227`.

**Acceptance:** A08.1 and A08.1.r1/r2; preserve independent request/sequence
structure without turning formatting-only line breaks into extra operations.

**Confidence:** 10/10.

The whitespace branch flushes the current word and records line-start state,
but does not retain a clause/sequence boundary for a newline. The predefined
input containing one literal line feed:

```text
Deploy the release
Review the release plan.
```

returns deploy / `/li:cycle --from SHIP` / high rather than unclear /
`/li:cycle` / low. The second governing request is absorbed into the first
clause's words. The contrasting wrapped single request,
`Please\nreview the fix\nwithout changing code`, correctly returns review/high.
The repair therefore needs structural request-boundary recognition, not a rule
that all newlines terminate an operation or four special-case phrases.

This recommendation error was observed through the producer and actual route/
confidence consumers only. No deployment, model invocation or bypass of a later
host permission gate was exercised.

## Exact 33-case independent routing matrix

q01 fixed all inputs and expectations before the single producer/consumer run.
Rows 1-21 are the unchanged prior independent matrix; rows 22-33 are the
predefined contrasts. In rows 28 and 29, `\n` denotes an actual LF in the input,
not the two literal backslash/n characters. Rows 20-21 set caller `IFS=:` and
verify it is unchanged. Every other row uses the ordinary caller IFS.

The probe sources the frozen router, then calls `classify_intent "$request"`,
`match_workflow "$actual" cycle` and `score_confidence "$actual" "$workflow"`.
It never executes a returned workflow. `safe` means one of research /
research-dive / high, review / review / high, or unclear / cycle / low.
Those are acceptable alternatives, not a requirement to pick one particular
read enum. Every non-safe expectation names its exact intent/route/confidence.

**Observed:** original matrix 21/21; additional contrasts 8/12; combined
expectation comparisons 29/33. The shell collector itself exited 0; successful
collection is not a specification pass.

| # | Exact input | Expected intent / route / confidence | Actual intent / route / confidence | Result |
|---|---|---|---|---|
| 1 | `Do not change the release plan; explain it.` | research / `/li:cycle --mode research-dive` / high | research / `/li:cycle --mode research-dive` / high | PASS |
| 2 | `Do not edit the deployment code; describe the release process.` | research / `/li:cycle --mode research-dive` / high | research / `/li:cycle --mode research-dive` / high | PASS |
| 3 | `Is it safe to deploy this release?` | research / `/li:cycle --mode research-dive` / high | research / `/li:cycle --mode research-dive` / high | PASS |
| 4 | `Do not build the release.` | unclear / `/li:cycle` / low | unclear / `/li:cycle` / low | PASS |
| 5 | `Review the release plan.` | review / `/li:review` / high | review / `/li:review` / high | PASS |
| 6 | `Deploy the reviewed release.` | deploy / `/li:cycle --from SHIP` / high | deploy / `/li:cycle --from SHIP` / high | PASS |
| 7 | `The release must not be deployed; explain the plan.` | safe | research / `/li:cycle --mode research-dive` / high | PASS |
| 8 | `Release notes: explain the deployment process.` | safe | research / `/li:cycle --mode research-dive` / high | PASS |
| 9 | `I want to know whether it is safe to deploy this release.` | safe | research / `/li:cycle --mode research-dive` / high | PASS |
| 10 | `I need advice on whether to deploy this release.` | safe | research / `/li:cycle --mode research-dive` / high | PASS |
| 11 | `Do not change the release plan, but explain the deployment process.` | safe | research / `/li:cycle --mode research-dive` / high | PASS |
| 12 | `Don't change the build or release notes; review the plan.` | safe | review / `/li:review` / high | PASS |
| 13 | `Is the plan ready for release, or does it need review?` | safe | research / `/li:cycle --mode research-dive` / high | PASS |
| 14 | `Could you deploy the reviewed release?` | safe | unclear / `/li:cycle` / low | PASS |
| 15 | `Review the change then deploy it.` | unclear / `/li:cycle` / low | unclear / `/li:cycle` / low | PASS |
| 16 | `Implement release-note validation.` | build / `/li:cycle` / high | build / `/li:cycle` / high | PASS |
| 17 | `Fix review comments.` | fix / `/li:cycle --mode hotfix` / high | fix / `/li:cycle --mode hotfix` / high | PASS |
| 18 | `Release v2.` | ship / `/li:cycle --from SHIP` / high | ship / `/li:cycle --from SHIP` / high | PASS |
| 19 | `Please deploy the reviewed release.` | deploy / `/li:cycle --from SHIP` / high | deploy / `/li:cycle --from SHIP` / high | PASS |
| 20 | `Do not change the release plan; explain it.` | safe; caller IFS retained | research / `/li:cycle --mode research-dive` / high; IFS retained | PASS |
| 21 | `Deploy the reviewed release.` | deploy / `/li:cycle --from SHIP` / high; caller IFS retained | deploy / `/li:cycle --from SHIP` / high; IFS retained | PASS |
| 22 | `Build the service and edit its configuration.` | unclear / `/li:cycle` / low | build / `/li:cycle` / high | FAIL F04 |
| 23 | `Build the service; edit its configuration.` | unclear / `/li:cycle` / low | unclear / `/li:cycle` / low | PASS |
| 24 | `Deploy the release and change the deployment manifest.` | unclear / `/li:cycle` / low | deploy / `/li:cycle --from SHIP` / high | FAIL F04 |
| 25 | `Deploy the release; change the deployment manifest.` | unclear / `/li:cycle` / low | unclear / `/li:cycle` / low | PASS |
| 26 | `Build the service and provision the environment.` | unclear / `/li:cycle` / low | build / `/li:cycle` / high | FAIL F04 |
| 27 | `Build the service; provision the environment.` | unclear / `/li:cycle` / low | unclear / `/li:cycle` / low | PASS |
| 28 | `Deploy the release\nReview the release plan.` | unclear / `/li:cycle` / low | deploy / `/li:cycle --from SHIP` / high | FAIL F05 |
| 29 | `Please\nreview the fix\nwithout changing code` | review / `/li:review` / high | review / `/li:review` / high | PASS |
| 30 | `Explain how to build and deploy the service.` | research / `/li:cycle --mode research-dive` / high | research / `/li:cycle --mode research-dive` / high | PASS |
| 31 | `Implement audit and review logging.` | build / `/li:cycle` / high | build / `/li:cycle` / high | PASS |
| 32 | `Release commands are prohibited; explain the plan.` | safe | research / `/li:cycle --mode research-dive` / high | PASS |
| 33 | `I would like information about how to deploy the release.` | research / `/li:cycle --mode research-dive` / high | research / `/li:cycle --mode research-dive` / high | PASS |

## Valid lifecycle and F03 evidence

c20 independently executed the unchanged 39-method lifecycle wrapper on the
sealed combined source, entirely within its recorded synthetic child. It exited
0 with 39 tests OK and no skips. This result is distinct from the invalid q02
custom replay described below.

The actual PLAN Step 8 preparation/persistence blocks are extracted and executed
by `tests\integration\universal-work-lifecycle.py:412-737`, not replaced by
manually correct caller selections. Valid c20 evidence includes:

| Requirement/discriminator | Observation and boundary |
|---|---|
| Two initiatives and cold persistence | Actual bootstrap/begin/resume, approved and DRAFT maps, selected report production and fresh-process persistence; original paths/IDs, other report, stale global report and source tasks retained. |
| Global history, three spellings times present/absent | All six cases exit 2 with the history/reconciliation diagnostic and unchanged snapshots. Native-backslash regression no longer selects the global path. |
| Same basename in a distinct directory | Present/absent and all three spellings preserve that proven distinct parent and the exact selected spelling; no read-side writes. |
| Wrong map and required-profile drift | Different-initiative refusal and same-mtime `PROFILE_DRIFT` refusal before report writes; original ledger retained. |
| Missing report persistence | Exit 2 with the explicit missing-report diagnostic; no ledger success. |
| Unproven or undeclared parent | Explicit INCOMPLETE, no directory/report creation, no arbitrary new allowed root. |
| Denied identity probe | Injected `PermissionError` produces explicit INCOMPLETE and unchanged files. This is fault injection, not a real OS permission-policy change. |
| Existing native case alias | Actual observed filesystem was case-insensitive (`case-sensitive existing pair observed: False`); alias refused by identity. A genuinely distinct case-sensitive pair was not observed on this filesystem. |
| Absent case-only alias and declared state root | Uncertain alias refused without creation; existing declared state root honored and its global history rejected. |
| Selected report binding | Actual P05 `bind_work` comparison occurs inside the isolated test child; selected report is used, global report excluded and `release_clearance` remains false. |
| Original lifecycle controls | Begin/idempotency, status-grounded footer, interrupted/truncated transition, reader/writer failures, injection refusals, explicit phase range, loop-back and two-initiative history pass. |

Only report prose is synthetic, explicitly `legs_checked: []`, incomplete
semantic legs and `verdict: INCOMPLETE`. A report pointer does not validate
analysis reasoning, accepted-finding carry-forward or release authority.
ADR-0004 remains advisory; P05's immutable obligations and later-rejection rules
are not relaxed. The native result and source-level use of `samefile` do not
claim new Linux/macOS or actual case-sensitive-volume acceptance.

## Invalid q02 replay and preserved limitations

**q02's reported 47/47 is INVALID and excluded from all acceptance, counts and
closure decisions in this report.** The custom replay's direct Python
`bind_work` comparison ran in its outer reviewer process,
outside the recorded synthetic child environment. The per-shell allowlists and
preflights do not cover that parent-process product call.

This is a reviewer verification-boundary error. The full q02 record remains
retained; its raw 47/47 cannot be relabeled PASS or spliced into c20. No portion
of q02 is needed to support F03's bounded closure. Real-home effects of the
uncontained parent call remain **UNKNOWN**: neither absence of visible output
nor knowledge of the helper is proof of no effect. No personal-home inspection,
cleanup, rollback or replay was performed after disclosure. The coordinator
explicitly required exclusion and report freeze.

Earlier shell27 INVALID, p8r2, p8r5/p8r6 failed preservation evidence, p8r7/p8r8
RED, p8r10 fixture mistakes, p8r11 guard bug and builder p8j1 INCOMPLETE retain
their original status. p8k2's deadline failure remains failed, cause unassigned.
The accepted dependency and new synthetic checks do not retroactively repair
them. The previously reported host-managed output capture remains uninspected;
it is not proof of either external effects or their absence.

## Commands actually run and separate preservation evidence

Let `$Frozen` be the sealed 137-character source root at
`.claude\runtime\p8v2xxxxx\src`. Each ordinary row below used
`bash --noprofile --norc <the indicated frozen wrapper>` with its own recorded
environment/preflight, stdout/stderr, actual exit and duration. Full expanded
argv/cwd/stdin and hashes are in private receipts. Paths below identify commands,
not newly proposed checks.

| Slot | Frozen wrapper or method selection | Actual exit / result |
|---|---|---|
| c1 | `tests\unit\intent-operation-boundary.sh` | 0; retained 183 assertions and final 574 assertions, 0 failures; one run, not two suites counted twice |
| c2 | `tests\unit\cycle-footer.sh` | 0; PASS |
| c3 | `tests\unit\cycle-continuity.sh` | 0; PASS |
| c4 | `tests\unit\context-repository-ownership.sh` | 0; PASS at original depth |
| c5 | `tests\unit\context-checkpoint-roundtrip.sh` | 0; PASS at original depth |
| c6 | `python -B tests\unit\context-safety.py` with the recorded 26 named deep methods | 0; 26 OK, no skips; not an invocation of the old whole wrapper |
| c7 | `tests\unit\jobs-steps.sh` | 0; PASS |
| c8 | `tests\unit\jobs-registry-concurrency.sh` | 0; PASS |
| c9 | `tests\unit\jobs-system-present.sh` | 0; PASS |
| c10 | `tests\unit\memory-v2.sh` | 0; PASS at its original one-character-longer slot depth |
| c11 | `tests\unit\work-artifacts.sh` | 127; `python3: command not found`; retained failed command |
| c12 | `tests\integration\enterprise-workflow-snippets.sh` | 127; `python3: command not found`; retained failed command |
| c13 | `tests\unit\review-source-target.sh` | 0; PASS |
| c14 | `tests\integration\swarm-workflow.sh` | 0; PASS |
| c15 | `tests\shape\claude-home-paths.sh` | 0; PASS |
| c16 | `tests\shape\audit-writes-via-helper.sh` | 0; PASS; structural writer contract, not deferred A13 event integration |
| c17 | `tests\shape\handoff-cap-wired.sh` | 0; PASS |
| c18 | `tests\shape\discover-scans-all-agent-categories.sh` | 0; PASS |
| c19 | `tests\unit\orientator-mechanical-routing.sh` | 0; all eight retained scenarios PASS |
| c20 | `tests\integration\universal-work-lifecycle.sh` | 0; 39 methods OK, no skips; 550.797 seconds for the wrapper |
| c21 | `tests\integration\observation-learning.sh` | 0; two methods OK, no skips |
| c22 | The two exact native threshold/publication methods below | 0; two methods OK, no skips |
| c11b | Unchanged c11 wrapper sourced after an explicit process-local `python3()` binding to verified Python 3.11.9 | 0; PASS; separate environment/result, not deletion of c11 |
| c12b | Unchanged c12 wrapper with that same explicit binding method | 0; PASS; separate environment/result, not deletion of c12 |
| q01 | `bash --noprofile --norc -s`, recorded 33-case producer/consumer script | collector 0; 29 expected outcomes pass, four FAIL |
| q02 | Custom actual-PLAN replay | **INVALID/excluded**, irrespective of its reported 47/47 |

c11b/c12b printed their effective interpreter version and forwarded arguments to
the existing verified `LINTEL_PYTHON`. They changed neither source nor installed
tools. Their sealed stdout/stderr and zero-residue checks are separate evidence.
There is no invented single "18/18", "22/22" or all-green aggregate across failed
commands, modified invocation environments, split fixtures or q02.

The changed shape oracles were not accepted solely because their source strings
match their consumers. c6's retained capacity test exercises the accepted P03
unknown/estimated/observed distinction; c17 must not reinstate an invented
500k/750k host default. c20 executes DISCOVER's source-root inventory with a
future agent category as well as its ADR/content snippets, supporting c18's
directory-derived discovery contract rather than a frozen category list.
Source metrics and token priors are not measured model usage or host capacity.

### Original-depth and exact-length preservation

For c4/c5/c6/c10 the actual preflight compared all 16 fields to the recorded
p8r5/p8r6 dimensions; every comparison was true. The table gives character
lengths, not newly chosen shorter defaults:

| Effective field | c4/c5/c6 | c10 |
|---|---|---|
| HOME | 140 | 141 |
| USERPROFILE | 140 | 141 |
| LINTEL_HOME | 148 | 149 |
| packs | 154 | 155 |
| active pointer | 166 | 167 |
| profile | 161 | 162 |
| global audit | 154 | 155 |
| hook audit | 159 | 159 |
| resolver audit | 154 | 155 |
| jobs | 158 | 158 |
| registry | 164 | 165 |
| canonical registry | 164 | 165 |
| state | 159 | 159 |
| sessions | 162 | 162 |
| repository | 137 | 137 |
| source | 137 | 137 |

The unchanged 28-method `ContextSafetyTests` source was enumerated. The c6
26-method set and c22 two-method set have empty intersection and a complete
union; `partition.json` retains every name and the source SHA-256. c22 ran only:

```text
ContextSafetyTests.test_native_checkpoint_thresholds_keep_logical_paths_and_owned_bytes
ContextSafetyTests.test_native_snapshot_atomic_publication_uses_218_to_260_without_shortening
```

The two unchanged exact-size fixtures require outer padding below 94 characters.
They ran beneath the specifically authorized, previously unused 88-character
session `files` child `p8s9`, with both that boundary and the deep source sandbox
named in their Git ceiling/containment record. This is an explicitly split-fixture
group, not a shortened c6 source/home or a passing run of its old whole wrapper.
Only that owned short-temp child was removed after it was empty; the session
root, other artifacts and personal state were not cleaned.

The exact methods assert real checkpoint operands of **259/260/268/278/277/290**
characters and real atomic publication **218 -> 260**, including stored bytes,
ownership and injected publication failure. The c6 deep bisect method asserts
the **283-character Git ref-lock** operand and checks dirty-source preservation,
success/error cleanup and retained trial evidence. These are not inferred from
a shallow substitute. The old 268/278/277/290 and 283 obligations therefore have
new positive mechanical evidence on this combined source, without rewriting
the older failures or clearing unrelated integration obligations.

## Source, argv and environment seals

One frozen copy contained **960 tracked checkout files**, preserving exact
working bytes, including checkout EOLs. Shell sources remained LF; checked-out
Python/Markdown files may be CRLF. The review did not normalize the source to
raw LF Git blobs. Raw-byte manifests and Git-mode/EOL records were compared
before/after the valid invocations. Both original tracked source and frozen copy
remained unchanged. This report is added only after product execution ended.

Each valid child starts from an allowlist rather than inherited redirects:
synthetic HOME/USERPROFILE/HOMEDRIVE/HOMEPATH, APPDATA/LOCALAPPDATA, XDG
config/data/state/cache/runtime, TEMP/TMP/TMPDIR, LINTEL_HOME and GSTACK_HOME;
explicit trusted source, target and interpreter; disabled Python user-site and
bytecode. No inherited LINTEL/CLAUDE/GSTACK, Git, BASH_ENV/ENV or Python redirect
is treated as authorization. Actual resolver, audit and read-only job resolution
records contained pack/pointer/profile, audit, registry, job, session/state and
target/source paths before execution.

Git global/system configuration, attributes, templates, hooks, signing and
credentials were isolated/disabled for fixture operations. Every preflight
proved Git refuses an uninitialized plain folder but recognizes an initialized
child inside the stated synthetic ceiling. Original-checkout Git identity uses
its separate explicit scope and checkout-equivalent `core.autocrlf=true`,
not fixture discovery isolation. No global long-path setting changed.

The approved existing jq has SHA-256
`a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`;
Python is native 3.11.9. No dependency/client installation, policy override,
network, credential operation, paid model, live deployment, promotion or hook
registration occurred. Direct fixture hook invocation is not host registration.
The retained Python 3.9 grammar/annotation check is not actual Python 3.9
execution. Live model semantics, actual host questions and other operating
systems were not observed; injected denial is not a real ACL exercise.

The private evidence roots are `.claude\runtime\p8v2xxxxx` and
`.claude\runtime\p08-combined-review`. Full local paths/environment values remain
there rather than copying personal absolute paths into this report. The
following SHA-256 seals make the selected evidence unambiguous:

| Artifact | SHA-256 |
|---|---|
| Frozen `source-manifest.json` | `e947e7392a8307606e5981dcfc650d12b4ad5b8ef9ff4378aeccc26e5adbff94` |
| Frozen `source-eol.txt` | `b31f1039f02e85944612c00a6fb881083228c99cd7687722d3aff03d33e8c821` |
| q01 `environment.json` | `63ab11c4480dc99f3c129cf26896e45cabcc43b2c6a7fc0e0270b66d4b950d77` |
| q01 `resolved-paths.json` | `4a3b6fd8a624e02cbf847df022259b366a4c94898f0af7be34b9752bf0f5d8e9` |
| q01 `inputs.json` | `4ec15d95428ee67f1f0eb5d3f5a347377ec41cfcf9626922d395dc4b1b9a49ed` |
| q01 `commands.sh` / stdin | `8772ced4e598d444135bb7e9388375fe4459da212c4cca00c311a1e0d977d203` |
| q01 producer/consumer argv/cwd/exit receipt | `9e148c8994786917b070c89ec472d2b25b6eeb49b164a1992967cfee087167f5` |
| q01 raw stdout | `8003d1f31c9491e272d409fc8f2a9160b58d109b51cabb8ead705d05dc266a66` |
| q01 raw stderr (empty) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| q01 `results.json` | `fb7503c1f29fe81132c9412dfcbe9c0e28f17c9cc726b28649113a4aba0de5df` |
| c6 complete/disjoint `partition.json` | `0f57b52e69b43cda84ae821a18cb977370c17169f3b71225a0f16720ff8b55bb` |
| c20 actual wrapper receipt | `3ab20d128a1cb776d61ee49ee2f5c3e924f0ed8d52d321754bcbd097d0fd31ef` |
| c22 actual special-method result | `e7b296cea070406e76599ef5bb41ad15fafa82689c38b4435bf9a6c874307d32` |
| Private `verify_driver.py` | `0f89de1369478c177b0a2e9bcb073f10de0b6a80b6d6290878e9b1ce661bc24d` |
| Private `independent_probes.py`, including excluded q02 caller | `9e7d35d66afa31441bc2f0a0cb5b01b0e7b6150c06eb53a40e17a75e790ac6f9` |

q01's exact shell argv is
`["C:\\Program Files\\Git\\bin\\bash.exe","--noprofile","--norc","-s"]`;
cwd is the sealed source. Its receipt records 5.937 seconds and the hashes above.
All valid command temp directories were empty at their recorded completion.
Evidence directories and the frozen source remain retained privately; they are
not presented as unclean test residue.

## Complete selected-leaf disposition

PASS is limited to the named original mechanical or explicitly instruction-only
contract. It does not waive upstream failures, prove model behavior or accept a
package. UNVERIFIED means the original requirement lacks observed evidence, not
that an unrelated platform expansion is demanded. All QUALITY cells remain
NOT STARTED.

| Original/refinement leaf | SPEC/evidence disposition | QUALITY | Original requirement still open, if any |
|---|---|---|---|
| A08.1 | FAIL | NOT STARTED | F04/F05: compound-operation honesty; earlier exact 21 pass but class closure is withheld. |
| A08.1.r1 | FAIL | NOT STARTED | Independent heads must be recognized consistently and retained across structural boundaries. |
| A08.1.r2 | FAIL | NOT STARTED | The four predefined contrasts fail despite all 574 retained/new wrapper assertions passing. |
| A08.2.a | PASS, mechanical | NOT STARTED | c3/c20 begin-before-phase, identity protection, interruption/truncation, failure propagation and no false DONE are positive; upstream A08.1 is still failed. |
| A08.2.b | PASS, mechanical | NOT STARTED | c2/c20 status-grounded STARTING/BLOCKED/DONE/DONE_WITH_CONCERNS and selected-range footer evidence. |
| A08.2.c | UNVERIFIED beyond mechanical selection/instruction wiring | NOT STARTED | c20 phase-range/no-duplicate helpers and c12b snippets pass; an actual agent's complete single-dispatch/no-duplicate phase loop was not observed. |
| A08.2 parent | BLOCKED | NOT STARTED | Failed routing prerequisite and unobserved full orchestration remain; preserved helper behavior is not complete acceptance. |
| A08.3.a | PASS, mechanical | NOT STARTED | c11b/c20 explicit original map/IDs, P04 parsing, distinct-byte manifest, missing artifacts, exact budget boundary and P05 binding; no second acceptance authority. |
| A08.3.b | PASS for tested resume identity | NOT STARTED | c20 real P07 fresh-shell reference/map/policy, same-mtime drift, missing-context refusal and target/map argument refusals. No broader cross-target transfer clearance is claimed or newly required. |
| A08.3.c.r1 | PASS for bounded native selection | NOT STARTED | Valid c20 closes F03's caller/history-spelling defect; unobserved case-sensitive filesystem execution is explicitly limited, not a new platform mandate. |
| A08.3.c.r2 | PASS for the executed mechanical matrix | NOT STARTED | Valid c20 proves caller/persistence/history and refusal cases. q02 supplies zero acceptance evidence. |
| A08.3.c | UNVERIFIED beyond those mechanical controls | NOT STARTED | Actual semantic DEFINE/PLAN/BUILD analysis, accepted-finding carry-forward and complete CAPTURE/BUILD/original-task update behavior are not proven by synthetic INCOMPLETE reports or shape tests. |
| A08.3 parent | BLOCKED | NOT STARTED | Shared mechanical selection is positive; upstream gates and remaining consumer behavior are not closed. |
| A08.4 | PASS, mechanical | NOT STARTED | c20 executes actual DISCOVER content/Markdown-YAML ADR snippets, source/future-category inventory and old/blocked/unknown-age jobs without writes; c7-c9/c18 preserve related behavior. |
| A08.5 | UNVERIFIED for complete original lifecycle acceptance | NOT STARTED | c20 two initiatives, Spec Kit IDs, loop-back and cold history plus repaired preservation are positive. Full agent orchestration and an actual update to the selected external task source across that flow were not observed. |
| A08.5.j1 | PASS, immutable composition | NOT STARTED | Exact reviewed dependency blobs/modes and the +5/-4 public-helper fixture consumer are separately attributed; the four frozen root-correction blobs are unchanged. |
| A08.5.j2 | BLOCKED for combined-candidate acceptance; named preservation controls PASS | NOT STARTED | Original 16-field dimensions, the complete/disjoint 26+2 split, real threshold/ref-lock operands and valid lifecycle receipts are positive. The final candidate still has four independent routing failures and unverified selected controls; no whole-candidate PASS or QUALITY follows. |
| A10.1 | UNVERIFIED for actual intake interaction | NOT STARTED | Shared unresolved-decision instructions and real capability resolution with synthetic allowed/denied/conversation bindings were checked; no actual host-question interaction/reuse scenario ran. |
| A10.2 | UNVERIFIED for task-type intake outcomes | NOT STARTED | Source keeps maintenance/migration/research proportional and venture opt-in; no live or equivalent semantic intake comparison establishes the required question outcomes. |
| A10.3 | UNVERIFIED for full entry-point equivalence | NOT STARTED | c12b canonical composition snippets and c20 real review writer/latest-reader/QA/SHIP with later-rejection revocation pass. They do not prove identical work artifacts/approval status for every alternative entry from the same input. |
| A10.4 | PASS, instruction-only dormant option | NOT STARTED | plan-tune remains explicitly dormant with no active shared reader or conflict-resolver effect; no activation claimed. |
| A13.3 advisory option | PASS within its explicitly permitted advisory boundary | NOT STARTED | c21 proves canonical freeze metadata is not falsely advertised as a wired guard; direct legacy hook is warn-only and the target remains writable. Existing lesson retrieval is preservation only, not A13.2 acceptance. |
| A13.1/.2/.4 | DEFERRED / NOT SELECTED | NOT STARTED | Actual P10 producer seam, common event/learning/promotion integration and their roundtrips remain gated; no new schema or activation was reviewed. |

The mandatory open rows are concrete original A08/A10 behaviors, not a demand
for a new scheduler, another interpreter version, every advertised client, paid
models or new live infrastructure. Missing semantic/host evidence is not silently
turned into PASS, and instructions whose declared contract is advisory/dormant
are assessed as such.

## Freeze and handoff

The selected-subset specification does not pass. No scoped QUALITY review or
final integration review started. No clearance record should be generated from
this report. The coordinator may give the original owner a bounded root repair;
this reviewer will not patch the findings or continue a phrase search.

Only this report is to be committed as a child of exact `8eb00b87`. Its immutable
commit/parent, report blob/SHA-256 and clean working status are returned separately
after report-only Git verification. Prior reports, product/dependency commits,
invalid evidence and the original reviewer ref remain preserved.
