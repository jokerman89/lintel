# Uniformity-as-contract

The system-wide uniformity audit (`.claude/engineering/audits/lintel-uniformity-*`) defined 14
uniformity dimensions (D1–D14) and ranked the top-20 findings. The audit was a
one-time snapshot. This document turns that snapshot into a **continuous,
machine-checked contract** — the parked `/autoplan` recommendation.

The contract has three moving parts, and this doc is the first:

| Part | Artifact | Role |
|---|---|---|
| Contract (this doc) | `docs/concepts/uniformity-contract.md` | Defines the per-kind floor + what is tracked above it |
| Floor enforcement | `tests/shape/uniformity-coverage.sh` | Gate-M3 shape-test; HARD-FAILS only on the floor |
| Living dashboard | `bin/li-uniformity` → `.claude/engineering/audits/uniformity-matrix.md` | Regenerable coverage matrix; replaces the static findings register |

References: `.claude/engineering/audits/lintel-uniformity-MASTER.md` (top-20),
`.claude/engineering/audits/lintel-uniformity-cross-X5-necessity.md` (the necessity denominator
and the REQUIRED/STRONGLY_RECOMMENDED/OPTIONAL distribution this contract
adopts).

---

## The core principle: per-kind floor, not global max

The audit reviews (`lintel-uniformity-REVIEW.md`,
`lintel-uniformity-REMEDIATION-REVIEW.md`) converged on one design rule:

> **Uniformity is a per-kind floor, not a global maximum.**

A read-only `warn-only` hook is *not* expected to declare `recovery:` (D6) —
it has nothing to recover; it observes and warns. A `workflow_root: true` skill
*is* expected to declare `necessity:` (D14) and `navigation:`, because an
orchestrator (cycle, orientator, autoplan) routes on those fields. Demanding
all 14 dimensions of every component would be uniformity-as-bureaucracy: it
would force meaningless declarations and bury the load-bearing ones.

So the contract is **kind-aware**. For each component KIND we define which
dimensions it MUST declare (the floor), which are OPTIONAL (tracked, adoption
is encouraged but not mandated), and which are N/A-for-kind (with a reason).

Two enforcement levels:

- **Floor (required)** — enforced *mechanically* by `tests/shape/uniformity-coverage.sh`.
  A floor miss is a HARD-FAIL (CI red). The floor is deliberately small so it is
  always satisfiable: it is the set of declarations an orchestrator genuinely
  cannot work without.
- **Above the floor (optional / tracked)** — *not* mandated. Adoption is
  **tracked**, not enforced, by `bin/li-uniformity` → `uniformity-matrix.md`.
  The matrix shows per-kind adoption %, so drift is visible and improvement is
  measurable, without making CI red over the long tail.

This is the subtraction-aligned route the X5 doc argues for: one small enforced
floor replaces ~148 prose `When NOT to use` sections as the machine-readable
source of truth, while the optional ring stays *visible* rather than *mandatory*.

---

## The 14 dimensions

| Dim | Name | Frontmatter signal(s) this contract tracks |
|---|---|---|
| D1 | head (orientation) | `name`, `layer`/`category`/`tier` |
| D2 | tail (status/observability close-out) | `observability:`, status-protocol prose |
| D3 | in/out contract | `inputs:` / `outputs:` / envelope use |
| D4 | entry-points | `entry_points:`, `triggers` (in `navigation:`) |
| D5 | checkpoints | `checkpoints:` |
| D6 | recovery | `recovery:` |
| D7 | pack-influence | `pack_influence:` |
| D8 | frontmatter completeness | the required-fields set (`frontmatter-lint-all.sh`) |
| D9 | brief-forge | `brief_forge_handoffs:` |
| D10 | lessons | `lessons_consulted:` / lessons-consult step |
| D11 | subagent-delegation | `delegates_to:` / subagent block |
| D12 | failure-mode | `failure_mode:` / `gap_if_skipped:` |
| D13 | observability | `observability:` / audit-line |
| D14 | necessity | `necessity:` + `gap_if_skipped:` |

