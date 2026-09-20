# P07 Windows repair and whole-component independent review

**Date:** 2026-09-20

**Reviewer:** Universal profile review, session `a7d78944-c02c-4909-a060-2c4f2a754b00`.
The reviewer implemented none of the reviewed product changes.

**Verdict:** **PASS for the owned P07 component on the reviewed local contract.**
P07-F01 through P07-F04 are closed in the tested scope. The first full bounded
quality review has now run and passed. **Final P07/Universal integration and
SHIP acceptance are not granted.**

| Sequential gate | Result |
|---|---|
| Stage 1: narrow Windows repair plus retained component specification | PASS, before starting Stage 2 |
| Stage 2: full bounded P07 quality, not just the Windows delta | PASS; 0 new P1, 0 P2, 0 P3 findings |
| Stage 3: authorized local review boundaries and synthetic neutral baseline | Satisfied in that scope only; real company/host gates were not run |
| P05/P06/P08/P14 joined acceptance, release and human approval | OPEN; not supplied by this report |

No old rejection is rewritten as an approval. Earlier reports remain evidence of
their exact earlier products, including the genuine F04 failure despite subsequent
passing repetitions. There are no open component findings from these four passes;
that statement is not a platform certification or clearance of downstream links.

## Exact identity and authority

| Item | Identity |
|---|---|
| Integration base | `40c279520a86945cc7e607692355bf5231446ff1` |
| Declared narrow P04 dependency | `b4e93162b95ea2562a04316fd0cfd251010a4028`, only the Brief Forge public accessor |
| Original P04 source | `8ea0fc4e4280803d1093468d06828daa54f9c700` |
| Initial P07 product | `912420f91729f1618b8f22804ea7ccd95bd7f6e8` |
| First repair product | `d02bb248b61dbbc703eb5252f5b46d86bdfc102b` |
| Third product, with F01-F03 repaired | `56981edc4bd73020fea78e20526b10d62e822305` |
| Approved Windows repair card | `c6736e56ac6d89da52c66016b4d4837d60dcddb1`, `packages/P07-windows-repair.md` |
| Frozen reviewed product / review checkout parent | `a8de5743987cc6ff6a78719d7822a15b8191ebbc` |
| Product tree | `0a616f1c444d9006947d23f30a22c3881a7eca31` |
| Product parent | `ceb38007656d2acfae77bb66b2e8669ed0ad39c4` |
| Additional builder evidence, not a new product | `0d85bbb736098659f2aecf8626a2936964e281a5`, only `reports/P07.md` differs from the product |
| New reviewer branch | `jokerman-microsoft-universal-profile-windows-review` |
| First review preserved | `9edf8c1e44c33a0530772eefd2d6537182d7fdda`, `reviews/P07-component.md` |
| Second review preserved | `ce386bad173c85d2628a89f26542d5608026f5c7`, `reviews/P07-recheck.md` |
| Third review preserved | `e4285fd199969112e042b0dfa5b03994b321a81b`, `reviews/P07-final.md` |

The new clean checkout is under the reviewer's gitignored
`.claude/runtime/review-worktrees/p07-windows-a8de574`. It was created at the
product commit, not reset to the builder's moving branch or to the report-only
tip. The repair card was read from its exact committed object. The explicit
`work.json` map validated; `spec.md`, `plan.md`, `packages/P07.md`, ADR-0018,
ADR-0028, ADR-0029, the adapter and repository review instructions govern the pass.
Shared plan, state, memory, source, ADR and other reviewer files were not edited.

The complete base-to-product diff has 23 paths: 21 P07 implementation/documentation/
test paths, the declared one-path P04 dependency, and the builder report. Stage 2
covers the P07 product, not only the five-path Windows repair. That narrow repair
changes only the comparison helper/guard, directly related documentation and tests.
AST comparison with `56981ed` confirmed that the only changed existing/new helper
definition bodies are `_runtime_path` and `_path_identity`; selection, parser,
reference, history and publication logic were not replaced by the repair.

## Stage 1: Windows repair acceptance

**P07-F04: CLOSED.** On this product, the original native missing-parent schedule
now succeeds on its **first** containment call. The same native lookup initially
raises WinError 3; the trace creates only the approved missing parent directories;
`ntpath.realpath` actually returns the extended-length spelling. No path function,
guard, I/O result or return status is substituted.

Observed forms, with only the synthetic temporary prefix abbreviated:

