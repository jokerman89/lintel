# P07 owned component review

**Date:** 2026-09-20

**Component specification verdict:** FAIL / return to the original builder.

**Specification findings:** P1 = 1, P2 = 1, P3 = 0.

**Component quality verdict:** NOT RUN; Stage 1 did not pass.

**Final P07 / Universal acceptance:** OPEN, not granted by this component review.

## Exact boundary and independence

| Boundary | Exact revision |
|---|---|
| Original baseline | `40c279520a86945cc7e607692355bf5231446ff1` |
| Declared narrow P04 dependency | `b4e93162b95ea2562a04316fd0cfd251010a4028`, from `8ea0fc4e4280803d1093468d06828daa54f9c700` |
| Reviewed P07 product result | `912420f91729f1618b8f22804ea7ccd95bd7f6e8` |
| Report-only input snapshot / review checkout HEAD before this report | `01c189e9d18373df59a5c2a4731f24a91c304b86` |
| Review branch | `jokerman-microsoft-universal-profile-review` |

The dependency changes only the Brief Forge public-accessor snippet (+3/-33).
The owned product diff is **19 files, +2277/-966**, measured from `b4e93162` to
`912420f`; comparing the original baseline to the product includes that twentieth,
separately declared dependency file. The input snapshot adds only `reports/P07.md`.
Both commit boundaries, the entire owned diff, substantive implementation and consumer
context were inspected, rather than accepting the builder's green report.

This is an independent review: this reviewer implemented neither the product nor the
dependency. No product repairs, nested agents, shared plan/state edits, other-source
edits, network/GitHub/account operations or activation were performed. Only this report
is added to the repository. Tests used temporary synthetic sources, homes, packs and
repositories. No actual private profile or personal/global configuration was read.

Authority read: repository/adapter instructions, the canonical review workflow,
relevant memory, pack architecture and ADR-0018, ADR-0028, new ADR-0029, the validated
Universal work map, mapped specification and A07/A20 acceptance, package P07 and its
builder report. No separate `docs/risks/` directory exists in this snapshot.
The task's report-only boundary overrides ordinary workflow state/artifact writes.

## Stage 1 findings

| ID | Severity | Product location | Failed requirement | Confidence |
|---|---|---|---|---|
| F01 | P1 - blocks component acceptance | `lib/pack-resolver.sh:82-89`, with per-call selection at `:59-60` | A07.3/A07.4: reference-only shell resume loses required policy before subsequent consumer reads | Reproduced, 10/10 |
| F02 | P2 - must fix | `lib/profile_context.py:814-833`, especially `:828-832` | A07.3/A07.4: concurrent successful rebinds leave the durable selected reference stale and documented recovery does not repair it | Reproduced, 10/10 |

### F01: successful verification is not a resumed shell binding

Bind an invocation-required `strict` pack, save its reference, and start a fresh shell
carrying that reference and the same approved source/target/home roots, but not the old
context or pack environment variables. Execute the documented sequence:

```bash
source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"
verify_profile_context "$HANDOFF" &&
profile_required_policy &&
resolve_pack_field compliance.mode
```

**Observed:** verification returns the exact original `strict` reference. The next
accessor returns the following, then `advisory`; the complete consumer command exits 0:

```json
{"applicability":"not_applicable","required":false,"source":"bundled-neutral","status":"not_required","version":"1.0.0"}
```

This reproduces both with no ambient host ID and with a different
`CLAUDE_SESSION_ID`. `verify_profile_context` clears `LINTEL_SESSION_ID` only for
its verification call; it neither retains the verified context for subsequent
accessors nor supplies them the verified record. The next call therefore resolves
one-shot neutral data or creates a new ambient-host context
(`lib/profile_context.py:924-930`). The producer record itself remains intact, but
its required policy is no longer the consumer's selected policy.

