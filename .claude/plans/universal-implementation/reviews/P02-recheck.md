# P02 independent repair re-review

**Date:** 2026-09-20. **Reviewer:** Universal private sync review, independent of
the implementer. No product changes were made by this reviewer.

| Review identity | Exact revision |
|---|---|
| Frozen candidate | `82d0f3980989bfc8cd6a2722982898d68fc92623` |
| Product/test revision | `17a9f69eb8ee48a4fd92762958d0adafad598b64` |
| Full package base | `21261f1ff76be994246060a7817924f2893f2454` |
| Previous rejected candidate | `a8b36a983499d5e2bcdd7968fd452156eac8442f` |
| Preserved first review | `2d6030d3d392e2a70cc3eae8e12e5f6c231df893`, `reviews\P02.md` |

**Stage 1, spec re-review: PASS at `17a9f69`.** F1-F3 close on the exact original
replay, inspected repair branches and package acceptance/preservation scenarios.
**Stage 2, previously unrun whole-package quality review: FAIL, 1 new P2.**
Staging a role deletion prevents its synchronization. The ordinary unstaged deletion
works, and the original base CLI handles the staged deletion correctly.

**Current counts:** 0 open P1, 1 open P2, 0 P3. The previous 3 P1 findings are closed
for this revision, not erased from the first report. **Package acceptance remains
blocked** by the new preservation regression. MasterSession returned it to the
original builder. No verdict applies to that builder's subsequent changes.

## Snapshot, scope and review order

Verified the reviewer workspace was clean at the first report commit. Created the
named reviewer branch `jokerman-microsoft-universal-private-sync-recheck` directly
at `82d0f39`; the original `jokerman-microsoft-universal-private-sync-review` branch
remains at `2d6030d`. No reset, source-branch edit or other-worktree operation occurred.

The repair changes only `lib\private_sync.py`, the Python integration support and
`reports\P02.md`. The last commit is report-only. The product/test files match
`17a9f69` exactly. Authority remains the validated `work.json`, spec R10/R11,
plan A26.1-A26.4, `packages\P02.md`, action A26 and audit RU-03.

First inspected the repair and ran the unchanged first-review replay. Then completed
the focused package tests and additional spec-preservation cases. Only after that
spec gate passed did the reviewer begin the separate quality stage.

Quality covered the entire six-file package since `21261f1`, not only the repair:
both public wrappers, all shared-helper paths, the integration runner and assertions,
and the builder's report. Related path resolution, public sync descriptions and
installer inclusion were considered as context, without expanding into their audits.
The only authored path is this report; existing reports, plan/state/memory, product
and other worktrees remain unchanged. No nested agent was used.

## Stage 1: old findings and per-leaf results

| Original finding | Disposition and actual evidence |
|---|---|
| F1, endpoint conflation | **CLOSED.** `lib\private_sync.py:40-54,118-128,140-149` retains URL spelling and compares the single Git-expanded fetch/push URL exactly. The original two CLI cases now select the literal suffixed repository correctly, then reject both status and push after drift: exit 1, no commit at the unapproved destination, approved HEAD unchanged. Added package cases exercise literal and percent-encoded suffix round trips and fetch-only/push-only drift. |
| F2, destructive pull refmap | **CLOSED.** `lib\private_sync.py:280-302` uses a source-only fetch with empty `--refmap=`, disables tag/prune/submodule effects, checks ancestry and then separately fast-forwards. The original two divergent cases exit 1 with the same pending HEAD, index tree and bytes; the pending commit stays on a local branch. New assertions protect all branch/tag/tracking refs and exercise legitimate fast-forwards, unborn first pulls, conflicts and local-ahead no-ops. |
| F3, source alias collision | **CLOSED.** `lib\private_sync.py:206-241` derives identity from the effective origin and only merges canonical file URI/local-path spellings when lossless. The unchanged replay leaves two distinct record names and retains project A after project B pushes. Added cases retain historical raw-alias records and preserve identity when another alias resolves to the same endpoint. |

The exact first-review five-case replay exited **0**, with
`ACCEPTANCE VIOLATIONS: 0`. No assertions or reviewed product files were changed to
obtain that result.

| Leaf | Spec re-review | Preservation evidence and quality caveat |
|---|---|---|
| A26.1 | **PASS** | Explicit enabled binding agrees with actual origin; A-to-B rebind, repeated setup and clone-conflict refusal retain content/index/history. Literal and encoded file URL selections target the actual selected repository. Additional dirty/staged rebind checks pass for both tools. |
| A26.2 | **PASS** | Missing, disabled, malformed, legacy, wrong-cache and mismatched bindings refuse. Rewrites, multiple URLs and suffix drift refuse before transfer/staging. Forget retains bytes, index, HEAD and origin and blocks subsequent sync. |
| A26.3 | **PASS** | Equal basenames remain distinct; effective source rewrites distinguish projects; same-endpoint aliases and linked worktrees remain stable. Basename-only and previous raw-alias records survive migration and round trips. |
| A26.4 | **PASS at the spec-stage gate; quality preservation hold** | Both tools pass positive push/pull, retry, ignored/dirty conflict, unborn and divergent-history cases. Quality then identified Q1: role deletion works unstaged but fails after ordinary `git rm`. Do not mark the leaf/package accepted until that regression is repaired. |

