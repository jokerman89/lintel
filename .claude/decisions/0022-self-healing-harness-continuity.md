# ADR-0022: the harness self-heals continuity — move "don't lose the thread" from prose to hooks

- **Status:** Accepted
- **Date:** 2026-06-14
- **Deciders:** operator (setup-hardening cycle, signoff 2026-06-14)
- **Supersedes:** —
- **Superseded by:** —

## Context

The operator reported a recurring, cross-session failure: "I run /li:cycle, it does a lot of work,
then total silence — no footer, no next step, as if the session forgot it was mid-cycle." They
asked whether it's a systemic fault, whether Claude Code doesn't respect the harness, and whether
building strict markdown harnesses is even wise.

A 7-agent diagnosis workflow + adversarial verification (and first-hand checks) established the root
cause with evidence, and corrected two of my own initial assumptions:

- The footer renderer is **not** broken — `render_cycle_footer` exits 0 and renders correctly. A
  live `BUILD/STARTING` cycle was found frozen on disk (the exact symptom captured).
- Only `SessionStart`, `PreToolUse`, `PostToolUse` hooks were registered — **no `Stop` hook, no
  `PreCompact` hook**. Nothing fired at turn-end or on compaction to catch a session ending
  mid-cycle. Every "render the footer / continue / append state" instruction lived in SKILL.md
  prose the model must *choose* to execute. Across long BUILDs, subagent returns, and compaction,
  that adherence decays — and nothing pulled it back. ADR-0003 itself cites "invisible discipline is
  indistinguishable from no discipline," yet shipped a footer whose *content* was visible but whose
  *invocation* was invisible. Self-documented as L-008 + L-016.
- Claude Code corrections (from its docs): there is **no PreCompact hook** (compaction is
  non-hookable); a `Stop` hook can **block (exit 2) or warn (exit 0 stdout)** but **cannot inject
  context** to resume. Project-root CLAUDE.md + auto-memory *are* re-injected after compaction.

So the honest answer to the operator's meta-question: a purely-prose harness **cannot** guarantee
continuity (proven three times). The fix is neither "stricter prose" (rejected — it's what already
failed) nor "abandon the harness" (chaos), but **move the load-bearing continuity guarantees into
the deterministic substrate (hooks) and keep the prose layer thin.**

## Decision

Four backstops, three now mechanical (the "full self-heal" the operator chose over the lighter
options):

1. **Footer code fix** — `lib/cycle-footer.sh`: a just-`CYCLE STARTING` cycle (no phase closed)
   now renders the full stepper instead of falling to the thin "no active cycle" line in auto/full
   tier (the compact tier already handled it). The one genuine renderer bug.
2. **`cycle-incomplete-warn` Stop hook** (NEW) — at turn end, if a cycle is open mid-flight, it
   surfaces the position footer. **Warn-only: stdout + `exit 0`, never `decision:block`/exit 2** (a
   blocking Stop hook forces continuation and can infinite-loop). Silent outside a cycle.
3. **`session-digest` reads state** — re-injects "Current cycle: phase X · next Y" so fresh /
   resumed / post-compaction sessions recover position. Reuses the single canonical segment
   selector (`state_cycle_segment`), not a new parser.
4. **`CYCLE STARTING` is the explicit first action** (`skills/cycle/SKILL.md`) — both new mechanisms
   depend on the marker existing.

Bundled in the same cycle (operator signoff): remove the 4 repo + 4 template agents (thin
duplicates that *shadowed* the richer plugin fleet — project beats plugin); de-stale the global
`~/.claude/CLAUDE.md` (defer paths to each repo, kill the dead `tasks/*` pointers); add a factory-
exception note to the repo CLAUDE.md; resolve the 0015/0016/0017 ADR numbering collision +
uniqueness guard; add one CURRENT pointer to working-state.

## Alternatives considered

- **Stricter prose** ("the model MUST always render the footer"): rejected — that is exactly what
  L-008/L-016 prove does not hold. Invisible discipline.
- **Blocking Stop hook** (`decision:block` to force continuation): rejected — infinite-loop risk and
  it blocks every legitimate stop. Warn-only surfaces the canary without coercing the model.
- **PreCompact hook** (my own initial idea): rejected — Claude Code has no PreCompact hook;
  compaction is non-hookable. The digest re-injection (SessionStart) + CLAUDE.md (re-injected post-
  compact) are the available recovery surface.
- **Demote the footer to best-effort / go lighter** (the steelman against more harness): a Stop hook
  taxes every turn end, is Claude-Code-only (other CLIs keep the prose fallback), and the footer is
  an affordance, not a correctness invariant. Considered and partially honored — the hook is
  warn-only and cheap, the fix-#1 code bug is the unambiguous win — but the operator chose full
  self-heal because the gap recurred 3+ times and the substrate already exists.

## Consequences

- **Positive:** a session can no longer silently end mid-cycle without the operator seeing the
  position; fresh/resumed/compacted sessions recover where they were; bare-name agent dispatch
  resolves to the richer fleet agent; the global/repo CLAUDE.md "fight" (dead `tasks/*` pointers) is
  gone; ADR numbers are unique + guarded.
- **Negative:** the Stop hook + digest line are Claude-Code-only (other CLIs rely on the prose
  footer convention — documented in the hook). One more registered hook to maintain.
- **Neutral:** the continuity guarantee is now split — mechanical on Claude Code, prose elsewhere.

## References

- Diagnosis: 7-agent `lintel-setup-diagnosis` workflow + adversarial verdict (2026-06-14, session record)
- ADR-0003 (cycle-position footer — the convention this enforces), ADR-0008 (state ledger),
  ADR-0015 (agent-surface subtraction), L-008 / L-016 (the recurring symptom)
- Tests: `tests/unit/cycle-continuity.sh`, `tests/shape/adr-numbers-unique.sh`
- Structure-change: `.claude/engineering/evolution/2026-06-14-setup-hardening.md`
