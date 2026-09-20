# P03 final independent package review

**Date:** 2026-09-20.
**Stage 1, affected specification and preservation:** PASS.
**Stage 2, Q1 closure and bounded remaining quality:** PASS.
**Open P03 product findings:** P1: 0; P2: 0; P3: 0.
**Disposition:** accept the bounded P03 package at the exact product result below.
This is not integrated initiative completion, host certification or SHIP clearance.

## Exact identity and scope

| Item | Exact reference |
|---|---|
| Original package base | `21261f1ff76be994246060a7817924f2893f2454` |
| First rejected product | `aa7fad47580510248956ffa242887d4457951348` |
| First independent report | `d0f4552347d7312073bbb42c84e18df9f66ef727`, `reviews\P03.md` |
| F1-F4 repaired product | `133eebe60a13d4fa8a67af4dace611a7a330a8e2` |
| Previous independent full quality report | `98515a1c4db4796d03005529d61f021bcc2d0df1`, `reviews\P03-recheck.md` |
| Focused Q1 repair base | `1523e5e7f55ffd753e4ef17b2bd1d6b6b546e60b` |
| Final reviewed product/test result | `500adb370c726b86047046998a6a5240ebd8ea8f` |
| Immutable supplied snapshot | `399a2e6b03a9ca3b3dfaddc4f38498f9f88115f4` |
| Snapshot difference from product | Only `.claude\plans\universal-implementation\reports\P03.md` |
| Same independent reviewer | Copilot lintel-reviewer session `d2f01e82-f00a-40fd-96e9-9294a8b01513` |
| Final review branch | `jokerman-microsoft-universal-context-safety-final` |
| Reviewer-authored file | Only `.claude\plans\universal-implementation\reviews\P03-final.md` |

Materialized a new clean branch directly at `399a2e6`; no reset or builder/master
checkout change. The earlier `jokerman-microsoft-universal-context-safety-review`
branch remains at `d0f4552` and `jokerman-microsoft-universal-context-safety-recheck`
remains at `98515a1`, including their reports and rejected-result evidence. This review
does not rewrite those historical verdicts. Product source remained pinned throughout.

The focused repair changes only `lib\context_safety.py` and its existing
`tests\unit\context-safety.py`. Full package range is `21261f1..500adb3`, the same
26 owned product/test paths already reviewed. Relative to the previous full quality
pass, all other product files are unchanged. Reused that bounded review rather than
opening an unrelated audit, and rechecked the changed matcher, its actual consumers,
the old finding replays and all package acceptance suites.

Authority remains the approved specification, mapped plan, P03 card, and exact
CP-01/02/05/13/16, AG-01/12 and RU-07 requirements read previously. The explicit work
map validates unchanged. No acceptance criterion, shared plan, memory, generator,
product file or existing report was edited by the reviewer. No nested agent was used.

## Stage 1: specification and preservation

The exact F1-F4 replay was extracted unchanged from `d0f4552` and executed against
the new result: **4/4 PASS, zero skips**. The exact Q1 CLI replay from `98515a1`
also passes unchanged. No input was rejected or test weakened to obtain those results.

| Finding | Final disposition | Evidence and current owner |
|---|---|---|
| F1, interrupted restore reacquires write authority | CLOSED, preserved | Unchanged v2 snapshot journal at `bin\li-snapshot.py:248-373`; original post-image re-edit replay and all 24 snapshot tests pass again. |
| F2, detached HEAD checkpoint failure | CLOSED, preserved | Exact safe `HEAD` handling at `bin\_context.sh:42-48`; baseline comparison, detached save/list/latest/read/warm and named-history checks pass again. |
| F3, Windows exclusion case aliases | CLOSED, preserved | Filesystem-aware segment comparison at `lib\context_safety.py:166-177` is unchanged by Q1; literal identity and glob consumers retain native alias exclusion and injected distinct-identity behavior. |
| F4, nonmatching file-prefix glob | CLOSED, preserved | Guard at `lib\context_safety.py:209-210` remains unchanged; actual CLI child-of-file patterns return empty/unmatched with exit 1, while exact-file/valid globs still work. |
| Q1, repeated globstar computation | Specification behavior preserved; quality closure below | Original valid selectors and saved patterns remain accepted. Matching and nonmatching cases return the correct manifest/exit status without recursive backtracking. |

