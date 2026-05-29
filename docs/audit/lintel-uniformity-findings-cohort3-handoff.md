# Lintel uniformity audit — Cohort 3: Brief Forge / hand-off / envelope candidates

**Cohort:** 3 of 8
**Status:** complete
**Auditor pass date:** 2026-05-29
**Components audited:** 18
**Budget:** ~25k

## Scope and method

Cohort 3 is the highest-fragmentation cohort by design — every skill currently doing
hand-off-like work *informally*, before Brief Forge / the payload envelope exist to
standardize it. I read every body in full (not frontmatter alone), scored each against
D1-D14, and grounded the D9 "should-fire" findings against
`docs/feature-requests/lintel-feature-brief-forge.md` (the five hand-off moments) and
`tests/shape/brief-forge-handoffs-canonical.sh` (the canonical `brief_forge_handoffs:`
field name, v4.0 §2.5 finding 2-P2.2).

**Components (18):**

- Persistence pair: `context-save`, `context-restore`
- Snapshot pair: `context-snapshot`, `context-dump`
- Warm family (base + 6 variants): `context-warm`, `context-warm-related`, `context-warm-sessions`, `context-warm-adrs`, `context-warm-customer`, `context-warm-from-url`, `context-warmup`
- Budget family: `context-budget`, `context-budgetwatch`, `context-cool`
- Cross-context: `pair-agent` (skill→subagent), `codex` (skill→subprocess)
- Router: `skill-router` (operator→skill)

**Hand-off moments these touch** (per brief-forge feature doc §"What every hand-off means"):
moment 1 (skill→subagent: `pair-agent`, `codex`), moment 4 (workflow→cold executor:
`context-save`/`-restore`/`-snapshot`/`-dump`/`-warm-sessions`), moment 5
(operator→skill: all 18). **None of the 18 fire Brief Forge — it is designed-not-built —
but moments 1 and 4 here are exactly what Brief Forge is designed to gate. Every save and
every restore in this cohort is an un-gated cold-executor hand-off. That is the central
finding of the cohort.**

---

## NO-CUT reminder

Every `proposed` raises a component to the strongest peer's depth. Nothing is cut.
Per-kind FLOOR (not max): the floor for a hand-off skill is set below in the peer table.

---

## Cohort-level structural findings (apply across the cohort)

These four are the dominant fragmentation patterns. They recur in nearly every per-component
record; stated once here, referenced by ID below.

### CF-1 — Storage-root schism (D3, D5, high-severity)

The cohort writes to **four mutually-inconsistent roots** for the same conceptual data
(saved session state + budget log):

| Root | Used by | nano |
|---|---|---|
| `~/.gstack/projects/<slug>/checkpoints/` | context-save, context-restore | context-save:41, context-restore:35 |
| `~/.lintel/sessions/<branch>/` | context-snapshot, context-dump, context-warm-sessions | context-snapshot:36, context-dump:38, context-warm-sessions:40 |
| `.lintel/state/` (in-repo) | context-warm, context-budget, context-cool | context-warm:66, context-budget:33, context-cool:34 |
| `~/.lintel/audit/*.jsonl` | context-warm-customer, context-warm-from-url, context-warmup, pair-agent, codex | context-warm-customer:96, etc. |

**high:** breaks the cross-session-memory promise and the future envelope promise
(`~/.lintel/jobs/<id>/envelopes/`). A save written to `~/.gstack/` is invisible to a
restore family that reads `~/.lintel/sessions/`. context-save and context-restore are a
matched pair that work; context-dump explicitly reads `*-context-save.md` from
`~/.lintel/sessions/` (context-dump:38) but context-save writes to `~/.gstack/` — **the
dump skill cannot find what save wrote.** This is a live breakage, not just a style nit.

**proposed (uplift):** Adopt a single canonical root. The brief-forge envelope already
declares `~/.lintel/jobs/<id>/envelopes/` as the home; converge all persistence there and
keep the in-repo `.lintel/state/` only for the live 00-state/budget ledger. Add a
`scaffolding`-level constant (e.g. `LINTEL_STATE_ROOT`) imported by every skill — shared
schema discipline. **Never delete the gstack path; alias it to the canonical root for
back-compat.**

**operator_decision_required: yes** (which root wins).

### CF-2 — context-save ↔ context-dump contract break (D3, high)

context-dump:38 greps for `*-context-save.md`; context-save never emits that filename
(it writes `<branch>-<ts>[-label].md`, context-save:41) and writes to a different root
(CF-1). **The in/out contract between a producer and its named consumer does not match on
either filename or path.** This is the single most concrete D3 failure in the cohort.

**proposed:** Define the checkpoint envelope shape once (filename pattern + root +
required sections) in a shared spec; both skills import it. Add the integration test the
operator's own schema-discipline rule requires ("at least one integration test per
communication link").

### CF-3 — No `brief_forge_handoffs:` frontmatter anywhere (D8/D9, high)

The canonical field name is `brief_forge_handoffs:` (asserted by
`tests/shape/brief-forge-handoffs-canonical.sh:35`). **Zero of the 18 declare it.** For
hand-off skills this is the field that would make the gate fire when built. The cohort is
where this field is most load-bearing and most absent.

**proposed:** When Brief Forge lands, every component crossing moments 1/4/5 declares
`brief_forge_handoffs:` listing the boundary + evaluators. Until then, add it as a
documented stub so the shape test can forward-positive count them. Mark "n/a unbuilt" on
runtime behavior, but the *declaration gap* is a real finding now.

### CF-4 — Status-protocol / report-format dialect split (D2, medium)

Two dialects coexist:

- **gstack dialect** (context-save, -restore, -budgetwatch, pair-agent, codex,
  skill-router): prose `## Report format` with a `✓` line, no DONE/BLOCKED status token.
- **lintel dialect** (context-snapshot, -dump, -cool, -warm + all warm variants):
  explicit `## Status protocol` with `DONE / BLOCKED / NEEDS_CONTEXT` + `## Hop-in support`
  + `## 00-state.md append`.

**high:** D2 (explicit declared exit) is the floor for any component a resume/replay engine
reads. The gstack-dialect skills have *implicit* tails — a resume engine cannot
machine-detect their completion. The strongest peers (lintel dialect) declare it.

**proposed:** Normalize all 18 to the lintel dialect: `## Status protocol` with
DONE/BLOCKED/NEEDS_CONTEXT + `## Hop-in support` + a 00-state append block. Keep the
human-friendly `✓` report as the *body* of the DONE branch — additive, not a replacement.

---

## Peer comparison (cohort floor + bar)

**Strongest peer:** `context-warm` — it is the only component with the *full* uniform
stack: declared inputs, Status protocol (DONE/BLOCKED/NEEDS_CONTEXT), Pause-points,
Hop-in support, structured Integration (reads/writes/triggers), Anti-patterns, **Failure
recovery**, and an explicit budget-event write (D5/D13). It is also the declared base for
6 variants — a real shared-schema spine. Runner-up: `context-warm-customer` (adds
mandatory sensitivity pause + audit log, D7+D13).

**Weakest peer:** `skill-router` — no Status protocol, no failure recovery, no
observability write, no 00-state append, no necessity, and its in/out contract (D3) is
the loosest (free-text in, free-text out, no envelope). It also still self-references the
deprecated name `/match` in its body (skill-router:83) while the frontmatter deprecates it.

