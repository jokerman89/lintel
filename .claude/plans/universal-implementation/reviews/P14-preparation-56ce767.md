# P14 bounded preparation review

**Preparation SPEC: FAIL. Whole preparation QUALITY: NOT STARTED.**
One source finding, P2 R01, plus the retained E01 entry failure. Native actors
are not released. This review is by recovery coordinator
`88aecc43-40f9-41d4-8947-6c2fb0a55481`, distinct from preparation owner
`8fa44739-f562-4213-a6c4-fb7719fc8c9e`; it is not builder self-review.

## Exact scope

Product `56ce767df652a5c86334e76c469945079e94e3a3`, sole parent
`9f8885be132b5af0f579dd64019d32aef5501d45`, changes only twenty new test/
fixture paths. Report-only child `f106f007cc8b3549a1460289eb60c9c35beb4b8a`
adds `reports/P14.md`. All twenty product paths and the complete report were
read. No production provider or original task file was changed by that owner.

The report is 366 LF lines and 20,976 Git bytes, SHA-256
`1ac711b540ecb653360347755ac3e4d3e7f9ad634175861244576acd22f3d345`.
The returned checkout hash matches after accounting only for checkout CRLF;
actual fixture and evidence bytes were not normalized.

## R01: regression success depends on unfinished initiative state

**P2, confidence 10/10.** In
`tests/integration/universal-profile-scenarios.py:236-245,396-401`, the fixture
compares the entire current authority files to a historical commit and then
requires all A24 leaves and A23.4/.5 to remain incomplete. The ordinary `.sh`
entry is automatically discovered by the existing integration runner.

Consequently legitimate completion of this initiative makes its own new test
fail. This is different from preserving original IDs, requirements or an
immutable per-experiment input. It cannot be fixed by leaving completed tasks
unchecked or treating the final test failure as native non-acceptance.

The coordinator copied the actual current work map/spec/plan/prompt to an owned
synthetic root, changed only the existing A24.1 checkbox, and used the real P08
reader. It correctly retained A24.1 and reported it complete. Direct invocation
of the unchanged C03 method then failed its fixed-incomplete assertion before
any later fixture operation. Evidence:
`verification/p14-legitimate-progress-probe-01`, actual probe exit 0 recording
that expected method failure. This was a bounded method/input probe, not a
rerun of the full fourteen-method preparation suite or a native scenario.

**Required correction:** test original identity and before/after preservation,
not permanent incompletion. Separate historical experiment provenance from
mutable current initiative progress. Preserve deliberate selected-source drift
refusal and requirement/approval checks; use existing work/source semantics,
not a new task parser or broad exclusion. A normal integration test must not
silently run historical helpers instead of its declared current subject.
Add paired legitimate-progress and requirement-change cases. Preserve all
historical preparation locks and do not repin old native observations.

## E01: ordinary shell entry remains unverified

The owner-reported no-argument entry failed one of fourteen methods with Git
exit 128 writing an object at the rapid-development target. The coordinator
read the exact argv and verified its retained hashes:

- `0078.json`: `ef72963ecf45295053dbefe055f07e1c9e075a06c4162cb9130874dde004e4a1`
- `0078.stderr.log`: `33e70f521b19b7b3223418b106057e9640e1a11a36dad8351529abbb37a40af2`

The separate explicit-root run used both a different path and a different Git
executable. Its fourteen passing methods do not establish the failed entry.
No universal numeric limit or unique cause has been proved by that comparison.

The original owner needs a bounded fixture-Git correction and same-dimension
entry verification. A command-local Windows Git long-path option may be applied
to owned synthetic repositories with the same inspected executable/root
dimensions; no global configuration, shorter test root, source-provider change
or P10 retry is released. Preserve the original failure and exact dimensions,
test a real matching positive, and keep unsupported/error outcomes explicit.
This is a test-harness correction, not a new Windows compatibility initiative.

## Remaining specification assessment

| Prepared boundary | Assessment |
|---|---|
| Identical business task | R1-R6, T001-T003, seed, exact output shape and finite oracle are shared across profiles. No native implementation is supplied. |
| Real profile effects | Existing P07 fields/provenance and selected policy text distinguish advice from strict publication/recovery outcomes. Policy explicitly accepts local equivalents; no installed hook is claimed. |
| Proportionate design | In-memory, grouping and transient SQLite are real choices. Differences are not forced; neutral/rapid retain business acceptance and independent review. |
| Existing contracts | P03/P05/P07/P08/P09 APIs are used rather than another scheduler, task store or review selector. Preparation records are non-clearing. |
| Oracle and negative layers | Eleven business methods, two atomic methods and two oracle checks are separate. Toy atomic output is not inventory success; the unimplemented seed is deliberately failing. |
| Cold continuation plan | One actual implementer per profile, strict PLAN pause and a genuinely fresh strict context, then distinct review. No actor or verdict is borrowed. |
| Source versus native evidence | Unknown native timing/usage/interventions remain unknown. Preparation counters and returned data are not native execution or review. |
| Automatic entry and legitimate progress | Open E01 and failing R01 above prevent preparation acceptance. |

Builder fourteen-method, 148-command and oracle results retain their builder
attribution. The coordinator did not rerun them or perform native operations.
No P05 decision/corroboration record, source fix, installer, dependency, network,
UI, release or other worktree mutation was performed during this review.

The rejected hook-override commit command is a separate recorded host correction.
Normal source-checkout commits must retain existing controls. Synthetic fixture
Git settings must not become product-commit settings.

## Return to the original owner

Repair only the owned preparation harness, necessary focused fixture controls
and report. Preserve the equal business request, existing oracle assertions,
profile policy, old locks/failures and all unrelated accepted sources. Return
an immutable candidate for complete preparation SPEC before whole QUALITY.
No native context, new reviewer, original task closure or installation gate is
authorized by this rejected preparation checkpoint.
