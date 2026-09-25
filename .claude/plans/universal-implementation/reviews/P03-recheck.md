# P03 independent repair recheck and quality review

**Date:** 2026-09-20.
**Stage 1, specification/repair/preservation:** PASS for the reviewed leaf acceptance.
**Stage 2, full bounded package quality:** FAIL; one new P2 requires repair.
**Overall:** not accepted for delivery. No SHIP clearance.
**Open product findings:** P1: 0; P2: 1; P3: 0.
**Earlier findings:** F1-F4 closed for this exact repaired result, not retroactively
removed from the rejected candidate's record.

## Exact identity and review boundary

| Item | Exact reference |
|---|---|
| Original package base | `21261f1ff76be994246060a7817924f2893f2454` |
| Rejected product | `aa7fad47580510248956ffa242887d4457951348` |
| Rejected report-only checkout / repair base | `5c52f2feb4a135e0d2998c7aa188e65f3673ba76` |
| Prior independent review commit | `d0f4552347d7312073bbb42c84e18df9f66ef727` |
| Repaired product/test result | `133eebe60a13d4fa8a67af4dace611a7a330a8e2` |
| Immutable repair-review checkout | `1523e5e7f55ffd753e4ef17b2bd1d6b6b546e60b` |
| Checkout difference from repaired product | Only `.claude\plans\universal-implementation\reports\P03.md` |
| Same independent reviewer | Copilot lintel-reviewer session `d2f01e82-f00a-40fd-96e9-9294a8b01513` |
| New review branch | `jokerman-microsoft-universal-context-safety-recheck` |
| Retained original branch | `jokerman-microsoft-universal-context-safety-review`, still at `d0f4552347d7312073bbb42c84e18df9f66ef727` |

Created the new branch directly at the supplied immutable checkout after confirming the
old review worktree was clean. No reset, builder/master checkout change or source repair
was performed. Only this report is authored in this pass. The old report remains in its
original branch/commit. No nested agent, remote operation or shared-state edit occurred.

Authority remains the approved Universal `spec.md`, mapped `plan.md`, `packages\P03.md`
and the exact CP-01/02/05/13/16, AG-01/12 and RU-07 acceptance read in the first review.
The explicit work map was validated again. No authoritative instructions or acceptance
were changed by the repair. Read the updated implementation report, but accepted evidence
only after inspecting actual source and executing the relevant helpers.

Focused repair range: `5c52f2f..133eebe`, ten previously owned product/test paths.
Full quality scope: `21261f1..133eebe`, all 26 P03 product/test paths, including the
original unchanged portions of the checkpoint, URL, context and recovery changes.
The implementation handoff is documentation, not a twenty-seventh product surface.

## Stage 1: old findings and preservation recheck

The complete four-case replay was read from the prior report using local Git, extracted
unchanged and run with `python -B -` against this checkout: **4/4 PASS, zero skips**.
The three product suites also pass **44 actual tests** (15 context, 24 snapshot, 5 URL).
Counts are not the acceptance argument; the discriminating behavior is recorded below.

| Finding | Disposition and repaired source | Independently observed result |
|---|---|---|
| F1, prior P1 | CLOSED at `bin\li-snapshot.py:248-373` | Version-2 per-file observations/progress consume completed rollback authority. The original interrupted A/B restore followed by a user edit back to the operation post-image is refused without rewriting user bytes. |
| F2, prior P2 | CLOSED at `bin\_context.sh:42-48` and its save/list callers | Exact historical `HEAD` is a safe detached namespace; ordinary branch validation remains. Base-versus-result replay, detached save/list/latest/owned read/warm, return to named history and `HEAD/../escape` refusal pass. |
| F3, prior P2 | CLOSED at `lib\context_safety.py:159-174,243-254,296-323` | Literal exclusions compare filesystem identity; glob case folding requires a same-file probe. Native Windows upper/lower aliases are excluded through both literal and glob consumers. |
| F4, prior P2 | CLOSED at `lib\context_safety.py:186-198` | A fixed-prefix file is returned only for a whole-file selector. Child/recursive patterns under a file return empty/unmatched and CLI exit 1; exact-file and valid directory globs remain usable. |

