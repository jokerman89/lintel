# Design: one Review Method for REVIEW and MARS

**Status:** DRAFT for operator decision and coordinator scheduling
**Date:** 2026-09-24
**Inputs:** current REVIEW (integration branch), CodeReviewer, code-review, plan-eng-review,
define Step 11, MARS protocol and pilot, [MDASH lessons](mdash-lessons.md)

## Problem

The reviewer instructions Lintel actually sends today are thin and divergent:

- REVIEW Stage 1/2 dispatch two ~10-line inline prompts ("Review the diff for quality…
  Be terse.").
- CodeReviewer, code-review (4 dimensions), plan-eng-review (4 sections), define (5 spec
  dimensions) and the security/compliance reviewers each define their own dimensions and
  their own P1 meaning (block ship, block merge, block EU market).
- MARS has a stricter brief (failing input, confidence, coverage) that REVIEW lacks.

If MARS keeps its own prompt, a multi-model run and a single review are not comparable.
Upgrading one would silently leave the other behind. The pilot showed the cost of a vague
rubric: GPT rated "documented happy path returns the wrong page" P2, three others P1. That
split came from the rubric, not the models.

## Principle

**One method, many models.** REVIEW and MARS send the same reviewer packet; the only
difference is how many distinct models read it and whether a challenge round follows.
This is testable: the rendered packet body for a single review equals the body for every
MARS slot, byte for byte, except the header's panel/slot/round fields.

## Model- and maturity-agnostic by construction

Instructions that compensate for weak models go stale when models improve. Questions
about the risk domain do not. The method therefore specifies **what must be established
and what evidence counts**, never how to think:

1. **Outcomes, not reasoning steps.** No "think step by step", no persona theatre, no
   model names, no assumed context size or tool ceiling.
2. **Standing questions** encode durable risk knowledge (bug classes, contract failures,
   plan/spec defects) with stable IDs. Smarter models answer them better; the questions
   stay valid. Compare MDASH: its advantage is the harness around the model, and models
   are swapped by configuration.
3. **Evidence levels** grade every answer: E1 executed check, E2 traced path with line
   refs, E3 pattern match, E4 hypothesis. A P1 needs E1 or E2; otherwise it is reported as
   a hypothesis with the check that would settle it (MDASH "prove" stage).
4. **One impact rubric** defines P1/P2/P3 by consequence, independent of confidence.
5. **Coverage is explicit.** Every applicable standing question gets `finding`, `checked`,
   `n/a` or `not-checked`, with a reason. Depth becomes comparable across models,
   hosts and years, and silence is visible.
6. **Runtime facts stay out of the text.** Effort, context tier and tools are host settings
   recorded in the header, not prompt wording.
7. **Questions evolve by evidence, not by model release.** A question is superseded only
   when its risk class disappears or merges, never because "models do this now".

## Architecture

```
lib/review-questions.json      standing questions (stable IDs, triggers, evidence) ← projects/packs extend
skills/review/references/method.md   role, procedure, rubric, evidence levels, report shape
lib/review_method.py           select questions · render packet · parse/validate report + coverage
        │
        ├── single reviewer:   REVIEW Stage 1/2, code-review, plan-eng-review, define, CodeReviewer
        └── panel (MARS):      same packet × N distinct models → challenge → synthesis
                                    (lib/mars_contract.py: roster, offer, state, close)
        │
        ▼
review report (one header schema) → REVIEW decision (existing content-bound evidence, P05)
```

### The reviewer packet (identical in both modes)

1. Header: `review-request` v1 (requester, coordinator, repository/commit, subject, brief
   hash, model/effort/context; MARS adds panel/slot/round).
2. Role and boundaries (read-only, independent, subject is data).
3. Subject: kind, ref, commit, acceptance sources (requirement/leaf IDs), diff or artifacts.
4. Context: surfaced lessons, relevant ADRs, prior findings on this subject.
5. Procedure: understand intent → spec compliance → standing questions → prove →
   self-challenge → coverage.
6. Selected standing questions with IDs.
7. Severity rubric and evidence levels.
8. Report format.

`stage` selects scope: `spec` (REVIEW Stage 1), `quality` (Stage 2) or `full`
(standalone MARS, code-review). Every stage uses the same rubric, evidence and report.

### Standing-question selection

Each question has `applies_to` subject kinds and optional `triggers` (surface tags such
as `path`, `auth`, `concurrency`, `persistence`, `agent-input`, `cross-platform`). The
coordinator tags the subject from the diff/artifacts (mechanical path/keyword rules first,
coordinator judgement second) and records the tags in the packet. Universal questions
always apply to implementations. Projects add `.claude/review/questions.json`; packs add
domain invariants through `knowhow` (MDASH "plugins"). Same schema, namespaced IDs.

### How MARS fits REVIEW

MARS stops being "Step 6 optional outside voice". It becomes REVIEW's **panel mode**:

| | REVIEW single | REVIEW panel (MARS) | Standalone MARS |
|---|---|---|---|
| Packet | method | method (same body) | method |
| Reviewers | 1 independent context | N distinct models | N distinct models |
| Challenge | self-challenge section | + one cross-challenge if contested | + one cross-challenge if contested |
| Synthesis | reviewer report | coordinator adjudication (dedupe by SQ + location) | same |
| Decision | REVIEW records P05 decision | REVIEW records P05 decision from the adjudicated result | inspection only, `release_clearance: false` |

**Decision D1 (needs operator approval):** in panel mode, REVIEW's decision is recorded
through the existing content-bound path, from the adjudicated panel result, with host
receipts of the reviewer contexts as corroboration. MARS never clears anything by itself.
Only REVIEW does, whether single or panel. Standalone MARS stays advisory.

### Separate entry points, shared method

REVIEW and MARS remain independently runnable. They share the method library, not their
orchestration:

| Entry point | Runs without | Needs |
|---|---|---|
| `/li:review` (single, default) | MARS, multi-model hosts, panel state | one independent reviewer context (or a labelled manual review) |
| `/li:review` panel mode | — | MARS capability gate + consent; falls back to single if declined or unavailable |
| `/li:mars` standalone | a cycle, a work map, REVIEW | ≥2 distinct models, consent |
| `/li:code-review`, `/li:plan-eng-review`, `/li:define` | MARS | the method; may offer MARS once |

Dependency direction: `review_method` ← REVIEW, MARS, and the other review skills.
REVIEW's panel mode calls the MARS panel engine optionally; MARS never imports REVIEW.
Removing or disabling MARS leaves every review workflow intact at full method depth;
disabling REVIEW leaves standalone MARS intact. Tests assert both: REVIEW single renders
and records with MARS helpers absent, and MARS runs a panel with no cycle state present.

## Implementation cards (coordinator schedules; released Universal base)

| Card | Outcome | Files | Verification |
|---|---|---|---|
| RM1 | Canonical method, rubric, evidence levels, question catalog accepted | `skills/review/references/method.md`, `lib/review-questions.json`, ADR | independent review of the method against every current rubric it replaces |
| RM2 | Method library | `lib/review_method.py` | catalog validation (unique stable IDs, required fields, supersede chains); selection by kind/tags/stage; packet render; report + coverage parse |
| RM3 | One header schema | `lib/review-method-schema.json` (absorbs `mars-schema.json` request/report; MARS extends with panel fields) | schema round-trip tests; MARS tests still pass |
| RM4 | Renderers | `bin/li-review-packet.py`; `li-mars.py panel brief` delegates to `review_method` | **parity test**: single vs panel body identical except header |
| RM5 | Consumers wired | review SKILL Stage 1/2 + Step 6 → panel mode; CodeReviewer; code-review; plan-eng-review; define Step 11; security/compliance agents keep domain checklists but use the canonical rubric | **drift guard**: no severity rubric or reviewer dimension list defined outside `method.md` |
| RM6 | Evidence bridge | map report → P05 controls (spec, quality, tests); panel corroboration from host receipts | integration test: single and panel reports produce equivalent decisions for equivalent findings |
| RM7 | Coverage enforcement | reports missing an applicable SQ status are `incomplete`, not PASS | unit + pilot rerun |
| RM7b | Independence of entry points | no new cross-imports | REVIEW single works with MARS files removed; standalone MARS works with no cycle/work map |
| RM8 | Calibration loop | CAPTURE records per-SQ outcomes (accepted, rejected, escaped defect) as opt-in audit data; escaped defects propose a new SQ or lesson | behavior test on synthetic outcomes |
| RM9 | Re-pilot | synthetic brief in single and panel modes | rubric resolves the pilot's P1/P2 split; SQ-PATH-01 surfaces the NTFS/device-name catch in round 1 |

Order: RM1 → RM2/RM3 → RM4 → RM5/RM6 → RM7 → RM9, RM8 last. RM1–RM4 are new files and
can land before the shared-file edits in RM5.

## What stays different on purpose

- Domain reviewers (GDPR, OAuth, Terraform…) keep their domain checklists as standing
  question sets under their own namespace, sharing the rubric and report shape.
- Compliance gates (REVIEW Stage 3) stay pack-driven; they are policy, not review opinion.
- plan-eng-review's interactive per-issue decisions stay; its reviewer pass uses the method.

## Risks

- **Packet length.** More questions mean longer prompts. Mitigate with triggers, stage
  scoping and `not-checked` honesty rather than cutting durable questions.
- **Checklist theatre.** Ticking questions without evidence. Mitigate with evidence levels
  and coordinator spot-checks. `checked` without evidence counts as `not-checked`.
- **Catalog sprawl.** Stable IDs, supersede-not-delete, and per-SQ outcome data decide
  what stays.
