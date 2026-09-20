# P07 third-candidate independent review

**Date:** 2026-09-20

**Reviewer:** Universal profile review, session `a7d78944-c02c-4909-a060-2c4f2a754b00`

**Scope:** P07 component; A07.1-A07.5 and the package's A20.3/A20.4 contracts.

**Disposition:** **BLOCKED - return to BUILD for P07-F04.**

| Stage | Result |
|---|---|
| 1 - Specification compliance | FAIL: one reproducible Windows concurrent-bootstrap deviation |
| 2 - Full bounded code quality | NOT RUN: Stage 1 did not pass |
| 3 - Compliance gates | NOT RUN: prerequisite stages did not pass |
| Integration, release or ship clearance | NOT GRANTED |

P07-F01, P07-F02 and P07-F03 are closed on this candidate within the independently
replayed cases below. A new P2 correctness/reliability finding prevents approval.
There are **0 open P1, 1 open P2, 0 open P3 specification findings**. These counts
are not a code-quality or security-audit verdict; those stages did not run.

## Identity and authority

| Item | Exact identity |
|---|---|
| Mapped requirements/tasks | `.claude/plans/universal-implementation/work.json`, `spec.md`, `plan.md`, `packages/P07.md` |
| Architecture | ADR-0018, ADR-0026, ADR-0028 and ADR-0029; directly related pack documentation |
| Integration base | `40c279520a86945cc7e607692355bf5231446ff1` |
| Included public-accessor dependency | `b4e93162b95ea2562a04316fd0cfd251010a4028` |
| Initial P07 implementation | `912420f91729f1618b8f22804ea7ccd95bd7f6e8` |
| Previous repair | `d02bb248b61dbbc703eb5252f5b46d86bdfc102b` |
| Frozen third product candidate | `56981edc4bd73020fea78e20526b10d62e822305` |
| Product candidate Git tree | `8fad3c5c210401df570f57b34bb88bd8eff4e194` |
| Reviewed report tip / checkout parent | `1e9a26b11a39a0945e34003089d61aaf354a9c55` |
| Review-only branch | `jokerman-microsoft-universal-profile-final-review` |
| First review preserved | `9edf8c1e44c33a0530772eefd2d6537182d7fdda`, `reviews/P07-component.md` |
| Second review preserved | `ce386bad173c85d2628a89f26542d5608026f5c7`, `reviews/P07-recheck.md` |

The difference from `56981ed` to `1e9a26b` is only the builder's
`reports/P07.md`. Neither earlier review branch/report was overwritten or
reinterpreted as approval. This review used a separate clean checkout under
gitignored runtime, then added only this review artifact. The reviewer implemented
none of the product changes and made no product, shared-plan, memory or ADR edits.

The explicit work map was validated with `bin/li-work-artifacts.py`. Review follows
the Copilot adapter and canonical three-stage REVIEW gate. Builder-reported results
are not substituted for the commands actually executed here.

## P07-F04 - Equivalent Windows runtime paths fail containment during bootstrap

**Severity:** P2 - must fix before this component's specification acceptance.

**Confidence:** 10/10 for the reproduced Windows/Python 3.11.9 condition.

**Primary location:** `lib/profile_context.py:655-659`.

**Affected path:** `_lock` at `748-750`, called by `bootstrap_profile_context`
at `859-870`.

**Failed acceptance:** A07.3; the actual two-fresh-process test at
`tests/integration/universal-profile-context.py:247-269`.

`_runtime_path` resolves the candidate and then compares it lexically with
`config.home` and the target runtime root. On Windows, Python's non-strict
`Path.resolve()` can return an extended-length `\\?\C:\...` spelling when another
bootstrap creates missing parent directories between native path lookups.
The configured roots still have the equivalent ordinary `C:\...` spelling.
`Path.is_relative_to()` treats their anchors as different and raises `PROFILE_IO`,
although the candidate is inside the authorized target runtime directory.

Observed values, with the synthetic temporary prefix abbreviated:

