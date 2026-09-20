# Brief Forge — explicit hand-off gate

**Last updated:** 2026-09-20
**Status:** Shipped helper and skill contract; activation is explicit

Brief Forge gives a workflow boundary a consistent envelope, evaluator result and audit trail. It is
not a universal host interceptor: a source workflow must invoke `/li:brief-forge` or execute the
documented helper sequence. Lintel does not register pre-spawn or pre-phase Brief Forge hooks.

This distinction matters. Pack policy configures what an invocation does; the presence of policy in
`pack.yaml` does not prove that a hand-off was forged.

## Why it exists

Agent hand-offs tend to lose three things as work scales:

1. a stable statement of the boundary and receiver;
2. a mechanical signal that required context is present and safe;
3. replayable evidence of what the receiver actually received.

Brief Forge addresses those gaps with the shared envelope schema, three built-in evaluators and a
scope-routed audit record. Workflows that do not invoke it must describe that degradation honestly.

## Activation reality

Brief Forge runs in two supported ways:

- a workflow explicitly invokes `/li:brief-forge <kind> <from> <to> <content_type> <content_file>`;
- a workflow calls `forge_handoff` from the trusted `lib/brief-forge.sh` bundle.

The Swarm profile requires an explicit Brief Forge boundary before a lane is dispatched. If a host
cannot invoke the skill, the coordinator records that limitation. A missing mandatory evaluator or
failed gate blocks the affected handoff; it is not converted into unaudited success.

There is no registered `brief-forge-pre-spawn` or `brief-forge-pre-phase` hook in the shipped hook
bundle. A future host callback remains inactive until its registration and firing are verified on
that host.

## Execution model

```text
source workflow explicitly invokes Brief Forge
    |
    v
read effective policy through the public profile accessor
    |
    v
read the selected nested hand-off policy
    |
    +-- disabled or eligible bypass --> audit bypass and stop
    |
    v
validate every configured evaluator name is loaded
    |
    +-- unknown evaluator --> audit block and stop
    |
    v
parse and validate content --> reject forbidden payloads --> run every evaluator
    |
    v
check budget/failures/minimum score --> finalize and validate TAIL
    |
    v
write metadata via unified audit_log --> verify persisted receipt --> emit envelope
    |
    v
caller performs any actual authorized dispatch
```

`lib/pack-resolver.sh` owns profile selection, inheritance and cache representation. Brief Forge
uses `resolve_pack_field_json` (or the retained public `resolve_pack_field` accessor on older bundles) for
`brief_forge_handoffs.<event>.{enabled,evaluators}` and
`brief_forge_handoffs.cold_path_bypass.eligible_skills`. Boolean/list responses are checked.
It never reads the private cache file or supplies its own fallback policy. The selected resolver's
documented fallback/required-profile behavior remains authoritative.

An unreadable event, missing `enabled` value or unknown evaluator fails closed before envelope
construction. Configuration is data: evaluator names are never evaluated as shell commands.

## Envelope

The envelope follows `lib/envelope-schema.yaml`:

- **HEAD** identifies the event, source, receiver, issue time, active pack, operator and cycle.
- **BODY** carries the typed content supplied by the caller.
- **TAIL** carries the minimum evaluator score, evaluators run, escape hatches and audit pointer.

The same envelope can therefore be inspected by the receiver, the coordinator and later review
without inventing a second task definition.

The producer emits JSON, also a YAML subset. JSON, Markdown adaptation and the canonical schema
(JSON stored at the retained `.yaml` path) need only Python 3.9+ standard-library support.
Legacy YAML input optionally uses `PyYAML>=6.0.3,<7.0` from `lib/envelope-requirements.txt`; import
is lazy and its absence is an explicit failure, not silent base64 wrapping.

Markdown briefs use Task, Ownership/Constraints, Acceptance and optional Inputs headings. The full
original text is retained under `original_markdown`. The Swarm adapter adds authoritative
work-map/package/leaf/scope references and the acceptance digest. No text is executed.
Real structured parsing rejects duplicate keys, YAML aliases, non-finite values, missing/nested
lookalike fields and wrong types before a payload reaches receiver output or audit.

## Event policies

The neutral `_default` pack declares five event policies:

| Event | Boundary | Default policy |
|---|---|---|
| `subagent_spawn` | parent workflow to agent | enabled; security, stale |
| `phase_transition` | one cycle phase to the next | enabled; completeness |
| `workflow_handoff` | one workflow to another | enabled; completeness |
| `cold_executor` | plan/spec/prompt to a cold executor | enabled; security, completeness |
| `operator_input` | operator to workflow | disabled |

These entries configure an invocation only. They do not install a callback or cause a host to
intercept the corresponding event.

