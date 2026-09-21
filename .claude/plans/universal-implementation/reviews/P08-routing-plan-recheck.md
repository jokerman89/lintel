# P08 routing and PLAN closure recheck

**Selected-subset SPEC: FAIL. F01/F02/F03: OPEN. QUALITY: NOT STARTED.**
**Preservation/integration readiness: BLOCKED. No whole-P08 acceptance.**

This is the same distinct independent reviewer as the rejection at
`9faebd2b7d027283a21a470c8e81473e39bd7a23`, not the implementer or a new reviewer.
The narrow recheck covers operation-authority routing and the actual PLAN
preparation/persistence caller only. The six original inputs now pass, but four
nearby operation-authority counterexamples remain. PLAN's original global-path
instruction was replaced, but its new legacy-history guard fails for a native
Windows backslash path. These improvements do not close the findings' contracts.

No nested agents, fixes, shared plan/memory edits, dependency imports, promotion,
live analysis, deployment, hook activation or external operation were performed.
The sole repository output is this report.

## Authority, ancestry and source identity

The original clean review/ref at `9faebd2b` and its report were preserved. A clean
detached continuation selected exactly
`8bde7005a1c6408f66c8656dc2e8a2923044b005`; no reset, discard or ref rewrite was
used. That report-only commit has sole parent
`44e2ef7d77ee1d9d68e466f2c7b11cd58be0d148`, the product under recheck. Product's
sole parent is rejected checkpoint `062ffc6cc0cfecee80646fda2a54bad4db837fad`.
The prior review branch still points at `9faebd2b`; the coordinator's preservation
as `a56aab4` is separate. Original integration base
`5c3e7533335eeae15556aeabba422bfdbbe07f46` remains an ancestor.

The complete earlier rejection, original selected work map/spec/cards, relevant
repository/adapter context and ADRs, and implementer's report including its full
append from line 525 were read. The immutable narrow repair authority is
`04e0ba94c1d42f6b7198e7175f67c4e45d8b4333:packages/P08.md`, under
`.claude/plans/universal-implementation/`. The original partial boundary at
`1105ebeb4df3792c78437a74a5bd852bea96209d` still forbids whole-P08 acceptance
and requires complete selected SPEC before QUALITY. MasterSession explicitly
confirmed keeping F01/F02 open at the class level and finishing only these
bounded checks.

Independent Git inspection confirmed exactly **four product paths, +377/-30**:

| Path | Delta | Product Git blob |
|---|---|---|
| `lib\orientator-routing.sh` | +52/-26 | `ef6d1b25ccd414dbf90934db7d07c06daf2414c1` |
| `skills\plan\SKILL.md` | +58/-4 | `7d511d86f13c6fb119aef81d2ea34139b1950320` |
| `tests\integration\universal-work-lifecycle.py` | +187/-0 | `abe75158cd862e010bcbcfaa82de3e8ba8fbe135` |
| `tests\unit\intent-operation-boundary.sh` | +80/-0 | `11cade8ecabfdd6108713b54b2d46989e7f6020c` |

The earlier builder report is a byte-unchanged prefix of the appended report:
old SHA-256 `872353f05dbdf4441f4e61005a00d5eb9fe59c702393aad568af7f7768d560da`,
new SHA-256 `8b2bd08688d8fd1e8e2cafe60589bed2c35ab478d4f35523cfeed5a5e4c2dfa8`.
The original 46-file partial component and its separately attributed dependencies
remain described by `9faebd2b`, not reclassified as this four-file repair.

There is no change to shared P03/P04/P05/P06/P07 implementation, schemas or provider,
`bin\_audit.sh`, `lib\memory.sh`, `bin\li-lessons-promote`, or P10 implementation.
Provider `lib\markdown_source.py` remains blob
`0b3da55046358864fcd3075ba5bfb6c2348b1fec`. The earlier separately attributed
`e3799480 -> 8a2429e`, `c8058497 -> acc728e`, `d53dc38 -> 35aff7e`,
`aa56a67 -> cce69c8`, and `935b640 -> f968553` dependencies are not P08 authorship.
The new P03 shared-path work is not present or accepted by this review.

## Scoped findings and closure decisions

