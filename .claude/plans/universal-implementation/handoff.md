# Universal implementation handoff

Updated 2026-09-20 by MasterSession.

## Durable state

- User-selected initiative: all A01-A26, preservation-first, with active Swarming integration.
- Implementation authority: current 2026-09-20 request; review audit completion is not build completion.
- Audit preserved in commit `74290e0`; 25 exact source files verified before import.
- Local separate SHA-256 backup and verified full-history Swarming bundle exist in the
  MasterSession's private session artifacts; no personal paths or credentials are needed
  to use the committed evidence.
- Baseline `origin/main`: `28061e434be455ca02f135b73244eaf4f73f3a69`; anonymous public
  API verification confirmed that same current main on 2026-09-20 without credentials.
- Swarming: `codex/swarming-work` at `275a35447c4ad271e05816ade43ac48f1acec24f`;
  original main checkout and four older Swarming worker worktrees remain untouched.
- Integration branch: `jokerman-microsoft-lintel-harness-preview`. Its historical branch
  label is not account authorization.

## Active work

The approved implementation trio, concrete first-wave cards and work map are committed
as `21261f1`. Independent plan review identified one P2 missing-dispatch-binding condition;
MasterSession supplied per-leaf dependencies, paths and executable checks before dispatch.
The reviewer was a synchronous native task; follow-up messaging to that instance is not
supported, so no second independent pass is claimed.

P01-P04 started in isolated app-native worktrees from `21261f1`; P05-P07 started
from the reviewed historical merge `40c2795`. Current implementation ownership:

| Package | Session ID | Current boundary |
|---|---|---|
| P01 trusted helpers | `b3853be7-dbbe-4161-9566-7e7d2c50e05e` | ACCEPTED and integrated `a2ef318`; idle, combined P07 gate remains |
| P02 sync binding | `2e21aa98-3b40-46e7-885d-2ec4161ec35d` | ACCEPTED and integrated `39561c0`; idle, no real private sync activated |
| P03 context safety | `9f06eebf-a3ee-4867-95ad-eb6e1d22a6d5` | ACCEPTED and integrated `9a1cf17`; idle, downstream consumer/host gates separate |
| P04 Swarming | `a8960a09-fcd7-4652-a9b6-74ad6a94a029` | Component ACCEPTED/integrated `490a0f4` + report history `8964267`; idle until explicit A22.7 |
| P05 review evidence | `2329e71f-cd9e-473b-94cf-41c579c29a88` | ACCEPTED by `33eac071`, integrated `c5c8f86`; current profile/review and focused gates pass, idle |
| P06 host adapters | `324863ff-e7cf-4abf-b449-04dd0f096170` | Component ACCEPTED/integrated `36593cd`; provider `7425960`, final review `1067da29`; idle |
| P07 profile context | `b9352dfe-1c1e-4ea3-b7d9-0fd008d39b3d` | Long-path repair ACCEPTED by `a7450597`, integrated `c344133` with reports; joined checks pass, idle |
| P08 work lifecycle | `f2c305ac-e8b0-4b02-b6cd-c7de598964cf` | Implementing ready A08/A10 from `5c3e753`; A13 installer observation waits for P10 seam/fixtures |
| P10 installer lifecycle | `5ea6c88c-68c1-4712-8f55-adecdfe0061f` | `62ffb9a` rejected by `1d871338`; original owner receives bounded F01 migration-row repair |

All are `lintel-builder` sessions with explicit ownership, local commits, report paths
and no remote authorization. P01/P02/P03 plus the owned P04-P07 components are accepted.
P04 A22.7 and the final cross-component/client requirements remain open.
Do not merge another product batch merely because its original tests are green.

Reuse these independent reviewer sessions for the next immutable candidate; they never
repair their own findings. All prior reports remain preserved in `reviews/` and Git:

