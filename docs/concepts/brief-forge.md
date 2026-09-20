# Brief Forge — explicit hand-off gate

**Last updated:** 2026-09-08
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
- a workflow reproduces the sequence in `skills/brief-forge/SKILL.md` and retains equivalent audit
  evidence.

The Swarm profile requires an explicit Brief Forge boundary before a lane is dispatched. If a host
cannot invoke the skill or an evaluator is unavailable, the coordinator records the exact condition
and follows the documented degradation path; it must not label the hand-off forged.

There is no registered `brief-forge-pre-spawn` or `brief-forge-pre-phase` hook in the shipped hook
bundle. A future host callback remains inactive until its registration and firing are verified on
that host.

## Execution model

```text
source workflow explicitly invokes Brief Forge
    |
    v
resolve active pack and immutable merged cache
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
construct HEAD + BODY --> run evaluators --> compose TAIL
    |
    v
write scope-routed audit --> emit envelope --> apply score decision
```

The policy reader is deliberately local to the skill. `lib/pack-resolver.sh` owns top-level and
two-level fields; Brief Forge uses an allowlisted block reader for
`brief_forge_handoffs.<event>.{enabled,evaluators}` and
`brief_forge_handoffs.cold_path_bypass.eligible_skills`. It reads PackResolver's merged session
cache, so inherited pack values and the rest of the session use the same snapshot.

An unreadable event, missing `enabled` value or unknown evaluator fails closed before envelope
construction. Configuration is data: evaluator names are never evaluated as shell commands.

## Envelope

The envelope follows `lib/envelope-schema.yaml`:

- **HEAD** identifies the event, source, receiver, issue time, active pack, operator and cycle.
- **BODY** carries the typed content supplied by the caller.
- **TAIL** carries the minimum evaluator score, evaluators run, escape hatches and audit pointer.

The same envelope can therefore be inspected by the receiver, the coordinator and later review
without inventing a second task definition.

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
A disabled event or eligible bypass writes an audit record rather than disappearing silently.

## Evaluators

Lintel ships exactly three evaluator functions in `lib/brief-forge-evaluators.sh`:

- `security` looks for secret-like, command-injection and prompt-injection patterns;
- `completeness` checks required fields for the envelope's content type;
- `stale` checks that referenced local context still exists.

Each returns JSON containing a score, budget use and notes. The aggregate score is the minimum, so
one serious result cannot be hidden by several high scores.

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

`brief_forge_handoffs.budget_tokens` caps evaluator work for one invocation. Budget exhaustion is
surfaced; a partial evaluation must not be presented as a complete pass.

## Audit and replay

Brief Forge uses the unified audit router from `bin/_audit.sh`:

1. an explicit `LINTEL_AUDIT_DIR`, when set;
2. `.claude/runtime/audit/` in a v5-layout repository;
3. the operator-global Lintel audit directory as the fallback.

Envelopes are stored in a dated JSONL stream. Emitted, bypassed and blocked events use the same
scope decision, so the envelope pointer and statistics do not disagree about location.

`bin/li-envelope-replay` can inspect a recorded envelope and dry-run its replay behavior. Applying
a replay remains an explicit, audited action and does not broaden the receiver's authority.

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

- **Missing or unreadable policy:** block before construction; repair the active pack or choose an
  explicitly documented un-forged path.
- **Unknown evaluator:** load the trusted pack evaluator or remove the unsupported policy name;
  never silently skip it.
- **Low score:** use the emitted notes and escape hatches, correct the content, then forge again.
- **Unavailable host integration:** record the degradation in the lane report and preserve the
  unmodified worker brief for replay.
- **Audit write failure:** do not claim a durable forged hand-off.

## Integration points

**Reads:**

- `lib/envelope-schema.yaml`
- `lib/pack-resolver.sh` and its merged session cache
- `lib/brief-forge.sh`
- `lib/brief-forge-evaluators.sh`
- trusted pack evaluator code explicitly sourced by the caller
- the caller's content file

**Writes:**

- scope-routed `envelopes-<date>.jsonl`
- scope-routed Brief Forge emitted, bypassed or blocked audit events
- the envelope on stdout

**Verified by:**

- `tests/unit/brief-forge-evaluator-runs.sh`
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