**Specification findings: P1 = 2, P2 = 1, P3 = 0.**
These retain F01/F02/F03 identifiers; they are not a QUALITY finding count.

| Finding | Leaf | Location in the new candidate | Disposition | Confidence |
|---|---|---|---|---|
| F01 - P1 | A08.1 | `lib\orientator-routing.sh:40-50,83,98,123-124` | OPEN: subject/prohibition words still become SHIP authority | 10/10 |
| F02 - P1 | A08.1 | `lib\orientator-routing.sh:49-74,82,123-124,215-221` | OPEN: indirect information/assessment requests still become deploy/high | 10/10 |
| F03 - P2 | A08.3.c under A08.3 | `skills\plan\SKILL.md:283-291` | OPEN: native-backslash global report escapes the history-only guard | 10/10 |

### F01/F02 share the action-token authority assumption

The original clause-negation reset and direct safety-question cases are repaired.
The remaining failures nevertheless share the same algorithmic assumption:
the first recognized operation token is treated as the requested operation,
without establishing its grammatical role or affirmative authority.

For `The release must not be deployed; explain the plan.`, the loop returns
`ship` at the subject `release` before reaching either `not` or `explain`.
For `Release notes: explain the deployment process.`, the topic heading supplies
`release`; colon removal does not establish that it is a noun/topic rather than
an imperative. Both consumers return `/li:cycle --from SHIP`, confidence `high`.
Expected behavior is the explicit read operation or safe clarification, not SHIP.

For `I want to know whether it is safe to deploy this release.` and
`I need advice on whether to deploy this release.`, question recognition applies
only at clause start. The initial `I` consumes that position; the inquiry/advice
context is not retained. `deploy` later becomes the first recognized operation,
and the consumers return `/li:cycle --from SHIP`, confidence `high`. Expected
behavior is assessment/read or safe clarification. Absence of `?` is not
affirmative deployment authority.

This is the action-token scan/early return, **not** the final bug/broken symptom
fallback. A repair should establish operation versus topic and scoped
prohibition/inquiry before returning a write recommendation, rather than add
four phrase exceptions. Preserve genuine direct mutations, retained read routes,
useful symptom triage and caller IFS; ambiguity may remain unclear/low.

No returned workflow was executed. These are incorrect recommendations, not
observed deployment, production effects or proof of bypassing later host controls.

### F03: slash-only recognition does not cover native Windows history paths

The original instruction inconsistency is removed: PLAN now executes
`workflow_resume` and selects a cycle report. The new refusal nevertheless checks
one forward-slash literal and `${analyze_report_path##*/}` before the parent
directory identity comparison. A native backslash spelling has no `/`, so the
basename condition is false and that comparison is never reached.

Using the real writer to record a historical selected pointer, then the actual
extracted PLAN preparation block, the native absolute spelling
`$Target\.claude\runtime\state\analyze-report.md` returns **exit 0**, no diagnostic,
and selects that same native global path. This occurs with the global file both
absent and present. Native path resolution independently confirms that the
selected output is the global history location, not a different filename.

Expected: **exit 2/INCOMPLETE and explicit reconciliation**, exactly as for
repository-relative and drive-qualified forward-slash spellings, whether or not
the report exists. The new selected-report contract must not ask ANALYZE to
produce at the history-only location.

The negative probes stop after selection; no synthetic producer overwrites this
global report. Ledger/target snapshots and the present stale-GREEN sentinel are
unchanged by each refusal check. Thus the finding proves wrong selection and
missing refusal, not an observed overwrite or release clearance. A bounded
repair should recognize supported native path identity before selecting output;
it does not authorize changing P03/P07, default homes, a report schema/parser,
ADR-0004 advisory semantics or P05 requirements.

## Exact independent routing evidence

Each request used the actual producer and both consumers:

```bash
source "$LINTEL_SOURCE_ROOT/lib/orientator-routing.sh"
actual=$(classify_intent "$request")
workflow=$(match_workflow "$actual" cycle)
confidence=$(score_confidence "$actual" "$workflow")
```

`safe` accepts research/research-dive/high, review/review/high or
unclear/cycle/low; it does not demand a single enum where clarification is
appropriate. Rows 1-6 preserve the exact original requests. Rows 20-21 repeat
the indicated inputs with caller `IFS=:` and verify that IFS is unchanged.

