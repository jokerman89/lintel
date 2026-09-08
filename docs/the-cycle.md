# The cycle

Lintel's main workflow. It turns a raw request into shipped, captured work through nine phases,
each of which is its own skill, produces its own artifact, and declares what it costs you to skip.

```
SENSE → SCOPE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE
```

Run the whole thing with `/li:cycle`, a subset with `--mode` or `--from`/`--to`, or any single phase
on its own (`/li:define`, `/li:review`, …). This page explains what each phase actually does, where
the gates are, and how the harness keeps your position when the session gets long.

---

## Why nine phases

The phases are not ceremony. Each one exists because skipping it has a specific, observed failure
mode — which is why every phase skill declares a machine-checkable `gap_if_skipped` field rather
than a vague "this is important".

The shape is deliberately front-loaded. Five of the nine phases happen before a line of code is
written, because the expensive failures in agent-driven work are not bad code — they are correct
code built against the wrong premise, discovered three hours later.

---

## Phase by phase

### 1. SENSE — read the situation

A silent, read-only diagnostic that runs before any decision. It detects operator intent, the active
pack and its compliance mode, the active role, any cycle state a prior session left behind, and the
current context budget. It ends with a mode recommendation.

**Produces** a SENSE report and a *scale pre-read* — a first guess at how big this is, plus a
`bimodal` flag when the request could plausibly be small or large.

**Gate** none. SENSE is cheap and never blocks.

**Skipping it costs** every downstream phase is mis-scoped, and a cycle left half-finished by the
previous session gets silently resurrected or silently ignored.

---

### 2. SCOPE — size the request

Light, skippable, and mostly silent. SCOPE turns a raw ask into a sized one. It fires **at most one**
clarifying question, and only when SENSE flagged the request as genuinely bimodal — the discipline
is that ambiguity gets resolved once, up front, not re-litigated in every later phase. It can also
override a confidently-wrong route (a request that looks like a one-line deploy but is really a full
cycle).

**Produces** `scope.md` — resolved size, depth schema, chosen reading, and any route override. The
depth schema is what PLAN later uses to pick its work-breakdown template.

**Gate** at most one question, only when bimodal. Silent on clearly small work.

**Skipping it costs** scale ambiguity is never resolved and PLAN has no depth schema to select
against.

---

### 3. DEFINE — lock the design

The forcing-question phase. DEFINE clarifies intent, locks premises, forces alternatives to be
stated rather than assumed, and picks the wedge — the specific first cut of the problem that the
rest of the cycle builds. It runs under the active role's lens.

**Produces** an **approved** design document. Not a draft.

**Gate** hard. The cycle does not proceed past DEFINE until you approve the design.

**Skipping it costs** PLAN and BUILD consume ad-hoc prose with no locked premises, so nothing
downstream can be checked against anything.

---

### 4. DISCOVER — gather before planning

Read-only. Maps the codebase around the wedge, surfaces the decision records and past lessons that
touch it, and identifies the skills, agents and patterns already in the repo that the work should
reuse rather than reinvent.

**Produces** `discover-report.md`.

**Gate** none — it mutates nothing.

**Skipping it costs** PLAN flies blind, and the work reinvents or contradicts decisions already made
and written down.

---

### 5. PLAN — break it into executable work

PLAN writes the **cold-executor trio**, all three born together:

| File | Holds |
|---|---|
| `plan.md` | short checkable tasks grouped into bounded work packages with owners and acceptance evidence |
| `spec.md` | what "done" means for each task |
| `prompt.md` | enough context for a fresh agent with no history to execute it |

Task granularity is hard-checked. PLAN also produces the cost estimate that the pre-BUILD gate uses.

**Produces** the trio, plus `tasks_count` and a labelled token estimate written to the state ledger.

**Gate** **mandatory approval pause.** PLAN does not hand off to BUILD on its own.

**Skipping it costs** BUILD runs against an unwritten, unreviewed plan.

---

### 6. BUILD — implement

Each **work package** gets one implementer with the full text of its short member tasks.
It passes two review stages: spec compliance for every leaf and their integration, then quality.
Review depth follows aggregate package complexity; substantive packages require independent
review and mechanical packages can be reviewed by the coordinator inline. Every leaf retains
its acceptance evidence. Missing evidence or a blocked leaf keeps the package open.

