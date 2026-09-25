# P07 immutable repair recheck

**Date:** 2026-09-20

**Stage 1 component specification:** FAIL. Original F01 and F02 are closed for
their reviewed paths; one additional P1 bootstrap defect, F03, remains.

**Stage 2 component quality:** NOT RUN because Stage 1 did not pass.

**Current findings:** P1 = 1, P2 = 0, P3 = 0. These are specification findings,
not the result of a completed quality review. Final P07/Universal acceptance and
the joined P05/P06/P08 gates remain OPEN.

## Exact revisions and read-only boundary

| Boundary | Revision |
|---|---|
| Original baseline | `40c279520a86945cc7e607692355bf5231446ff1` |
| Declared P04 dependency | `b4e93162b95ea2562a04316fd0cfd251010a4028`, from `8ea0fc4e4280803d1093468d06828daa54f9c700` |
| Initial P07 product | `912420f91729f1618b8f22804ea7ccd95bd7f6e8` |
| Initial builder report snapshot | `01c189e9d18373df59a5c2a4731f24a91c304b86` |
| Preserved independent component review | `9edf8c1e44c33a0530772eefd2d6537182d7fdda` |
| Repaired product under review | `d02bb248b61dbbc703eb5252f5b46d86bdfc102b` |
| Frozen report-only snapshot used for this pass | `5c1d98e7595c6bfb6aa912f61fa3fc38b7ccefb6` |
| New reviewer branch | `jokerman-microsoft-universal-profile-recheck` |

The new clean worktree was created inside the original reviewer's workspace at
`.claude/runtime/review-worktrees/p07-recheck-d02bb24`, pinned to `5c1d98e`.
The original branch `jokerman-microsoft-universal-profile-review` still points to
`9edf8c1`; its report was not edited or reset. Neither builder nor MasterSession
worktree/branch was changed.

The repair product commit changes exactly four product files:
`lib/pack-resolver.sh`, `lib/profile_context.py`,
`docs/concepts/pack-resolver.md`, and
`tests/integration/universal-profile-context.py`. The following `5c1d98e`
changes only the builder report. The initial 19-file component and narrow
Brief Forge dependency remain in the ancestry. The repaired four-file diff,
new tests, documentation, runtime call paths and builder claims were read directly.
The repository/adapter, ADR-0028/0029, specification and package authority loaded
for the first pass are unchanged between these snapshots.

This is the same independent reviewer, not the implementer. Only this recheck report
is authored and committed. No product repairs, nested agents, shared plan/state edits,
other-source modifications, network/GitHub/account operations, installations or
activation occurred. All test profiles, homes and Git fixtures were synthetic.
No personal/global configuration or actual private profile was inspected.

## Original finding closures

| Finding | Recheck | Evidence and limits |
|---|---|---|
| F01, P1: reference-only resume loses subsequent required-policy selection | CLOSED for direct verify/bind/rebind | The exact original executable F01 block now exits 0: the next policy is required/loaded/applicable with `invocation:LINTEL_PROFILE_PACK`, and the field is `hard`. Both absent/changed ambient-ID variants and inherited Bash consumers execute in the 29-case suite. Independent probes also verify exports after bind/rebind, re-source retention, explicit context conflicts, malformed/stale transports and genuine neutral behavior. |
| F02, P2: concurrent rebind publishes stale selected generation | CLOSED | The exact old reproduction was attempted first, but its deleted `if config.selected.is_file():` trace point cannot be reached; that harness failure is not passing concurrency evidence or a new product defect. A replacement scheduling-only trace at the actual current-written/selected-unpublished boundary confirms both locks are held and the second real process waits. Both then succeed with selected/current generation 3, history 1/2 retained and successful bootstrap. Restoring a real historic selection followed by explicit rebind recovers selected/current generation 4. |