| # | Exact request | Expected | Actual intent / workflow / confidence | Result |
|---|---|---|---|---|
| 1 | `Do not change the release plan; explain it.` | research | research / `/li:cycle --mode research-dive` / high | PASS |
| 2 | `Do not edit the deployment code; describe the release process.` | research | research / `/li:cycle --mode research-dive` / high | PASS |
| 3 | `Is it safe to deploy this release?` | research | research / `/li:cycle --mode research-dive` / high | PASS |
| 4 | `Do not build the release.` | unclear | unclear / `/li:cycle` / low | PASS |
| 5 | `Review the release plan.` | review | review / `/li:review` / high | PASS |
| 6 | `Deploy the reviewed release.` | deploy | deploy / `/li:cycle --from SHIP` / high | PASS |
| 7 | `The release must not be deployed; explain the plan.` | safe | ship / `/li:cycle --from SHIP` / high | FAIL |
| 8 | `Release notes: explain the deployment process.` | safe | ship / `/li:cycle --from SHIP` / high | FAIL |
| 9 | `I want to know whether it is safe to deploy this release.` | safe | deploy / `/li:cycle --from SHIP` / high | FAIL |
| 10 | `I need advice on whether to deploy this release.` | safe | deploy / `/li:cycle --from SHIP` / high | FAIL |
| 11 | `Do not change the release plan, but explain the deployment process.` | safe | research / `/li:cycle --mode research-dive` / high | PASS |
| 12 | `Don't change the build or release notes; review the plan.` | safe | review / `/li:review` / high | PASS |
| 13 | `Is the plan ready for release, or does it need review?` | safe | research / `/li:cycle --mode research-dive` / high | PASS |
| 14 | `Could you deploy the reviewed release?` | safe | unclear / `/li:cycle` / low | PASS |
| 15 | `Review the change then deploy it.` | unclear | unclear / `/li:cycle` / low | PASS |
| 16 | `Implement release-note validation.` | build | build / `/li:cycle` / high | PASS |
| 17 | `Fix review comments.` | fix | fix / `/li:cycle --mode hotfix` / high | PASS |
| 18 | `Release v2.` | ship | ship / `/li:cycle --from SHIP` / high | PASS |
| 19 | `Please deploy the reviewed release.` | deploy | deploy / `/li:cycle --from SHIP` / high | PASS |
| 20 | `Do not change the release plan; explain it.` | safe | research / `/li:cycle --mode research-dive` / high | PASS |
| 21 | `Deploy the reviewed release.` | deploy | deploy / `/li:cycle --from SHIP` / high | PASS |

No broader language search followed these four bounded counterexamples. The
retained routing wrapper independently passed all 183 assertions, including the
original 54; the separate unchanged eight-scenario mechanical wrapper passed,
including affirmative deploy/ship, Swedish, risk and escalation behavior.
Those positive suites do not override the independent counterexamples.

## Actual PLAN preparation, persistence and consumers

The independent probe extracted exactly the two Bash blocks from PLAN Step 8;
it did not substitute manually selected report pointers for the caller. Its
26 fresh child shell invocations each have an allowlisted environment, effective
path preflight, exact script/stdin, stdout/stderr, exit and duration receipt.
There are **47 recorded observations, 45 PASS and 2 FAIL**, including setup and
preservation checks; these are not 47 lifecycle unittest methods.

| Discriminator | Observed result | Scoped disposition |
|---|---|---|
| Two initiatives, no prepopulated pointers | Actual P07 bootstrap, `workflow_begin` and PLAN phase; approved alpha and DRAFT beta maps, original T007/T019 IDs | PASS |
| Actual prepare, produce, cold persist | Real `workflow_resume`, work-map/P04/P03 context, report writes and `state_append ANALYZE`; distinct cycle reports | PASS |
| Source/target/history preservation | Original maps/tasks unchanged; ledger prefixes retained; other report and stale global GREEN unchanged | PASS |
| Cold return to alpha | Same map, report, generation/digest/context and required policy; no extra append or phase completion | PASS |
| Actual selected consumer/P05 binding | Selected pointer read; `workflow_inspect --package T019 --leaf T019 --acceptance <selected-report>` equals real `bind_work`; global report excluded and `release_clearance=false` | PASS |
| Wrong-map preparation | Exit 2, `selected map is a different initiative`; no target/report/ledger write | PASS |
| Required-profile same-mtime drift | Verified required profile first; synthetic pack changed with mtime retained; exit 2/`PROFILE_DRIFT` before target write | PASS |
| Missing persisted report | Actual preparation plus persistence returns exit 2, `analysis report was not persisted`; ledger unchanged | PASS |
| Legacy relative path, absent/present | Both exit 2 with history/reconciliation diagnostic; target unchanged | PASS |
| Legacy drive-qualified forward-slash path, absent/present | Both exit 2 with history/reconciliation diagnostic; target unchanged | PASS |
| Legacy native-backslash path, absent/present | Both exit 0 and select the same global history location; target unchanged | FAIL (F03) |