```text
ordinary: C:\<synthetic-fixture>\repo\.claude\runtime\profiles\selected.json
native:   \\?\C:\<synthetic-fixture>\repo\.claude\runtime\profiles\selected.json
approved: C:\<synthetic-fixture>\repo
result:   first call accepted; same-path control accepted; outside write denied
```

`lib/profile_context.py:655-686` recognizes ordinary/extended absolute drive and
UNC filesystem aliases for comparison only. `:689-697` compares complete resolved
components with frozen home and lexical target-runtime anchors. It does not use
string-prefix containment, globally case-fold Windows names, follow a redirected
runtime into a new approved root, or rewrite I/O locations, manifests or digests.
Unestablished casing equivalence remains a conservative rejection.

The 13-method path suite passed with **zero skips**, including actual native
ordinary/extended drive reads/writes, actual distinct case-sensitive sibling
directories, file/directory symlinks and junctions. Different drives/shares/servers,
sibling prefixes, unsupported device namespaces, ADS, ambiguous names and
unresolved traversal remain rejected. Outside write attempts leave no outside
file; an existing outside file behind a symlink remains unchanged. An inside
symlink continues to work.

UNC checks are **pure injected/comparison-data evidence**, not live-share I/O.
The spelling-injected bootstrap also preserved the exact reference, input hashes,
provenance and current-record bytes. It is labeled separately from native evidence.
Case sensitivity was enabled only on the disposable fixture directory and verified
with two distinct actual filesystem objects; no global setting was changed.

The untouched lifecycle suite passed **44/44 methods**, including the original
concurrent-bootstrap case and the added 12 separate rounds of three actual Bash
bootstraps. Each round retained one required generation-1 reference in all three
processes and on disk. No failed attempt was discarded or retried into success.

| Repair-card leaf | Independent disposition |
|---|---|
| A07.3.w1 | The original native failure/schedule remains recorded at `e4285fd`; the same causal schedule was exercised against the new product with explicit repaired expectations below. |
| A07.3.w2 | PASS: comparison-only ordinary/extended drive and UNC identities, exact resolved components and approved anchors inspected and tested. |
| A07.3.w3 | PASS: native first-call acceptance, native drive I/O, unchanged bootstrap reference/provenance and real concurrent triples. |
| A07.4.w1 | PASS: device/ADS/traversal/outside/reparse/case-distinct negatives; no-write controls, with native and injected categories separate. |
| A07.4.w2 | PASS: all 43 original lifecycle methods retained within the 44-method suite, plus 13 path methods and all nine preservation scripts. |
| A07.4.w3 | PASS for this checkpoint: same independent reviewer completed Stage 1 and then the first full bounded component quality pass. Final integration is still separate. |

### Executable repaired acceptance

Run from the frozen product root with Windows Python 3.11.9 using a PowerShell
single-quoted here-string piped to `python -B -s -`. This block was executed from
this report as well as during investigation. A zero exit here means **repaired
acceptance**, unlike the old F04 report's zero exit, which meant defect reproduced.

```python
import importlib.util
import ntpath
import sys
import tempfile
from pathlib import Path

assert sys.platform == "win32"
spec = importlib.util.spec_from_file_location(
    "reviewed_profile", Path.cwd() / "lib" / "profile_context.py"
)
profile = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = profile
spec.loader.exec_module(profile)

with tempfile.TemporaryDirectory(prefix="lintel-f04-acceptance-") as temp:
    base = Path(temp)
    source, repo, home = base / "source", base / "repo", base / "home"
    for folder in (source, repo / ".claude", home / "packs"):
        folder.mkdir(parents=True)
    config = profile.ProfileConfig(
        source, repo, home, home / "packs", home / "packs" / "active-pack",
        context_id="synthetic-work",
    )
    before = (str(config.repo), str(config.home), str(config.selected))
    triggered, native_returns = [], []

    def schedule(frame, event, argument):
        if frame.f_code is ntpath.realpath.__code__:
            if (event == "exception" and isinstance(argument[1], OSError)
                    and getattr(argument[1], "winerror", None) == 3
                    and ntpath.normcase(str(frame.f_locals.get("path")))
                    == ntpath.normcase(str(config.selected))):
                config.selected.parent.mkdir(parents=True, exist_ok=True)
                triggered.append(True)
            if (event == "return" and triggered and isinstance(argument, str)
                    and argument.endswith("\\selected.json")):
                native_returns.append(argument)
            return schedule
        return None

    previous_trace = sys.gettrace()
    sys.settrace(schedule)
    try:
        profile._runtime_path(config, config.selected)
    finally:
        sys.settrace(previous_trace)

    assert triggered == [True], triggered
    assert any(value.startswith("\\\\?\\") for value in native_returns), native_returns
    assert before == (str(config.repo), str(config.home), str(config.selected))
    assert not config.selected.exists()
    profile._runtime_path(config, config.selected)
    outside = base / "unapproved" / "record.json"
    try:
        profile._write_json(config, outside, {"must_not_write": True})
    except profile.ProfileError as error:
        assert error.code == "PROFILE_IO", error.code
    else:
        raise AssertionError("unapproved path was admitted")
    assert not outside.exists()
    print("PASS: F04 first native call and same-path control accepted; outside denied")
    print("ordinary=" + str(config.selected))
    print("native=" + native_returns[0])
```