| Package | Current review target / next gate | Independent reviewer session |
|---|---|---|
| P01 | Final `f078165`; SPEC/QUALITY PASS at `041417a`; idle | `d699f463-ee4d-4950-9b9d-98f35e96f689` |
| P02 | Final `1b6153f`; SPEC/QUALITY PASS at `9bdaeb4`; idle | `da23fa6f-499b-4011-b39b-a632312a8800` |
| P03 | Final `2840012`; SPEC/QUALITY PASS at `500adb3`; idle | `efd3f877-550a-4ef0-9009-ed71b95b01ab` |
| P04 | Final `279dfc9`; component SPEC/QUALITY PASS at `aa73651`; A22.7 open | `ed672f58-2e85-42e2-b1b2-0635ba5b2325` |
| P05 | Final `33eac071` accepts `b023e8c`; integrated `c5c8f86`; earlier rejections retained | `6ed9c7df-4845-4d70-88c7-f0746ab28059` |
| P06 | Final `1067da29`; complete component SPEC/QUALITY PASS at `7425960`; integrated | `d2a89ac3-151a-4dc0-ab09-1f3a62465cab` |
| P07 | Final `a7450597` accepts `4d001463`; integrated through `56de830`, earlier `a8de574`/`3d8e715` preserved | `a7d78944-c02c-4909-a060-2c4f2a754b00` |
| P10 | Report `1d871338` SPEC FAIL/F01; quality NOT STARTED; new repair checkpoint pending | `1578dfd8-f239-4eba-989b-3c4bde3e5792` |

## Accepted local integrations

P01: complete worker/final-review history merged as `a2ef318`. Source matches independently
reviewed `041417a`; all eight leaves passed spec and full bounded quality. The reviewer
ran 51 tests plus corrected numeric/record probes and new failure/ownership probes.
Eight selected joined-tree tests passed with jq: hostile resolvers, retained policy,
numeric/path metadata, vault, ADR index ownership and updater failure/fallback.
Registration is unchanged and dormant hooks remain dormant. P07 is now integrated;
the copied-fixture repair and joined source/profile checks are recorded below.

P02: complete worker and final-review history merged as `39561c0`. Source exactly matches
independently reviewed `9bdaeb4`; 60 scenarios/875 assertions passed independently.
Joined A26.4 run completed with 31 scenarios/278 assertions/zero skips. Wrong destination,
fetch refmap, source alias and staged-role deletion findings are all closed. Actual
private endpoints, credentials and non-Windows runtimes remain untested.

P03: complete worker/final-review history merged as `9a1cf17`. Source matches reviewed
`500adb3`; 51 product tests, original checkpoints and 182,520 finite matcher comparisons
passed independently. Joined checkpoint ownership/roundtrip, URL-policy and executable-mode
checks passed. Catalog regenerated from actual frontmatter and its drift check passed.
Unsafe restore resume, detached HEAD, case aliases, prefix globs and exponential matching
are closed. Live transport/client/installer and remaining P08/P09 consumers are separate.

Coordinator A08.1 routing slice: `b72ab47` plus `1d40193` (caller IFS isolation), 33 new
assertions and all old routing scenarios passed; independent P08 acceptance remains open.
Provenance slice `9f49e26` awaits P13 independent/selection acceptance.

P04: independent final `279dfc9` accepts product `aa73651`; merged as `490a0f4`,
then report-only builder history merged as `8964267`. The sole conflict was the already
included `8ea` standalone skill accessor; resolution equals the accepted skill bytes,
with that intent now in the shared helper. All changed product blobs match the reviewed
source. Actual Git swarm/fan-in/recovery, Forge/evaluator/schema and work-map joined checks
passed. No hook/automatic dispatch was activated. A22.7 remains explicit unfinished work.

P07: all ten owned commits after the already-integrated P04 dependency were cherry-picked,
preserving the original source branch. Final owned acceptance `3d8e715` is on master as
`62ca389`; all owned product blobs match `a8de574`. Joined Forge and enterprise-pack
consumers pass. P01's copied test fixture initially omitted the new real profile module/
schemas, causing 11 failures; `d7eb92f` fixes only that fixture resource list, with no
weakened assertion or fake dependency. Six real source/home-fallback/hook/vault tests
then passed. Final P05-v2, P06/P08/P14 and live-platform gates remain open.

P06: product `7425960` and independent report `1067da29` are integrated as `36593cd`.
Complete owned spec then first whole bounded quality passed, closing C01-C07 with
99 repository methods, 12 independent fact probes and actual installed/clone refusal
and preservation cases. Key provider/generator/library blobs match the reviewed product.
P05 consumer acceptance and final joined preflight/profile/workflow gates remain separate.