The advertised shell sequence and identity claim at
`docs/concepts/pack-resolver.md:83-97` do not establish what they promise.
The green tests at `tests/integration/universal-profile-context.py:194-217` and
`:283-294` compare only the verification response. They never read the policy or a
field afterward. This is an owned shell API/documentation defect, not a demand to
pretend that the separate P05/P06/P08 joined integrations already exist.

**Required repair:** make the documented handoff/resume path select and retain the
verified work binding for subsequent shell accessors, without changing the global
active pointer or bypassing explicit-context conflicts. If verification intentionally
stays read-only, provide and use an explicit verified session-selection operation.
Add a producer -> new shell -> verify/select -> actual policy/field consumer regression,
including a changed ambient host ID and invocation-required selection. Do not stop at
comparing reference JSON.

### F02: rebind publishes two related records outside one transaction

Two actual Python subprocesses called the real `rebind_profile_context` implementation.
A trace barrier paused the first process at line 829, after it had written generation 2
and released the context lock, but before its selected-reference update. No product
function, parser, policy result or file operation was mocked.

The second process writes generation 3, sees `selected.json` still naming generation 1
rather than its `previous` generation 2, skips the pointer update and returns success.
The first process resumes, sees its generation-1 predecessor and publishes generation 2.

| Observation | Actual result |
|---|---|
| First / second rebind | Both successful; generations 2 / 3 |
| Durable selected / current record | Generations 2 / 3 |
| Next no-ID bootstrap | `PROFILE_REFERENCE_MISMATCH` |
| Further documented reason-bearing rebind | Creates generation 4; selected reference remains generation 2 |
| Next bootstrap after that rebind | Still `PROFILE_REFERENCE_MISMATCH` |
| History | Generations 1, 2 and 3 retained |

This fails closed rather than returning neutral policy, so it is distinct from F01.
Nevertheless, a permitted interleaving of two successful writes strands fresh-shell
bootstrap; the documented rebind procedure cannot repair the selected reference.
The existing concurrency test at
`tests/integration/universal-profile-context.py:245-269` tests first bootstrap only.

**Required repair:** coordinate current-record and selected-reference publication with
bootstrap and other rebinds, using a consistent lock order or equivalent checked
transaction. Do not introduce context-lock/selection-lock inversion against bootstrap.
Preserve history and stale-reference rejection; require a deterministic real-process
regression and a demonstrated recovery path. Both findings were sent to MasterSession
for the original builder. This reviewer made no repair.

## Per-leaf specification and preservation

| Leaf | Owned component verdict | Evidence, preservation and remaining boundary |
|---|---|---|
| A07.1 | PASS | ADR-0029 explicitly separates required repository/invocation selection, optional legacy preference and genuine neutral first use. Initial missing/malformed required data rejects; invalid neutral baseline rejects. No historic ADR was silently rewritten. |
| A07.2 | PASS | One stdlib parser supplies typed values, whole-top-level replacement, ancestry, origins and compatibility. Block/flow lists, quoting, null/false/empty values, indentationless lists and extension aliases execute. A null block stays null; overwritten parent-field origins disappear. Store -> target -> source precedence and requirement-name precedence are observed. |
| A07.3 | FAIL | Same-target fresh shells, concurrent no-ID bootstrap and an explicitly selected consumer in a real isolated Git worktree work. Reference-only shell consumption fails F01; concurrent rebind/selected-reference continuity fails F02. Different target roots are intentionally not transplanted. |
| A07.4 | FAIL | Initial required-load failures, bound manifest/pointer/parent drift, same-mtime edits, deletion and corruption fail without neutral values and preserve old evidence. Optional legacy rebind is labeled. F01 still loses required status after advertised resume; F02 prevents durable recovery after successful concurrent rebinds. |
| A07.5 | PASS for owned inputs only | Rapid/strict synthetic profiles change real routing and gate-list/evaluator/digest inputs, plus attributed design-token input artifacts. Existing explicit review/research routing and extension behavior remain. This does not prove final design rendering, company-control execution or a joined work lifecycle. |
| A20.3 | PASS for owned compatibility | Pack release, schema, actual installed public product and declared resolver-feature versions are separate. Exact historical `>=4.0.0` remains a legacy marker; ambiguous legacy ranges require migration. Missing product metadata cannot satisfy a requested product range. |
| A20.4 | PASS for owned synthetic-pack checks | Compatible synthetic declarations accept; schema/product/feature/unknown-feature and inherited incompatibilities reject with their own reason. External-contribution provenance is still P13's part, not accepted here. |