## Retained F01-F03 closures

| Finding | Current verdict and independently executed evidence |
|---|---|
| F01: verification did not bind subsequent shell reads | CLOSED. The original first-report Python block was replayed unchanged on this product and returned the strict reference, required/loaded policy and `hard`. Fresh receivers with a changed ambient host ID and actual inherited children agree. Failed verification preserves the earlier binding. |
| F02: concurrent current/selected publication could go backwards | CLOSED. A trace-only real writer paused after current generation 2 and before selected publication. Both actual locks remained held. A second real writer reached and waited on the selected lock. Returned generations were 2/3; final current and selected were both 3. History-backed stale-selection recovery advanced to 4 with older bytes unchanged. Fabricated recovery and another context's selection remain protected in the full suite. |
| F03: selecting entrypoints could lose required policy or adopt a child generation | CLOSED. The original second-report block now rejects its old rc0 expectation at `PROFILE_CONTEXT_MISSING`, with required/error/unknown and no neutral success. This expected rejection is not counted as an unchanged-harness PASS. Repaired acceptance was separately tested for all five entrypoints and both policy sources. |

The independent ten-case matrix used bootstrap, bind, verify, rebind and compatibility
clear under both invocation-scoped and repository-required policy. It checked the
canonical reference in the caller and an actual child; strict policy; missing and
corrupt pin rejection; no field value on failure; byte-identical retained history;
reason-bearing recovery to the next generation; and rejection of the old expected
generation until explicit verification. Bootstrap did not depend on hidden resolver
pre-sourcing. The shipped suite additionally checks parent rejection after a child's
rebind, ID-only/Python `create=True` history protection, rollback/ambiguous history,
explicit conflicts and legitimate neutral first use/new work.

### Actual different-worktree boundary

A temporary **real detached Git worktree** of `a8de574` was created and its distinct
Git top-level verified. A fresh Bash receiver running there, plus its actual child,
consumed the original reference with a different ambient host ID and retained strict
required policy. The approved **original policy target/source/home were explicitly
retained**, not inferred from the receiver's working directory.

Changing `LINTEL_REPO_ROOT` to the receiver worktree was rejected with missing context.
Forcing the old context-file path across that target change was rejected as drift.
These are honest supported-use and unsupported-transfer boundaries, not evidence of
automatic different-target propagation. This is real-process/worktree evidence,
not a nested agent/model session or validation of the P06/P08 handoff implementation.
The temporary worktree was removed cleanly; all earlier review worktrees remain.

## Per-leaf specification and preservation

| Leaf | Component result | Preserved behavior and limit |
|---|---|---|
| A07.1 | PASS | ADR-0029 and external requirements distinguish required failure, optional diagnostic fallback and valid neutral first use. No emergency advisory values. |
| A07.2 | PASS | Whole-top-level-block inheritance, explicit null/false/empty/quoted/list values, neutral missing-field defaults, configured-store/target/source precedence and per-field manifest provenance remain. Actual BOM/CRLF bytes and same-time comment-only changes are fingerprinted. |
| A07.3 | PASS | F01-F04 closed; stable no-ID bootstrap, explicit work IDs, exact inherited references, native concurrency, cold receiver and separate Git worktree behavior verified within the target boundary above. |
| A07.4 | PASS | Malformed/missing required declarations/packs, lost/replaced pins, changed pointer/manifest/parent/source, deletion and stale/fabricated history fail without neutralization. Explicit rebind preserves prior evidence and does not steal another selection. |
| A07.5 | PASS for owned synthetic input contract | Rapid/strict fixtures change actual routing and control/design inputs. No claim that a renderer, company control, paid model task or A24 benchmark executed. |
| A20.3 | PASS | Schema, pack release, public product and capability axes remain distinct. Ancestor constraints cannot be erased; exact legacy marker and explicit migration behavior are retained. |
| A20.4 | PASS for P07 synthetic compatibility | Compatible synthetic packs accept and incompatible/invalid constraints reject. External source/license attribution and integrated outcomes remain with their owners. |

