---
name: mars
layer: foundation
description: Use when a problem, plan, spec, implementation or review deserves a deliberate multi-model adversarial second look — runs a small, bounded panel of the latest distinct models (independent first pass, at most one challenge round), preserves dissent and never grants release clearance.
color: red
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
necessity: OPTIONAL
gap_if_skipped: "Single-model blind spots survive review; no independent cross-model challenge of the plan, spec or change."
---

# MARS — Multi-Model Adversarial Review & Screening

A deliberate, targeted check: several **different** models read the same frozen brief
independently, then (only if they disagree) challenge each other once. The coordinator
adjudicates against evidence and reports agreement, dissent and gaps. MARS is advice.
It is **not** Swarm, not implementation fan-out, not a scheduler and not a release gate.

## When to use

- Operator asks for MARS, a multi-model review, a second/outside opinion or a model panel.
- A full `/li:cycle` reaches its PLAN approval gate and the offer gate says `offer: true`.
- A standalone review workflow (`review`, `code-review`, `plan-eng-review`, `define`)
  offers it once for a concrete target on a capable host.
- High-stakes or easily-fooled subjects: auth, data loss, concurrency, migration plans,
  security boundaries, specs with irreversible decisions.

## When NOT to use

- Trivial diffs, typo fixes, docs-only changes.
- Hotfix, research-only or partial cycles — no automatic offer (explicit request still OK).
- The host cannot select a different model per child, or cannot show which model ran.
- As a substitute for tests, independent spec/quality review or SHIP gates.
- Inside a MARS participant (no recursion) or after the operator declined this cycle.

## Defaults (`lib/mars-defaults.json`)

| Setting | Default | Notes |
|---|---|---|
| Roster | latest model per family: Claude (Opus first), GPT, Grok, MAI | Gemini optional; `--families` adds more; min 2, default 4, max 8 |
| Reasoning effort | `xhigh` (extra high) | clamped to the model's highest supported at or below; recorded |
| Context | `long_context` (1M) | falls back to default where unsupported; recorded |
| Rounds | blind pass + one challenge **only when contested** | max 2 rounds, max participants × 2 calls |
| Transport | `subagent` (cheapest); `nested-session` when the operator wants visible sessions | nested sessions are closed after collection |
| Offers | once, at the full-cycle PLAN gate or once per standalone review | never re-offered after decline; auto mode is not consent |
| Output | findings, dissent, gaps, identity evidence | `release_clearance: false` always |

"Latest" is resolved from the **host's live model list** every run, never from a fixed
catalog. `bin/li-mars.py roster` applies the family rules to a host snapshot you write
from the actual tool schema.

## Workflow

Helper: `python3 <source>/bin/li-mars.py` (stdlib only; never dispatches models or closes
sessions — you do that with host tools). Panel state lives in the working repository under
`.claude/runtime/mars/<panel>/` (gitignored): `inputs/` is immutable, `records/` is mutable.

### 1. Gate

For an automatic offer, build a request and run `li-mars.py offer --request <file>`.
Exit 3 means do not offer; say nothing unless the operator asked. Required: separate child
contexts, per-child model selection, delegation allowed, observable model identity, two or
more distinct models; for cycles, the actual ordered nine-phase route at the PLAN gate.
An explicit operator request skips placement rules but never capability or consent.

### 2. Propose and get consent

Write the host snapshot (models with supported efforts/context tiers), run `roster`, and
show the operator: target, the resolved models with effective effort/context, participant
count, max rounds/calls. One confirmation covers that exact roster and budget. A changed
roster, target or larger budget needs new consent. An existing explicit request counts.

### 3. Freeze the brief and open the panel

Write the subject brief to `inputs/brief.md`: subject (inline excerpt, diff or artifact paths
at a commit), the questions and the round-1 body from [protocol.md](references/protocol.md).
Keep mutable records **outside** anything the brief selects for content binding; if the
operator's scope includes `.claude/runtime/`, narrow it deliberately or store records
elsewhere — never silently exclude.

```bash
python3 "$src/bin/li-mars.py" panel init --panel "$run/records/panel.json" --id "$panel_id" \
  --owner "$HOST_SESSION_ID" --brief "$run/inputs/brief.md" --kind code-review \
  --subject-ref "<path, PR or excerpt label>" --consent "<operator turn reference>" \
  --requested-by "operator via $HOST_SESSION_ID" --trigger explicit --caller standalone \
  --surface copilot-app            # repository/branch/commit default to read-only git facts
```

The panel's `origin` (who requested it, trigger, caller, coordinator, surface, repository,
branch, commit, optional cycle/work map) feeds every header. `brief` refuses to render
without it.