**Produces** implemented code in atomic commits.

**Gate** the **cost-estimate gate fires before BUILD starts**, presenting the task count and the
token estimate — honestly labelled `UNCALIBRATED` until the estimator has recorded actuals for work
of that size.

**Skipping it costs** no implementation is produced.

---

### 7. REVIEW — adversarial, three stages

1. **Spec compliance** — does it do what `spec.md` said?
2. **Code quality** — would a staff engineer approve this?
3. **Pack compliance** — does it satisfy the active pack's gates?

A P1 finding blocks SHIP. The review is deliberately adversarial: a reviewer that agrees with the
implementer is not a review.

**Produces** review and compliance reports.

**Gate** P1 findings block SHIP.

**Skipping it costs** unreviewed code reaches SHIP with no signal at all.

---

### 8. SHIP — land it

Pull request by default. SHIP runs final compliance hard-stops, applies the active pack's voice
gates to anything customer-facing, validates CI, and writes an audit record.

**Produces** a PR, release notes, and an audit-log entry.

**Gate** compliance hard-stop when the active pack's compliance mode is `hard`. Direct-push to the
default branch is never the default path.

**Skipping it costs** no deploy validation, no rollback path, no audit trail.

---

### 9. CAPTURE — make it durable

The phase that makes the next session cheaper. CAPTURE records lessons from any correction, drafts a
decision record for any non-trivial decision, appends the evolution log, updates working state, and
reaffirms the cold-executor trio against what was actually built.

**Produces** lesson entries, an ADR, evolution-log and working-state updates.

**Gate** none, but it is where the compounding happens.

**Skipping it costs** cross-session continuity is lost and the next operator re-derives everything.

---

## Modes — you rarely need all nine

| Mode | Phases | Reach for it when |
|---|---|---|
| `hotfix` | SENSE → BUILD → REVIEW → SHIP | the bug is known and the fix path is clear |
| `internal-tool` | all nine, lighter REVIEW | ordinary feature work |
| `research-dive` | SENSE → DEFINE → DISCOVER | explore and understand, no code yet |
| `meta-infra` | all nine, heavier REVIEW and CAPTURE, plus gates M1–M4 | the change touches the harness itself |
| `auto` | SENSE recommends, you confirm | you are not sure which fits |

A pack can contribute its own modes with their own voice and compliance posture. The neutral spine
ships the five above.

**Composite shortcuts** are pure delegators to a subset:

```
/li:fix                SENSE + BUILD + REVIEW + SHIP
/li:research           SENSE + DEFINE + DISCOVER
/li:plan-and-build     PLAN + BUILD
/li:review-and-ship    REVIEW + SHIP + CAPTURE
```

---

## The gates, in one list

Five gates are always enforced, whatever the mode:

1. **Cost estimate before BUILD** — the token-heavy phase never starts unconfirmed.
2. **Approval at the end of PLAN** — a mandatory pause, not a notification.
3. **Three-stage REVIEW** — spec, then quality, then compliance.
4. **Compliance hard-stop in SHIP** — when the active pack sets `hard`.
5. **Two-stage review per BUILD work package** — complexity-gated, with every leaf covered.

`meta-infra` mode adds four more, because changes to the harness ripple into every downstream cycle:

| Gate | Where | What it demands |
|---|---|---|
| **M1** structure-impact | DEFINE | an evolution-log entry: what changed, backward compat, migration path, verification, rollback |
| **M2** compatibility audit | REVIEW | a mechanical sweep for changed frontmatter contracts, renamed or moved skills/agents/hooks, changed defaults, changed shared-helper signatures. RED requires an explicit override |
| **M3** shape tests | REVIEW | the structural-contract suite green. Any failure blocks SHIP |
| **M4** future-operator clarity | CAPTURE | a recap a cold operator can act on: every migration to run, every new convention, every deprecated path |

---

## Auto-mode cannot walk through a one-way door

`--auto` decides the recommended option at reversible gates so you are not confirming trivia. It
still stops at irreversible ones — and that distinction is **mechanical, not a promise in prose**:

```bash
source lib/auto-decide.sh
if is_one_way_door "$decision_text"; then ask_operator; else auto_decide_recommended; fi
```

