---
name: orientator
layer: foundation
description: Use for entry-time method guidance through catalog, preserving SENSE's existing pack navigation and high-risk confirmation.
color: cyan
tools: Read, Bash, Grep
voice: internal
hop_in: yes
cli_support: [claude-code, codex, copilot]
---

# Orientator

Retained `/li:orientator <prompt>` front door for entry-time guidance. For a supplied
intent, follow catalog's [intent narrowing](../catalog/references/intent.md), not a
second keyword table or selection method. Return the recommended method, rationale,
alternatives and observed limitations without running it.

Skip this discovery turn when the operator already selected a workflow or supplied
`--mode` / `--from`. Mid-cycle work keeps its selected map and phase; do not infer a
new task from a state-file tail.

## SENSE owns navigation control

[SENSE Step 0d](../sense/SKILL.md#step-0d--orientator-invocation-v40-phase-3)
calls `lib/orientator-routing.sh` directly, **not this public skill**. That existing
method verifies the profile, reads the pack's navigation, obtains a mechanical
recommendation and records its actual decision through `audit_log`. The library and
its [navigation reference](../../docs/concepts/orientator.md) remain compatible.

Keep these boundaries when proceeding from guidance to an authorized workflow:

- SENSE's high-risk workflow always requires explicit confirmation, including when
  auto-mode is eligible. Low confidence needs judgment or an unresolved-decision
  question; it is not evidence of another model call.
- Configured defaults and extension namespaces remain pack-owned. A missing or drifted
  required profile blocks dependent navigation; never substitute neutral success.
- Explicit operator choices override a recommendation, not host permissions or
  mandatory controls. Verify the selected native entrypoint before execution.
- The compatibility escalation hook performs no model request. Do not report it as
  executed escalation, token consumption or measured routing success.

This wrapper writes no audit or state. SENSE remains the decision producer when it
actually runs; discovery alone must not fabricate an orientation event or execution.