**Cohort floor (what every hand-off skill must reach):** declared inputs (D3 in),
declared outputs/report (D3 out), explicit Status protocol (D2), one observability write
(D13), one failure-mode branch (D12), and — once built — a `brief_forge_handoffs:`
declaration (D8/D9). context-warm meets the floor; ~11 of 18 fall below it on at least
two dimensions.

---

## Per-component records

> Dimensions that are uniform-with-cohort or n/a-for-kind are collapsed to one line.
> Load-bearing dimensions get the full nano/macro/high/finding/proposed/why shape.
> CF-n references the cohort-level findings above.

### context-save (strongest of the persistence pair, but root-broken)

```yaml
component: skills/context-save/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head:
    state: present
    nano: context-save:28 ("## Inputs"), :38 ("## Workflow" step 1)
    finding: Inputs declared (no-arg + optional label); head is explicit. Uniform-strong.
    proposed: none (at bar)
  D2_tail:
    state: partial
    nano: context-save:102 ("## Report format" ✓ line); no Status protocol token
    high: resume/replay cannot machine-detect completion (CF-4)
    finding: gstack-dialect tail — human ✓ only, no DONE/BLOCKED.
    proposed: add Status protocol DONE/BLOCKED + Hop-in support; keep ✓ as DONE body.
    why: bring to context-warm bar; lintel dialect is the machine-readable floor.
  D3_objects:
    state: partial
    nano: context-save:41 (writes ~/.gstack/...); consumer context-dump:38 expects ~/.lintel/...
    high: producer/consumer contract break (CF-1, CF-2) — live breakage.
    finding: output filename + root do not match its named consumer (context-dump).
    proposed: shared checkpoint-envelope spec; both import; add integration test.
    why: operator's own shared-schema rule — define once, import both sides.
  D4_entrypoints:
    state: present
    nano: context-save:13, :150 (li-token-watcher hook surfaces it; /clean offers it)
    finding: reachable via token-watcher + /clean + manual. Coverage good.
    proposed: none
  D5_checkpoints:
    state: present
    nano: context-save:50-97 (writes the checkpoint file itself — it IS the checkpoint)
    finding: this skill is the canonical checkpoint writer. Uniform-strong.
    proposed: emit to canonical root (CF-1) so checkpoints are replay-readable.
  D6_recovery:
    state: present
    nano: context-save:123 ("## Failure modes": write-fail -> stdout fallback)
    finding: has stdout fallback on write failure. Above-bar for cohort.
    proposed: none
  D7_pack:
    state: absent
    nano: not declared
    high: pack-influence designed-not-built (D7 runtime).
    finding: n/a unbuilt — but a pack could set checkpoint root/retention.
    proposed: when packs land, expose checkpoint root + retention as pack policy.
  D8_frontmatter:
    state: partial
    nano: context-save:1-9 (has layer/color/voice/cli_support; no necessity, no brief_forge_handoffs, no expected_inputs/outputs)
    finding: missing necessity + brief_forge_handoffs (CF-3) + declared I/O contract.
    proposed: add necessity, expected_inputs/outputs, brief_forge_handoffs stub.
  D9_brief_forge:
    state: absent
    nano: n/a unbuilt
    high: hand-off moment 4 (workflow->cold executor). THIS IS A BRIEF-FORGE SHOULD-FIRE.
    finding: every /context-save is a cold-executor hand-off that Brief Forge is designed to gate (curate->evaluate->envelope). Today it is un-gated.
    proposed: on save, Brief Forge "curate" phase evaluates completeness (next-steps present? failed-attempts captured?) and writes the envelope instead of an ad-hoc .md.
    why: the checkpoint IS the brief; save is the canonical place the gate earns its keep.
  D10_lessons:
    state: absent
    nano: not referenced
    finding: save captures "failed attempts" inline but never writes them to lessons.md.
    proposed: offer to promote failed-attempts -> lessons.md (operator-relation evolution).
    why: closes the repo-relation/operator-relation loop the motto promises.
  D11_subagent:
    state: n/a-for-kind
    finding: single-shot capture; no delegation needed.
  D12_failure:
    state: present
    nano: context-save:123-127 (write/slug/branch failures all handled)
    finding: above-bar. Uniform-strong.
  D13_observability:
    state: partial
    nano: context-save:104 (prints path); no jsonl/usage-log write
    finding: operator sees output inline but no durable observability record.
    proposed: append a save event to the canonical jobs/envelope log.
  D14_necessity:
    state: absent
    nano: not declared
    finding: no REQUIRED/RECOMMENDED/OPTIONAL + gap-if-skipped.
    proposed: declare STRONGLY RECOMMENDED at session-end; gap = cold restart loses state.
peer_comparison:
  strongest_peer_in_cohort: context-warm
  this_component_depth: below-bar (D2, D3, D13)
  uplift_needed: Status protocol, canonical root, observability write
operator_decision_required: yes  # CF-1 root choice
priority: high
```

### context-restore (matched to save; inherits the root break)

```yaml
component: skills/context-restore/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "context-restore:27 (Inputs: optional path / auto-discover)", finding: explicit head, uniform }
  D2_tail:
    state: partial
    nano: context-restore:43 (Report format ✓ only, no Status protocol)
    finding: gstack-dialect tail (CF-4).
    proposed: add Status protocol; keep restoration summary as DONE body.
  D3_objects:
    state: partial
    nano: context-restore:35 (reads ~/.gstack/...checkpoints)
    high: reads a different root than snapshot/dump write (CF-1).
    finding: pairs correctly with context-save root but diverges from the snapshot family.
    proposed: read canonical root; accept legacy gstack path as alias.
  D4_entrypoints: { state: present, nano: "context-restore:13, :120 (companion to /clean, save)", finding: covered }
  D5_checkpoints:
    state: present
    nano: context-restore:39 (git log diff-check since checkpoint sha)
    finding: above-bar — verifies drift between checkpoint and HEAD. Strong.
  D6_recovery:
    state: present
    nano: context-restore:69-75 (no checkpoint / missing files / stale -> inform, never error)
    finding: graceful degradation throughout. Above-bar.
  D7_pack: { state: absent, nano: n/a unbuilt, finding: "pack could set staleness window (7d hardcoded :74)", proposed: pack-policy staleness threshold }
  D8_frontmatter:
    state: partial
    nano: context-restore:1-9 (no necessity, no brief_forge_handoffs, no declared I/O)
    finding: CF-3 + missing necessity/I-O.
    proposed: add necessity + expected_inputs/outputs + brief_forge_handoffs stub.
  D9_brief_forge:
    state: absent
    nano: n/a unbuilt
    high: hand-off moment 4 RECEIVE side. SHOULD-FIRE.
    finding: restore is the receive end of the cold-executor hand-off; Brief Forge "evaluate" phase belongs here (is the brief sufficient to resume?).
    proposed: on restore, Brief Forge evaluate-phase scores the loaded envelope and warns if next-steps/decisions are thin before declaring DONE.
    why: receive-side evaluation is half the gate; today restore trusts the file blindly.
  D10_lessons: { state: absent, finding: "doesn't surface prior lessons on restore", proposed: "warm lessons.md tagged to the restored task" }
  D11_subagent: { state: n/a-for-kind }
  D12_failure: { state: present, nano: "context-restore:82-86", finding: above-bar }
  D13_observability: { state: partial, nano: "prints summary; no durable log", proposed: append restore event to canonical log }
  D14_necessity: { state: absent, proposed: "STRONGLY RECOMMENDED at session resume; gap = re-deriving prior state" }
peer_comparison:
  strongest_peer_in_cohort: context-warm
  this_component_depth: below-bar (D2, D13)
  uplift_needed: Status protocol + observability + receive-side Brief Forge eval
operator_decision_required: no
priority: high
```