```text
path:     C:\<synthetic-fixture>\target\.claude\runtime\profiles\selected.json
resolved: \\?\C:\<synthetic-fixture>\target\.claude\runtime\profiles\selected.json
repo:     C:\<synthetic-fixture>\target
error:    PROFILE_IO: profile runtime must stay in selected LINTEL_HOME or target runtime
```

The untouched full lifecycle suite returned **42 passing methods and 1 failure**
in 462.844 seconds. This was not a timeout or missing dependency. Ten subsequent
ordinary repetitions of the failing method passed, so those repetitions do not
erase the first failure. A trace-only observer then reproduced the failure on the
**fifth triple of actual concurrent Bash bootstraps**: one returned status 2 with
the values above; the other two returned the same valid generation-1 reference.
No resolver or path function was replaced in that observation.

A separate deterministic native-filesystem schedule reproduces the cause:
after the first native lookup reports missing parents, create those authorized
parents before Python finishes resolving the same path. The guard then rejects
the extended-length spelling. Retrying the identical selected path after the
parents exist succeeds; a genuinely unapproved path still fails.

This is a false rejection of authorized work, **not** a neutral-policy bypass or
evidence destruction. It nonetheless violates the promised stable concurrent
no-ID bootstrap and prevents the required test from reliably passing. The affected
helper belongs to the P07 implementation even though these lines were not newly
changed in the last repair.

**Required correction:** use a consistent, platform-correct resolved path identity
for the candidate and approved roots, including Windows extended DOS/UNC spellings.
Preserve symlink/reparse resolution and the out-of-root rejection boundary. Do not
fix this by disabling containment, accepting arbitrary prefixes, dropping the test
or merely adding an unconditional retry. Add a discriminating Windows regression
and rerun the genuine parallel-bootstrap and full lifecycle cases.

### Deterministic diagnostic reproduction

Run the following Python from the frozen candidate root on Windows Python 3.11.9.
The trace only schedules creation of approved directories between two real native
filesystem lookups; it does not change the product, substitute `Path.resolve`, or
mock `_runtime_path`. It creates and removes its own temporary fixture.

```python
import importlib.util
import ntpath
import sys
import tempfile
from pathlib import Path

assert sys.platform == "win32"
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location(
    "reviewed_profile", Path.cwd() / "lib" / "profile_context.py"
)
profile = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = profile
spec.loader.exec_module(profile)

with tempfile.TemporaryDirectory(prefix="lintel-native-path-review-") as temp:
    base = Path(temp)
    source, repo, home = base / "source", base / "repo", base / "home"
    for folder in (source, repo / ".claude", home / "packs"):
        folder.mkdir(parents=True)
    config = profile.ProfileConfig(
        source, repo, home, home / "packs", home / "packs" / "active-pack",
        context_id="synthetic-work",
    )
    observed, triggered = {}, []

    def schedule(frame, event, argument):
        if frame.f_code is ntpath.realpath.__code__:
            if (event == "exception"
                    and isinstance(argument[1], OSError)
                    and getattr(argument[1], "winerror", None) == 3
                    and ntpath.normcase(str(frame.f_locals.get("path")))
                    == ntpath.normcase(str(config.selected))):
                config.selected.parent.mkdir(parents=True, exist_ok=True)
                triggered.append(True)
            return schedule
        if frame.f_code is profile._runtime_path.__code__:
            if event == "exception":
                observed["resolved"] = str(frame.f_locals["resolved"])
            return schedule
        return None

    sys.settrace(schedule)
    try:
        profile._runtime_path(config, config.selected)
    except profile.ProfileError as error:
        observed["code"] = error.code
    finally:
        sys.settrace(None)

    assert triggered == [True]
    assert observed["code"] == "PROFILE_IO"
    assert observed["resolved"].startswith("\\\\?\\")
    profile._runtime_path(config, config.selected)
    try:
        profile._runtime_path(config, base / "unapproved" / "record.json")
    except profile.ProfileError as error:
        assert error.code == "PROFILE_IO"
    else:
        raise AssertionError("unapproved path was admitted")
    print("P07-F04 reproduced; same-path retry passes; outside path stays denied")
```

This reproduction's successful exit means the **defect was reproduced**, not that
the candidate meets the acceptance criterion.

## Previously blocking findings

