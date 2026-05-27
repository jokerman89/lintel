---
name: jstack-onerai-submit-draft
v1_alias: [jstack-onerai-prep]
description: Prepare a One RAI submission draft — checklist, capability/limitation, mitigation plan.
color: orange
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

# /onerai-submit-draft

Drafts a One RAI (Responsible AI) submission for an AI feature or system under development. Output is a structured markdown form the operator refines + pastes into the MS-internal One RAI portal. This skill does NOT submit — it prepares.

Per Layer 2: AI features with sensitive-use characteristics, customer-facing AI, or AI driving consequential decisions need One RAI clearance before launch.

## When to use

- Greenfield AI feature about to be designed — One RAI prep early prevents late-stage rework
- AI feature that touches a sensitive-use category (per `/rais-sensitive-use`)
- Customer-facing AI capability (chatbot, decision support, content generation)
- Significant change to existing One-RAI-cleared feature (re-prep required)

## When NOT to use

- AI used purely for internal engineering productivity (no customer impact) — typically exempt
- Already-cleared feature with no material change — re-prep wastes review cycles
- Non-AI features — One RAI is AI-specific

## Inputs

- Required `--feature <name>` — short name for the AI feature
- Optional `--source <path>` — code or design doc describing the feature
- Optional `--sensitive-use-report <path>` — output from `/rais-sensitive-use` (auto-attached if recent)
- Optional `--out <path>` — output draft path (default: `~/.jstack/rai/<feature>-onerai-DRAFT.md`)
- Optional `--update <id>` — update existing draft instead of new

## Workflow

1. **Read inputs.** Feature source if present, sensitive-use report if present.
2. **Structured intake via AskUserQuestion.** Gather:
   - Intended use cases (free text, multi-paragraph)
   - Out-of-scope uses (explicit limits)
   - Primary user populations (e.g. internal employees, paying customers, public)
   - Decision impact level (informational / suggestive / consequential)
   - Data flow (inputs, outputs, retention, deletion)
   - Capabilities (what does it do well?)
   - Limitations (what does it do poorly / not at all?)
   - Known failure modes
3. **Build draft sections:**
   - **Feature overview** (problem solved, users, business context)
   - **Capabilities** (concrete list)
   - **Limitations** (concrete list — required to be honest, not hedged)
   - **Sensitive-use assessment** (from `/rais-sensitive-use` if available)
   - **Data flow diagram** (textual; operator can render later)
   - **Risk register** (3-7 named risks with severity + likelihood + mitigation)
   - **Mitigation plan** (per risk, what's done now + what's planned)
   - **Monitoring + measurement** (how will operator know if a risk materializes?)
   - **Rollback path** (if launch goes wrong, how is the feature pulled?)
   - **Open questions for One RAI reviewer** (gaps operator wants the review board to weigh in on)
4. **Compliance scan.** Customer-data patterns BLOCKED in the draft (use placeholders). Sensitive-use indicators surface as cross-references.
5. **Mark DRAFT.** Frontmatter explicitly `status: DRAFT — for One RAI reviewer review only`. Never auto-submit.
6. **Report.**

## Report format

```
One RAI prep: feature=case-analysis-ai

Output: ~/.jstack/rai/case-analysis-ai-onerai-DRAFT.md (4.8 KB)
Sections: 10
Sensitive-use cross-ref: present (DLP-002, from /rais-sensitive-use)
Open questions for reviewer: 4

## Capability / Limitation balance
Capabilities listed: 8
Limitations listed: 7
Ratio 8/7 — balanced (good — honest about limits)

## Risk register
3 risks listed:
1. Hallucinated legal claim (severity: HIGH, mitigation: human-in-loop review)
2. Bias against minority case patterns (severity: MEDIUM, mitigation: monitored evaluation set)
3. Over-confidence in low-evidence cases (severity: MEDIUM, mitigation: confidence threshold + caveat surface)

## Next steps
1. Operator refines DRAFT (especially the 4 open questions)
2. Submit to One RAI portal for review
3. Update with reviewer feedback via /onerai-submit-draft --update PROV-<id>
4. After approval: archive in ~/.jstack/rai/approved/ + reference in repo CLAUDE.md
```

## Compliance integration

- Implements Item 4 of the 7 on-demand compliance items.
- Output is DRAFT only. Distribution outside operator → reviewer requires explicit confirmation per Layer 2.
- Customer-data scan on draft body — BLOCKS on hit. Use placeholders.
- Cross-links to `/rais-sensitive-use` output for risk-register seeding.

## Voice tier note

`voice: internal`. RAI submission text is MS-internal review form, not customer-facing.

## Failure modes

- **Operator skips required field (capabilities, limitations, risks):** form is INVALID, refuse to write. Each section must have ≥1 entry.
- **All risks marked LOW severity:** WARN — honest assessment usually surfaces at least one MEDIUM.
- **Capabilities outnumber limitations by >2x:** WARN — likely undersold limitations. Reviewer will push back.
- **Sensitive-use report absent + feature is customer-facing AI:** WARN — run `/rais-sensitive-use` first; reviewer will require it.
- **Draft target path collides:** ask whether to update existing or write new variant.

## Examples

**New feature:**
```
> /onerai-submit-draft --feature case-analysis-ai --source docs/design/case-analysis-ai.md
[Intake interview]
✓ DRAFT at ~/.jstack/rai/case-analysis-ai-onerai-DRAFT.md
  Next: refine + submit to One RAI portal.
```

**With sensitive-use input:**
```
> /onerai-submit-draft --feature legal-summary --sensitive-use-report ~/.jstack/rai/legal-summary-sensitive-use.md
[Auto-imports sensitive-use findings into risk register seed]
✓ DRAFT generated.
```

**Update post-review:**
```
> /onerai-submit-draft --feature case-analysis-ai --update
[Reads existing DRAFT, prompts for reviewer feedback to incorporate]
✓ Updated. Re-submit when ready.
```

## See also

- `/rais-sensitive-use` — feeds risk register
- `/dpia-submit-draft` — if personal data; complementary
- `/rais-transparency-note` — customer-facing disclosure document
- `/onecs-check` Item 4 — runs this for sensitive-use category features
- One RAI internal portal — destination for the DRAFT after operator refinement
