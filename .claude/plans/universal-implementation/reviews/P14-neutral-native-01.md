# P14 neutral native implementation review

**SPEC PASS, followed by QUALITY PASS.** Open P1/P2/P3 findings: 0/0/0.
This accepts the exact neutral implementation for subsequent real review
consumption. It does not close the native comparison, A24, final A23 or SHIP.

Reviewer: recovery coordinator `88aecc43-40f9-41d4-8947-6c2fb0a55481`.
Actual implementation builder, both ID and context:
`7169bb1a-e2f9-46b0-950d-4ebf24e29ce0`. Original T001 planning belongs to
`7742184c-1e60-424e-a570-7937dd6eac72`; the reviewer implemented neither.

## Exact scope and provenance

- Trusted source: `c544fd07491b1bf6c16363b60470cb5ed77ba3b2`.
- Original neutral target: the controller's
  `files\p14-native-01\cases\neutral\target`.
- Original map/package/leaves: `work.json`, P1, T001/T002/T003.
- Attempt: `neutral-7169bb1a-business-01`.
- Ready packet SHA-256:
  `4013742e23a1a02469d210560197ed826c796c15b7c25c6d49888ff29ef161e9`.
- `inventory.py`: 5,849 bytes, SHA-256
  `4b68c09baebbce9257e36ec7e83986cd8431b5bc617dad2cdf84968e9a44f36d`.
- Final `plan.md`: 30,751 bytes, SHA-256
  `254f1d35f1b3ff25f654caad3cea65bffee4f3f075e321f2481ea3a1e049a2ff`.
- Final context canonical digest:
  `87d73b55b626ab6deb6c19960ba275a8311ab3336f9568212295f49262abbcc2`.
- Final QA raw SHA-256:
  `e9fd124462405fb2601103eab52184272e817d36875aa7262f36a2a4ba30a4cb`.

The reviewer read the complete original spec, map, prompt, AGENTS, authored
plan, implementation, frozen oracle, actual neutral profile fields, context,
QA, business observations and transport receipts. The archive's exact hash
and Git commit comment, all 565 exported raw source files and all 18 approved
fixture raw identities were independently checked. No blanket source/data EOL
equivalence substituted for exact bytes.

All 20 ready-packet files plus four additional instruction/environment/transport
files remained identical before and after reviewer execution. The selected
code and seed equal their context snapshots. The final QA retains the setup's
literal mandatory typed `inventory-business` obligation and exact context.

## Complete specification assessment

| Requirement | Result and discriminating evidence |
|---|---|
| R1 | PASS. `inventory.py:24-61,64-89` rejects duplicate keys, non-objects, missing/extra fields, invalid UTF-8, blank lines, noninteger/boolean/nonfinite values, invalid ASCII IDs/SKUs and more than 1,000 physical lines. Inclusive number/count boundaries pass. Additional probes cover exact maximum identifier lengths, 1,000 identical lines, invalid UTF-8, both infinities, 1.0 and a non-ASCII ID. |
| R2 | PASS. `inventory.py:80-89` validates each repeated record, admits identical ID tuples once and rejects conflicting tuples before publication. The unchanged oracle exercises both conflict dimensions and repeated seed events. |
| R3 | PASS. `inventory.py:91-98` constructs only the required integer-valued shape, retains zero/negative totals and orders SKUs before deterministic compact JSON serialization. Seed and reversed-input output bytes agree. |
| R4 | PASS. `inventory.py:101-161` checks normalized and existing-file identity, validates fully before publication, diagnoses failures, stages in the destination directory and returns 0 only after replacement. The actual oracle checks missing/invalid input and same-path alias preservation; the reviewer also verifies a real hard-link alias refusal with unchanged bytes. |
| R5 | PASS. Original T001 records dictionary reconciliation versus sorting/grouping and the actual storage/complexity trade-off. The implementation matches. Resolved neutral advisory fields and empty additional policy sources do not mandate its algorithm or optional staging choice. |
| R6 | PASS for the completed review stages. The unchanged oracle actually ran, exact count/exit/raw evidence is preserved, and this distinct reviewer performed SPEC followed by QUALITY. Actual host corroboration and producer/latest-reader/QA consumption remain separate delivery gates. |