The repair uses a canonical exported `LINTEL_PROFILE_REFERENCE` and the shared
`expected_reference` validator. Subsequent transported-reference reads verify
context/generation/digest, rather than treating a new ambient host ID as authority.
Failed verification preserves the previous selection; a missing transported pin
returns required/error/unknown without creating a replacement. The new conflict
and corruption probes passed.

The selection -> context lock order now matches bootstrap
(`lib/profile_context.py:834-864`). The independent trace did not replace locks,
writers, parser results or policy data. It paused process A after the current
record write, observed process B actually waiting on the selection lock, then
released A. The committed tests additionally exercise preservation of a different
context's selection and rejection of an unbacked fabricated historical reference.
These checks are not a claim of arbitrary power-loss durability or automatic stale-lock
recovery.

## New Stage 1 finding

| ID | Severity | Location | Requirement | Confidence |
|---|---|---|---|---|
| F03 | P1 - blocks component acceptance | `lib/copilot-env.sh:32-34`; consuming path `lib/profile_context.py:772-789,953-967` | A07.3/A07.4: ordinary bootstrap remains ID-only, permits lost-pin recreation and silent generation changes | Reproduced, 10/10 |

### Bootstrap never retains the verified reference

The repair covers direct `verify_profile_context`, `bind_profile_context` and
`rebind_profile_context`, but the documented `lintel_copilot_env` producer still
exports only `LINTEL_PROFILE_CONTEXT`. It does not export the verified reference.
`_profile_cli bootstrap` returns only the context ID. Later ordinary accessors
therefore reach `load_profile_context(config, create=True)` without
`expected_reference`.

This is a previously missed defect in the owned P07 bootstrap, not a claim that
the four-file repair introduced it or a request to implement the open P06/P08 joins.

**Discriminating required-policy reproduction:** a synthetic `strict` pack exists,
there is no repository requirement or optional pointer, and the caller makes an
ordinary invocation-scoped explicit selection:

```bash
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
LINTEL_PROFILE_PACK=strict lintel_copilot_env "$LINTEL_REPO_ROOT" || exit $?
profile_required_policy || exit $?
pin=$(_profile_cli context-path) || exit $?
rm -- "$pin"  # synthetic fixture only: simulate loss of the current runtime pin
profile_required_policy
resolve_pack_field compliance.mode
```

Before pin loss the policy is required/loaded/applicable, source
`invocation:LINTEL_PROFILE_PACK`, version `1.2.3`. After removing **only** the
synthetic current record, the next accessor creates a replacement record and returns:

```json
{"applicability":"not_applicable","required":false,"source":"bundled-neutral","status":"not_required","version":"1.0.0"}
```

The next field is `advisory`; both operations exit 0. The saved selected reference
is still present. No pointer or policy declaration was edited, no environment
variable was explicitly cleared after bootstrap, and no rebind was requested.
The scoped assignment is a valid explicit function invocation, not a mocked host.
With a persistent repository-required declaration, the same missing-pin probe
still recreates the record and exits 0, although it retains required status.

**Generation variant:** after ordinary bootstrap, a real child Bash process
performs an approved rebind to generation 2. The already-bootstrapped parent then
returns generation 2 successfully without explicitly verifying the new reference.
An already-running parent carrying the repaired exported reference correctly
rejects this change; the ID-only bootstrap parent does not.

The passing `test_documented_bootstrap_without_injected_host_id_pins_two_fresh_shells`
compares separate bootstrap outputs and checks manifest drift while the pin exists.
The new missing-pin test first calls `verify_profile_context`, which already
installs the new reference. Neither exercises the missing transport on bootstrap
itself.

**Required builder action:** make successful bootstrap carry the same exact verified
reference as the repaired direct lifecycle APIs, into later accessors and inherited
processes. A known missing pin must not be recreated as first use; a subsequent
generation must require explicit re-verification. Preserve genuinely unbound neutral
first use, explicit-root behavior, source/target boundaries and failed-binding
preservation. Add actual bootstrap -> consumer -> lost-pin and bootstrap -> child
rebind -> old-parent regressions, not only reference-return assertions.