### Recovery states, not merely the original two-file happy path

Reviewed `pending -> applying -> restored` transitions, persistence order, full-set
preflight, observation validation, result/manifest binding and completion checks:

- Intent is persisted before each source mutation; the recorded `before` observation
  must still match. A failed intent write leaves source bytes untouched.
- Completed entries require their recorded `after` observation, never the old operation
  receipt. Distinct edits, reapplication of the old post-image, and intervening same-byte
  writes with changed modification time are rejected without destructive rewriting.
- Interruption after replacement but before its completion record can recognize a
  verified original without replaying that write. Supplemental fixtures exercised this
  for editing an existing file, recreating an operation-deleted file, and removing an
  operation-created file. In each case only the still-pending files were applied.
- Recreating an already-restored originally absent file is rejected even if its bytes
  equal the old operation output. Its deletion authority is consumed.
- Malformed/missing progress, stale result identity, premature aggregate completion and
  unreadable journal bounds fail without source mutation. The old aggregate-only v1
  journal is refused, preserved byte-for-byte and protected from pruning after the
  normal age/count window. It is not silently upgraded into fresh write authority.
- Ordinary interrupted resume, idempotent unchanged completion, later unrelated WIP,
  staged/unstaged content, snapshot digests and persistent-error preservation still pass.

The added four-test reviewer recovery fixture passed. One initial invocation had an
invalid multiline `with` statement in the review fixture and executed **zero tests**.
After correcting that syntax, the entire fixture ran successfully. No product edit or
acceptance claim was based on the failed invocation.

### Per-leaf specification and retained behavior

PASS here records Stage 1 functional/preservation acceptance at the exact result.
Q1, found subsequently in Stage 2, blocks quality acceptance of the shared selector;
it is not hidden by these passing rows.

| Leaf | Stage 1 | Acceptance and preservation evidence |
|---|---|---|
| A01.1.a | PASS | Literal spaces/metacharacters remain data; hostile input cannot create the marker. Traversal, symlink/reparse and invalid path cases fail. |
| A01.1.b | PASS; Q1 quality concern | Actual warm/related/ADR recipes use the common selector and expose sources/digests/sizes/missing/omitted paths. Whole-file-prefix fix passes actual CLI rejection; normal direct/recursive selection and ranking remain. |
| A01.2.a | PASS | Explicit owner/root, normalized paths, modes, sizes and digests; foreign, malformed, aliased, traversal and native junction inputs are refused. |
| A01.2.b | PASS | Verified bytes, source recheck and atomic activation retained. Transient Windows publication denial is bounded/reported; persistent denial and unrelated I/O failures are failures, not published success. |
| A01.2.c | PASS | Whole-set preflight plus per-file progress/observations protect later edits and consumed authority. Ordinary owned changes/deletions/new-file rollback and index/WIP preservation remain usable. |
| A01.3 | PASS | Exact four-case replay and additional interruption transitions pass. Unsafe v1 aggregate journals and unmanifested backups remain available for explicit manual inspection, not unsafe automatic resume. |
| A01.4.a | PASS | Actual isolated bisect recipe runs on success/error. A fresh five-commit reviewer fixture finds the true midpoint regression, returns the retained trial to its original bad HEAD, clears bisect markers/refs and preserves caller HEAD/staged/unstaged/untracked state. |
| A01.4.b | PASS | Refactor baseline/technique/owned-trial method remains. Snapshot recovery no longer inherits F1. Migration predicate still rejects unknown/unverified/wrong-target/external-side-effect cases; no live migration is asserted. |
| A01.5.a | PASS | Exact host remains distinct from sibling/subdomain/apex; only explicit wildcards broaden. Malformed URL/policy, userinfo, controls, schemes and ports are checked by the actual parser. |
| A01.5.b | PASS within declared adapter boundary | Actual checked redirect loop validates before transport calls. Added zero-redirect and denied-second-hop fixtures pass; allowed relative/authorized redirects and provenance remain. No live HTTP/browser adapter is claimed. |
| A11.1 | PASS | Existing checkpoint owner, repository keys, branch scope, exact legacy attribution, explicit shared history, collisions, empty reservations, plain/unborn and repaired detached HEAD paths all pass. |
| A11.2 | PASS | Unknown capacity/usage remain unknown; source estimates and observed/estimated headroom retain provenance and classification. No assumed universal capacity or synthetic exemption. |
| A11.3 | PASS | Perf entry and flags remain resource advice; 800000 is a preference, not capacity. No marker/configuration mutation or fabricated cost/elapsed/usage. |
| A11.4 | PASS; Q1 quality concern | Literal/glob exclusions have an actual consumer, native case aliases are handled, clearing restores selection, failed policy replacement preserves old policy, zero active tokens/disk bytes are claimed reclaimed. |