Five of seven owned leaf surfaces have passing component evidence; two have concrete
deviations. This is not a percentage of Universal completion or a quality score.

### Origin and trust semantics actually verified

For repository-required policy, `required_policy.source` is the path of the
**requirement declaration**, not the pack manifest. Its `version` is the selected
pack release. The record's ancestry and per-field provenance identify the actual
manifest path/name/version/raw-byte SHA-256. The requirement file's own raw hash
is present in `profile.inputs`. Do not present the compact bridge alone as manifest
provenance or evidence that any control passed.

The configured pack store still precedes an identically named target/source pack.
The repository declaration constrains the required name; it is not a content pin
that secretly overrides the documented approved-store precedence. This distinction
was exercised with synthetic packs and actual origins.

BOM/CRLF inputs retain exact raw-byte hashes. A comment-only change that leaves
effective values unchanged, with the old modification time restored, invalidates the
old context. Hostile target `lib/profile_context.py` data is not executed by the
approved-source bootstrap in the shipped regression. Named source shadowing also
invalidates the previous binding.

### Real worktree boundary, not a same-directory proxy

A reviewer probe created a temporary Git repository and used `git worktree add
--detach` to create a second checkout. A separate Bash consumer ran with that
worktree as its working directory. With the original approved policy target/home/source
and explicit profile context carried forward, verification, a subsequent policy read
and a subsequent reference read retained the exact producer identity and `hard` policy.

Changing `LINTEL_REPO_ROOT` to the second checkout instead returned
`PROFILE_CONTEXT_MISSING`; explicitly pointing it at the old context file returned
`PROFILE_DRIFT`. Those are the declared source/target-boundary protections, not another
defect. No automatic different-target profile propagation was demonstrated or claimed.
This is real subprocess/Git-worktree evidence, not an observed Copilot delegated model
session or the eventual P06/P08 handoff. Synthetic ambient host-ID changes are inputs,
not proof of live host correlation.

## Checks actually executed

All product checks below ran against unchanged product `912420f` in report snapshot
`01c189e`, using Windows Git Bash and **Python 3.11.9**.

| Command / probe | Observed result |
|---|---|
| `python bin\li-work-artifacts.py --repo . --map .claude\plans\universal-implementation\work.json` | PASS; approved map selects the expected original spec/plan/tasks/prompt |
| `bash tests/integration/universal-profile-context.sh` | **22/22 PASS**, zero skips, 100.793 seconds |
| Nine existing scripts below, sequential `&&` chain | **9/9 PASS**, zero skips, including actual jq assertions |
| Reviewer `ResumeConsumer.test_reference_only_resume_keeps_required_policy_for_actual_consumer`, via `python -` | **FAIL**; both absent and changed ambient-ID subcases lose required policy; 9.537 seconds |
| Reviewer `RebindConcurrency.test_concurrent_rebinds_keep_selected_reference_current`, via `python -` | **FAIL**; real-process controlled interleaving and failed recovery above; 0.900 seconds |
| Reviewer `IsolatedConsumer.test_real_worktree_consumer_and_explicit_target_boundary`, via `python -` | PASS; actual second Git worktree and separate shell, explicit-context consumption and two rejected target-transfer variants; 7.448 seconds |
| Seven reviewer `AdditionalPreservation` methods below, via `python -` | **7/7 PASS**, zero skips, 53.550 seconds |
| `bash --noprofile --norc -n <file>` separately for each of the nine changed `.sh` files | PASS for all nine |
| `ast.parse(..., feature_version=(3, 9))` for implementation and new lifecycle tests | PASS **for grammar only**, not an actual Python 3.9 runtime |
| `json.loads` of `lib/profile-context-schema.json` | PASS for JSON syntax, not a claim of complete JSON Schema validation |
| `git diff --check b4e93162 912420f` | PASS |
| `git status --short` before writing this report | Empty; reviewed product and shared state remained untouched |

