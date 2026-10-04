---
name: li-mars
description: Use when a problem, plan, spec, implementation or review needs a deliberate multi-model adversarial review with bounded rounds and preserved dissent.
---

> **Lintel on GitHub Copilot.** Generated from `skills/mars/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/mars/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/mars/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# MARS — Multi-Model Adversarial Review & Screening

A deliberate, targeted check: several **different** models read the same frozen brief
independently, then (only if they disagree) challenge each other once. The coordinator
adjudicates against evidence and reports agreement, dissent and gaps. MARS is advice.
It is **not** Swarm, not implementation fan-out, not a scheduler and not a release gate.

## When to use

- Operator asks for MARS, a multi-model review, a second/outside opinion or a model panel.
- A full `/li-cycle` reaches PLAN's approval gate and the offer gate
  says `offer: true`.
- A standalone review workflow (`review`, `code-review`) offers it once for a concrete
  target on a capable host.
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
| Transport | `subagent` (nothing to close); `nested-session` when the operator wants visible sessions | similar input cost per call in a large repository (RM9); nested sessions are closed after collection |
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

Render the subject once with the shared [Review Method](../../../skills/review/references/method.md)
(see [protocol.md](../../../skills/mars/references/protocol.md) "Round 1") into `inputs/brief.md` and
`inputs/method.json`. For repository content, bind the exact selection with `--select`
(repeatable; `--base` defaults to `HEAD`): `panel init` snapshots it through the shared
content-bound review contract into `inputs/snapshot.json` and records the selected profile
reference when one exists. Records that would sit inside the selection (for example a
repository-root selection with records under `.claude/runtime/`) are refused with
`output_overlaps_selection` before anything is written; store them outside the selection.
The selection is never narrowed or excluded for you.

```bash
python3 "$src/bin/li-mars.py" panel init --panel "$run/records/panel.json" --id "$panel_id" \
  --owner "$HOST_SESSION_ID" --brief "$run/inputs/brief.md" --kind implementation \
  --method-meta "$run/inputs/method.json" --select <path> [--select <path>] \
  --subject-ref "<path, PR or excerpt label>" --consent "<operator turn reference>" \
  --requested-by "operator via $HOST_SESSION_ID" --trigger explicit --caller standalone \
  --surface "<observed-host-surface>"  # repository/branch/commit default to read-only git facts
```

The panel's `origin` (who requested it, trigger, caller, coordinator, surface, repository,
branch, commit, optional cycle/work map) feeds every header. `brief` refuses to render
without it, refuses a round-1 body that differs from the frozen brief, and refuses to
dispatch after the bound input changed (`panel verify-input` reports the changed paths).

### 4. Dispatch the blind pass

Register each slot, render its request and dispatch that exact text — same brief for
every slot, no peer output, read-only tools, no recursion:

```bash
python3 "$src/bin/li-mars.py" panel add --panel "$panel" --slot r1 --model "$resolved_model" \
  --transport "$selected_transport" --session <child-id> \
  --effort "$effective_effort" --context "$effective_context"
python3 "$src/bin/li-mars.py" panel brief --panel "$panel" --slot r1 --round 1 \
  --body "$run/inputs/brief.md" --out "$run/records/r1-round1.request.md"
```

For nested sessions, create the child with the rendered request as its kickoff and add it
**immediately** with the returned session ID, so closing can never target the wrong
session. The request opens with a ` ```mars-request ` header naming the requester,
coordinator session, repository/commit, subject, brief hash, model, effort and context.

Bind model/effort/context from the consented `roster` result and the selected
transport from actual host capability. Use the
[host dispatch guidance](../../../skills/mars/references/integration.md#host-dispatch-and-identity)
only after inspecting the current tool schema and permission. A documented
parameter is not proof the current host accepts it.

### 5. Collect and verify identity

The reviewer's **final response** is the report and must open with a ` ```mars-report `
header (verdict, P1/P2/P3 counts, confidence, `read_only: attested`, coverage, echoed
panel/slot/round/brief hash). Save it to `records/<slot>-round<n>.md` and run `panel record`;
a missing or mismatched header is refused, not repaired. Record host-observed identity
with `panel observe --evidence host-usage` when the host shows which model actually ran
(see the integration reference for host-specific observation paths).
A model's self-description is `self-report`, not
proof. A substituted model does not count toward the approved roster. An empty final
response gets one resend request; then the slot is `failed`.

### 6. Challenge once, only if contested

Build a claim matrix (claim IDs, which slots raised it, severity spread, disputed facts).
If every claim has agreement, skip round 2 and say why. Otherwise render each slot's
round-2 request with `panel brief --round 2 --body <matrix+challenge body>` (a
`round_type: challenge` header) and send it to the same child. Reviewers defend, revise or
refute with evidence and summarize stances in the report header's `positions` field.

### 7. Synthesize

Open the synthesis with `panel synthesis-header --adjudicated <p1,p2,p3[,deviations]>` (a
` ```mars-synthesis ` block: status, requester, coordinator, repository/commit, subject,
requested vs verified models, downgrades, failed slots, calls, input verification, profile,
coverage, the shared-rule `outcome`, `release_clearance: false`). Then adjudicate against the
source, not the head count: agreed findings (with the strongest evidence), disputed
findings with each side, rejected claims and why, unique catches (single-reviewer findings
that survive challenge are often the most valuable), gaps nobody covered, and
recommended checks. `panel inspection --synthesis <file> --out <records file>` emits the
content-bound inspection record REVIEW consumes; it refuses a changed input.

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

Render from the **actual** `li-mars.py roster` output: each `roster` entry's `model`,
`effort`, `context_tier` and `downgraded`, plus `missing_families` and `eligible`.
Do not substitute remembered model names, assume four usable slots, or describe
unsupported settings as available. Preserve ADR-0036's requested defaults and
show effective settings/downgrades. Count the selected distinct models; the
proposed call bound is that count × the selected round bound, within existing limits.

> MARS is available: `<observed count>` reviewers — `<observed roster with effective
> effort/context and downgrades>`. Missing families: `<actual result or none>`.
> One blind pass + challenge only if contested (`≤ selected call bound`).
> Run it on `<target>` with this roster and budget? [yes / no]

"No" is remembered for this cycle or invocation. Silence is "no".

## Failure handling

- Fewer than two usable distinct models → blocked; explain. Never role-play extra reviewers.
- A child fails or times out → slot `failed`; the panel is `partial`; no silent replacement.
- Identity unverifiable → keep the findings, mark `multi_model_verified: false`.
- Brief or target changed mid-run → stop; start a new panel with new consent.
- Budget reached → stop dispatching; synthesize what exists.

## Integration

- Offer points: full-cycle `/li-plan` approval option E, standalone `/li-review`
  Step 6b (panel mode) and `/li-code-review`. Current caller mappings and per-host
  mechanics: [integration.md](../../../skills/mars/references/integration.md). CYCLE only carries PLAN's answer.
- One method: [Review Method](../../../skills/review/references/method.md) and
  `lib/review-questions.json`; single reviews and panels send the same packet body.
- Decision: [ADR-0036](../../../.claude/decisions/0036-mars-multi-model-review.md).
  Lessons from Microsoft's MDASH on catching bugs inline: `.claude/plans/mars/mdash-lessons.md`.
- Evidence contract: MARS output is inspection data only. Strict review, QA and SHIP stay
  with `/li-review`, `/li-ship` and the content-bound review evidence. In REVIEW panel mode,
  REVIEW records its own decision from the adjudicated result.

## Voice tier behavior

`voice: internal`. Reports are engineering-internal and cite file:line or section evidence.
