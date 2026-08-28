# Cross-cutting pass X5 — necessity + gap-if-skipped coverage

**Pass:** X5 of the Lintel uniformity audit
**Standard:** `.claude/engineering/audits/lintel-uniformity-audit-prompt.md` §"X5 — Necessity + gap-if-skipped coverage" + dimension **D14**
**Inputs synthesized:** all 8 cohort findings files (`lintel-uniformity-findings-cohort1..8`)
**Date:** 2026-05-29
**Rule:** NO-CUT. Every recommendation adds a declaration; nothing is removed.

---

## 1. The synthesized finding

D14 (necessity declaration) is the most uniformly-absent dimension in the entire audit. Across the 8 cohorts:

| Cohort | Components | D14 state |
|---|---|---|
| 1 — phase-core | 13 (8 phase + 5 composite) | **0 declare it.** All necessity is implicit prose ("always first in cycle", `When NOT to use`). |
| 2 — planner sub-chain | 7 | 4 state necessity in *prose* ("required review", "optional but recommended"); **0 in a frontmatter field**; 3 absent entirely. |
| 3 — handoff / Brief Forge | 18 | **0 declare it.** Every record carries a `proposed: necessity` line. |
| 4 — agents | 83 | **0 declare it.** Template-level absence (Part A D14). |
| 5 — hooks | 19 | Only the 4 newest (job×3, frontend-surface) carry *de-facto* necessity framing; 15 older hooks have rationale prose but **no stamp**. |
| 6 — eng domains | 5 domains | SC enforces necessity only *implicitly* via downstream-block; **declared field nowhere** (C6-F5). |
| 7 — packs / roles | 8 role skills + 3 role files | **0 role skills declare it** (implicitly OPTIONAL). Role files carry rich schema but no necessity. |
| 8 — cross-cutting | 6 layers | Necessity n/a at the layer level, but every consuming phase skill inherits the cohort-1 gap. |

**Total components where `necessity:` + `gap_if_skipped:` would be load-bearing if added: 144** (see §4 for the full denominator and the exclusions). The Architect pattern declares per-section REQUIRED / STRONGLY RECOMMENDED / OPTIONAL plus the gap-if-skipped; Lintel declares neither, anywhere, in any machine-readable field.