### Per-leaf acceptance

| Leaf | Result | Preserved behavior and actual evidence |
|---|---|---|
| A01.1.a | PASS | Literal spaces/metacharacters are data; actual warm recipe and hostile-input fixtures cannot execute the input. Traversal/link refusal retained. |
| A01.1.b | PASS | Shared selector still drives warm/related/ADR entry points, source manifests, normal direct/recursive globs, ranking and missing/omitted sources. Whole-path and repeated-globstar match/no-match cases pass. |
| A01.2.a | PASS | Explicit owned root/path/digest/size/mode manifest; malformed, foreign, aliased, traversal and native junction cases rejected without source mutation. |
| A01.2.b | PASS | Exact copied bytes and source recheck retained; partial copies never become success; bounded reported Windows retry and persistent-error preservation pass. |
| A01.2.c | PASS | Owned rollback preserves unrelated, staged and unstaged content. Per-file intent/completion and consumed authority prevent later-edit overwrites; all snapshot cases pass. |
| A01.3 | PASS | Original F1-F4 replay, positive CLI roundtrip, interrupted resume, failed journal writes, malformed/stale/old journal refusal and old-backup preservation pass. |
| A01.4.a | PASS | Unchanged isolated bisect procedure executes success/error fixtures, clears bisect state and preserves caller HEAD/index/WIP/untracked content. Prior five-commit midpoint evidence remains applicable to identical role code. |
| A01.4.b | PASS | Refactor ownership/WIP and partial-migration predicate fixtures pass; baseline/refactor/migration methods remain intact and share repaired recovery. No live migration is asserted. |
| A01.5.a | PASS | Unchanged actual URL parser preserves exact/wildcard/sibling/apex distinctions and rejects malformed authorities, schemes, credentials, controls and invalid ports. |
| A01.5.b | PASS within declared adapter boundary | Actual injected single-hop loop validates before the next request, retains allowed redirects/provenance and rejects denial/loop/downgrade/error/size cases. No live adapter is invented. |
| A11.1 | PASS | Existing checkpoint owner, repository keys, exact legacy attribution, explicit history, branch scope, collisions, empty reservations and plain/unborn/detached behavior remain. |
| A11.2 | PASS | Actual helper keeps capacity/usage unknown without observations and labels estimates and provenance; no fictional universal limit. |
| A11.3 | PASS | Perf entry and flags remain advice, not a host mutation or fabricated billing/capacity claim. |
| A11.4 | PASS | Future exclusions are actually consumed, native aliases handled, repeated patterns bounded, policy/source bytes preserved, and zero already-sent tokens/disk bytes claimed reclaimed. |

## Stage 2: Q1 quality closure

The prior full bounded quality pass found only Q1. After the specification recheck above
passed, reviewed its algorithmic repair and affected failure paths. No new product
finding was established.

**Q1 is CLOSED at `lib\context_safety.py:159-196`.** Adjacent `**` segments normalize
internally; original input and persisted policy strings remain unchanged. Rolling
dynamic-programming rows replace recursive backtracking. Each path/rule cell is visited
at most once; separated globstars use the same algorithm, so closure does not depend
only on removing redundant adjacent segments. DP storage is two rows proportional to
normalized rule count. There is no new pattern rejection threshold or empty-result
fallback for errors.

The recurrence handles zero-component globstar transitions in the initial/current row
and consuming transitions from the previous row. Non-globstar comparisons run only from
a reachable prefix. An empty reachable set can return false because no later component
can restore a match. The original segment matcher and filesystem identity checks are
unchanged. This is a polynomial state bound, not constant time for arbitrary input,
constant-cost filesystem probes, or a wall-clock product guarantee.