For each positive report, only its prose is synthetic: `legs_checked: []`,
explicit incomplete semantic legs and `verdict: INCOMPLETE`. Preparation performs
real profile verification; the handoff carries the original selection/reference
into a fresh process, where persistence verifies again. Both canonical phases
remain PLAN and each gets one initial INCOMPLETE ANALYZE entry, not PLAN DONE.

The actual invocation sequences are retained as `command.sh` and stdin hashes.
They comprise: bootstrap/begin without pointers; extracted preparation plus
real `workflow_inspect` and an explicitly synthetic INCOMPLETE writer; extracted
persistence in a separate process; cold selected reader and P05 binding; and
the focused refusal cases above. Legacy setup uses
`state_append ANALYZE INCOMPLETE "analyze_report_path=$LEGACY_REPORT"` before
capturing the unchanged snapshot and running actual preparation.

This is not live semantic DEFINE/PLAN analysis, operator-question evidence,
automatic report-identity parsing, or proof of carrying accepted findings across
a model rerun. No new source schema exists. ADR-0004 remains advisory; P05's
immutable v2 QA requirements and later-rejection rules are unchanged, not newly
cleared by this pointer test. The prior actual writer/latest-reader/QA/SHIP
coverage is historical independent evidence, not a run in this continuation.

## Per-leaf disposition and stage boundary

Prior scoped PASS below means the bounded evidence already recorded in
`9faebd2b`, not a new full acceptance or a rerun here. All QUALITY entries remain
NOT STARTED. Missing original proofs cannot be waived by closing local findings.

| Original/refinement leaf | SPEC | QUALITY | Evidence boundary |
|---|---|---|---|
| A08.1 | FAIL | NOT STARTED | Six originals repaired; F01/F02 class-level counterexamples remain. |
| A08.2.a | PASS (prior scoped) | NOT STARTED | Earlier actual identity/transition/framing/error fixtures; no source delta or rerun here. |
| A08.2.b | PASS (prior scoped) | NOT STARTED | Earlier actual status-grounded footer cases; no new footer acceptance. |
| A08.2.c | UNVERIFIED | NOT STARTED | Actual host phase-loop dispatch remains unobserved. |
| A08.2 parent | BLOCKED | NOT STARTED | Orchestration and preservation prerequisites still unmet. |
| A08.3.a | PASS (scoped) | NOT STARTED | Prior parser/selector coverage; current actual selected context/original IDs/P05 binding passes. |
| A08.3.b | UNVERIFIED | NOT STARTED | Current cold resume and required-profile drift pass; full generation/digest/cross-target matrix not established. |
| A08.3.c | FAIL | NOT STARTED | Actual PLAN caller substantially improved; F03 native-path refusal fails. Other consumer/semantic proofs remain incomplete. |
| A08.3 parent | FAIL | NOT STARTED | F03 and incomplete profile/consumer proof prevent acceptance. |
| A08.4 | PASS (prior scoped) | NOT STARTED | Earlier actual ADR/discovery/jobs cases unchanged; not rerun. |
| A08.5 | BLOCKED | NOT STARTED | Additional two-initiative/cold-process evidence does not close inherited interrupted-recovery preservation. |
| A10.1 | UNVERIFIED | NOT STARTED | No actual host question interaction; synthetic binding evidence is not permission/runtime proof. |
| A10.2 | UNVERIFIED | NOT STARTED | No live maintenance/migration/research intake comparison; optional venture lens remains instruction-only evidence. |
| A10.3 | UNVERIFIED | NOT STARTED | Current PLAN handoff is bounded and F03 remains; all alternative entry points are not accepted end to end. |
| A10.4 | PASS (prior instruction-only) | NOT STARTED | Plan-tune remains dormant, not a newly active settings reader. |
| A13.3 advisory option | UNVERIFIED | NOT STARTED | No freeze activation or new observation-learning execution. |
| A13.1 | DEFERRED/BLOCKED | NOT STARTED | Producer-interface gate remains; not an unrequested omission. |
| A13.2 | DEFERRED/BLOCKED | NOT STARTED | No promotion, global learning write or configured-sink acceptance. |
| A13.4 | DEFERRED/BLOCKED | NOT STARTED | No event/lesson/incomplete-log roundtrip acceptance. |