The specification is not relaxed: the spec-pass-at-`17a9f69` milestone does not
override the subsequently demonstrated preservation failure.

## Stage 2: quality decision and new finding

**FAIL: 1 P2, 0 P1, 0 P3.** The review completed the bounded quality stage; it is
not the earlier "quality not reached" result.

### Q1 - P2: staged Markdown role deletions are rejected as unrelated data

**Source:** `lib\private_sync.py:258-264`.
**Affected entrypoint:** `bin\li-roles-sync`.
**Confidence:** reproduced against the candidate and original base.

For roles, the selected set comes from `git ls-files --cached --others ... "*.md"`.
After `git rm retired.md`, that path is no longer in the index, so it is absent
from `selected`. It is still present in the staged diff. Consequently
`staged.difference(selected)` rejects a legitimate role deletion as unrelated,
before the helper can commit or push it.

| Local fixture | Candidate result | Remote result |
|---|---|---|
| Publish `architect.md` and `retired.md`; remove `retired.md` from the worktree without staging | Exit **0** | `retired.md` deleted, `architect.md` retained |
| Same initial files; `git rm -- retired.md`; run public roles `push` | Exit **1** | `retired.md` remains at the remote; HEAD/index/local deletion remain unchanged |
| Run original `21261f1` roles CLI from Git objects against that same staged fixture | Exit **0** | `retired.md` deleted, `architect.md` retained |

The exact candidate error is:

```text
ERROR: li-roles-sync: Unrelated staged files in the cache; commit or unstage them before private sync.
```

This is a supported-sync regression, not a data-loss or unapproved-destination claim.
The operator can work around it by manually committing or unstaging first, but an
ordinary staging action should not make an otherwise supported role deletion fail.
The existing unrelated-staging safeguard remains valuable and must not be removed.

**Required repair:** include staged deletions of owned Markdown role paths in the
authorized role-change set, using the old/index/HEAD path information as appropriate.
Continue rejecting unrelated staged non-role paths. Add discriminating staged versus
unstaged deletion tests, including deletion of the last role and nested role paths,
while retaining the existing unrelated-staging and destination checks.

### Other bounded quality results

| Area | Assessment |
|---|---|
| Command binding and configuration | Explicit origin/current-branch pushes, no-follow-tags, no submodule push and mirror override withstand the tested config changes. Both tools ignore a decoy push default/branch push remote; configured mirror/refspec/follow-tags cannot broaden published refs. Fetch refmap isolation is materially tested, not inferred from `--ff-only`. |
| Preservation and failure handling | Setup stages clones before conflict checks; forget changes only authorization. Git failures remain visible/nonzero, failed pushes keep commits for retry, and dirty/staged setup retains local state. The remaining concrete defect is Q1. |
| Paths and interface | Wrappers fix internal arguments behind `--` and retain public commands/aliases. Lessons still resolve through `lib\paths.sh`. Leading-dash, spaced and bracketed role filenames sync literally; wrapper executable modes remain `100755`. |
| Maintainability and dependencies | One typed binding schema and shared standard-library helper serve both CLIs. No new third-party dependency or duplicate transport implementation. Syntax checks pass; no substantial performance or maintainability finding identified in this bounded helper. |
| Test quality | The 52 scenario/789 assertion claim is independently confirmed. Assertions check actual refs, index entries, bytes and Git transport traces. Counts include setup/subcase assertions, not 789 distinct requirements. Staged role deletion was absent and is now documented by a failing independent fixture. |
| Installation/docs context | Existing installers copy `lib` and `bin`; the Copilot bundle includes both. Existing opt-in sync descriptions remain applicable. This is static inclusion evidence, not a fresh install or generated-output validation. |

## Commands and measured results

| Executed command or probe | Result |
|---|---|
| `git switch -c jokerman-microsoft-universal-private-sync-recheck 82d0f3980989bfc8cd6a2722982898d68fc92623` after clean-state/preserved-ref checks | Exact isolated reviewer snapshot; first review branch retained |
| Repair diff `a8b36a9..17a9f69`, full package `21261f1..82d0f39`, and report-only identity check | Expected three-file repair; six-file full package; no product difference between `17a9f69` and `82d0f39` |
| `python bin\li-work-artifacts.py --repo . --map .claude\plans\universal-implementation\work.json` | Exit 0; original authority map validated |
| Unchanged five-case replay extracted with `git show` from `2d6030d:...reviews/P02.md`, executed via `bash -c 'export LINTEL_TEST_BASH="$BASH"; python3 -B -'` | **Exit 0, zero violations** |
| `bash tests\integration\private-sync-binding.sh` on the frozen candidate | **Exit 0: 52 scenarios, 789 assertions, 0 skipped**, 440.146 seconds |
| Four extra spec-preservation fixtures through the real wrappers | **4 pass**: push config/ref isolation and ignored-file conflict preservation, both tools |
| Staged-role deletion probe and original-base control | **Exit 1 intentionally** for the candidate regression; original-base remote deletion succeeds |
| Five quality characterization/control cases | Expected staged failure confirmed; unstaged deletion, literal role filenames and both dirty/staged rebind controls pass |
| Report-contained Q1 replay below | **Exit 1: `CONFIRMED QUALITY REGRESSIONS: 1`**; unstaged candidate and staged original-base controls both synchronize the deletion |
| Three `bash -n` checks: both wrappers and the focused shell runner | Exit 0 |
| `ast.parse(..., feature_version=(3, 9))` for shared helper and Python integration support | Exit 0; grammar check only |
| `git diff --check 21261f1ff76be994246060a7817924f2893f2454 82d0f3980989bfc8cd6a2722982898d68fc92623` and clean-product status checks | Exit 0; no product modifications |