These are leaf-local component verdicts, not edits to shared task checkboxes or
authorization to waive the dependency chain.

## Stage 2: first full bounded quality pass

Stage 2 started only after the current component specification checks passed.
It covered the full owned base-to-product change and substantive direct consumers,
including the narrow P04 accessor dependency, not merely a green builder report.

| Dimension | Review and evidence |
|---|---|
| Correctness and error handling | Read the complete structured helper and shell adapters: parser `:81-273`, inputs/selection `:302-409`, compatibility/inheritance `:412-633`, identity/storage/lifecycle `:636-953`, CLI and policy bridge `:957-1114`. Independent malformed requirement, byte provenance, deleted input, invalid reference, compatibility and busy-lock probes passed. |
| Data/source and write boundaries | Manifest values remain data, not shell/Python execution. Helpers execute from the approved source; target lookalike code is not imported. Runtime checks retain physical resolution, frozen anchors and explicit errors. Exact required-policy source/version is observable without claiming control enforcement. |
| Concurrency and recoverability | Selected-before-context lock order, atomic individual publication, retained-generation checks and explicit history-backed recovery were read and exercised with real writers. Existing locks time out visibly rather than being stolen. Local records are not claimed to be tamper-proof or a hostile-concurrency sandbox. |
| Performance | Inspected per-read content verification, ancestry/input/nesting bounds and history scans. Re-reading policy bytes is intentional; no timestamp-only cache shortcut was reintroduced. No new daemon/dependency or speculative execution layer. No large-installation stress/SLA claim is made. |
| Maintainability and contracts | One parser/typed representation supplies fields, validation, provenance and identity; one `_profile_accept_reference` publishes all selecting entrypoints. Compatibility axes and JSON transport are documented. No duplicate alias updater or target-side executable fallback was added. |
| Consumer preservation and coverage | Checked actual routing, evaluator, extension, pack-create/validate and neutral capture seams. The declared P04 dependency removes the raw cache reader and preserves error propagation in its public accessor. Existing useful tests were retained; changed old success expectations implement ADR-0029's explicit failure semantics. |

**Findings:** P1 **0**, P2 **0**, P3 **0** in the bounded reviewed component.
No product fix was made by this reviewer. Consumer workflows outside P07 are not
declared integrated solely because their input/accessor seam passed.

The eight additional quality-probe groups passed: exact typed parsing and six
unsupported-input cases; nine malformed requirement declarations plus directory I/O
failure; raw BOM/CRLF provenance and same-time byte-only drift; deleted pointer and
required declaration; eight malformed/stale references without evidence mutation;
semantic prerelease/build/conjunction behavior and eight invalid ranges; preserved
shell options plus an explicitly injected missing-interpreter failure; and an actual
busy lock with no record mutation, followed by explicit retry. The interpreter
failure was a dependency-failure injection, not execution under Python 3.9.

## Commands and results actually obtained

Environment: Windows, `C:\Program Files\Git\bin\bash.exe`, Python **3.11.9**.
The Bash regression batches used the approved task-local jq directory on PATH:

```text
C:\Users\jokerman\reference-repos\copilot-worktrees\jokerman-session-setup\jokerman-microsoft-fictional-broccoli\.claude\runtime\tools\jq-1.8.2
SHA-256: a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627
Version: jq-1.8.2
```

The hash was verified before execution. No installation or global PATH/configuration
change occurred. Bash ran with `--noprofile --norc`; `BASH_ENV`/`ENV` were cleared.
Python used `PYTHONDONTWRITEBYTECODE=1` and `PYTHONNOUSERSITE=1`; inline probes used
`python -B -s -`. Fixtures explicitly set synthetic source, target, home, pack and
audit roots. No actual private profile, home configuration or customer data was read.

