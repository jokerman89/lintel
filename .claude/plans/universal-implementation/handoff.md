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
| P05 review evidence | `2329e71f-cd9e-473b-94cf-41c579c29a88` | Paused at `5a4933e` / product `3adae4b`; v2 QA closes, literal-boundary repair waits for coordinated shared facts |
| P06 host adapters | `324863ff-e7cf-4abf-b449-04dd0f096170` | Frozen narrow nav checkpoint `9f6b69d`; shared boundary extraction API/card being coordinated before any new edits |
| P07 profile context | `b9352dfe-1c1e-4ea3-b7d9-0fd008d39b3d` | Component ACCEPTED: own commits integrated through `62ca389`; idle, final consumers remain open |

All are `lintel-builder` sessions with explicit ownership, local commits, report paths
and no remote authorization. P01/P02/P03 plus the owned P04/P07 components are accepted.
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
| P05 | Third rejection `85e8d90` at `5a4933e` / `3adae4b`; literal repair re-planned | `6ed9c7df-4845-4d70-88c7-f0746ab28059` |
| P06 | Third rejection `6b874c7`; new `9f6b69d` m1-m6 checkpoint not independently accepted | `d2a89ac3-151a-4dc0-ab09-1f3a62465cab` |
| P07 | Final `3d8e715`; owned SPEC/QUALITY PASS at `a8de574`; final joins open | `a7d78944-c02c-4909-a060-2c4f2a754b00` |

## Accepted local integrations

P01: complete worker/final-review history merged as `a2ef318`. Source matches independently
reviewed `041417a`; all eight leaves passed spec and full bounded quality. The reviewer
ran 51 tests plus corrected numeric/record probes and new failure/ownership probes.
Eight selected joined-tree tests passed with jq: hostile resolvers, retained policy,
numeric/path metadata, vault, ADR index ownership and updater failure/fallback.
Registration is unchanged and dormant hooks remain dormant. P07's changed resolver is
not yet on the integration branch, so that combined gate remains open.

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

## Current repair gates

- P01's former staging/metadata/record defects are all closed in P01-final.md. The old
  overrestrictive decimal oracle remains historical, not authoritative. Do not re-open
  accepted behavior merely because its earlier rejected reports are still present.
- P04's five owned findings are closed in P04-final.md. Data-only symlink and type/mode
  identity, original-member prerequisite readiness and all historical preservation are
  accepted; unsupported submodules and final independently corroborated shared binding
  remain explicit limits. Do not redo the accepted component.
- P05's first four findings led to `54147fd` / `e5b92a4`, but re-review reproduced new
  false clearance: submitted QA can omit/relabel/change the kind of bound test obligations,
  and indented literal Markdown checkbox examples are treated as progress. Fix the shared
  expectation/identity invariants, preserving true docs-only acceptance and task progress.
  Approved decision `c6736e5`: affected bound review/context/QA format is v2 with required
  immutable qa_requirements. Profile refs/corroboration remain v1, CLI flags stay stable.
  Preserve ordered non-clearing history, not silent v1 reinterpretation or permanent
  log poisoning. The actual v2 source is now `3adae4b`, canonical example in
  skills/review/references/evidence.md. Its QA/migration invariants close individually,
  but compound-list fences/raw PRE literals still permit acceptance normalization.
  P05 is paused for a shared stateless Markdown-boundary checkpoint, not more local regexes.
- P06's C01-C03 close individually. Its C04 EOF-title and C05 quoted-indented-code
  boundaries are addressed under approved `e76ed6c` in immutable `9f6b69d`, with local
  27 nav/16 registry/14 Universal/22 Copilot methods passing; not independent acceptance.
  Its current internal MarkdownSource lacks explicit raw/quote/task-marker facts P05 needs.
  MasterSession chose a shared trusted `lib/markdown_source.py` direction, with P06 as sole
  classifier owner and P05 as the later one-character progress consumer. Exact API, supported/
  opaque spans and ownership card must be approved BEFORE extraction/import. No external
  parser dependency, shared task schema, scheduler or silent eligibility assumptions.
- P07's four owned findings close in P07-windows-final.md. Preserve its native versus
  injected/UNC/other-OS evidence boundary and original approved policy target; no automatic
  cross-target transfer or enterprise enforcement claim follows.

P05's unchanged real four-case producer/reader/SHIP bridge passed with P07 `d02bb24`
and again with `56981ed` (P05 `54147fd`),
including saved-reference shell paths, but did not exercise the defective ordinary
bootstrap path. Keep those scopes distinct and re-run the appropriate chain on the final
P07 candidate. Candidate archives/compositions are tests, not acceptance of their source.

## Continuation gate

All useful independent coordinator preparation is committed. Await worker/reviewer
notifications rather than polling or duplicating their code investigation. On a package
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

Coordinate and approve the P05/P06 common boundary facts/card, then sequence its one
writer and consumer. Obtain their same-reviewer spec/quality evidence before integration.
P01/P02/P03 and owned P04/P07 are not to be rebuilt.
Use host-native delegation while Swarming component/final gates remain open.

Prepared successors: P05-P07 contracts and official host-source report committed in
`3f584c8`; all P08-P14 dispatch cards already committed in `76e9e80`. P08 requires the
accepted shared P05/P06/P07 contracts; its context-file ownership is now released by P03.
Continue P08-P14 and final P04 A22.7 binding in dependency order, then final independent
integrated review, strict suite, authorized-account PR/CI and durable capture.

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