### context-snapshot

```yaml
component: skills/context-snapshot/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "context-snapshot:32 (name arg)", finding: explicit }
  D2_tail: { state: present, nano: "context-snapshot:96 (Status protocol DONE/BLOCKED)", finding: lintel dialect, at-bar }
  D3_objects:
    state: partial
    nano: context-snapshot:36 (writes ~/.lintel/sessions/<branch>/...-snapshot-<name>.md)
    high: a THIRD filename convention vs save and dump (CF-1, CF-2).
    finding: overlaps context-save in purpose; explicitly distinguishes itself (:15) but uses yet another root+name.
    proposed: converge root with the persistence pair; declare snapshot vs save as a `content_type` on one envelope schema, not two file conventions.
    why: subtraction-bias — one envelope with a type field, not two near-duplicate skills.
  D4_entrypoints: { state: present, nano: "context-snapshot:18-22", finding: covered; also surfaced by context-cool:79 as the restart path }
  D5_checkpoints: { state: present, nano: "context-snapshot:87 (00-state.md append event)", finding: at-bar }
  D6_recovery: { state: absent, nano: "no failure-modes section", high: "below floor — no recovery branch", finding: "unlike save, no write-fail fallback", proposed: "add Failure modes (write-fail -> stdout) mirroring context-save:123" }
  D7_pack: { state: absent, nano: n/a unbuilt, finding: "frontmatter has Mode/Role/WorkProfile fields IN the snapshot body (:57-62) — captures pack state but doesn't consume it" }
  D8_frontmatter: { state: partial, nano: "context-snapshot:1-9 (no necessity, no brief_forge_handoffs)", proposed: "add CF-3 stub + necessity" }
  D9_brief_forge:
    state: absent
    nano: n/a unbuilt
    high: moment 4 (mid-session cold-restart bridge). SHOULD-FIRE.
    finding: snapshot->restart->dump is a deliberate cold-executor hand-off; Brief Forge curate-phase belongs at snapshot.
    proposed: snapshot writes a Brief Forge envelope (HEAD+BODY+TAIL) so dump can replay it.
  D10_lessons: { state: absent, proposed: "n/a — too lightweight; defer" }
  D11_subagent: { state: n/a-for-kind }
  D12_failure: { state: partial, nano: "context-snapshot:96 (DONE/BLOCKED only)", finding: "no concrete failure branches", proposed: "enumerate write-fail / no-name cases" }
  D13_observability: { state: present, nano: "context-snapshot:87 (00-state append)", finding: at-bar }
  D14_necessity: { state: absent, proposed: "OPTIONAL; gap = no mid-session rollback point" }
peer_comparison:
  strongest_peer_in_cohort: context-warm
  this_component_depth: below-bar (D6, D3)
  uplift_needed: failure recovery + envelope convergence with save
operator_decision_required: yes  # snapshot-vs-save consolidation
priority: medium
```

### context-dump (the broken consumer)

```yaml
component: skills/context-dump/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "context-dump:33 (session_id + branch args)", finding: explicit }
  D2_tail: { state: present, nano: "context-dump:88 (Status protocol DONE/BLOCKED)", finding: lintel dialect, at-bar }
  D3_objects:
    state: absent
    nano: context-dump:38 (greps for *-context-save.md in ~/.lintel/sessions/)
    high: CF-2 — its declared producer (context-save) writes neither that name nor that root. The contract is BROKEN at the consumer.
    finding: this is the single most concrete in/out contract failure in the cohort; dump cannot find what save writes.
    proposed: align to the shared checkpoint-envelope spec; add the producer->consumer integration test.
    why: a named consumer that cannot read its named producer is a correctness bug, not a style gap.
  D4_entrypoints: { state: present, nano: "context-dump:18-22; referenced by context-snapshot:84 + context-cool:81", finding: covered }
  D5_checkpoints: { state: present, nano: "context-dump:80 (00-state append context_dump event)", finding: at-bar }
  D6_recovery: { state: partial, nano: "context-dump:40-47 (no-match -> lists sessions)", finding: handles no-match; no handling for malformed file }
  D7_pack: { state: absent, nano: n/a unbuilt }
  D8_frontmatter: { state: partial, nano: "context-dump:1-9 (CF-3; no necessity)", proposed: add stub + necessity }
  D9_brief_forge:
    state: absent
    nano: n/a unbuilt
    high: moment 4 RECEIVE side. SHOULD-FIRE.
    finding: dump is a receive-side cold-executor hand-off; same evaluate-phase argument as restore.
    proposed: evaluate envelope sufficiency before injecting; delegate load via canonical warm.
  D10_lessons: { state: absent }
  D11_subagent: { state: n/a-for-kind }
  D12_failure: { state: present, nano: "context-dump:88 + :40", finding: at-bar }
  D13_observability: { state: present, nano: "context-dump:80", finding: at-bar }
  D14_necessity: { state: absent, proposed: "OPTIONAL; gap = cannot recover a specific named prior session" }
peer_comparison:
  strongest_peer_in_cohort: context-warm
  this_component_depth: below-bar (D3 — broken contract)
  uplift_needed: fix producer/consumer contract (CF-2) is the priority
operator_decision_required: yes  # tied to CF-1/CF-2
priority: high
```

### context-warm (THE BAR — strongest peer)