Coordinator regeneration exposed a real joined schema-consumer mismatch: the envelope
contract is JSON-compatible YAML, but the wiki grepped YAML-only version headers and
hardcoded the now-optional requires_lintel pack field. A23.4.g1/g2 repair the renderer
using the accepted stdlib parser, test dynamic metadata and fail malformed/missing
schemas before output. Unit/schema-shape RED was reproduced; repaired unit, schema/wiki
shapes, instruction/catalog/wiki checks and repository adapter init/check all pass.
Source repair and generated outputs are committed in `80f36fb`. They are refreshed
from source, not hand-edited. This is a bounded
coordinator-reviewed repair, not final independent integrated acceptance.

Shared preflight rejects five previously omitted P04/P07 dependencies; actual
installed checks no longer create Python bytecode before refusal. Initially seven of
eight focused joined methods passed. The remaining installed-profile test reproduced
a real native Windows default-home failure: history publication from a 220-character temp
path to a 274-character destination fails in os.replace. Shortening the fixture name
did not fix it; direct installed Python invocation also reproduces it. P07's appended
long-path card preserved containment/identity and reopened the actual consumer gate,
now closed by the independent repair and joined results below.
Exact frozen preflight/regression checkpoint: `98ad7edfaed7566848ecf26f2bbe563c0486e91d`.

P03 compatibility correction `ca280747b9fe8c16ea54598c4192f40567b8430e` postpones
annotation evaluation in context_safety.py and li-snapshot.py; no function behavior or
snapshot format changed. The new annotation regression was RED before repair; all
23 context and 24 snapshot methods pass afterward on Python 3.11.9. Python 3.9 grammar
and postponed annotations are checked, but `py -3.9 --version` exits 103: actual 3.9
execution remains unavailable. P10 may import this exact dependency; bare installation
remains native and does not acquire a Python prerequisite.

Cleanup-only dependency `0eab731c381985e21ef5b5520d7f93f49d3a8216` adapts the
coordinator Copilot sandbox teardown to the same owned Windows long-path spelling.
Actual long/readonly cleanup and unrelated sentinel preservation pass. P07's WIP had
reached method-body OK but overall ERROR at ordinary cleanup; that is not acceptance.
The method, default home and durable filenames remain unchanged. P07 and P10 were
explicitly authorized to import this separate test dependency and rerun the whole case.

P07's final frozen handoff is product `4d0014639204e5b5ad84838272a840c5283e28d0`
and report-only child `da614cad615a06c52d2aefd32818c082f9557c0e`. The coordinator
verified the four owned product paths and report-only parent, read the final evidence,
and dispatched the same reviewer `a7d78944` for repair spec then quality. Builder-only
final evidence: 45 lifecycle methods, 19 path methods, nine preservation scripts and
the unchanged installed method including teardown pass, zero skips.
Independent report `a745059786933c049a9fa52b74c0d2f5a9d19da1` now accepts scoped
spec then whole-repair quality, zero findings. Its own runs were 19 path methods,
19 focused lifecycle methods, nine preservation scripts and the actual installed
RED/GREEN pair, not the builder's 45-method run.

Only owned product/report/review were cherry-picked as `c344133` / `991b99b` /
`56de830`; all four product blobs equal the reviewed source. Cleanup `28b49add`
equals the already integrated `0eab731` and was not replayed. All eight joined adapter
methods now pass (253.575s); all 19 path methods pass (7.755s) via the canonical
runner, and the local adapter check passes. A direct Python invocation between
those runs omitted --root and executed no path tests; it was corrected, not hidden
as a passing aggregate. P05/P08/P10, other runtimes/platforms and final A22.7/A24/P14
remain separate; no release or live-host acceptance follows.

## Current repair gates

- P01's former staging/metadata/record defects are all closed in P01-final.md. The old
  overrestrictive decimal oracle remains historical, not authoritative. Do not re-open
  accepted behavior merely because its earlier rejected reports are still present.
- P04's five owned findings are closed in P04-final.md. Data-only symlink and type/mode
  identity, original-member prerequisite readiness and all historical preservation are
  accepted; unsupported submodules and final independently corroborated shared binding
  remain explicit limits. Do not redo the accepted component.