### Discriminating evidence

| Independent observation | Actual result |
|---|---|
| Prior exact Q1 CLI replay: 20 directories, one one-byte file | `**/missing.txt`: unmatched, exit 1, **0.265 s**; twelve adjacent globstars plus `missing.txt`: unmatched, exit 1, **0.235 s**. Both finish before the existing five-second test backstop. |
| Actual DP cell tracing, 21-component path, twelve adjacent globstars, match and no-match | **42 distinct cells, 21 segment comparisons** in each case; normalized rules: 2; no repeated cell. |
| Same tracing with twelve separated `**/*/` segments, match and no-match | **525 distinct cells, 195 segment comparisons** in each case; normalized rules: 25; no repeated cell. |
| Exact prior cooling scenario through real `update_exclusions`/`select_files`, three repeated reads | Nonmatching saved pattern: **42 comparisons** per read and one selected file; matching saved pattern: **41 comparisons** per read and no selected file. Saved policy and source bytes remain unchanged. |
| Finite semantic comparison with the actual prior reviewed matcher | **182520 path/pattern pairs agree**: 39 paths over `a`, `b`, `A` at depths 1-3, crossed with 4680 patterns at depths 1-4 using literals, `*`, `?`, classes, negation, `**` and `***`. |
| Recursive filesystem-aware matching/exclusion | Native Windows case aliases behave as before; injected distinct-identity response preserves case-sensitive semantics. No OS setting was changed. |
| Permission failure in actual filesystem identity probe, both source glob and saved-exclusion consumers | Explicit CLI-main **exit 2**, error on stderr, no misleading empty-result JSON; source and policy preserved. |

The finite semantic oracle is the old matcher on small nonpathological inputs, not an
assertion that the old algorithm was performant. The new 1500-component string tests
also pass without recursion; these are matcher tests, not claims about filesystem path
length support. Actual path/candidate/file/byte bounds remain separate controls.

The seven added product regressions preserve match/no-match semantics and expose repeated
states, separated globstars, long path/rule strings, real CLI timeout backstops, repeated
saved-exclusion consumption and explicit error outcomes. Existing F1-F4 tests remain.
The green total is supporting evidence, not a substitute for these assertions.

## Commands and outcomes at this exact result

| Command/scenario actually run | Outcome |
|---|---|
| `python -B bin\li-work-artifacts.py --repo . --map .claude\plans\universal-implementation\work.json` | PASS; approved map unchanged. |
| Local `git show` of the first report, extract its PowerShell-embedded Python and run unchanged with `python -B -` | PASS: exact F1-F4 replay, four cases, zero skips. |
| Same extraction from the previous quality report | PASS: exact Q1 CLI replay, both valid patterns unmatched; timings above. |
| `bash tests\unit\context-safety.sh` | PASS: 22 actual tests, including seven Q1 regressions and all previous context/case/role/capacity cases. |
| `bash tests\unit\snapshot-ownership.sh` | PASS: 24 actual tests; per-file recovery, persistent injected publication denial and native Windows junction refusal. |
| `bash tests\unit\url-policy.sh` | PASS: 5 actual tests, no network. |
| `bash tests\unit\context-checkpoint-roundtrip.sh` | PASS. |
| `bash tests\unit\context-repository-ownership.sh` | PASS, including detached and named historical scopes. |
| `bash tests\unit\memory-v2.sh`; `bash tests\shape\claude-home-paths.sh` | PASS. Existing warn-hook is invoked only inside synthetic fixtures, not activated. |
| `python -B -`, independent DP-state/comparison tracing and repeated cooling probe | PASS; exact cell/comparison counts and preserved bytes above. |
| `python -B -`, prior-matcher finite semantic comparison and native/injected case fixtures | PASS; all 182520 finite comparisons agree and both filesystem branches retain intended behavior. |
| `python -B -`, AST parsing of both Q1 changed Python files and injected identity-error cases | PASS; both consumers report explicit failure rather than empty success. |
| `git diff --check 21261f1ff76be994246060a7817924f2893f2454 399a2e6b03a9ca3b3dfaddc4f38498f9f88115f4` | PASS. |
| `python -B bin\li-catalog.py --check` | EXPECTED FAIL: catalog stale; outside P03 writer ownership, not hidden by package acceptance. |