F03 was sent to MasterSession for the original builder. This reviewer made no repair
and did not begin quality review.

## Per-leaf preservation and verdict

| Leaf | Owned verdict | Rechecked behavior and boundary |
|---|---|---|
| A07.1 | PASS | Required declaration/invocation failure, optional diagnostic fallback and genuine neutral first use remain distinct under ADR-0029. Invalid neutral baseline rejects. |
| A07.2 | PASS | Structured inheritance, typed quoting/null/false/lists, whole-block replacement, exact field origins, ancestry and approved source/store/target precedence remain covered by the rerun lifecycle and preserved scripts. |
| A07.3 | FAIL | Direct reference-only resume and inherited consumers now retain identity; original concurrent publication defect is repaired. Ordinary bootstrap still lacks generation-bound continuation (F03). |
| A07.4 | FAIL | Required missing/malformed/incompatible inputs, pointer/parent/manifest drift and transported-reference loss reject. F03 still lets bootstrap consumers recreate a missing pin and, for scoped required selection, return neutral success. |
| A07.5 | PASS for owned inputs | Synthetic rapid/strict routing, gate/evaluator inputs and design-token references remain different and attributable. Actual company control, renderer and joined work lifecycle are not inferred. |
| A20.3 | PASS for owned compatibility | Schema, pack release, installed public product and feature compatibility remain separate; legacy marker/migration and unknown product metadata behavior are preserved. |
| A20.4 | PASS for synthetic-pack checks | Compatible fixtures accept and per-axis/ancestor incompatibilities reject. P13 external-contribution provenance is not accepted here. |

Repository-required bridge `source` remains the **requirement declaration path**,
not a claim to be the manifest path. The actual manifest path/version/raw-byte
hash belongs to ancestry and per-field provenance. No hook/policy enforcement or
independent-actor identity is proven by these hashes.

### Actual isolated-worktree behavior

A new reviewer probe created a temporary Git repository and actual second
`git worktree add --detach` checkout. A separate Bash process ran there with only
the reference handoff, changed synthetic ambient host ID, and the original approved
policy source/target/home roots. After direct verification, both the policy read
and reference read retained the exact required strict profile and `hard` field.
This now tests the repaired reference-only consumption, not only explicit context IDs.

Changing `LINTEL_REPO_ROOT` to the second checkout still returns
`PROFILE_CONTEXT_MISSING`; explicitly supplying the original context file returns
`PROFILE_DRIFT`. These are the declared different-target transfer boundary, not
another defect or evidence of automatic propagation. This was a real Git worktree
and subprocess fixture, not a delegated live-model session or the future P06/P08 flow.

## Checks actually run

Execution was against immutable product `d02bb24` at snapshot `5c1d98e`, using
Windows Git Bash and **Python 3.11.9**. No full repository suite or external service ran.

| Command / scenario | Actual result |
|---|---|
| Exact Python F01 block extracted from preserved `P07-component.md` and executed in the new worktree | PASS, exit 0; required strict policy persists after verification |
| Exact original F02 block | Harness cannot reach its removed trace point; no acceptance credited |
| Independent `TransactionRecheck.test_writer_cannot_pass_current_selected_publication_boundary`, `python -` | PASS, 2.032 seconds; actual lock wait, selected/current agreement, history and explicit stale recovery |
| `bash tests/integration/universal-profile-context.sh` | **29/29 PASS**, zero skips, 205.372 seconds |
| Nine preserved scripts below | **9/9 PASS**, zero skips; real jq assertions executed |
| Two `ReferenceEdges` methods, `python -` | **2/2 PASS**, 24.784 seconds; exact bind/rebind exports, re-source/inherited consumption, explicit conflicts, five malformed/stale transports, neutral preservation |
| `BootstrapPin.test_bootstrap_does_not_recreate_missing_pin`, `python -` | **FAIL**, 7.084 seconds; persistent repo-required record is recreated after deletion, exit 0 |
| Two `BootstrapPropagation` methods, `python -` | **2/2 FAIL**, 11.865 seconds; scoped required selection becomes neutral after pin loss; old parent silently adopts child generation 2 |
| `WorktreeReferenceRecheck.test_reference_only_receiver_in_distinct_worktree_uses_approved_policy_target`, `python -` | PASS, 12.638 seconds; real second checkout and reference-only receiver, with both rejected target-transfer variants |
| `ast.parse(..., feature_version=(3, 9))` on implementation and new lifecycle test | PASS for grammar only; not actual Python 3.9 execution |
| `json.loads` on `lib/profile-context-schema.json` | PASS for JSON syntax, not full JSON Schema certification |
| `bash --noprofile --norc -n` separately for all nine owned changed shell files | PASS |
| `git diff --check b4e93162 d02bb24` and clean status before report creation | PASS; product unchanged |

