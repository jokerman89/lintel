# Universal implementation handoff

Updated 2026-09-20 by MasterSession.

## Durable state

- User-selected initiative: all A01-A26, preservation-first, with active Swarming integration.
- Implementation authority: current 2026-09-20 request; review audit completion is not build completion.
- Audit preserved in commit `74290e0`; 25 exact source files verified before import.
- Local separate SHA-256 backup and verified full-history Swarming bundle exist in the
  MasterSession's private session artifacts; no personal paths or credentials are needed
  to use the committed evidence.
- Baseline `origin/main`: `28061e434be455ca02f135b73244eaf4f73f3a69` (local ref, not freshly fetched).
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

First wave is running in isolated app-native worktrees from `21261f1`:

| Package | Session ID | Current boundary |
|---|---|---|
| P01 trusted helpers | `b3853be7-dbbe-4161-9566-7e7d2c50e05e` | A04/A25 local implementation and tests; no shared generators |
| P02 sync binding | `2e21aa98-3b40-46e7-885d-2ec4161ec35d` | A26 synthetic local remotes only |
| P03 context safety | `9f06eebf-a3ee-4867-95ad-eb6e1d22a6d5` | A01/A11; existing context ownership retained |
| P04 Swarming | `a8960a09-fcd7-4652-a9b6-74ad6a94a029` | Early real merge and SW repairs; final A22.7 remains dependent |
| P05 review evidence | `2329e71f-cd9e-473b-94cf-41c579c29a88` | A02/A03; exact shared review/control API sent before consumer binding |
| P06 host adapters | `324863ff-e7cf-4abf-b449-04dd0f096170` | A05/A06; now owns Copilot generator adaptation and targeted tests |
| P07 profile context | `b9352dfe-1c1e-4ea3-b7d9-0fd008d39b3d` | A07/A20 compatibility; independent parser/pinning now, final contract integration later |

All are `lintel-builder` sessions with explicit ownership, acceptance, local commits,
report paths and no remote authorization. MasterSession must arrange separate spec and
quality review after results arrive. No package is complete yet.

Initial reviewed candidates (rejected versions remain preserved for audit):

| Package | Candidate | Independent reviewer session |
|---|---|---|
| P01 | `d6820a1b9fd8d92ed019e9eab25128b2c7699e0d` (product `c4542e4`) | `d699f463-ee4d-4950-9b9d-98f35e96f689` |
| P02 | `a8b36a983499d5e2bcdd7968fd452156eac8442f` (product/tests `53b9462`) | `da23fa6f-499b-4011-b39b-a632312a8800` |

P01's independent spec/preservation review failed with three P2 findings: ADR commit
sweeps unrelated staged work; malformed p95 values are accepted by prefix; literal
metacharacter filenames are interpreted as regex. Quality was not run. Report source
`4e848a9` is preserved on master as `8450263`. The original P01 worker is repairing,
not frozen. Request re-review from the same independent reviewer on the new exact SHA.

P02's independent spec review failed with three P1 findings: file-URL fragments are
normalized differently from Git and redirect a push to an unapproved local destination;
configured fetch refspec overwrites pending HEAD/index/worktree before a failed pull;
raw source aliases collapse distinct projects into one lesson record. Report source
`2d6030d` is preserved as `93c3dd4`. The worker reproduced all classes and is repairing.
Its earlier 539 green assertions did not cover these failures; no quality pass is claimed.

P03 repaired the fail-closed Windows publication error in `aa7fad4`, but independent
spec review of `5c52f2f` found four more concrete defects despite the green original
32-test matrix: interrupted restore overwrites a between-invocation edit (P1), detached
HEAD checkpoint regression, Windows case-alias exclusion bypass and file-prefix glob
overselection (three P2). Reviewer `efd3f877-550a-4ef0-9009-ed71b95b01ab` is finalizing
the report without quality review. Original builder is repairing only its owned paths.

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

No new authorization for main merge, releases, production, hook activation or private sync.

## Next action

While first-wave work runs, prepare shared P05-P08 contracts and executable cards, keeping
product edits off P04's historical merge paths until its checkpoint is ready. Integrate
the history-preserving merge first; review and integrate other package results in order.
Use host-native delegation until Swarming's authority/evidence defects are corrected.

Prepared successors: P05-P07 contracts and official host-source report committed in
`3f584c8`; A08.1 routing correction committed in `b72ab47` (30 new assertions plus all
prior routing cases pass; independent P08 acceptance pending). P08-P14 dispatch cards
are being supplied before their dependent writers start.

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

P07's own 21-case matrix and nine affected existing scripts passed, including the actual
P04 accessor dependency and jq-backed checks. Its direct producer-to-P05 policy bridge
still needs the frozen P05 source; no final integration or independent approval yet.
P05's unnecessary Python 3.10 requirement was rejected and is being restored to the
existing 3.9 floor. The one canonical required_policy schema and exact CLI are recorded
in interfaces.md; P06 must consume them rather than inventing another clearance reader.
