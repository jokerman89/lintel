# Core Principles

These are load-bearing rules. They are not changed ad hoc — only via the deliberate process described in [EVOLUTION.md](EVOLUTION.md).

If a rule here conflicts with a per-repo adaptation, the rule here wins, unless the repo's CLAUDE.md explicitly documents a motivated deviation with date and reason.

---

## 1. Plan before code

- Non-trivial task (3+ steps or architectural decision) → enter plan mode first
- If something goes wrong mid-implementation → STOP and re-plan; do not push through
- Detailed specs upfront reduce ambiguity and minimize rework

## 2. Subagents for parallel work and context preservation

- Use subagents for research, exploration, audits, and parallel analysis
- Keep the main context clean for synthesis and decisions
- One task per subagent → focused output the main agent can act on
- When in doubt, prefer a subagent over polluting main context

## 3. Self-improvement loop (lessons.md)

- After ANY correction from the user → update `.claude/memory/lessons.md`
- Write rules that prevent the same mistake in the future
- Include **date, context, what went wrong, what should have happened, the rule**
- Review `.claude/memory/lessons.md` at session start
- This is the only way to compound learning

## 4. Verify before "done"

- Never mark a task complete without proof that it works
- Green tests are a minimum, not sufficient
- Diff behavior against baseline when relevant
- Mock implementation ≠ done implementation. Mocks must be explicitly flagged as "deferred to phase X"

## 5. Deviation flagging

If you discover during implementation that the INSTRUCTION or spec does not match reality (external API, docs, existing code):

1. STOP
2. Pause-report with: what you found + source, three alternatives + trade-offs, your recommendation
3. Wait for a decision
4. Do not silently fix or assume your interpretation is correct

## 6. Auto-mode bounds

Auto-mode authorizes code changes and local verification WITHOUT extra prompting, but NOT:

- Mutations against live/shared/production infrastructure
- Pushing secrets to external systems
- Force-push to `main` or the equivalent primary branch
- Destructive operations (data delete, schema drop, role revoke)
- Pushing container images to a registry that runs against live

When in doubt → ask. Auto-mode is not a license to destroy.

## 7. Cleanup when a bound is crossed

1. Stop immediately. Do not push on in hope that a successful continuation "fixes" the mutation
2. Verify state with read-only checks
3. Report honestly: what was done, the state now, the risks
4. Propose options with trade-offs, not a request for absolution
5. Wait for explicit authorization for rollback or continuation

## 8. Shared schema discipline

When two or more components talk to each other (event format, API payload, RPC message):

1. Define the schema ONCE in a shared lib or equivalent
2. Both components import from shared
3. Never duplicate the schema definition locally
4. Never "interpret" the schema differently in two components
5. Write at least one integration test per communication link

## 9. Simplicity first

- Each change as simple as possible
- Find root causes, not temporary fixes
- Changes should touch only what is necessary
- Do not add features, refactoring, or abstractions beyond what the task requires
- Three similar lines > a premature abstraction

## 10. Documented change beats silent change

- ADR (or equivalent decision record) for non-trivial architectural decisions
- Per-batch commits on a feature branch
- PR against main with a description
- Direct-push to main is allowed only with explicit per-batch authorization in the current session
