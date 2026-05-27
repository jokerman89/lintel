---
name: jstack-compliance-gate
description: Run the 7 on-demand MS compliance checklist items on-request (vs the 5 always-on auto).
color: red
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /compliance-gate

Operator-triggered checklist for the 7 on-demand MS compliance items (the always-on 5 run automatically at session start). Use before any moment of compliance significance: pre-ship of customer artifact, pre-deploy, pre-demo, pre-external-share.

Per A4 from design: this skill is a CHECKLIST run by operator, not automated enforcement. The skill surfaces what to verify; the OPERATOR confirms each item.

## When to use

- Before shipping a customer-facing artifact
- Before triggering a production deploy
- Before sharing artifacts externally (customer, partner, public)
- After scope-change in a project that may have introduced new compliance surface
- Periodic spot-check (weekly review, before stakeholder demo)

## When NOT to use

- Engineering-internal work, no external surface — overkill
- Just want the 5 always-on rules — those auto-run; this is the on-demand layer
- Reference reading (the 8 reference-only docs) — use `/help --rules reference`

## Inputs

- Optional `--scope <item-list>` — run only specified items (default: all 7)
- Optional `--artifact <path>` — focus the check on a specific artifact
- Optional `--out <path>` — write report to file
- Optional `--checklist-only` — render the checklist without running content scans (fastest)

## Workflow

1. **Read on-demand items.** From `scaffolding/02-compliance/ON-DEMAND-RULES.md` (the 7 items, listed in Phase 6 content).
2. **For each item, run the structured check:**
   - **Item 1: AGT / agent governance** — does the work introduce a new agent? If yes: verify it has tier-stamp + license-class + per-call-auth defaults.
   - **Item 2: First-party-first** — are first-party MS solutions considered before third-party? Scan for new external service deps.
   - **Item 3: MS Business Data class** — does the artifact reference data classes? Verify Public/Non-business only; flag Business / Sensitive / Highly Sensitive / Confidential.
   - **Item 4: Sensitive-use case** — does this fit a sensitive-use category per MS RAI? If yes: One RAI Sensitive Uses prep required; trigger `/sensitive-use-report`.
   - **Item 5: DSB (Data Sharing Board)** — does this share data outside intended audience? If yes: prep DSB submission via `/dsb-prep`.
   - **Item 6: DPIA (Data Protection Impact)** — does this process personal data? If yes: prep DPIA via `/dpia-prep`.
   - **Item 7: Transparency note / disclosure** — does this customer-facing output need a transparency note? If yes: prep via `/transparency-doc-gen`.
3. **Aggregate.** Per-item status: PASS / NEEDS_ACTION / NOT_APPLICABLE.
4. **Surface action items.** For each NEEDS_ACTION, name the specific follow-up skill or human escalation path.
5. **Operator confirms.** Via AskUserQuestion: "all NEEDS_ACTION items confirmed handled?" Operator says yes / not yet / N/A.
6. **Audit log.** Append every item + operator decision to `~/.jstack/audit/compliance-gate.jsonl`.
7. **Report.**

## Report format

```
Compliance gate: pre-customer-demo

Scope: all 7 on-demand items
Artifact: docs/customer-demo-scripts/demo-001.md
Always-on (auto): ✓ 5/5 clean

## Item 1: AGT / agent governance
NOT_APPLICABLE — no new agent introduced

## Item 2: First-party-first
PASS — Azure OpenAI used (not OpenAI direct), Defender for Cloud (not 3rd-party SIEM)

## Item 3: MS Business Data class
NEEDS_ACTION — demo references "production customer data" without class declaration
   Action: classify as Public/Non-business (synthetic data) OR sanitize/replace before use
   Follow-up: re-run /compliance-gate after sanitization

## Item 4: Sensitive-use case
NOT_APPLICABLE — internal demo, no AI-driven decision on individuals

## Item 5: DSB
NOT_APPLICABLE — no data sharing outside intended audience

## Item 6: DPIA
NOT_APPLICABLE — no personal data processing

## Item 7: Transparency note
PASS — demo script includes AI-disclosure paragraph + capability/limitation note

## Verdict
1 NEEDS_ACTION (Item 3). Resolve before customer demo.

Operator confirmation: not yet — sanitize data first
Audit logged: ~/.jstack/audit/compliance-gate-20260527-185412.jsonl
```

## Compliance integration

- This skill IS the on-demand half of Layer 2 (the 5 always-on run automatically; this runs the 7).
- Does NOT replace operator judgment — it surfaces the checklist, operator confirms.
- All decisions logged. Audit log is append-only.
- A NEEDS_ACTION item BLOCKS downstream `/ship` of customer-bearing artifacts.

## Voice tier note

`voice: internal`. Compliance is engineering-internal — direct, no rhetorical flourish.

## Failure modes

- **ON-DEMAND-RULES.md not found:** report missing file, exit. This skill depends on Phase 6 content.
- **Item check requires external system query (e.g. DSB API):** fall back to manual prompt. Surface "verify in <portal-url>" with explicit operator confirmation.
- **Operator says "yes" to all items by reflex:** require per-NEEDS_ACTION individual confirmation, not bulk. Bulk-confirm too easy to fire without reading.
- **Audit log unwriteable:** treat as compliance failure. Refuse to record the gate event without audit trail.

## Examples

**Pre-demo gate:**
```
> /compliance-gate --artifact docs/customer-demo-001.md
[Runs 7 items, surfaces 1 NEEDS_ACTION]
Resolve Item 3 (data class) before demo.
```

**Periodic check:**
```
> /compliance-gate
[Runs across general repo state]
6 PASS / 0 NEEDS_ACTION / 1 NOT_APPLICABLE. Clean.
```

**Quick checklist render:**
```
> /compliance-gate --checklist-only
[Prints all 7 items as a static checklist, no scan]
For manual review.
```

## See also

- 5 always-on rules — auto-run at session start, see [LAYERS.md](../../LAYERS.md)
- ON-DEMAND-RULES.md (Phase 6) — the source of truth for the 7 items here
- `/sensitive-use-report`, `/dsb-prep`, `/dpia-prep`, `/transparency-doc-gen` — Item-specific follow-up skills
- `/ship` — refuses customer-bearing artifacts with open NEEDS_ACTION items