The matrix and the shape-test track the **frontmatter-declarable** subset of
these — the dimensions a machine can verify by reading a YAML field. Some
dimensions (D1 head, D8 frontmatter completeness) are already enforced by
`frontmatter-lint-all.sh` and are not re-checked here; this contract layers the
*workflow-orchestration* dimensions (D14 necessity, navigation/D4, D9
brief-forge, D7 pack-influence, D12/D6 failure/recovery, D13 observability) on
top.

---

## Component kinds

KIND is **directory- and frontmatter-derived** (the shape-test computes it the
same way):

| Kind | How it is detected |
|---|---|
| `workflow_root skill` | `skills/*/SKILL.md` with `workflow_root: true` |
| `regular skill` | `skills/*/SKILL.md` without `workflow_root: true` |
| `agent` | `agents/*/*.md` (excluding README / _TEMPLATE) |
| `block-hook` | `hooks/shared/*/HOOK.md` with `tier: JUSTIFIED-BLOCK` or `HARD-RULE` |
| `warn-hook` | `hooks/shared/*/HOOK.md` with `tier: warn-only` / `surface-only` |
| `lifecycle-hook` | `hooks/shared/*/HOOK.md` with `tier: lifecycle` (job-begin/end) |
| `pack` | `packs/*/pack.yaml` |

(`lifecycle-hook` is split out from `warn-hook` only so the matrix doesn't
penalise job-begin/job-end for lacking warn-hook semantics; for floor purposes
it behaves like a warn-hook — no `necessity:` floor.)

---

## The contract: kind × dimension × {required | optional | n/a}

Legend: **R** = required (floor, mechanically enforced) · **O** = optional
(tracked, not mandated) · **n/a** = not applicable for this kind (with reason).

| Dimension (field) | workflow_root skill | regular skill | agent | block-hook | warn-hook | pack |
|---|---|---|---|---|---|---|
| D14 necessity (`necessity:`) | **R** | O | O | **R** | O | O |
| D12 gap-if-skipped (`gap_if_skipped:`) | **R** | O | O | **R** | O | O |
| D4 navigation (`navigation:`) | **R** | O | n/a¹ | n/a² | n/a² | O |
| D9 brief-forge (`brief_forge_handoffs:`) | O | O | O | n/a² | n/a² | n/a³ |
| D7 pack-influence (`pack_influence:`) | O | O | O | O | O | n/a⁴ |
| D6 recovery (`recovery:`) | O | O | n/a⁵ | n/a⁶ | n/a⁶ | n/a⁷ |
| D5 checkpoints (`checkpoints:`) | O | O | n/a⁵ | n/a⁶ | n/a⁶ | n/a⁷ |
| D13 observability (`observability:`) | O | O | O | O | O | n/a⁷ |
| D10 lessons (`lessons_consulted:`) | O | O | O | n/a⁶ | n/a⁶ | n/a⁷ |
| D11 delegation (`delegates_to:`) | O | O | n/a⁸ | n/a⁶ | n/a⁶ | n/a⁷ |

The **floor** (the only R cells) is intentionally tiny:

- **`workflow_root: true` skill** MUST declare `necessity:` and `gap_if_skipped:`
  and `navigation:`. Rationale: an orchestrator routes on these. `navigation:`
  is already independently enforced by
  `tests/shape/workflow-root-has-navigation.sh`; this contract adds the
  `necessity:` floor.
- **block-hook** (`JUSTIFIED-BLOCK` / `HARD-RULE`) MUST declare `necessity:`
  (and `gap_if_skipped:`). Rationale: a hook that *blocks* an operator action
  must state why it is justified and what breaks if it is skipped/overridden —
  that is the override-with-audit contract.

Everything else is **O** or **n/a**. The shape-test HARD-FAILS only on the two
R rows above (necessity floor for workflow_root skills + block-hooks). The
matrix tracks every cell.

### N/A reasons (per-kind floor justification)