The preservation chain was:

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

MasterSession's same exact task-local jq executable was independently rehashed:
`a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`.
It reported `jq-1.8.2`; its directory was prefixed on that process's PATH only.
No global installation/configuration change occurred. Synthetic Git fixture commands
used empty fixture configuration and a non-existent fixture hooks directory.
The temporary probes cleaned up their data; they did not write product tests.

## Executable F03 reproduction

From this reviewed repository root, set `PYTHONDONTWRITEBYTECODE=1` and pipe this
Python block to `python -` using a PowerShell single-quoted here-string. It uses the
committed fixture and synthetic temporary roots. On `d02bb24` it deliberately exits
nonzero at the missing-pin assertion, after printing the lost required policy.
This exact block was extracted from the report and rerun: exit 1 with
`bootstrap lost required policy`, neutral/advisory output and `pin-recreated=yes`.

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
    env = dict(case.env)
    env.pop("LINTEL_PROFILE_CONTEXT")
    result = case.shell(
        'source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"\n'
        'LINTEL_PROFILE_PACK=strict lintel_copilot_env "$LINTEL_REPO_ROOT" || exit $?\n'
        'profile_required_policy || exit $?\n'
        'pin=$(_profile_cli context-path) || exit $?\n'
        'rm -- "$pin" || exit $?\n'
        'profile_required_policy || exit $?\n'
        'resolve_pack_field compliance.mode || exit $?\n'
        'printf "\\n"\n'
        'if [ -e "$pin" ]; then printf "pin-recreated=yes\\n"; '
        'else printf "pin-recreated=no\\n"; fi',
        env=env,
    )
    print(result.stdout)
    lines = result.stdout.splitlines()
    assert json.loads(lines[0])["required"]
    assert json.loads(lines[1])["required"], "bootstrap lost required policy"
    assert lines[2] == "hard"
    assert lines[3] == "pin-recreated=no"
finally:
    case.doCleanups()
```

## Remaining acceptance gates

1. Original builder repairs F03; repeat immutable Stage 1 review, then perform the
   still-unrun full bounded P07 Stage 2 quality pass. Closing F01/F02 alone does not
   accept the component.
2. The actual P05 `evaluate_controls(..., required_policy=...)` bridge and actual
   P06/P08 operation/work/capture/resume join remain separate gates. Another session's
   bridge probe is not this reviewer's approval. No stub or schema-only proxy was
   substituted here.
3. Python 3.9 remains the floor; only 3.11.9 ran here. Runtime 3.9, other platforms,
   installed packaging/product metadata, final integrated strict suite, generated
   outputs and actual host/model/company-control acceptance need their own evidence.
4. No private policy activation, hook registration, enforcement certification,
   tamper-proof storage, automatic different-target transfer or ROI is claimed.

**Cycle position:** REVIEW (component specification BLOCKED) -> BUILD (original
P07 builder, F03) -> immutable specification re-review -> quality only after PASS.
Final joined REVIEW remains separate and open.
