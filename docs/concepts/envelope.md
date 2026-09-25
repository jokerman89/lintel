# Envelope — the universal hand-off shape

**Last updated:** 2026-09-20
**Status:** Explicit opt-in contract; shared producer, validator and evaluator implementation

> An explicitly invoked Brief Forge boundary carries an envelope: who sent it, who it is for, what
> it contains, which checks ran and which audit receipt identifies it. Automatic construction stays
> dormant under ADR-0008. The caller, not this format or its helper, owns actual dispatch.

## The problem

Pre-v4.0, every hand-off was ad-hoc:
- Subagent spawn: parent skill writes a free-form prompt
- Phase transition: phase appends to `00-state.md` and the next phase reads it
- Cold-executor: plan + spec + prompt files in `.claude/runtime/state/` named by convention

Three failure modes:

1. **Drift across hand-off kinds.** A subagent brief and a phase brief look nothing alike. Operators learning Lintel encounter five shapes for five kinds. Tooling can't audit them uniformly.
2. **No replay.** When a hand-off goes wrong, there's no canonical envelope to inspect. The brief lives in whatever file the original skill wrote — gone after cleanup, partial after compaction.
3. **No completeness signal.** A hand-off either works or breaks; there's no shared score for "is this brief complete enough that the receiver can act?" Brief Forge (Phase 3) needs this score.

The envelope supplies one shared shape for boundaries that explicitly invoke it, without inventing
host callbacks or weakening the original task authority.

## The model

```
ENVELOPE
├── HEAD              ← metadata (6 required fields)
│   ├── envelope_id
│   ├── envelope_schema_version
│   ├── kind                  ← subagent_spawn | phase_transition | workflow_handoff | cold_executor | operator_input | reply | audit
│   ├── from
│   ├── to
│   └── issued_at
│
├── BODY              ← payload, free-form by content_type
│   ├── content_type          ← brief | spec | plan | payload_freeform
│   ├── content               ← (shape varies by content_type)
│   ├── context_pointers      ← (optional)
│   └── guardrails            ← (optional, evaluator names that ran)
│
└── TAIL              ← closing context (4 required fields)
    ├── completeness_score    ← 0-100, written by Brief Forge
    ├── evaluators_run
    ├── escape_hatches        ← how the receiver can request more context
    └── audit_pointer         ← jsonl file where this envelope is logged
```

Three sections, all required. HEAD answers "what kind of hand-off is this and who's it between." BODY carries the payload (shape varies per kind). TAIL closes the loop with score + audit trail.

The canonical schema remains `lib/envelope-schema.yaml`, serialized as JSON (a YAML subset) so the
default producer and consumers need only Python 3.9+. `lib/envelope_contract.py` is the shared
implementation. Optional legacy YAML input requires `PyYAML>=6.0.3,<7.0` from
`lib/envelope-requirements.txt`; it is lazily imported, never installed automatically.
Missing parser support fails before output/audit. JSON and Markdown need no third-party package.

## Content-type discrimination

`body.content_type` is the discriminator that tells the receiver what shape `body.content` will be:

| content_type | Typical payload | Required content fields |
|---|---|---|
| `brief` | Structured brief from Brief Forge | `task`, `constraints`, `acceptance` |
| `spec` | Design contract for a build | `intent`, `inputs`, `outputs` |
| `plan` | Task breakdown | `tasks` |
| `payload_freeform` | Catch-all for non-structured payloads | (none) |

This is how the envelope absorbs different kinds of hand-off without forking the shape. Brief Forge writes `brief`. PLAN phase writes `plan`. DEFINE writes `spec`. A subagent reply writes `payload_freeform`.

These are explicit caller choices, not automatic phase emissions. A rich Markdown brief is adapted
to `task`, nonempty `constraints` and `acceptance`, with the whole source preserved as
`original_markdown`. Swarm adds work-map/package/leaf/scope references and an acceptance digest.
Duplicate keys, malformed/nested lookalike fields, wrong types, non-finite values and YAML aliases
are rejected. Diagnostics do not echo a rejected payload.

## Replay semantics

Every envelope can be replayed via `bin/li-envelope-replay <envelope-file>`:

- **Default: dry-run.** The tool surfaces what the hand-off would do without actually re-invoking the receiver. The operator sees the envelope content + the current state of the world.
- **Explicit: `--apply`.** Records replay intent for the operator's session; the tool does not invoke
  a receiver. Requires `envelope.tail.replay_safe: true` OR `--force`, with a verified audit receipt.
- **Refused if past `deprecated_after`.** Envelopes may declare a TTL after which replay is rejected (relevant for envelopes carrying time-bound context).