| Finding | Verdict on third candidate | Independent evidence |
|---|---|---|
| P07-F01 - reference-only resume loses required selection | CLOSED in tested scope | Replayed the original first-report Python block unchanged. Fresh receiver returns the exact strict reference, `required:true`, `loaded/applicable`, and `hard`. The additional real-worktree receiver and inherited child agree. |
| P07-F02 - current/selected publication order | CLOSED in tested scope | Real Python writer A paused after current publication but before selected publication; both locks remained held. Actual writer B waited on the selected lock. Successful writers returned generations 2 and 3, and current/selected both ended at 3. History 1/2/3 remained intact; history-backed stale-selection recovery explicitly advanced to 4. |
| P07-F03 - bootstrap/ID-only pin loss recreates neutral state | CLOSED in tested scope | Replayed the original second-report Python block; the former neutral-success path now exits at `PROFILE_CONTEXT_MISSING` with `required:true`, `error/unknown`. Independently exercised all five selection entrypoints under both invocation-scoped and repository-required selection, without hidden pre-sourcing for bootstrap. |

The independent ten-scenario selector matrix covered bootstrap, bind, verify,
rebind and compatibility clear. For each policy/entrypoint combination it asserted:
the same canonical reference in the caller and an actual inherited Bash process;
strict loaded policy; missing and malformed-replacement pins rejected in both
processes; no field value on failure; byte-identical retained history through
rejections; reason-bearing recovery to the next generation; required selection
preserved; and a later child rebind rejected by the parent until explicit verify.
History generations remained consecutive in these actual recovery scenarios.

Separate actual Python API cases established that `create=True` cannot reset a
known missing generation, stale expected references and fabricated selected
references cannot authorize recovery, valid latest-history recovery preserves
required policy and older bytes, and genuine neutral first use/new repository-
required work still initializes normally.

## Per-leaf specification verdicts

| Leaf | Component verdict | Evidence and boundary |
|---|---|---|
| A07.1 | PASS | ADR-0029, external requirements declaration and selection precedence explicitly separate required, optional-fallback and neutral-first-use behavior. |
| A07.2 | PASS | Structured values, whole-block replacement, null/false/quoted/list distinctions, field source/version/digest and neutral-fallback provenance pass lifecycle and preserved pack tests. |
| A07.3 | FAIL | F01-F03 continuation repairs pass, including an actual isolated Git worktree receiver, but F04 breaks the required concurrent no-ID bootstrap on Windows. |
| A07.4 | PASS for observed component behavior; dependent package acceptance remains blocked | Missing/invalid required input, lost/replaced/stale pins, same-mtime manifest/parent/pointer changes, deletion and changed targets fail explicitly rather than becoming advisory success. |
| A07.5 | PASS for declared synthetic input acceptance | Rapid/strict fixtures change routing, gate and design inputs. This does not establish that a renderer, company control, agent/model task or A24 benchmark executed. |
| A20.3 | PASS | Schema, public product and feature constraints are independently accepted/rejected, including ancestor constraints and the explicit historical-marker migration. |
| A20.4 | PASS for the P07 synthetic compatibility contract | Valid synthetic pack accepts and invalid constraints reject for their declared reasons. External attribution/license and complete source-provenance outcomes remain with their owning package and final reconciliation. |

Six leaf-local checks pass and one fails. This is not six authorized task closures:
the dependency chain and the whole package remain unapproved, and shared task state
was deliberately not changed.

## Checks actually executed

Environment: Windows, Git Bash, Python **3.11.9**, standard-library profile helper.
The already supplied task-local `jq-1.8.2` was verified before execution against
SHA-256 `a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`.
No dependency was installed and no personal profile/pack was used.

All Bash checks ran from the frozen checkout through the explicit Git Bash
interpreter, without login/startup files. Profile tests used synthetic isolated
source, target, home and pack directories. Runtime environment selectors were
cleared for the preserved-script batch.