`is_one_way_door` matches a deliberately broad set of irreversible classes — delete, drop, truncate,
migrate, schema change, production, force-push, rewrite history, secret, rotate key, rename a skill
or agent, breaking change — regardless of how the decision was phrased. A false positive costs one
question. A false negative is the failure being guarded against, so the guard errs wide.

---

## Keeping your position

Long sessions lose the thread. The cycle's answer is a state ledger plus three hooks, so position
survives compaction, a fresh session, and your own attention.

Every phase appends one mechanical line:

```bash
source lib/state.sh
state_append DEFINE DONE next=DISCOVER note="design approved"
```

Then:

- **`session-digest`** (SessionStart) re-injects the active pack, recent lessons, open jobs and
  recent decision records — session two starts knowing what session one learned.
- **`cycle-position-inject`** (UserPromptSubmit) re-asserts your position at the start of every
  turn.
- **`cycle-incomplete-warn`** (Stop) fires when a turn ends mid-cycle, so work never goes silent.

And every phase closes with the same footer, so you always know where you are and what the one
logical next action is:

```
Lintel cycle · mode meta-infra · done ✅ · skipped ⊘ · here 📍 · pending ▢

SENSE ✅ → SCOPE ✅ → DEFINE ✅ → DISCOVER ✅ → PLAN 📍 → BUILD ▢ → REVIEW ▢ → SHIP ▢ → CAPTURE ▢

▶ Awaiting your answer: Proceed with BUILD? [Y/n/edit-plan]
```

Skipped phases render `⊘`, so a `hotfix` run shows honestly that DEFINE and PLAN were never run.

---

## Hopping in, resuming, and looking before you leap

```
/li:cycle --from PLAN        enter at PLAN — dependencies are verified first
/li:cycle --to REVIEW        stop before SHIP
/li:cycle --skip DISCOVER    drop a phase deliberately
/li:cycle --dry-run          print the phase list and cost forecast, execute nothing
/li:resume                   read the ledger and pick up at the next phase
/li:status                   where am I right now
```

Hop-in verifies dependencies rather than trusting you: BUILD needs a plan, REVIEW needs a diff, SHIP
needs a REVIEW pass. If the dependency is missing, the cycle says so instead of running anyway.

---

## When a phase blocks

A phase that cannot complete returns `BLOCKED` rather than continuing. The orchestrator surfaces the
reason and offers four moves:

- **Retry** with the same inputs
- **Skip** to the next phase, writing a stub and an issue-log entry so the gap is recorded
- **Loop back** to an earlier phase — a blocked BUILD usually means PLAN was wrong
- **Abort**, saving state so `/li:resume` can pick it up later

Silently continuing past a blocked phase is the one thing the orchestrator will not do.

---

## A worked example

This documentation set was itself produced by a `meta-infra` cycle. The trace:

| Phase | What actually happened |
|---|---|
| SENSE | Read repo state: 250 commits, 130 documentation files, branch 16 commits ahead of the default branch, no release tag on the current line |
| SCOPE | Sized L, depth schema `phased`; three workstreams identified |
| DEFINE | Three decisions forced and locked: rewrite commit messages in place, relocate internal engineering artifacts out of the public tree, release as `v0.9.0-beta` |
| DISCOVER | Mapped every inbound reference to the directories about to move — the dependency that broke a previous attempt at the same move |
| PLAN | 33 tasks across four waves, written to `.claude/plans/todo.md`, approval gate before BUILD |
| BUILD | Waves executed; a parallel read-only recon pass produced the reference map, link audit, truth audit and sanitation map |
| REVIEW | M2 compatibility audit, M3 shape suite, adversarial review of the result |
| SHIP | Tag and release notes |
| CAPTURE | Lessons recorded, evolution-log entry, working state updated |

The point of the example is not the outcome. It is that the trace exists at all — every phase left
an artifact you can read afterwards.

---

## See also

- [Getting started](getting-started.md) — install and first run
- [Architecture](architecture.md) — how the cycle sits inside the spine-and-packs model
- [Glossary](GLOSSARY.md) — trio, wedge, pack, depth schema
- [Skill catalog](../skills/CATALOG.md) — every phase skill and its options