The nine-script preservation command was:

```bash
bash tests/unit/enterprise-pack-resolution.sh &&
bash tests/unit/pack-inheritance-depth-3.sh &&
bash tests/shape/pack-resolver-fallbacks.sh &&
bash tests/integration/pack-source-target-resolution.sh &&
bash tests/integration/enterprise-pack-impact.sh &&
bash tests/shape/extension-pack-contract.sh &&
bash tests/unit/capture-vault-sink.sh &&
bash tests/unit/brief-forge-evaluator-runs.sh &&
bash tests/shape/adr-numbers-unique.sh
```

The process-local PATH was prefixed with MasterSession's exact approved task-local
jq directory. Before execution, `Get-FileHash -Algorithm SHA256` independently matched
`a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`;
the binary returned `jq-1.8.2`. No download, installation or global PATH/configuration
change occurred. The test environment cleared ambient profile selectors; each script
used its synthetic home/store/audit seams. No full repository suite ran concurrently.

Additional preservation methods executed:

| Method | Discriminating observations |
|---|---|
| `test_required_declaration_is_not_silently_absent` | Ten malformed/missing-required declaration variants plus a directory at the declaration path all return `PROFILE_REQUIRED` without success values |
| `test_deleted_inputs_do_not_replace_bound_evidence` | Requirement, pointer, selected manifest and neutral manifest deletion all return drift; restoring exact bytes restores the original reference; bound record bytes never change |
| `test_raw_byte_provenance_and_same_time_comment_edit` | BOM/CRLF hashes, requirement versus manifest origin, and semantic-equivalent same-mtime drift |
| `test_explicit_null_whole_block_and_typed_scalar_lists` | Null block, removed parent provenance, empty control list and comma/hash/null/false/quoted block-list items |
| `test_store_target_bundle_precedence_has_exact_origin` | Required name beats optional preference; configured store beats target beats source; a newly higher-precedence source invalidates the old binding |
| `test_context_and_selected_corruption_fail_without_rewrite` | Four corrupt-context variants, stale selected generation and missing selected context reject without replacing evidence |
| `test_interrupted_writer_lock_is_not_stolen` | Existing writer lock yields `PROFILE_CONTEXT_BUSY`; no neutral binding or lock theft |

The ad hoc probes reused the committed `ProfileLifecycle` fixture through `runpy`,
not a second parser or mocked P05 consumer. They wrote only synthetic temporary data
and cleaned it up. The two minimal failing reproductions are retained below.

## Reviewed files and consumer preservation

The 19 owned files inspected were:

```text
.claude/decisions/0029-required-profile-context.md
docs/concepts/pack-defaults.md
docs/concepts/pack-inheritance.md
docs/concepts/pack-resolver.md
lib/copilot-env.sh
lib/pack-resolver.sh
lib/pack-schema.yaml
lib/profile-context-schema.json
lib/profile_context.py
packs/_default/pack.yaml
skills/pack-validate/SKILL.md
tests/integration/enterprise-pack-impact.sh
tests/integration/pack-source-target-resolution.sh
tests/integration/universal-profile-context.py
tests/integration/universal-profile-context.sh
tests/shape/extension-pack-contract.sh
tests/unit/enterprise-pack-resolution.sh
tests/unit/pack-inheritance-depth-3.sh
tests/unit/pack-resolver-fallbacks.sh
```

The old tests' pointer-ignore/deletion-tolerance/emergency-default expectations were
compared with the new assertions and ADR-0029. The changed assertions now require a
nonzero drift result without identity/policy values; the initial optional-fallback,
neutral-first-use, inheritance, extension/scaffolder and existing consumer positives
still execute. The jq alternative does not silently skip the former JSON assertions.
The three actual `pack-validate` Bash blocks execute without activation; a malformed
required selector propagates failure rather than empty-selecting `_default`.