There is no whole-46-file QUALITY, integration signoff, or quality-start
authorization. No broader audit was undertaken after the counterexamples.

## Commands, isolation and raw evidence

The following are the actual reviewer entry commands; `$Private` and
`$FrozenCheckout` replace private absolute paths only. Each run has its own
retained fixture under `p08-routing-plan-recheck-evidence`.

```powershell
python -I -S -X utf8 "$Private\p08_recheck_runner.py" --repo "$FrozenCheckout" --slot r01 --probe "$Private\p08_recheck_operation_probe.sh"
python -I -S -X utf8 "$Private\p08_recheck_runner.py" --repo "$FrozenCheckout" --slot r02 --suite "tests\unit\intent-operation-boundary.sh"
python -I -S -X utf8 "$Private\p08_recheck_runner.py" --repo "$FrozenCheckout" --slot r03 --suite "tests\unit\orientator-mechanical-routing.sh"
python -I -S -X utf8 "$Private\p08_recheck_runner.py" --repo "$FrozenCheckout" --slot r04 --python-probe "$Private\p08_recheck_plan_probe.py"
```

Shell probes use `bash --noprofile --norc -s` with recorded literal stdin;
wrappers use `bash --noprofile --norc <frozen-wrapper>`. The PLAN probe runs
`python -I -S -X utf8 <private-probe> --source <frozen-source> --slot <r04>`.
All four runs were serial.

| Run | Independent result | Exit | Child duration |
|---|---|---|---|
| r01 | 21 routing cases: 17 PASS, four FAIL; caller IFS retained | 1 | 5.953 s |
| r02 | 183 routing assertions, zero failures | 0 | 43.422 s |
| r03 | Eight retained mechanical scenarios, all PASS | 0 | 3.735 s |
| r04 | 47 PLAN observations: 45 PASS, two FAIL; 26 child commands | 1 | 290.219 s |

No zero-run, skip, setup error or cleanup failure is counted as green. The failing
exits are real assertion failures. Positive and expected-refusal child commands
are not substituted for their aggregate failures.

Each run sealed all **959 tracked checkout files** and copied their immutable
working bytes into its own disposable source. Each child environment was
allowlisted: synthetic HOME, USERPROFILE, HOMEDRIVE/HOMEPATH, app data, XDG
config/data/state/cache/runtime, temp, LINTEL_HOME and GSTACK_HOME; intentional
source/target/interpreter inputs only. Inherited LINTEL/CLAUDE/GSTACK, Git,
BASH_ENV/ENV and Python execution redirects were not carried over.

Before each top-level test and every PLAN child command, actual helpers resolved
and recorded **32 contained paths**, including packs, pointer, profile, audit,
jobs/registries, state and session roots. Git global/system configuration,
attributes, template, hooks and signing were isolated; no global setting was
changed. jq was used read-only on per-process PATH after SHA-256 verification:
`a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`.
No tool installation or PowerShell test/policy override occurred.

Original and copied source manifests remained unchanged after all four runs
and were rechecked before report authoring. Router and routing test working files
are LF; PLAN and lifecycle Python working files are CRLF, with LF Git blobs.
The four working hashes match the disclosed candidate/p8r13 hashes exactly.
Source checks used per-command checkout-equivalent `core.autocrlf=true`, separate
from fixture Git isolation; no normalization/reset occurred. This is **not**
a raw-LF blob claim. All four synthetic temp directories were empty; named
source/home/target/command fixtures remain intentionally retained privately,
not claimed as deleted. No broad cleanup was attempted.

