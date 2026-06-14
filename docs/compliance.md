# Compliance

The rule set that the canonical session instructions enforce. The neutral baseline below applies everywhere; tiered, team-specific rules come from the active **pack**. Audit this doc against your own constraints before relying on it.

> **Status note.** This document codifies the 5-step session-start check from `AGENT-INSTRUCTIONS.md` and lists 15 hard rules. The hard rules below are **derived** from common enterprise compliance patterns (data sovereignty, customer data, secrets, shared infrastructure). Tiered rules are pack-driven — before using this in a customer-adjacent context, verify against your pack's authoritative compliance source and replace any rule that is wrong for your tenant.

## The 5-step session-start check

Every session starts with this check. Trivial actions (a typo fix, a question, a doc edit) can skip it. Anything that touches code, data, or external systems goes through it.

### Step 1 — Authority scope

Is the work the operator is asking for inside this repo's authorized scope?

- "Authorized scope" = stated in the repo's `CLAUDE.md` or charter, or explicitly granted by the operator.
- If unclear → ask. Do not assume scope expands to adjacent repos.

**Fail action:** halt, ask which scope applies.

### Step 2 — Customer-data check

Any path, secret, or content involved in this work that could be customer data?

- Customer data = anything tied to a named customer account, tenant, or end-user.
- Internal MS engineering data (process docs, code conventions) is NOT customer data.
- Synthetic / public sample data is NOT customer data.

**Fail action:** halt immediately. Do not read further. Escalate to operator.

### Step 3 — Production-mutation check

Will this action mutate a shared or production system?

- DB schemas / DML against live, container image push to a live registry, deploy-pipeline triggers, secret rotation, role assignments — all mutations.
- Local builds, local DB ops, branch builds with no deploy hookup — not mutations.

**Fail action:** require explicit per-call authorization from operator. Auto-mode does not cover production mutations.

### Step 4 — Secrets check

Any secret being introduced into code, logs, commit messages, or shared chat?

- "Secret" = API key, OAuth token, connection string with credentials, private cert, SSH key.
- Public IDs (account names, org slugs) are not secrets.

**Fail action:** halt. Request a secret-store path (Key Vault, environment variable name, secret-manager reference) instead.

### Step 5 — Hard-rule check

Any operation that contradicts an explicit hard rule from the list below?

**Fail action:** halt and report which rule.

A clean five-OK pass is the floor for any non-trivial action.

## 15 hard rules

These rules are non-negotiable in auto-mode. The operator can grant an explicit exception per-call; the rule still applies for everything else.

### Data sovereignty

1. **EU customer data stays in EU regions.** Reads, writes, exports, transient processing — all in-region. Cross-region transfer requires explicit operator + customer authorization.
2. **Customer data does not leave the customer's tenant boundary.** No copying customer artifacts into MS-internal repos, no sample-extraction into shared workspaces.
3. **No customer data in this scaffolding repo, ever.** Issue templates, ADRs, example files — all must use synthetic or public-domain data.

### Secrets and credentials

4. **No secrets in code, comments, or commit messages.** Use environment variables that resolve from a secret store (Key Vault preferred for Azure, internal secret-manager for MS-internal services).
5. **No secrets in logs.** Redact before logging. If you find a secret in a log, treat it as a confirmed incident.
6. **No secrets in chat or shared channels.** Including Slack, Teams, GitHub issue comments, PR descriptions.

### Production mutations

7. **No production database DDL outside the migrations pipeline.** Direct DDL against live = halt + per-call authorization.
8. **No `git push --force` to `main` or release branches.** Force-push to feature branches is allowed.
9. **No deploy-pipeline triggers from a session.** Operator runs deploys. Agents prepare them.
10. **No container image push to a production registry.** Push to local or branch registries is fine.

### Customer engagement

11. **No customer-facing artifacts go to a customer without operator approval.** PR descriptions, sample analyses, demos — operator reviews before send.
12. **No public-internet calls with customer data.** Calls to public APIs (translation services, public LLM endpoints) with customer payload = halt.

### Tooling and supply chain

13. **No third-party code bundled into MS-licensed projects without LICENSE check.** Use this scaffolding's `install/` pattern (install from upstream, do not vendor).
14. **No skill or agent installed from an un-vetted source.** Only sources listed in [promoted-agents.md](promoted-agents.md) and `install/upstream-sources.yaml`.

### Audit

15. **Every non-trivial action is traceable.** Commits are atomic, ADRs document non-obvious choices, `tasks/lessons.md` captures corrections. A reviewer should be able to reconstruct the reasoning without asking the operator.

## When a rule has been broken

Same cleanup pattern as auto-mode breach in `AGENT-INSTRUCTIONS.md`:

1. Stop immediately. Do not push on hoping the next step undoes it.
2. Verify state with read-only checks.
3. Report honestly — what was done, current state, risks.
4. Propose concrete options with trade-offs. Do not ask for absolution.
5. Wait for explicit authorization before rollback or continuation.

## Rule deltas per repo

Some repos have additional rules (e.g., regulated-industry customer work). Those go in the repo's own `CLAUDE.md`, not here. Per-repo rules add to the 15 above; they do not subtract.

## Reviewing this doc

This list should be reviewed at least every 6 months, and whenever:

- A new Microsoft policy lands that affects agent-based development.
- An incident reveals a rule that should be added.
- A rule has been overridden three times in a quarter (signal that it is wrong or unrealistic).

Reviews are logged in `scaffolding/EVOLUTION-LOG.md`.