Substantive consumer context included `lib/orientator-routing.sh`,
`lib/brief-forge-evaluators.sh`, the corrected Brief Forge skill helper and its guards,
`hooks/shared/session-digest/run.sh`, and current sense/compliance/pack-switch recipes.
The direct public-accessor dependency is preserved. Positive routing/evaluator/digest
tests are not evidence of fail-closed control aggregation: the unchanged snapshot
still contains empty-list/no-op compliance recipes and digest fallback handling.
Their eventual error propagation belongs in the explicitly open consumer integration.
Direct fixture invocation of the digest script is not hook registration or enforcement.

## Remaining gates and limitations

1. **Repair and immutable component re-review:** original P07 builder fixes F01/F02,
   supplies the new product SHA and real regressions; this same reviewer repeats
   Stage 1 before any Stage 2 quality pass. No quality clearance exists for `912420f`.
2. **P05 direct bridge remains OPEN:** run the actual canonical
   `evaluate_controls(controls, required_policy=required_policy(verified_record))`
   producer/consumer link after its implementation is available. It was not run,
   replaced by a stub, or inferred from successful profile loading.
3. **P06/P08 joined lifecycle remains OPEN:** actual operation/work handoff,
   selected-work propagation, capture and cold resume must carry and consume the exact
   reference. Different-target transfer needs an explicit supported decision/path.
4. **Runtime/packaging limits:** Python 3.9 remains the floor, but only Python 3.11.9
   executed here. Actual 3.9, other OS runtimes, installed-consumer bundles and required
   product-metadata packaging need their own evidence. No dependency was installed.
5. **Final review remains separate:** integrated strict suite, generated outputs,
   actual clients/models, live company controls, external provenance and the broader
   design/enterprise outcomes are not accepted by these component probes. No real
   profile activation, hook/policy enforcement, human-review replacement or ROI claim
   follows from this report.

## Executable minimal reproductions

Run either Python block from this immutable repository root, using `python -` and a
PowerShell single-quoted here-string (`@'` on its own line, the block, then
`'@ | python -`). Set `PYTHONDONTWRITEBYTECODE=1` in that process. Both deliberately
exit nonzero on this product revision. They use the shipped fixture and temporary
roots; they do not read personal configuration or modify product files.

Both embedded blocks were extracted from this report and executed again. Each exited 1
at its stated regression assertion; the verification harness confirmed the expected
failure text and observed policy/generation outputs.

### F01: verify, then actually consume policy

```python
import json
import runpy
import sys
from pathlib import Path

root = Path.cwd()
sys.argv = ["probe", "--root", str(root), "--bash",
            r"C:\Program Files\Git\bin\bash.exe"]
fixture = runpy.run_path(
    str(root / "tests" / "integration" / "universal-profile-context.py"),
    run_name="review_probe",
)["ProfileLifecycle"]
case = fixture()
case.setUp()
try:
    case.pack("strict")
    producer = dict(case.env, LINTEL_PROFILE_PACK="strict")
    reference = json.loads(case.shell(
        "profile_context_reference", env=producer,
    ).stdout)
    handoff = case.target / "handoff.json"
    handoff.write_text(json.dumps(reference), encoding="utf-8")
    consumer = dict(case.env, HANDOFF=handoff.as_posix(),
                    CLAUDE_SESSION_ID="different-host-on-resume")
    consumer.pop("LINTEL_PROFILE_CONTEXT")
    result = case.shell(
        'verify_profile_context "$HANDOFF" && '
        'profile_required_policy && resolve_pack_field compliance.mode',
        env=consumer,
    )
    print(result.stdout)
    lines = result.stdout.splitlines()
    assert json.loads(lines[0]) == reference
    assert json.loads(lines[1])["required"], "required policy became neutral"
    assert lines[2] == "hard"
finally:
    case.doCleanups()
```