- P05's S01-S04/R01/R02/Q01 findings now close in `P05-excerpt-context-final.md`.
  Bound review/context/QA remain v2 with immutable qa_requirements; profile/work-map/
  corroboration domains are unchanged. The single provider and domain-separated
  excerpt-permission preimage preserve literal identity, real progress, docs-only
  validation and ordered historical recovery. Do not rebuild its accepted parser
  consumer or silently upgrade older insufficient receipts.
- P06's C01-C07 now close in the independent `P06-provider-repair-final.md` at `7425960`.
  Older C04/C05 and `09148b7` C06/C07 reports remain rejected history. P06 retains sole
  ownership of the stateless provider; P05 owns only its one-character progress consumer.
  No external parser dependency, shared task schema, scheduler or silent eligibility
  was added. Do not re-open the accepted component or infer P05 acceptance from it.

P05's former 81-method candidate used exact 742 helper bytes but missed Q01.
Its current accepted candidate retains those methods and adds ten new cases. Do not
import the rejected 091 helper or conflate dependency commits with P05 authorship.
See interfaces.md for the exact Git blob, checksum and accepted excerpt identity.
- P07's four owned findings close in P07-windows-final.md. Preserve its native versus
  injected/UNC/other-OS evidence boundary and original approved policy target; no automatic
  cross-target transfer or enterprise enforcement claim follows.

Historical P05 rejection: report `0cdbf596` / integrated `29ae5d9` closes earlier individual
cases but finds Q01. Wrapping a selected excerpt in an outer fence/raw PRE can retain
its normalized bytes and old clearance because interpretation facts are not part of
identity. The provider is correct and stays frozen. The P05 owner subsequently bound relevant selection-relative context, preserving
genuine progress and unrelated outside edits. The rejection's SPEC FAIL and started/
stopped quality remain historical, not retroactively approved.

New Q01 candidate: product `b023e8c25a922ffc536ffde6dd911865bf2eea21`, report-only
child `ec90b609423418ee4136f9fe425dfada11a08fae`. The coordinator checked its parents,
three owned product paths and unchanged provider blob, read the repair evidence, and
dispatched the same reviewer `6ed9c7df`. Builder-only final evidence is one combined
91-method run (81 retained plus 10 new), 12 controls, source-target/hook and focused
shape checks, zero skips. The mapped-excerpt hash now binds relative normalization
permission plus text, with explicit old-receipt invalidation.

Independent `33eac071a26f5eb931c8ca7ed220fee91ea4469b` now passes complete owned
spec and the first whole bounded quality review across 28 surfaces. It independently
ran 91 evidence methods, 12 controls, two hooks and additional real-gate/oracle cases.
Its separate source-target/shapes wrapper cleanup ERROR is retained, not claimed as a
green aggregate. The coordinator later inspected and removed only the exact two empty
ordinary fixture directories, nonrecursively; the immutable report was not amended.

Accepted P05 history/report are merged in `c5c8f8638f4ae7a93331c4b615f3b9f275ab18ca`.
All 29 product/provider paths equal reviewed `b023e8c`. Joined checks: ten Q01 methods
149.835s, four actual current-P07 bridge methods 32.592s, 12 controls 35.430s, two hook
methods 14.002s and source-target's three assertions pass. Four shapes and regenerated
catalog/wiki/local-adapter checks also pass with no generated drift. A source diff
command inherited fixture-only Git isolation and returned CRLF diagnostics; normal
checkout checks and read-only ignore-CR comparison are clean, without source edits.
The failed aggregate is not relabeled. Final ordinary workflow, mandatory installed
resource closure and P04/P08/P10/P14/CI acceptance remain separate.

P05's unchanged real four-case producer/reader/SHIP bridge passed with P07 `d02bb24`
and again with `56981ed` (P05 `54147fd`),
including saved-reference shell paths, but did not exercise the defective ordinary
bootstrap path. Keep those scopes distinct and re-run the appropriate chain on the final
P07 candidate. The four-case bridge has now passed on the actual joined current P05/P07
source as recorded above. Its saved-reference path and the separately verified ordinary
installed bootstrap remain distinct evidence, not a full live-client workflow claim.

## Continuation gate

