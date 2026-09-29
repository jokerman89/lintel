# Spec: trusted workflow helper sources

**Status:** APPROVED for the bounded correctness fix.
**Source finding:** DR-29, original remediation card W1-1.
**Authority:** the operator's 2026-09-29 clarification requires implemented review
outcomes, not report publication. This card enforces existing source/target
separation; it does not authorize the broader proposed portfolio changes.
**Plan:** [plan.md](plan.md).

## Architecture and requirements

The Universal adapter and ADR-0028 separate trusted Lintel helper code from the
working repository. ADR-0031 requires a missing trusted helper to fail rather than
select a target substitute. No new resolver, schema or permission mechanism is needed.

| ID | Required behavior | Existing authority |
|---|---|---|
| R1 | Executable helpers in the affected workflow examples come only from explicit `LINTEL_SOURCE_ROOT` or the documented `CLAUDE_PLUGIN_ROOT` binding. | Universal adapter; ADR-0028 |
| R2 | Missing or invalid trusted helper input stops a required audit/state/routing step with a visible error. Never select the working repo, Git cwd or personal home as a substitute. | ADR-0031 |
| R3 | The optional REVIEW/SHIP position footer reports unavailable evidence without loading a helper from another root or claiming completion. | ADR-0003; existing welcome footer |
| R4 | Canonical and generated native workflows remain consistent; data destinations, required policy, review independence and latest-decision semantics are unchanged. | ADR-0024, ADR-0028, ADR-0039 |

## Scope and constraints

The current source sweep identifies the same fallback in `review`, `ship`,
`usage-log`, `orientator` and `frontend-style-extract`. Fix only their helper-source
selection and corresponding regression coverage and generated native artifacts.
Do not change rendering, routing decisions, audit destinations, tool permissions,
hook activation, historical evidence, or the frozen historical work index.

Tests use inert, owned helper fixtures and controlled environments. They do not
reproduce exploitation or run production operations. Missing host capabilities
remain explicit; synthetic tests are not live-client acceptance.

## Verification

Require nonzero regression tests for explicit source selection, permitted plugin
binding, missing/invalid trusted inputs and optional-footer degradation. Run the
existing source/target and footer contracts and generated-artifact checks. A
separate reviewer evaluates the actual changed source and evidence before delivery.

Broader W4/W5 design and governance choices are outside this card.