| Command/scenario from frozen checkout | Result |
|---|---|
| `bash --noprofile --norc tests\unit\profile-path-identity.sh` | 13/13 PASS, zero skips, 4.540s |
| Independent native acceptance block above | PASS on the first call, real extended return observed, same-path/outside controls pass |
| `bash --noprofile --norc tests\integration\universal-profile-context.sh` | 44/44 PASS, zero skips, 407.336s; includes all original 43 methods and 12 real concurrent triples |
| Inline independent five-entrypoint by two-policy matrix | 10/10 PASS, 165.218s; canonical caller/child reference, pin failure, unchanged history and explicit recovery |
| Inline real detached Git-worktree receiver and inherited child | PASS with original approved target; missing-context/drift controls for target transfer |
| Original F01 report's Python block, unchanged | PASS on current product |
| Original F03 report's Python block, unchanged | Expected fail-closed rejection of its old rc0 assumption; actual missing-pin status 2, required/error/unknown |
| Inline trace-only F02 actual-writer interleaving | PASS: both locks held, B waited, generations 2/3, selected/current 3, explicit recovery 4 |
| Inline eight supplemental quality groups | PASS; no residual fixture state |
| `python -B -s bin\li-work-artifacts.py --repo . --map .claude\plans\universal-implementation\work.json` | PASS, explicit approved map |
| Separate `bash --noprofile --norc -n <file>` for every changed shell file | All 10 files PASS; not one multi-argument check |
| `ast.parse(..., feature_version=(3, 9))` plus `compile(...)` on helper and both Python test files | PASS as 3.9 grammar / 3.11 compilation only; **not actual Python 3.9 runtime evidence** |
| `git diff --check 40c279520a86945cc7e607692355bf5231446ff1 HEAD` before report creation | PASS |
| AST definition comparison against `56981ed` | Only `_path_identity` / `_runtime_path` differ; retained lifecycle implementation unchanged |
| Synthetic neutral baseline and stdlib-import inspection | PASS in local scope; no company gates or external dependency audit claimed |

All nine preservation scripts below ran to exit 0, with zero skips and the actual
jq assertions executed. The shape fallback script also executes its retained unit
scenario file.

```text
tests\unit\enterprise-pack-resolution.sh
tests\unit\pack-inheritance-depth-3.sh
tests\shape\pack-resolver-fallbacks.sh
tests\integration\pack-source-target-resolution.sh
tests\integration\enterprise-pack-impact.sh
tests\shape\extension-pack-contract.sh
tests\unit\capture-vault-sink.sh
tests\unit\brief-forge-evaluator-runs.sh
tests\shape\adr-numbers-unique.sh
```

One probe-preparation attempt failed before executing a regression: Git's ambiguous
`show <revision>:<long-path>` lookup hit Windows filename-length handling from the
nested checkout. The unchanged blocks were then read from the preserved review
files and actually executed. This was not a product failure or a discarded failing
product run. No source was changed to obtain a passing result.

## Compliance boundary and remaining final gates

The local review used only its granted read-only product/test authority and synthetic
fixtures. The explicit neutral fixture has advisory mode, empty company/voice gates,
disabled extension awareness and disabled vault sink. The new helper imports only
Python's standard library; no third-party dependency or executable configuration
was introduced. This is not an online vulnerability/license check, assessment of
the operator's active private pack, or a claim that any host hook or policy enforced.
No nested agents, network/GitHub/account actions, private activation, global settings,
paid models, production mutations, push or other-source edits occurred.

The final gates remain explicit:

- **P05:** the actual canonical `evaluate_controls(..., required_policy=...)` bridge,
  mandatory control outcomes and exact-content independent review clearance need their
  own joined evidence. Another session's probe is not this reviewer's bridge approval.
- **P06/P08:** actual host operations, work/handoff/capture/resume transport and
  host-correlated identity remain separately unverified. A same-directory process,
  actual Git worktree or synthetic child is not a complete real-client lifecycle.
- **P14 and owning packaging/reconciliation packages:** integrated tree, strict
  aggregate suite, generated outputs, fresh installed consumer, bundled product
  metadata, cross-platform/runtime matrix and final independent integrated review
  remain open. Only Windows/Python 3.11.9 ran here; actual Python 3.9, Linux/macOS and
  live UNC access were not tested.
- **Human/company acceptance:** private company controls, model/renderer task outcomes,
  host enforcement, external attribution and measured enterprise value are not certified.

**Handoff:** this checkpoint can proceed to the coordinator's separate integration
gates with the owned component spec/quality evidence above. It cannot close the whole
P07/Universal outcome from local tests. Only this report is committed by the reviewer;
the frozen product and all three earlier review branches/reports remain unchanged.

**Cycle position:** REVIEW (owned component spec and quality PASS) -> MasterSession
integration evidence and final independent REVIEW; SHIP remains gated.