All behavioral probes used Git Bash 5.3.15, Git 2.55.0.windows.3 and Python 3.11.9
on Windows. No entire repository suite was run. The original red-run counts, other
shape tests, actual Python 3.9/Bash 3.2 execution and remote host acceptance were
not independently established by this recheck.

## Executable Q1 regression fixture

This replay uses the committed test fixture and both candidate/base CLI implementations.
It creates and cleans up only its exact temporary synthetic fixture directories.
Run from the reviewer repository root in PowerShell; no script file is created:

```powershell
@'
from pathlib import Path
text = Path(r".claude\plans\universal-implementation\reviews\P02-recheck.md").read_text(encoding="utf-8")
code = text.split("```python\n# p02-q1-repro\n", 1)[1].split("\n```", 1)[0]
exec(compile(code, "<P02-Q1-review-repro>", "exec"))
'@ | bash -c 'export LINTEL_TEST_BASH="$BASH"; python3 -B -'
```

```python
# p02-q1-repro
import json
from pathlib import Path
import runpy
import subprocess

tests = runpy.run_path(str(Path("tests") / "integration" / "private-sync-binding.py"))
base_cli = subprocess.run(
    ["git", "show", "21261f1ff76be994246060a7817924f2893f2454:bin/li-roles-sync"],
    check=True, capture_output=True, text=True, encoding="utf-8",
).stdout
regressions = 0
for staged in (False, True):
    case = tests["RolesSyncTests"]()
    case.setUp()
    try:
        f = case.fixture
        remote = f.remote("role-deletion")
        f.setup(remote)
        f.content(b"# Keep this role.\n")
        retired = f.cache / "retired.md"
        retired.write_bytes(b"# Retire this role.\n")
        f.cli("push")
        if staged:
            f.git(f.cache, "rm", "--", retired.name)
        else:
            retired.unlink()
        before = f.state()
        result = f.cli("push", ok=None)
        still_remote = bool(f.git(remote, "ls-tree", "HEAD", "--", retired.name))
        evidence = dict(
            staged=staged, candidate_exit=result.returncode,
            deletion_synced=not still_remote, state_preserved=f.state() == before,
            stderr=result.stderr.strip(),
        )
        if staged:
            old = subprocess.run(
                [tests["BASH"], "-s", "--", "push"], input=base_cli,
                cwd=f.project, env=f.env, capture_output=True, text=True, encoding="utf-8",
            )
            base_deleted = not f.git(remote, "ls-tree", "HEAD", "--", retired.name)
            evidence.update(
                base_exit=old.returncode, base_deletion_synced=base_deleted,
                other_role_retained=bool(f.git(remote, "ls-tree", "HEAD", "--", "architect.md")),
            )
            if result.returncode != 0 and still_remote and old.returncode == 0 and base_deleted:
                regressions += 1
        print(json.dumps(evidence), flush=True)
    finally:
        case.doCleanups()
print(f"CONFIRMED QUALITY REGRESSIONS: {regressions}", flush=True)
raise SystemExit(1 if regressions else 0)
```

## Limits and handoff

All transfer targets were temporary local bare repositories. The fixture isolates HOME,
USERPROFILE, XDG and Lintel paths, disables global/system Git configuration, configures
only synthetic local identities and permits only the file protocol. No real private
destination/content, credentials, network, GitHub, publication or source-branch mutation
was used. Nothing was installed or activated.

The lack of an atomic external-writer lock remains a disclosed boundary, not a finding.
Tests use fixed configuration before the command. Q1 needs no concurrency, malicious
hook or arbitrary executable helper. This review does not establish all concurrent
Git/editor behavior, foreign transport helpers, live credentials/privacy, Linux/macOS,
consumer installation, CI or final integrated initiative acceptance.

MasterSession owns the acceptance ledger. The implementer must repair Q1 without
weakening unrelated-staging protection or reopening F1-F3, supply the next immutable
candidate, and return it for independent recheck. This report is evidence for the
rejected `82d0f39` snapshot only; no future repair is pre-approved.

**Cycle position:** REVIEW quality blocked -> BUILD (Q1) -> independent REVIEW.
