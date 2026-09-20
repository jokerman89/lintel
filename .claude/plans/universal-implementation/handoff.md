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

All are `lintel-builder` sessions with explicit ownership, acceptance, local commits,
report paths and no remote authorization. MasterSession must arrange separate spec and
quality review after results arrive. No package is complete yet.

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
session: `ed672f58-2e85-42e2-b1b2-0635ba5b2325`. Do not confuse that checkpoint with
post-merge SW/A21 fixes still being built in P04's session.