```yaml
component: skills/context-warm/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "context-warm:34 (Step 1 parse target, glob-resolve)", finding: explicit + validates 0-match at head, above-bar }
  D2_tail: { state: present, nano: "context-warm:123 (DONE/BLOCKED/NEEDS_CONTEXT)", finding: full lintel dialect — sets the bar }
  D3_objects:
    state: present
    nano: context-warm:138-150 (Integration: explicit Reads/Writes/Triggers)
    finding: the only component with a fully-itemized I/O contract incl. side-effects. Sets the bar.
    proposed: promote this Integration block to a frontmatter expected_inputs/outputs so it is machine-readable too.
  D4_entrypoints: { state: present, nano: "context-warm:23-26 (pre-PLAN/mid-BUILD/pre-REVIEW)", finding: covered; base for 6 variants }
  D5_checkpoints: { state: present, nano: "context-warm:92 (.lintel/state/context-budget.md append, full event schema)", finding: best checkpoint write in cohort }
  D6_recovery: { state: present, nano: "context-warm:158 (Failure recovery: 0-match / unreadable / overrun)", finding: only component with a named Failure-recovery section — bar-setter }
  D7_pack: { state: partial, nano: "context-warm:155 (WorkProfile customer-PII check)", finding: consumes WorkProfile (one of few that do); pack-influence still designed-not-built }
  D8_frontmatter:
    state: partial
    nano: context-warm:1-9 (rich description, but no necessity, no brief_forge_handoffs, no expected_inputs/outputs field)
    finding: even the bar-setter lacks CF-3 field + necessity.
    proposed: add brief_forge_handoffs stub + necessity + lift Integration to frontmatter I/O.
  D9_brief_forge:
    state: absent
    nano: n/a unbuilt
    high: moment 5 (operator->skill) + it is the delegation TARGET of 5 variants (moment 1-ish).
    finding: warm is the common sink for the whole family; Brief Forge could standardize the "what got loaded + why" envelope here once for all variants.
    proposed: warm emits a load-envelope; variants delegate and inherit it. Single gate point.
    why: most elegant — gate the base, all variants inherit, zero per-variant duplication.
  D10_lessons: { state: absent, proposed: "n/a — warm is a mechanism, not a decision point" }
  D11_subagent: { state: n/a-for-kind }
  D12_failure: { state: present, nano: "context-warm:158-162", finding: bar-setter }
  D13_observability: { state: present, nano: "context-warm:92 (durable budget event)", finding: bar-setter }
  D14_necessity: { state: absent, proposed: "OPTIONAL (on-demand); gap = under-utilized 1M window" }
peer_comparison:
  strongest_peer_in_cohort: context-warm (self — sets the bar)
  this_component_depth: at-bar
  uplift_needed: only D8 (frontmatter I/O + brief_forge_handoffs + necessity)
operator_decision_required: no
priority: low
```

### Warm variants (related / sessions / adrs) — uniform sub-cluster

These three share one shape: head=topic/N arg, tail=DONE/BLOCKED, body=surface-candidates
then **delegate to `/li:context-warm`**, 00-state append. They are the cleanest sub-cluster
in the cohort (consistent delegation = good D11-adjacent pattern). Records compressed.

```yaml
component: skills/context-warm-related/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "context-warm-related:32 (topic/scope/limit args)", finding: explicit }
  D2_tail: { state: present, nano: "context-warm-related:87 (DONE/DONE_WITH_CONCERNS/BLOCKED/NEEDS_CONTEXT)", finding: richest status enum in cohort — above-bar }
  D3_objects: { state: present, nano: "context-warm-related:102 (delegates load to context-warm; clear in=topic out=loaded-files)", finding: at-bar via delegation }
  D4_entrypoints: { state: present, nano: "context-warm-related:21-26" }
  D5_checkpoints: { state: present, nano: "context-warm-related:76 (00-state append)" }
  D6_recovery: { state: partial, nano: "no Failure-recovery section (relies on warm's)", proposed: "note that recovery is inherited from delegated warm; make inheritance explicit" }
  D7_pack: { state: absent, nano: n/a unbuilt }
  D8_frontmatter: { state: partial, nano: "CF-3; no necessity", proposed: stub + necessity }
  D9_brief_forge: { state: absent, nano: n/a unbuilt, high: "moment 5; inherits warm's envelope if CF gate lands at base", finding: "should inherit base-warm envelope", proposed: "no own gate — inherit from context-warm (elegant)" }
  D10_lessons: { state: absent }
  D11_subagent: { state: n/a-for-kind, finding: "delegates to a sibling skill, not a subagent (acceptable)" }
  D12_failure: { state: present, nano: "context-warm-related:87 + :106 (anti-patterns cover broad-topic)" }
  D13_observability: { state: present, nano: "context-warm-related:76 (via 00-state + warm's budget log)" }
  D14_necessity: { state: absent, proposed: OPTIONAL }
peer_comparison: { strongest_peer_in_cohort: context-warm, this_component_depth: below-bar (D6 inherited-not-stated), uplift_needed: "make delegated recovery explicit + CF-3" }
operator_decision_required: no
priority: low
```

```yaml
component: skills/context-warm-sessions/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "context-warm-sessions:32 (N arg, default 3)" }
  D2_tail: { state: present, nano: "context-warm-sessions:78 (DONE/BLOCKED/NEEDS_CONTEXT)" }
  D3_objects:
    state: partial
    nano: context-warm-sessions:40 (reads ~/.lintel/sessions/<branch>/*-context-save.md)
    high: same broken assumption as context-dump (CF-2) — expects context-save at ~/.lintel/sessions, but save writes ~/.gstack.
    finding: SECOND consumer that cannot find context-save output. Reinforces CF-1/CF-2 severity.
    proposed: align to shared checkpoint-envelope spec.
  D4_entrypoints: { state: present, nano: "context-warm-sessions:18; also the recommended path from context-dump:27" }
  D5_checkpoints: { state: present, nano: "context-warm-sessions:69 (00-state append)" }
  D6_recovery: { state: partial, nano: "no-sessions -> BLOCKED; no malformed-file handling" }
  D7_pack: { state: absent, nano: n/a unbuilt }
  D8_frontmatter: { state: partial, nano: "CF-3; no necessity" }
  D9_brief_forge: { state: absent, nano: n/a unbuilt, high: "moment 4 receive (multi-envelope)", finding: "loads N cold-executor briefs; evaluate-phase should rank/dedupe", proposed: "Brief Forge dedupes overlapping session envelopes" }
  D10_lessons: { state: absent }
  D11_subagent: { state: n/a-for-kind }
  D12_failure: { state: present, nano: "context-warm-sessions:78 + :90 (cross-branch anti-pattern)" }
  D13_observability: { state: present, nano: "context-warm-sessions:69" }
  D14_necessity: { state: absent, proposed: OPTIONAL }
peer_comparison: { strongest_peer_in_cohort: context-warm, this_component_depth: below-bar (D3 broken), uplift_needed: "fix CF-2 contract" }
operator_decision_required: yes  # CF-1/CF-2
priority: high
```

```yaml
component: skills/context-warm-adrs/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "context-warm-adrs:32 (topic arg)" }
  D2_tail: { state: present, nano: "context-warm-adrs:85 (DONE/BLOCKED)" }
  D3_objects: { state: present, nano: "context-warm-adrs:36 (in=topic, reads docs/adr/*.md, out=delegated load)", finding: clean in-repo source, no CF-1 issue }
  D4_entrypoints: { state: present, nano: "context-warm-adrs:18-22 (pre-PLAN/DEFINE)" }
  D5_checkpoints: { state: present, nano: "context-warm-adrs:76" }
  D6_recovery: { state: partial, nano: "no-dir/no-match -> BLOCKED silent (:87)" }
  D7_pack: { state: absent, nano: n/a unbuilt }
  D8_frontmatter: { state: partial, nano: "CF-3; no necessity" }
  D9_brief_forge:
    state: absent
    nano: n/a unbuilt
    high: moment 5 + this is a KNOWLEDGE hand-off (D10 overlap). SHOULD-FIRE.
    finding: ADR warm is the cohort's clearest knowledge->session hand-off; Brief Forge curate-phase = "which prior decisions are relevant + which deliberately excluded".
    proposed: ADR-warm envelope records the deliberate-exclusions list (a Brief Forge curate field).
  D10_lessons:
    state: partial
    nano: context-warm-adrs:15 (loads ADRs = prior decisions)
    high: this IS knowledge integration — strongest D10 in cohort.
    finding: consults ADRs but not lessons.md/knowhow tag-funnel.
    proposed: extend to also surface lessons tagged to the topic (repo-relation thread).
    why: ADRs + lessons are the two halves of repo memory; warm one, warm both.
  D11_subagent: { state: n/a-for-kind }
  D12_failure: { state: present, nano: "context-warm-adrs:87 + :99 (anti-patterns)" }
  D13_observability: { state: present, nano: "context-warm-adrs:76" }
  D14_necessity: { state: absent, proposed: "STRONGLY RECOMMENDED pre-PLAN; gap = contradicting prior ADRs" }
peer_comparison: { strongest_peer_in_cohort: context-warm, this_component_depth: below-bar (D6, D10 partial), uplift_needed: "lessons.md integration + necessity" }
operator_decision_required: no
priority: medium
```

