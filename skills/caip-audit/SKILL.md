---
name: caip-audit
layer: ms-team
description: CAIP-SE-specific readiness audit — engagement state, compliance, voice, deliverables.
color: yellow
tools: Read, Bash, Grep, Glob, Write
voice: internal
cli_support: [claude-code, codex]
---

# /caip-audit

Operator-level audit for CAIP-SE customer engagements. Checks engagement state across four dimensions: engagement metadata, compliance status, voice-gate status of deliverables, technical readiness. Output is a readiness scorecard the operator uses pre-customer-meeting.

Distinct from `/onecs-check` (item-by-item checklist) and `/health` (technical install diagnostics). This is engagement-shaped.

## When to use

- Pre-customer-meeting prep — verify everything's in shape
- Post-engagement retrospective on artifact + compliance hygiene
- Onboarding a teammate to an in-flight engagement
- Periodic CAIP-SE review across multiple engagements

## When NOT to use

- Generic engineering tasks — `/health` or `/onecs-check` fit
- Non-CAIP work — this skill is opinionated for CAIP-SE
- Within-MS-engineering project (no customer surface) — overkill

## Inputs

- Optional `--engagement <path>` — path to engagement repo (default: cwd)
- Optional `--customer <placeholder>` — sanitized customer name reference
- Optional `--dimensions <list>` — restrict to specific dimensions (default: all 4)
- Optional `--out <path>` — write scorecard to file

## Workflow

1. **Locate engagement repo.** Validate it has `.git/`, `CLAUDE.md`, `compliance/` dir. If not: surface required structure.
2. **Dimension 1: Engagement metadata.**
   - Customer placeholder set (no real names)
   - Engagement type declared (demo / PoC / co-dev)
   - Stakeholders named (role-only)
   - Timeline + milestones
3. **Dimension 2: Compliance status.**
   - 5 always-on rules current
   - 7 on-demand items: which run, which open
   - DPIA / One RAI / Sensitive Use docs present + state (DRAFT / APPROVED)
   - Data class declarations present per artifact
4. **Dimension 3: Voice gates.**
   - All customer-bound DRAFTs identified
   - `/rais-customer-voice-check` status per DRAFT
   - Provenance records present per finalized artifact
5. **Dimension 4: Technical readiness.**
   - Tests pass on main
   - Deploy stubs validated
   - No `WIP:` commits on the engagement branch
   - Frozen-zones honored
6. **Score per dimension.** GREEN / YELLOW / RED + per-item findings.
7. **Output scorecard.**

## Report format

```
CAIP Audit: customer-A nordic-finserv quarterly-engagement

Engagement repo: /e/Workspace/customer-A-nordic-finserv-demo
Last commit: 2 hours ago
Branch: main

## Dimension 1 — Engagement metadata
GREEN
✓ Customer placeholder ("customer-A") consistent (no real name found)
✓ Engagement type: PoC (declared in README.md)
✓ Stakeholders named by role: Field-CTO, SE engineer, customer CISO
✓ Timeline: 6 weeks, milestones at week 1/3/6

## Dimension 2 — Compliance status
YELLOW
✓ 5 always-on rules: clean
⚠ 7 on-demand: 5 PASS, 1 NEEDS_ACTION (Item 3 data class on follow-up email), 1 NOT_APPLICABLE
✓ DPIA: APPROVED
✓ One RAI: DRAFT (pending submission)
⚠ Sensitive-Use report: DRAFT — REQUIRED before customer demo (Item 4 triggered)

## Dimension 3 — Voice gates
YELLOW
✓ 3 customer-bound DRAFTs identified (script, handout, follow-up email)
⚠ /rais-customer-voice-check: 2 PASS, 1 not-yet-run (handout)
⚠ Provenance: 2 records present, 1 missing for handout

## Dimension 4 — Technical readiness
GREEN
✓ Tests pass (npm test, 47/47)
✓ Deploy stubs validated for staging
✓ No WIP: commits
✓ Frozen-zones honored

## Overall: YELLOW
- Resolve Item 3 data class on follow-up email
- Submit One RAI before customer demo
- Run /rais-customer-voice-check on handout-DRAFT
- /provenance-track the handout

Recommended order: voice-check + provenance (5 min), then compliance items (15 min).

Estimated time to GREEN: 25 minutes.
```

## Compliance integration

- Aggregates results from `/onecs-check` + voice-check status + provenance state.
- Per-dimension scoring is advisory; operator decides whether to proceed.
- YELLOW + RED both block customer-demo per Layer 2 (operator can override with logged reason).

## Voice tier note

`voice: internal`. Audit is engineering-internal.

## Failure modes

- **Engagement repo doesn't match CAIP-SE structure:** report missing pieces, suggest `/scaffold-engagement-demo` to fix.
- **Customer real-name detected (sanitization failure):** STOP — RED on Dimension 1 + refuse other dimensions until sanitized.
- **Compliance gate hasn't been run recently:** WARN, recommend running, continue with stale data caveat.
- **Operator on personal branch (not main) with engagement work:** WARN — engagement artifacts on a personal branch are fragile.

## Examples

**Pre-customer-meeting check:**
```
> /caip-audit
[All 4 dimensions, 25 min to GREEN]
YELLOW overall. Resolve 4 items before customer demo.
```

**Single-dimension focus:**
```
> /caip-audit --dimensions voice-gates
[Only Dimension 3]
2 PASS, 1 missing voice-check. Run /rais-customer-voice-check on handout-DRAFT.md.
```

**Scorecard to file for stakeholder share:**
```
> /caip-audit --out engagement-status.md
[Sanitized scorecard written]
File written. Internal-share-only — no customer-bound info.
```

## See also

- `/onecs-check` — Dimension 2 input
- `/rais-customer-voice-check` — Dimension 3 input
- `/provenance-track` — Dimension 3 input
- `/health` — system-level diagnostic (this skill is engagement-level)
- `/scaffold-engagement-demo` — fix Dimension 1 structure if missing