`cold_path_bypass.eligible_skills` lets an active pack identify sources that may bypass evaluation.
A disabled event or eligible bypass writes a verified metadata record and returns exit 3 without
an envelope. It does not claim a forged handoff.

## Evaluators

Lintel ships exactly three evaluator functions in `lib/brief-forge-evaluators.sh`:

- `security` looks for secret-like, command-injection and prompt-injection patterns;
- `completeness` checks required fields for the envelope's content type;
- `stale` checks that referenced local context still exists.

Each returns JSON containing a score, budget use and notes. The aggregate score is the minimum, so
one serious result cannot be hidden by several high scores. A hard failure or missing/incomplete
evaluation blocks regardless of score; schema validation and baseline security are always required.
The security patterns are mechanical checks, not a claim of comprehensive tenant-policy enforcement.

A pack may select another evaluator name, but policy does not load executable code. Trusted
active-pack integration must first source a library that defines the corresponding
`evaluator_<name>` function. If that function is not loaded, Brief Forge writes a
`brief_forge_blocked` audit entry and refuses the hand-off before building the envelope.

## Score and budget decisions

The default decision bands are:

| Score | Result |
|---|---|
| 60–100 | proceed |
| 40–59 | proceed with concerns and exposed escape hatches |
| 0–39 | block and escalate |

`brief_forge_handoffs.budget_tokens` caps evaluator work for one invocation. Budget exhaustion,
nonzero evaluator exit and malformed evaluator JSON block before release; missing scores/costs
cannot default to success. The helper emits nothing if release fails.

## Audit and replay

Brief Forge uses the unified audit router from `bin/_audit.sh`:

1. an explicit `LINTEL_AUDIT_DIR`, when set;
2. `.claude/runtime/audit/` in a v5-layout repository;
3. the operator-global Lintel audit directory as the fallback.

`brief-forge.jsonl` retains identity, digest and outcome metadata only. Neither raw payload nor a
reversible base64 copy is written. Rejected payloads and evaluator notes are absent from audit and
diagnostics. The envelope pointer and events use the same scope. Because the shared audit writer
has a fail-open API, this boundary also verifies its exact receipt before releasing the payload.

`bin/li-envelope-replay` validates and inspects an explicitly retained envelope artifact. `--apply`
records intent with a persisted receipt; the operator's session still invokes the receiver.
Legacy full-envelope audit records remain readable, but a new metadata-only record cannot
reconstruct a payload. Preserve an authorized artifact separately and compare its digest.

## Relationship to Swarming work

Brief Forge structures one dispatch boundary; it does not schedule lanes. The Swarm profile owns
dependency readiness, attributable isolation, lane scopes, reports, independent reviews and serial
integration. Brief Forge supplies the boundary envelope and audit evidence used before a worker is
handed a lane.

If the host supports native subagents, several eligible isolated lanes may run concurrently. A
sequenced host replays the same briefs one at a time. A host with no delegation support leaves the
artifacts inspectable for manual execution. In every case, the coordinator remains the single
writer for shared ledgers and reducers.

## Failure and recovery

- **Missing or unreadable policy:** block before construction and repair its source/accessor.
- **Unknown evaluator:** load the trusted pack evaluator or remove the unsupported policy name;
  never silently skip it.
- **Low score or forbidden content:** use the safe diagnostic, correct/redact the original, then retry.
- **Unavailable host integration:** record the degradation in the lane report and preserve the
  unmodified worker brief for replay.
- **Audit write failure or missing receipt:** return failure with no receiver payload.

## Integration points

**Reads:**

- `lib/envelope-schema.yaml`
- the public accessors in `lib/pack-resolver.sh`
- `lib/envelope_contract.py` (shared structured implementation)
- `lib/brief-forge.sh`
- `lib/brief-forge-evaluators.sh`
- trusted pack evaluator code explicitly sourced by the caller
- the caller's content file

**Writes:**

- scope-routed Brief Forge identity/digest/outcome events through the unified writer
- the envelope on stdout

**Verified by:**

- `tests/unit/brief-forge-evaluator-runs.sh`
- `tests/integration/brief-forge-boundary.py` (including missing optional parser and failed audit)
- `tests/shape/brief-forge-handoffs-canonical.sh`
- `tests/shape/every-handoff-uses-envelope.sh`
- the integrated Swarm workflow and full repository suite

## Anti-patterns

- Calling pack policy an automatic hook.
- Treating an unknown evaluator as a no-op.
- Bypassing without an audit record.
- Averaging evaluator scores and masking a serious result.
- Writing an audit pointer to a different scope than the emitted event.
- Forging recursively for Brief Forge's own evaluator work.
- Letting a forged envelope become a second source of task authority.