### context-warm-customer (runner-up strongest — best D7/D13)

```yaml
component: skills/context-warm-customer/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "context-warm-customer:32 (engagement arg + repo resolution)", finding: explicit, multi-candidate resolve, above-bar }
  D2_tail: { state: present, nano: "context-warm-customer:98 (DONE/BLOCKED)" }
  D3_objects: { state: present, nano: "context-warm-customer:54-62 (declared default load-set + --scope override)", finding: best-specified input contract among variants }
  D4_entrypoints: { state: present, nano: "context-warm-customer:18-22" }
  D5_checkpoints: { state: present, nano: "context-warm-customer:86 (00-state) + :96 (audit jsonl)" }
  D6_recovery: { state: partial, nano: "repo-not-found -> BLOCKED w/ suggestion (:44)" }
  D7_pack:
    state: present
    nano: context-warm-customer:51 (WorkProfile=on mandatory sensitivity gate)
    high: one of the few skills where WorkProfile measurably changes behavior — D7 exemplar.
    finding: WorkProfile gating present and load-bearing; pack-runtime still unbuilt.
    proposed: when packs land, pack policy sets the customer-PII pattern list (today hardcoded).
  D8_frontmatter: { state: partial, nano: "CF-3; no necessity" }
  D9_brief_forge:
    state: absent
    nano: n/a unbuilt
    high: moment 5 + sensitivity gate is exactly a Brief Forge "deliberate-exclusion" evaluator.
    finding: the sensitivity pause is a proto-Brief-Forge evaluator already; formalize it as one.
    proposed: register customer-PII scan as a named Brief Forge evaluator that packs can toggle.
  D10_lessons: { state: absent, proposed: "surface prior-engagement lessons for this customer" }
  D11_subagent: { state: n/a-for-kind }
  D12_failure: { state: present, nano: "context-warm-customer:98 + :114 (anti-patterns mandatory)" }
  D13_observability:
    state: present
    nano: context-warm-customer:96 (~/.lintel/audit/customer-repo-access.jsonl)
    high: best observability in cohort — durable audit trail.
    finding: bar-setter for D13 (durable audit, not just 00-state).
  D14_necessity: { state: absent, proposed: "REQUIRED before cross-repo customer reasoning; gap = unaudited customer access" }
peer_comparison: { strongest_peer_in_cohort: context-warm, this_component_depth: at-bar (above on D7/D13), uplift_needed: "necessity + brief-forge evaluator formalization" }
operator_decision_required: no
priority: low
```

### context-warm-from-url

```yaml
component: skills/context-warm-from-url/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "context-warm-from-url:33 (url arg + format validation at head)", finding: validates input at head, above-bar }
  D2_tail: { state: present, nano: "context-warm-from-url:96 (DONE/BLOCKED)" }
  D3_objects: { state: partial, nano: "context-warm-from-url:71 (in=url, out=fetched content injected); no envelope", finding: web content injected as free text, no provenance wrapper }
  D4_entrypoints: { state: present, nano: "context-warm-from-url:18-22" }
  D5_checkpoints: { state: present, nano: "context-warm-from-url:84 (00-state) + :93 (url-fetches.jsonl)" }
  D6_recovery: { state: present, nano: "context-warm-from-url:114 (binary/paywalled/JS -> clean fail)", finding: above-bar }
  D7_pack:
    state: present
    nano: context-warm-from-url:42-66 (WorkProfile=on -> MS-allowed-domain gate)
    finding: WorkProfile changes behavior (domain allowlist). D7 exemplar #2.
    proposed: pack policy supplies the allowlist (today hardcoded :48-53).
  D8_frontmatter: { state: partial, nano: "CF-3; no necessity" }
  D9_brief_forge: { state: absent, nano: n/a unbuilt, high: "moment 5 + external-source provenance is a Brief Forge TAIL concern", finding: "fetched content has no provenance envelope", proposed: "wrap fetched content in envelope TAIL (url, domain, fetch-ts, integrity)" }
  D10_lessons: { state: absent }
  D11_subagent: { state: n/a-for-kind }
  D12_failure: { state: present, nano: "context-warm-from-url:97 + :112" }
  D13_observability: { state: present, nano: "context-warm-from-url:93 (durable url-fetch audit)", finding: above-bar }
  D14_necessity: { state: absent, proposed: OPTIONAL }
peer_comparison: { strongest_peer_in_cohort: context-warm, this_component_depth: at-bar, uplift_needed: "provenance envelope + necessity" }
operator_decision_required: no
priority: low
```

### context-warmup (the odd one — phase-budget model, different config)

```yaml
component: skills/context-warmup/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "context-warmup:37 (--task/--all/--estimate-only flags)", finding: explicit; also has the cohort's only degraded-cli_support declaration (:8-16) }
  D2_tail: { state: partial, nano: "context-warmup:58 (Report format); no Status protocol token", finding: gstack-dialect tail (CF-4) }
  D3_objects:
    state: partial
    nano: context-warmup:46 (reads context-state.json + warmup_tasks frontmatter)
    high: introduces a FOURTH state file name — context-state.json — vs 00-state.md used by every other lintel-dialect skill.
    finding: reads context-state.json (:46) while siblings read .lintel/state/00-state.md — naming drift inside one cohort.
    proposed: converge on 00-state.md; or declare context-state.json as the canonical machine-state and 00-state.md as the human log (pick one, document it).
    why: two state-file names is exactly the fragmentation this audit exists to surface.
  D4_entrypoints: { state: present, nano: "context-warmup:21 (auto-warmup on phase entry vs explicit)" }
  D5_checkpoints: { state: partial, nano: "context-warmup:53 (warmup_tasks_completed) — phase-budget model, no 00-state append", finding: uses a different checkpoint model (phase budget) than the budget-event model of context-warm }
  D6_recovery: { state: present, nano: "context-warmup:86-91 (ambiguous-spec/over-budget/read-fail all handled)", finding: above-bar }
  D7_pack: { state: partial, nano: "context-warmup:25 (warmup_enabled config) + per-phase budget (:67)", finding: config-driven but not pack-driven; closest to pack model }
  D8_frontmatter: { state: present, nano: "context-warmup:8-16 (richest cli_support w/ degradation strategy) — but no necessity, no brief_forge_handoffs (CF-3)", finding: best cli_support, still CF-3 gap }
  D9_brief_forge:
    state: absent
    nano: n/a unbuilt
    high: moment 2 (phase->phase: warmup runs at phase entry). SHOULD-FIRE — distinct from the moment-4/5 cluster.
    finding: this is the cohort's only moment-2 (phase boundary) hand-off; Brief Forge phase-entry curate belongs here.
    proposed: warmup-tasks BECOME the Brief Forge curate declaration for phase entry.
    why: warmup_tasks is already a proto-brief; promote it to the real one.
  D10_lessons: { state: absent }
  D11_subagent: { state: partial, nano: "context-warmup:118 (references ContextBudgetAdvisor agent) but doesn't spawn it", finding: names an agent it could delegate to but doesn't }
  D12_failure: { state: present, nano: "context-warmup:86-91", finding: above-bar }
  D13_observability: { state: present, nano: "context-warmup:78 (context-warmup.jsonl audit)", finding: above-bar }
  D14_necessity: { state: absent, proposed: "OPTIONAL when auto-warmup on; gap = manual preload needed" }
peer_comparison: { strongest_peer_in_cohort: context-warm, this_component_depth: below-bar (D2, D3 state-file drift), uplift_needed: "Status protocol + state-file naming convergence (CF-1 sibling)" }
operator_decision_required: yes  # context-state.json vs 00-state.md
priority: medium
```