P1 covers all three original leaves. T001 retains its real original author;
T002 is implemented by the explicitly released continuation. T003 remains
unchecked until the controller consumes actual review/QA and finishes the
original local workflow. Neither task progress nor a private PASS is clearance.

The actual profile is generation 1 `p14-native-neutral`, bundled `_default`
1.0.0, digest `eebc79dd3a11f21b36ea3ae72f65575408370e293d901e4ef9cc19e0fab80460`.
It declares advisory compliance, no company hooks/voice gates and no additional
algorithm source. The required policy is explicitly not required, not a failed
policy load treated as neutral. R1-R6 and independent review remain mandatory.

## Subsequent whole implementation quality

Validation, reconciliation, alias checks and publication have distinct small
functions and explicit failures. Deduplication occurs after validation of every
physical line, preventing invalid repeated records from being silently ignored.
Signed integer totals and deterministic serialization do not depend on input
order. Expected work is O(L + K log K) record operations and O(U + K) retained
records, excluding line/output bytes; the plan states those limits accurately.

Input is read-only. Only actual missing-destination metadata is treated as
absence; other errors remain visible. Temporary output is invocation-owned,
both handles close before replacement, and cleanup failure is diagnosed rather
than hidden. Atomic staging is an optional neutral implementation choice,
not a claim of crash durability or protection against hostile concurrent path
retargeting. No strict-only policy, service, dependency or global change was added.

The oracle's cases distinguish the real seed arithmetic, duplicate conflicts,
schema/type bounds, deterministic bytes and refusal preservation. Independent
edge probes agree with the implementation, not merely repeated expected labels.
No actionable correctness, maintainability, error-handling or scoped coverage
finding remains. Source and evidence limitations remain explicit.

## Actual verification and limitations

The controller's original oracle run is 11 methods, zero failures/errors/skips,
exit 0. The reviewer independently reran that unchanged 11-method business oracle
against the same code and added eight separately recorded direct probes.
These are not 22 distinct test methods or a newly invented aggregate.
The oracle's original `category: local-oracle` and `native_scenario: false`
remain unchanged; actual native actor provenance is supplied separately.

Reviewer evidence is under recovery88's `files\p14-neutral-review-01`:
`before.json`, `after.json`, `verification.json`, actual command/raw-stream
records, and separately authored `spec-stage.json` then `quality-stage.json`.
New reviewer scratch is only the declared neutral-case siblings
`review-88-business-01` and `review-88-probes-01`. No target/source file was edited.
Execution used the inspected original synthetic environment and Python 3.11 on
Windows; Python 3.9 grammar was checked, not a 3.9 runtime or other OS/client.

The plan-only sync actor, rejected follow-up, explicit extra neutral context and
later successful same-background-context follow-up retain their actual history.
Controller-local actor receipts are attributed to that observer, not claimed as
independent parent API queries. Source-guard and bookkeeping failures remain;
actual model, token usage and cost stay unknown. No causal performance/ROI claim.

## Consumption boundary

The accompanying reviewer-authored v2 decision uses exact final context and
unchanged business QA, declared provenance, all three required controls and
T001/T002/T003 coverage. It binds only existing immutable supporting files;
the original plan remains protected through the normal work-acceptance contract,
not a redundant raw mutable progress hash. The decision is not self-corroborated.

The distinct controller must record its actual observation of this returned
review, bind that host receipt to the full decision digest/attempt/actors, and
use the real producer/latest-reader/same-context QA before accepting neutral.
Keep current inputs frozen through consumption. Only legitimate original task
progress may follow without changing acceptance; new substantive plan prose
would require a fresh applicable context/review. Remaining rapid/strict work,
fresh strict recovery, whole A24/A23, all denied routes and SHIP remain open.