1. **agent navigation n/a** — agents are dispatched by the orientator /
   DISCOVER via `description:` affinity, not by a self-declared `navigation:`
   block. Their entry-point is the dispatcher, not a slash-command surface.
2. **hook navigation / brief-forge n/a** — hooks fire on tool events
   (PreToolUse/PostToolUse), not as workflow steps. They have no navigation
   surface and produce no brief-forge hand-off.
3. **pack brief-forge n/a** — packs are declarative config consumed by the
   resolver; they don't emit hand-offs. (Packs *configure* which brief-forge
   evaluators fire, via `compliance:`, but don't declare `brief_forge_handoffs:`
   themselves.)
4. **pack pack-influence n/a** — a pack *is* the pack-influence source; it can't
   be influenced by itself.
5. **agent recovery / checkpoints n/a** — agents are single-shot subagent
   invocations (one task per agent, per the subagent guide). They have no
   multi-step checkpoint/recovery state to declare; the *calling skill* owns
   checkpointing.
6. **block/warn-hook recovery / checkpoints / lessons / delegation n/a** — a
   hook is a single synchronous gate. It blocks or warns and returns. It has no
   resumable state, consults no lessons, delegates to no subagent.
7. **pack recovery / checkpoints / observability / lessons / delegation n/a** —
   packs are static config, not executable workflow steps.
8. **agent delegation n/a** — per the subagent discipline ("one task per
   subagent", "no fixes from review subagents"), agents do not themselves
   delegate to further subagents.

A **warn-hook deliberately has no `necessity:` floor** — this is the canonical
example from the audit reviews: a read-only observe-and-warn hook is not
expected to carry recovery/necessity machinery. Where a warn-hook *does* carry
`necessity:` (e.g. `no-direct-main-push`, `no-production-mutation-without-auth`),
that is *adoption above the floor* — tracked and welcome, never required.

---

## Enforcement vs tracking — the boundary

| | Floor (R cells) | Above the floor (O cells) |
|---|---|---|
| Where defined | this doc, the R cells | this doc, the O cells |
| How verified | `tests/shape/uniformity-coverage.sh` HARD-FAIL | `bin/li-uniformity` matrix adoption-% |
| CI behavior | red on miss (exit 1) | always green; reports % only |
| Intent | "an orchestrator cannot work without this" | "more uniformity is better; make drift visible" |

The shape-test ALSO *reports* (non-failing) the adoption % of every tracked
field per kind, so a single test run gives both the pass/fail gate and the
tracking snapshot. The matrix generator produces the durable, browsable version.

---

## Why this is the mechanism that makes uniformity continuous

The audit was a register of 144+ findings that goes stale the moment a component
is added or changed. The X5 doc names the recurring anti-pattern: *a concept
declared in prose but never promoted to a parseable, consumed field.* This
contract closes that for the uniformity audit itself:

- the **floor** is now a parseable field set, consumed by a CI gate;
- the **matrix** is regenerated from frontmatter on every run, so it can never
  silently drift from reality (the same regenerable-artifact discipline as
  `bin/li-wiki-gen` and the L-003 counts lesson);
- a new component automatically appears in the matrix and is automatically held
  to its kind's floor.

The static findings register (`.claude/engineering/audits/lintel-uniformity-*`) remains the
*historical record* and the source of the dimension definitions. The matrix is
the *living dashboard*.

## See also

- `tests/shape/uniformity-coverage.sh` — the Gate-M3 floor enforcer + adoption reporter
- `bin/li-uniformity` — the regenerable matrix generator
- `.claude/engineering/audits/uniformity-matrix.md` — the generated living dashboard
- `.claude/engineering/audits/lintel-uniformity-MASTER.md` — top-20 findings
- `.claude/engineering/audits/lintel-uniformity-cross-X5-necessity.md` — the necessity denominator + value distribution
- `tests/shape/workflow-root-has-navigation.sh` — the sibling floor for `navigation:`
- `tests/shape/frontmatter-lint-all.sh` — the D1/D8 frontmatter-completeness floor