### context-budget

```yaml
component: skills/context-budget/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "context-budget:24-27 (when-to-use; no-arg query)", finding: implicit head (no formal Inputs section), partial }
  D2_tail: { state: present, nano: "context-budget:115 (DONE)", finding: lintel dialect, at-bar }
  D3_objects:
    state: partial
    nano: context-budget:33 (.lintel/state/context-budget.md) + :64 (~/.lintel/profile.yaml mode)
    high: reads in-repo budget log AND home profile.yaml — straddles two roots (CF-1).
    finding: mode-envelope caps (:53-60) hardcoded in the skill body, not in a shared config.
    proposed: move mode_envelopes to the canonical config (shared schema); skill reads, doesn't define.
  D4_entrypoints: { state: present, nano: "context-budget:18-22" }
  D5_checkpoints: { state: present, nano: "context-budget:107 (light 00-state append)" }
  D6_recovery: { state: absent, nano: "no failure-modes section", proposed: "add: log-missing -> estimate; profile-missing -> default mode" }
  D7_pack:
    state: partial
    nano: context-budget:64 (reads mode from ~/.lintel/profile.yaml)
    high: mode IS a proto-pack/WorkProfile influence — the cap changes by mode.
    finding: mode-driven caps present; this is the closest D7 to the designed pack model.
    proposed: when packs land, mode_envelopes become pack policy.
  D8_frontmatter: { state: partial, nano: "CF-3; no necessity" }
  D9_brief_forge:
    state: absent
    nano: n/a unbuilt
    high: it ENFORCES the 500k soft / 750k hard handoff cap (:49-76) — directly the Brief Forge size budget.
    finding: this skill already implements the handoff-size logic Brief Forge envelopes need; it should be the enforcement point the gate calls.
    proposed: Brief Forge calls context-budget's cap logic at every envelope emit; don't duplicate the cap math.
    why: subtraction — one cap implementation, reused by the gate.
  D10_lessons: { state: absent }
  D11_subagent: { state: n/a-for-kind }
  D12_failure: { state: partial, nano: "context-budget:131 (anti-patterns) but no failure-modes", proposed: add recovery branch }
  D13_observability: { state: present, nano: "context-budget:107" }
  D14_necessity: { state: absent, proposed: "RECOMMENDED before heavy phase; gap = blind to headroom" }
peer_comparison: { strongest_peer_in_cohort: context-warm, this_component_depth: below-bar (D6, D3 root-straddle), uplift_needed: "config externalization + failure recovery" }
operator_decision_required: yes  # mode_envelopes home (CF-1)
priority: medium
```

### context-budgetwatch

```yaml
component: skills/context-budgetwatch/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "context-budgetwatch:32-36 (--budget/--quiet/--mode flags)", finding: explicit, above-bar for budget cluster }
  D2_tail: { state: partial, nano: "context-budgetwatch:60 (Report format GREEN/YELLOW/RED); no Status protocol token", finding: gstack-dialect (CF-4); but CI exit-code behavior (:99) is a strong machine-tail }
  D3_objects:
    state: partial
    nano: context-budgetwatch:39 (~/.lintel/config.yaml watcher section) + :49 (~/.lintel/sessions/<id>/tokens.txt)
    high: a FIFTH config location — ~/.lintel/config.yaml — vs context-budget's ~/.lintel/profile.yaml and context-budgetwatch's own. Config schism within the budget cluster.
    finding: budget reads profile.yaml; budgetwatch reads config.yaml — two skills, two config files, same domain.
    proposed: one config file with a watcher + envelopes section; both read it.
  D4_entrypoints:
    state: present
    nano: context-budgetwatch:14 + context-save:150 (token-watcher hook surfaces save, but is budgetwatch wired to the hook?)
    high: D4 gap — the li-token-watcher HOOK is the automated entrypoint, but budgetwatch is described as the MANUAL trigger; unclear if the hook calls budgetwatch or duplicates its logic.
    finding: possible duplication between li-token-watcher hook and this manual skill.
    proposed: hook should call this skill (single source of threshold logic), not reimplement.
  D5_checkpoints: { state: absent, nano: "read-only, no event write (:88 says audit not needed)", finding: deliberately no checkpoint — acceptable for a read-only watcher }
  D6_recovery: { state: present, nano: "context-budgetwatch:94-99 (telemetry-unavailable -> estimate; missing config -> defaults)", finding: above-bar }
  D7_pack: { state: partial, nano: "context-budgetwatch:33 (operator-configurable thresholds, Layer 4)", finding: config-tunable, not pack-driven }
  D8_frontmatter: { state: present, nano: "context-budgetwatch:4 (v1_alias declared) — good migration hygiene; but CF-3 + no necessity" }
  D9_brief_forge: { state: absent, nano: n/a unbuilt, high: "moment 5; it's the trigger that SURFACES save (a hand-off)", finding: "watcher recommends save but doesn't itself produce an envelope", proposed: "watcher RED -> auto-invoke Brief Forge curate to pre-stage the handoff envelope" }
  D10_lessons: { state: absent }
  D11_subagent: { state: n/a-for-kind }
  D12_failure: { state: present, nano: "context-budgetwatch:94-99 (incl. CI non-zero exit on RED)", finding: above-bar — best CI integration in cohort }
  D13_observability: { state: partial, nano: "context-budgetwatch:88 (explicitly no audit log)", finding: read-only justification reasonable but means no record it ran }
  D14_necessity: { state: absent, proposed: "RECOMMENDED on long sessions; gap = silent quality degradation past 50k" }
peer_comparison: { strongest_peer_in_cohort: context-warm, this_component_depth: below-bar (D2, D3 config-schism, D4 hook duplication), uplift_needed: "Status protocol + config convergence + hook/skill dedup" }
operator_decision_required: yes  # config.yaml vs profile.yaml + hook duplication
priority: high
```

### context-cool