The three product suites execute **51 tests**, retaining the previous 44 and original
32. Replayed review fixtures and finite semantic pairs are additional observations, not
newly counted product tests. No validation command failed in this pass except the
explicitly separated known generated-catalog check.

### Replaying the previously published defects

From this pinned checkout, PowerShell can rerun both original report fixtures without
editing them or checking out another worktree:

```powershell
@'
import re
import subprocess
import sys

reports = [
    "d0f4552347d7312073bbb42c84e18df9f66ef727:.claude/plans/universal-implementation/reviews/P03.md",
    "98515a1c4db4796d03005529d61f021bcc2d0df1:.claude/plans/universal-implementation/reviews/P03-recheck.md",
]
for reference in reports:
    text = subprocess.run(["git", "show", reference], check=True,
                          capture_output=True, text=True).stdout
    replay = re.search(r"```powershell\n@'\n(.*?)\n'@ \| python -B -\n```", text, re.S)
    assert replay is not None
    subprocess.run([sys.executable, "-B", "-"], input=replay[1], text=True, check=True)
'@ | python -B -
```

This final report's replay block was itself extracted and executed successfully.

## Limits and separate integration obligations

- Review tests mutate only disposable synthetic fixtures. Git-using/compatibility runs
  use synthetic HOME/USERPROFILE/LINTEL_HOME, isolated Git configuration, fixture-only
  hook paths and disabled signing. Python bytecode writes are disabled. No credentials,
  personal/private state, network, global install, production action, real-worktree
  recovery or nested agent was used.
- Native evidence is Windows/Git Bash/Python 3.11. Case-sensitive identity and selected
  I/O failures are explicitly injected; no live POSIX/case-sensitive-volume acceptance
  is claimed. Local timings are observations, not cross-host benchmarks or SLAs.
- The original documented recovery boundary remains: regular owned files and recorded
  modes; isolated/quiescent target; per-file rather than whole-tree atomicity; no
  tamper-proof metadata, live-service rollback, hard-crash durability or portable
  cross-process compare-and-swap. Unknown old journals are preserved for manual action.
- Actual single-hop browser/HTTP transport, live host telemetry/pricing, mandatory-profile
  integration, complete installer ownership wiring and the unowned
  `ContextBudgetAdvisor` role remain separately assigned work. Missing browser/telemetry
  was not replaced with fake evidence.
- **Coordinator catalog debt:** regenerate the stale catalog from source before integrated
  acceptance. Its known failing check is not an open P03 product finding.
- **P08 historical capacity proxies:** previously passing string checks still label
  historical example thresholds as a default cap. They were not rerun or counted as
  capacity evidence here and still require reconciliation. Package PASS does not close
  that obligation.
- No full repository suite, CI, remote/current-main comparison, fresh consumer install,
  private-pack policy run or live client/model acceptance occurred. Those integration
  and human review gates remain with MasterSession.

## Final disposition

Accept P03 specification/preservation and quality for
`21261f1ff76be994246060a7817924f2893f2454..500adb370c726b86047046998a6a5240ebd8ea8f`.
F1-F4 remain closed and Q1 is now closed by an algorithmic repair with discriminating
semantic, state-bound and consumer evidence. No new P1/P2/P3 issue was found in this
bounded final pass. Review approval is revision-scoped; later repairs or integration
changes require their applicable checks.

Only this report belongs in the review commit. Shared package/leaf status, integration,
generated outputs and delivery decisions remain coordinator-owned.

**Cycle position:** REVIEW (spec PASS, quality PASS) -> coordinator integration and
integrated acceptance. No blanket SHIP or production authorization.
