# Swarm charter: Adaptive review

One coordinator owns shared state, generated output, commits and serial
integration. The mapped plan is the only task and acceptance authority.
P1 and P2 use separate Git worktrees and disjoint scopes; no shared-tree
concurrent writers. Both request Opus 5.5 / high / long_context.

Workers write only their declared source files and own report. They run focused
tests, retain observed command outcomes and return attribution. They do not
commit, publish, install dependencies, run exploits, mutate other sessions or
write their independent review. The coordinator checks scopes before integration.

Independent reviewers report findings without repairs; their invocation is
separately attributable. Specification precedes quality. Local observations do
not replace ADR-0028's current review/QA or ADR-0029's profile reference.

Recover from this map, exact Git states, original leaf IDs and actual evidence,
not process status or a remembered PASS. Preserve out-of-scope changes for
reconciliation, never discard another owner's work.