```yaml
component: skills/context-cool/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "context-cool:32 (Step 1 surface loaded)", finding: implicit head (no Inputs section) }
  D2_tail: { state: present, nano: "context-cool:93 (DONE / DONE_WITH_CONCERNS)", finding: lintel dialect; honest DONE_WITH_CONCERNS for the no-real-trim caveat — good }
  D3_objects:
    state: partial
    nano: context-cool:58 (writes .lintel/state/context-ignore.md as a COORDINATION signal)
    high: introduces a coordination-signal contract (context-ignore.md) that other skills must honor — but no other skill in cohort declares reading it.
    finding: the IGNORE contract is write-only; no documented consumer respects it (:68 admits it's coordination-only).
    proposed: document which skills/agents read context-ignore.md, or fold into the envelope's exclusion list.
    why: a contract with no consumer is dead weight — Brief Forge "deliberate exclusions" is the right home for it.
  D4_entrypoints: { state: present, nano: "context-cool:22-28" }
  D5_checkpoints: { state: present, nano: "context-cool:85 (00-state append context_cool)" }
  D6_recovery: { state: absent, nano: "no failure-modes section", proposed: "add: budget-log-missing -> nothing to cool, inform" }
  D7_pack: { state: absent, nano: n/a unbuilt }
  D8_frontmatter: { state: partial, nano: "CF-3; no necessity" }
  D9_brief_forge: { state: absent, nano: n/a unbuilt, high: "the IGNORE list IS a Brief Forge deliberate-exclusion declaration", finding: "context-cool's ignore-markers are exactly Brief Forge curate-phase exclusions", proposed: "fold context-ignore.md into the envelope exclusion list — one mechanism" }
  D10_lessons: { state: absent }
  D11_subagent: { state: n/a-for-kind }
  D12_failure: { state: partial, nano: "context-cool:96 (DONE_WITH_CONCERNS caveat) but no failure branches" }
  D13_observability: { state: present, nano: "context-cool:85" }
  D14_necessity: { state: absent, proposed: "OPTIONAL; gap = budget bloat with no declared drop signal" }
peer_comparison: { strongest_peer_in_cohort: context-warm, this_component_depth: below-bar (D6, D3 orphan-contract), uplift_needed: "consumer for IGNORE contract + failure recovery" }
operator_decision_required: no
priority: medium
```

### pair-agent (best D11 in cohort — true subagent delegation)

```yaml
component: skills/pair-agent/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "pair-agent:33 (required --agent + task; --turns/--scope)", finding: explicit, validated inputs }
  D2_tail: { state: partial, nano: "pair-agent:51 (Report format + Synthesis); no DONE/BLOCKED token", finding: gstack-dialect (CF-4); synthesis is a strong human tail but not machine-tokenized }
  D3_objects:
    state: present
    nano: pair-agent:33-38 (Inputs) + :50 (two-perspective trace + synthesis out)
    high: clearest skill->subagent (moment 1) contract in cohort; --scope restricts subagent reads (:38).
    finding: above-bar I/O contract; the scope-restriction is a curated-brief pattern (Architect-style).
    proposed: formalize the per-turn subagent prompt as a Brief Forge curate declaration.
  D4_entrypoints: { state: present, nano: "pair-agent:21-24" }
  D5_checkpoints: { state: absent, nano: "no 00-state append; turn-loop is in-session only", high: "a multi-turn pair session has no resumable checkpoint", finding: "if interrupted mid-turn-loop, no recovery point", proposed: "append per-turn state to 00-state so an interrupted pair can resume" }
  D6_recovery: { state: present, nano: "pair-agent:88-94 (subagent-not-found / disagreement / 3-reject / budget / no-Agent-tool all handled)", finding: best failure enumeration in cohort — above-bar }
  D7_pack: { state: absent, nano: n/a unbuilt, proposed: "pack could pre-select default --agent per work type" }
  D8_frontmatter: { state: partial, nano: "pair-agent:1-9 (claude-code-only correctly single; CF-3; no necessity)" }
  D9_brief_forge:
    state: absent
    nano: n/a unbuilt
    high: moment 1 (skill->subagent) — the PRIMARY Brief Forge use case. SHOULD-FIRE per turn.
    finding: every subagent turn is a skill->subagent hand-off; the focused prompt + scope (:43-46) is a proto-curate. This is the cohort's flagship should-fire.
    proposed: each turn's subagent invocation goes through Brief Forge curate (context+task+scope+exclusions) -> evaluate -> envelope; logged to jobs/.
    why: moment 1 is the canonical Brief Forge case; pair-agent is the most-built example of it already.
  D10_lessons: { state: absent, proposed: "feed subagent disagreements into lessons.md" }
  D11_subagent:
    state: present
    nano: pair-agent:40-48 (resolves agent, spawns via Agent tool, scoped, per-turn)
    high: the ONLY true subagent-delegating skill in cohort — sets the D11 bar.
    finding: above-bar; curated scope per :38 is the right pattern.
    proposed: none — this is the exemplar other skills should learn from.
  D12_failure: { state: present, nano: "pair-agent:88-94", finding: bar-setter }
  D13_observability: { state: present, nano: "pair-agent:81 (~/.lintel/audit/pair-agent.jsonl)", finding: at-bar }
  D14_necessity: { state: absent, proposed: "OPTIONAL (heavyweight); gap = no in-loop second perspective" }
peer_comparison: { strongest_peer_in_cohort: context-warm (overall); pair-agent sets the D11 bar, this_component_depth: below-bar only on D2/D5, uplift_needed: "Status protocol + per-turn checkpoint" }
operator_decision_required: no
priority: medium
```

### codex (skill->subprocess hand-off; best provenance-into-log)

```yaml
component: skills/codex/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "codex:30-35 (required target one-of; --prompt-style/--budget) + :38 preflight", finding: explicit + preflight PATH check at head, above-bar }
  D2_tail: { state: partial, nano: "codex:46 (Report format + Synthesis); no DONE/BLOCKED token", finding: gstack-dialect (CF-4) }
  D3_objects:
    state: present
    nano: codex:39-44 (in=diff/plan/code/hypothesis -> Codex -> normalized P1/P2/P3 out, persisted via gstack-review-log)
    high: skill->subprocess (a moment-1 variant) with a NORMALIZED output contract (P1/P2/P3) — strongest output-normalization in cohort.
    finding: above-bar; normalizes external tool output to Lintel severities (:41).
    proposed: persist via the canonical envelope/jobs log, not gstack-review-log (CF-1 sibling).
  D4_entrypoints:
    state: present
    nano: codex:111-116 (used by /investigate --with-codex, /plan-eng-review, /release-ev2)
    high: best D4 in cohort — explicitly enumerates the skills that call it.
    finding: above-bar; chained from 3 named callers.
  D5_checkpoints: { state: present, nano: "codex:43 (persist via gstack-review-log so release-ev2 can read)", finding: durable cross-skill state — strong, but on gstack root (CF-1) }
  D6_recovery: { state: present, nano: "codex:85-89 (CLI-missing / malformed / budget-exceeded / hallucination all handled)", finding: above-bar; hallucination-suppression (:89) is unique }
  D7_pack: { state: partial, nano: "codex:78 (first-party-first: prefer Azure OpenAI gateway per config)", finding: config-driven provider routing — a proto-pack policy }
  D8_frontmatter: { state: partial, nano: "codex:1-9 (claude-code-only correctly single; CF-3; no necessity)" }
  D9_brief_forge:
    state: absent
    nano: n/a unbuilt
    high: moment 1 (skill->external executor). SHOULD-FIRE on the prompt construction.
    finding: codex:39 constructs a focused prompt injecting the target — a proto-curate; and the customer-data BLOCK at :76 is a proto-evaluator.
    proposed: Codex prompt goes through Brief Forge curate (what to send, what to exclude — the :76 PII block becomes a named evaluator); response wrapped in envelope.
    why: external-executor hand-offs are where the deliberate-exclusion evaluator most protects against data leak.
  D10_lessons: { state: absent, proposed: "log persistent Codex-vs-local disagreements to lessons.md" }
  D11_subagent: { state: n/a-for-kind, finding: "delegates to external CLI, not an Agent-tool subagent — different mechanism, intentional" }
  D12_failure: { state: present, nano: "codex:85-89", finding: bar-setter }
  D13_observability:
    state: present
    nano: codex:77 (~/.lintel/audit/codex-spend.jsonl) + :87 (raw output capture)
    finding: above-bar — token-spend audit + raw-capture debug trail.
  D14_necessity: { state: absent, proposed: "RECOMMENDED pre-release-ev2 on non-trivial diffs; gap = no outside voice" }
peer_comparison: { strongest_peer_in_cohort: context-warm (overall); codex sets D3-out + D4 bar, this_component_depth: below-bar only on D2, uplift_needed: "Status protocol + canonical-log persistence" }
operator_decision_required: no
priority: low
```