P10 is active in its isolated child from `0df1042`. The operator explicitly rejected
Python as an installation prerequisite; ADR-0030 and the P10 card govern native bare
installation versus already Python-based runtime operations. The preflight
batch is frozen in `98ad7ed`, and P10 has received only the narrow adapter transaction
seam and related interruption tests. P07 long-path
repair and P05 Q01 repair use the original owners and reviewers. On a package
review rejection, return exact findings to its original builder, keep the package open,
and request re-review of the repaired immutable commit. On PASS, integrate only the
reviewed candidate and report, rerun the smallest joined checks and update its leaf
acceptance. Do not launch P08's dependent lifecycle implementation until its actual
predecessor contracts and P03 ownership are available. Use the approved successor cards
to continue P08-P14 and final P04 binding; do not stop the initiative at the first wave.

## Blockers and boundaries

Only `jokerman89` may be used for authenticated GitHub operations. Local GitHub CLI and
Git Credential Manager lookup found no stored credentials for that account. A separate
anonymous public API read (curl defaults disabled, no credentials supplied) verified
current main is still `28061e434be455ca02f135b73244eaf4f73f3a69` on 2026-09-20.
Push, PR and authenticated CI operations still require the authorized identity. Do not reuse the rejected injected
credentials or revive the abandoned lintel-harness repository operation.
An additional anonymous lookup did not establish the old local `azureflipper` label as
the authorized account (404); no credential was retrieved or used on that basis.

No new authorization for main merge, releases, production, hook activation or private sync.

## Next action

P05/P06/P07 are accepted and integrated. P08 is dispatched in session `f2c305ac`
from exact `5c3e7533335eeae15556aeabba422bfdbbe07f46` and has acknowledged its scope.
Its work-map reader ownership is released by P04; preserve the existing task/package
APIs. A08/A10 lifecycle work is ready. A13 installer observations await P10's actual
producer/receipt seam and fixtures, not an invented event or an imported WIP dependency.
P10 continues native/runtime installer work and may consume accepted P05/P07.
Await its immutable candidate rather than polling or duplicating investigation;
assign a separate independent P10 reviewer then integrate exact accepted deltas. The
coordinator retains generated outputs and final fan-in. No navigation/provider or P05
policy/schema workaround is authorized; all final joined/delivery gates remain open.
Use host-native delegation while Swarming component/final gates remain open.

P08 cross-owner seam `c805849` changes only SHIP's advisory ANALYZE-report guidance:
read the explicitly linked selected-work/cycle report and verify its identity; an
unlinked global report is history. ADR-0004's advisory default and P05 mandatory
controls are unchanged. The existing shape check passes; actual cross-initiative
selector evidence remains P08 work. P10 owns CP-16 migration inventory and reports
overdue/unknown/missing-catalog preservation cases; its final independent gate remains open.

P08 boundary incident (2026-09-21): cycle-continuity ran without a synthetic outer
home; session-digest may have read or initialized user-global state. Effects remain
unverified, no real-home inspection/rollback occurred, and the run is invalid evidence.
The operator explicitly approved resuming only with verified per-process synthetic
home/derived-path isolation. P08 acknowledged and continues ready work under that
boundary; A13.1/.2/.4 remains separately gated. See L-037.

P10's first frozen handoff is product `a73cf9ee38977501c201225d8269dac3668c1080`,
report `1117b9b54a55105d7202f92141a670f7b0cff578`, owned base `fb96f713`.
Its 48-path scope and seven contract hashes were verified from Git, not accepted
as product correctness. The strict run is 120/128, with zero skips/partial; later
owned 46-case and seven-runtime-case passes are separate. A narrow P07 copied-fixture/
single-method follow-up is authorized by the P10 card; a new frozen checkpoint is
required before independent review. Do not import the product or release A13 yet.

That follow-up is now frozen in `acf97f1`, only the copied-source list and the
authorized validation method. Snapshot `a400c03d384be29879644ec11214f0eeadafe7df`
also carries separately attributed coordinator dependencies; report-only tip
`62ffb9a072c3314b97e015e0f8f98b7f64459fc8` records targeted 8/8 and committed 1/1
fixture evidence without relabeling the failed aggregate. All seven producer hashes
and shared P07/provider bytes remain unchanged. The coordinator verified identity and
launched distinct reviewer `1578dfd8-f239-4eba-989b-3c4bde3e5792` on exact `62ffb9a`.
Review covers original 48 owned paths plus the authorized fixture and the canonical
installed caller/child bridge. P10 source is frozen; no master import, A13 release or
completion credit is given before the independent verdict.