### F02: actual rebind processes at the vulnerable interleaving

The trace barrier changes scheduling only. Both processes execute the real resolver,
locks, file writes and reference checks; no return values are substituted.

```python
import importlib.util
import json
import runpy
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path

root = Path.cwd()
sys.argv = ["probe", "--root", str(root), "--bash",
            r"C:\Program Files\Git\bin\bash.exe"]
fixture = runpy.run_path(
    str(root / "tests" / "integration" / "universal-profile-context.py"),
    run_name="review_probe",
)["ProfileLifecycle"]
case = fixture()
case.setUp()
process = None
try:
    case.pack("strict")
    case.require("strict")
    helper = str(case.source / "lib" / "profile_context.py")
    spec = importlib.util.spec_from_file_location("review_profile", helper)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    config = module.ProfileConfig(case.source, case.target, case.home,
                                  case.store, case.store / "active-pack")
    first = module.bootstrap_profile_context(config)
    bound = replace(config, context_id=first["context_id"])
    arguments = json.dumps({
        key: str(getattr(bound, key))
        for key in ("source", "repo", "home", "packs", "pointer", "context_id")
    })
    ready, release = case.base / "ready", case.base / "release"
    child = r'''
import importlib.util, inspect, json, sys, time
from pathlib import Path
helper, data, ready, release = sys.argv[1:]
spec = importlib.util.spec_from_file_location("child_profile", helper)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
cfg = m.ProfileConfig(**json.loads(data))
if ready != "-":
    lines, start = inspect.getsourcelines(m.rebind_profile_context)
    pause = start + next(i for i, line in enumerate(lines)
                         if line.strip() == "if config.selected.is_file():")
    def trace(frame, event, arg):
        if (event == "line" and frame.f_code.co_filename == helper
                and frame.f_lineno == pause):
            Path(ready).write_text("ready", encoding="utf-8")
            deadline = time.monotonic() + 20
            while not Path(release).exists():
                if time.monotonic() > deadline:
                    raise RuntimeError("scheduling barrier timed out")
                time.sleep(0.01)
        return trace
    sys.settrace(trace)
record = m.rebind_profile_context(cfg, "synthetic approved replan")
sys.settrace(None)
print(json.dumps(m.profile_reference(record)))
'''
    process = subprocess.Popen(
        [sys.executable, "-c", child, helper, arguments, str(ready), str(release)],
        env=case.env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    deadline = time.monotonic() + 15
    while not ready.exists():
        if process.poll() is not None or time.monotonic() > deadline:
            raise AssertionError("first rebind did not reach barrier")
        time.sleep(0.01)
    second = subprocess.run(
        [sys.executable, "-c", child, helper, arguments, "-", "-"],
        env=case.env, text=True, capture_output=True, timeout=15, check=True,
    )
    release.write_text("continue", encoding="utf-8")
    output, error = process.communicate(timeout=15)
    assert process.returncode == 0, error
    selected = json.loads(config.selected.read_text(encoding="utf-8"))
    current = json.loads(module.context_path(bound).read_text(encoding="utf-8"))
    print("successful rebind generations:",
          json.loads(output)["generation"], json.loads(second.stdout)["generation"])
    print("selected/current generations:", selected["generation"], current["generation"])
    try:
        module.bootstrap_profile_context(config)
    except module.ProfileError as error:
        print("fresh bootstrap:", error.code)
    recovery = module.rebind_profile_context(bound, "synthetic recovery replan")
    print("after documented recovery: current", recovery["generation"],
          "selected", json.loads(config.selected.read_text())["generation"])
    assert selected == json.loads(second.stdout), "selected reference is stale"
finally:
    if process is not None and process.poll() is None:
        process.kill()
        process.communicate()
    case.doCleanups()
```

**Cycle position:** REVIEW (owned component BLOCKED) -> BUILD (original P07 builder)
-> immutable component re-review. Final joined REVIEW remains a separate open gate.
