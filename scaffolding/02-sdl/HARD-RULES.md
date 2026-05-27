# HARD RULES — 5 always-on compliance rules

These run at session start automatically. They cannot be disabled. Detection happens inline in skills and opt-in hooks.

## Rule 1: No customer data anywhere

**The rule:** No real customer data in:
- Repo content (source, fixtures, docs)
- Operator prompts to the agent
- Generated artifacts that may be committed
- Screenshots / DOM captures from `/browse`
- Provenance records or audit logs

**Why:** This is a Premise of the JStack design. Customer data in repo = compliance incident. Even immediate-revert leaves git-history traces.

**Detection patterns:**
- Email addresses
- Phone numbers (international + Swedish formats)
- Swedish personnummer (YYMMDD-NNNN)
- Names paired with case identifiers
- Address lines with street + number

**Hooks that enforce:**
- `no-customer-data-in-message` (warn-only) — prompt scan
- `no-customer-data-in-screenshot` (warn-only) — DOM scan
- `customer-data-block` (JUSTIFIED-BLOCK) — git commit scan

**Override path:** ONLY at commit-block tier, via explicit `JSTACK_OVERRIDE_CUSTOMER_DATA=1 JSTACK_OVERRIDE_REASON="..."`. Use only for confirmed placeholders, public-domain examples, test fixtures explicitly marked.

**What to do if violated:**
- Stop immediately
- Quarantine the artifact (~/.jstack/quarantine/)
- Re-collect from sanitized source
- Open an issue if it landed in git history (then real-quarantine the repo)

## Rule 2: No secrets, credentials, tokens

**The rule:** No real secrets in:
- Code (committed or staged)
- Operator prompts
- Generated artifacts

**Why:** Once committed, secrets leak into git history. Force-push removal leaves traces. Rotation is the only fully-mitigating action.

**Detection patterns:**
- GitHub tokens: `gh[opur]_[A-Za-z0-9]{36}`
- OpenAI keys: `sk-[A-Za-z0-9]{32,}`
- Anthropic keys: `sk-ant-[A-Za-z0-9-]{30,}`
- Slack tokens: `xox[abposr]-[A-Za-z0-9-]{10,}`
- AWS access keys: `AKIA[0-9A-Z]{16}`
- Azure connection strings, account keys
- Private keys: `-----BEGIN ... PRIVATE KEY-----`
- Hardcoded passwords (heuristic)

**Hooks:**
- `no-secrets-in-edit` (warn-only)
- `secret-scan-block` (JUSTIFIED-BLOCK at commit)

**Override path:** ONLY at commit-block tier, via `JSTACK_OVERRIDE_SECRET=1 JSTACK_OVERRIDE_REASON="..."`. Use only when known-false-positive (example placeholder in docs, test fixture).

**What to do if violated:**
- Stop. Do NOT commit / push hoping to fix forward.
- Rotate the secret immediately (the real one, in the real system)
- Remove from staged content
- If already committed: rotation IS the mitigation; git history cleanup is supplementary
- Audit log the incident

## Rule 3: Production-mutation requires per-call auth

**The rule:** Operations that mutate live/shared/production resources require explicit, per-call operator authorization. Auto-mode does NOT authorize these.

**What counts as production-mutation:**
- Database DDL/DML on a live DB (outside the migrations pipeline)
- Container image push to a live registry
- Deploy pipeline triggers
- Secret rotation in production secret store
- Role assignment / firewall rule change in production
- Direct push to `main` (per CLAUDE.md)

**Hooks:**
- `no-production-mutation-without-auth` (warn-only) — Bash heuristic
- `no-direct-main-push` (warn-only) — git push to main

**Auth model:** "Yes, I authorize this batch" in conversation. NOT a flag, NOT environment-variable. Operator-explicit per call. Audit-logged.

**What to do if violated:**
- STOP IMMEDIATELY
- Verify state with read-only checks
- Report honestly: what was done, current state, risks
- Propose options (rollback / continue with mitigations / pause)
- Wait for authorization on next step

## Rule 4: MS SSO only, zero retention, feedback off

**The rule:** Claude Code (and Claude API access generally) must be configured for:
- MS SSO authentication only
- Zero retention of conversation content
- Telemetry feedback OFF
- No Claude.ai workbench parallel session (avoid retention via that path)

**Why:** MS info-protection policy. CAIP-SE operators have been onboarded via MS Digital + ProcureWeb (SSPA) and the operating model assumes MS-managed identity + zero retention.

**Detection:** This rule is a SETUP rule — verified at install time and at session start. No content-pattern detection.

**Hooks:** None at runtime. `/health` skill checks setup state.

**What to do if violated:**
- Pause session
- Verify Claude Code config (claude.json, settings.json)
- Reconfigure with MS SSO + zero retention + feedback off
- Restart session

## Rule 5: First-party-first

**The rule:** Prefer Microsoft first-party solutions (GitHub Copilot Enterprise, M365 Copilot, Azure OpenAI, Azure-managed services) before third-party alternatives. Third-party choices need documented justification.

**Why:** MS partnership economics + supportability + security posture + integration depth.

**What it does NOT mean:** Never pick third-party. Just don't pick third-party reflexively — surface the MS option, evaluate honestly, document the decision.

**Detection patterns:**
- Common 3P deps in package.json / requirements.txt / etc. with documented MS alternatives
- See `~/.jstack/first-party-alternatives.yaml` for the mapping

**Hooks:**
- `non-first-party-warn` (warn-only) — manifest edit scan

**Skills:**
- `/first-party-check` — dedicated scan
- `FirstPartyMigrator` agent — produces concrete migration plan

**Override path:** Document the decision in commit message, ADR, or `/learn` entry. Periodic `/first-party-check` re-audit will pick up justified deps and skip them.

**What to do if violated:**
- Not a violation — a question. The decision is operator's; the rule asks that the question be asked.
- Document the answer.

## What these 5 rules are NOT

- They are NOT exhaustive of MS compliance. The 7 on-demand items + 8 reference docs cover broader scope.
- They are NOT a substitute for human compliance review on customer-bearing AI features.
- They are NOT a guarantee — they are pattern-detection that catches the common cases. Sophisticated leaks may evade detection.

## See also

- [ON-DEMAND-RULES.md](ON-DEMAND-RULES.md) — the 7 on-demand items
- [REFERENCE-RULES.md](REFERENCE-RULES.md) — the 8 reference-only docs
- `/onecs-check` skill — runs the 7 on-demand items
- `02-sdl/hooks/` — opt-in enforcement layer