### 4. Dispatch the blind pass

Register each slot, render its request and dispatch that exact text — same brief for
every slot, no peer output, read-only tools, no recursion:

```bash
python3 "$src/bin/li-mars.py" panel add --panel "$panel" --slot r1 --model claude-opus-5.5 \
  --transport nested-session --session <child-id> --effort xhigh --context long_context
python3 "$src/bin/li-mars.py" panel brief --panel "$panel" --slot r1 --round 1 \
  --body "$run/inputs/brief.md" --out "$run/records/r1-round1.request.md"
```

For nested sessions, create the child with the rendered request as its kickoff and add it
**immediately** with the returned session ID, so closing can never target the wrong
session. The request opens with a ` ```mars-request ` header naming the requester,
coordinator session, repository/commit, subject, brief hash, model, effort and context.

Copilot App: `task` (subagent, `model`, `reasoning_effort`, `context_tier`) or
`create_session` (`kickoff.model`, `kickoff.reasoning_effort`, `kickoff.context_tier`,
`kickoff.mode: autopilot`, `coordinate_with_creator: false`, `notify_on_idle`).
Other hosts: their native per-child model API.

### 5. Collect and verify identity

The reviewer's **final response** is the report and must open with a ` ```mars-report `
header (verdict, P1/P2/P3 counts, confidence, `read_only: attested`, coverage, echoed
panel/slot/round/brief hash). Save it to `records/<slot>-round<n>.md` and run `panel record`;
a missing or mismatched header is refused, not repaired. Record host-observed identity
with `panel observe --evidence host-usage` when the host shows which model actually ran
(Copilot App: the local session store's `assistant_usage_events.model` and
`reasoning_effort` per child session). A model's self-description is `self-report`, not
proof. A substituted model does not count toward the approved roster. An empty final
response gets one resend request; then the slot is `failed`.

### 6. Challenge once, only if contested

Build a claim matrix (claim IDs, which slots raised it, severity spread, disputed facts).
If every claim has agreement, skip round 2 and say why. Otherwise render each slot's
round-2 request with `panel brief --round 2 --body <matrix+challenge body>` (a
`round_type: challenge` header) and send it to the same child. Reviewers defend, revise or
refute with evidence and summarize stances in the report header's `positions` field.

### 7. Synthesize

Open the synthesis with `panel synthesis-header` (a ` ```mars-synthesis ` block: status,
requester, coordinator, repository/commit, subject, requested vs verified models,
downgrades, failed slots, calls, `release_clearance: false`). Then adjudicate against the
source, not the head count: agreed findings (with the strongest evidence), disputed
findings with each side, rejected claims and why, unique catches (single-reviewer findings
that survive challenge are often the most valuable), gaps nobody covered, and
recommended checks.

### 8. Close only what you spawned

```bash
python3 "$src/bin/li-mars.py" panel close-plan --panel "$panel" --owner "$HOST_SESSION_ID"
```

The plan lists only nested sessions registered in **this** panel, spawned by **this** owner,
whose reports are collected. Before archiving each, confirm with the host that it is idle
and has no file changes, commits or open PR; then archive it and run `panel mark-closed`.
Never archive by name pattern, never close sessions absent from the panel, never close
the owner. Subagents need no close. Abort path: `--include-incomplete`, after reporting.

## Offer text (cycle PLAN gate or standalone review)

> MARS is available: 4 reviewers (Claude Opus 5.5, GPT-6 Astra, Grok 4.7, MAI — resolved
> now), extra-high effort, 1M context where supported, 1 blind pass + challenge only if
> contested (≤ 8 calls). Run it on `<target>`? [yes / no]

"No" is remembered for this cycle or invocation. Silence is "no".

## Failure handling

- Fewer than two usable distinct models → blocked; explain. Never role-play extra reviewers.
- A child fails or times out → slot `failed`; the panel is `partial`; no silent replacement.
- Identity unverifiable → keep the findings, mark `multi_model_verified: false`.
- Brief or target changed mid-run → stop; start a new panel with new consent.
- Budget reached → stop dispatching; synthesize what exists.

## Integration

- Offer hook points for cycle/plan/review/define/plan-eng-review/code-review:
  [integration.md](references/integration.md).
- Lessons from Microsoft's MDASH on catching bugs inline:
  `.claude/plans/mars/mdash-lessons.md`.
- Evidence contract: MARS output is inspection data only. Strict review, QA and SHIP stay
  with `/li:review`, `/li:ship` and the content-bound review evidence.

## Voice tier behavior

`voice: internal`. Reports are engineering-internal and cite file:line or section evidence.
