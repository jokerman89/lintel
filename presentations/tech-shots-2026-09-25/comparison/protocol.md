# Prerecorded A/B build protocol - attempt 2
Date: 2026-09-20. Amendment: both arms restart from a stronger identical project baseline. Scenario: synthetic customer-support pilot cockpit.

## Question
With the same implementation prompt, source data, stakeholder answers, runtime and inherited model defaults, what changes when an agent receives a curated Lintel workflow context?
This is a single paired worked example, not a benchmark or causal estimate of productivity.

## Controls
- Fresh-context builders, fork_turns=none, one run per arm; no builder sees the other output.
- Identical implementation-prompt.md, stakeholder-answers.md, tickets.js, AGENTS.md, verify.mjs and CI workflow, byte hashes recorded before attempt 2.
- Both arms get competent project engineering instructions, project knowledge, 14 meaningful browser checks and a CI definition. Both must run and fix the same tests. Baseline is not instructed to be shallow.
- Treatment only: curated, frozen source excerpts from Lintel SCOPE / PLAN / REVIEW / CAPTURE, with lineage and local execution adaptation. This is not an installed plugin or hook enforcement test.
- Same default model and effort inherited by the spawning API. Exact resolved runtime identity not exposed in the spawn result; not asserted here.
- No cherry-picking, post-run repairs or reruns to improve comparative appearance. Verification may be rerun to correct a broken test adapter, but code hashes stay frozen.
- Build time and token/cost differences are not used as outcome measures.
- Additional context length and explicit process instructions are inseparable from this treatment. This does not isolate brand, model, instruction length or a complete harness installation.

## Frozen behavioral rubric (each result reported separately; no vanity total)
B01 Offline launch without console errors; required synthetic rows available.
B02 Northwind default: total 8, active 5; Contoso: total 4, active 3.
B03 Resolved-only Northwind: total 3, active 0.
B04 UTC date 2026-09-19 includes NW-102, NW-103, NW-104; excludes NW-105.
B05 UTC date 2026-09-22 includes NW-107 and NW-108.
B06 Combined customer/status/severity/search filters intersect.
B07 Empty filter: zero KPIs, understandable empty result; no NaN.
B08 Daily and status graph counts reconcile with the current filtered data; equivalent accessible labels exist.
B09 CSV exports exact filtered rows, stable named columns, preserves timestamp, quotes commas/newlines/quotes.
B10 CSV neutralizes =,+,-,@ prefixes, including whitespace-prefix cases.
B11 Suspicious ticket subject rendered as literal text; no injected element or script execution.
B12 Native controls labelled, keyboard focus visible; usable at 390px and 1440px.
B13 Clear/reset filters preserves customer.
B14 UI and handoff distinguish client filtering from server authorization.

## Frozen documentary rubric (presence alone is not quality)
D01 Business ambiguity: exact questions, answers vs assumptions, cited source.
D02 Plan: named work units, dependencies, acceptance checks, verification route; density and execution usefulness assessed, not word count.
D03 Decision rationale: alternatives/trade-offs and trace from decision to behavior.
D04 Verification: actual runs, failure/correction evidence, remaining limits; self-review is labelled honestly.
D05 Cold handoff: next engineer can run, understand scope/contracts, verify and extend without chat history.
D06 Reuse: any scoped, useful lesson/check persisted without inventing an incident.

## Fair stage direction
Show both running results first. Reveal the identical prompt and information. Examine actual branch points in questions, plan, decisions and tests. If both are correct, say so. Never invent a bad baseline, a human question exchange, measured acceleration, or security guarantees.

## Amendment log
The operator strengthened the baseline after attempt 1 had started: ordinary modern agent plus good AGENTS.md, project knowledge, tests and CI. Rather than add these mid-run, both original agents were interrupted and all original files archived under attempt-01-superseded. The initial baseline had executed 15 checks; the initial treatment had written planning artifacts but no finished implementation. These are NOT the presented comparison. Both attempt-2 builders start fresh from the same new starter, with no access to attempt 1 or each other.

The shared test code was written after seeing attempt-1 baseline's DOM layout, then frozen before both attempt-2 builds. It expresses the pre-existing behavioral rubric and a shared neutral selector contract; both receive it equally. This is disclosed rather than presented as blinded test design.

CI configuration is supplied equally. Its browser checks are executed locally; no remote repository is created and no remote CI run is claimed. The local browser runtime is installed Playwright 1.62.1 / Chromium. The shared tests cover functional risks; complete accessibility, security and production readiness are not established.