Independent P10 report `1d871338dcdd1b6a535e4b546c2b2d0a7aea031b` is now
preserved report-only as `46e8b0f`. SPEC FAIL: one P2 F01, a truncated active
migration row is silently discarded into successful empty output. The P10 card
authorizes only its parser/focused-test/report repair. Quality is NOT STARTED.
Default setup D01 failed before target publication at an actual 260-character
snapshot blob destination; the separately successful explicit-store neutral bridge
does not replace that default case. D03's one-test cleanup ERROR is also not green.
Neither observation is assigned to F01 or authorized as a P03/P07/global-setting
repair. A13 and product integration remain closed.

Coordinator repairs for P10's reported shared-suite failures are committed separately:
`d53dc38` changes only the reviewed evidence CLI's Git mode to 100755, preserving its
content blob; `aa56a67` preserves literal runner failure text instead of interpreting
backslash escapes; `935b640` restores the actual trusted welcome footer invocation
and updates the obsolete six-file parity oracle to accepted ADR-0025. All original
failures were reproduced; focused runner/cohort/footer/protocol/executable checks pass.
The exact welcome snippet also passed synthetic no-state/no-write and missing-helper
checks. Neither P10's 120/128 aggregate nor P08's invalid isolation run is relabeled.
These dependency commits may be imported separately; generated drift and the narrow
P07 validation fixture still require their recorded follow-up/fan-in.

Prepared successors: P05-P07 contracts and official host-source report committed in
`3f584c8`; all P08-P14 dispatch cards already committed in `76e9e80`. P08 requires the
accepted shared P05/P06/P07 contracts; its context-file ownership is now released by P03.
Continue P08-P14 and final P04 A22.7 binding in dependency order, then final independent
integrated review, strict suite, authorized-account PR/CI and durable capture.

P10's native Bash fixture exposed a raw-drive ancestor termination bug and then exceeded
600 seconds from per-file Git Bash overhead; no passing aggregate was claimed. The
approved Windows entry may now use the already-present PowerShell performer, with no
Python or permission bypass. Both native entry points need real verification; the
POSIX/Bash 3.2 path remains separately required and cannot be inferred from Windows runs.
Windows PowerShell 5.1 then refused script loading under Restricted. The operator
explicitly approved using existing PowerShell 7.6.6 for local disposable verification;
its already configured policy is RemoteSigned. Neither policy changed. The native
selector is explicit, never an automatic fallback after denial, and 5.1 stays
denied/unverified. No Python or other installation dependency was added.

P04's historical merge checkpoint is `e74849db6b33c7b93baadb86206009cb9f9eb6d5`
(parents `21261f1` and original Swarming `275a354`). Independent merge-only reviewer
session: `ed672f58-2e85-42e2-b1b2-0635ba5b2325`, PASS spec then quality with zero new
findings. Its report-only commit `4bf5315` and ancestry were merged as `40c2795`.
P05-P07 started from that combined baseline. Do not confuse this checkpoint with
post-merge SW/A21 fixes still being built in P04's session.

Narrow mechanical P04/P07 bridge: P04 commit `8ea0fc4` replaces the skill's raw YAML cache
parser with the public nested profile accessor. MasterSession inspected it and integrated
it as `116d74b`; actual brief-forge evaluator/policy tests passed. P07 carries an explicit
cherry-pick dependency `b4e9316` for its real JSON-profile integration tests. This is not
acceptance of the broader Swarming/envelope WIP.

Required jq was absent (exit 127). A checksum-verified official jq 1.8.2 executable was
restored only under master `.claude/runtime/tools/jq-1.8.2/`; see reports/toolchain.md.
Use a per-process PATH prefix for required tests; no global setting or account changed.

P05 restored the existing Python 3.9 floor. Real Python 3.9/other-platform execution is
not established by grammar checks. The one required_policy schema, host transport and
profile reference APIs are in interfaces.md; final implementations and integration tests
must consume them consistently. Do not import an unreviewed dependency into another
writer's authored batch just to make a test green.