The case-sensitive-filesystem branch uses an injected distinct-identity response; it is
not a live POSIX or Windows case-sensitive-volume observation. A supplementary native
probe confirmed `I.txt`/`i.txt` aliasing and correct exclusion; the tested dotless-I
spelling was not a native alias and was not claimed to be one. No filesystem settings
were changed.

## Stage 2: full bounded quality review

This stage began only after the preceding repair/specification recheck passed.
Reviewed correctness, fail-closed errors, ownership/path boundaries, test discrimination,
performance, shared helper reuse and documentation consistency across the full package.

| ID | Severity | Exact repaired-result lines | Finding | Confidence |
|---|---|---|---|---|
| Q1 | P2, must fix | `lib\context_safety.py:176-180`; consumers at `208,322` | Globstar backtracking is not bounded by the advertised candidate/file/byte limits | 10/10 |

### Q1: repeated recursive segments make tiny selections computationally unbounded

`match(i, j)` branches on `**` without memoizing states or imposing a matching-work
limit. Different recursion paths repeatedly evaluate the same `(i, j)` pair.
The 10000-entry walk limit and selected file/byte limits cannot constrain those calls.
This also runs when checking a saved cooling pattern against a single literal file.

**Actual CLI reproduction:** in a new temporary tree containing only 20 nested directories
and one one-byte file, `**/missing.txt` returned unmatched (exit 1) in **0.297 seconds**.
The equivalent valid selector consisting of twelve `**/` segments followed by
`missing.txt` did not complete within the reviewer's **5-second timeout**. Only that
owned child process was terminated. The timeout is a bounded diagnostic, not a claimed
product performance SLA or an estimate of eventual completion time.

**Independent deterministic evidence:** the real matcher reached 100000 segment
comparisons without returning for one 21-component path and a 13-component pattern.
There are only 308 distinct `(i, j)` states including end positions. A review-only
counting wrapper stopped this probe. Applying the same saved glob through
`update_exclusions` and then calling the actual `select_files` on one literal one-byte
source also reached the bound without returning. Source bytes were unchanged.

**Impact:** a permitted short pattern can stall a context selection on a tiny repository.
If stored as a cooling exclusion, the same work is repeated during subsequent selections.
The helper's finite file inventory does not provide a practical computational bound.
This is a new quality finding in code introduced by P03, not a regression reopening the
four repaired findings and not coordinator/P08 catalog debt.

**Required correction:** use memoized or iterative matching with a bounded number of
states; normalize redundant adjacent `**` where useful without relying on that alone
for all backtracking patterns. Preserve the actual-filesystem case rules, literal
metacharacters, whole-path matching and empty/partial CLI status semantics. Add a
deep-path/repeated-glob preservation regression for both selection and saved exclusions.
Do not disable recursive glob support or silently drop the pattern as a shortcut.