**Why this matters (the load-bearing argument).** Necessity is not cosmetic metadata. It is the field a *workflow recommender* (the orientator, cycle's mode-presets, autoplan's chain composition, DISCOVER's dynamic dispatch) needs to answer "can the operator safely skip this step?" Today that judgement is buried in prose `When NOT to use` sections that no orchestrator parses. The danger is **silent degradation**: a component skipped inside a workflow where its absence quietly weakens the result with no signal. That class — *skip silently degrades* — is exactly where necessity is most load-bearing, and is the selection criterion for the table below.

---

## 2. Headline table — the highest-leverage ~18 components

Selection criterion: the component sits inside a workflow where skipping it **silently degrades** the downstream result (no error, no gate, just a worse outcome the operator can't see coming). Ranked by danger of silent degradation.

| # | Component | Proposed necessity | Proposed `gap_if_skipped` (one line) | Priority |
|---|---|---|---|---|
| 1 | `skills/plan/SKILL.md` | REQUIRED (unless trivial hotfix) | BUILD executes against an unwritten/unreviewed plan; the caller-relyable trio contract never exists, so CAPTURE and cold executors have nothing to read. | high |
| 2 | `skills/review/SKILL.md` | REQUIRED (gate before SHIP) | Unreviewed code reaches SHIP; compliance/security gates never fire; ship-ready verdict is asserted without evidence. | high |
| 3 | `skills/build/SKILL.md` | REQUIRED | No shippable artifact is produced; REVIEW and SHIP have nothing to act on. | high |
| 4 | `skills/sense/SKILL.md` | REQUIRED | Cycle runs with no intent detection / mode recommendation / context budget; every downstream phase is mis-scoped. | high |
| 5 | `skills/discover/SKILL.md` | STRONGLY RECOMMENDED | PLAN flies blind on prior ADRs and existing code; reinvents or contradicts prior decisions. | high |
| 6 | `skills/define/SKILL.md` | STRONGLY RECOMMENDED (REQUIRED unless hotfix/ship-only) | PLAN consumes ad-hoc prose with no premise/decision structure; scope drifts unchallenged. | high |
| 7 | `skills/capture/SKILL.md` | STRONGLY RECOMMENDED | Cross-session memory is lost; lessons never written, so the operator-relation learning thread never compounds. | medium |
| 8 | `skills/plan-eng-review/SKILL.md` | REQUIRED (the required gate) | `release-ev2` dashboard verdict cannot be issued; arch + test gaps reach build unchallenged. | high |
| 9 | `skills/office-hours/SKILL.md` | STRONGLY RECOMMENDED | The whole review chain runs against unstructured prose with no premises/decisions for ceo/eng/design to evaluate. | high |
| 10 | `hooks/shared/secret-scan-block` | REQUIRED | A secret reaches a commit/push with no block; credential leak ships. | medium |
| 11 | `hooks/shared/customer-data-block` | REQUIRED | Customer PII reaches a commit/push unaudited; compliance breach with no trail. | high |
| 12 | `skills/onecs-check/SKILL.md` (SC module entry) | REQUIRED before `/release-ev2` | A NEEDS_ACTION compliance item ships unresolved; the downstream-block that protects release is never evaluated. | high |
| 13 | `agents/security/SecurityAuditor.md` | STRONGLY RECOMMENDED before ship | Security review is skipped on a shippable diff; vulnerabilities ship with no second pass. | medium |
| 14 | `agents/ms-specific/OneCSAuditor.md` | STRONGLY RECOMMENDED before release-ev2 | OneCS items go unverified; release gate passes on an incomplete check. | medium |
| 15 | `skills/context-save/SKILL.md` | STRONGLY RECOMMENDED at session-end | Cold restart loses in-flight state; next session re-derives prior work from scratch. | high |
| 16 | `skills/context-warm-adrs/SKILL.md` | STRONGLY RECOMMENDED pre-PLAN | PLAN proceeds without prior ADRs loaded and may contradict already-decided architecture. | medium |
| 17 | `da` module entry (designed, cohort 6) | STRONGLY RECOMMENDED when work touches schema/migrations/storage | A destructive migration or untagged-PII schema reaches `main` with no DA gate (the load-bearing C6-F1 gap). | high |
| 18 | `skills/role-activate/SKILL.md` | OPTIONAL | Customer-facing artifacts ship in the operator's raw voice with no role calibration. | medium |

Honourable mentions (necessity proposed in cohorts, lower silent-degradation risk): `pair-agent` (OPTIONAL — no in-loop second perspective), `codex` (RECOMMENDED pre-release-ev2 — no outside voice), `context-budget` (RECOMMENDED before heavy phase — blind to headroom), `autoplan` (OPTIONAL — operator runs reviews manually with no aggregated verdict), the 4 composites (OPTIONAL — convenience shortcuts).

---

## 3. Necessity-value distribution (proposed, across the full denominator)

Synthesizing every `proposed: necessity` line found across the 8 cohorts:

- **REQUIRED** (skipping breaks the workflow or ships a defect): the core phase chain inside a cycle (plan, build, review, sense), the required planner gate (plan-eng-review), the two justified-block hooks (secret, customer-data), the SC release gate (onecs-check). ~9 components.
- **STRONGLY RECOMMENDED** (skipping silently degrades; allowed only with a stated reason): discover, define, capture, office-hours, the warm-* knowledge loaders pre-PLAN, context-save at session-end, the DA module on schema work, gate-adjacent agents (SecurityAuditor, OneCSAuditor). ~15-20 components.
- **OPTIONAL** (convenience or specialist; absence is safe): the 4 composites, role-* skills, most domain agents, the budget/snapshot/cool family, plan-tune, autoplan, pair-agent. The large majority of the 144.

The shape matches Architect's: a small REQUIRED spine, a STRONGLY-RECOMMENDED ring whose skips need justification, and a wide OPTIONAL surface.

---

## 4. The denominator (every component where the field would be load-bearing)

"Load-bearing if added" = the component runs inside a workflow and a recommender/orchestrator could act on its necessity. The count:

| Kind | Count | Notes |
|---|---|---|
| Phase-core skills (cohort 1) | 13 | All 8 phase + 5 composite; composites mostly OPTIONAL. |
| Planner skills (cohort 2) | 7 | 4 have prose necessity to promote; 3 absent. |
| Handoff / Brief Forge skills (cohort 3) | 18 | All absent; all carry a `proposed: necessity`. |
| Agents (cohort 4) | 83 | Template-level field; most OPTIONAL/RECOMMENDED, a few STRONGLY-RECOMMENDED at gates. |
| Hooks (cohort 5) | 19 | Add `necessity` + `gap_if_skipped` to every HOOK.md. |
| Role skills (cohort 7) | 8 | All OPTIONAL; absent today. |
| **Total components needing a necessity declaration** | **148** | Phase/planner/handoff/role skills (46) + agents (83) + hooks (19). |

The eng-domain modules (cohort 6) and cross-cutting layers (cohort 8) are *designed-not-built* — their necessity declarations are specified inside the v4.0 module pattern (`domain:` block) and should ship with the modules, not be retrofitted. They are counted within the skill/agent totals as they are built.

**Conservative headline figure: ~148 built components** would carry a load-bearing `necessity` + `gap_if_skipped`. (144 active skills + 83 agents + 19 hooks is the full population; the necessity field is load-bearing on essentially all of them, with the ~18 in §2 being where its *absence* is dangerous rather than merely incomplete.)

---

## 5. Recommendation — make `necessity` + `gap_if_skipped` a required frontmatter field

**Tie to D14 + the v4.0 frontmatter contract.** Every cohort independently arrived at the same `proposed` text ("add necessity + gap_if_skipped"). That convergence is the signal: this should not be 148 individual edits, it should be **one frontmatter-contract decision** folded into the v4.0 schema work, exactly as cohorts 1-4 recommend ("do not re-vote, fold into the master schema decision", cohort 4 F-405).

Proposed contract:

1. **Add two required frontmatter fields** to the v4.0 component schema, for skills, agents, and hooks:
   - `necessity: REQUIRED | STRONGLY_RECOMMENDED | OPTIONAL`
   - `gap_if_skipped: <one line — what silently degrades or breaks>`
2. **Enforce via a shape test** (`tests/shape/`), the same mechanism that already guards `brief_forge_handoffs` (`tests/shape/brief-forge-handoffs-canonical.sh`) and frontmatter shape. A missing or empty `necessity`/`gap_if_skipped` fails the test. This is the elegant route — Lintel already proves (cohort 7) that a *generator + shape test* is how uniformity is guaranteed (role-new bakes the schema; the shape suite enforces it).
3. **Wire consumers** so the field is read, not just written (closing the X3 write-only-memory anti-pattern that recurs across cohorts): the orientator / cycle mode-presets surface "you are about to skip a STRONGLY_RECOMMENDED step — here is the gap"; DISCOVER's dynamic dispatch ranks by necessity; autoplan's chain composition respects it.
4. **Steal from Architect:** Architect declares necessity *per section* and pairs it with the gap. Lintel's analog is *per component within a workflow*. The pattern is proven elsewhere (speckit/GSD gate on explicit status; the Architect bild declares per-section necessity) — adopt it rather than inventing a new vocabulary.

**Why a required field, not optional:** an optional necessity field reproduces today's state — present on the conscientious components, absent where it matters. Making it required (test-enforced) is the only mechanism that guarantees uniformity, and it costs one line of frontmatter per component plus one shape test. That is subtraction-aligned: one enforced field replaces 148 prose `When NOT to use` sections as the machine-readable source of truth (the prose stays as human detail; the field becomes the contract).

---

## 6. Cross-cohort note

The necessity gap is the X5 instance of the audit's recurring meta-pattern: **a concept declared in prose but never promoted to a parseable, consumed field.** It is the same shape as the Brief Forge `brief_forge_handoffs:` gap (cohort 3 CF-3), the pack-resolver zero-consumers gap (cohort 7), and the audit-writer bypass (cohort 8). Each is "the contract exists in words; the field/consumer does not." The recommendation in §5 fixes the necessity instance and should be sequenced with the broader v4.0 frontmatter-contract landing so all of these parseable-field gaps close together.