| Evidence artifact | SHA-256 |
|---|---|
| Prior isolation utility reused | `4202cc9ddb52d96a3dbb9c8b00589f88e67943146e7a455d6ba5a5f8ac579d7d` |
| Recheck source-sealing driver | `f02c20a5ee4562afd7ccf89228f8f9b2c035c5809796f7215cf3d7a48ca19cae` |
| 21-case probe/stdin | `254a806ada419ff6e1349d11ad6df070bf405091eeeef535db1bb61e5af2a822` |
| Independent actual PLAN probe | `b03699c904b9d9eae15cbe944cc87dd9b8e10941b227196107bb1b1ec13d6df0` |
| Identical 959-file manifest, r01-r04 | `c698a3b2b41bd7aebe46a8fc6c697a260370c974fc122b8a1539c1a90ce65a9f` |
| r01 exact input/output | `603b732bb5c2dff8724abce8b66878c6720eb794c12e8db748007a42d15ca4e5` |
| r02 assertion output | `e96020cebe5ae48f2a38ed8195b63ae19ca29874005c4aa8bb4c91633c35df9b` |
| r03 scenario output | `a65d60cc49f1b2203f9dc25aa5954db5c69a74487ddcdfba89e9324200d5aba3` |
| r04 observation output | `3915a5561620bfa1b96dfdc36976d56ba4d67b95a727b1f4a07da31e6f6e3694` |
| Extracted actual PLAN preparation | `776cab357c8d032fe758360fbdbb7dc2361fce181758e9f6dba06b3864e0ea5f` |
| Extracted actual PLAN persistence | `c5de9fdc0001861d00bb4993510b7bb2c25bcbe2346c8d0979e92b05158b6f22` |

## Separate unresolved gates and stop

Historical p8r4 lifecycle 29/observation two positives, p8r5 **14/18 failed
preservation aggregate**, p8r6 same-depth unchanged-control reproduction, and
**22/23 context-safety** remain their original implementer/control evidence.
Checkpoint reservations at 268/278/277/290 characters and the Git bisect
ref-lock at 283 characters are separate inherited groups, not a newly attributed
P08 defect or proven common root cause. No rerun, shorter-root acceptance,
P03/P07 repair, global long-path setting or missing-proof waiver occurred here.
Their original owner retains the work.

**shell27 remains INVALID authorized evidence; real-home effects remain UNKNOWN.**
No actual-home inspection, cleanup or rollback was authorized or performed.
p8r1 zero-run/setup and p8r2 fixture-unlink/teardown errors remain failures, not
P07 operation evidence or retrospective passes. Builder p8r7/p8r8 RED, p8r10
fixture mistakes and p8r11 guard defect remain historical. Builder p8r13's
183/eight/33 passing counts and timings are not this reviewer's runs; the current
retained suites were independently rerun as r02/r03, not the full 33-method suite.
The earlier review's 54 retained passes, three independent failures and 29-method
in-flight pass remain unchanged in `9faebd2b`.

The two original post-run cycle authority sentences remain unexecuted host
instructions, and wrapper mode staging is distinct from explicit Bash execution.
The prior capacity/discovery shape-oracle inspection and producer cases are not
new wrapper runs here. Source metrics/token priors are not observed host usage
or capacity.

Joined distribution/preflight closure, including trusted `lib\workflow.sh`,
generated/native-kit reconciliation and P14's installed canonical caller/child
bridge, remains coordinator-owned and pending. P10 default-store/cleanup and
separate F01 migration work retain their owners. Actual Python 3.9, other OSs,
live model/question/client behavior, semantic report identity checking and
operator-accepted finding carryforward remain unobserved. No synthetic grammar
or binding result supplies that proof.

Return the three open findings to the original builder through MasterSession.
This sole report-only checkpoint is to be committed directly on `8bde7005`;
its immutable SHA, sole parent and clean status are supplied in the handoff.
Preserve the old report/ref and all failure evidence. Stop for a separately
authorized immutable candidate/combined checkpoint: this report authorizes no
integration, QUALITY start, A13 work, release or real-home recovery.