### Minimal Q1 replay

Run from this pinned checkout in PowerShell. This calls the real selector through its
CLI, uses only a new temporary tree, and fails at the reviewed result after terminating
the timed-out child. The original four-finding replay remains at the prior review commit;
it now passes unchanged and is not replaced by this new case.
The embedded Q1 replay was also extracted from this report and rerun: the control
returned unmatched in 0.187 seconds and the repeated-globstar case again timed out.

```powershell
@'
from pathlib import Path
import subprocess
import sys
import tempfile
import time

helper = Path.cwd() / "lib" / "context_safety.py"
with tempfile.TemporaryDirectory(prefix="lintel-p03-q1-") as directory:
    root = Path(directory).resolve()
    nested = root
    for number in range(20):
        nested = nested / ("d" + str(number))
        nested.mkdir()
    (nested / "hit.txt").write_bytes(b"x")
    command = [sys.executable, "-B", str(helper), "select", "--root", str(root), "--glob"]
    for pattern in ["**/missing.txt", "**/" * 12 + "missing.txt"]:
        started = time.monotonic()
        try:
            result = subprocess.run(command + [pattern], capture_output=True,
                                    text=True, timeout=5)
        except subprocess.TimeoutExpired:
            raise SystemExit("FAIL Q1: tiny-tree selector exceeded the review timeout")
        assert result.returncode == 1, result.stderr
        print("unmatched:", pattern, "seconds:", round(time.monotonic() - started, 3))
'@ | python -B -
```

### Other quality conclusions

The repaired recovery state machine has explicit transitions and a single journal reader;
intent/completion writes and unsupported-state refusal are exercised, not just described.
No further demonstrated data-loss defect was found in the reviewed supported boundary.
File replacement remains individually atomic, not a whole-tree transaction.

Snapshot locks fail without being stolen; unrelated I/O failures are not mislabeled as
Windows sharing errors or retried. Failed exclusions publication keeps the previous
policy. URL errors, zero redirect budget and disallowed next hops fail before the next
request. Context capacity remains observation-driven. Shared selector, snapshot and
URL helpers are standard-library-only and preserve the existing checkpoint store.

The roles retain causal bisection, baseline/post-refactor checks and partial-migration
classification rather than replacing specialist methods with generic checklists.
Skill/agent metadata and entry-point tests are structural evidence only, not proof of
client behavior, paid model use or enterprise enforcement.

## Executed checks and outcomes