Why dry-run by default: envelopes capture state at the moment of hand-off. The world may have moved on — files renamed, packs switched, dependencies updated. Replaying blind risks acting on stale assumptions. Dry-run lets the operator diff against now and decide.

## Completeness score

`tail.completeness_score` is an integer 0-100 written by Brief Forge (or by the issuing skill when Brief Forge isn't in the path). It answers: "given the receiver's known requirements, is this envelope complete enough that the receiver can act without escalation?"

Scoring rubric (Phase 3 Brief Forge will own this):
- 100 — every required field for the receiver is present, with prior context, evaluators clean
- 80-99 — required fields present, some optional context missing
- 60-79 — required fields present but one or more evaluators raised concerns
- 40-59 — minimal; receiver should expect to request more context
- < 40 — should escalate to operator before acting

No missing score defaults to success. Candidate envelopes start unevaluated. Every configured
evaluator must finish with a valid result within budget before release; mandatory failure blocks
even when other scores are high. The complete Brief Forge release gate validates forbidden content,
checks the minimum score and confirms its audit receipt before writing a receiver payload.

## Escape hatches

`tail.escape_hatches` is a list of strings the receiver can use to request more context without giving up:

```yaml
escape_hatches:
  - "Re-invoke source skill /li:plan with --more-detail flag"
  - "Read .claude/runtime/state/PLAN-2026-05-29.md for full plan"
  - "Ask operator: 'plan completeness scored 65 — re-run with elaboration?'"
```

The receiver acts on the envelope and uses an escape hatch when it hits ambiguity. Without escape hatches, the receiver either fakes context or stalls — both bad. With them, ambiguity has a documented resolution path.

## Audit pointer

`tail.audit_pointer` identifies the minimal identity/digest/outcome receipt, not a stored payload.
Brief Forge writes through the existing unified audit helper and verifies that the matching record
persisted before output. An audit failure cannot be converted into a successful handoff.

The route is explicit `LINTEL_AUDIT_DIR`, then the migrated working repository's
`.claude/runtime/audit/brief-forge.jsonl`, then the operator-global fallback. Raw content, evaluator
notes and reversible base64 are never copied to this audit. Preserve an authorized envelope artifact
separately for replay. `--from-audit` can read legacy full-envelope records, but metadata-only records
fail with an explicit request for the original artifact rather than fabricating one.

## Schema versioning

`head.envelope_schema_version` is the version the envelope conforms to. Phase 2 ships v1. The validator accepts v1; future versions:

- **v1 (Phase 2):** the schema described here
- **v2 (future):** additive fields may be added without breaking v1 consumers (minor bump). Breaking changes ship as v2 with both validators supported until migration index marks v1 grace ended.

Per design doc §1.3 C1-D2: warn-only enforcement in v4.0, block-on-incompat from v4.1.

## When NOT to use envelopes

- **Operator-facing UI output.** Stdout, terminal output, log lines aren't envelopes. Envelopes are skill-to-skill / skill-to-agent / phase-to-phase contracts.
- **Internal file I/O within a single skill.** A skill reading its own state doesn't need envelope shape.
- **Audit-only events with no consumer.** If a skill writes `kind: audit` (the audit envelope kind) just for observability, the envelope still exists but doesn't expect re-execution. Replay-safe defaults to false.

## Anti-patterns

- **Inventing a new hand-off shape for a new kind of work** — extend `content_type` instead. Brief, spec, plan, payload_freeform cover most cases; if not, propose a new `content_type` via a structure-changes entry.
- **Bypassing the audit_pointer** — a release needs its persisted metadata receipt; an artifact alone
  is not proof of a successful audited handoff.
- **Lying about completeness_score** — receivers act on this score. Inflating it to skip Brief Forge gates undermines the contract.
- **Replaying with `--force` without an operator note** — forced replays are audited, but the audit entry is more useful when it carries the operator's reasoning.

## Integration points

**Reads:**
- `lib/envelope-schema.yaml` — the contract

**Writes:**
- scope-routed `brief-forge.jsonl` metadata through the unified audit writer

**Tools:**
- `bin/li-envelope-validate <file>` — validates against schema, returns PASS/FAIL + errors
- `bin/li-envelope-replay <file>` — dry-run by default, `--apply` to record caller-owned replay intent
- `bin/li-forge-stats` (planned — not yet shipped) — will aggregate completeness scores across envelopes

**Consumed by:**
- Brief Forge — issues briefs as envelopes with completeness scoring
- explicit workflow callers, including Swarm's structured brief export

Host enforcement, a real independent reviewer and final shared work/profile/domain binding need
their own evidence. A valid envelope or different actor name never supplies those guarantees.
