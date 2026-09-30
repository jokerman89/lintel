# Verified delivery status capture

Status: APPROVED within the existing implementation and continuity mandate.
This is documentation reconciliation, not another implementation backlog.

| ID | Requirement | Acceptance |
|---|---|---|
| R1 | Update only verified original task progress | Original leaf IDs, requirements, dependencies and work-map approval remain unchanged. Completed implementation and delivery must have actual evidence. |
| R2 | Distinguish history, delivery and open work | Retain earlier build observations as history. Source-only candidates, unrun controls, broader parent work and held scopes are never marked delivered. |
| R3 | Leave a usable public handoff | Link original maps, summarize actual delivered behavior and preserve migration/host limitations without private session paths, raw conversations or personal data. |
| R4 | Preserve product and governance | No executable, test, version, schema, instruction protocol, ADR or policy changes; `.claude/plans/todo.md` stays byte-identical. |

The header candidate is a dependency, not an outcome supplied by this capture.
Do not publish a descendant until that exact candidate has independently passed
its required gates and actually landed.