| Actual command/scenario | Outcome at `133eebe` / report-only `1523e5e` |
|---|---|
| `python -B bin\li-work-artifacts.py --repo . --map .claude\plans\universal-implementation\work.json` | PASS; approved authoritative map unchanged. |
| Extract prior report replay from `git show d0f4552347d7312073bbb42c84e18df9f66ef727:.claude/plans/universal-implementation/reviews/P03.md`, execute unchanged with `python -B -` | PASS: F1-F4, four cases, zero skips. |
| `bash tests\unit\context-safety.sh` | PASS: 15 actual tests, including native Windows case aliases and file symlink refusal. |
| `bash tests\unit\snapshot-ownership.sh` | PASS: 24 actual tests, including native Windows junction, v2 recovery and bounded injected rename failures. |
| `bash tests\unit\url-policy.sh` | PASS: 5 actual tests, injected single-hop transport, zero network. |
| `bash tests\unit\context-checkpoint-roundtrip.sh` | PASS. |
| `bash tests\unit\context-repository-ownership.sh` | PASS, including detached HEAD and historical/named-branch preservation. |
| `bash tests\unit\memory-v2.sh`; `bash tests\shape\claude-home-paths.sh` | PASS. Existing warn-hook invoked directly only in synthetic fixtures; no activation. |
| `python -B -`, supplemental v2 recovery matrix | PASS: 4 tests, including three after-apply interruption subcases; prior fixture-only syntax failure disclosed above. |
| `python -B -`, quality error/lock/exclusion/redirect matrix | PASS: 4 tests; real helpers with scoped failure injection. |
| `python -B -`, five-commit bisect success/error fixture | PASS: 1 test with both outcomes; dirty caller and bisect cleanup preserved. |
| `python -B -`, native path-identity probe | Observed ASCII case alias correctly excluded; dotless-I spelling not an alias on this filesystem. |
| `python -B -`, Q1 CLI timeout fixture | FAIL: repeated-globstar selector times out; ordinary equivalent returns unmatched. |
| `python -B -`, Q1 matcher and persisted-exclusion counting probes | Both reproduce 100000 segment comparisons without a result; review-only bounds stop them. |
| `bash tests\unit\context-warm-skills-present.sh`; `bash tests\unit\cohort5-partial-skills-present.sh` | PASS; familiar entry points retained. |
| `bash tests\shape\frontmatter-lint-all.sh` | PASS; structural metadata only. |
| `bash tests\unit\design-locks-cohort3.sh`; `bash tests\shape\handoff-cap-wired.sh` | PASS as historical string checks only, not capacity evidence. |
| `ast.parse` for six source/support Python files; separate `bash -n` for five changed shell files | PASS. |
| `git diff --check 21261f1ff76be994246060a7817924f2893f2454 1523e5e7f55ffd753e4ef17b2bd1d6b6b546e60b` | PASS. |
| `python -B bin\li-catalog.py --check` | EXPECTED FAIL: generated catalog stale; no regeneration performed. |

These are distinct evidence categories. The 44 product tests retain the original 32;
the unchanged four-case replay is an additional run, not four newly added product tests.
The quality failure is not hidden by the green totals.

## Limits and retained integration debt

- All test mutations were in disposable synthetic fixtures. Git-using/compatibility
  runners used synthetic HOME/USERPROFILE/LINTEL_HOME, isolated system/global Git
  configuration, fixture-only hook paths and disabled signing. Python bytecode writes
  were disabled. No credentials, personal state, network, global install, production
  action, destructive recovery on a real checkout or nested agent was used.
- Recovery requires the disclosed quiescent/isolated target. This review does not assert
  portable cross-process compare-and-swap, tamper-proof metadata, hard-crash durability
  or arbitrary filesystem metadata recovery. Stale locks require verified manual action.
  Tests cover native Windows plus explicitly identified injected failures/identity cases,
  not live cross-platform or case-sensitive-volume acceptance.
- Actual browser/single-hop transport, host telemetry/pricing, mandatory profile
  integration and full installer ownership/result wiring remain separately assigned
  P06/P07/P08/P09/P10/P11 work. Missing observations were not replaced with fake data.
  Existing `ContextBudgetAdvisor` constants remain P09's disclosed unowned role work.
- **Coordinator-owned catalog:** its check still fails and must be regenerated from
  source during integration. It is not an additional P03 product finding.
- **P08 capacity proxies:** the two passing historical string checks still call example
  thresholds a default cap. They must be reconciled with the observed/unknown contract;
  their green messages do not prove capacity or enforcement.
- No full suite, CI, remote/current-main comparison, fresh consumer installation,
  private-pack policy or live client/model acceptance occurred. This bounded independent
  review cannot replace those final integration and human review gates.

## Disposition

F1-F4 are resolved for the exact pinned repair. The previously unrun quality stage is
now complete and rejects Q1 as a P2 correction within the owned selector, affecting both
warming and future-exclusion consumers. Return that focused repair with its regressions
at a new immutable result; rerun affected specification/preservation and quality evidence.
No product changes or risk acceptance were made by this reviewer.

Only `reviews\P03-recheck.md` belongs in this review commit. MasterSession owns shared
task status, catalog reconciliation, integration and delivery decisions.

**Cycle position:** REVIEW (spec PASS, quality FAIL) -> BUILD Q1 repair ->
immutable independent recheck. No SHIP clearance.
