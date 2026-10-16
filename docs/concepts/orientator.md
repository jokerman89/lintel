# Intent navigation in SENSE and catalog

**Last updated:** 2026-10-09
**Status:** Current implementation boundary

Lintel has two related but distinct paths for choosing a method. SENSE performs its
existing cycle-entry recommendation; catalog supports operator-requested discovery.
Neither path turns a recommendation into host discovery, permission, or execution.

## SENSE routing

When the operator has not already selected `--mode` or `--from`, SENSE uses the
trusted `lib/orientator-routing.sh` helper. It verifies profile context, classifies
the requested operation, resolves the pack's default and high-risk workflow policy,
and records the resulting intent, workflow, risk and confidence through the shared
audit writer. The heuristic confidence is not measured accuracy.

SENSE surfaces the recommendation in its report. A configured auto-mode may proceed
only within its existing eligibility rules; high-risk work still requires explicit
confirmation. Low confidence calls for operator judgment or a missing-decision
question. `invoke_llm_orientation` remains a dormant stub, not a model invocation or
evidence of escalation.

The helper is an internal SENSE dependency, not a separate discoverable workflow.
See [SENSE Step 0d](../../skills/sense/SKILL.md#step-0d--orientator-invocation-v40-phase-3)
and the [routing helper](../../lib/orientator-routing.sh).

## Operator-requested discovery

For free-text method discovery, use `/li:catalog` and follow its
[intent narrowing method](../../skills/catalog/references/intent.md). It builds a
metadata-first shortlist, checks only selected method bodies, and reports fit,
alternatives and limitations. It does not execute a method or dispatch an agent.

Native host discovery and permission are separate facts. A catalog entry or source
file does not prove that a workflow is installed, callable or authorized on the
current client.

## Boundaries

- An explicit operator-selected method takes precedence over recommendations.
- SENSE's verified profile, pack policy, high-risk confirmation and audit behavior
  remain the navigation control; catalog does not replace them.
- Recommendations do not add authority, waive mandatory review, or establish that
  any subsequent operation ran.
- Missing profile or required policy is a blocker, not a successful default route.