### skill-router (WEAKEST peer)

```yaml
component: skills/skill-router/SKILL.md
kind: skill
cohort: 3
dimensions:
  D1_head: { state: present, nano: "skill-router:31 (intent from arg or AskUserQuestion)", finding: explicit-ish head }
  D2_tail:
    state: absent
    nano: skill-router:47 (Output format) — NO Status protocol, NO DONE/BLOCKED, NO Hop-in support
    high: below floor — no machine-detectable tail at all.
    finding: weakest D2 in cohort; nothing signals completion to a caller.
    proposed: add Status protocol DONE/NEEDS_CONTEXT; keep the match output as DONE body.
  D3_objects:
    state: partial
    nano: skill-router:33 (loads all skills/*/SKILL.md), out=top-3 free-text
    high: loosest in/out contract in cohort — free text in, free text out, no envelope.
    finding: no structured output a downstream router/orchestrator could consume.
    proposed: emit structured matches (name, confidence, invocation) as data, not just prose.
  D4_entrypoints:
    state: partial
    nano: skill-router:12 (body still self-refers as /match) vs frontmatter deprecated_aliases:[match] (:4)
    high: name drift — body uses deprecated /match (:83 "/match"), frontmatter deprecates it.
    finding: internal inconsistency between frontmatter and body naming.
    proposed: scrub /match from body; use /skill-router consistently.
  D5_checkpoints: { state: absent, nano: "no 00-state append", finding: below floor — no record it ran, proposed: "append a router-invocation event" }
  D6_recovery: { state: partial, nano: "skill-router:74-78 (no-match -> /skillify; multi-step -> autoplan)", finding: graceful no-match routing, decent }
  D7_pack:
    state: absent
    nano: not declared
    high: a pack SHOULD scope which skills the router considers (a research pack surfaces research skills first).
    finding: router considers ALL skills regardless of active pack/role.
    proposed: when packs land, router filters/ranks by active pack's skill set.
  D8_frontmatter: { state: partial, nano: "skill-router:4 (deprecated_aliases good); CF-3; no necessity" }
  D9_brief_forge: { state: absent, nano: n/a unbuilt, high: "moment 5 (operator->skill) — the FIRST hand-off; router is the entry to all others", finding: "router is the operator->skill front door; Brief Forge curate could start the envelope chain here", proposed: "router seeds the first envelope (operator intent -> chosen skill)" }
  D10_lessons: { state: partial, nano: "skill-router:42 (reads ~/.lintel/telemetry/ usage frequency)", finding: consults usage telemetry — a proto-operator-relation signal; doesn't read lessons.md, proposed: "rank matches by both telemetry AND lesson-tagged relevance" }
  D11_subagent: { state: n/a-for-kind }
  D12_failure: { state: partial, nano: "skill-router:74-78 + :88 (privacy: local only)", finding: no explicit failure-modes section }
  D13_observability: { state: absent, nano: "no write; reads telemetry but logs nothing", high: "below floor — invisible runs", finding: "router never records what it routed to", proposed: "append match->choice to telemetry so the operator-relation thread learns" }
  D14_necessity: { state: absent, proposed: "OPTIONAL (discovery aid); gap = 144-skill cognitive load with no router" }
peer_comparison:
  strongest_peer_in_cohort: context-warm
  this_component_depth: below-bar (D2 absent, D3 loose, D5 absent, D13 absent, D4 name-drift)
  uplift_needed: Status protocol + structured output + observability write + scrub /match from body + pack-scoped ranking
operator_decision_required: no
priority: high
```

---

## Cohort summary

**18 components, 14 dimensions.** This cohort earns its "highest-fragmentation" label:

1. **Storage-root schism (CF-1)** — four roots for the same data; **two live producer/consumer
   breakages** (context-save→context-dump, context-save→context-warm-sessions) where a
   consumer cannot find what its named producer writes. This is the cohort's headline.
2. **Config schism (D3)** — `~/.gstack/`, `~/.lintel/profile.yaml`, `~/.lintel/config.yaml`,
   `.lintel/state/`, plus `context-state.json` vs `00-state.md`. Five-way drift inside one cohort.
3. **Dialect split (CF-4)** — gstack-prose tail vs lintel Status-protocol tail; ~7 skills
   below the machine-readable-tail floor.
4. **Brief Forge should-fire is dense here (D9)** — designed-not-built, but moments 1
   (pair-agent, codex), 2 (context-warmup), 4 (save/snapshot/dump/warm-sessions), and 5
   (all) are all present and un-gated. pair-agent + codex are the most-built proto-gates;
   several skills already contain proto-evaluators (customer-PII scans, domain allowlists,
   IGNORE lists) that should be formalized as named Brief Forge evaluators rather than
   reinvented.
5. **CF-3** — zero of 18 declare the canonical `brief_forge_handoffs:` frontmatter field.
6. **Necessity (D14) absent in all 18** — no REQUIRED/RECOMMENDED/OPTIONAL + gap-if-skipped.

**Strongest peer:** `context-warm` (full uniform stack + base-skill spine).
Runner-up: `context-warm-customer` (best D7/D13).
pair-agent sets the **D11** bar; codex sets the **D3-out / D4** bar.

**Weakest peer:** `skill-router` (no tail, no checkpoint, no observability, loosest
contract, body/frontmatter name drift).

**operator_decision_required: 6** — context-save (CF-1 root), context-snapshot
(snapshot-vs-save consolidation), context-dump (CF-1/CF-2), context-warm-sessions
(CF-1/CF-2), context-warmup (state-file naming), context-budget (mode_envelopes home),
context-budgetwatch (config + hook duplication). *(7 records flag yes; context-dump and
context-warm-sessions share the same CF-1/CF-2 decision, so 6 distinct decisions.)*