| Command or scenario | Actual result |
|---|---|
| `python bin/li-work-artifacts.py --repo . --map .claude/plans/universal-implementation/work.json` | PASS: explicit approved work map resolves |
| `bash tests/integration/universal-profile-context.sh` | **FAIL: 43 methods, 42 pass, 1 failure, 0 skipped; 462.844s**. Exact failed method: `ProfileLifecycle.test_concurrent_no_id_bootstraps_share_one_binding`. |
| Same shell runner with that method named ten times | PASS: 10/10, 49.881s; intermittent failure not waived |
| Trace-only actual concurrent-bootstrap triples | First four triples passed; fifth produced one `PROFILE_IO` failure and two matching valid references; 31.344s |
| Deterministic native-filesystem F04 schedule above | Defect reproduced; authorized same-path retry passes and genuinely outside path rejects |
| Independent five-entrypoint by two-policy matrix | PASS: all 10 scenarios, 223.282s |
| Actual-writer F02 publication barrier and stale-selection recovery | PASS: 7.288s |
| Actual second Git worktree plus fresh reference receiver and inherited child | PASS: 19.002s; approved original policy target retained. Changing target gives missing-context failure; forcibly pointing at old pin gives drift failure. |
| Independent Python history/creation and genuine-new-work cases | PASS: 2/2, 0.762s |
| Original F01 reproduction, unchanged | Correct strict continuation; status 0 |
| Original F03 reproduction, unchanged | Correctly rejects the former unsafe path with `PROFILE_CONTEXT_MISSING`; no neutral success |
| `git diff --check 40c2795 56981ed` | PASS |
| Separate `bash -n` invocation for each of all nine changed shell files | PASS |
| Python grammar parse with `feature_version=(3, 9)` and compile on 3.11.9 | PASS for helper and lifecycle tests; **not a Python 3.9 runtime execution** |

All nine preserved scoped scripts completed successfully with verified `jq`:

```text
tests/unit/enterprise-pack-resolution.sh
tests/unit/pack-inheritance-depth-3.sh
tests/shape/pack-resolver-fallbacks.sh
tests/integration/pack-source-target-resolution.sh
tests/integration/enterprise-pack-impact.sh
tests/shape/extension-pack-contract.sh
tests/unit/capture-vault-sink.sh
tests/unit/brief-forge-evaluator-runs.sh
tests/shape/adr-numbers-unique.sh
```

These include the public-accessor handoff consumer, installed-source/target
separation, actual routing/evaluator inputs, extension validation/scaffolding,
preserved list/boolean/whole-block behavior, and 29 unique ADR numbers. They do
not turn the failed lifecycle run into a green aggregate.

## Stage gates, limitations and handoff

The initial two review passes stopped at specification failures. This third pass
also stops there. **The first full bounded P07 quality review is still NOT RUN.**
No quality score, dependency/security clearance, active-pack compliance verdict or
human approval is implied by the passing cases.

The remaining integration gates are explicit:

- **P05:** consuming the policy bridge does not itself prove mandatory controls
  passed or content-bound independent review clearance.
- **P06:** real host-adapter/session execution and regenerated portable bundle
  acceptance remain distinct from these local helper tests.
- **P08:** work-map/handoff/resume consumers must carry the same profile identity;
  they were not accepted as a joined system here.
- **P14/A24:** full strict aggregate, fresh consumer installation, generated drift
  checks, actual company-task outcomes, paid/client/model runs, measured value and
  the final reconciled independent review remain unverified.

This pass did not run Linux/macOS or actual Python 3.9 runtime validation, the full
repository strict suite, authenticated clients, CI, remote operations, private
policy activation, hook registration or any production action. The diagnostic
Windows reproduction is not a cross-host assertion. Actual synthetic worktree
fixtures and diagnostic temporary directories were cleaned up; the immutable
review checkout and earlier report branches remain available.

**Coordinator disposition after three specification iterations:** the original
builder must first submit a narrow path-identity/containment re-plan and native/
injected boundary-test plan for MasterSession's repair-card review, **before code**.
No blanket prefix stripping, weakened guard or new broad audit is authorized.
This reviewer finishes the bounded report only and performs no repair or quality pass.

After coordinator approval, a repaired immutable checkpoint can receive the
required specification recheck. The full bounded Stage 2 review still requires
Stage 1 PASS; do not mark it complete from a narrow path repair, or mark P07
complete from F01-F03 closure alone.
